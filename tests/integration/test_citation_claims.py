"""AC-03R2b: unranked (summarize/explain) citations are claim-specific, never arbitrary."""
from __future__ import annotations

from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.policy import local_allow_all
from jarvis_core.query import QueryEngine
from jarvis_core.repositories import FileSystemKnowledgeRepository

_DATE = "2026-07-27"


def _build(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    # Project whose FIRST body section is unrelated; the project identity/link is later.
    (root / "Zeta.md").write_text(
        "---\nid: project-zeta\ntype: project\ntitle: \"Zeta\"\nstatus: active\n"
        f"created: {_DATE}\nupdated: {_DATE}\ngoal: \"Zeta goal\"\npriority: high\n"
        "sensitivity: internal\n---\n\n# Zeta\n\n## Intro\n\n"
        "Completely unrelated preamble content about weather.\n\n"
        "## Links\n\nRelated work: [[Helper]].\n",
        encoding="utf-8",
    )
    (root / "Helper.md").write_text(
        "---\nid: concept-helper\ntype: concept\ntitle: \"Helper\"\nstatus: active\n"
        f"created: {_DATE}\nupdated: {_DATE}\nsensitivity: internal\nprojects: [Zeta]\n---\n\n"
        "# Helper\n\nUnrelated opening line about cooking.\n\nSupports [[Zeta]] directly.\n",
        encoding="utf-8",
    )
    # A resource linked FROM the project whose own text never names the project -> a source
    # reference with no claim-supporting passage (coverage=incomplete).
    (root / "Widget.md").write_text(
        "---\nid: resource-widget\ntype: resource\ntitle: \"Widget\"\nresource_type: doc\n"
        f"source_of_truth: local\nstatus: active\ncreated: {_DATE}\nupdated: {_DATE}\n"
        "sensitivity: internal\n---\n\n# Widget\n\nStandalone widget notes, unrelated text.\n",
        encoding="utf-8",
    )
    # Link the resource from the project so it enters the summary context.
    zeta = root / "Zeta.md"
    zeta.write_text(zeta.read_text(encoding="utf-8").replace(
        "Related work: [[Helper]].", "Related work: [[Helper]] and [[Widget]]."),
        encoding="utf-8")


def _engine(path: Path) -> QueryEngine:
    _build(path)
    notes = FileSystemKnowledgeRepository(Config(vault_path=path)).discover()
    return QueryEngine(notes, scope=local_allow_all("local"), source_root=path)


def test_summarize_citations_are_claim_specific_not_first_content(tmp_path: Path):
    a = _engine(tmp_path).summarize("Zeta")
    by = {c.relpath: c for c in a.citations}
    # Every supported citation cites a passage that actually references the project 'Zeta',
    # never the unrelated first section.
    for c in a.citations:
        if c.coverage == "supported":
            assert "zeta" in c.excerpt.lower()
            assert "weather" not in c.excerpt.lower()   # not the unrelated preamble
            assert "cooking" not in c.excerpt.lower()
    # Helper references Zeta -> supported with the linking passage.
    assert "Helper.md" in by and by["Helper.md"].coverage == "supported"
    assert "zeta" in by["Helper.md"].excerpt.lower()


def test_explain_citations_cite_the_linking_passage(tmp_path: Path):
    a = _engine(tmp_path).explain("Zeta", "Helper")
    by = {c.relpath: c for c in a.citations}
    assert "directly linked" in a.answer or "share" in a.answer
    # Zeta cites the passage linking Helper (not its unrelated first section).
    if "Zeta.md" in by and by["Zeta.md"].coverage == "supported":
        assert "helper" in by["Zeta.md"].excerpt.lower()
        assert "weather" not in by["Zeta.md"].excerpt.lower()


def test_incomplete_coverage_has_no_arbitrary_excerpt(tmp_path: Path):
    # A source with no claim-specific supporting passage is marked incomplete, not filled.
    a = _engine(tmp_path).summarize("Zeta")
    for c in a.citations:
        if c.coverage == "incomplete":
            assert c.excerpt == ""
            assert c.locator.line_start == 0 and c.locator.line_end == 0


def test_summarize_produces_a_visible_incomplete_reference(tmp_path: Path):
    a = _engine(tmp_path).summarize("Zeta")
    by = {c.relpath: c for c in a.citations}
    # Widget is in the project context but never names the project -> incomplete reference.
    assert "Widget.md" in by
    assert by["Widget.md"].coverage == "incomplete"
    assert by["Widget.md"].excerpt == ""
    assert by["Widget.md"].locator.line_start == 0
    # Answer-level coverage signal reflects the mix.
    cov = a.citation_coverage()
    assert cov["label"] == "partial"
    assert cov["supported"] >= 1 and cov["incomplete"] >= 1
    # Incomplete references are not counted as supported (material) citations.
    assert all(c.coverage == "supported" for c in a.supported_citations())
    assert "Widget.md" not in {c.relpath for c in a.supported_citations()}
