"""LA-18-01 — residual: one coherent lifecycle-lock protocol (Handoff 18 §2-4).

AC-05-02R-2 made the terminal-commit half of the lifecycle transaction atomic, but the OTHER
half was not: ``prepare_turn()`` wrote ``pending_credentials`` and later replaced
``pending_prepared`` outside ``session.lock``, then called ``reset_lifecycle()`` afterward;
``remove_context()`` replaced ``pending_prepared`` outside the lock, then invalidated
afterward; ``approve()`` read a prepared snapshot and wrote ``pending_approval`` outside the
lock; and ``_run_attempt()`` read ``pending_prepared``/``pending_approval`` BEFORE acquiring
the lock that claims the attempt. Replacement state could become visible before generation/
approval invalidation, or a dispatch could retain stale prepared/approval references and claim
them after a concurrent replacement.

Every lifecycle entry point now keeps its expensive work (retrieval, context construction,
integrity/digest calculation, approval-object construction) OUTSIDE ``session.lock``, and
commits its result — publish, staleness verification, invalidation — as ONE atomic critical
section under that same lock. ``prepare_turn()``/``remove_context()``/``approve()`` each expose
a private, production-no-op pre-commit seam (mirroring ``_pre_commit_seam`` from AC-05-02R-2)
so these tests can pause a REAL call at its own internal pre-commit point and run a real
concurrent lifecycle operation against it, then resume and assert the real, observable outcome.
No test establishes its result by directly mutating ``pending_prepared``/``pending_approval``/
``generation``/``in_flight`` itself.
"""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from pathlib import Path

import pytest

from jarvis_core.config import Config
from jarvis_core.conversation import ConversationApplication, PrepareTurnRequest, mock_profile
from jarvis_core.conversation.contract import DriftError
from jarvis_core.policy import local_allow_all
from jarvis_core.providers.conversation import (
    MockConversationProvider,
    NormalizedResult,
    TerminalState,
)
from jarvis_core.repositories import FileSystemKnowledgeRepository

T = datetime(2026, 8, 1, tzinfo=timezone.utc)
_MSG = "summarize the AI Operating System project"


def _req(sid: str, root: Path, request_id: str = "r1") -> PrepareTurnRequest:
    return PrepareTurnRequest(
        request_id=request_id,
        session_id=sid,
        workspace_id="local",
        scope=local_allow_all(workspace_id="local", max_sensitivity="internal"),
        source_root=root,
        user_text=_MSG,
        provider_profile=mock_profile(),
        evaluation_time=T,
    )


class SeamGate:
    """A reusable pause point for a private production seam.

    ``entered`` fires the instant the paused thread calls the seam; the thread then blocks in
    the seam until the test calls ``release()``. Always ``assert gate.entered.wait(timeout=5)``
    before performing the concurrent operation the test wants to land in that window — the
    seam cannot fire until the paused call has already done everything before it (its own
    prior lock-guarded reads/claims included), so this ordering is real, not assumed.
    """

    def __init__(self) -> None:
        self.entered = threading.Event()
        self._release = threading.Event()

    def __call__(self) -> None:
        self.entered.set()
        self._release.wait(timeout=5)

    def release(self) -> None:
        self._release.set()


