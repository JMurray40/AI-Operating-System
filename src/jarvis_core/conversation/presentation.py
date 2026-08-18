"""One immutable, sanitized presentation result (AC-05-05R).

A single public object built once from the internal turn result and consumed identically by
the in-process API, the text renderer, the JSON renderer, and the CLI. Raw provider output
never crosses this boundary: the answer and every claim are sanitized here, and the raw
provider payload is already discarded upstream (it is never stored in the result, evidence,
session history, trace, or errors).

AC-05-05R residual: ``claims``/``usage``/``cost`` were retained as plain mutable dicts (and
``to_dict()`` embedded ``self.usage``/``self.cost`` directly, with no copy at all), so a
caller mutating a dict obtained from one accessor could corrupt the SAME retained
``PresentationResult`` and change what a later ``to_dict()``/``to_text()`` call on that same
object returns. Every collection here is now deep-frozen at construction (reusing the
AC-05-01R immutability helpers), and ``to_dict()`` deep-thaws fresh, fully detached mutable
copies for its output — public serialization may still return ordinary dicts/lists, but
mutating them can never reach back into the retained object or any later render of it.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_core.conversation.contract import TerminalState
from jarvis_core.conversation.evidence import AnswerEvidence, Claim
from jarvis_core.conversation.immutable import deep_thaw, freeze_mapping, freeze_tuple_of_mappings
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
    # V05-PT-37: fixed, redacted safe fields for a typed local-profile block. Empty
    # (and inert) for every non-local turn.
    details: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # AC-05-05R: deep-freeze every retained collection so no caller-held reference —
        # including one returned by an earlier accessor on THIS SAME object — can mutate the
        # retained presentation or change what a later render of it returns.
        object.__setattr__(self, "claims", freeze_tuple_of_mappings(self.claims))
        object.__setattr__(self, "limitations", tuple(self.limitations))
        object.__setattr__(self, "citations", tuple(self.citations))
        object.__setattr__(self, "usage", freeze_mapping(self.usage))
        object.__setattr__(self, "cost", freeze_mapping(self.cost))
        object.__setattr__(self, "details", freeze_mapping(self.details))

    def to_dict(self) -> dict[str, object]:
        # Deep-thaw fresh, fully DETACHED mutable copies for the output: a caller is free to
        # mutate this dict (that is the point of "public serialization returns a fresh
        # copy"), but doing so can never reach back into the retained frozen state above.
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
                "claims": [deep_thaw(c) for c in self.claims],
                "limitations": list(self.limitations),
                "citations": list(self.citations),
                "usage": deep_thaw(self.usage),
                "cost": deep_thaw(self.cost),
                "details": deep_thaw(self.details),
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
    if evidence is None and a.status is TerminalState.COMPLETED:
        # V05-PT-37 (Handoff 147 §4): a completed local-profile turn carries the
        # model's own closed-schema answer/limitations/citations directly — there is
        # no claims taxonomy to render here (that belongs to the remote/mock contract
        # only; a completed remote/mock attempt always has ``evidence`` set). ``a.text``
        # was already fully validated by the adapter's hostile-output boundary before
        # reaching COMPLETED; it still passes through ``sanitize_markdown`` here for
        # the same defense-in-depth every other public-surface string gets.
        pub_claims: tuple[dict[str, object], ...] = ()
        supported = tuple(a.local_citations)
        limitations = tuple(sanitize_markdown(lim) for lim in a.local_limitations)
        answer = sanitize_markdown(a.text) if a.text is not None else None
    else:
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
        details=dict(a.details),
    )


__all__ = ["PresentationResult", "answer_from_claims", "present"]
