"""Unchanged-vault evidence for v0.3.1: bytes, file set, and metadata are identical after
the complete query/CLI/citation path runs (ADR-0007, brief section 8)."""
from __future__ import annotations

import hashlib
from pathlib import Path

from jarvis_core import cli
from jarvis_core.config import Config
from jarvis_core.policy import local_allow_all
from jarvis_core.query import QueryEngine
from jarvis_core.query.passages import validate
from jarvis_core.repositories import FileSystemKnowledgeRepository

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _snapshot(root: Path) -> dict[str, tuple[str, int, int]]:
    snap: dict[str, tuple[str, int, int]] = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            st = p.stat()
            snap[p.relative_to(root).as_posix()] = (
                hashlib.sha256(p.read_bytes()).hexdigest(), st.st_size, int(st.st_mtime),
            )
    return snap


def test_full_query_path_does_not_modify_vault():
    vault = FIXTURES / "fileorbit"
    before = _snapshot(vault)

    # CLI surface
    cli.main(["ask", "Summarize the FileOrbit project.", "--path", str(vault)])
    cli.main(["search", "deduplication", "--path", str(vault)])
    cli.main(["explain", "FileOrbit", "File Deduplication", "--path", str(vault)])
    cli.main(["ask", "What projects mention deduplication?", "--path", str(vault),
              "--trace", "--format", "json"])

    # Engine surface under an explicit scope + citation validation (re-reads bytes).
    notes = FileSystemKnowledgeRepository(Config(vault_path=vault)).discover()
    eng = QueryEngine(notes, scope=local_allow_all("local"))
    ans = eng.search("deduplication")
    for c in ans.citations:
        note = eng.note_by_relpath(c.relpath)
        raw = (vault / c.relpath).read_bytes()
        validate(locator=c.locator, excerpt=c.excerpt, source_fingerprint=c.source_fingerprint,
                 current_bytes=raw, current_text=note.source_text)

    after = _snapshot(vault)
    assert before == after, "vault changed during the query path (read-only violation)"
    assert set(before) == set(after)
