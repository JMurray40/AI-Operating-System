from __future__ import annotations

from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.policy import local_allow_all
from jarvis_core.query import QueryEngine
from jarvis_core.query.passages import validate
from jarvis_core.repositories import FileSystemKnowledgeRepository


def _engine(path: Path) -> QueryEngine:
    notes = FileSystemKnowledgeRepository(Config(vault_path=path)).discover()
    return QueryEngine(notes, scope=local_allow_all("local"), source_root=path)


def test_ranked_citation_resolves_to_exact_source(fileorbit_dir: Path):
    eng = _engine(fileorbit_dir)
    c = eng.search("deduplication").citations[0]
    note = eng.note_by_relpath(c.relpath)
    raw = (fileorbit_dir / c.relpath).read_bytes()
    v = validate(locator=c.locator, excerpt=c.excerpt, source_fingerprint=c.source_fingerprint,
                 current_bytes=raw, current_text=note.source_text)
    assert v.ok is True
    assert c.source_identity_kind in ("explicit", "path_derived")
    assert c.relative_relevance is not None


def test_changed_bytes_make_citation_stale(fileorbit_dir: Path):
    eng = _engine(fileorbit_dir)
    c = eng.search("deduplication").citations[0]
    note = eng.note_by_relpath(c.relpath)
    mutated = (fileorbit_dir / c.relpath).read_bytes() + b"\nappended\n"
    v = validate(locator=c.locator, excerpt=c.excerpt, source_fingerprint=c.source_fingerprint,
                 current_bytes=mutated, current_text=note.source_text)
    assert v.ok is False and "stale" in v.reason
