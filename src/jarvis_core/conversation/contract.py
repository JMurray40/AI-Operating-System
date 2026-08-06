"""Versioned contract surface for v0.5 visible-context conversation (H07 §7).

Central home for the conversation-layer version strings, the closed taxonomies
(evidence type, coverage, failure class, remote eligibility), the CLI exit-code
contract, and the typed error hierarchy. Everything here is provider-neutral and
imports only the normalized provider boundary, never a wire format.
"""

from __future__ import annotations

from enum import Enum

from jarvis_core.providers.conversation import (
    PROVIDER_CONTRACT_VERSION,
    TerminalState,
    UsageProvenance,
)


def as_int(value: object) -> int:
    """Coerce a loosely-typed dict value to int without an unsafe cast (0 on failure)."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str) and value.strip().lstrip("-").isdigit():
        return int(value)
    return 0


# ------------------------------------------------------------------ versions (H07 §7)
CONVERSATION_CONTRACT_VERSION = "jarvis.conversation.v0.5.0"
CONTEXT_SNAPSHOT_VERSION = "jarvis.conversation-context.v0.5.0"
EGRESS_APPROVAL_VERSION = "jarvis.conversation-egress.v0.5.0"
PROMPT_CONTRACT_VERSION = "jarvis.conversation-prompt.v0.5.0"
CONVERSATION_TRACE_VERSION = "jarvis.conversation-trace.v0.5.0"
RESPONSE_CONTRACT_VERSION = "jarvis.conversation-response.v0.5.0"

# Bound prompt-construction component versions (each is separately bound into the
# snapshot and the approval; changing any one invalidates a prior approval — C09).
PROMPT_TEMPLATE_VERSION = "jarvis.conversation-prompt-template.v0.5.0"
PROMPT_ASSEMBLER_VERSION = "jarvis.conversation-prompt-assembler.v0.5.0"
HISTORY_SERIALIZATION_VERSION = "jarvis.conversation-history.v0.5.0"
TOKEN_ESTIMATOR_VERSION = "jarvis.conversation-token-estimator.v0.5.0"
SAFETY_INSTRUCTION_VERSION = "jarvis.conversation-safety.v0.5.0"
OUTPUT_RESERVE_VERSION = "jarvis.conversation-output-reserve.v0.5.0"

# Re-exported for convenience so callers bind one import surface.
__provider_contract_version__ = PROVIDER_CONTRACT_VERSION


# ------------------------------------------------------------------ evidence taxonomy
class EvidenceType(str, Enum):
    """Closed material-claim taxonomy (R6 / C18). Distinct and non-overlapping."""

    FACT = "fact"  # requires current valid citation(s)
    INFERENCE = "inference"  # cites every material premise
    MODEL_KNOWLEDGE = "model_knowledge"  # visibly NOT vault-supported
    UNKNOWN = "unknown"  # the model could not answer
    ASSUMPTION = "assumption"  # a visible reference-resolution assumption


class Coverage(str, Enum):
    """Answer coverage (R6 / C19). Incomplete-only is never 'fully backed'."""

    COMPLETE = "complete"
    PARTIAL = "partial"
    INCOMPLETE = "incomplete"
    NONE = "none"


# ------------------------------------------------------------------ failure classes
class FailureClass(str, Enum):
    """Distinct, redacted, actionable failure classes (R8 / C23)."""

    UNAVAILABLE_CREDENTIAL = "unavailable_credential"
    UNAVAILABLE_PROVIDER = "unavailable_provider"
    NETWORK_DENIED = "network_denied"
    POLICY_BLOCKED = "policy_blocked"
    VALIDATION_FAILED = "validation_failed"
    BUDGET_EXCEEDED = "budget_exceeded"
    PROVIDER_TIMEOUT = "provider_timeout"
    CANCELLED = "cancelled"
    MALFORMED_RESPONSE = "malformed_response"
    EVIDENCE_FAILED = "evidence_failed"
    DRIFT_BLOCKED = "drift_blocked"
    INTERNAL = "internal"


# ------------------------------------------------------------------ remote eligibility
class RemoteEligibility(str, Enum):
    ELIGIBLE = "eligible"
    DENIED = "denied"


# Exact sensitivity eligibility for a remote destination (H07 §4.2). Missing/unknown
# and anything not listed is denied *before retrieval* (fail closed).
_REMOTE_ELIGIBLE_SENSITIVITIES = frozenset({"public", "internal"})


def remote_eligibility(sensitivity: str | None) -> RemoteEligibility:
    """Return remote eligibility for a single item's sensitivity, failing closed."""
    if sensitivity is None:
        return RemoteEligibility.DENIED
    label = sensitivity.strip().lower()
    if label in _REMOTE_ELIGIBLE_SENSITIVITIES:
        return RemoteEligibility.ELIGIBLE
    return RemoteEligibility.DENIED


