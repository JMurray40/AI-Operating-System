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


def test_without_source_root_uses_discovery_snapshot(tmp_path: Path):
    # No source_root: discovery-revision consistency; citations still emit and validate.
    build_query_vault(tmp_path)
    notes = FileSystemKnowledgeRepository(Config(vault_path=tmp_path)).discover()
    eng = QueryEngine(notes, scope=local_allow_all("local"))
    assert any(c.relpath == "Bookkeeping App.md" for c in eng.search("invoices").citations)
