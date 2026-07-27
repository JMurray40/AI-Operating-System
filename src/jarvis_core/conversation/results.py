"""Conversational answer + streaming event types (provider-independent)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from jarvis_core.conversation.explanation import Statement
from jarvis_core.query.results import Citation


@dataclass(frozen=True)
class ConflictNote:
    """Two or more sources that appear to disagree about the same subject."""

    subject: str
    relpaths: tuple[str, ...]
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {"subject": self.subject, "relpaths": list(self.relpaths), "reason": self.reason}


@dataclass(frozen=True)
class ConversationAnswer:
    """A conversational answer with full provenance."""

    question: str
    effective_query: str
    text: str
    confidence: float
    reasoning_summary: str
    citations: tuple[Citation, ...] = ()
    statements: tuple[Statement, ...] = ()
    conflicts: tuple[ConflictNote, ...] = ()
    assumptions: tuple[str, ...] = ()
    provider: str = "none"
    status: str = "completed"  # 'completed' | 'failed'

    def to_dict(self) -> dict[str, object]:
        return {
            "question": self.question,
            "effective_query": self.effective_query,
            "text": self.text,
            "confidence": self.confidence,
            "reasoning_summary": self.reasoning_summary,
            "citations": [c.to_dict() for c in self.citations],
            "statements": [s.to_dict() for s in self.statements],
            "conflicts": [c.to_dict() for c in self.conflicts],
            "assumptions": list(self.assumptions),
            "provider": self.provider,
            "status": self.status,
        }


class StreamEventKind(str, Enum):
    """Normalized streaming events (Chat PRD architecture)."""

    STARTED = "started"
    DELTA = "delta"
    CITATION = "citation"
    USAGE = "usage"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class StreamEvent:
    """One normalized event in a streamed response."""

    kind: StreamEventKind
    text: str = ""
    data: dict[str, object] | None = None

    def to_dict(self) -> dict[str, object]:
        return {"kind": self.kind.value, "text": self.text, "data": self.data}
