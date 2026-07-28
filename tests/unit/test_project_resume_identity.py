"""C3: exact tiered project identity selection (ADR-0018)."""
from __future__ import annotations

from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.policy import local_allow_all
from jarvis_core.policy.scope import AuthorizationScope
from jarvis_core.project_resume.contract import (
    TIER_ALIAS,
    TIER_CANONICAL_ID,
    TIER_FILENAME_STEM,
    TIER_TITLE,
)
from jarvis_core.project_resume.identity import (
    SELECTION_AMBIGUOUS,
    SELECTION_INVALID,
    SELECTION_NOT_FOUND,
    SELECTION_SELECTED,
    resolve_project,
)
from jarvis_core.repositories import FileSystemKnowledgeRepository

_DATE = "2026-07-27"


def _project(root: Path, fname: str, pid: str, title: str, *, aliases=(), sensitivity="internal"):
    alias_line = f"aliases: [{', '.join(aliases)}]\n" if aliases else ""
    (root / fname).write_text(
        f"---\nid: {pid}\ntype: project\ntitle: \"{title}\"\nstatus: active\n"
        f"created: {_DATE}\nupdated: {_DATE}\ngoal: \"g\"\npriority: high\n"
        f"sensitivity: {sensitivity}\n{alias_line}---\n\n# {title}\n\nBody.\n",
        encoding="utf-8",
    )


def _concept(root: Path, fname: str, cid: str, title: str):
    (root / fname).write_text(
        f"---\nid: {cid}\ntype: concept\ntitle: \"{title}\"\nstatus: active\n"
        f"created: {_DATE}\nupdated: {_DATE}\nsensitivity: internal\n---\n\n# {title}\n\nBody.\n",
        encoding="utf-8",
    )


def _vault(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    _project(root, "Alpha.md", "project-alpha", "Alpha Project", aliases=["alpha-alias"])
    _project(root, "Beta.md", "project-beta", "Beta Project", aliases=["shared-alias"])
    _project(root, "Gamma.md", "project-gamma", "Gamma Project", aliases=["shared-alias"])
    _project(root, "Delta.md", "project-delta", "Beta Project")  # title collides with Beta
    _project(root, "Echo.md", "project-echo", "foxtrot")          # title == Foxtrot's stem
    _project(root, "Foxtrot.md", "project-foxtrot", "Foxtrot Project")
    _concept(root, "AlphaConcept.md", "concept-alpha", "Alpha Project")  # non-project, ignored


def _notes(root: Path):
    return FileSystemKnowledgeRepository(Config(vault_path=root)).discover()


def _scope():
    return local_allow_all("local")


def test_canonical_id_tier_selects(tmp_path: Path):
    _vault(tmp_path)
    sel = resolve_project(_notes(tmp_path), _scope(), "local:id:project-alpha")
    assert sel.status == SELECTION_SELECTED
    assert sel.identity.relpath == "Alpha.md"
    assert sel.identity.tier == TIER_CANONICAL_ID


def test_title_tier_selects_and_ignores_non_projects(tmp_path: Path):
    _vault(tmp_path)
    sel = resolve_project(_notes(tmp_path), _scope(), "Alpha Project")
    # Only the project Alpha.md matches; the concept note with the same title is ignored.
    assert sel.status == SELECTION_SELECTED
    assert sel.identity.relpath == "Alpha.md" and sel.identity.tier == TIER_TITLE


def test_title_collision_is_ambiguous(tmp_path: Path):
    _vault(tmp_path)
    sel = resolve_project(_notes(tmp_path), _scope(), "Beta Project")
    assert sel.status == SELECTION_AMBIGUOUS
    relpaths = [c.relpath for c in sel.candidates]
    assert relpaths == sorted(relpaths)  # sorted by (source_id, relpath)
    assert set(relpaths) == {"Beta.md", "Delta.md"}
    assert sel.identity is None


def test_alias_tier_selects(tmp_path: Path):
    _vault(tmp_path)
    sel = resolve_project(_notes(tmp_path), _scope(), "alpha-alias")
    assert sel.status == SELECTION_SELECTED and sel.identity.tier == TIER_ALIAS


def test_alias_collision_is_ambiguous(tmp_path: Path):
    _vault(tmp_path)
    sel = resolve_project(_notes(tmp_path), _scope(), "shared-alias")
    assert sel.status == SELECTION_AMBIGUOUS
    assert {c.relpath for c in sel.candidates} == {"Beta.md", "Gamma.md"}


def test_filename_stem_tier_selects(tmp_path: Path):
    _vault(tmp_path)
    # "alpha" matches no canonical id/title/alias exactly, but matches Alpha.md's stem.
    sel = resolve_project(_notes(tmp_path), _scope(), "alpha")
    assert sel.status == SELECTION_SELECTED
    assert sel.identity.relpath == "Alpha.md" and sel.identity.tier == TIER_FILENAME_STEM


def test_stronger_tier_wins_over_weaker(tmp_path: Path):
    _vault(tmp_path)
    # "foxtrot": Echo.md has title 'foxtrot' (title tier); Foxtrot.md has stem 'Foxtrot'
    # (stem tier). The stronger title tier controls -> Echo.md, never Foxtrot.md.
    sel = resolve_project(_notes(tmp_path), _scope(), "foxtrot")
    assert sel.status == SELECTION_SELECTED
    assert sel.identity.relpath == "Echo.md" and sel.identity.tier == TIER_TITLE


def test_not_found_returns_no_substitute(tmp_path: Path):
    _vault(tmp_path)
    sel = resolve_project(_notes(tmp_path), _scope(), "does-not-exist")
    assert sel.status == SELECTION_NOT_FOUND
    assert sel.identity is None and sel.candidates == ()


def test_excluded_project_is_not_disclosed(tmp_path: Path):
    _vault(tmp_path)
    _project(tmp_path, "Secret.md", "project-secret", "Secret Project", sensitivity="restricted")
    scope = AuthorizationScope(workspace_id="local", max_sensitivity="internal")
    sel = resolve_project(_notes(tmp_path), scope, "Secret Project")
    # A restricted project above the ceiling cannot be selected or surface as a candidate.
    assert sel.status == SELECTION_NOT_FOUND
    assert sel.identity is None and sel.candidates == ()


def test_duplicate_explicit_id_fails_closed_invalid(tmp_path: Path):
    _vault(tmp_path)
    _project(tmp_path, "Dup1.md", "project-dup", "Dup One")
    _project(tmp_path, "Dup2.md", "project-dup", "Dup Two")
    sel = resolve_project(_notes(tmp_path), _scope(), "Alpha Project")
    assert sel.status == SELECTION_INVALID
    # No excluded/duplicate source identity is named in the candidate surface.
    assert sel.candidates == () and sel.identity is None
