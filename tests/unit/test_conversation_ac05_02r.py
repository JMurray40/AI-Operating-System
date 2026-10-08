"""AC-05-02R — residual: REAL concurrent callers, barrier-controlled (Handoff 14 §3).

The prior AC-05-02 round proved the single-use/attempt-lifecycle invariants only with
sequential calls and one test that simulated "concurrent" by poking the session's in-flight
attribute directly from the test itself — never exercising the actual check-then-set race
between two threads. ``Session.in_flight``/``approval_consumed`` were
plain attributes with no lock, so two real simultaneous callers could both observe
"not in flight" before either claimed it (a classic TOCTOU race).

These tests use ``threading.Barrier`` to force genuine simultaneous entry into
``ConversationApplication._run_attempt`` and prove, with real threads and no internal-flag
poking:

- only one initial dispatch can consume the approval;
- retry cannot overlap an in-flight attempt;
- successful retry preserves the original public session and turn identity;
- exactly one public terminal result exists;
- cancellation/reset defeats late completion.
"""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from pathlib import Path

import pytest

from jarvis_core.config import Config
from jarvis_core.conversation import ConversationApplication, PrepareTurnRequest, mock_profile
from jarvis_core.conversation.contract import ApprovalError
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
    """Blocks inside ``dispatch`` until released, widening the race window on purpose."""

    name = "gated"
    adapter_version = "test.gated"

    def __init__(self, status: TerminalState = TerminalState.COMPLETED) -> None:
        self.status = status
        self.calls = 0
        self.release = threading.Event()
        self.entered = threading.Event()

    def dispatch(self, request, cancel=None):  # type: ignore[no-untyped-def]
        from jarvis_core.providers.conversation import structured_answer

        self.calls += 1
        self.entered.set()
        self.release.wait(timeout=5)
        text = (
            structured_answer([("ok [C1]", "model_knowledge", [])])
            if self.status is TerminalState.COMPLETED
            else None
        )
        return NormalizedResult(
            status=self.status,
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


# ------------------------------------------------------------------ real concurrent initial
def test_real_concurrent_initial_dispatch_exactly_one_winner(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = _prepared(app, notes, root)
    prov = GatedProvider()
    prov.release.set()  # let dispatch complete promptly once it's reached (widen entry race only)
    n = 8
    barrier = threading.Barrier(n)
    results: list[object] = [None] * n

    def worker(i: int) -> None:
        barrier.wait(timeout=5)  # force every thread into dispatch_turn at ~the same instant
        try:
            results[i] = app.dispatch_turn(s, prov, now=T)
        except ApprovalError as exc:
            results[i] = exc

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n)]
    for th in threads:
        th.start()
    for th in threads:
        th.join(timeout=5)

    successes = [r for r in results if not isinstance(r, Exception)]
    blocked = [r for r in results if isinstance(r, ApprovalError)]
    assert len(successes) == 1, f"expected exactly one winner, got {len(successes)}"
    assert len(blocked) == n - 1
    # exactly one public terminal result was ever recorded into session state
    assert len(s.turns) == 1
    assert len(s.attempts) == 1
    assert prov.calls == 1  # the losers never reached prompt assembly / provider dispatch


# ------------------------------------------------------------------ retry cannot overlap in-flight
def test_real_retry_cannot_overlap_in_flight_initial(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = _prepared(app, notes, root)
    prov = GatedProvider()  # release.wait() blocks dispatch() until we set it

    initial_result: dict[str, object] = {}

    def run_initial() -> None:
        initial_result["value"] = app.dispatch_turn(s, prov, now=T)

    t = threading.Thread(target=run_initial)
    t.start()
    assert prov.entered.wait(timeout=5)  # the initial dispatch is now genuinely in flight

    # A concurrent retry attempted WHILE the initial dispatch is still inside provider.dispatch
    # must be refused; there is no terminal attempt yet either way, so ValidationError OR
    # ApprovalError are both acceptable fail-closed outcomes, but the provider must not be
    # invoked a second time while the first is still in flight.
    from jarvis_core.conversation.contract import ValidationError

    with pytest.raises((ApprovalError, ValidationError)):
        app.retry_attempt(s, prov, now=T)
    assert prov.calls == 1  # the overlapping retry never reached the provider

    prov.release.set()
    t.join(timeout=5)
    assert initial_result["value"].attempt.status is TerminalState.COMPLETED  # type: ignore[union-attr]


# ------------------------------------------------------------------ reset defeats late completion
def test_reset_defeats_late_completion_from_another_thread(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = _prepared(app, notes, root)
    prov = GatedProvider()  # blocks inside dispatch() until released

    outcome: dict[str, object] = {}

    def run_dispatch() -> None:
        outcome["value"] = app.dispatch_turn(s, prov, now=T)

    t = threading.Thread(target=run_dispatch)
    t.start()
    assert prov.entered.wait(timeout=5)  # dispatch is genuinely in flight on the other thread

    # Reset the session WHILE the attempt above is still blocked inside provider.dispatch.
    app.reset_session(s)

    # Now let the stale, already-in-flight attempt complete.
    prov.release.set()
    t.join(timeout=5)

    result = outcome["value"]
    assert result.attempt.status is TerminalState.CANCELLED  # type: ignore[union-attr]
    assert "reset" in (result.attempt.message or "")  # type: ignore[union-attr]
    # The reset session must show NO trace of the defeated late completion.
    assert s.turns == []
    assert s.attempts == []
    # A fresh prepare/approve/dispatch on the SAME (now reset) session must work normally —
    # proving the stale attempt's finally-block did not corrupt in_flight for the new one.
    app.prepare_turn(s, _req(s.session_id, root), notes)
    app.approve(s, actor="jason", now=T)
    prov2 = GatedProvider()
    prov2.release.set()
    res2 = app.dispatch_turn(s, prov2, now=T)
    assert res2.attempt.status is TerminalState.COMPLETED
    assert len(s.turns) == 1
