from __future__ import annotations

from jarvis_core.query.intent import Intent, IntentParser


def _parse(q: str):
    return IntentParser().parse(q)


def test_summarize_intent():
    p = _parse("Summarize the FileOrbit project.")
    assert p.intent is Intent.SUMMARIZE_PROJECT
    assert p.target == "fileorbit"


def test_projects_mentioning_intent():
    p = _parse("What projects mention QuickBooks?")
    assert p.intent is Intent.PROJECTS_MENTIONING
    assert "quickbooks" in p.terms


def test_related_to_intent():
    p = _parse("Show every note related to Home Automation")
    assert p.intent is Intent.RELATED_TO
    assert p.target == "home automation"


def test_explain_intent_extracts_both_sides():
    p = _parse("Explain the relationship between Project A and Project B")
    assert p.intent is Intent.EXPLAIN_RELATIONSHIP
    assert p.left == "project a"
    assert p.right == "project b"


def test_search_fallback():
    p = _parse("quickbooks invoices")
    assert p.intent is Intent.SEARCH
    assert p.terms == ("quickbooks", "invoices")


def test_parser_is_pure_and_deterministic():
    a = _parse("What projects mention QuickBooks?").to_dict()
    b = _parse("What projects mention QuickBooks?").to_dict()
    assert a == b
