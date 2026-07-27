from __future__ import annotations

from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.policy import local_allow_all
from jarvis_core.query import Intent, QueryEngine
from jarvis_core.repositories import FileSystemKnowledgeRepository
from tests.support.synthetic_vault import build_query_vault


def _engine(path: Path) -> QueryEngine:
    return QueryEngine(FileSystemKnowledgeRepository(Config(vault_path=path)).discover(),
                       scope=local_allow_all("local"))


def test_projects_mentioning_quickbooks(tmp_path: Path):
    build_query_vault(tmp_path)
    r = _engine(tmp_path).ask("What projects mention QuickBooks?")
    assert r.intent is Intent.PROJECTS_MENTIONING
    titles = {m.title for m in r.matches}
    assert "Bookkeeping App" in titles
    assert "Marketing Site" not in titles


def test_related_to_home_automation(tmp_path: Path):
    build_query_vault(tmp_path)
    r = _engine(tmp_path).ask("Show every note related to Home Automation")
    assert r.intent is Intent.RELATED_TO
    rels = {m.relpath for m in r.matches}
    assert "Home Automation.md" in rels
    assert "Smart Home.md" in rels  # neighbour via wikilink


def test_summarize_project(tmp_path: Path):
    build_query_vault(tmp_path)
    r = _engine(tmp_path).ask("Summarize the Bookkeeping App project.")
    assert r.intent is Intent.SUMMARIZE_PROJECT
    assert "Bookkeeping App" in r.answer


def test_summarize_unknown_project_is_graceful(tmp_path: Path):
    build_query_vault(tmp_path)
    r = _engine(tmp_path).ask("Summarize the Nonexistent project.")
    assert r.intent is Intent.SUMMARIZE_PROJECT
    assert "No project" in r.answer


def test_generic_search_fallback(tmp_path: Path):
    build_query_vault(tmp_path)
    r = _engine(tmp_path).ask("invoices")
    assert r.intent is Intent.SEARCH
    assert any(m.relpath == "Bookkeeping App.md" for m in r.matches)


def test_query_is_deterministic(tmp_path: Path):
    build_query_vault(tmp_path)
    eng = _engine(tmp_path)
    a = eng.ask("What projects mention QuickBooks?").to_dict()
    b = eng.ask("What projects mention QuickBooks?").to_dict()
    assert a == b
