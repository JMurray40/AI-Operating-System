"""Offline, deterministic query engine over the parsed vault.

This is the read-only foundation for a future AI-backed ``ask``. It does NOT call any
network service, use randomness, or require keys. It composes small, single-purpose
collaborators -- an :class:`IntentParser`, a :class:`LexicalIndex`, a :class:`Ranker`, and
a :class:`QueryContextBuilder` -- injected at construction so each can be tested and
replaced independently (SYSTEM_PRINCIPLES: small modules, low coupling).

Two surfaces are exposed:

* :meth:`ask` -- the stable v0.2 API returning a :class:`QueryResult` (kept for
  backwards compatibility; existing callers and tests are unaffected).
* :meth:`run` / :meth:`search` / :meth:`summarize` / :meth:`explain` -- the v0.3 surface
  returning cited :class:`QueryAnswer` objects, with optional :class:`QueryTrace`.
"""
from __future__ import annotations

import time
from dataclasses import dataclass

from jarvis_core.context.loader import ProjectContextLoader, ProjectNotFoundError
from jarvis_core.models.base import NoteType
from jarvis_core.models.context import SourceRef
from jarvis_core.models.note import Note
from jarvis_core.providers import get_provider
from jarvis_core.providers.base import Provider
from jarvis_core.query.context_builder import (
    DEFAULT_TOKEN_BUDGET,
    QueryContext,
    QueryContextBuilder,
    estimate_tokens,
)
from jarvis_core.query.index import LexicalIndex
from jarvis_core.query.intent import Intent, IntentParser, ParsedQuery
from jarvis_core.query.ranking import Ranker, RankingWeights, ScoredNote
from jarvis_core.query.results import Citation, QueryAnswer, citation_from_scored
from jarvis_core.query.tokenizer import normalize
from jarvis_core.query.trace import QueryTrace
from jarvis_core.relationships.resolver import RelationshipResolver

_SEARCH_LIMIT = 20

__all__ = [
    "Intent",
    "QueryAnswer",
    "QueryEngine",
    "QueryResult",
    "RankingWeights",
]


@dataclass(frozen=True)
class QueryResult:
    """A deterministic answer to a question (stable v0.2 shape)."""

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


def _ref(note: Note) -> SourceRef:
    return SourceRef(id=note.id, title=(note.title or note.path.stem), relpath=note.relpath)


