"""Immutable authorization scope required by every query entry point (ADR-0015).

Authorization is applied *before* request-visible index candidate generation and before
graph expansion. Absence of scope never means unrestricted: a local "allow all" scope is
still an explicit object with a non-empty workspace id and a declared sensitivity ceiling.
Unknown/invalid policy fails closed with a :class:`PolicyError`.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from jarvis_core.policy.errors import PolicyError
from jarvis_core.policy.sensitivity import ceiling_rank, within_ceiling

_ALLOW_ALL_POLICY = "local-allow-all"
_POLICY_VERSION = "1"


@dataclass(frozen=True)
class AuthorizationScope:
    """A workspace-scoped, immutable authorization decision context.

    ``allowed_source_ids`` / ``allowed_path_prefixes`` / ``allowed_types`` = ``None`` means
    "no restriction on that dimension" (still bounded by the sensitivity ceiling). Empty
    frozensets/tuples mean "allow nothing on that dimension".
    """

    workspace_id: str
    max_sensitivity: str
    request_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    allowed_source_ids: frozenset[str] | None = None
    allowed_path_prefixes: tuple[str, ...] | None = None
    allowed_types: frozenset[str] | None = None
    policy_id: str = _ALLOW_ALL_POLICY
    policy_version: str = _POLICY_VERSION

    def __post_init__(self) -> None:
        if not self.workspace_id or not self.workspace_id.strip():
            raise PolicyError("authorization scope requires a non-empty workspace_id")
        if not self.request_id or not self.request_id.strip():
            raise PolicyError("authorization scope requires a non-empty request_id")
        # Validates the ceiling is a known label; raises PolicyError otherwise (fail closed).
        ceiling_rank(self.max_sensitivity)

    # ------------------------------------------------------------- decisions
    def permits(
        self,
        *,
        source_id: str,
        relpath: str,
        sensitivity: str | None,
        note_type: str | None,
    ) -> bool:
        """Return True only if the source is authorized under every dimension (fail closed)."""
        if not within_ceiling(sensitivity, self.max_sensitivity):
            return False
        if self.allowed_source_ids is not None and source_id not in self.allowed_source_ids:
            return False
        if self.allowed_path_prefixes is not None:
            norm = relpath.replace("\\", "/").lstrip("/")
            if not any(norm.startswith(p) for p in self.allowed_path_prefixes):
                return False
        return not (
            self.allowed_types is not None
            and (note_type is None or note_type not in self.allowed_types)
        )

    def trace_summary(self) -> dict[str, object]:
        """A trace-safe description of the policy — no excluded identities or content."""
        return {
            "policy_id": self.policy_id,
            "policy_version": self.policy_version,
            "workspace_id": self.workspace_id,
            "max_sensitivity": self.max_sensitivity,
            "restricts_source_ids": self.allowed_source_ids is not None,
            "restricts_path_prefixes": self.allowed_path_prefixes is not None,
            "restricts_types": self.allowed_types is not None,
            "request_id": self.request_id,
        }


def local_allow_all(
    workspace_id: str = "local",
    *,
    max_sensitivity: str = "restricted",
    request_id: str | None = None,
) -> AuthorizationScope:
    """An explicit local scope that permits all *known* sensitivities up to the ceiling.

    Still requires a workspace id and a declared ceiling; notes with unknown sensitivity
    remain excluded (fail closed).
    """
    return AuthorizationScope(
        workspace_id=workspace_id,
        max_sensitivity=max_sensitivity,
        request_id=request_id or uuid.uuid4().hex,
        policy_id=_ALLOW_ALL_POLICY,
        policy_version=_POLICY_VERSION,
    )