# ------------------------------------------------------------------ CLI exit codes (§9)
class ExitCode(int, Enum):
    """Public CLI exit contract; never the raw provider status."""

    SUCCESS = 0
    USER_DECLINED = 3  # user declined or cancelled
    POLICY_BLOCKED = 4  # policy/eligibility block before dispatch
    PROVIDER_UNAVAILABLE = 5  # provider/credential/network unavailable
    VALIDATION_FAILED = 6  # request/snapshot/evidence validation failure
    INTERNAL_ERROR = 7  # unexpected internal failure


_FAILURE_EXIT = {
    FailureClass.UNAVAILABLE_CREDENTIAL: ExitCode.PROVIDER_UNAVAILABLE,
    FailureClass.UNAVAILABLE_PROVIDER: ExitCode.PROVIDER_UNAVAILABLE,
    FailureClass.NETWORK_DENIED: ExitCode.PROVIDER_UNAVAILABLE,
    FailureClass.POLICY_BLOCKED: ExitCode.POLICY_BLOCKED,
    FailureClass.VALIDATION_FAILED: ExitCode.VALIDATION_FAILED,
    FailureClass.BUDGET_EXCEEDED: ExitCode.VALIDATION_FAILED,
    FailureClass.PROVIDER_TIMEOUT: ExitCode.PROVIDER_UNAVAILABLE,
    FailureClass.CANCELLED: ExitCode.USER_DECLINED,
    FailureClass.MALFORMED_RESPONSE: ExitCode.VALIDATION_FAILED,
    FailureClass.EVIDENCE_FAILED: ExitCode.VALIDATION_FAILED,
    FailureClass.DRIFT_BLOCKED: ExitCode.VALIDATION_FAILED,
    FailureClass.INTERNAL: ExitCode.INTERNAL_ERROR,
}


def exit_code_for_failure(failure: FailureClass) -> ExitCode:
    """Map a redacted failure class to the public CLI exit code."""
    return _FAILURE_EXIT[failure]


# ------------------------------------------------------------------ error hierarchy
class ConversationError(Exception):
    """Base for all typed conversation errors (fail-closed, redacted)."""

    failure_class: FailureClass = FailureClass.INTERNAL


class ValidationError(ConversationError):
    failure_class = FailureClass.VALIDATION_FAILED


class PolicyBlockedError(ConversationError):
    failure_class = FailureClass.POLICY_BLOCKED


class BudgetError(ConversationError):
    failure_class = FailureClass.BUDGET_EXCEEDED


class ApprovalError(ConversationError):
    failure_class = FailureClass.VALIDATION_FAILED


class DriftError(ConversationError):
    failure_class = FailureClass.DRIFT_BLOCKED


class ProviderUnavailableError(ConversationError):
    failure_class = FailureClass.UNAVAILABLE_PROVIDER


class CredentialUnavailableError(ConversationError):
    failure_class = FailureClass.UNAVAILABLE_CREDENTIAL


class EvidenceError(ConversationError):
    failure_class = FailureClass.EVIDENCE_FAILED


__all__ = [
    "CONTEXT_SNAPSHOT_VERSION",
    "CONVERSATION_CONTRACT_VERSION",
    "CONVERSATION_TRACE_VERSION",
    "EGRESS_APPROVAL_VERSION",
    "HISTORY_SERIALIZATION_VERSION",
    "OUTPUT_RESERVE_VERSION",
    "PROMPT_ASSEMBLER_VERSION",
    "PROMPT_CONTRACT_VERSION",
    "PROMPT_TEMPLATE_VERSION",
    "PROVIDER_CONTRACT_VERSION",
    "RESPONSE_CONTRACT_VERSION",
    "SAFETY_INSTRUCTION_VERSION",
    "TOKEN_ESTIMATOR_VERSION",
    "ApprovalError",
    "BudgetError",
    "ConversationError",
    "Coverage",
    "CredentialUnavailableError",
    "DriftError",
    "EvidenceError",
    "EvidenceType",
    "ExitCode",
    "FailureClass",
    "PolicyBlockedError",
    "ProviderUnavailableError",
    "RemoteEligibility",
    "TerminalState",
    "UsageProvenance",
    "ValidationError",
    "as_int",
    "exit_code_for_failure",
    "remote_eligibility",
]
