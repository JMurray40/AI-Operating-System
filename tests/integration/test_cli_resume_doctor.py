"""C13: the `jarvis resume-doctor` CLI command (brief §21, A12).

Diagnoses the environment and rebuilds derived state, read-only. Healthy vaults exit 0 (or 2 if
Git is absent); an unusable vault or a rejected repository root exits non-zero.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from jarvis_core import cli

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


def test_doctor_text_healthy(tmp_path: Path, capsys) -> None:
    _vault(tmp_path)
    code = cli.main(["resume-doctor", "--path", str(tmp_path)])
    out = capsys.readouterr().out
    assert "== RESUME DOCTOR ==" in out
    assert "derived_state" in out
    assert code in (0, 2)  # 0 healthy, 2 if git is unavailable in the environment


def test_doctor_json_reports_checks(tmp_path: Path, capsys) -> None:
    _vault(tmp_path)
    cli.main(["resume-doctor", "--path", str(tmp_path), "--format", "json"])
    payload = json.loads(capsys.readouterr().out)
    names = [c["name"] for c in payload["checks"]]
    assert names[:3] == ["runtime", "vault", "derived_state"]
    assert payload["overall_status"] in ("ok", "warn", "fail")


def test_doctor_unusable_vault_fails(tmp_path: Path, capsys) -> None:
    # An empty directory has no readable notes -> vault check fails -> exit 1.
    empty = tmp_path / "empty"
    empty.mkdir()
    code = cli.main(["resume-doctor", "--path", str(empty)])
    capsys.readouterr()
    assert code == 1


@pytest.mark.skipif(shutil.which("git") is None, reason="git not available")
def test_doctor_rejects_bad_repository_root(tmp_path: Path, capsys) -> None:
    _vault(tmp_path)
    not_repo = tmp_path / "plain"
    not_repo.mkdir()
    code = cli.main(
        ["resume-doctor", "--path", str(tmp_path), "--repository-root", str(not_repo)]
    )
    out = capsys.readouterr().out
    assert code == 1
    assert "repository_root" in out
