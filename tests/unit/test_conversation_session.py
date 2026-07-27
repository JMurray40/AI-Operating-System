from __future__ import annotations

from jarvis_core.conversation.entities import MentionedEntity
from jarvis_core.conversation.session import ConversationSession


def _e(title: str, relpath: str) -> MentionedEntity:
    return MentionedEntity(relpath=relpath, title=title, id=None, turn=0)


def test_focus_is_top_ranked_entity():
    s = ConversationSession()
    # entities passed top-ranked first; focus must be the first, not the last
    s.record("q", "q", "a", [_e("FileOrbit", "p/FileOrbit.md"), _e("Repo", "r/Repo.md")])
    assert s.focus() is not None and s.focus().title == "FileOrbit"


def test_recent_entity_moves_to_front():
    s = ConversationSession()
    s.record("q1", "q1", "a1", [_e("A", "A.md")])
    s.record("q2", "q2", "a2", [_e("B", "B.md")])
    assert [e.title for e in s.entity_stack][:2] == ["B", "A"]


def test_reset_clears_state():
    s = ConversationSession()
    s.record("q", "q", "a", [_e("A", "A.md")])
    s.reset()
    assert s.turn_count == 0
    assert s.entity_stack == []


def test_history_budget_returns_trailing_turns():
    s = ConversationSession(history_token_budget=6)
    for i in range(5):
        s.record(f"question {i}", "q", "short answer here", [])
    recent = s.recent_history()
    assert 0 < len(recent) <= 5
    assert recent[-1].user_input == "question 4"
