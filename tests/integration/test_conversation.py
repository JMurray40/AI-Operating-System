from __future__ import annotations

from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.conversation import ConversationManager
from jarvis_core.conversation.explanation import StatementKind
from jarvis_core.query import QueryEngine
from jarvis_core.repositories import FileSystemKnowledgeRepository
from tests.support.synthetic_vault import build_feature_vault, build_query_vault


def _manager(path: Path) -> ConversationManager:
    notes = FileSystemKnowledgeRepository(Config(vault_path=path)).discover()
    return ConversationManager(QueryEngine(notes))


def test_followup_resolves_pronoun_to_prior_entity(fileorbit_dir: Path):
    mgr = _manager(fileorbit_dir)
    mgr.ask("What is FileOrbit?")
    ans, _ = mgr.ask("Who is working on it?")
    assert "FileOrbit" in ans.effective_query
    assert any("refers to 'FileOrbit'" in a for a in ans.assumptions)


def test_multi_turn_history_and_reset(fileorbit_dir: Path):
    mgr = _manager(fileorbit_dir)
    mgr.ask("What is FileOrbit?")
    mgr.ask("What are its risks?")
    assert mgr.session.turn_count == 2
    mgr.reset()
    assert mgr.session.turn_count == 0
    assert mgr.session.entity_stack == []


def test_entity_memory_tracks_focus(fileorbit_dir: Path):
    mgr = _manager(fileorbit_dir)
    mgr.ask("What is FileOrbit?")
    assert mgr.session.focus() is not None
    assert mgr.session.focus().title == "FileOrbit"


def test_taxonomy_has_facts_and_relationships(fileorbit_dir: Path):
    mgr = _manager(fileorbit_dir)
    ans, _ = mgr.ask("What is FileOrbit?")
    kinds = {s.kind for s in ans.statements}
    assert StatementKind.FACT in kinds
    assert StatementKind.RELATIONSHIP in kinds


def test_unknown_when_no_person_information(fileorbit_dir: Path):
    mgr = _manager(fileorbit_dir)
    mgr.ask("What is FileOrbit?")
    ans, _ = mgr.ask("Who is working on it?")
    assert any(s.kind is StatementKind.UNKNOWN for s in ans.statements)


def test_ambiguous_reference_across_topics(tmp_path: Path):
    build_query_vault(tmp_path)
    mgr = _manager(tmp_path)
    mgr.ask("What is Bookkeeping App?")
    mgr.ask("Summarize Smart Home")
    ans, _ = mgr.ask("Tell me about it")
    # 'it' is ambiguous across the two unrelated topics; resolver records the assumption
    assert any("unrelated" in a for a in ans.assumptions)


def test_conflicting_notes_detected(tmp_path: Path):
    build_feature_vault(tmp_path)  # contains two notes both titled "Report"
    mgr = _manager(tmp_path)
    ans, _ = mgr.ask("Show me the report")
    assert ans.conflicts
    subjects = {c.subject.lower() for c in ans.conflicts}
    assert "report" in subjects


def test_empty_result_is_graceful(fileorbit_dir: Path):
    mgr = _manager(fileorbit_dir)
    ans, _ = mgr.ask("zzz-nothing-here")
    assert ans.citations == ()
    assert any(s.kind is StatementKind.UNKNOWN for s in ans.statements)
    assert ans.confidence == 0.0


def test_conversation_is_deterministic(fileorbit_dir: Path):
    a = _manager(fileorbit_dir)
    b = _manager(fileorbit_dir)
    a.ask("What is FileOrbit?")
    b.ask("What is FileOrbit?")
    r1, _ = a.ask("What are its risks?")
    r2, _ = b.ask("What are its risks?")
    assert r1.to_dict() == r2.to_dict()


def test_trace_includes_conversation_state(fileorbit_dir: Path):
    mgr = _manager(fileorbit_dir)
    mgr.ask("What is FileOrbit?")
    _, trace = mgr.ask("What are its risks?", want_trace=True)
    assert trace is not None
    d = trace.to_dict()
    assert d["resolved"]["focus"]["title"] == "FileOrbit"
    assert d["query_trace"] is not None
    assert "CONVERSATION TRACE" in trace.render_text()
