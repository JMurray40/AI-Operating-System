"""Normalized turn/attempt results shared by the application API and the CLI (§9).

Text and JSON render one semantic result: terminal status, coverage, citations,
limitations, usage/cost provenance, and a one-based turn number. Failure classes are
redacted and taxonomic — never a raw provider error.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from jarvis_core.conversation.contract import (
    Coverage,
    FailureClass,
    TerminalState,
)
from jarvis_core.conversation.evidence import AnswerEvidence
from jarvis_core.providers.conversation import Cost, Usage, UsageProvenance


def _unknown_usage() -> Usage:
    return Usage(None, None, UsageProvenance.UNKNOWN)


def _unknown_cost() -> Cost:
    return Cost(None, "USD", "unset", UsageProvenance.UNKNOWN)


@dataclass(frozen=True)
class AttemptResult:
    """The outcome of exactly one dispatch attempt (terminal once)."""

    attempt_id: str
    status: TerminalState
    failure: FailureClass | None = None
    message: str | None = None  # redacted, safe, actionable
    text: str | None = None
    evidence: AnswerEvidence | None = None
    usage: Usage = field(default_factory=_unknown_usage)
    cost: Cost = field(default_factory=_unknown_cost)
    finish_reason: str = "unknown"
    elapsed_ms: float | None = None
    # V05-PT-37: fixed, redacted safe fields for a typed local-profile block (never
    # raw runtime/model/host/error text). Empty for every existing provider/path.
    details: Mapping[str, object] = field(default_factory=dict)
    # V05-PT-37 (Handoff 147 §4): the local profile's closed response shape carries its
    # own model-declared ``limitations``/``citations`` directly — never a claims-derived
    # ``evidence.AnswerEvidence`` (that taxonomy belongs to the remote/mock claims
    # contract only). Empty for every non-local attempt.
    local_limitations: tuple[str, ...] = ()
    local_citations: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "attempt_id": self.attempt_id,
            "status": self.status.value,
            "failure": self.failure.value if self.failure else None,
            "message": self.message,
            "text": self.text,
            "evidence": self.evidence.to_dict() if self.evidence else None,
            "usage": self.usage.to_dict(),
            "cost": self.cost.to_dict(),
            "finish_reason": self.finish_reason,
            "elapsed_ms": self.elapsed_ms,
            "details": dict(self.details),
            "local_limitations": list(self.local_limitations),
            "local_citations": list(self.local_citations),
        }


@dataclass(frozen=True)
class TurnResult:
    """One turn's public result: identity, coverage, and the terminal attempt."""

    turn_number: int
    request_id: str
    session_id: str
    snapshot_digest: str
    coverage: Coverage
    attempt: AttemptResult

    def to_dict(self) -> dict[str, object]:
        return {
            "turn_number": self.turn_number,
            "request_id": self.request_id,
            "session_id": self.session_id,
            "snapshot_digest": self.snapshot_digest,
            "coverage": self.coverage.value,
            "attempt": self.attempt.to_dict(),
        }


__all__ = ["AttemptResult", "TurnResult"]