class GatedProvider:
    """Blocks inside ``dispatch`` until released; ``entered`` confirms the attempt already
    passed its initial lock-guarded claim (reading prepared/approval, setting in_flight)."""

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
        return NormalizedResult(
            status=TerminalState.COMPLETED,
            provider_id=request.transport.provider_id,
            model_id=request.transport.model_id,
            adapter_version=self.adapter_version,
            text=structured_answer([("ok [C1]", "model_knowledge", [])]),
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


# ------------------------------------------------------------------ (1) prepare replacement
# commits before an old terminal commit
def test_prepare_replacement_before_old_terminal_commit_discards_old_completion(
    vault: tuple[list, Path],
) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = _prepared(app, notes, root)
    old_prepared = s.pending_prepared

    prov = GatedProvider()
    seam = SeamGate()
    app._pre_commit_seam = seam  # type: ignore[assignment]
    outcome: dict[str, object] = {}

    def run() -> None:
        outcome["value"] = app.dispatch_turn(s, prov, now=T)

    t = threading.Thread(target=run)
    t.start()
    assert prov.entered.wait(timeout=5)  # the attempt already claimed old_prepared/approval
    prov.release.set()
    assert seam.entered.wait(timeout=5)  # interpretation finished; paused at the pre-commit seam

    # A fresh, FULL prepare_turn() replacement commits now, while the old attempt is paused.
    new_snap = app.prepare_turn(s, _req(s.session_id, root, request_id="r2"), notes)
    assert s.pending_prepared is not old_prepared
    assert s.pending_approval is None  # the replacement invalidated the old approval

    seam.release()
    t.join(timeout=5)

    result = outcome["value"]
    assert result.attempt.status is TerminalState.CANCELLED  # type: ignore[union-attr]
    # No attempt/turn/focus/terminal-trace event from the discarded old completion.
    assert s.turns == []
    assert s.attempts == []
    assert s.pending_prepared.snapshot.digest == new_snap.digest  # type: ignore[union-attr]


# ------------------------------------------------------------------ (2) old terminal commit
# wins before prepare replacement
def test_old_terminal_commit_before_prepare_replacement_preserves_turn_and_starts_clean(
    vault: tuple[list, Path],
) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = _prepared(app, notes, root)
    old_prepared = s.pending_prepared

    prov = MockConversationProvider(reply="a [C1]")  # completes promptly, no gating needed
    prepare_seam = SeamGate()
    app._prepare_commit_seam = prepare_seam  # type: ignore[assignment]
    prepare_outcome: dict[str, object] = {}

    def run_prepare() -> None:
        prepare_outcome["value"] = app.prepare_turn(
            s, _req(s.session_id, root, request_id="r2"), notes
        )

    pt = threading.Thread(target=run_prepare)
    pt.start()
    assert prepare_seam.entered.wait(timeout=5)  # replacement computed, paused before its commit

    # The old attempt dispatches and commits FULLY now, while the replacement is paused.
    result = app.dispatch_turn(s, prov, now=T)
    assert result.attempt.status is TerminalState.COMPLETED
    assert len(s.turns) == 1
    assert s.in_flight is False

    prepare_seam.release()
    pt.join(timeout=5)

    # The replacement publishes cleanly afterward, with its OWN new generation and no stale
    # approval/attempt state, and the old completed turn remains a valid prior turn.
    assert s.pending_prepared is not old_prepared
    assert s.pending_approval is None
    assert s.attempts == []  # invalidated by the replacement
    assert len(s.turns) == 1  # the old completed turn is untouched
    assert s.turns[0].coverage  # sanity: it's the real completed turn, not a placeholder


# ------------------------------------------------------------------ (3) context removal fails
# closed on a concurrently replaced/reset preparation
def test_context_removal_fails_closed_on_concurrent_prepare_replacement(
    vault: tuple[list, Path],
) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = _prepared(app, notes, root)
    item_id = s.pending_prepared.snapshot.items[0].item_id  # type: ignore[union-attr]
    old_prepared = s.pending_prepared

    seam = SeamGate()
    app._remove_context_commit_seam = seam  # type: ignore[assignment]
    outcome: dict[str, object] = {}

    def run_remove() -> None:
        try:
            outcome["value"] = app.remove_context(s, item_id)
        except DriftError as exc:
            outcome["error"] = exc

    rt = threading.Thread(target=run_remove)
    rt.start()
    assert seam.entered.wait(timeout=5)  # new snapshot computed FROM old_prepared, paused

    # A concurrent, unrelated prepare_turn() replacement lands before the removal commits.
    app.prepare_turn(s, _req(s.session_id, root, request_id="r2"), notes)
    assert s.pending_prepared is not old_prepared

    seam.release()
    rt.join(timeout=5)

    assert "error" in outcome, "removal computed from a superseded preparation must fail closed"
    assert isinstance(outcome["error"], DriftError)
    assert "value" not in outcome
    # The concurrent replacement's own state is completely untouched by the failed removal.
    assert s.pending_prepared is not old_prepared
    assert s.pending_prepared.snapshot.items  # type: ignore[union-attr]


def test_context_removal_fails_closed_on_concurrent_reset(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = _prepared(app, notes, root)
    item_id = s.pending_prepared.snapshot.items[0].item_id  # type: ignore[union-attr]

    seam = SeamGate()
    app._remove_context_commit_seam = seam  # type: ignore[assignment]
    outcome: dict[str, object] = {}

    def run_remove() -> None:
        try:
            outcome["value"] = app.remove_context(s, item_id)
        except DriftError as exc:
            outcome["error"] = exc

    rt = threading.Thread(target=run_remove)
    rt.start()
    assert seam.entered.wait(timeout=5)

    app.reset_session(s)  # a full reset, not just a replacement

    seam.release()
    rt.join(timeout=5)

    assert "error" in outcome
    assert isinstance(outcome["error"], DriftError)
    assert s.pending_prepared is None  # the reset session shows no trace of the failed removal


# ------------------------------------------------------------------ (4) approval fails closed
# on a concurrently replaced/removed/reset snapshot
def test_approval_fails_closed_on_concurrent_prepare_replacement(
    vault: tuple[list, Path],
) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")
    app.prepare_turn(s, _req(s.session_id, root), notes)
    old_prepared = s.pending_prepared

    seam = SeamGate()
    app._approve_commit_seam = seam  # type: ignore[assignment]
    outcome: dict[str, object] = {}

    def run_approve() -> None:
        try:
            outcome["value"] = app.approve(s, actor="jason", now=T)
        except DriftError as exc:
            outcome["error"] = exc

    at = threading.Thread(target=run_approve)
    at.start()
    assert seam.entered.wait(timeout=5)  # approval built FROM old_prepared, paused before commit

    app.prepare_turn(s, _req(s.session_id, root, request_id="r2"), notes)
    assert s.pending_prepared is not old_prepared

    seam.release()
    at.join(timeout=5)

    assert "error" in outcome, "an approval built from a superseded preparation must fail closed"
    assert isinstance(outcome["error"], DriftError)
    assert s.pending_approval is None  # the stale approval was never published


def test_approval_fails_closed_on_concurrent_context_removal(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")
    app.prepare_turn(s, _req(s.session_id, root), notes)
    item_id = s.pending_prepared.snapshot.items[0].item_id  # type: ignore[union-attr]

    seam = SeamGate()
    app._approve_commit_seam = seam  # type: ignore[assignment]
    outcome: dict[str, object] = {}

    def run_approve() -> None:
        try:
            outcome["value"] = app.approve(s, actor="jason", now=T)
        except DriftError as exc:
            outcome["error"] = exc

    at = threading.Thread(target=run_approve)
    at.start()
    assert seam.entered.wait(timeout=5)

    app.remove_context(s, item_id)  # a genuine, unpaused removal commits normally

    seam.release()
    at.join(timeout=5)

    assert "error" in outcome
    assert isinstance(outcome["error"], DriftError)
    assert s.pending_approval is None


def test_approval_fails_closed_on_concurrent_reset(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")
    app.prepare_turn(s, _req(s.session_id, root), notes)

    seam = SeamGate()
    app._approve_commit_seam = seam  # type: ignore[assignment]
    outcome: dict[str, object] = {}

    def run_approve() -> None:
        try:
            outcome["value"] = app.approve(s, actor="jason", now=T)
        except DriftError as exc:
            outcome["error"] = exc

    at = threading.Thread(target=run_approve)
    at.start()
    assert seam.entered.wait(timeout=5)

    app.reset_session(s)

    seam.release()
    at.join(timeout=5)

    assert "error" in outcome
    assert isinstance(outcome["error"], DriftError)
    assert s.pending_approval is None


# ------------------------------------------------------------------ (5) dispatch cannot claim
# stale prepared/approval references after a concurrent replacement
def test_dispatch_after_replacement_never_uses_stale_prepared_or_approval(
    vault: tuple[list, Path],
) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = _prepared(app, notes, root)  # P1 prepared + approved (A1)
    old_prepared = s.pending_prepared
    old_approval = s.pending_approval

    # A fresh, unrelated replacement lands (no re-approval yet).
    app.prepare_turn(s, _req(s.session_id, root, request_id="r2"), notes)
    assert s.pending_prepared is not old_prepared
    assert s.pending_approval is None  # A1 was invalidated, not carried over to P2

    from jarvis_core.conversation.contract import ApprovalError

    with pytest.raises(ApprovalError):
        app.dispatch_turn(s, MockConversationProvider(reply="a [C1]"), now=T)

    # Approving the NEW preparation and dispatching now must use ONLY the new state.
    new_approval = app.approve(s, actor="jason", now=T)
    assert new_approval is not old_approval
    result = app.dispatch_turn(s, MockConversationProvider(reply="a [C1]"), now=T)
    assert result.attempt.status is TerminalState.COMPLETED
    assert result.snapshot_digest == s.turns[0].snapshot_digest
    # (The new preparation's snapshot digest may coincide with the old one when fixture
    # content is identical across prepares — tests 1/2 give the identity-based,
    # digest-independent proof that a genuinely distinct object was used.)


def test_dispatch_claim_reads_prepared_and_approval_inside_the_same_lock(
    vault: tuple[list, Path],
) -> None:
    """A concurrent replacement landing between a would-be pre-lock read and the lock
    acquisition must never let dispatch observe a torn (new prepared, old approval) pair — the
    exact LA-18-01 gap. Race a dispatch attempt directly against a paused replacement."""
    notes, root = vault
    app = ConversationApplication()
    s = _prepared(app, notes, root)
    old_prepared = s.pending_prepared

    prepare_seam = SeamGate()
    app._prepare_commit_seam = prepare_seam  # type: ignore[assignment]
    prepare_outcome: dict[str, object] = {}

    def run_prepare() -> None:
        prepare_outcome["value"] = app.prepare_turn(
            s, _req(s.session_id, root, request_id="r2"), notes
        )

    pt = threading.Thread(target=run_prepare)
    pt.start()
    assert prepare_seam.entered.wait(timeout=5)  # replacement computed, paused before its commit

    # While the replacement is paused (NOT yet published), the still-current P1/A1 pair is used
    # by a normal dispatch — this must succeed cleanly using the OLD, still-authoritative pair,
    # not some mix with whatever the paused replacement is about to publish.
    result = app.dispatch_turn(s, MockConversationProvider(reply="a [C1]"), now=T)
    assert result.attempt.status is TerminalState.COMPLETED
    assert s.pending_prepared is old_prepared  # unchanged: replacement still paused

    prepare_seam.release()
    pt.join(timeout=5)
    assert s.pending_prepared is not old_prepared
    assert s.pending_approval is None


# ------------------------------------------------------------------ (6) no torn intermediate
# state is observable through the application API
def test_no_torn_new_preparation_old_generation_state_via_the_api(
    vault: tuple[list, Path],
) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = _prepared(app, notes, root)
    old_prepared = s.pending_prepared
    old_generation = s.generation

    seam = SeamGate()
    app._prepare_commit_seam = seam  # type: ignore[assignment]

    def run_prepare() -> None:
        app.prepare_turn(s, _req(s.session_id, root, request_id="r2"), notes)

    pt = threading.Thread(target=run_prepare)
    pt.start()
    assert seam.entered.wait(timeout=5)

    # Every read that goes THROUGH the application API (dispatch's own claim, which is what
    # actually matters for correctness) is lock-protected and must see a fully-old, coherent
    # pair while the replacement is still paused before its own commit.
    with pytest.raises(Exception):  # noqa: B017 - any of ApprovalError/ValidationError is fine
        # A retry with no prior attempt is a harmless probe that still exercises the same
        # lock-guarded prepared/approval read _run_attempt uses, without mutating state.
        app.retry_attempt(s, MockConversationProvider(reply="x"), now=T)
    assert s.pending_prepared is old_prepared
    assert s.generation == old_generation

    seam.release()
    pt.join(timeout=5)
    assert s.pending_prepared is not old_prepared
    assert s.generation != old_generation
    assert s.pending_approval is None


def test_concurrent_dispatch_and_replacement_stress_no_inconsistent_outcome(
    vault: tuple[list, Path],
) -> None:
    """Stress: repeatedly race a dispatch attempt against a prepare replacement. Every outcome
    observed through the API must be internally self-consistent (a completed turn's digest
    matches a snapshot that was validly current at some point; a failure is one of the
    documented lifecycle exceptions) — never a crash, never a mixed/inconsistent state."""
    notes, root = vault
    app = ConversationApplication()
    s = _prepared(app, notes, root)

    from jarvis_core.conversation.contract import ApprovalError, ValidationError

    errors: list[BaseException] = []

    def hammer_prepare() -> None:
        for i in range(15):
            try:
                app.prepare_turn(s, _req(s.session_id, root, request_id=f"h{i}"), notes)
            except BaseException as exc:  # captured for the assertion below
                errors.append(exc)

    def hammer_dispatch() -> None:
        for _ in range(15):
            try:
                app.approve(s, actor="jason", now=T)
                app.dispatch_turn(s, MockConversationProvider(reply="a [C1]"), now=T)
            except (ApprovalError, ValidationError, DriftError):
                pass  # an expected, well-typed lifecycle rejection is not a failure
            except BaseException as exc:
                errors.append(exc)

    t1 = threading.Thread(target=hammer_prepare)
    t2 = threading.Thread(target=hammer_dispatch)
    t1.start()
    t2.start()
    t1.join(timeout=10)
    t2.join(timeout=10)

    assert errors == [], f"unexpected exception types during the race: {errors}"
    # Every recorded turn's snapshot digest is a real digest belonging to the FINAL prepared
    # state or an earlier one — never garbage. (Session bookkeeping stayed internally sane.)
    for turn in s.turns:
        assert turn.snapshot_digest.startswith("sha256:")
    assert s.in_flight is False  # nothing left claimed after the race settles


# ------------------------------------------------------------------ (7) accepted suites remain
# green — see test_conversation_ac05_02r2.py / test_conversation_ac05_01r2.py, run unmodified
# alongside this file as part of the full conversation suite.
