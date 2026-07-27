from __future__ import annotations

from pathlib import Path

from jarvis_core import cli
from tests.support.synthetic_vault import build_query_vault


def test_cli_ask_projects_mentioning(tmp_path: Path, capsys):
    build_query_vault(tmp_path)
    code = cli.main(["ask", "What projects mention QuickBooks?", "--path", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == cli.EXIT_OK
    assert "Bookkeeping App" in out
    assert "Sources (supporting passages):" in out


def test_cli_ask_json(tmp_path: Path, capsys):
    build_query_vault(tmp_path)
    cli.main(
        ["ask", "Summarize the Smart Home project.", "--path", str(tmp_path),
         "--format", "json"]
    )
    out = capsys.readouterr().out
    assert '"intent": "summarize_project"' in out


def test_cli_ask_no_match_warns(tmp_path: Path):
    build_query_vault(tmp_path)
    code = cli.main(["ask", "zzz-nonexistent-term", "--path", str(tmp_path)])
    assert code == cli.EXIT_WARNINGS
