"""One immutable, sanitized presentation result (AC-05-05).

A single public object built once from the internal turn result and consumed identically by
the in-process API, the text renderer, the JSON renderer, and the CLI. Raw provider output
never crosses this boundary: the answer and every claim are sanitized here, and the raw
provider payload is already discarded upstream (it is never stored in the result, evidence,
session history, trace, or errors).
"""
from __future__ import annotations

from dataclasses import dataclass

from jarvis_core.conversation.evidence import AnswerEvidence, Claim
from jarvis_core.conversation.results import TurnResult
from jarvis_core.conversation.sanitize import sanitize_markdown


def _public_claim(claim: Claim) -> dict[str, object]:
    return {
        "text": sanitize_markdown(claim.text),
        "evidence_type": claim.evidence_type.value,
        "citations": list(claim.citations),
    }


def answer_from_claims(evidence: AnswerEvidence | None) -> str:
    """Render a sanitized answer from validated claims (never the raw provider payload)."""
    if evidence is None:
        return ""
    parts: list[str] = []
    for claim in evidence.claims:
        marker = f" [{','.join(claim.citations)}]" if claim.citations else ""
        parts.append(sanitize_markdown(claim.text) + marker)
    return "\n".join(parts)


@dataclass(frozen=True)
class PresentationResult:
    """The immutable, sanitized public result surface."""

    turn_number: int
    request_id: str
    session_id: str
    snapshot_digest: str
    status: str
    coverage: str
    failure: str | None
    message: str | None
    answer: str | None
    claims: tuple[dict[str, object], ...]
    limitations: tuple[str, ...]
    citations: tuple[str, ...]
    usage: dict[str, object]
    cost: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "turn_number": self.turn_number,
            "request_id": self.request_id,
            "session_id": self.session_id,
            "snapshot_digest": self.snapshot_digest,
            "coverage": self.coverage,
            "attempt": {
                "status": self.status,
                "failure": self.failure,
                "message": self.message,
                "answer": self.answer,
                "claims": [dict(c) for c in self.claims],
                "limitations": list(self.limitations),
                "citations": list(self.citations),
                "usage": self.usage,
                "cost": self.cost,
            },
        }

    def to_text(self) -> str:
        lines = [f"Turn {self.turn_number} | status: {self.status} | coverage: {self.coverage}"]
        if self.failure is not None:
            lines.append(f"failure: {self.failure}")
            if self.message:
                lines.append(f"  {self.message}")
        if self.answer:
            lines.append("answer:")
            lines.append(self.answer)
        for lim in self.limitations:
            lines.append(f"limitation: {lim}")
        usage = self.usage
        cost = self.cost
        lines.append(
            f"usage: in={usage.get('input_tokens')} out={usage.get('output_tokens')} "
            f"({usage.get('provenance')}) | "
            f"cost: {cost.get('amount_usd')} {cost.get('currency')} ({cost.get('provenance')})"
        )
        return "\n".join(lines)


def present(turn: TurnResult) -> PresentationResult:
    """Build the single sanitized presentation object from a turn result."""
    a = turn.attempt
    evidence = a.evidence
    claims = evidence.claims if evidence is not None else ()
    pub_claims = tuple(_public_claim(c) for c in claims)
    supported = tuple(sorted({cid for c in claims for cid in c.citations}))
    limitations = evidence.limitations if evidence is not None else ()
    answer = answer_from_claims(evidence) if a.text is not None else None
    return PresentationResult(
        turn_number=turn.turn_number,
        request_id=turn.request_id,
        session_id=turn.session_id,
        snapshot_digest=turn.snapshot_digest,
        status=a.status.value,
        coverage=turn.coverage.value,
        failure=a.failure.value if a.failure else None,
        message=sanitize_markdown(a.message) if a.message else None,
        answer=answer,
        claims=pub_claims,
        limitations=limitations,
        citations=supported,
        usage=a.usage.to_dict(),
        cost=a.cost.to_dict(),
    )


__all__ = ["PresentationResult", "answer_from_claims", "present"]
