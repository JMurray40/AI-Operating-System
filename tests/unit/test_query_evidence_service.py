"""C1: the extracted query-evidence service reproduces v0.3.1 citation behavior.

Covers path-confined current-byte re-read (fail closed on escape/missing/change) and the
supported / incomplete / declined-material citation outcomes, independent of QueryEngine.
"""
from __future__ import annotations

from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.policy import local_allow_all
from jarvis_core.query.authorized import build_authorized_view
from jarvis_core.query.evidence import CitationFactory, CurrentSourceResolver
from jarvis_core.repositories import FileSystemKnowledgeRepository

_DATE = "2026-07-27"


def _vault(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "Alpha.md").write_text(
        "---\nid: project-alpha\ntype: project\ntitle: \"Alpha\"\nstatus: active\n"
        f"created: {_DATE}\nupdated: {_DATE}\ngoal: \"Alpha goal\"\npriority: high\n"
        "sensitivity: internal\n---\n\n# Alpha\n\n## Intro\n\nUnrelated preamble.\n\n"
        "## Links\n\nRelated: [[Beta]] supports Alpha directly.\n",
        encoding="utf-8",
    )


def _factory(root: Path) -> tuple[CitationFactory, dict]:
    notes = FileSystemKnowledgeRepository(Config(vault_path=root)).discover()
    view = build_authorized_view(notes, local_allow_all("local"))
    by = {n.relpath: n for n in view.notes}
    return CitationFactory(view.identities, CurrentSourceResolver(root)), by


def test_resolver_confines_reads_and_fails_closed(tmp_path: Path):
    _vault(tmp_path)
    notes = FileSystemKnowledgeRepository(Config(vault_path=tmp_path)).discover()
    resolver = CurrentSourceResolver(tmp_path)
    note = next(n for n in notes if n.relpath == "Alpha.md")
    assert resolver.current_bytes(note) == (tmp_path / "Alpha.md").read_bytes()
    # Deleting the source -> empty bytes (fail closed), never a snapshot fallback.
    (tmp_path / "Alpha.md").unlink()
    assert resolver.current_bytes(note) == b""


def test_supported_citation_binds_claim_passage(tmp_path: Path):
    _vault(tmp_path)
    factory, by = _factory(tmp_path)
    note = by["Alpha.md"]
    cit = factory.make(
        note, frozenset({"alpha"}), relevance=None, reason="supports", material=False
    )
    assert cit is not None and cit.coverage == "supported"
    assert "alpha" in cit.excerpt.lower()
    assert cit.locator.line_start > 0


def test_material_reference_without_passage_is_declined(tmp_path: Path):
    _vault(tmp_path)
    factory, by = _factory(tmp_path)
    note = by["Alpha.md"]
    # A term that never appears -> no supporting passage; a material (ranked) reference is
    # declined entirely rather than emitted incomplete.
    assert factory.make(
        note, frozenset({"zzznotpresent"}), relevance=0.5, reason="retrieval match",
        material=True,
    ) is None


def test_unranked_reference_without_passage_is_incomplete(tmp_path: Path):
    _vault(tmp_path)
    factory, by = _factory(tmp_path)
    note = by["Alpha.md"]
    cit = factory.make(
        note, frozenset({"zzznotpresent"}), relevance=None, reason="context", material=False
    )
    assert cit is not None and cit.coverage == "incomplete"
    assert cit.excerpt == "" and cit.locator.line_start == 0 and cit.locator.line_end == 0


def test_changed_source_after_discovery_is_stale(tmp_path: Path):
    _vault(tmp_path)
    factory, by = _factory(tmp_path)
    note = by["Alpha.md"]
    (tmp_path / "Alpha.md").write_text("changed entirely\n", encoding="utf-8")
    assert factory.make(
        note, frozenset({"alpha"}), relevance=None, reason="supports", material=False
    ) is None
