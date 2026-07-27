from __future__ import annotations

from pathlib import Path

from jarvis_core import cli


def test_inspect_ok(aios_dir: Path, capsys):
    code = cli.main(["inspect", str(aios_dir)])
    out = capsys.readouterr().out
    assert code == cli.EXIT_OK
    assert "Notes: 7" in out


def test_validate_edge_cases_returns_fatal(edge_dir: Path, capsys):
    code = cli.main(["validate", str(edge_dir)])
    assert code == cli.EXIT_FATAL  # contains a syntax error


def test_validate_clean_ok(aios_dir: Path):
    assert cli.main(["validate", str(aios_dir)]) == cli.EXIT_OK


def test_load_project_json(aios_dir: Path, capsys):
    code = cli.main(
        ["load-project", "AI Operating System", "--path", str(aios_dir), "--format", "json"]
    )
    out = capsys.readouterr().out
    assert code in (cli.EXIT_OK, cli.EXIT_WARNINGS)
    assert '"project-ai-operating-system"' in out


def test_summarize_project_mock(fileorbit_dir: Path, capsys):
    code = cli.main(
        ["summarize-project", "FileOrbit", "--path", str(fileorbit_dir), "--provider", "mock"]
    )
    out = capsys.readouterr().out
    assert code in (cli.EXIT_OK, cli.EXIT_WARNINGS)
    assert "[mock:fast]" in out
    assert "FileOrbit" in out


def test_unknown_project_is_fatal(aios_dir: Path):
    assert cli.main(["load-project", "Nope", "--path", str(aios_dir)]) == cli.EXIT_FATAL
