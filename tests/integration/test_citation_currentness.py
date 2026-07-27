"""AC-03R2a: citations are validated against CURRENT source bytes before emission."""
from __future__ import annotations

from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.policy import local_allow_all
from jarvis_core.query import QueryEngine
from jarvis_core.repositories import FileSystemKnowledgeRepository
from tests.support.synthetic_vault import build_query_vault


def _engine(path: Path) -> QueryEngine:
    notes = FileSystemKnowledgeRepository(Config(vault_path=path)).discover()
    return QueryEngine(notes, scope=local_allow_all("local"), source_root=path)


def test_citation_valid_before_mutation(tmp_path: Path):
    build_query_vault(tmp_path)
    a = _engine(tmp_path).search("invoices")
    assert any(c.relpath == "Bookkeeping App.md" for c in a.citations)


def test_post_discovery_mutation_declines_stale_citation(tmp_path: Path):
    build_query_vault(tmp_path)
    notes = FileSystemKnowledgeRepository(Config(vault_path=tmp_path)).discover()
    eng = QueryEngine(notes, scope=local_allow_all("local"), source_root=tmp_path)
    assert any(c.relpath == "Bookkeeping App.md" for c in eng.search("invoices").citations)
    # Mutate the source on disk AFTER discovery — a non-normalized byte change.
    target = tmp_path / "Bookkeeping App.md"
    target.write_bytes(target.read_bytes() + b"\r\nappended byte change\r\n")
    # The engine re-reads current bytes at emission; the stale citation is declined.
    after = eng.search("invoices")
    assert all(c.relpath != "Bookkeeping App.md" for c in after.citations)


def test_missing_source_after_discovery_fails_closed(tmp_path: Path):
    build_query_vault(tmp_path)
    notes = FileSystemKnowledgeRepository(Config(vault_path=tmp_path)).discover()
    eng = QueryEngine(notes, scope=local_allow_all("local"), source_root=tmp_path)
    (tmp_path / "Bookkeeping App.md").unlink()  # delete after discovery
    after = eng.search("invoices")
    assert all(c.relpath != "Bookkeeping App.md" for c in after.citations)


def test_source_root_is_mandatory(tmp_path: Path):
    # AC-03R3-01: a discovery snapshot alone must never back a 'supported' citation; the
    # engine fails closed at construction when no source_root is supplied.
    import pytest

    from jarvis_core.policy import PolicyError
    build_query_vault(tmp_path)
    notes = FileSystemKnowledgeRepository(Config(vault_path=tmp_path)).discover()
    with pytest.raises(TypeError):
        QueryEngine(notes, scope=local_allow_all("local"))          # source_root required
    with pytest.raises(PolicyError):
        QueryEngine(notes, scope=local_allow_all("local"), source_root=None)


def test_symlink_escape_declines_citation(tmp_path: Path):
    # A note that is a symlink resolving OUTSIDE the source root fails closed.
    import os

    outside = tmp_path.parent / "outside_secret.md"
    outside.write_text(
        "---\nid: n\ntype: concept\ntitle: \"Outside\"\nstatus: active\n"
        "created: 2026-07-27\nupdated: 2026-07-27\nsensitivity: internal\n---\n\n"
        "# Outside\n\nContains uniqueescterm content.\n",
        encoding="utf-8",
    )
    vault = tmp_path / "vault"
    vault.mkdir()
    try:
        os.symlink(outside, vault / "Link.md")
    except (OSError, NotImplementedError):
        import pytest
        pytest.skip("symlinks not supported in this environment")
    notes = FileSystemKnowledgeRepository(Config(vault_path=vault)).discover()
    eng = QueryEngine(notes, scope=local_allow_all("local"), source_root=vault)
    a = eng.search("uniqueescterm")
    # The symlinked source resolves outside the root -> no supported citation is emitted.
    assert all(c.relpath != "Link.md" for c in a.supported_citations())
