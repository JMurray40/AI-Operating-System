"""Scale + read-only-at-scale tests using synthetic vaults (100/500/1000 notes)."""
from __future__ import annotations

import hashlib
import time
from pathlib import Path

import pytest

from jarvis_core.config import Config
from jarvis_core.context.validator import validate_notes
from jarvis_core.health import analyze_vault
from jarvis_core.relationships import RelationshipResolver
from jarvis_core.repositories import FileSystemKnowledgeRepository
from tests.support.synthetic_vault import build_synthetic_vault


def _snapshot(root: Path) -> dict[str, str]:
    return {
        p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*")) if p.is_file()
    }


@pytest.mark.parametrize("n_notes", [100, 500, 1000])
def test_scale_discovers_all_and_stays_healthy(tmp_path: Path, n_notes: int):
    vault = tmp_path / "vault"
    exp = build_synthetic_vault(vault, n_notes, missing_fm=5)

    before = _snapshot(vault)
    start = time.perf_counter()
    notes = FileSystemKnowledgeRepository(Config(vault_path=vault)).discover()
    resolution = RelationshipResolver(notes).resolve_all()
    validation = validate_notes(notes)
    report = analyze_vault(notes, vault, resolution=resolution, validation=validation)
    elapsed = time.perf_counter() - start
    after = _snapshot(vault)

    # correctness
    assert report.note_count == exp.note_count == n_notes
    assert report.counts_by_category().get("missing_frontmatter", 0) == exp.missing_fm_count()
    # a chain has no orphans, broken links, or schema errors
    assert report.counts_by_category().get("orphan_note", 0) == 0
    assert report.counts_by_category().get("broken_wikilink", 0) == 0
    assert report.ok  # missing frontmatter is a warning, not an error

    # read-only: nothing changed
    assert before == after
    assert set(before) == set(after)

    # sanity performance guard (generous; catches pathological regressions)
    assert elapsed < 15.0, f"{n_notes} notes took {elapsed:.2f}s"

