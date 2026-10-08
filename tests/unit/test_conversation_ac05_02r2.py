"""AC-05-02R-2 — residual: atomic terminal lifecycle commit (Handoff 17 §3).

The AC-05-02R round made the check-then-set at the START of an attempt (in_flight /
approval_consumed / attempts) one atomic critical section, and defeated a late completion by
comparing a captured ``generation`` against the session's current one. But that staleness
check ran BEFORE response interpretation, and every terminal write after it — appending the
attempt, recording the turn, updating focus, recording the terminal trace event, clearing
in_flight — happened as a sequence of UNLOCKED mutations with no re-check. A lifecycle
invalidation (reset / a fresh prepare / context removal / an equivalent session-clearing path)
racing with interpretation itself, or landing in the unlocked window between interpretation
finishing and those terminal writes, was not defeated at all: it could interleave with, or be
overwritten by, this stale attempt's writes.

These tests use ``ConversationApplication._pre_commit_seam`` — a private hook invoked in
production only as a no-op, immediately after interpretation and immediately before the one
atomic terminal-commit lock acquisition — as a real internal pre-commit barrier. To land the
invalidation in exactly that window (and not, by scheduling luck, before the attempt has even
claimed ``in_flight``), each test first gates the attempt inside ``provider.dispatch()``
(proving, via ``prov.entered``, that the attempt already passed _run_attempt's initial
lock-guarded claim) before releasing it to run interpretation and pause at the seam. No test
establishes its result by directly setting ``session.in_flight``/``generation``/
``active_attempt_id``; every case drives the real ``ConversationApplication`` API on a real
second thread and asserts on its real, observable outcome.
"""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from pathlib import Path

import pytest

from jarvis_core.config import Config
from jarvis_core.conversation import ConversationApplication, PrepareTurnRequest, mock_profile
from jarvis_core.policy import local_allow_all
from jarvis_core.providers.conversation import NormalizedResult, TerminalState
from jarvis_core.repositories import FileSystemKnowledgeRepository

T = datetime(2026, 8, 1, tzinfo=timezone.utc)
_MSG = "summarize the AI Operating System project"


def _req(sid: str, root: Path) -> PrepareTurnRequest:
    return PrepareTurnRequest(
        request_id="r1",
        session_id=sid,
        workspace_id="local",
        scope=local_allow_all(workspace_id="local", max_sensitivity="internal"),
        source_root=root,
        user_text=_MSG,
        provider_profile=mock_profile(),
        evaluation_time=T,
    )


class GatedProvider:
    """Blocks inside ``dispatch`` until released, so a test can confirm (via ``entered``)
    that the attempt already passed its initial in-flight claim before proceeding."""

    name = "gated"
    adapter_version = "test.gated"

    def __init__(self) -> None:
        self.calls = 0
        self.release = threading.Event()
        self.entered = threading.Event()

    def dispatch(self, request, cancel=None):  # type: ignore[no-untyped-def]
        from jarvis_core.providers.conversation import structured_answer

        self.calls += 1
        self.entered.set()
        self.release.wait(timeout=5)
        text = structured_answer([("ok [C1]", "model_knowledge", [])])
        return NormalizedResult(
            status=TerminalState.COMPLETED,
            provider_id=request.transport.provider_id,
            model_id=request.transport.model_id,
            adapter_version=self.adapter_version,
            text=text,
        )


def _prepared(app: ConversationApplication, notes: list, root: Path):  # type: ignore[no-untyped-def]
    s = app.create_session("local")
    app.prepare_turn(s, _req(s.session_id, root), notes)
    app.approve(s, actor="jason", now=T)
    return s


@pytest.fixture(scope="module")
def vault() -> tuple[list, Path]:
    repo = FileSystemKnowledgeRepository(Config())
    return repo.discover(), Path(repo.root)


def _run_paused_at_seam(
    app: ConversationApplication, session, outcome: dict[str, object]
) -> tuple[threading.Thread, threading.Barrier, GatedProvider]:
    """Start a real dispatch on another thread, and pause it exactly at the internal
    pre-commit seam — i.e. AFTER it has already claimed in_flight/generation/active_attempt_id
    (proven via the gated provider's ``entered`` signal) AND after interpretation has run.

    Returns the started thread, the barrier the caller must invalidate against and then
    release with ``barrier.wait(timeout=5)``, and the gated provider (already released).
    """
    prov = GatedProvider()
    barrier = threading.Barrier(2)
    app._pre_commit_seam = barrier.wait  # type: ignore[assignment]

    def run() -> None:
        outcome["value"] = app.dispatch_turn(session, prov, now=T)

    t = threading.Thread(target=run)
    t.start()
    # The attempt cannot reach provider.dispatch() until AFTER _run_attempt's initial
    # lock-guarded section has already claimed in_flight/active_attempt_id and captured
    # generation — so this confirms the invalidation the caller is about to perform will land
    # strictly after that claim, not race it away entirely.
    assert prov.entered.wait(timeout=5)
    prov.release.set()  # let dispatch() return promptly; interpretation runs next, then the seam
    return t, barrier, prov


