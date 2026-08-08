"""LA-18-02 — the lifecycle transaction's remaining gaps (Handoff 20 / Handoff 11 §20).

LA-18-01 made prepared/approval publication, attempt admission, terminal commit, and reset
mutations individually atomic, but three narrower gaps in the complete semantic lifecycle
remained:

20.1 — ``_run_attempt()`` captured prepared/approval/generation/attempt-identity under
``session.lock`` but did NOT capture the matching ``pending_credentials``; ``_recheck_credential``
and ``_credential`` re-read ``session.pending_credentials`` later, outside the lock, so a
concurrent ``prepare_turn()`` could replace the credential provider after admission but before
credential use. Fix: capture ``pending_credentials`` in the SAME admission lock acquisition and
thread that exact reference through the rest of the attempt; never reread session state.

20.2 — ``prepare_turn()`` read ``focus_titles``/``history_text()`` outside the lock and published
unconditionally; a terminal commit landing between capture and publish does not bump
``generation`` (only reset/removal/a fresh prepare do) but DOES advance bound history, so a
paused preparation could publish a snapshot bound to now-stale history. Fix: capture generation
AND the exact immutable history/focus inputs under the lock before building, and require them to
remain current at publish time; a mismatch fails closed with ``DriftError``.

20.3 — the ``snapshot_created``/``context_removed``/``approval_created`` trace events were
recorded AFTER their state commit, outside the lock; ``session.reset()`` replaces
``session.trace`` with a brand-new ``Trace`` object, so a stale operation's trace write landing
after a concurrent reset would append to the RESET session's new trace. Fix: record each event
under the SAME lock acquisition as its state commit (no gap for a reset to land in between).

Every test below drives the real public API with real threads and the existing private
pre-commit/post-admission seams (production no-ops); none establishes its result by directly
mutating session-internal fields.
"""

from __future__ import annotations

import threading
from datetime import datetime, timezone
from pathlib import Path

import pytest

from jarvis_core.config import Config
from jarvis_core.conversation import (
    Budgets,
    ConversationApplication,
    PrepareTurnRequest,
    mock_profile,
)
from jarvis_core.conversation.contract import DriftError
from jarvis_core.policy import local_allow_all
from jarvis_core.providers.conversation import (
    MockConversationProvider,
    NormalizedResult,
    TerminalState,
    structured_answer,
)
from jarvis_core.providers.credentials import StaticCredentialProvider
from jarvis_core.providers.google_gemini import APPROVED_MAX_OUTPUT_TOKENS, google_gemini_profile
from jarvis_core.repositories import FileSystemKnowledgeRepository

T = datetime(2026, 8, 1, tzinfo=timezone.utc)
_MSG = "summarize the AI Operating System project"
_OLD_CANARY = "OLD-CANARY-do-not-log-1a1a"
_NEW_CANARY = "NEW-CANARY-do-not-log-2b2b"

_GOOGLE_BUDGETS = Budgets(
    context_tokens=3000, prompt_tokens=20000, output_reserve_tokens=APPROVED_MAX_OUTPUT_TOKENS
)


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


def _remote_req(sid: str, root: Path, request_id: str = "r1") -> PrepareTurnRequest:
    return PrepareTurnRequest(
        request_id=request_id,
        session_id=sid,
        workspace_id="local",
        scope=local_allow_all(workspace_id="local", max_sensitivity="internal"),
        source_root=root,
        user_text=_MSG,
        provider_profile=google_gemini_profile(),
        budgets=_GOOGLE_BUDGETS,
        evaluation_time=T,
    )


class SeamGate:
    """A reusable pause point for a private production seam (see test_conversation_la18_01.py
    for the full rationale: ``entered`` confirms the paused thread already did everything
    before the seam, so the concurrent operation the test performs lands in a real, confirmed
    window rather than an assumed one)."""

    def __init__(self) -> None:
        self.entered = threading.Event()
        self._release = threading.Event()

    def __call__(self) -> None:
        self.entered.set()
        self._release.wait(timeout=5)

    def release(self) -> None:
        self._release.set()


class CapturingProvider:
    """A non-blocking ``ConversationProvider`` that records every request it receives.

    Used for LA-18-02A: the pause point this file races against is ``_post_admission_seam``,
    which fires BEFORE dispatch is ever reached, so the provider itself does not need to block
    — it only needs to capture the exact ``ProviderRequest`` (and therefore the exact
    ``Credential``) it was handed.
    """

    name = "capturing"
    adapter_version = "test.capturing"

    def __init__(self) -> None:
        self.requests: list[object] = []

    def dispatch(self, request, cancel=None):  # type: ignore[no-untyped-def]
        self.requests.append(request)
        return NormalizedResult(
            status=TerminalState.COMPLETED,
            provider_id=request.transport.provider_id,
            model_id=request.transport.model_id,
            adapter_version=self.adapter_version,
            text=structured_answer([("ok [C1]", "model_knowledge", [])]),
        )


