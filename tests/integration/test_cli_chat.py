from __future__ import annotations

from pathlib import Path

from jarvis_core import cli


def test_cli_chat_scripted_turns(fileorbit_dir: Path, capsys):
    code = cli.main([
        "chat", "--path", str(fileorbit_dir),
        "--turns", "What is FileOrbit?", "Who is working on it?",
    ])
    out = capsys.readouterr().out
    assert code == cli.EXIT_OK
    assert "Why:" in out and "Confidence:" in out and "Sources:" in out
    assert "refers to 'FileOrbit'" in out  # pronoun resolution surfaced


def test_cli_chat_trace(fileorbit_dir: Path, capsys):
    cli.main([
        "chat", "--path", str(fileorbit_dir),
        "--turns", "What is FileOrbit?", "--trace",
    ])
    out = capsys.readouterr().out
    assert "CONVERSATION TRACE" in out


def test_cli_chat_json(fileorbit_dir: Path, capsys):
    cli.main([
        "chat", "--path", str(fileorbit_dir),
        "--turns", "What is FileOrbit?", "--format", "json",
    ])
    out = capsys.readouterr().out
    assert '"reasoning_summary"' in out
    assert '"statements"' in out


def test_cli_chat_stream(fileorbit_dir: Path, capsys):
    code = cli.main([
        "chat", "--path", str(fileorbit_dir), "--turns", "What is FileOrbit?", "--stream",
    ])
    assert code == cli.EXIT_OK
