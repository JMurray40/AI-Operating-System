from __future__ import annotations

from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.context.validator import validate_notes
from jarvis_core.models.validation import Severity, Stage
from jarvis_core.repositories import FileSystemKnowledgeRepository


def _validate(path: Path):
    return validate_notes(FileSystemKnowledgeRepository(Config(vault_path=path)).discover())


def test_clean_fixture_has_no_errors(aios_dir: Path):
    result = _validate(aios_dir)
    assert result.ok, [i.message for i in result.errors]


def test_edge_cases_report_syntax_error(edge_dir: Path):
    result = _validate(edge_dir)
    assert not result.ok
    stages = {i.stage for i in result.errors}
    assert Stage.SYNTAX in stages
    # unresolved links appear as integrity warnings
    assert any(
        i.stage is Stage.INTEGRITY and i.severity is Severity.WARNING
        for i in result.warnings
    )


def test_secret_detection_policy(tmp_path: Path):
    (tmp_path / "leak.md").write_text(
        "---\nid: n\ntype: reference\ntitle: L\nstatus: draft\n"
        "created: 2026-07-27\nupdated: 2026-07-27\nsensitivity: internal\n---\n"
        "api_key = 'sk-abcdef0123456789abcdef'\n",
        encoding="utf-8",
    )
    result = _validate(tmp_path)
    assert any(i.stage is Stage.POLICY for i in result.errors)
