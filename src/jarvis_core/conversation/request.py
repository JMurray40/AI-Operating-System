"""Frozen prepare-turn request and provider profile (H07 §4.2, §7.1).

``PrepareTurnRequest`` is the single immutable input to a turn. ``ProviderProfile`` is
the domain identity of a destination — provider and native model kept strictly
separate, never a LiteLLM composite string. These are configuration/evidence, never
secrets; no credential is carried here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from jarvis_core.conversation.contract import CONVERSATION_CONTRACT_VERSION
from jarvis_core.policy.scope import AuthorizationScope

# The features that MUST be disabled/omitted for the approved Google surface (H07 §4.2).
DISABLED_PROVIDER_FEATURES = (
    "streaming",
    "live_api",
    "grounding",
    "url_context",
    "file_search",
    "files_media",
    "cached_content",
    "tools",
    "function_calls",
    "code_execution",
    "computer_use",
    "stored_interactions",
    "datasets",
    "feedback_log_sharing",
    "fallback",
    "hidden_retries",
)


@dataclass(frozen=True)
class ProviderProfile:
    """Domain identity + bounded policy for one destination (no secrets)."""

    provider_id: str
    model_id: str
    scheme: str
    host: str
    path: str
    operation: str
    max_input_tokens: int
    max_output_tokens: int
    timeout_seconds: float
    thinking_level: str = "minimal"
    streaming: bool = False
    automatic_retries: int = 0
    requests_per_approval: int = 1
    max_cost_usd_per_request: float = 0.05
    price_table_version: str = "unset"
    is_remote: bool = True
    retention_disclosure: str = ""
    disabled_features: tuple[str, ...] = DISABLED_PROVIDER_FEATURES

    def __post_init__(self) -> None:
        if self.streaming:
            raise ValueError("streaming is excluded in v0.5 (ADR-0024)")
        if self.automatic_retries != 0:
            raise ValueError("automatic provider retries are prohibited")
        if self.requests_per_approval != 1:
            raise ValueError("exactly one request per approval is permitted")
        if self.max_input_tokens <= 0 or self.max_output_tokens <= 0:
            raise ValueError("token limits must be positive")

    def trace_summary(self) -> dict[str, object]:
        """Trace-safe description (no secrets; identity + policy only)."""
        return {
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "scheme": self.scheme,
            "host": self.host,
            "operation": self.operation,
            "streaming": self.streaming,
            "thinking_level": self.thinking_level,
            "max_input_tokens": self.max_input_tokens,
            "max_output_tokens": self.max_output_tokens,
            "timeout_seconds": self.timeout_seconds,
            "automatic_retries": self.automatic_retries,
            "requests_per_approval": self.requests_per_approval,
            "max_cost_usd_per_request": self.max_cost_usd_per_request,
            "price_table_version": self.price_table_version,
            "is_remote": self.is_remote,
            "disabled_features": list(self.disabled_features),
        }


@dataclass(frozen=True)
class Budgets:
    """Hard budgets. The prompt budget includes every wrapper and the output reserve."""

    context_tokens: int = 3000
    prompt_tokens: int = 6000
    output_reserve_tokens: int = 800

    def __post_init__(self) -> None:
        for name in ("context_tokens", "prompt_tokens", "output_reserve_tokens"):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be non-negative")
        if self.output_reserve_tokens >= self.prompt_tokens:
            raise ValueError("output reserve must be smaller than the prompt budget")


@dataclass(frozen=True)
class HistoryLimits:
    """Hard caps on retained session history (deterministic, visible eviction)."""

    max_turns: int = 20
    max_history_tokens: int = 4000
    max_history_bytes: int = 200_000

    def __post_init__(self) -> None:
        for name in ("max_turns", "max_history_tokens", "max_history_bytes"):
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be positive")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class PrepareTurnRequest:
    """The single immutable input to a prepared turn (H07 §7.1)."""

    request_id: str
    session_id: str
    workspace_id: str
    scope: AuthorizationScope
    source_root: Path
    user_text: str
    provider_profile: ProviderProfile
    project_selector: str | None = None
    budgets: Budgets = field(default_factory=Budgets)
    history_limits: HistoryLimits = field(default_factory=HistoryLimits)
    evaluation_time: datetime = field(default_factory=_utc_now)
    want_trace: bool = False
    contract_version: str = CONVERSATION_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if not self.request_id or not self.session_id or not self.workspace_id:
            raise ValueError("request_id, session_id, and workspace_id are required")
        if self.source_root is None:
            raise ValueError("source_root is required for current-byte validation")
        if self.scope.workspace_id != self.workspace_id:
            raise ValueError("scope workspace_id must match the request workspace_id")


def mock_profile(*, max_input_tokens: int = 64000, max_output_tokens: int = 800) -> ProviderProfile:
    """A local, no-egress mock destination profile for offline flows."""
    return ProviderProfile(
        provider_id="mock",
        model_id="mock-deterministic",
        scheme="none",
        host="local",
        path="/mock",
        operation="complete",
        max_input_tokens=max_input_tokens,
        max_output_tokens=max_output_tokens,
        timeout_seconds=60.0,
        is_remote=False,
        price_table_version="mock",
        retention_disclosure="Local mock adapter; no data leaves the process.",
    )


__all__ = [
    "DISABLED_PROVIDER_FEATURES",
    "Budgets",
    "HistoryLimits",
    "PrepareTurnRequest",
    "ProviderProfile",
    "mock_profile",
]
