"""Assemble a token-budgeted, provider-independent context from ranked notes.

Given the top-ranked seed notes, expand outward along the resolved graph (linked notes,
their parent projects, and supporting references) until a configurable token budget is
reached. The output is a plain data structure -- no provider, no prompt formatting -- so
any provider adapter can consume it (SYSTEM_PRINCIPLES: durable data stays provider-neutral).

Token counting is a deterministic word-count estimate. It is intentionally simple and
model-agnostic; a provider adapter that needs exact tokens can re-measure with its own
tokenizer without changing selection semantics.
"""
from __future__ import annotations

from dataclasses import dataclass

from jarvis_core.models.base import NoteType
from jarvis_core.models.note import Note
from jarvis_core.query.index import LexicalIndex
from jarvis_core.relationships.resolver import ResolutionReport

#: Default budget: generous for a small vault, bounded so large vaults never blow up.
DEFAULT_TOKEN_BUDGET = 4000


def estimate_tokens(text: str) -> int:
    """Deterministic, model-agnostic token estimate (whitespace-delimited words)."""
    return len(text.split())


@dataclass(frozen=True)
class ContextChunk:
    """One note admitted to (or considered for) the assembled context."""

    relpath: str
    title: str
    role: str  # 'seed' | 'linked' | 'project' | 'support'
    tokens: int
    excerpt: str

    def to_dict(self) -> dict[str, object]:
        return {
            "relpath": self.relpath,
            "title": self.title,
            "role": self.role,
            "tokens": self.tokens,
            "excerpt": self.excerpt,
        }


@dataclass(frozen=True)
class ExcludedChunk:
    relpath: str
    title: str
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {"relpath": self.relpath, "title": self.title, "reason": self.reason}


@dataclass(frozen=True)
class QueryContext:
    """The selected context plus what was left out and why."""

    included: tuple[ContextChunk, ...]
    excluded: tuple[ExcludedChunk, ...]
    total_tokens: int
    token_budget: int

    def to_dict(self) -> dict[str, object]:
        return {
            "token_budget": self.token_budget,
            "total_tokens": self.total_tokens,
            "included": [c.to_dict() for c in self.included],
            "excluded": [c.to_dict() for c in self.excluded],
        }


_EXCERPT_WORDS = 60


def _excerpt(note: Note) -> str:
    words = note.body.split()
    return " ".join(words[:_EXCERPT_WORDS])


class QueryContextBuilder:
    """Expands seed notes into a bounded context along the resolved graph."""

    def __init__(
        self,
        index: LexicalIndex,
        report: ResolutionReport,
        *,
        token_budget: int = DEFAULT_TOKEN_BUDGET,
    ) -> None:
        self._index = index
        self._report = report
        self._budget = token_budget

    def build(self, seed_relpaths: list[str]) -> QueryContext:
        """Assemble context from seeds (given in priority order)."""
        planned: list[tuple[str, str]] = [(rp, "seed") for rp in seed_relpaths]

        # Expand: parent projects, then one-hop neighbours, then supporting references.
        seen_plan = {rp for rp, _ in planned}
        neighbours: list[tuple[str, str]] = []
        for rp in seed_relpaths:
            for tgt in self._report.outgoing(rp):
                if tgt in seen_plan or not self._index.contains(tgt):
                    continue
                seen_plan.add(tgt)
                role = self._role_for(self._index.note(tgt))
                neighbours.append((tgt, role))
            for src in self._report.incoming(rp):
                if src in seen_plan or not self._index.contains(src):
                    continue
                seen_plan.add(src)
                neighbours.append((src, "linked"))
        # Deterministic: projects/support before generic links, then by relpath.
        role_rank = {"seed": 0, "project": 1, "support": 2, "linked": 3}
        neighbours.sort(key=lambda x: (role_rank.get(x[1], 9), x[0]))
        planned.extend(neighbours)

        included: list[ContextChunk] = []
        excluded: list[ExcludedChunk] = []
        total = 0
        for relpath, role in planned:
            note = self._index.note(relpath)
            title = note.title or note.path.stem
            excerpt = _excerpt(note)
            tokens = estimate_tokens(excerpt) or 1
            if total + tokens > self._budget and included:
                excluded.append(ExcludedChunk(relpath, title, "token_budget"))
                continue
            included.append(ContextChunk(relpath, title, role, tokens, excerpt))
            total += tokens
        return QueryContext(tuple(included), tuple(excluded), total, self._budget)

    @staticmethod
    def _role_for(note: Note) -> str:
        if note.type is NoteType.PROJECT:
            return "project"
        if note.type in (NoteType.RESOURCE, NoteType.CONCEPT, NoteType.DECISION):
            return "support"
        return "linked"