class QueryEngine:
    """Routes a question to an intent and answers from the vault (read-only)."""

    def __init__(
        self,
        notes: list[Note],
        *,
        weights: RankingWeights | None = None,
        token_budget: int = DEFAULT_TOKEN_BUDGET,
        provider: Provider | None = None,
    ) -> None:
        self._notes = notes
        self._resolver = RelationshipResolver(notes)
        self._report = self._resolver.resolve_all()
        self._by_relpath = {n.relpath: n for n in notes}
        self._parser = IntentParser()
        self._index = LexicalIndex(notes)
        self._ranker = Ranker(self._index, self._report, weights)
        self._context = QueryContextBuilder(
            self._index, self._report, token_budget=token_budget
        )
        self._provider = provider or get_provider("mock")

    # ============================================================ v0.2 API
    def ask(self, question: str) -> QueryResult:
        """Answer a question and return the stable v0.2 :class:`QueryResult`."""
        answer, _ = self.run(question)
        matches = tuple(
            SourceRef(id=c.id, title=c.title, relpath=c.relpath) for c in answer.citations
        )
        return QueryResult(answer.intent, answer.question, answer.answer, matches)

    # ============================================================ v0.3 API
    def run(
        self, question: str, *, want_trace: bool = False
    ) -> tuple[QueryAnswer, QueryTrace | None]:
        """Answer a question, returning a cited :class:`QueryAnswer` and optional trace."""
        parsed = self._parser.parse(question)
        trace = QueryTrace(parsed=parsed) if want_trace else None

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
            return QueryAnswer(Intent.SEARCH, parsed.question, "No searchable terms found.")
        t0 = time.perf_counter()
        candidates = self._index.candidates(terms)
        t1 = time.perf_counter()
        ranked = self._ranker.rank(terms, candidates, phrase=" ".join(terms))
        t2 = time.perf_counter()
        top = ranked[:limit]
        if not top:
            answer = f"No notes match: {', '.join(terms)}."
        else:
            answer = (
                f"{len(ranked)} note(s) match {terms}; top {len(top)} by relevance."
            )
        citations = tuple(citation_from_scored(s) for s in top)
        self._fill_trace(
            trace, candidates, ranked, top, provider="none",
            timings={"retrieval": (t1 - t0) * 1000, "ranking": (t2 - t1) * 1000},
        )
        return QueryAnswer(Intent.SEARCH, parsed.question, answer, citations)

    def _projects_mentioning(
        self, parsed: ParsedQuery, trace: QueryTrace | None
    ) -> QueryAnswer:
        term = normalize(parsed.target or "")
        if not term:
            return QueryAnswer(
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
        citations = tuple(citation_from_scored(s) for s in ranked)
        self._fill_trace(
            trace, {n.relpath for n in hits}, ranked, ranked, provider="none", timings={}
        )
        return QueryAnswer(Intent.PROJECTS_MENTIONING, parsed.question, answer, citations)

    def _related_to(self, parsed: ParsedQuery, trace: QueryTrace | None) -> QueryAnswer:
        term = normalize(parsed.target or "")
        if not term:
            return QueryAnswer(Intent.RELATED_TO, parsed.question, "No search term found.")
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
        if not ranked:
            answer = f"No notes related to '{parsed.target}'."
        else:
            answer = (
                f"{len(ranked)} note(s) related to '{parsed.target}' "
                f"(direct matches and neighbours)."
            )
        citations = tuple(citation_from_scored(s) for s in ranked)
        context = self._context.build([s.relpath for s in ranked]) if ranked else None
        self._fill_trace(
            trace, set(related), ranked, ranked, provider="none", timings={}, context=context
        )
        return QueryAnswer(Intent.RELATED_TO, parsed.question, answer, citations)

    def _summarize_project(
        self, parsed: ParsedQuery, trace: QueryTrace | None
    ) -> QueryAnswer:
        name = parsed.target or parsed.question
        loader = ProjectContextLoader(self._notes)
        try:
            package = loader.load(name)
        except ProjectNotFoundError as exc:
            return QueryAnswer(Intent.SUMMARIZE_PROJECT, parsed.question, str(exc))
        t0 = time.perf_counter()
        response = self._provider.summarize(package, model_role="research")
        t1 = time.perf_counter()
        citations = tuple(
            Citation(
                id=s.id, title=s.title, relpath=s.relpath,
                confidence=1.0 if s.relpath == package.sources[0].relpath else 0.8,
                reason="in assembled project context",
            )
            for s in package.sources
        )
        if trace is not None:
            context = self._context.build([s.relpath for s in package.sources])
            trace.candidates = tuple(sorted(s.relpath for s in package.sources))
            trace.context = context
            trace.provider = self._provider.name
            trace.timings_ms = {"provider": (t1 - t0) * 1000}
            trace.token_counts = {
                "context": context.total_tokens,
                "summary": estimate_tokens(response.summary),
            }
        return QueryAnswer(
            Intent.SUMMARIZE_PROJECT, parsed.question, response.summary, citations
        )

    def _explain(self, parsed: ParsedQuery, trace: QueryTrace | None) -> QueryAnswer:
        left_note = self._resolve_note(parsed.left or "")
        right_note = self._resolve_note(parsed.right or "")
        if left_note is None or right_note is None:
            missing = parsed.left if left_note is None else parsed.right
            return QueryAnswer(
                Intent.EXPLAIN_RELATIONSHIP, parsed.question,
                f"Could not find a note matching '{missing}'.",
            )
        lp, rp = left_note.relpath, right_note.relpath
        direct = rp in self._report.outgoing(lp) or lp in self._report.outgoing(rp)
        l_neighbours = set(self._report.outgoing(lp)) | set(self._report.incoming(lp))
        r_neighbours = set(self._report.outgoing(rp)) | set(self._report.incoming(rp))
        shared = sorted((l_neighbours & r_neighbours) - {lp, rp})

        lt = left_note.title or left_note.path.stem
        rt = right_note.title or right_note.path.stem
        parts: list[str] = []
        if direct:
            parts.append(f"'{lt}' and '{rt}' are directly linked.")
        if shared:
            names = ", ".join((self._by_relpath[s].title or s) for s in shared)
            parts.append(f"They share {len(shared)} connected note(s): {names}.")
        if not parts:
            parts.append(f"No direct link or shared neighbour connects '{lt}' and '{rt}'.")
        answer = " ".join(parts)

        cited = [left_note, right_note, *(self._by_relpath[s] for s in shared)]
        citations = tuple(
            Citation(
                id=n.id, title=n.title or n.path.stem, relpath=n.relpath,
                confidence=1.0 if n.relpath in (lp, rp) else 0.6,
                reason="relationship endpoint" if n.relpath in (lp, rp) else "shared neighbour",
            )
            for n in cited
        )
        if trace is not None:
            context = self._context.build([lp, rp, *shared])
            trace.candidates = tuple(sorted({lp, rp, *shared}))
            trace.context = context
            trace.token_counts = {"context": context.total_tokens}
        return QueryAnswer(Intent.EXPLAIN_RELATIONSHIP, parsed.question, answer, citations)

    # ============================================================ helpers
    def _rank_subset(
        self,
        terms: list[str],
        notes: list[Note],
        *,
        phrase: str | None = None,
        neighbor_boost: frozenset[str] = frozenset(),
    ) -> list[ScoredNote]:
        """Rank a pre-selected subset, falling back to relpath order if terms don't score."""
        candidate_set = {n.relpath for n in notes}
        ranked = self._ranker.rank(
            terms, candidate_set, phrase=phrase, neighbor_boost=neighbor_boost
        )
        ranked_paths = {s.relpath for s in ranked}
        # Preselected notes that scored zero (e.g. matched only via a linked note) are
        # still valid answers; append them in stable order with zero-confidence citations.
        leftovers = sorted(
            (n for n in notes if n.relpath not in ranked_paths), key=lambda n: n.relpath
        )
        from jarvis_core.query.ranking import RankingExplanation

        for n in leftovers:
            ranked.append(
                ScoredNote(n, 0.0, 0.0, RankingExplanation(n.relpath, 0.0, ()))
            )
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

    @staticmethod
    def _fill_trace(
        trace: QueryTrace | None,
        candidates: set[str],
        ranked: list[ScoredNote],
        top: list[ScoredNote],
        *,
        provider: str,
        timings: dict[str, float],
        context: QueryContext | None = None,
    ) -> None:
        if trace is None:
            return
        trace.candidates = tuple(sorted(candidates))
        trace.ranked = tuple(top)
        top_paths = {s.relpath for s in top}
        trace.excluded_candidates = tuple(
            sorted(rp for rp in candidates if rp not in top_paths)
        )
        trace.provider = provider
        trace.timings_ms = dict(timings)
        if context is not None:
            trace.context = context
            trace.token_counts = {"context": context.total_tokens}
