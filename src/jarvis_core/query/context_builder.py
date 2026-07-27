"""Token-budgeted, provider-independent context assembly with a hard budget invariant (R2).

Invariant: ``0 <= total_tokens <= token_budget`` for every build. Negative budgets fail at
construction. A zero budget yields no chunks. Oversized chunks are deterministically
truncated to the remaining allowance or omitted with a typed reason — never admitted whole
and never assigned a fictional one-token minimum. A deterministic per-chunk separator
overhead (charged between chunks) counts toward the total.

Authorization is enforced upstream: this builder only sees the request-authorized index,
so excluded sources cannot enter context (ADR-0015).
"""
from __future__ import annotations

from dataclasses import dataclass

from jarvis_core.models.base import NoteType
from jarvis_core.models.note import Note
from jarvis_core.query.contract import CONTRACT_VERSION
from jarvis_core.query.index import LexicalIndex
from jarvis_core.relationships.resolver import ResolutionReport

DEFAULT_TOKEN_BUDGET = 4000
#: Deterministic separator/wrapper overhead charged for each chunk after the first.
SEPARATOR_TOKENS = 1
_EXCERPT_WORDS = 60


def estimate_tokens(text: str) -> int:
    """Deterministic, model-agnostic token estimate (whitespace-delimited words)."""
    return len(text.split())


@dataclass(frozen=True)
class ContextChunk:
    relpath: str
    title: str
    role: str          # 'seed' | 'linked' | 'project' | 'support'
    tokens: int
    excerpt: str
    truncated: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "relpath": self.relpath,
            "title": self.title,
            "role": self.role,
            "tokens": self.tokens,
            "excerpt": self.excerpt,
            "truncated": self.truncated,
        }


@dataclass(frozen=True)
class ExcludedChunk:
    relpath: str
    title: str
    reason: str        # 'token_budget'

    def to_dict(self) -> dict[str, object]:
        return {"relpath": self.relpath, "title": self.title, "reason": self.reason}


@dataclass(frozen=True)
class QueryContext:
    included: tuple[ContextChunk, ...]
    excluded: tuple[ExcludedChunk, ...]
    total_tokens: int
    token_budget: int

    def to_dict(self) -> dict[str, object]:
        return {
            "contract_version": CONTRACT_VERSION,
            "token_budget": self.token_budget,
            "total_tokens": self.total_tokens,
            "included": [c.to_dict() for c in self.included],
            "excluded": [c.to_dict() for c in self.excluded],
        }


def _excerpt(note: Note) -> str:
    return " ".join(note.body.split()[:_EXCERPT_WORDS])


class QueryContextBuilder:
    """Expands seed notes into a bounded context along the authorized graph."""

    def __init__(
        self,
        index: LexicalIndex,
        report: ResolutionReport,
        *,
        token_budget: int = DEFAULT_TOKEN_BUDGET,
    ) -> None:
        if token_budget < 0:
            raise ValueError(f"token_budget must be non-negative, got {token_budget}")
        self._index = index
        self._report = report
        self._budget = token_budget

    def build(self, seed_relpaths: list[str]) -> QueryContext:
        planned = self._plan(seed_relpaths)
        included: list[ContextChunk] = []
        excluded: list[ExcludedChunk] = []
        total = 0
        for relpath, role in planned:
            note = self._index.note(relpath)
            title = note.title or note.path.stem
            words = _excerpt(note).split()
            base = len(words)
            sep = 0 if not included else SEPARATOR_TOKENS
            remaining = self._budget - total - sep
            if remaining <= 0 or base == 0:
                excluded.append(ExcludedChunk(relpath, title, "token_budget"))
                continue
            take = min(base, remaining)
            excerpt = " ".join(words[:take])
            total += sep + take
            included.append(
                ContextChunk(relpath, title, role, take, excerpt, truncated=take < base)
            )
        assert 0 <= total <= self._budget, "context budget invariant violated"
        return QueryContext(tuple(included), tuple(excluded), total, self._budget)

    def _plan(self, seed_relpaths: list[str]) -> list[tuple[str, str]]:
        planned: list[tuple[str, str]] = [(rp, "seed") for rp in seed_relpaths]
        seen = {rp for rp, _ in planned}
        neighbours: list[tuple[str, str]] = []
        for rp in seed_relpaths:
            for tgt in self._report.outgoing(rp):
                if tgt in seen or not self._index.contains(tgt):
                    continue
                seen.add(tgt)
                neighbours.append((tgt, self._role_for(self._index.note(tgt))))
            for src in self._report.incoming(rp):
                if src in seen or not self._index.contains(src):
                    continue
                seen.add(src)
                neighbours.append((src, "linked"))
        role_rank = {"seed": 0, "project": 1, "support": 2, "linked": 3}
        neighbours.sort(key=lambda x: (role_rank.get(x[1], 9), x[0]))
        planned.extend(neighbours)
        return planned

    @staticmethod
    def _role_for(note: Note) -> str:
        if note.type is NoteType.PROJECT:
            return "project"
        if note.type in (NoteType.RESOURCE, NoteType.CONCEPT, NoteType.DECISION):
            return "support"
        return "linked"
