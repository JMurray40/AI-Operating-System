"""Prove the application never modifies its inputs (read-only safety)."""
from __future__ import annotations

import hashlib
from pathlib import Path

from jarvis_core import cli

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _snapshot(root: Path) -> dict[str, str]:
    snap: dict[str, str] = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            snap[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return snap


def test_full_run_does_not_modify_fixtures():
    before = _snapshot(FIXTURES)
    # Exercise every command across every fixture.
    cli.main(["inspect", str(FIXTURES / "ai-operating-system")])
    cli.main(["inspect", str(FIXTURES / "edge-cases")])
    cli.main(["validate", str(FIXTURES / "fileorbit")])
    cli.main(["validate", str(FIXTURES / "edge-cases")])
    cli.main(["load-project", "AI Operating System",
              "--path", str(FIXTURES / "ai-operating-system"), "--format", "json"])
    cli.main(["summarize-project", "FileOrbit",
              "--path", str(FIXTURES / "fileorbit"), "--provider", "mock"])
    cli.main(["vault-report", str(FIXTURES / "ai-operating-system")])
    cli.main(["vault-report", str(FIXTURES / "edge-cases"), "--format", "json"])
    cli.main(["ask", "Summarize the FileOrbit project.", "--path", str(FIXTURES / "fileorbit")])
    cli.main(["ask", "notes related to Markdown", "--path", str(FIXTURES / "ai-operating-system")])
    after = _snapshot(FIXTURES)
    assert before == after, "fixture files changed during a run (read-only violation)"
    # no files added or removed
    assert set(before) == set(after)
