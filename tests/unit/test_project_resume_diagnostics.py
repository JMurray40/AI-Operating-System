"""C13: read-only diagnostics and derived-state recovery (brief §21, A12).

The doctor rebuilds derived state (authorized view + lexical index + relationship graph) from
canonical sources — there is no persisted index, so a "missing/corrupt derived index" self-heals
on the next run — and diagnoses the runtime, vault, Git availability, and an optional repository
root, all strictly read-only.
"""
from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

import pytest

from jarvis_core.config import Config
from jarvis_core.policy import local_allow_all
from jarvis_core.project_resume import diagnostics as diag
from jarvis_core.project_resume.diagnostics import (
    STATUS_FAIL,
    STATUS_OK,
    STATUS_WARN,
    run_diagnostics,
)
from jarvis_core.repositories import FileSystemKnowledgeRepository

_DATE = "2026-07-27"


def _write(root: Path, fname: str, front: str, body: str) -> None:
    (root / fname).write_text(f"---\n{front}---\n\n{body}\n", encoding="utf-8")


def _vault(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    _write(
        root, "Alpha.md",
        f'id: project-alpha\ntype: project\ntitle: "Alpha"\nstatus: active\n'
        f"created: {_DATE}\nupdated: {_DATE}\ngoal: g\npriority: high\nsensitivity: internal\n",
        "# Alpha\n\n## Current state\n\nThe Alpha widget pipeline is green.\n",
    )


def _notes(root: Path):
    return FileSystemKnowledgeRepository(Config(vault_path=root)).discover()


def _report_for(root: Path, **kw):
    return run_diagnostics(
        _notes(root), scope=local_allow_all("local"), source_root=root, **kw
    )


def _check(report, name):
    return next(c for c in report.checks if c.name == name)


def _vault_hash(root: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        if p.is_file():
            h.update(p.read_bytes())
    return h.hexdigest()


def test_healthy_vault_rebuilds_derived_state(tmp_path: Path) -> None:
    _vault(tmp_path)
    report = _report_for(tmp_path)
    assert report.overall_status in (STATUS_OK, STATUS_WARN)  # git may be absent in some envs
    derived = _check(report, "derived_state")
    assert derived.status == STATUS_OK
    assert derived.detail["index_version"]  # the derived index version is reported
    assert str(derived.detail["workspace_fingerprint"]).startswith("sha256:")


def test_empty_vault_fails(tmp_path: Path) -> None:
    report = run_diagnostics(
        [], scope=local_allow_all("local"), source_root=tmp_path
    )
    assert _check(report, "vault").status == STATUS_FAIL
    assert report.overall_status == STATUS_FAIL


def test_duplicate_identity_fails_derived_state(tmp_path: Path) -> None:
    tmp_path.mkdir(parents=True, exist_ok=True)
    for fname in ("D1.md", "D2.md"):
        _write(
            tmp_path, fname,
            f'id: project-dup\ntype: project\ntitle: "Dup {fname}"\nstatus: active\n'
            f"created: {_DATE}\nupdated: {_DATE}\ngoal: g\npriority: high\nsensitivity: internal\n",
            "# dup\n",
        )
    report = _report_for(tmp_path)
    derived = _check(report, "derived_state")
    assert derived.status == STATUS_FAIL
    assert "identity" in derived.message.lower()


def test_missing_git_is_a_warning_not_a_failure(tmp_path: Path, monkeypatch) -> None:
    _vault(tmp_path)
    monkeypatch.setattr(diag, "resolve_git_executable", lambda *a, **k: None)
    report = _report_for(tmp_path)
    git = _check(report, "git")
    assert git.status == STATUS_WARN
    assert git.detail["available"] is False
    # A missing Git never fails the run; local vault diagnostics stay healthy.
    assert _check(report, "derived_state").status == STATUS_OK


def test_repository_root_missing_directory_fails(tmp_path: Path) -> None:
    _vault(tmp_path)
    report = _report_for(tmp_path, repository_root=tmp_path / "does-not-exist")
    repo = _check(report, "repository_root")
    assert repo.status == STATUS_FAIL


@pytest.mark.skipif(shutil.which("git") is None, reason="git not available")
def test_repository_root_non_repo_is_rejected(tmp_path: Path) -> None:
    _vault(tmp_path)
    not_repo = tmp_path / "plain"
    not_repo.mkdir()
    report = _report_for(tmp_path, repository_root=not_repo)
    repo = _check(report, "repository_root")
    # A non-repository (or a root that does not canonicalize to itself) is rejected, redacted.
    assert repo.status == STATUS_FAIL
    assert repo.detail["kind"] in ("unavailable", "denied")


def test_diagnostics_is_read_only(tmp_path: Path) -> None:
    _vault(tmp_path)
    before = _vault_hash(tmp_path)
    _report_for(tmp_path, repository_root=tmp_path)
    assert _vault_hash(tmp_path) == before  # no canonical source was written or repaired


def test_report_serialization_is_stable(tmp_path: Path) -> None:
    _vault(tmp_path)
    report = _report_for(tmp_path)
    data = report.to_dict()
    assert data["overall_status"] == report.overall_status
    assert [c["name"] for c in data["checks"]][:3] == ["runtime", "vault", "derived_state"]
