"""Structured, versioned query results for v0.3.1 (deterministic, provider-independent).

Every affected structured output carries ``contract_version``. Ranking exposes
``relative_relevance`` (a query-local ranking normalization), never ``confidence``, and no
numeric answer confidence is emitted (ADR-0014). Citations bind a stable identity to an
exact source revision and a deterministic passage (ADR-0016).
"""
from __future__ import annotations

from dataclasses import dataclass

from jarvis_core.query.contract import CONTRACT_VERSION
from jarvis_core.query.intent import Intent
from jarvis_core.query.passages import Locator
from jarvis_core.query.ranking import ScoredNote


@dataclass(frozen=True)
class Citation:
    """A passage-and-revision citation (ADR-0016)."""

    source_id: str
    source_identity_kind: str          # 'explicit' | 'path_derived'
    title: str
    relpath: str
    source_fingerprint: str
    locator: Locator
    excerpt: str
    reason: str
    relative_relevance: float | None = None  # query-local ranking value; None if unranked

    def to_dict(self) -> dict[str, object]:
        return {
            "contract_version": CONTRACT_VERSION,
            "source_id": self.source_id,
            "source_identity_kind": self.source_identity_kind,
            "title": self.title,
            "relpath": self.relpath,
            "source_fingerprint": self.source_fingerprint,
            "locator": self.locator.to_dict(),
            "excerpt": self.excerpt,
            "relative_relevance": self.relative_relevance,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class QueryAnswer:
    """A complete answer: intent, prose, cited sources, and a safe excluded count."""

    intent: Intent
    question: str
    answer: str
    citations: tuple[Citation, ...] = ()
    excluded_count: int = 0  # aggregate only; never identifies an excluded source

    # Reserved for a later evidence-assessment contract; unavailable in v0.3.1 (ADR-0014).
    answer_confidence: None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "contract_version": CONTRACT_VERSION,
            "intent": self.intent.value,
            "question": self.question,
            "answer": self.answer,
            "answer_confidence": self.answer_confidence,
            "citations": [c.to_dict() for c in self.citations],
            "excluded_count": self.excluded_count,
        }


def citation_from_scored(
    scored: ScoredNote,
    *,
    source_id: str,
    source_identity_kind: str,
    source_fingerprint: str,
    locator: Locator,
    excerpt: str,
) -> Citation:
    """Build a passage citation from a ranked note, carrying its relative relevance."""
    reasons = scored.explanation.reasons()
    reason = "; ".join(reasons[:3]) if reasons else "matched"
    note = scored.note
    return Citation(
        source_id=source_id,
        source_identity_kind=source_identity_kind,
        title=note.title or note.path.stem,
        relpath=note.relpath,
        source_fingerprint=source_fingerprint,
        locator=locator,
        excerpt=excerpt,
        reason=reason,
        relative_relevance=scored.relative_relevance,
    )