@pytest.fixture(scope="module")
def vault() -> tuple[list, Path]:
    repo = FileSystemKnowledgeRepository(Config())
    return repo.discover(), Path(repo.root)


# ================================================================ 20.1 credential binding
def test_admitted_attempt_uses_captured_credential_not_a_concurrent_replacement(
    vault: tuple[list, Path],
) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")
    old_cred = StaticCredentialProvider(_OLD_CANARY)
    app.prepare_turn(s, _remote_req(s.session_id, root), notes, credentials=old_cred)
    app.approve(s, actor="jason", now=T)

    prov = CapturingProvider()
    seam = SeamGate()
    app._post_admission_seam = seam  # type: ignore[assignment]
    outcome: dict[str, object] = {}

    def run() -> None:
        outcome["value"] = app.dispatch_turn(s, prov, now=T)

    t = threading.Thread(target=run)
    t.start()
    # Admitted: prepared/approval/credentials captured and in_flight claimed, all under one
    # lock acquisition — but paused BEFORE any credential recheck or materialization.
    assert seam.entered.wait(timeout=5)

    # A concurrent, unrelated prepare_turn() replaces BOTH the preparation and the credential
    # provider while the admitted attempt is paused.
    new_cred = StaticCredentialProvider(_NEW_CANARY)
    app.prepare_turn(
        s, _remote_req(s.session_id, root, request_id="r2"), notes, credentials=new_cred
    )
    assert s.pending_credentials is new_cred

    seam.release()
    t.join(timeout=5)

    # The admitted attempt dispatched using its OWN captured (old) credential — it never
    # reread the now-replaced session.pending_credentials.
    assert len(prov.requests) == 1
    credential = prov.requests[0].credential  # type: ignore[attr-defined]
    assert credential is not None
    assert credential.reveal() == _OLD_CANARY

    # Per LA-18-01 (unregressed): the completion is still discarded because the replacement
    # also bumped generation.
    result = outcome["value"]
    assert result.attempt.status is TerminalState.CANCELLED  # type: ignore[union-attr]
    assert s.turns == []


def test_admitted_attempt_credential_unaffected_by_concurrent_reset(
    vault: tuple[list, Path],
) -> None:
    """A concurrent reset (not just a replacement) must not change which credential an already
    -admitted attempt uses, even though the reset clears session.pending_credentials entirely."""
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")
    old_cred = StaticCredentialProvider(_OLD_CANARY)
    app.prepare_turn(s, _remote_req(s.session_id, root), notes, credentials=old_cred)
    app.approve(s, actor="jason", now=T)

    prov = CapturingProvider()
    seam = SeamGate()
    app._post_admission_seam = seam  # type: ignore[assignment]
    outcome: dict[str, object] = {}

    def run() -> None:
        outcome["value"] = app.dispatch_turn(s, prov, now=T)

    t = threading.Thread(target=run)
    t.start()
    assert seam.entered.wait(timeout=5)

    app.reset_session(s)
    assert s.pending_credentials is None

    seam.release()
    t.join(timeout=5)

    assert len(prov.requests) == 1
    credential = prov.requests[0].credential  # type: ignore[attr-defined]
    assert credential is not None
    assert credential.reveal() == _OLD_CANARY

    result = outcome["value"]
    assert result.attempt.status is TerminalState.CANCELLED  # type: ignore[union-attr]
    assert s.turns == []


# ================================================================ 20.2 history/focus linearization
def test_replacement_publishes_first_old_terminal_completion_discarded(
    vault: tuple[list, Path],
) -> None:
    """Lock order 1: a fresh, unpaused replacement commits (publishing cleanly, since nothing
    raced its own capture-to-publish window) while an old dispatch is paused post-interpretation;
    the old completion is then discarded by the (unregressed) LA-18-01 admissibility check."""
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")
    app.prepare_turn(s, _req(s.session_id, root), notes)
    app.approve(s, actor="jason", now=T)
    old_prepared = s.pending_prepared

    class _GatedProvider:
        name = "gated"
        adapter_version = "test.gated"

        def __init__(self) -> None:
            self.entered = threading.Event()
            self.release = threading.Event()

        def dispatch(self, request, cancel=None):  # type: ignore[no-untyped-def]
            self.entered.set()
            self.release.wait(timeout=5)
            return NormalizedResult(
                status=TerminalState.COMPLETED,
                provider_id=request.transport.provider_id,
                model_id=request.transport.model_id,
                adapter_version=self.adapter_version,
                text=structured_answer([("ok [C1]", "model_knowledge", [])]),
            )

    prov = _GatedProvider()
    commit_seam = SeamGate()
    app._pre_commit_seam = commit_seam  # type: ignore[assignment]
    outcome: dict[str, object] = {}

    def run() -> None:
        outcome["value"] = app.dispatch_turn(s, prov, now=T)

    t = threading.Thread(target=run)
    t.start()
    assert prov.entered.wait(timeout=5)
    prov.release.set()
    assert commit_seam.entered.wait(timeout=5)  # paused after interpretation, before commit

    new_snap = app.prepare_turn(s, _req(s.session_id, root, request_id="r2"), notes)

    commit_seam.release()
    t.join(timeout=5)

    result = outcome["value"]
    assert result.attempt.status is TerminalState.CANCELLED  # type: ignore[union-attr]
    assert s.turns == []
    assert s.pending_prepared is not old_prepared
    assert s.pending_prepared.snapshot.digest == new_snap.digest  # type: ignore[union-attr]


