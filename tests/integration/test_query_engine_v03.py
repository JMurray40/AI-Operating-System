from __future__ import annotations

from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.policy import local_allow_all
from jarvis_core.query import Intent, QueryEngine
from jarvis_core.repositories import FileSystemKnowledgeRepository
from tests.support.synthetic_vault import build_feature_vault


def _engine(path: Path) -> QueryEngine:
    build_feature_vault(path)
    notes = FileSystemKnowledgeRepository(Config(vault_path=path)).discover()
    return QueryEngine(notes, scope=local_allow_all("local"), source_root=path)


# --- search -------------------------------------------------------------------
def test_search_exact_title_ranks_first(tmp_path: Path):
    a = _engine(tmp_path).search("Ledger")
    assert a.citations[0].relpath == "Ledger.md"
    assert a.citations[0].relative_relevance == 1.0


def test_search_alias_match(tmp_path: Path):
    a = _engine(tmp_path).search("Billing")
    assert any(c.relpath == "Invoicing.md" for c in a.citations)


def test_search_tag_match(tmp_path: Path):
    a = _engine(tmp_path).search("finance")
    assert any(c.relpath == "Invoicing.md" for c in a.citations)


def test_search_partial_term(tmp_path: Path):
    a = _engine(tmp_path).search("quickbooks")
    hits = {c.relpath for c in a.citations}
    assert {"Invoicing.md", "Payments.md"} <= hits
    assert "Scratch.md" not in hits  # unknown sensitivity -> excluded (ADR-0015)


def test_search_empty_result(tmp_path: Path):
    a = _engine(tmp_path).search("zzz-nothing-matches")
    assert a.citations == ()
    assert "No notes match" in a.answer


def test_missing_frontmatter_note_is_excluded_fail_closed(tmp_path: Path):
    # A note without frontmatter has unknown sensitivity and must fail closed (ADR-0015).
    a = _engine(tmp_path).search("exports")
    assert all(c.relpath != "Scratch.md" for c in a.citations)


def test_every_citation_has_reason_and_relevance(tmp_path: Path):
    a = _engine(tmp_path).search("quickbooks")
    for c in a.citations:
        assert c.reason
        assert c.relative_relevance is None or 0.0 <= c.relative_relevance <= 1.0
        assert c.relpath


# --- duplicate titles ---------------------------------------------------------
def test_duplicate_titles_both_returned_stably(tmp_path: Path):
    a = _engine(tmp_path).search("report")
    reports = [c.relpath for c in a.citations if c.relpath.startswith("Report")]
    assert reports == ["Report A.md", "Report B.md"]


# --- projects mentioning (graph-aware) ---------------------------------------
def test_projects_mentioning_via_linked_note(tmp_path: Path):
    # Storefront mentions QuickBooks only through its linked note 'Payments'.
    ans, _ = _engine(tmp_path).run("What projects mention QuickBooks?")
    assert ans.intent is Intent.PROJECTS_MENTIONING
    # The answer prose still names both projects (graph-aware selection)...
    assert "Invoicing" in ans.answer and "Storefront" in ans.answer
    cited = {c.relpath for c in ans.citations}
    # ...but a citation is only emitted where a supporting passage exists in that note
    # itself (AC-03). Invoicing contains "QuickBooks"; Storefront does not (its evidence
    # lives in the linked Payments note), so Storefront yields no material citation.
    assert "Invoicing.md" in cited
    assert "Storefront.md" not in cited


# --- broken links do not crash ------------------------------------------------
def test_broken_wikilink_is_tolerated(tmp_path: Path):
    # Invoicing links to a non-existent 'Ghost Note'; explain/search must not error.
    a = _engine(tmp_path).search("invoicing")
    assert a.citations


# --- explain ------------------------------------------------------------------
def test_explain_direct_link(tmp_path: Path):
    a = _engine(tmp_path).explain("Invoicing", "Ledger")
    assert "directly linked" in a.answer
    assert {c.relpath for c in a.citations} == {"Invoicing.md", "Ledger.md"}


def test_explain_unknown_note_is_graceful(tmp_path: Path):
    a = _engine(tmp_path).explain("Invoicing", "Does Not Exist")
    assert "Could not find" in a.answer
    assert a.citations == ()


# --- summarize ----------------------------------------------------------------
def test_summarize_unknown_project_is_graceful(tmp_path: Path):
    a = _engine(tmp_path).summarize("No Such Project")
    assert "No project" in a.answer


# --- trace --------------------------------------------------------------------
def test_trace_captures_ranking_and_context(tmp_path: Path):
    _, trace = _engine(tmp_path).run("Show notes related to Invoicing", want_trace=True)
    assert trace is not None
    d = trace.to_dict()
    assert d["parsed"]["intent"] == "related_to"
    assert d["ranked"]
    assert d["context"] is not None
    text = trace.render_text()
    assert "TRACE" in text and "Ranking" in text


def test_run_without_trace_returns_none(tmp_path: Path):
    _, trace = _engine(tmp_path).run("quickbooks")
    assert trace is None


# --- determinism --------------------------------------------------------------
def test_answers_are_deterministic(tmp_path: Path):
    eng = _engine(tmp_path)
    a = eng.search("quickbooks").to_dict()
    b = eng.search("quickbooks").to_dict()
    assert a == b
