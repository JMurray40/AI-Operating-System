"""Provider-neutral complete-response contract for v0.5 conversation (ADR-0024).

This module owns the *normalized* provider boundary shared by every conversation
adapter: the deterministic content-bearing request projection, the allowlisted
transport metadata, the opaque credential transport, and the normalized result. It
deliberately has no knowledge of any provider wire format — the Google translation
lives solely in :mod:`jarvis_core.providers.google_gemini` (WP2). It imports nothing
from the conversation application package, so the dependency direction is one-way
(``conversation`` depends on ``providers``, never the reverse).

Terminal states are exactly ``completed``, ``failed``, ``cancelled``, ``blocked``
(ADR-0024). Usage and cost carry explicit provenance so an absent value is never
silently rendered as zero. Raw provider payloads never cross this boundary.
"""

from __future__ import annotations

import threading
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol, runtime_checkable

PROVIDER_CONTRACT_VERSION = "jarvis.provider-complete-response.v0.5.0"

# Canonical, redacted error codes an adapter may set on a non-completed result. The
# application maps these to typed conversation failure classes; raw provider text never
# appears here.
ERROR_TIMEOUT = "provider_timeout"
ERROR_NETWORK = "network_denied"
ERROR_MALFORMED = "malformed_response"
ERROR_BLOCKED = "policy_blocked"
ERROR_ENDPOINT_DENIED = "endpoint_denied"
ERROR_UNAVAILABLE_CREDENTIAL = "unavailable_credential"


class TerminalState(str, Enum):
    """The only normalized terminal states for a dispatch attempt (ADR-0024)."""

    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class UsageProvenance(str, Enum):
    """Where a usage/cost figure came from. ``UNKNOWN`` never means zero."""

    REPORTED = "reported"  # the provider reported the value
    ESTIMATED = "estimated"  # locally estimated from the request
    UNKNOWN = "unknown"  # genuinely unavailable; must not be shown as zero


# ------------------------------------------------------------------ credential
class Credential:
    """An opaque secret handle. Its value never appears in ``repr``/``str``/logs.

    The production retrieval boundary lives in :mod:`jarvis_core.providers.credentials`
    (WP2). Tests inject canaries through this same type; nothing reads a live key here.
    """

    __slots__ = ("_secret",)

    def __init__(self, secret: str) -> None:
        self._secret = secret

    def reveal(self) -> str:
        """Return the raw secret. Callers must place it only in transport headers."""
        return self._secret

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return "Credential(<redacted>)"

    __str__ = __repr__


# ------------------------------------------------------------------ request
@dataclass(frozen=True)
class ProviderContent:
    """The deterministic, approved, content-bearing fields (and nothing else).

    Every field here is a pure function of the approved snapshot and its bound
    prompt-construction versions. An adapter may translate these into its wire format
    but may not add, drop, or mutate content-bearing information.
    """

    system_instruction: str
    user_text: str
    max_output_tokens: int
    thinking_level: str = "minimal"


@dataclass(frozen=True)
class TransportMetadata:
    """Allowlisted, non-content transport facts. Kept separate from content on purpose."""

    provider_id: str
    model_id: str
    scheme: str
    host: str
    path: str
    operation: str
    timeout_seconds: float
    max_input_tokens: int
    streaming: bool = False
    automatic_retries: int = 0


@dataclass(frozen=True)
class ProviderRequest:
    """A normalized dispatch request: content, transport, credential, diagnostics.

    The four concerns are separated (H07 §7.4): (1) deterministic content-bearing
    fields, (2) allowlisted transport metadata, (3) opaque credential transport, and
    (4) local diagnostics that never reach the wire.
    """

    request_id: str
    attempt_id: str
    content: ProviderContent
    transport: TransportMetadata
    credential: Credential | None = None
    diagnostics: Mapping[str, object] = field(default_factory=dict)


# ------------------------------------------------------------------ result
@dataclass(frozen=True)
class Usage:
    """Token usage with explicit provenance (never a silent zero)."""

    input_tokens: int | None
    output_tokens: int | None
    provenance: UsageProvenance

    def to_dict(self) -> dict[str, object]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "provenance": self.provenance.value,
        }


@dataclass(frozen=True)
class Cost:
    """Estimated cost with currency, rate-table version, and provenance."""

    amount_usd: float | None
    currency: str
    rate_table_version: str
    provenance: UsageProvenance

    def to_dict(self) -> dict[str, object]:
        return {
            "amount_usd": self.amount_usd,
            "currency": self.currency,
            "rate_table_version": self.rate_table_version,
            "provenance": self.provenance.value,
        }