def test_terminal_completion_first_precomputed_replacement_rejected(
    vault: tuple[list, Path],
) -> None:
    """Lock order 2 (the newly required case): a paused replacement's history/focus inputs were
    captured BEFORE an old attempt's terminal commit lands; that commit advances session
    history without bumping generation, so the replacement must be rejected on resume rather
    than silently publish a snapshot bound to stale history."""
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")
    app.prepare_turn(s, _req(s.session_id, root), notes)
    app.approve(s, actor="jason", now=T)
    old_prepared = s.pending_prepared

    prepare_seam = SeamGate()
    app._prepare_commit_seam = prepare_seam  # type: ignore[assignment]
    prepare_outcome: dict[str, object] = {}

    def run_prepare() -> None:
        try:
            prepare_outcome["value"] = app.prepare_turn(
                s, _req(s.session_id, root, request_id="r2"), notes
            )
        except DriftError as exc:
            prepare_outcome["error"] = exc

    pt = threading.Thread(target=run_prepare)
    pt.start()
    assert prepare_seam.entered.wait(timeout=5)  # r2's history/focus captured, paused pre-commit

    result = app.dispatch_turn(s, MockConversationProvider(reply="a [C1]"), now=T)
    assert result.attempt.status is TerminalState.COMPLETED
    assert len(s.turns) == 1

    prepare_seam.release()
    pt.join(timeout=5)

    assert "error" in prepare_outcome
    assert isinstance(prepare_outcome["error"], DriftError)
    assert "value" not in prepare_outcome
    assert s.pending_prepared is old_prepared  # rejected; no stale-history snapshot published
    assert len(s.turns) == 1  # the old completed turn is untouched


# ================================================================ 20.3 atomic trace publication
def test_reset_during_prepare_commit_leaves_no_stale_trace_event(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")

    seam = SeamGate()
    app._prepare_commit_seam = seam  # type: ignore[assignment]
    outcome: dict[str, object] = {}

    def run_prepare() -> None:
        try:
            outcome["value"] = app.prepare_turn(s, _req(s.session_id, root), notes)
        except DriftError as exc:
            outcome["error"] = exc

    pt = threading.Thread(target=run_prepare)
    pt.start()
    assert seam.entered.wait(timeout=5)  # built, paused before its ONE atomic state+trace commit

    app.reset_session(s)  # replaces session.trace with a brand-new Trace object

    seam.release()
    pt.join(timeout=5)

    # Whether the paused prepare is rejected (generation moved) or not, the reset session's
    # trace must contain no "snapshot_created" event attributable to the paused operation's
    # now-discarded state — the state write and the trace write are one atomic commit, so
    # neither can straddle the reset.
    event_names = [e.name for e in s.trace.events]
    assert "snapshot_created" not in event_names
    assert "session_reset" in event_names
    assert "error" in outcome
    assert isinstance(outcome["error"], DriftError)


def test_reset_during_remove_context_commit_leaves_no_stale_trace_event(
    vault: tuple[list, Path],
) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")
    app.prepare_turn(s, _req(s.session_id, root), notes)
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

    app.reset_session(s)

    seam.release()
    rt.join(timeout=5)

    event_names = [e.name for e in s.trace.events]
    assert "context_removed" not in event_names
    assert "session_reset" in event_names
    assert "error" in outcome
    assert isinstance(outcome["error"], DriftError)


def test_reset_during_approve_commit_leaves_no_stale_trace_event(vault: tuple[list, Path]) -> None:
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

    event_names = [e.name for e in s.trace.events]
    assert "approval_created" not in event_names
    assert "session_reset" in event_names
    assert "error" in outcome
    assert isinstance(outcome["error"], DriftError)
