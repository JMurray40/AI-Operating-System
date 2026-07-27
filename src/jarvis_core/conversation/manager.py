"""Conversation manager: orchestrates a multi-turn, read-only conversation.

Composes an injected :class:`QueryEngine` (retrieval/ranking/citations), a
:class:`ReferenceResolver` (pronoun/ellipsis resolution), and an in-memory
:class:`ConversationSession`. Conversation state is isolated from retrieval: the manager
resolves references, hands a plain query to the engine, and enriches the result with
provenance. Nothing is persisted; the vault is never modified.

Retrieved note text is treated as data, never as instructions (Chat PRD req. 9).
"""
from __future__ import annotations

import time
from collections.abc import Iterator

from jarvis_core.conversation.entities import MentionedEntity
from jarvis_core.conversation.explanation import (
    Statement,
    StatementKind,
    reasoning_summary,
)
from jarvis_core.conversation.references import ReferenceResolver, ResolvedInput
from jarvis_core.conversation.results import (
    ConflictNote,
    ConversationAnswer,
    StreamEvent,
    StreamEventKind,
)
from jarvis_core.conversation.session import ConversationSession
from jarvis_core.conversation.trace import ConversationTrace
from jarvis_core.models.base import NoteType
from jarvis_core.query.engine import QueryEngine
from jarvis_core.query.intent import Intent
from jarvis_core.query.results import Citation, QueryAnswer
from jarvis_core.query.tokenizer import normalize

_MAX_ENTITIES_PER_TURN = 3
_PERSON_WORDS = frozenset({"who", "whom", "person", "people", "owner", "owns", "working"})