@dataclass(frozen=True)
class NormalizedResult:
    """The only shape a conversation adapter may return. No raw payload crosses here."""

    status: TerminalState
    provider_id: str
    model_id: str
    adapter_version: str
    text: str | None = None
    finish_reason: str = "unknown"
    usage: Usage = field(default_factory=lambda: Usage(None, None, UsageProvenance.UNKNOWN))
    cost: Cost = field(default_factory=lambda: Cost(None, "USD", "unset", UsageProvenance.UNKNOWN))
    error_code: str | None = None  # redacted, taxonomic; never a raw provider error
    elapsed_ms: float | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status.value,
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "adapter_version": self.adapter_version,
            "text": self.text,
            "finish_reason": self.finish_reason,
            "usage": self.usage.to_dict(),
            "cost": self.cost.to_dict(),
            "error_code": self.error_code,
            "elapsed_ms": self.elapsed_ms,
        }


# ------------------------------------------------------------------ cancellation
class CancellationToken:
    """A thread-safe cooperative cancellation flag observable by an adapter."""

    __slots__ = ("_event",)

    def __init__(self) -> None:
        self._event = threading.Event()

    def cancel(self) -> None:
        self._event.set()

    @property
    def cancelled(self) -> bool:
        return self._event.is_set()

    def wait(self, timeout: float) -> bool:
        """Block up to ``timeout`` seconds; return True if cancelled meanwhile."""
        return self._event.wait(timeout)


# ------------------------------------------------------------------ protocol
@runtime_checkable
class ConversationProvider(Protocol):
    """The complete-response contract every conversation adapter satisfies."""

    name: str
    adapter_version: str

    def dispatch(
        self, request: ProviderRequest, cancel: CancellationToken | None = None
    ) -> NormalizedResult:
        """Perform exactly one complete-response attempt and normalize the result."""
        ...


# ------------------------------------------------------------------ credential boundary
@runtime_checkable
class CredentialProvider(Protocol):
    """Typed credential boundary (H07 §4.2, Handoff 08a Decision A).

    ``is_available`` answers availability only — no network, no remote key validation,
    and it never returns or logs the secret. ``get`` materializes the opaque
    :class:`Credential` solely at the adapter boundary for one approved dispatch. The
    production environment-backed implementation (reading ``GEMINI_API_KEY``) is WP2;
    tests inject a fake availability provider with canary values.
    """

    def is_available(self) -> bool:
        """Return whether a credential is present, without exposing or transmitting it."""
        ...

    def get(self) -> Credential:
        """Return the opaque credential handle for a single dispatch attempt."""
        ...


# ------------------------------------------------------------------ mock adapter
class MockConversationProvider:
    """Deterministic, offline mock. No network, no key, no randomness.

    Produces a stable ``completed`` result derived only from the request content, so
    fixtures and the shared conformance suite can exercise the whole pipeline without a
    provider. It honours cancellation cooperatively.
    """

    name = "mock"
    adapter_version = "jarvis.provider.mock.v0.5.0"

    def __init__(self, *, reply: str | None = None) -> None:
        self._reply = reply

    def dispatch(
        self, request: ProviderRequest, cancel: CancellationToken | None = None
    ) -> NormalizedResult:
        if cancel is not None and cancel.cancelled:
            return NormalizedResult(
                status=TerminalState.CANCELLED,
                provider_id=request.transport.provider_id,
                model_id=request.transport.model_id,
                adapter_version=self.adapter_version,
                finish_reason="cancelled",
            )
        content = request.content
        text = (
            self._reply
            if self._reply is not None
            else (
                f"[mock:{request.transport.model_id}] "
                f"Received {len(content.user_text.split())} user token(s) and a "
                f"{len(content.system_instruction.split())}-token system instruction; "
                f"output reserve {content.max_output_tokens}."
            )
        )
        out_tokens = len(text.split())
        return NormalizedResult(
            status=TerminalState.COMPLETED,
            provider_id=request.transport.provider_id,
            model_id=request.transport.model_id,
            adapter_version=self.adapter_version,
            text=text,
            finish_reason="stop",
            usage=Usage(
                input_tokens=len(content.user_text.split())
                + len(content.system_instruction.split()),
                output_tokens=out_tokens,
                provenance=UsageProvenance.ESTIMATED,
            ),
            cost=Cost(0.0, "USD", "mock", UsageProvenance.ESTIMATED),
            elapsed_ms=0.0,
        )


__all__ = [
    "PROVIDER_CONTRACT_VERSION",
    "CancellationToken",
    "ConversationProvider",
    "Cost",
    "Credential",
    "CredentialProvider",
    "MockConversationProvider",
    "NormalizedResult",
    "ProviderContent",
    "ProviderRequest",
    "TerminalState",
    "TransportMetadata",
    "Usage",
    "UsageProvenance",
]
