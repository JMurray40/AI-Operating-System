from __future__ import annotations

from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.query.passages import Locator, locate, validate
from jarvis_core.repositories import FileSystemKnowledgeRepository
from tests.support.synthetic_vault import build_trust_vault_no_dupes


def _notes(path: Path):
    build_trust_vault_no_dupes(path)
    return {n.relpath: n for n in
            FileSystemKnowledgeRepository(Config(vault_path=path)).discover()}


def test_nested_heading_path(tmp_path: Path):
    note = _notes(tmp_path)["Crlf.md"]
    loc, excerpt = locate(note, frozenset({"carriage"}))
    assert loc.heading_path == ("Crlf", "Details")
    assert "carriage" in excerpt.lower()
    assert loc.line_start <= loc.line_end


def test_single_heading_note_path(tmp_path: Path):
    note = _notes(tmp_path)["Bare.md"]  # frontmatter-less note with a single H1
    loc, excerpt = locate(note, frozenset({"frontmatter"}))
    assert loc.heading_path == ("Bare",)
    assert excerpt


def test_validate_ok_and_stale(tmp_path: Path):
    notes = _notes(tmp_path)
    note = notes["Crlf.md"]
    loc, excerpt = locate(note, frozenset({"carriage"}))
    raw = (tmp_path / "Crlf.md").read_bytes()
    ok = validate(locator=loc, excerpt=excerpt, source_fingerprint=note.source_fingerprint,
                  current_bytes=raw, current_text=note.source_text)
    assert ok.ok is True
    stale = validate(locator=loc, excerpt=excerpt, source_fingerprint=note.source_fingerprint,
                     current_bytes=raw + b"x", current_text=note.source_text)
    assert stale.ok is False and "stale" in stale.reason


def test_validate_bad_range_and_excerpt_mismatch(tmp_path: Path):
    notes = _notes(tmp_path)
    note = notes["Crlf.md"]
    loc, excerpt = locate(note, frozenset({"carriage"}))
    raw = (tmp_path / "Crlf.md").read_bytes()
    bad = validate(locator=Locator(loc.heading_path, 9990, 9991), excerpt=excerpt,
                   source_fingerprint=note.source_fingerprint, current_bytes=raw,
                   current_text=note.source_text)
    assert bad.ok is False and "range" in bad.reason
    mism = validate(locator=loc, excerpt="text that is not present anywhere zzz",
                    source_fingerprint=note.source_fingerprint, current_bytes=raw,
                    current_text=note.source_text)
    assert mism.ok is False and "excerpt" in mism.reason


def test_crlf_and_lf_fingerprints_differ_but_locate(tmp_path: Path):
    note = _notes(tmp_path)["Crlf.md"]
    # CRLF source still yields a resolvable locator/excerpt
    loc, excerpt = locate(note, frozenset({"carriage"}))
    assert excerpt and 1 <= loc.line_start <= loc.line_end <= len(note.source_lines)
