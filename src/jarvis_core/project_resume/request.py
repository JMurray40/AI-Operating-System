"""Immutable Project Resume request and its fail-closed construction (ADR-0020 §6).

Scope and source root are mandatory. ``evaluation_time`` is an explicit ISO-8601 UTC input,
never an implicit wall-clock dependency. When the CLI omits the request ID it is derived
deterministically from the semantic request fields plus a safe authorization summary.
Negative/out-of-range budgets and malformed inputs fail *before* any discovery, and no
request field authorizes writes or network access.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from jarvis_core.policy.errors import PolicyError
from jarvis_core.policy.scope import AuthorizationScope
from jarvis_core.project_resume.contract import (
    DEFAULT_EVIDENCE_TOKEN_BUDGET,
    DEFAULT_OUTPUT_TOKEN_BUDGET,
    EVIDENCE_BUDGET_MAX,
    EVIDENCE_BUDGET_MIN,
    OUTPUT_BUDGET_MAX,
    OUTPUT_BUDGET_MIN,
    PROJECT_RESUME_CONTRACT_VERSION,
)
from jarvis_core.project_resume.repository_activity import RepositoryActivityGrant


class ProjectResumeError(Exception):
    """Base class for Project Resume request/build failures."""


class RequestValidationError(ProjectResumeError):
    """A malformed or empty request input detected before discovery."""


class BudgetRangeError(ProjectResumeError):
    """An evidence/output budget outside its accepted bounds."""


@dataclass(frozen=True)
class ProjectResumeRequest:
    """A frozen, fully-validated Project Resume request."""

    request_id: str
    workspace_id: str
    project_selector: str
    authorization_scope: AuthorizationScope
    source_root: Path
    evidence_token_budget: int
    output_token_budget: int
    evaluation_time: datetime
    repository_activity_grant: RepositoryActivityGrant | None
    trace_requested: bool
    contract_version: str = PROJECT_RESUME_CONTRACT_VERSION

    @property
    def evaluation_time_iso(self) -> str:
        """The canonical ISO-8601 UTC form used for determinism and staleness."""
        return self.evaluation_time.astimezone(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, object]:
        return {
            "contract_version": self.contract_version,
            "request_id": self.request_id,
            "workspace_id": self.workspace_id,
            "project_selector": self.project_selector,
            "evidence_token_budget": self.evidence_token_budget,
            "output_token_budget": self.output_token_budget,
            "evaluation_time": self.evaluation_time_iso,
            "repository_activity": (
                self.repository_activity_grant.to_dict()
                if self.repository_activity_grant is not None
                else None
            ),
            "trace_requested": self.trace_requested,
        }


def parse_evaluation_time(value: str) -> datetime:
    """Parse an explicit ISO-8601 UTC evaluation time; reject naive/non-UTC/malformed input."""
    if not isinstance(value, str) or not value.strip():
        raise RequestValidationError("evaluation_time must be an explicit ISO-8601 UTC string")
    raw = value.strip()
    normalized = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise RequestValidationError(f"malformed evaluation_time: {value!r}") from exc
    if parsed.tzinfo is None:
        raise RequestValidationError("evaluation_time must include a UTC offset (naive rejected)")
    if parsed.utcoffset() != timezone.utc.utcoffset(None):
        raise RequestValidationError("evaluation_time must be UTC (offset +00:00)")
    return parsed.astimezone(timezone.utc)


def _validate_budget(name: str, value: int, low: int, high: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise BudgetRangeError(f"{name} must be an integer")
    if value < low or value > high:
        raise BudgetRangeError(f"{name} must be {low}..{high}")
    return value


def _derive_request_id(
    *,
    workspace_id: str,
    selector: str,
    source_root: Path,
    evaluation_time_iso: str,
    evidence_budget: int,
    output_budget: int,
    grant: RepositoryActivityGrant | None,
    scope: AuthorizationScope,
    trace_requested: bool,
) -> str:
    """Deterministically derive a request ID from semantic fields + a safe scope summary."""
    # Use the SAFE, stable authorization surface (policy id/version, workspace, ceiling, and
    # restriction flags) but never the scope's volatile per-instance request_id, so identical
    # semantic requests derive identical IDs regardless of scope object identity.
    scope_summary = {k: v for k, v in scope.trace_summary().items() if k != "request_id"}
    payload = {
        "workspace_id": workspace_id,
        "selector": selector,
        "source_root": str(source_root),
        "evaluation_time": evaluation_time_iso,
        "evidence_budget": evidence_budget,
        "output_budget": output_budget,
        "trace_requested": trace_requested,
        "grant": grant.to_dict() if grant is not None else None,
        "scope": scope_summary,
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()[:32]
    return f"prr:{digest}"


def build_request(
    *,
    workspace_id: str,
    project_selector: str,
    authorization_scope: AuthorizationScope,
    source_root: Path,
    evaluation_time: str,
    evidence_token_budget: int = DEFAULT_EVIDENCE_TOKEN_BUDGET,
    output_token_budget: int = DEFAULT_OUTPUT_TOKEN_BUDGET,
    repository_activity_grant: RepositoryActivityGrant | None = None,
    trace_requested: bool = False,
    request_id: str | None = None,
) -> ProjectResumeRequest:
    """Build a fully-validated request, failing closed before any discovery occurs."""
    if authorization_scope is None:
        raise PolicyError("Project Resume requires an explicit AuthorizationScope")
    if source_root is None:
        raise PolicyError("Project Resume requires a source_root for current-source validation")
    selector = (project_selector or "").strip()
    if not selector:
        raise RequestValidationError("project_selector must be a non-empty string")

    resolved_root = source_root.resolve()
    evidence_budget = _validate_budget(
        "evidence_token_budget", evidence_token_budget, EVIDENCE_BUDGET_MIN, EVIDENCE_BUDGET_MAX
    )
    output_budget = _validate_budget(
        "output_token_budget", output_token_budget, OUTPUT_BUDGET_MIN, OUTPUT_BUDGET_MAX
    )
    eval_dt = parse_evaluation_time(evaluation_time)
    eval_iso = eval_dt.isoformat()

    rid = request_id or _derive_request_id(
        workspace_id=workspace_id,
        selector=selector,
        source_root=resolved_root,
        evaluation_time_iso=eval_iso,
        evidence_budget=evidence_budget,
        output_budget=output_budget,
        grant=repository_activity_grant,
        scope=authorization_scope,
        trace_requested=trace_requested,
    )
    return ProjectResumeRequest(
        request_id=rid,
        workspace_id=workspace_id,
        project_selector=selector,
        authorization_scope=authorization_scope,
        source_root=resolved_root,
        evidence_token_budget=evidence_budget,
        output_token_budget=output_budget,
        evaluation_time=eval_dt,
        repository_activity_grant=repository_activity_grant,
        trace_requested=trace_requested,
    )
