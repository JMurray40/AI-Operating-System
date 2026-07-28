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


def test_engine_requires_explicit_scope(tmp_path):
    """AC-01: omitted scope is a TypeError; explicit None fails closed with PolicyError."""
    import pytest

    from jarvis_core.config import Config
    from jarvis_core.query import QueryEngine
    from jarvis_core.repositories import FileSystemKnowledgeRepository
    from tests.support.synthetic_vault import build_query_vault

    build_query_vault(tmp_path)
    notes = FileSystemKnowledgeRepository(Config(vault_path=tmp_path)).discover()
    with pytest.raises(TypeError):
        QueryEngine(notes)                    # scope AND source_root required
    with pytest.raises(PolicyError):
        QueryEngine(notes, scope=None, source_root=tmp_path)  # explicit None fails closed
    with pytest.raises(PolicyError):
        QueryEngine(notes, scope=local_allow_all("local"), source_root=None)  # AC-03R3-01


def _permit(scope, relpath):
    return scope.permits(source_id="s", relpath=relpath, sensitivity="internal",
                         note_type="concept")


def test_path_prefix_rejects_absolute_empty_and_traversal():
    for bad in ("/abs/x", "", "   ", "a/../b", "..", "C:/x"):
        with pytest.raises(PolicyError):
            AuthorizationScope(workspace_id="w", max_sensitivity="restricted",
                               allowed_path_prefixes=(bad,))


def test_path_prefix_segment_boundary_no_sibling_leak():
    scope = AuthorizationScope(workspace_id="w", max_sensitivity="restricted",
                               allowed_path_prefixes=("projects/alpha",))
    assert _permit(scope, "projects/alpha/notes.md") is True   # descendant
    assert _permit(scope, "projects/alpha") is True            # exact
    assert _permit(scope, "projects/alpha-restricted/x.md") is False  # sibling prefix
    assert _permit(scope, "projects/alphabet.md") is False     # near match


def test_path_prefix_slash_and_case_normalization():
    scope = AuthorizationScope(workspace_id="w", max_sensitivity="restricted",
                               allowed_path_prefixes=("Projects\\Alpha",))
    assert _permit(scope, "projects/alpha/x.md") is True       # backslash + case folded
    assert _permit(scope, "/projects/Alpha/x.md") is True      # leading slash tolerated
