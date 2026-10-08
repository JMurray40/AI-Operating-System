"""Immutable visible-context snapshot and its canonical digest (ADR-0023, H07 §7.2).

A ``ContextSnapshot`` is a session-only, immutable semantic object. Its SHA-256 digest
covers the exact canonical serialization of every semantic input and explicitly excludes
declared diagnostics/timings. Removing an item never mutates a snapshot — it returns a
new object with a new digest (C07). Serialization is deterministic for identical inputs
regardless of construction order (C08).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, replace

from jarvis_core.conversation.contract import (
    CONTEXT_SNAPSHOT_VERSION,
    HISTORY_SERIALIZATION_VERSION,
    OUTPUT_RESERVE_VERSION,
    PROMPT_ASSEMBLER_VERSION,
    PROMPT_TEMPLATE_VERSION,
    PROVIDER_CONTRACT_VERSION,
    SAFETY_INSTRUCTION_VERSION,
    TOKEN_ESTIMATOR_VERSION,
    as_int,
)
from jarvis_core.conversation.immutable import (
    deep_thaw,
    freeze_mapping,
    freeze_tuple_of_mappings,
    json_default,
)


@dataclass(frozen=True)
class ContextItem:
    """One ordered, user-visible context item bound to an exact revision."""

    item_id: str  # stable displayed id, e.g. "C1"
    source_id: str
    source_identity_kind: str
    relpath: str
    title: str
    sensitivity: str | None
    source_fingerprint: str
    heading_path: tuple[str, ...]
    line_start: int
    line_end: int
    excerpt: str
    reason: str
    token_count: int
    relative_relevance: float | None = None

    def __post_init__(self) -> None:
        # AC-05-01R: normalize heading_path into an owned tuple and reject anything that is
        # not a string sequence. A caller-owned mutable list is copied here (never aliased),
        # so a later mutation of the caller's original list cannot change this retained item.
        hp = self.heading_path
        if isinstance(hp, str) or not isinstance(hp, Sequence):
            raise TypeError(
                f"heading_path must be a sequence of strings, not {type(hp).__name__!r}"
            )
        normalized = tuple(hp)
        if not all(isinstance(part, str) for part in normalized):
            raise TypeError("heading_path elements must all be strings")
        object.__setattr__(self, "heading_path", normalized)

    def semantic(self) -> dict[str, object]:
        """The exact fields that participate in the digest (order-independent)."""
        return {
            "item_id": self.item_id,
            "source_id": self.source_id,
            "source_identity_kind": self.source_identity_kind,
            "relpath": self.relpath,
            "title": self.title,
            "sensitivity": self.sensitivity,
            "source_fingerprint": self.source_fingerprint,
            "heading_path": list(self.heading_path),
            "line_start": self.line_start,
            "line_end": self.line_end,
            "excerpt": self.excerpt,
            "reason": self.reason,
            "token_count": self.token_count,
            "relative_relevance": self.relative_relevance,
        }

    def to_dict(self) -> dict[str, object]:
        return self.semantic()


@dataclass(frozen=True)
class ProviderPolicy:
    """The exact endpoint/feature policy bound into the snapshot (no secrets)."""

    provider_id: str
    model_id: str
    scheme: str
    host: str
    path: str
    operation: str
    streaming: bool
    thinking_level: str
    timeout_seconds: float
    automatic_retries: int
    max_input_tokens: int
    max_output_tokens: int
    disabled_features: tuple[str, ...]
    is_remote: bool
    provider_contract_version: str = PROVIDER_CONTRACT_VERSION

    def __post_init__(self) -> None:
        # AC-05-01R: normalize + own disabled_features so a caller-retained mutable list
        # cannot later mutate this digest-bearing feature-control field in place.
        df = self.disabled_features
        if isinstance(df, str) or not isinstance(df, Sequence):
            raise TypeError(
                f"disabled_features must be a sequence of strings, not {type(df).__name__!r}"
            )
        normalized = tuple(df)
        if not all(isinstance(feat, str) for feat in normalized):
            raise TypeError("disabled_features elements must all be strings")
        object.__setattr__(self, "disabled_features", normalized)

    def semantic(self) -> dict[str, object]:
        return {
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "scheme": self.scheme,
            "host": self.host,
            "path": self.path,
            "operation": self.operation,
            "streaming": self.streaming,
            "thinking_level": self.thinking_level,
            "timeout_seconds": self.timeout_seconds,
            "automatic_retries": self.automatic_retries,
            "max_input_tokens": self.max_input_tokens,
            "max_output_tokens": self.max_output_tokens,
            "disabled_features": list(self.disabled_features),
            "is_remote": self.is_remote,
            "provider_contract_version": self.provider_contract_version,
        }


@dataclass(frozen=True)
class PromptConstructionVersions:
    """Every bound prompt-construction version plus the output-reserve value (R3.6)."""

    output_reserve_value: int
    prompt_template_version: str = PROMPT_TEMPLATE_VERSION
    prompt_assembler_version: str = PROMPT_ASSEMBLER_VERSION
    history_serialization_version: str = HISTORY_SERIALIZATION_VERSION
    token_estimator_version: str = TOKEN_ESTIMATOR_VERSION
    safety_instruction_version: str = SAFETY_INSTRUCTION_VERSION
    output_reserve_version: str = OUTPUT_RESERVE_VERSION

    def semantic(self) -> dict[str, object]:
        return {
            "output_reserve_value": self.output_reserve_value,
            "prompt_template_version": self.prompt_template_version,
            "prompt_assembler_version": self.prompt_assembler_version,
            "history_serialization_version": self.history_serialization_version,
            "token_estimator_version": self.token_estimator_version,
            "safety_instruction_version": self.safety_instruction_version,
            "output_reserve_version": self.output_reserve_version,
        }


def _canonical_bytes(payload: dict[str, object]) -> bytes:
    """Deterministic canonical serialization used for the digest."""
    return json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=json_default,
    ).encode("utf-8")


@dataclass(frozen=True)
class ContextSnapshot:
    """An immutable, digest-bound visible-context snapshot (session-only)."""

    request_id: str
    session_id: str
    workspace_id: str
    normalized_user_input: str
    assumptions: tuple[Mapping[str, object], ...]
    items: tuple[ContextItem, ...]
    provider_policy: ProviderPolicy
    prompt_versions: PromptConstructionVersions
    policy_summary: Mapping[str, object]
    authorization_summary: Mapping[str, object]
    budget_accounting: Mapping[str, object]
    safe_omissions: tuple[Mapping[str, object], ...]
    user_exclusions: tuple[str, ...]
    price_table_version: str
    max_cost_usd_per_request: float
    evaluation_time: str
    history_serialization: str = ""
    snapshot_version: str = CONTEXT_SNAPSHOT_VERSION
    digest: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        # AC-05-01R: deep-freeze every caller-owned collection reachable from this snapshot
        # (defensive copy, not just a defensive check) so no retained reference — including
        # the caller's own `items` list/tuple — can mutate a semantic value, then bind the
        # canonical digest. Each ContextItem/ProviderPolicy already owns its own nested
        # collections (heading_path, disabled_features) via their own __post_init__; owning
        # the top-level `items` tuple here closes the last aliasing gap (a caller-retained
        # list of items being appended/removed/reordered after construction).
        object.__setattr__(self, "items", tuple(self.items))
        object.__setattr__(self, "assumptions", freeze_tuple_of_mappings(self.assumptions))
        object.__setattr__(self, "safe_omissions", freeze_tuple_of_mappings(self.safe_omissions))
        object.__setattr__(self, "policy_summary", freeze_mapping(self.policy_summary))
        object.__setattr__(
            self, "authorization_summary", freeze_mapping(self.authorization_summary)
        )
        object.__setattr__(self, "budget_accounting", freeze_mapping(self.budget_accounting))
        object.__setattr__(self, "user_exclusions", tuple(self.user_exclusions))
        object.__setattr__(self, "digest", self._compute_digest())

    def verify_integrity(self) -> None:
        """Recompute the canonical digest and fail closed on any drift (AC-05-01)."""
        if self._compute_digest() != self.digest:
            raise ValueError("snapshot integrity check failed: canonical digest drifted")

    def _semantic_payload(self) -> dict[str, object]:
        """The exact semantic content covered by the digest (no diagnostics/timings)."""
        return {
            "snapshot_version": self.snapshot_version,
            "request_id": self.request_id,
            "session_id": self.session_id,
            "workspace_id": self.workspace_id,
            "normalized_user_input": self.normalized_user_input,
            "assumptions": list(self.assumptions),
            "items": [item.semantic() for item in self.items],
            "provider_policy": self.provider_policy.semantic(),
            "prompt_versions": self.prompt_versions.semantic(),
            "policy_summary": self.policy_summary,
            "authorization_summary": self.authorization_summary,
            "budget_accounting": self.budget_accounting,
            "safe_omissions": list(self.safe_omissions),
            "user_exclusions": list(self.user_exclusions),
            "price_table_version": self.price_table_version,
            "max_cost_usd_per_request": self.max_cost_usd_per_request,
            "evaluation_time": self.evaluation_time,
            "history_serialization": self.history_serialization,
        }

    def canonical_bytes(self) -> bytes:
        return _canonical_bytes(self._semantic_payload())

    def _compute_digest(self) -> str:
        return "sha256:" + hashlib.sha256(self.canonical_bytes()).hexdigest()

    # ---------------------------------------------------------- immutable operations
    def item(self, item_id: str) -> ContextItem | None:
        return next((it for it in self.items if it.item_id == item_id), None)

    def without_item(self, item_id: str) -> ContextSnapshot:
        """Return a NEW snapshot with ``item_id`` removed; this object is unchanged (C07)."""
        if self.item(item_id) is None:
            raise KeyError(f"unknown context item id: {item_id!r}")
        remaining = tuple(it for it in self.items if it.item_id != item_id)
        removed_tokens = sum(it.token_count for it in self.items if it.item_id == item_id)
        new_accounting = dict(self.budget_accounting)
        prior = as_int(new_accounting.get("context_tokens_used", 0))
        new_accounting["context_tokens_used"] = max(0, prior - removed_tokens)
        new_accounting["items_included"] = len(remaining)
        return replace(
            self,
            items=remaining,
            user_exclusions=(*self.user_exclusions, item_id),
            budget_accounting=new_accounting,
            digest="",
        )

    def to_dict(self) -> dict[str, object]:
        thawed = deep_thaw(self._semantic_payload())
        assert isinstance(thawed, dict)
        thawed["digest"] = self.digest
        return thawed


__all__ = [
    "ContextItem",
    "ContextSnapshot",
    "PromptConstructionVersions",
    "ProviderPolicy",
]