class ConversationManager:
    """Drives a read-only, session-only conversation over the query engine."""

    def __init__(
        self,
        engine: QueryEngine,
        *,
        session: ConversationSession | None = None,
        resolver: ReferenceResolver | None = None,
    ) -> None:
        self._engine = engine
        self._session = session or ConversationSession()
        self._resolver = resolver or ReferenceResolver()

    @property
    def session(self) -> ConversationSession:
        return self._session

    def reset(self) -> None:
        self._session.reset()

    # ------------------------------------------------------------------ ask
    def ask(
        self, user_input: str, *, want_trace: bool = False
    ) -> tuple[ConversationAnswer, ConversationTrace | None]:
        resolved = self._resolver.resolve(user_input, self._session.entity_stack)
        t0 = time.perf_counter()
        try:
            query_answer, query_trace = self._engine.run(
                resolved.effective_query, want_trace=want_trace
            )
        except Exception as exc:  # provider or engine failure -> graceful, retained
            answer = self._failed_answer(user_input, resolved, exc)
            self._session.record(user_input, resolved.effective_query, answer.text, [])
            trace = self._build_trace(resolved, None, "failed", want_trace)
            return answer, trace
        elapsed = (time.perf_counter() - t0) * 1000

        answer = self._enrich(user_input, resolved, query_answer)
        entities = self._entities_from(query_answer, self._session.turn_count)
        self._session.record(user_input, resolved.effective_query, answer.text, entities)

        trace = self._build_trace(resolved, query_trace, answer.status, want_trace)
        if trace is not None:
            trace.timings_ms = {"retrieval_run": elapsed}
        return answer, trace

    # -------------------------------------------------------------- streaming
    def ask_stream(self, user_input: str) -> Iterator[StreamEvent]:
        """Stream a turn as normalized events. Optional; deterministic ordering."""
        yield StreamEvent(StreamEventKind.STARTED, data={"input": user_input})
        try:
            answer, _ = self.ask(user_input)
        except Exception as exc:  # pragma: no cover - ask() already guards
            yield StreamEvent(StreamEventKind.FAILED, text=str(exc))
            return
        # Emit the answer text in word deltas (uniform whether or not the provider streamed).
        words = answer.text.split(" ")
        for i, word in enumerate(words):
            yield StreamEvent(StreamEventKind.DELTA, text=(word if i == 0 else " " + word))
        for c in answer.citations:
            yield StreamEvent(StreamEventKind.CITATION, data=c.to_dict())
        yield StreamEvent(
            StreamEventKind.USAGE,
            data={"citations": len(answer.citations), "confidence": answer.confidence},
        )
        kind = StreamEventKind.FAILED if answer.status == "failed" else StreamEventKind.COMPLETED
        yield StreamEvent(kind, data={"status": answer.status})

    # ------------------------------------------------------------- enrichment
    def _enrich(
        self, user_input: str, resolved: ResolvedInput, qa: QueryAnswer
    ) -> ConversationAnswer:
        statements = self._build_statements(resolved, qa)
        conflicts = self._detect_conflicts(qa.citations)
        confidence = qa.citations[0].confidence if qa.citations else 0.0
        return ConversationAnswer(
            question=user_input,
            effective_query=resolved.effective_query,
            text=qa.answer,
            confidence=confidence,
            reasoning_summary=reasoning_summary(statements),
            citations=qa.citations,
            statements=statements,
            conflicts=conflicts,
            assumptions=resolved.assumptions,
            provider=self._engine.provider_name if qa.intent is Intent.SUMMARIZE_PROJECT
            else "none",
            status="completed",
        )

    def _build_statements(
        self, resolved: ResolvedInput, qa: QueryAnswer
    ) -> tuple[Statement, ...]:
        out: list[Statement] = []
        # Assumptions from reference resolution.
        for a in resolved.assumptions:
            out.append(Statement(StatementKind.ASSUMPTION, a))
        # Facts from the top cited notes.
        for c in qa.citations[:_MAX_ENTITIES_PER_TURN]:
            note = self._engine.note_by_relpath(c.relpath)
            if note is None:
                continue
            fact = self._fact_for(note.type, c.title, note)
            if fact:
                out.append(Statement(StatementKind.FACT, fact, c.relpath))
        # Relationships among cited notes (resolved graph edges).
        cited = {c.relpath for c in qa.citations}
        report = self._engine.report
        seen_rel: set[tuple[str, str]] = set()
        for c in qa.citations[:_MAX_ENTITIES_PER_TURN]:
            for tgt in report.outgoing(c.relpath):
                if tgt in cited and (c.relpath, tgt) not in seen_rel:
                    seen_rel.add((c.relpath, tgt))
                    tgt_note = self._engine.note_by_relpath(tgt)
                    tgt_title = (tgt_note.title or tgt) if tgt_note else tgt
                    out.append(
                        Statement(
                            StatementKind.RELATIONSHIP,
                            f"'{c.title}' links to '{tgt_title}'.",
                            c.relpath,
                        )
                    )
        # Inference when the answer leaned on graph proximity rather than direct text.
        if qa.intent is Intent.RELATED_TO and qa.citations:
            out.append(
                Statement(
                    StatementKind.INFERENCE,
                    "Some results are inferred from graph proximity, not direct term matches.",
                )
            )
        # Unknowns: person/owner questions with no person note found.
        if self._asks_about_people(resolved.raw) and not self._has_person(qa.citations):
            subject = resolved.focus.title if resolved.focus else "the subject"
            out.append(
                Statement(
                    StatementKind.UNKNOWN,
                    f"No owner or person information was found for {subject}.",
                )
            )
        if not qa.citations:
            out.append(
                Statement(StatementKind.UNKNOWN, "No supporting notes matched this question.")
            )
        return tuple(out)

    @staticmethod
    def _fact_for(note_type: NoteType | None, title: str, note: object) -> str | None:
        if note_type is NoteType.PROJECT:
            status = getattr(note, "status", None)
            fm = getattr(note, "frontmatter", {})
            goal = fm.get("goal") if isinstance(fm, dict) else None
            attrs = [a for a in (f"status={status}" if status else None,
                                 f"goal={goal}" if goal else None) if a]
            suffix = f" ({', '.join(attrs)})" if attrs else ""
            return f"'{title}' is a project{suffix}."
        if note_type is not None:
            return f"'{title}' is a {note_type.value.replace('-', ' ')} note."
        return f"'{title}' is a note in the vault."

    def _detect_conflicts(self, citations: tuple[Citation, ...]) -> tuple[ConflictNote, ...]:
        conflicts: list[ConflictNote] = []
        # Same title, different notes -> potential conflict.
        by_title: dict[str, list[Citation]] = {}
        for c in citations:
            by_title.setdefault(normalize(c.title), []).append(c)
        for _title, group in sorted(by_title.items()):
            relpaths = sorted({c.relpath for c in group})
            if len(relpaths) > 1:
                conflicts.append(
                    ConflictNote(
                        subject=group[0].title,
                        relpaths=tuple(relpaths),
                        reason="multiple distinct notes share this title",
                    )
                )
        # Same frontmatter id, different notes -> duplicate-id conflict.
        by_id: dict[str, list[str]] = {}
        for c in citations:
            if c.id:
                by_id.setdefault(c.id, []).append(c.relpath)
        for note_id, relpaths in sorted(by_id.items()):
            distinct = sorted(set(relpaths))
            if len(distinct) > 1:
                conflicts.append(
                    ConflictNote(
                        subject=note_id,
                        relpaths=tuple(distinct),
                        reason="duplicate id across notes",
                    )
                )
        return tuple(conflicts)

    @staticmethod
    def _asks_about_people(text: str) -> bool:
        words = set(normalize(text).split())
        return bool(words & _PERSON_WORDS)

    def _has_person(self, citations: tuple[Citation, ...]) -> bool:
        for c in citations:
            note = self._engine.note_by_relpath(c.relpath)
            if note is not None and note.type in (NoteType.PERSON, NoteType.ORGANIZATION):
                return True
        return False

    def _entities_from(self, qa: QueryAnswer, turn: int) -> list[MentionedEntity]:
        out: list[MentionedEntity] = []
        for c in qa.citations[:_MAX_ENTITIES_PER_TURN]:
            out.append(MentionedEntity(relpath=c.relpath, title=c.title, id=c.id, turn=turn))
        return out

    def _failed_answer(
        self, user_input: str, resolved: ResolvedInput, exc: Exception
    ) -> ConversationAnswer:
        return ConversationAnswer(
            question=user_input,
            effective_query=resolved.effective_query,
            text=f"The provider could not complete this request ({type(exc).__name__}). "
            "No partial answer is available; the vault was not modified.",
            confidence=0.0,
            reasoning_summary="Provider failure; request not completed.",
            assumptions=resolved.assumptions,
            provider=self._engine.provider_name,
            status="failed",
        )

    def _build_trace(
        self,
        resolved: ResolvedInput,
        query_trace: object,
        status: str,
        want_trace: bool,
    ) -> ConversationTrace | None:
        if not want_trace:
            return None
        from jarvis_core.query.trace import QueryTrace

        qt = query_trace if isinstance(query_trace, QueryTrace) else None
        return ConversationTrace(
            turn_index=self._session.turn_count,
            resolved=resolved,
            entity_stack=tuple(self._session.entity_stack),
            query_trace=qt,
            provider=self._engine.provider_name,
            status=status,
        )
