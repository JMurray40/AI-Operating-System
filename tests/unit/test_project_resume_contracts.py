"""C2: Project Resume versioned contracts, request validation, and deterministic serialization."""
from __future__ import annotations

from pathlib import Path

import pytest

from jarvis_core.policy import local_allow_all
from jarvis_core.policy.errors import PolicyError
from jarvis_core.project_resume import (
    PROJECT_RESUME_CONTRACT_VERSION,
    BudgetRangeError,
    ProjectResumeResult,
    RequestValidationError,
    build_request,
)
from jarvis_core.project_resume.contract import (
    COVERAGE_NONE,
    STATUS_NOT_FOUND,
)
from jarvis_core.project_resume.repository_activity import RepositoryActivityGrant
from jarvis_core.project_resume.request import parse_evaluation_time
from jarvis_core.project_resume.results import CoverageSummary

_ROOT = Path("/tmp/does-not-need-to-exist")
_T = "2026-07-27T00:00:00Z"


def _req(**over):
    kw = dict(
        workspace_id="local",
        project_selector="Alpha",
        authorization_scope=local_allow_all("local"),
        source_root=_ROOT,
        evaluation_time=_T,
    )
    kw.update(over)
    return build_request(**kw)


def test_contract_versions_are_distinct_and_pinned():
    from jarvis_core.project_resume import (
        PROJECT_RESUME_TRACE_VERSION,
        REPOSITORY_ACTIVITY_CONTRACT_VERSION,
    )
    versions = {
        PROJECT_RESUME_CONTRACT_VERSION,
        PROJECT_RESUME_TRACE_VERSION,
        REPOSITORY_ACTIVITY_CONTRACT_VERSION,
    }
    assert len(versions) == 3
    assert PROJECT_RESUME_CONTRACT_VERSION == "jarvis.project-resume.v0.4.0"


def test_scope_and_source_root_are_mandatory():
    with pytest.raises(PolicyError):
        _req(authorization_scope=None)
    with pytest.raises(PolicyError):
        _req(source_root=None)


def test_empty_selector_fails_before_discovery():
    with pytest.raises(RequestValidationError):
        _req(project_selector="   ")


@pytest.mark.parametrize("ev,out", [(-1, 4000), (255, 4000), (32001, 4000), (8000, -5)])
def test_out_of_range_budgets_fail(ev, out):
    with pytest.raises(BudgetRangeError):
        _req(evidence_token_budget=ev, output_token_budget=out)


def test_boolean_budget_rejected():
    with pytest.raises(BudgetRangeError):
        _req(evidence_token_budget=True)


def test_evaluation_time_must_be_explicit_utc():
    with pytest.raises(RequestValidationError):
        parse_evaluation_time("2026-07-27T00:00:00")  # naive
    with pytest.raises(RequestValidationError):
        parse_evaluation_time("2026-07-27T00:00:00+02:00")  # non-UTC
    with pytest.raises(RequestValidationError):
        parse_evaluation_time("not-a-time")
    assert parse_evaluation_time("2026-07-27T00:00:00Z").isoformat() == "2026-07-27T00:00:00+00:00"


def test_request_id_is_deterministic_and_scope_sensitive():
    a = _req().request_id
    b = _req().request_id
    assert a == b and a.startswith("prr:")
    # A different selector changes the derived ID.
    assert _req(project_selector="Beta").request_id != a


def test_explicit_request_id_is_respected():
    assert _req(request_id="prr:fixed").request_id == "prr:fixed"


def test_grant_bounds_enforced():
    with pytest.raises(ValueError):
        RepositoryActivityGrant(workspace_id="local", project_id="p", repository_root=_ROOT,
                                max_records=0)
    with pytest.raises(ValueError):
        RepositoryActivityGrant(workspace_id="local", project_id="p", repository_root=_ROOT,
                                max_records=51)
    with pytest.raises(ValueError):
        RepositoryActivityGrant(workspace_id="local", project_id="p", repository_root=_ROOT,
                                timeout_seconds=11)


def test_result_to_dict_has_fixed_key_order():
    result = ProjectResumeResult(
        request_id="prr:x", status=STATUS_NOT_FOUND,
        coverage=CoverageSummary(label=COVERAGE_NONE),
    )
    keys = list(result.to_dict().keys())
    assert keys == [
        "contract_version", "request_id", "status", "project_identity", "candidates",
        "sections", "citations", "repository_citations", "conflicts", "omissions",
        "limitations", "coverage", "trace",
    ]
    assert result.to_dict()["contract_version"] == PROJECT_RESUME_CONTRACT_VERSION


def test_request_id_stable_across_scope_object_identity():
    # Two independently constructed allow-all scopes must derive the same request id.
    r1 = build_request(workspace_id="local", project_selector="Alpha",
                       authorization_scope=local_allow_all("local"), source_root=_ROOT,
                       evaluation_time=_T)
    r2 = build_request(workspace_id="local", project_selector="Alpha",
                       authorization_scope=local_allow_all("local"), source_root=_ROOT,
                       evaluation_time=_T)
    assert r1.request_id == r2.request_id
