"""Offline, deterministic, authorized query engine over the parsed vault (v0.3.1).

Composes small collaborators (IntentParser, authorized LexicalIndex, Ranker,
QueryContextBuilder) injected at construction. Every query runs under an immutable
:class:`AuthorizationScope`; authorization is applied before the index/graph are built, so
excluded sources cannot influence retrieval, ranking, context, citations, conflicts, or
trace (ADR-0015). Rankings expose ``relative_relevance`` (ADR-0014); citations bind a
stable identity to an exact revision and a deterministic passage (ADR-0016). Read-only.
"""
from __future__ import annotations

import hashlib
import time
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

from jarvis_core.context.loader import ProjectContextLoader, ProjectNotFoundError
from jarvis_core.identity import fingerprint_bytes
from jarvis_core.models.base import NoteType
from jarvis_core.models.context import SourceRef
from jarvis_core.models.note import Note
from jarvis_core.policy.errors import PolicyError
from jarvis_core.policy.scope import AuthorizationScope
from jarvis_core.providers import get_provider
from jarvis_core.providers.base import Provider
from jarvis_core.query.authorized import build_authorized_view
from jarvis_core.query.context_builder import (
    DEFAULT_TOKEN_BUDGET,
    QueryContext,
    QueryContextBuilder,
)
from jarvis_core.query.contract import CONTRACT_VERSION, INDEX_VERSION
from jarvis_core.query.index import LexicalIndex
from jarvis_core.query.intent import Intent, IntentParser, ParsedQuery
from jarvis_core.query.passages import Locator, locate, validate_against_text
from jarvis_core.query.ranking import Ranker, RankingWeights, ScoredNote
from jarvis_core.query.results import Citation, QueryAnswer, citation_from_scored
from jarvis_core.query.tokenizer import normalize, token_set
from jarvis_core.query.trace import QueryTrace
from jarvis_core.relationships.resolver import RelationshipResolver, ResolutionReport

_SEARCH_LIMIT = 20

__all__ = ["Intent", "QueryAnswer", "QueryEngine", "QueryResult", "RankingWeights"]


@dataclass(frozen=True)
class QueryResult:
    """Stable v0.2 shape (kept for backwards compatibility)."""

    intent: Intent
    question: str
    answer: str
    matches: tuple[SourceRef, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "intent": self.intent.value,
            "question": self.question,
            "answer": self.answer,
            "matches": [m.to_dict() for m in self.matches],
        }


