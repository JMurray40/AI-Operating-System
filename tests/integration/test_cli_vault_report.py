from __future__ import annotations

from pathlib import Path

from jarvis_core import cli
from tests.support.synthetic_vault import build_defect_vault, build_synthetic_vault


def test_vault_report_text_healthy(tmp_path: Path, capsys):
    build_synthetic_vault(tmp_path, 20)
    code = cli.main(["vault-report", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == cli.EXIT_OK
    assert "Vault Health Report" in out
    assert "PERFORMANCE" in out  # timing on by default


def test_vault_report_no_timing(tmp_path: Path, capsys):
    build_synthetic_vault(tmp_path, 10)
    cli.main(["vault-report", str(tmp_path), "--no-timing"])
    out = capsys.readouterr().out
    assert "PERFORMANCE" not in out


def test_vault_report_defects_fatal(tmp_path: Path, capsys):
    build_defect_vault(tmp_path)
    code = cli.main(["vault-report", str(tmp_path)])
    assert code == cli.EXIT_FATAL  # duplicate ids + invalid schema are errors


def test_vault_report_json(tmp_path: Path, capsys):
    build_defect_vault(tmp_path)
    cli.main(["vault-report", str(tmp_path), "--format", "json"])
    out = capsys.readouterr().out
    assert '"counts_by_category"' in out
    assert '"circular_reference"' in out


def test_output_file_disabled_by_default(tmp_path: Path):
    vault = tmp_path / "vault"
    build_synthetic_vault(vault, 5)
    before = {p.name for p in tmp_path.iterdir()}
    cli.main(["vault-report", str(vault)])
    after = {p.name for p in tmp_path.iterdir()}
    assert before == after  # no report file created unless --output is given


def test_output_file_written_when_requested(tmp_path: Path):
    vault = tmp_path / "vault"
    build_synthetic_vault(vault, 5)
    out_file = tmp_path / "health.txt"
    cli.main(["vault-report", str(vault), "--output", str(out_file)])
    assert out_file.exists()
    assert "Vault Health Report" in out_file.read_text(encoding="utf-8")
