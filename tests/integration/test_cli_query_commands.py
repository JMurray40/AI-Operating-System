from __future__ import annotations

from pathlib import Path

from jarvis_core import cli
from tests.support.synthetic_vault import build_feature_vault


def test_cli_search_ok(tmp_path: Path, capsys):
    build_feature_vault(tmp_path)
    code = cli.main(["search", "quickbooks", "--path", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == cli.EXIT_OK
    assert "Sources (supporting passages):" in out
    assert "relative relevance=" in out


def test_cli_search_empty_warns(tmp_path: Path):
    build_feature_vault(tmp_path)
    assert cli.main(["search", "zzznope", "--path", str(tmp_path)]) == cli.EXIT_WARNINGS


def test_cli_search_json_has_citations(tmp_path: Path, capsys):
    build_feature_vault(tmp_path)
    cli.main(["search", "ledger", "--path", str(tmp_path), "--format", "json"])
    out = capsys.readouterr().out
    assert '"citations"' in out
    assert '"relative_relevance"' in out


def test_cli_summarize_cited(tmp_path: Path, capsys):
    build_feature_vault(tmp_path)
    code = cli.main(["summarize", "Invoicing", "--path", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == cli.EXIT_OK
    assert "[mock:research]" in out
    assert "Sources (supporting passages):" in out


def test_cli_explain(tmp_path: Path, capsys):
    build_feature_vault(tmp_path)
    code = cli.main(["explain", "Invoicing", "Ledger", "--path", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == cli.EXIT_OK
    assert "directly linked" in out


def test_cli_ask_trace_text(tmp_path: Path, capsys):
    build_feature_vault(tmp_path)
    cli.main(["ask", "Show notes related to Invoicing", "--path", str(tmp_path), "--trace"])
    out = capsys.readouterr().out
    assert "== TRACE ==" in out
    assert "Ranking" in out


def test_cli_ask_trace_json(tmp_path: Path, capsys):
    build_feature_vault(tmp_path)
    cli.main(["ask", "quickbooks", "--path", str(tmp_path), "--trace", "--format", "json"])
    out = capsys.readouterr().out
    assert '"trace"' in out
