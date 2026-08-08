"""AC-05-05R — residual: immutable retained presentation + full redaction corpus (Handoff 14 §6).

Two gaps closed:

1. ``PresentationResult.claims``/``usage``/``cost`` were retained as plain mutable dicts, and
   ``to_dict()`` embedded ``self.usage``/``self.cost`` directly with NO copy at all. A caller
   mutating a dict obtained from one accessor (or from a prior ``to_dict()`` call) could
   silently corrupt the retained object and change what a LATER render of the SAME object
   returns. These are now deep-frozen at construction; ``to_dict()`` deep-thaws fresh,
   detached copies.
2. The shared redaction pipeline (``sanitize_markdown``) never addressed absolute-path,
   traceback/exception, or credential/secret-like disclosure — the existing hostile-corpus
   test didn't even assert on those three categories, even though the corpus embeds them.
   This file extends the corpus check across every public surface: the in-process API
   (``present()``), text, JSON, CLI-equivalent (``render.result_dict``/``result_text``),
   trace, and history.
"""
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
from jarvis_core.conversation.sanitize import sanitize_markdown
from jarvis_core.policy import local_allow_all
from jarvis_core.providers.conversation import MockConversationProvider
from jarvis_core.repositories import FileSystemKnowledgeRepository

T = datetime(2026, 8, 1, tzinfo=timezone.utc)

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


# ------------------------------------------------------------------ sanitizer unit coverage
def test_sanitize_redacts_windows_path() -> None:
    out = sanitize_markdown(r"see C:\Users\jmurr\secret\notes.txt for details")
    assert "C:\\Users\\jmurr" not in out
    assert "[redacted-path]" in out


def test_sanitize_redacts_posix_absolute_path() -> None:
    out = sanitize_markdown("config lives at /etc/jarvis/secrets.yaml on disk")
    assert "/etc/jarvis/secrets.yaml" not in out
    assert "[redacted-path]" in out


def test_sanitize_does_not_touch_relative_or_fractional_text() -> None:
    # A leading-slash-free relative mention and an ordinary fraction must survive untouched.
    out = sanitize_markdown("see docs/setup.md; roughly 3/4 of notes are tagged")
    assert "docs/setup.md" in out
    assert "3/4" in out


def test_sanitize_redacts_traceback_header() -> None:
    out = sanitize_markdown("Traceback (most recent call last):\n  oops")
    assert "Traceback (most recent call last)" not in out
    assert "[redacted-traceback]" in out


def test_sanitize_redacts_file_line_disclosure() -> None:
    out = sanitize_markdown('File "/opt/app/main.py", line 42, in run')
    assert 'line 42' not in out or "[redacted-file-line]" in out
    assert "[redacted-file-line]" in out


def test_sanitize_redacts_exception_marker() -> None:
    out = sanitize_markdown("ValueError: invalid literal for int()")
    assert "[redacted-error]" in out


def test_sanitize_redacts_secret_like_canary() -> None:
    out = sanitize_markdown("leaked API_KEY=sk-abc123 and SECRETVALUE in the log")
    assert "sk-abc123" not in out
    assert "SECRETVALUE" not in out
    assert "[redacted-credential]" in out


def test_sanitize_redacts_bearer_token() -> None:
    out = sanitize_markdown("Authorization: Bearer abcdef0123456789")
    assert "abcdef0123456789" not in out


# ------------------------------------------------------------------ full corpus, all surfaces
def test_hostile_corpus_absent_across_every_public_surface(completed) -> None:  # type: ignore[no-untyped-def]
    _app, s, turn = completed
    api_blob = str(present(turn).to_dict())
    text_blob = present(turn).to_text()
    json_blob = str(result_dict(turn))
    cli_text_blob = result_text(turn)
    trace_blob = str(s.trace.to_dict())
    history_blob = " ".join(rec.answer_text for rec in s.turns)

    forbidden = (
        "<script>",
        "http://evil.example/i.png",
        "javascript:alert",
        "\x07",
        "C:\\Users\\jmurr\\secret",
        "Traceback(most recent call last)",
        "Traceback (most recent call last)",
        "SECRETVALUE",
    )
    for surface_name, blob in (
        ("api", api_blob), ("text", text_blob), ("json", json_blob),
        ("cli_text", cli_text_blob), ("trace", trace_blob), ("history", history_blob),
    ):
        for marker in forbidden:
            assert marker not in blob, f"{marker!r} leaked into the {surface_name} surface"


# ------------------------------------------------------------------ immutability / alias mutation
def test_presentation_claims_are_frozen(completed) -> None:  # type: ignore[no-untyped-def]
    _app, _s, turn = completed
    pr = present(turn)
    assert pr.claims, "fixture expected at least one claim"
    with pytest.raises(TypeError):
        pr.claims[0]["text"] = "tampered"  # type: ignore[index]
    with pytest.raises(TypeError):
        pr.usage["input_tokens"] = 999999  # type: ignore[index]
    with pytest.raises(TypeError):
        pr.cost["amount_usd"] = 0.0  # type: ignore[index]


def test_mutating_to_dict_output_does_not_affect_a_later_render(completed) -> None:  # type: ignore[no-untyped-def]
    """The historical bug: ``to_dict()`` embedded ``self.usage``/``self.cost`` with NO copy,
    so mutating the first call's output silently corrupted every later render of the SAME
    PresentationResult."""
    _app, _s, turn = completed
    pr = present(turn)
    first = pr.to_dict()
    first["attempt"]["usage"]["input_tokens"] = -1  # type: ignore[index]
    first["attempt"]["cost"]["amount_usd"] = -999.0  # type: ignore[index]
    if first["attempt"]["claims"]:  # type: ignore[index]
        first["attempt"]["claims"][0]["text"] = "TAMPERED"  # type: ignore[index]

    second = pr.to_dict()  # a later render of the SAME object
    assert second["attempt"]["usage"]["input_tokens"] != -1  # type: ignore[index]
    assert second["attempt"]["cost"]["amount_usd"] != -999.0  # type: ignore[index]
    if second["attempt"]["claims"]:  # type: ignore[index]
        assert second["attempt"]["claims"][0]["text"] != "TAMPERED"  # type: ignore[index]
    # to_text() must also be unaffected by the mutated (detached) to_dict() output.
    assert "TAMPERED" not in pr.to_text()
    assert "-999.0" not in pr.to_text()
