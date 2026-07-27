from __future__ import annotations

from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.repositories import FileSystemKnowledgeRepository
from jarvis_core.repositories.base import KnowledgeRepository


def test_discovers_expected_notes(aios_dir: Path):
    repo = FileSystemKnowledgeRepository(Config(vault_path=aios_dir))
    notes = repo.discover()
    assert len(notes) == 7
    assert all(n.relpath.endswith(".md") for n in notes)
    # deterministic order
    assert [n.relpath for n in notes] == sorted(n.relpath for n in notes)


def test_repository_has_no_write_methods(aios_dir: Path):
    repo = FileSystemKnowledgeRepository(Config(vault_path=aios_dir))
    method_names = {m for m in dir(repo) if not m.startswith("_")}
    for forbidden in ("write", "save", "delete", "update", "create", "move"):
        assert forbidden not in method_names
    assert isinstance(repo, KnowledgeRepository)


def test_excluded_dirs_are_skipped(tmp_path: Path):
    (tmp_path / ".obsidian").mkdir()
    (tmp_path / ".obsidian" / "config.md").write_text("# hidden", encoding="utf-8")
    (tmp_path / "real.md").write_text("# real", encoding="utf-8")
    repo = FileSystemKnowledgeRepository(Config(vault_path=tmp_path))
    notes = repo.discover()
    assert [n.relpath for n in notes] == ["real.md"]


def test_missing_path_raises(tmp_path: Path):
    repo = FileSystemKnowledgeRepository(Config(vault_path=tmp_path / "nope"))
    try:
        repo.discover()
    except FileNotFoundError:
        return
    raise AssertionError("expected FileNotFoundError")