# ------------------------------------------------------------------ reset at the exact seam
def test_reset_after_interpretation_but_before_commit_defeats_late_completion(
    vault: tuple[list, Path],
) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = _prepared(app, notes, root)
    outcome: dict[str, object] = {}

    t, barrier, _prov = _run_paused_at_seam(app, s, outcome)
    # The dispatch thread cannot reach the barrier until interpretation has already run (the
    # seam is called only after _interpret() returns), and it already claimed in_flight before
    # this point (confirmed above); it cannot proceed past the barrier until this thread also
    # arrives, so invalidating here — before this thread's own barrier.wait() — happens-before
    # the dispatch thread's terminal-commit block, no matter which thread physically arrives at
    # the barrier first.
    app.reset_session(s)
    barrier.wait(timeout=5)
    t.join(timeout=5)

    result = outcome["value"]
    assert result.attempt.status is TerminalState.CANCELLED  # type: ignore[union-attr]
    assert "reset" in (result.attempt.message or "")  # type: ignore[union-attr]
    # No attempt, turn, focus, or trace-completion event was written from the discarded
    # interpretation — the reset session shows no trace of it at all.
    assert s.turns == []
    assert s.attempts == []
    assert s.in_flight is False


def test_fresh_dispatch_after_seam_reset_proceeds_normally(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = _prepared(app, notes, root)
    outcome: dict[str, object] = {}

    t, barrier, _prov = _run_paused_at_seam(app, s, outcome)
    app.reset_session(s)
    barrier.wait(timeout=5)
    t.join(timeout=5)

    # A fresh prepare/approve/dispatch on the SAME (now reset) session must work exactly as if
    # the stale attempt had never run — proving its discarded terminal-commit block did not
    # leave in_flight/active_attempt_id/generation corrupted for the new attempt.
    app._pre_commit_seam = lambda: None  # type: ignore[assignment]
    app.prepare_turn(s, _req(s.session_id, root), notes)
    app.approve(s, actor="jason", now=T)
    from jarvis_core.providers.conversation import MockConversationProvider

    prov2 = MockConversationProvider(reply="a [C1]")
    res2 = app.dispatch_turn(s, prov2, now=T)
    assert res2.attempt.status is TerminalState.COMPLETED
    assert len(s.turns) == 1
    assert len(s.attempts) == 1


# ------------------------------------------------------------------ prepare-replacement at the
# exact seam
def test_prepare_replacement_after_interpretation_but_before_commit_defeats_late_completion(
    vault: tuple[list, Path],
) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = _prepared(app, notes, root)
    outcome: dict[str, object] = {}

    t, barrier, _prov = _run_paused_at_seam(app, s, outcome)
    # A fresh prepare_turn() is an "invalidation" path: it bumps generation and clears
    # in_flight/active_attempt_id/approval via Session.reset_lifecycle(), exactly like reset.
    app.prepare_turn(s, _req(s.session_id, root), notes)
    barrier.wait(timeout=5)
    t.join(timeout=5)

    result = outcome["value"]
    assert result.attempt.status is TerminalState.CANCELLED  # type: ignore[union-attr]
    # The replacement's own prepared snapshot is intact; nothing from the discarded attempt
    # was written into the session's turns/attempts.
    assert s.turns == []
    assert s.attempts == []


# ------------------------------------------------------------------ context removal at the
# exact seam
def test_context_removal_after_interpretation_but_before_commit_defeats_late_completion(
    vault: tuple[list, Path],
) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = _prepared(app, notes, root)
    outcome: dict[str, object] = {}
    item_id = s.pending_prepared.snapshot.items[0].item_id  # type: ignore[union-attr]

    t, barrier, _prov = _run_paused_at_seam(app, s, outcome)
    app.remove_context(s, item_id)
    barrier.wait(timeout=5)
    t.join(timeout=5)

    result = outcome["value"]
    assert result.attempt.status is TerminalState.CANCELLED  # type: ignore[union-attr]
    assert s.turns == []
    assert s.attempts == []


# ------------------------------------------------------------------ approval invalidation
# (the generic session-clearing path) at the exact seam
def test_approval_invalidation_after_interpretation_but_before_commit_defeats_late_completion(
    vault: tuple[list, Path],
) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = _prepared(app, notes, root)
    outcome: dict[str, object] = {}

    t, barrier, _prov = _run_paused_at_seam(app, s, outcome)
    # reset_lifecycle() is the equivalent generic session-clearing path every named
    # invalidation (reset/prepare replacement/context removal) already funnels through; it
    # invalidates the approval directly (pending_approval=None, approval_consumed=False).
    s.reset_lifecycle()
    barrier.wait(timeout=5)
    t.join(timeout=5)

    result = outcome["value"]
    assert result.attempt.status is TerminalState.CANCELLED  # type: ignore[union-attr]
    assert s.turns == []
    assert s.attempts == []
    assert s.pending_approval is None


# ------------------------------------------------------------------ no in_flight/focus/trace
# leakage from a discarded late completion
def test_discarded_late_completion_leaves_no_stale_in_flight_or_focus(
    vault: tuple[list, Path],
) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = _prepared(app, notes, root)
    outcome: dict[str, object] = {}
    focus_before = s.focus_titles

    t, barrier, _prov = _run_paused_at_seam(app, s, outcome)
    app.reset_session(s)
    barrier.wait(timeout=5)
    t.join(timeout=5)

    assert s.in_flight is False
    assert s.focus_titles == focus_before or s.focus_titles == ()
    # No terminal trace event for the discarded attempt id was appended.
    attempt_id = outcome["value"].attempt.attempt_id  # type: ignore[union-attr]
    trace_dict = s.trace.to_dict()  # type: ignore[union-attr]
    events = trace_dict.get("events", [])
    assert isinstance(events, list)
    completed_events = [
        e
        for e in events
        if isinstance(e, dict)
        and e.get("event") in ("dispatch_completed", "attempt_failed")
        and e.get("attempt_id") == attempt_id
    ]
    assert completed_events == []
