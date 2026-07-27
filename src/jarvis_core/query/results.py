"""Structured, serializable results for the v0.3 query engine.

These types are provider-independent and deterministic: field order is fixed and no
timestamps or randomness leak in, so identical questions on identical vaults serialize
byte-for-byte identically.
"""
from __future__ import annotations

from dataclasses import dataclass

from jarvis_core.query.intent import Intent
from jarvis_core.query.ranking import ScoredNote


@dataclass(frozen=True)
class Citation:
    """Where a piece of an answer came from, and why it was selected."""

    id: str | None
    title: str
    relpath: str
    confidence: float
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "title": self.title,
            "relpath": self.relpath,
            "confidence": self.confidence,
            "reason": self.reason,
        }


def citation_from_scored(scored: ScoredNote) -> Citation:
    """Build a citation from a ranked note, using its top ranking reasons."""
    reasons = scored.explanation.reasons()
    reason = "; ".join(reasons[:3]) if reasons else "matched"
    note = scored.note
    return Citation(
        id=note.id,
        title=note.title or note.path.stem,
        relpath=note.relpath,
        confidence=scored.confidence,
        reason=reason,
    )


@dataclass(frozen=True)
class QueryAnswer:
    """A complete answer: intent, prose answer, and ranked, cited sources."""

    intent: Intent
    question: str
    answer: str
    citations: tuple[Citation, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "intent": self.intent.value,
            "question": self.question,
            "answer": self.answer,
            "citations": [c.to_dict() for c in self.citations],
        }
