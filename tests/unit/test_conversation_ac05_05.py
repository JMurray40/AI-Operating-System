"""AC-05-05 — one immutable sanitized presentation object; API/text/JSON/CLI parity."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from jarvis_core.config import Config
from jarvis_core.conversation import (
    ConversationApplication,
    PrepareTurnRequest,
    mock_profile,
    present,
)
from jarvis_core.conversation.render import result_dict, result_text
from jarvis_core.policy import local_allow_all
from jarvis_core.providers.conversation import MockConversationProvider
from jarvis_core.repositories import FileSystemKnowledgeRepository

T = datetime(2026, 8, 1, tzinfo=timezone.utc)

# Hostile corpus embedded in a claim: HTML/script, remote image, markdown/javascript links,
# an autolink, a control character, a path, a raw-error-looking token, and a secret marker.
HOSTILE = (
    "<script>steal()</script> ![img](http://evil.example/i.png) "
    "[click](javascript:alert(1)) <http://evil.example/x> \x07bell "
    "C:\\Users\\jmurr\\secret Traceback(most recent call last) SECRETVALUE"
)


@pytest.fixture()
def completed():  # type: ignore[no-untyped-def]
    repo = FileSystemKnowledgeRepository(Config())
    notes = repo.discover()
    app = ConversationApplication()
    s = app.create_session("local")
    req = PrepareTurnRequest(
        request_id="r", session_id=s.session_id, workspace_id="local",
        scope=local_allow_all(workspace_id="local", max_sensitivity="internal"),
        source_root=Path(repo.root), user_text="summarize the AI Operating System project",
        provider_profile=mock_profile(), evaluation_time=T, want_trace=True,
    )
    app.prepare_turn(s, req, notes)
    app.approve(s, actor="jason", now=T)
    turn = app.dispatch_turn(
        s, MockConversationProvider(claims=[(HOSTILE, "model_knowledge", [])]), now=T
    )
    return app, s, turn


def test_text_json_are_the_same_presentation_object(completed) -> None:  # type: ignore[no-untyped-def]
    _app, _s, turn = completed
    assert result_dict(turn) == present(turn).to_dict()   # JSON renderer == presentation
    assert result_text(turn) == present(turn).to_text()   # text renderer == presentation


def test_all_public_surfaces_are_sanitized(completed) -> None:  # type: ignore[no-untyped-def]
    _app, _s, turn = completed
    surfaces = str(present(turn).to_dict()) + present(turn).to_text() + str(result_dict(turn))
    for active in ("<script>", "http://evil.example/i.png", "javascript:", "\x07"):
        assert active not in surfaces


def test_text_and_json_are_semantically_equal(completed) -> None:  # type: ignore[no-untyped-def]
    _app, _s, turn = completed
    d = present(turn).to_dict()
    txt = present(turn).to_text()
    assert str(d["attempt"]["status"]) in txt           # type: ignore[index]
    assert str(d["coverage"]) in txt
    answer = d["attempt"]["answer"]                       # type: ignore[index]
    assert isinstance(answer, str) and answer in txt


def test_raw_provider_payload_absent_from_trace_and_history(completed) -> None:  # type: ignore[no-untyped-def]
    _app, s, _turn = completed
    trace_blob = str(s.trace.to_dict())
    assert "<script>" not in trace_blob and "SECRETVALUE" not in trace_blob
    # session history stores only the sanitized answer, never raw active content
    for rec in s.turns:
        assert "<script>" not in rec.answer_text
        assert "javascript:" not in rec.answer_text
