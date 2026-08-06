"""AC-05-02 — single-use approval, typed attempt lifecycle, byte-identical retry."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from jarvis_core.config import Config
from jarvis_core.conversation import ConversationApplication, PrepareTurnRequest, mock_profile
from jarvis_core.conversation.contract import ApprovalError, ValidationError
from jarvis_core.policy import local_allow_all
from jarvis_core.providers.conversation import (
    CancellationToken,
    NormalizedResult,
    ProviderContent,
    TerminalState,
)
from jarvis_core.repositories import FileSystemKnowledgeRepository

T = datetime(2026, 8, 1, tzinfo=timezone.utc)
_MSG = "summarize the AI Operating System project"


@pytest.fixture(scope="module")
def vault() -> tuple[list, Path]:
    repo = FileSystemKnowledgeRepository(Config())
    return repo.discover(), Path(repo.root)


def _req(sid: str, root: Path) -> PrepareTurnRequest:
    return PrepareTurnRequest(
        request_id="r1", session_id=sid, workspace_id="local",
        scope=local_allow_all(workspace_id="local", max_sensitivity="internal"),
        source_root=root, user_text=_MSG, provider_profile=mock_profile(), evaluation_time=T,
    )


class RecordingProvider:
    """Records every content-bearing request and returns a configurable terminal result."""

    name = "rec"
    adapter_version = "test.rec"

    def __init__(self, status: TerminalState = TerminalState.COMPLETED,
                 text: str = "ok [C1]") -> None:
        self.status = status
        self.text = text
        self.contents: list[ProviderContent] = []
        self.calls = 0

    def dispatch(self, request, cancel=None):  # type: ignore[no-untyped-def]
        from jarvis_core.providers.conversation import structured_answer
        self.calls += 1
        self.contents.append(request.content)
        text = (
            structured_answer([(self.text, "model_knowledge", [])])
            if self.status is TerminalState.COMPLETED
            else None
        )
        return NormalizedResult(
            status=self.status, provider_id=request.transport.provider_id,
            model_id=request.transport.model_id, adapter_version=self.adapter_version,
            text=text,
        )


def _prepared(app: ConversationApplication, notes: list, root: Path):  # type: ignore[no-untyped-def]
    s = app.create_session("local")
    app.prepare_turn(s, _req(s.session_id, root), notes)
    app.approve(s, actor="jason", now=T)
    return s


# ------------------------------------------------------------------ single-use
def test_second_initial_dispatch_is_replay_blocked(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = _prepared(app, notes, root)
    prov = RecordingProvider()
    app.dispatch_turn(s, prov, now=T)
    with pytest.raises(ApprovalError):
        app.dispatch_turn(s, prov, now=T)   # dispatch-after-terminal / replay


def test_concurrent_initial_dispatch_blocked(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = _prepared(app, notes, root)
    s.in_flight = True   # simulate an in-flight dispatch
    prov = RecordingProvider()
    with pytest.raises(ApprovalError):
        app.dispatch_turn(s, prov, now=T)
    assert prov.calls == 0   # never reached prompt assembly / provider


def test_ineligible_retry_without_attempt_does_not_call_provider(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = _prepared(app, notes, root)
    prov = RecordingProvider()
    with pytest.raises(ValidationError):
        app.retry_attempt(s, prov, now=T)   # no terminal attempt yet
    assert prov.calls == 0


# ------------------------------------------------------------------ eligible retry
def test_eligible_retry_new_attempt_byte_identical_content(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = _prepared(app, notes, root)
    prov = RecordingProvider(status=TerminalState.FAILED)
    first = app.dispatch_turn(s, prov, now=T)
    second = app.retry_attempt(s, prov, now=T)
    assert first.attempt.attempt_id != second.attempt.attempt_id
    assert first.snapshot_digest == second.snapshot_digest
    # byte-identical approved content bytes across the two attempts
    assert prov.contents[0] == prov.contents[1]


def test_retry_uses_bound_history_not_live_session(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = _prepared(app, notes, root)
    prov = RecordingProvider(status=TerminalState.COMPLETED)
    app.dispatch_turn(s, prov, now=T)     # completes and records a turn -> live history grows
    app.retry_attempt(s, prov, now=T)     # retry must still use the bound (empty) history
    assert prov.contents[0].user_text == prov.contents[1].user_text


# ------------------------------------------------------------------ cancellation
def test_provider_ignoring_cancellation_yields_cancelled(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = _prepared(app, notes, root)
    ignoring = RecordingProvider(status=TerminalState.COMPLETED, text="sneaky answer [C1]")
    token = CancellationToken()
    token.cancel()
    res = app.dispatch_turn(s, ignoring, now=T, cancel=token)
    assert res.attempt.status is TerminalState.CANCELLED   # forced, provider result overridden
    assert res.attempt.text is None
    assert s.turns == []   # no completed answer recorded


def test_attempt_limit_enforced(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = _prepared(app, notes, root)
    prov = RecordingProvider(status=TerminalState.FAILED)
    app.dispatch_turn(s, prov, now=T)
    for _ in range(4):
        app.retry_attempt(s, prov, now=T)   # 1 initial + 4 retries = 5 attempts (the cap)
    with pytest.raises(ValidationError):
        app.retry_attempt(s, prov, now=T)    # 6th is refused
