"""AC-03: claim-supporting citation binding — heading hierarchy, metadata, decline cases."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from jarvis_core.identity import fingerprint_bytes
from jarvis_core.models.note import Note
from jarvis_core.query.passages import Locator, locate, validate_against_text


def _note(text: str) -> Note:
    base = Note(path=Path("t.md"), relpath="t.md", frontmatter={}, body=text)
    body_start = 1  # these fixtures have no frontmatter fence
    return replace(base, source_text=text, source_fingerprint=fingerprint_bytes(text.encode()),
                   body_start_line=body_start)


def test_metadata_title_match_cites_frontmatter():
    text = ('---\ntitle: "ZebraWidget"\n---\n\n# Overview\n\nGeneric body with no match.\n')
    note = _note(text)
    note = replace(note, body_start_line=5)  # body starts after the closing fence
    loc, excerpt = locate(note, frozenset({"zebrawidget"}))
    assert loc.heading_path == ()               # frontmatter passage, before any heading
    assert "zebrawidget" in excerpt.lower()     # excerpt shows the actual evidence


def test_duplicate_leaf_heading_requires_full_path():
    text = "# Alpha\n\n## Shared\n\nunique-xterm detail\n\n# Beta\n\n## Shared\n\nother detail\n"
    note = _note(text)
    loc, excerpt = locate(note, frozenset({"unique-xterm"}))
    assert loc.heading_path == ("Alpha", "Shared")     # full path distinguishes the sections
    assert validate_against_text(loc, excerpt, text).ok is True
    # A locator claiming the Beta>Shared path but pointing at the Alpha section fails.
    wrong = Locator(("Beta", "Shared"), loc.line_start, loc.line_end)
    assert validate_against_text(wrong, excerpt, text).ok is False


def test_renamed_parent_invalidates_citation():
    text = "# Alpha\n\n## Shared\n\ndetail token here\n"
    note = _note(text)
    loc, excerpt = locate(note, frozenset({"token"}))
    assert loc.heading_path == ("Alpha", "Shared")
    renamed = text.replace("# Alpha", "# Renamed")
    assert validate_against_text(loc, excerpt, renamed).ok is False


def test_locator_moved_outside_section_invalid():
    text = "# One\n\nfirst section\n\n# Two\n\nsecond section\n"
    note = _note(text)
    locate(note, frozenset({"first"}))  # sanity: locates in the One section
    # Claim the same ("One",) path but a line range inside the "Two" section.
    bad = Locator(("One",), 7, 7)
    assert validate_against_text(bad, "second section", text).ok is False


def test_empty_excerpt_rejected():
    text = "# H\n\nbody\n"
    assert validate_against_text(Locator(("H",), 3, 3), "", text).ok is False


def test_empty_source_declines():
    note = _note("")
    loc, excerpt = locate(note, frozenset({"anything"}))
    assert loc == Locator((), 0, 0)
    assert excerpt == ""


def test_evidence_absent_declines():
    note = _note("# H\n\nno matching terms at all\n")
    loc, excerpt = locate(note, frozenset({"missingterm"}))
    assert loc == Locator((), 0, 0) and excerpt == ""
