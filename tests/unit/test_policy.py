from __future__ import annotations

import pytest

from jarvis_core.policy import AuthorizationScope, PolicyError, local_allow_all, within_ceiling


def test_scope_requires_workspace():
    with pytest.raises(PolicyError):
        AuthorizationScope(workspace_id="", max_sensitivity="internal")


def test_scope_requires_known_ceiling():
    with pytest.raises(PolicyError):
        AuthorizationScope(workspace_id="w", max_sensitivity="banana")


def test_within_ceiling_ordering():
    assert within_ceiling("public", "internal") is True
    assert within_ceiling("internal", "internal") is True
    assert within_ceiling("restricted", "internal") is False


def test_unknown_or_missing_sensitivity_fails_closed():
    assert within_ceiling(None, "restricted") is False
    assert within_ceiling("weird", "restricted") is False


def test_allow_all_permits_known_excludes_unknown():
    scope = local_allow_all("local")
    assert scope.permits(source_id="local:id:x", relpath="a.md",
                         sensitivity="restricted", note_type="concept") is True
    # unknown sensitivity fails closed even under allow-all
    assert scope.permits(source_id="local:id:y", relpath="b.md",
                         sensitivity=None, note_type="concept") is False


def test_permits_path_prefix_and_types():
    scope = AuthorizationScope(
        workspace_id="w", max_sensitivity="restricted",
        allowed_path_prefixes=("projects/",), allowed_types=frozenset({"project"}),
    )
    assert scope.permits(source_id="s", relpath="projects/a.md",
                         sensitivity="internal", note_type="project") is True
    assert scope.permits(source_id="s", relpath="notes/a.md",
                         sensitivity="internal", note_type="project") is False
    assert scope.permits(source_id="s", relpath="projects/a.md",
                         sensitivity="internal", note_type="concept") is False


def test_trace_summary_has_no_content():
    scope = local_allow_all("local")
    d = scope.trace_summary()
    assert d["workspace_id"] == "local"
    assert set(d) >= {"policy_id", "policy_version", "max_sensitivity", "request_id"}
