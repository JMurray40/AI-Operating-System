"""C11: the ``jarvis resume`` CLI command (brief §13).

Exercises the resume subcommand end-to-end through ``cli.main``: text and JSON rendering, the
optional trace, the terminal outcomes and their distinct exit codes, both budget overrides,
repository-activity activation (flag validation + real-Git degradation on a non-repository
root), and read-only integrity of the vault. Output is stdout only.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jarvis_core import cli

_DATE = "2026-07-27"
_EVAL = "2026-07-28T00:00:00Z"


def _write(root: Path, fname: str, front: str, body: str) -> None:
    (root / fname).write_text(f"---\n{front}---\n\n{body}\n", encoding="utf-8")


def _vault(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    _write(
        root, "Alpha.md",
        f'id: project-alpha\ntype: project\ntitle: "Alpha"\nstatus: active\n'
        f"created: {_DATE}\nupdated: {_DATE}\ngoal: g\npriority: high\nsensitivity: internal\n",
        "# Alpha\n\n## Current state\n\nThe Alpha widget pipeline is green and shipping weekly.\n",
    )
    _write(
        root, "Decision.md",
        f'id: decision-one\ntype: decision\ntitle: "Adopt widgets"\nstatus: accepted\n'
        f"created: {_DATE}\nupdated: {_DATE}\nsensitivity: internal\ndecision_date: {_DATE}\n"
        "projects: [Alpha]\n",
        "# Adopt widgets\n\nWe will adopt the Alpha widget pipeline for shipping.\n",
    )


def _vault_hash(root: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        if p.is_file():
            h.update(p.relative_to(root).as_posix().encode())
            h.update(b"\0")
            h.update(p.read_bytes())
            h.update(b"\0")
    return h.hexdigest()


def _base_args(root: Path, selector: str = "Alpha") -> list[str]:
    return ["resume", selector, "--path", str(root), "--as-of", _EVAL]


# ---------------------------------------------------------------- happy path


def test_resume_text_complete(tmp_path: Path, capsys) -> None:
    _vault(tmp_path)
    code = cli.main(_base_args(tmp_path))
    out = capsys.readouterr().out
    assert code == 0
    assert "== PROJECT RESUME ==" in out
    assert "Project : Alpha" in out
    assert "[supported]" in out
    assert "L0-L0" not in out


def test_resume_json_is_valid_and_versioned(tmp_path: Path, capsys) -> None:
    _vault(tmp_path)
    code = cli.main([*_base_args(tmp_path), "--format", "json"])
    out = capsys.readouterr().out
    payload = json.loads(out)  # must be valid JSON
    assert code == 0
    assert payload["status"] == "complete"
    assert payload["contract_version"] == "jarvis.project-resume.v0.4.0"
    assert payload["project_identity"]["title"] == "Alpha"


def test_resume_trace_flag_includes_trace(tmp_path: Path, capsys) -> None:
    _vault(tmp_path)
    cli.main([*_base_args(tmp_path), "--trace", "--format", "json"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["trace"] is not None
    assert str(payload["trace"]["workspace_fingerprint"]).startswith("sha256:")
    assert "candidates" not in payload["trace"]  # rejected candidates never traced


# ---------------------------------------------------------------- terminals + exit codes


def test_resume_not_found_exit_code(tmp_path: Path, capsys) -> None:
    _vault(tmp_path)
    code = cli.main(_base_args(tmp_path, selector="Nonexistent"))
    out = capsys.readouterr().out
    assert code == 4
    assert "not_found" in out


def test_resume_ambiguous_exit_code(tmp_path: Path, capsys) -> None:
    tmp_path.mkdir(parents=True, exist_ok=True)
    for stem, pid in (("A1", "project-a1"), ("A2", "project-a2")):
        _write(
            tmp_path, f"{stem}.md",
            f'id: {pid}\ntype: project\ntitle: "Alpha"\nstatus: active\n'
            f"created: {_DATE}\nupdated: {_DATE}\ngoal: g\npriority: high\nsensitivity: internal\n",
            f"# {stem}\n",
        )
    code = cli.main(_base_args(tmp_path, selector="Alpha"))
    out = capsys.readouterr().out
    assert code == 3
    assert "Ambiguous candidates" in out


def test_resume_output_budget_error_exit_code(tmp_path: Path, capsys) -> None:
    _vault(tmp_path)
    code = cli.main([*_base_args(tmp_path), "--output-budget", "256"])
    capsys.readouterr()
    assert code == 7


def test_resume_invalid_budget_range_exit_code(tmp_path: Path, capsys) -> None:
    _vault(tmp_path)
    code = cli.main([*_base_args(tmp_path), "--evidence-budget", "10"])  # below the 256 minimum
    err = capsys.readouterr().err
    assert code == 7  # budget range failure maps to the budget exit code
    assert "evidence_token_budget" in err


# ---------------------------------------------------------------- repository activity


def test_resume_repository_flag_requires_root(tmp_path: Path, capsys) -> None:
    _vault(tmp_path)
    code = cli.main([*_base_args(tmp_path), "--include-repository-activity"])
    err = capsys.readouterr().err
    assert code == 5  # invalid input
    assert "requires --repository-root" in err


def test_resume_repository_non_repo_degrades_but_completes(tmp_path: Path, capsys) -> None:
    _vault(tmp_path)
    not_a_repo = tmp_path / "notrepo"
    not_a_repo.mkdir()
    code = cli.main(
        [*_base_args(tmp_path), "--include-repository-activity",
         "--repository-root", str(not_a_repo), "--format", "json"]
    )
    payload = json.loads(capsys.readouterr().out)
    # Local vault evidence stays usable; the missing repository is a limitation, not a failure.
    assert code in (0, 2)
    assert not payload["repository_citations"]
    assert any(
        limit["code"].startswith(("unavailable", "denied")) for limit in payload["limitations"]
    )


# ---------------------------------------------------------------- read-only integrity


def test_resume_does_not_modify_the_vault(tmp_path: Path, capsys) -> None:
    _vault(tmp_path)
    before = _vault_hash(tmp_path)
    cli.main([*_base_args(tmp_path), "--trace"])
    capsys.readouterr()
    assert _vault_hash(tmp_path) == before  # no source bytes, metadata, or files changed
