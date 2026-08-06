"""Digest-bound egress approval (ADR-0023, H07 §7.3, C09).

An ``EgressApproval`` binds an actor confirmation to the exact snapshot digest, workspace,
destination, model, policy version, every prompt-construction version and the output-reserve
value, an approval time, an expiry, and exactly one permitted request. It is session-only and
cannot be replayed across workspace, session, request, snapshot, destination, model, policy,
version, or expiry — any mismatch fails closed before prompt assembly.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from jarvis_core.conversation.contract import (
    EGRESS_APPROVAL_VERSION,
    ApprovalError,
)
from jarvis_core.conversation.immutable import deep_thaw, freeze_mapping
from jarvis_core.conversation.snapshot import ContextSnapshot

DEFAULT_APPROVAL_TTL_SECONDS = 300


@dataclass(frozen=True)
class EgressApproval:
    """An immutable, single-use, digest-bound approval record."""

    actor: str
    request_id: str
    session_id: str
    workspace_id: str
    snapshot_digest: str
    provider_id: str
    host: str
    operation: str
    model_id: str
    model_role: str
    policy_version: str
    prompt_versions: Mapping[str, object]
    output_reserve_value: int
    approval_time: str
    expiry_time: str
    permitted_requests: int = 1
    approval_contract_version: str = EGRESS_APPROVAL_VERSION

    def __post_init__(self) -> None:
        # AC-05-01: the bound prompt-construction versions are deeply immutable.
        object.__setattr__(self, "prompt_versions", freeze_mapping(self.prompt_versions))

    def _expired(self, now: datetime) -> bool:
        return now >= datetime.fromisoformat(self.expiry_time)

    def check(
        self,
        snapshot: ContextSnapshot,
        *,
        policy_version: str,
        now: datetime,
    ) -> None:
        """Raise :class:`ApprovalError` on any mismatch, expiry, or replay condition."""
        if self.snapshot_digest != snapshot.digest:
            raise ApprovalError("approval snapshot digest does not match current snapshot")
        if self.request_id != snapshot.request_id:
            raise ApprovalError("approval request_id mismatch")
        if self.session_id != snapshot.session_id:
            raise ApprovalError("approval session_id mismatch")
        if self.workspace_id != snapshot.workspace_id:
            raise ApprovalError("approval workspace_id mismatch")
        if self.provider_id != snapshot.provider_policy.provider_id:
            raise ApprovalError("approval provider mismatch")
        if self.host != snapshot.provider_policy.host:
            raise ApprovalError("approval destination host mismatch")
        if self.operation != snapshot.provider_policy.operation:
            raise ApprovalError("approval operation mismatch")
        if self.model_id != snapshot.provider_policy.model_id:
            raise ApprovalError("approval model mismatch")
        if self.policy_version != policy_version:
            raise ApprovalError("policy version changed since approval")
        if self.prompt_versions != snapshot.prompt_versions.semantic():
            raise ApprovalError("a bound prompt-construction version changed since approval")
        if self.output_reserve_value != snapshot.prompt_versions.output_reserve_value:
            raise ApprovalError("output reserve changed since approval")
        if self.permitted_requests != 1:
            raise ApprovalError("exactly one request per approval is permitted")
        if self._expired(now):
            raise ApprovalError("approval has expired")

    def to_dict(self) -> dict[str, object]:
        return {
            "approval_contract_version": self.approval_contract_version,
            "actor": self.actor,
            "request_id": self.request_id,
            "session_id": self.session_id,
            "workspace_id": self.workspace_id,
            "snapshot_digest": self.snapshot_digest,
            "provider_id": self.provider_id,
            "host": self.host,
            "operation": self.operation,
            "model_id": self.model_id,
            "model_role": self.model_role,
            "policy_version": self.policy_version,
            "prompt_versions": deep_thaw(self.prompt_versions),
            "output_reserve_value": self.output_reserve_value,
            "approval_time": self.approval_time,
            "expiry_time": self.expiry_time,
            "permitted_requests": self.permitted_requests,
        }


def create_approval(
    snapshot: ContextSnapshot,
    *,
    actor: str,
    model_role: str,
    policy_version: str,
    approval_time: datetime | None = None,
    ttl_seconds: int = DEFAULT_APPROVAL_TTL_SECONDS,
) -> EgressApproval:
    """Create an approval bound to the exact snapshot and its provider policy."""
    at = approval_time or datetime.now(timezone.utc)
    exp = at + timedelta(seconds=ttl_seconds)
    pol = snapshot.provider_policy
    return EgressApproval(
        actor=actor,
        request_id=snapshot.request_id,
        session_id=snapshot.session_id,
        workspace_id=snapshot.workspace_id,
        snapshot_digest=snapshot.digest,
        provider_id=pol.provider_id,
        host=pol.host,
        operation=pol.operation,
        model_id=pol.model_id,
        model_role=model_role,
        policy_version=policy_version,
        prompt_versions=snapshot.prompt_versions.semantic(),
        output_reserve_value=snapshot.prompt_versions.output_reserve_value,
        approval_time=at.isoformat(),
        expiry_time=exp.isoformat(),
    )


__all__ = ["DEFAULT_APPROVAL_TTL_SECONDS", "EgressApproval", "create_approval"]
