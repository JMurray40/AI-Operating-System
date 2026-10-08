"""Redacted, allowlisted conversation trace (R9, C26).

Trace is an event audit, not chain-of-thought. Only allowlisted event names and safe
scalar fields are retained; message bodies, excerpts, secrets, excluded identities, raw
payloads, absolute private paths, and raw errors can never enter it. Values are coerced to
safe scalars and bounded in length.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_core.conversation.contract import CONVERSATION_TRACE_VERSION

_ALLOWED_EVENTS = frozenset(
    {
        "session_created",
        "prepare_started",
        "authorization_applied",
        "retrieval_completed",
        "snapshot_created",
        "context_removed",
        "approval_created",
        "revalidation_passed",
        "prompt_assembled",
        "dispatch_started",
        "dispatch_completed",
        "attempt_cancelled",
        "attempt_failed",
        "evidence_validated",
        "rendered",
        "session_reset",
        # V05-PT-37: local-profile readiness/capacity lifecycle events (Handoff 147
        # §3.2/§5). Never carry raw runtime/model/host/error text — only the fixed
        # safe fields allowlisted below.
        "local_admission_checked",
        "local_admission_blocked",
        "local_readiness_changed",
    }
)

_ALLOWED_FIELDS = frozenset(
    {
        "turn_number",
        "request_id",
        "session_id",
        "attempt_id",
        "snapshot_digest",
        "policy_version",
        "provider_id",
        "model_id",
        "adapter_version",
        "contract_version",
        "provider_contract_version",
        "items_included",
        "items_omitted",
        "excluded_count",
        "context_tokens_used",
        "input_tokens",
        "output_reserve_tokens",
        "total_tokens",
        "coverage",
        "supported_count",
        "model_knowledge_count",
        "status",
        "failure",
        "finish_reason",
        "usage_provenance",
        "cost_provenance",
        "elapsed_ms",
        "eligible",
        "is_remote",
        # V05-PT-37: local-profile fixed safe fields (never raw runtime/model/host/
        # error text; see LocalGatewayBlocked.details / AttemptResult.details).
        "destination_profile_id",
        "local_state",
        "reason",
        "warm_class",
        "retry_eligible",
    }
)

_MAX_STR = 200


def _safe_value(value: object) -> object | None:
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return value[:_MAX_STR]
    return None


@dataclass(frozen=True)
class TraceEvent:
    name: str
    fields: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {"event": self.name, **self.fields}


@dataclass
class Trace:
    """A bounded, redacted event log for one session."""

    events: list[TraceEvent] = field(default_factory=list)
    trace_version: str = CONVERSATION_TRACE_VERSION

    def record(self, name: str, **fields: object) -> None:
        if name not in _ALLOWED_EVENTS:
            return  # silently drop unknown events rather than leak
        safe: dict[str, object] = {}
        for key, value in fields.items():
            if key not in _ALLOWED_FIELDS:
                continue
            coerced = _safe_value(value)
            if coerced is not None or value is None:
                safe[key] = coerced
        self.events.append(TraceEvent(name, safe))

    def to_dict(self) -> dict[str, object]:
        return {
            "trace_version": self.trace_version,
            "events": [e.to_dict() for e in self.events],
        }


__all__ = ["Trace", "TraceEvent"]
