from __future__ import annotations

import json
from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.health import analyze_vault, compute_vault_fingerprint
from jarvis_core.repositories import FileSystemKnowledgeRepository
from tests.support.synthetic_vault import build_synthetic_vault


def _notes(path: Path):
    return FileSystemKnowledgeRepository(Config(vault_path=path)).discover()


def test_envelope_fields_present(tmp_path: Path):
    build_synthetic_vault(tmp_path, 10)
    notes = _notes(tmp_path)
    report = analyze_vault(notes, tmp_path, generated_at=None,
                           vault_version=compute_vault_fingerprint(notes))
    d = report.to_dict()
    assert d["schemaVersion"] == "1.0"
    assert d["generatedBy"].startswith("Jarvis ")
    assert d["timestamp"] is None  # deterministic when not supplied
    assert d["vaultVersion"].startswith("sha256:")


def test_fingerprint_changes_with_content(tmp_path: Path):
    v1 = tmp_path / "v1"
    v2 = tmp_path / "v2"
    build_synthetic_vault(v1, 10)
    build_synthetic_vault(v2, 11)
    assert compute_vault_fingerprint(_notes(v1)) != compute_vault_fingerprint(_notes(v2))


def test_fingerprint_stable_for_same_content(tmp_path: Path):
    build_synthetic_vault(tmp_path, 10)
    notes = _notes(tmp_path)
    assert compute_vault_fingerprint(notes) == compute_vault_fingerprint(notes)


def test_deterministic_json_identical_when_no_timestamp(tmp_path: Path):
    build_synthetic_vault(tmp_path, 12)
    notes = _notes(tmp_path)
    fp = compute_vault_fingerprint(notes)
    a = json.dumps(analyze_vault(notes, tmp_path, vault_version=fp).to_dict())
    b = json.dumps(analyze_vault(notes, tmp_path, vault_version=fp).to_dict())
    assert a == b