class QueryEngine:
    """Routes a question to an intent and answers from the authorized vault (read-only)."""

    def __init__(
        self,
        notes: list[Note],
        *,
        scope: AuthorizationScope,
        weights: RankingWeights | None = None,
        token_budget: int = DEFAULT_TOKEN_BUDGET,
        provider: Provider | None = None,
        source_root: Path | None = None,
    ) -> None:
        # An explicit AuthorizationScope is REQUIRED at the query boundary (AC-01, ADR-0015).
        # A missing/None scope fails closed rather than silently broadening to allow-all; use
        # the explicit local_allow_all() factory for local read-only workflows.
        if scope is None:
            raise PolicyError(
                "QueryEngine requires an explicit AuthorizationScope; "
                "use jarvis_core.policy.local_allow_all() for local workflows"
            )
        self._scope = scope
        # When provided, current source bytes are re-read from this root (confined to it)
        # at citation emission so a post-discovery change makes the citation stale (AC-03R2).
        self._source_root = source_root.resolve() if source_root is not None else None
        view = build_authorized_view(notes, self._scope)
        self._notes = view.notes
        self._identities = view.identities
        self._excluded_count = view.excluded_count
        self._resolver = RelationshipResolver(self._notes)
        self._report = self._resolver.resolve_all()
        self._by_relpath = {n.relpath: n for n in self._notes}
        self._parser = IntentParser()
        self._index = LexicalIndex(self._notes)
        self._ranker = Ranker(self._index, self._report, weights)
        self._context = QueryContextBuilder(
            self._index, self._report, token_budget=token_budget
        )
        self._provider = provider or get_provider("mock")

    # ---------------------------------------------------------- read-only accessors
    @property
    def report(self) -> ResolutionReport:
        return self._report

    @property
    def scope(self) -> AuthorizationScope:
        return self._scope

    @property
    def excluded_count(self) -> int:
        return self._excluded_count

    @property
    def provider_name(self) -> str:
        return self._provider.name

    def note_by_relpath(self, relpath: str) -> Note | None:
        return self._by_relpath.get(relpath)

    def all_notes(self) -> list[Note]:
        return list(self._notes)

    def workspace_fingerprint(self) -> str:
        h = hashlib.sha256()
        for n in sorted(self._notes, key=lambda n: n.relpath):
            h.update(n.relpath.encode("utf-8"))
            h.update(b"\0")
            h.update(n.source_fingerprint.encode("utf-8"))
            h.update(b"\0")
        return "sha256:" + h.hexdigest()

    # ============================================================ v0.2 API
    def ask(self, question: str) -> QueryResult:
        answer, _ = self.run(question)
        matches = tuple(
            SourceRef(
                id=(self._by_relpath[c.relpath].id if c.relpath in self._by_relpath else None),
                title=c.title,
                relpath=c.relpath,
            )
            for c in answer.citations
        )
        return QueryResult(answer.intent, answer.question, answer.answer, matches)

    # ============================================================ v0.3.1 API
    def run(
        self, question: str, *, want_trace: bool = False
    ) -> tuple[QueryAnswer, QueryTrace | None]:
        parsed = self._parser.parse(question)
        trace = self._new_trace(parsed) if want_trace else None
        if parsed.intent is Intent.SUMMARIZE_PROJECT:
            answer = self._summarize_project(parsed, trace)
        elif parsed.intent is Intent.PROJECTS_MENTIONING:
            answer = self._projects_mentioning(parsed, trace)
        elif parsed.intent is Intent.RELATED_TO:
            answer = self._related_to(parsed, trace)
        elif parsed.intent is Intent.EXPLAIN_RELATIONSHIP:
            answer = self._explain(parsed, trace)
        else:
            answer = self._search(parsed, trace)
        return answer, trace

    def search(self, query: str, *, limit: int = _SEARCH_LIMIT) -> QueryAnswer:
        parsed = ParsedQuery(Intent.SEARCH, query.strip(), self._parser.parse(query).terms)
        return self._search(parsed, None, limit=limit)

    def summarize(self, name: str) -> QueryAnswer:
        parsed = ParsedQuery(Intent.SUMMARIZE_PROJECT, name.strip(), (), target=name.strip())
        return self._summarize_project(parsed, None)

    def explain(self, left: str, right: str) -> QueryAnswer:
        question = f"relationship between {left} and {right}"
        parsed = ParsedQuery(
            Intent.EXPLAIN_RELATIONSHIP, question, (), left=left.strip(), right=right.strip()
        )
        return self._explain(parsed, None)

    # ============================================================ intents
    def _search(
        self, parsed: ParsedQuery, trace: QueryTrace | None, *, limit: int = _SEARCH_LIMIT
    ) -> QueryAnswer:
        terms = list(parsed.terms)
        if not terms:
            return self._answer(Intent.SEARCH, parsed.question, "No searchable terms found.")
        t0 = time.perf_counter()
        candidates = self._index.candidates(terms)
        t1 = time.perf_counter()
        ranked = self._ranker.rank(terms, candidates, phrase=" ".join(terms))
        t2 = time.perf_counter()
        top = ranked[:limit]
        answer = (
            f"No notes match: {', '.join(terms)}." if not top
            else f"{len(ranked)} note(s) match {terms}; top {len(top)} by relative relevance."
        )
        ev = frozenset(terms)
        citations = self._drop_none(self._cite_scored(s, ev) for s in top)
        self._fill_trace(
            trace, candidates, top, provider="none",
            timings={"retrieval": (t1 - t0) * 1000, "ranking": (t2 - t1) * 1000},
        )
        return self._answer(Intent.SEARCH, parsed.question, answer, citations)

    def _projects_mentioning(
        self, parsed: ParsedQuery, trace: QueryTrace | None
    ) -> QueryAnswer:
        term = normalize(parsed.target or "")
        if not term:
            return self._answer(
                Intent.PROJECTS_MENTIONING, parsed.question, "No search term found."
            )
        hits = [
            n for n in self._notes
            if n.type is NoteType.PROJECT and self._note_or_related_mentions(n, term)
        ]
        ranked = self._rank_subset(list(parsed.terms) or [term], hits, phrase=parsed.target)
        if not ranked:
            answer = f"No projects mention '{parsed.target}'."
        else:
            names = ", ".join(s.note.title or s.note.path.stem for s in ranked)
            answer = f"{len(ranked)} project(s) mention '{parsed.target}': {names}."
        ev = frozenset(parsed.terms) or frozenset({term})
        citations = self._drop_none(self._cite_scored(s, ev) for s in ranked)
        self._fill_trace(trace, {n.relpath for n in hits}, ranked, provider="none", timings={})
        return self._answer(Intent.PROJECTS_MENTIONING, parsed.question, answer, citations)

    def _related_to(self, parsed: ParsedQuery, trace: QueryTrace | None) -> QueryAnswer:
        term = normalize(parsed.target or "")
        if not term:
            return self._answer(Intent.RELATED_TO, parsed.question, "No search term found.")
        direct = [n for n in self._notes if term in self._searchable(n.relpath)]
        related: dict[str, Note] = {n.relpath: n for n in direct}
        neighbours: set[str] = set()
        for n in direct:
            for tgt in self._report.outgoing(n.relpath):
                if tgt in self._by_relpath and tgt not in related:
                    related[tgt] = self._by_relpath[tgt]
                    neighbours.add(tgt)
            for src in self._report.incoming(n.relpath):
                if src in self._by_relpath and src not in related:
                    related[src] = self._by_relpath[src]
                    neighbours.add(src)
        ranked = self._rank_subset(
            list(parsed.terms) or [term], list(related.values()),
            phrase=parsed.target, neighbor_boost=frozenset(neighbours),
        )
        answer = (
            f"No notes related to '{parsed.target}'." if not ranked
            else f"{len(ranked)} note(s) related to '{parsed.target}' "
                 f"(direct matches and neighbours)."
        )
        ev = frozenset(parsed.terms) or frozenset({term})
        citations = self._drop_none(self._cite_scored(s, ev) for s in ranked)
        context = self._context.build([s.relpath for s in ranked]) if ranked else None
        self._fill_trace(
            trace, set(related), ranked, provider="none", timings={}, context=context
        )
        return self._answer(Intent.RELATED_TO, parsed.question, answer, citations)

    def _summarize_project(
        self, parsed: ParsedQuery, trace: QueryTrace | None
    ) -> QueryAnswer:
        name = parsed.target or parsed.question
        loader = ProjectContextLoader(self._notes)
        try:
            package = loader.load(name)
        except ProjectNotFoundError as exc:
            return self._answer(Intent.SUMMARIZE_PROJECT, parsed.question, str(exc))
        t0 = time.perf_counter()
        response = self._provider.summarize(package, model_role="research")
        t1 = time.perf_counter()
        # Claim-specific evidence: each source is cited where it references the project
        # (a supporting passage), not arbitrary first content (AC-03R2).
        proj_terms = self._claim_terms(package.project_title)
        citations = self._drop_none(
            self._make_citation(
                self._by_relpath[s.relpath], proj_terms, relevance=None,
                reason="supports project context", material=False,
            )
            for s in package.sources if s.relpath in self._by_relpath
        )
        if trace is not None:
            context = self._context.build([s.relpath for s in package.sources])
            self._fill_trace(
                trace, {s.relpath for s in package.sources}, (), provider=self._provider.name,
                timings={"provider": (t1 - t0) * 1000}, context=context,
            )
        return self._answer(Intent.SUMMARIZE_PROJECT, parsed.question, response.summary, citations)

    def _explain(self, parsed: ParsedQuery, trace: QueryTrace | None) -> QueryAnswer:
        left = self._resolve_note(parsed.left or "")
        right = self._resolve_note(parsed.right or "")
        if left is None or right is None:
            missing = parsed.left if left is None else parsed.right
            return self._answer(
                Intent.EXPLAIN_RELATIONSHIP, parsed.question,
                f"Could not find a note matching '{missing}'.",
            )
        lp, rp = left.relpath, right.relpath
        direct = rp in self._report.outgoing(lp) or lp in self._report.outgoing(rp)
        l_n = set(self._report.outgoing(lp)) | set(self._report.incoming(lp))
        r_n = set(self._report.outgoing(rp)) | set(self._report.incoming(rp))
        shared = sorted((l_n & r_n) - {lp, rp})
        lt = left.title or left.path.stem
        rt = right.title or right.path.stem
        parts: list[str] = []
        if direct:
            parts.append(f"'{lt}' and '{rt}' are directly linked.")
        if shared:
            names = ", ".join((self._by_relpath[s].title or s) for s in shared)
            parts.append(f"They share {len(shared)} connected note(s): {names}.")
        if not parts:
            parts.append(f"No direct link or shared neighbour connects '{lt}' and '{rt}'.")
        cited_notes = [left, right, *(self._by_relpath[s] for s in shared)]
        _titles = {n.relpath: (n.title or n.path.stem) for n in cited_notes}

        def _rel_evidence(n: Note) -> frozenset[str]:
            # Cite the passage in n that links the other endpoint(s)/shared note(s).
            others = [_titles[m.relpath] for m in cited_notes if m.relpath != n.relpath]
            return self._claim_terms(*others)

        citations = self._drop_none(
            self._make_citation(n, _rel_evidence(n), relevance=None,
                                reason="relationship evidence", material=False)
            for n in cited_notes
        )
        if trace is not None:
            context = self._context.build([lp, rp, *shared])
            self._fill_trace(
                trace, {lp, rp, *shared}, (), provider="none", timings={}, context=context
            )
        return self._answer(Intent.EXPLAIN_RELATIONSHIP, parsed.question, " ".join(parts),
                            citations)

    # ============================================================ helpers
    def _answer(
        self, intent: Intent, question: str, text: str, citations: tuple[Citation, ...] = ()
    ) -> QueryAnswer:
        return QueryAnswer(intent, question, text, citations, excluded_count=self._excluded_count)

    def _current_bytes(self, note: Note) -> bytes:
        """Exact current source bytes for ``note``, confined to the configured root.

        With a source root, the file is re-read (path-escape and missing files fail closed
        by returning empty bytes, which then fail the fingerprint check). Without a root, the
        discovery-time bytes are used (this proves discovery-revision consistency only, not a
        post-discovery on-disk change).
        """
        if self._source_root is not None:
            try:
                cand = (self._source_root / note.relpath).resolve()
                if cand.is_relative_to(self._source_root) and cand.is_file():
                    return cand.read_bytes()
            except OSError:
                pass
            return b""  # missing / escaped / unreadable under a known root -> fail closed
        return note.source_bytes

    def _make_citation(
        self,
        note: Note,
        evidence: frozenset[str],
        *,
        relevance: float | None,
        reason: str,
        material: bool,
        scored: ScoredNote | None = None,
    ) -> Citation | None:
        """Emit a validated citation, or None. Validates the stored fingerprint against the
        CURRENT source bytes plus locator/hierarchy/excerpt before emission (AC-03R2)."""
        ident = self._identities[note.relpath]
        current = self._current_bytes(note)
        if fingerprint_bytes(current) != note.source_fingerprint:
            return None  # stale: source changed since discovery -> never emitted as valid
        current_text = current.decode("utf-8", errors="replace")
        locator, excerpt = locate(note, evidence)
        if excerpt and validate_against_text(locator, excerpt, current_text).ok:
            if scored is not None:
                return citation_from_scored(
                    scored, source_id=ident.source_id, source_identity_kind=ident.kind,
                    source_fingerprint=note.source_fingerprint, locator=locator, excerpt=excerpt,
                )
            return Citation(
                source_id=ident.source_id, source_identity_kind=ident.kind,
                title=note.title or note.path.stem, relpath=note.relpath,
                source_fingerprint=note.source_fingerprint, locator=locator, excerpt=excerpt,
                reason=reason, relative_relevance=relevance, coverage="supported",
            )
        # No claim-specific supporting passage.
        if material:
            return None  # decline a ranked material citation with no supporting passage
        # Unranked reference: emit an explicit coverage-incomplete citation (never arbitrary
        # first content) — identity + revision only, no passage claim.
        return Citation(
            source_id=ident.source_id, source_identity_kind=ident.kind,
            title=note.title or note.path.stem, relpath=note.relpath,
            source_fingerprint=note.source_fingerprint, locator=Locator((), 0, 0), excerpt="",
            reason=reason, relative_relevance=relevance, coverage="incomplete",
        )

    def _cite_scored(self, scored: ScoredNote, evidence: frozenset[str]) -> Citation | None:
        return self._make_citation(
            scored.note, evidence, relevance=scored.relative_relevance,
            reason="retrieval match", material=True, scored=scored,
        )

    @staticmethod
    def _claim_terms(*titles: str) -> frozenset[str]:
        terms: set[str] = set()
        for t in titles:
            terms |= token_set(t)
        return frozenset(terms)

    @staticmethod
    def _drop_none(cits: Iterable[Citation | None]) -> tuple[Citation, ...]:
        return tuple(c for c in cits if c is not None)

    def _rank_subset(
        self, terms: list[str], notes: list[Note], *, phrase: str | None = None,
        neighbor_boost: frozenset[str] = frozenset(),
    ) -> list[ScoredNote]:
        candidate_set = {n.relpath for n in notes}
        ranked = self._ranker.rank(
            terms, candidate_set, phrase=phrase, neighbor_boost=neighbor_boost
        )
        ranked_paths = {s.relpath for s in ranked}
        leftovers = sorted(
            (n for n in notes if n.relpath not in ranked_paths), key=lambda n: n.relpath
        )
        from jarvis_core.query.ranking import RankingExplanation
        for n in leftovers:
            ranked.append(ScoredNote(n, 0.0, 0.0, RankingExplanation(n.relpath, 0.0, ())))
        return ranked

    def _resolve_note(self, name: str) -> Note | None:
        relpath = self._resolver.resolve_target(name)
        if relpath is not None and relpath in self._by_relpath:
            return self._by_relpath[relpath]
        return None

    def _searchable(self, relpath: str) -> str:
        ni = self._index.get(relpath)
        return " ".join(ni.field_norm.values())

    def _note_or_related_mentions(self, project: Note, term: str) -> bool:
        if term in self._searchable(project.relpath):
            return True
        for tgt in self._report.outgoing(project.relpath):
            if self._index.contains(tgt) and term in self._searchable(tgt):
                return True
        for src in self._report.incoming(project.relpath):
            if self._index.contains(src) and term in self._searchable(src):
                return True
        return False

    # ------------------------------------------------------------- trace
    def _new_trace(self, parsed: ParsedQuery) -> QueryTrace:
        return QueryTrace(
            parsed=parsed,
            contract_version=CONTRACT_VERSION,
            index_version=INDEX_VERSION,
            request_id=self._scope.request_id,
            workspace_fingerprint=self.workspace_fingerprint(),
            authorization=self._scope.trace_summary(),
            excluded_count=self._excluded_count,
        )

    def _fill_trace(
        self, trace: QueryTrace | None, candidates: set[str], ranked: Sequence[ScoredNote],
        *, provider: str, timings: dict[str, float], context: QueryContext | None = None,
    ) -> None:
        if trace is None:
            return
        trace.candidates = tuple(sorted(candidates))
        trace.ranked = tuple(ranked)
        trace.provider = provider
        trace.timings_ms = dict(timings)
        if context is not None:
            trace.context = context
            trace.token_counts = {"context": context.total_tokens}
