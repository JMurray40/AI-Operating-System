from __future__ import annotations

from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.health import HealthCategory, analyze_vault, render_text
from jarvis_core.repositories import FileSystemKnowledgeRepository
from tests.support.synthetic_vault import build_defect_vault


def _analyze(path: Path):
    notes = FileSystemKnowledgeRepository(Config(vault_path=path)).discover()
    return analyze_vault(notes, path)


def test_each_defect_category_detected(tmp_path: Path):
    exp = build_defect_vault(tmp_path)
    report = _analyze(tmp_path)
    counts = report.counts_by_category()
    assert counts.get(HealthCategory.MISSING_FRONTMATTER.value, 0) == exp.missing_frontmatter
    assert counts.get(HealthCategory.DUPLICATE_ID.value, 0) == exp.duplicate_id
    assert counts.get(HealthCategory.ORPHAN_NOTE.value, 0) == exp.orphan_note
    assert counts.get(HealthCategory.BROKEN_WIKILINK.value, 0) == exp.broken_wikilink
    assert counts.get(HealthCategory.INVALID_SCHEMA.value, 0) == exp.invalid_schema
    assert counts.get(HealthCategory.MISSING_ALIAS.value, 0) == exp.missing_alias
    assert counts.get(HealthCategory.CIRCULAR_REFERENCE.value, 0) == exp.circular_reference


def test_report_not_ok_with_errors(tmp_path: Path):
    build_defect_vault(tmp_path)
    report = _analyze(tmp_path)
    assert not report.ok  # duplicate ids + invalid schema are errors
    assert report.recommendations()  # non-empty


def test_render_text_has_all_sections(tmp_path: Path):
    build_defect_vault(tmp_path)
    text = render_text(_analyze(tmp_path))
    for section in ("SUMMARY", "ERRORS", "WARNINGS", "RECOMMENDATIONS"):
        assert section in text


def test_clean_vault_is_healthy(tmp_path: Path):
    from tests.support.synthetic_vault import build_synthetic_vault
    build_synthetic_vault(tmp_path, 30)
    report = _analyze(tmp_path)
    assert report.ok
    assert report.warnings == ()
