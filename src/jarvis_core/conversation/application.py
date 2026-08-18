"""Conversation application API and terminal-state machine (ADR-0022/0023, H07 §8).

Owns the versioned commands and the *only* accepted remote-turn ordering. Every failure
prevents all later steps. No provider or network call occurs before dispatch. Retry reuses
the exact snapshot digest and approval, creates a new attempt id, and repeats every
pre-dispatch validation; drift blocks retry and requires a fresh prepare.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from jarvis_core.conversation import context as context_service
from jarvis_core.conversation.approval import EgressApproval, create_approval
from jarvis_core.conversation.contract import (
    CONVERSATION_CONTRACT_VERSION,
    ApprovalError,
    Coverage,
    CredentialUnavailableError,
    DriftError,
    EvidenceError,
    FailureClass,
    LocalCapacityError,
    LocalConversationError,
    LocalNotReadyError,
    LocalOutputContractError,
    LocalPolicyDriftError,
    LocalTimeoutError,
    LocalUnavailableError,
    LocalUnsafeOutputError,
    PolicyBlockedError,
    RemoteEligibility,
    ValidationError,
    as_int,
    remote_eligibility,
)
from jarvis_core.conversation.evidence import validate_response
from jarvis_core.conversation.presentation import answer_from_claims
from jarvis_core.conversation.prompt import assemble_local_prompt, assemble_prompt
from jarvis_core.conversation.request import (
    LOCAL_QWEN_PROFILE_ID,
    HistoryLimits,
    PrepareTurnRequest,
)
from jarvis_core.conversation.results import AttemptResult, TurnResult
from jarvis_core.conversation.session import AttemptRecord, Session, new_attempt_id
from jarvis_core.conversation.snapshot import ContextSnapshot
from jarvis_core.models.note import Note
from jarvis_core.providers.conversation import (
    ERROR_ENDPOINT_DENIED,
    ERROR_MALFORMED,
    ERROR_NETWORK,
    ERROR_TIMEOUT,
    ERROR_UNAVAILABLE_CREDENTIAL,
    CancellationToken,
    ConversationProvider,
    Credential,
    CredentialProvider,
    NormalizedResult,
    ProviderRequest,
    TerminalState,
    TransportMetadata,
)
from jarvis_core.providers.local_ollama import (
    ERROR_LOCAL_CAPACITY,
    ERROR_LOCAL_CONTEXT_LIMIT,
    ERROR_LOCAL_NOT_READY,
    ERROR_LOCAL_OUTPUT_CONTRACT,
    ERROR_LOCAL_POLICY_DRIFT,
    ERROR_LOCAL_TIMEOUT,
    ERROR_LOCAL_UNAVAILABLE,
    ERROR_LOCAL_UNSAFE_OUTPUT,
    LocalGatewayBlocked,
    LocalReadinessGateway,
)
from jarvis_core.providers.local_ollama import (
    PROVIDER_ID as LOCAL_PROVIDER_ID,
)
from jarvis_core.query.evidence import CurrentSourceResolver
from jarvis_core.query.passages import Locator
from jarvis_core.query.passages import validate as validate_passage

# Map an adapter's redacted error code to a typed conversation failure class (C23).
_FAILURE_BY_CODE = {
    ERROR_TIMEOUT: FailureClass.PROVIDER_TIMEOUT,
    ERROR_NETWORK: FailureClass.NETWORK_DENIED,
    ERROR_MALFORMED: FailureClass.MALFORMED_RESPONSE,
    ERROR_ENDPOINT_DENIED: FailureClass.POLICY_BLOCKED,
    ERROR_UNAVAILABLE_CREDENTIAL: FailureClass.UNAVAILABLE_CREDENTIAL,
    # V05-PT-37: the local adapter never raises — it returns these redacted codes on
    # ``NormalizedResult.error_code`` exactly like every existing adapter (C23).
    ERROR_LOCAL_NOT_READY: FailureClass.LOCAL_NOT_READY,
    ERROR_LOCAL_UNAVAILABLE: FailureClass.LOCAL_UNAVAILABLE,
    ERROR_LOCAL_CAPACITY: FailureClass.LOCAL_CAPACITY,
    ERROR_LOCAL_CONTEXT_LIMIT: FailureClass.LOCAL_CONTEXT_LIMIT,
    ERROR_LOCAL_TIMEOUT: FailureClass.LOCAL_TIMEOUT,
    ERROR_LOCAL_UNSAFE_OUTPUT: FailureClass.LOCAL_UNSAFE_OUTPUT,
    ERROR_LOCAL_OUTPUT_CONTRACT: FailureClass.LOCAL_OUTPUT_CONTRACT,
    ERROR_LOCAL_POLICY_DRIFT: FailureClass.LOCAL_POLICY_DRIFT,
}

# V05-PT-37: translate the provider-layer LocalGatewayBlocked.code into the matching
# typed conversation.contract error, raised directly from prepare_turn (pre-retrieval
# — a raised exception there, not a NormalizedResult, matching this method's existing
# style, e.g. CredentialUnavailableError above).
_LOCAL_ERROR_BY_CODE: dict[str, type[LocalConversationError]] = {
    ERROR_LOCAL_NOT_READY: LocalNotReadyError,
    ERROR_LOCAL_UNAVAILABLE: LocalUnavailableError,
    ERROR_LOCAL_CAPACITY: LocalCapacityError,
    ERROR_LOCAL_TIMEOUT: LocalTimeoutError,
    ERROR_LOCAL_UNSAFE_OUTPUT: LocalUnsafeOutputError,
    ERROR_LOCAL_OUTPUT_CONTRACT: LocalOutputContractError,
    ERROR_LOCAL_POLICY_DRIFT: LocalPolicyDriftError,
}


def _raise_typed_local_error(exc: LocalGatewayBlocked) -> None:
    error_cls = _LOCAL_ERROR_BY_CODE.get(exc.code, LocalNotReadyError)
    raise error_cls(str(exc), details=exc.details) from exc


def _local_coverage() -> Coverage:
    """Handoff 150 §4 (PT37-CTO-03) correction — SUPERSEDES the prior ``_local_coverage``.

    The prior version inferred ``Coverage.COMPLETE``/``PARTIAL`` from citation-ID presence
    and model-declared limitations alone, with no binding of the answer's text to the cited
    passages. The CTO review found this let a hostile or fabricated answer cite one
    valid-but-unrelated snapshot item and reach ``COMPLETE`` coverage. That mapping is
    REMOVED here, not merely tightened: "Do not infer support or coverage from citation-ID
    presence or model-declared limitations" (Handoff 150 §4) rules out any citation/
    limitation-keyed heuristic, however strict.

    The remote/mock contract's ``Coverage`` is derived from PER-CLAIM typed, exactly
    verified support (``evidence.validate_response`` — each claim independently declares
    fact/inference/model_knowledge/unknown/assumption and, for source-backed types, is
    checked against an exact current source span or the deterministic premise conjunction).
    Handoff 147/147b's closed local schema (``{"answer","limitations","citations"}``, frozen
    and outside this correction's path ceiling) has no per-claim decomposition and no
    self-declared per-claim type at all — there is no field the model sets that would let
    Engineering honestly reconstruct a ``Claim`` without Engineering itself deciding, on the
    model's behalf, what kind of statement the answer is making. Fabricating that decision
    would not be "entering the same claim/evidence semantics"; it would be a different,
    self-authorized taxonomy standing in for it — the same category of overreach this
    correction round exists to close, just tightened rather than removed.

    Handoff 150 §4 explicitly authorizes stopping instead: "or Engineering must stop and
    request a separately authorized public-contract amendment if the closed local schema
    cannot express them." That is the path taken for THIS correction round (recorded in the
    Handoff 149 superseding revision, with a concrete proposed amendment for Product
    Owner/CTO to adjudicate): every completed local turn is unconditionally ``Coverage.NONE``
    until such an amendment defines real per-claim local evidence semantics. This does not
    weaken safety relative to the prior (returned) version — ``_revalidate_local_citations``
    (added alongside this fix) still fails the WHOLE attempt closed if any cited source is
    unknown, removed, or has drifted since the snapshot was built; the adapter still rejects
    fake/duplicate citation ids and hostile output before ``COMPLETED`` is even reachable; and
    no local turn can now present as more supported than ``NONE`` regardless of citation
    count, so citation presence can no longer manufacture an elevated coverage reading.
    """
    return Coverage.NONE


def _revalidate_local_citations(
    snap: ContextSnapshot,
    citations: tuple[str, ...],
    source_root: Path,
    notes_by_relpath: dict[str, Note],
) -> None:
    """Handoff 150 §4 (PT37-CTO-03): re-validate every item the model actually cited against
    CURRENT source bytes, at interpretation time — i.e. AFTER the (potentially slow) local
    inference call returns, not only at pre-dispatch admission (step 8 /
    ``_revalidate_current_bytes``, which runs once for the whole snapshot before the request
    is sent). Pre-dispatch revalidation closes the window up to the moment the request left
    Core; it cannot see a source edited or removed WHILE the local model was generating. A
    cited item that is no longer in the current snapshot, whose source note has disappeared,
    or whose source bytes have drifted since the snapshot was built fails the WHOLE attempt
    closed (``EvidenceError``) rather than letting a now-stale citation stand — the same
    current-byte validation semantics ``evidence.validate_response`` applies to every remote/
    mock fact/inference citation (``_validate_current_premise`` in ``evidence.py``), reused
    here directly against the local citation list rather than reimplemented.
    """
    resolver = CurrentSourceResolver(source_root)
    for item_id in citations:
        item = snap.item(item_id)
        if item is None:
            raise EvidenceError(f"cited evidence {item_id} is no longer in the current snapshot")
        note = notes_by_relpath.get(item.relpath)
        if note is None:
            raise EvidenceError(f"cited evidence {item_id} source is no longer present")
        current_bytes = resolver.current_bytes(note)
        current_text = current_bytes.decode("utf-8", "replace")
        locator = Locator(
            heading_path=item.heading_path,
            line_start=item.line_start,
            line_end=item.line_end,
        )
        result = validate_passage(
            locator=locator,
            excerpt=item.excerpt,
            source_fingerprint=item.source_fingerprint,
            current_bytes=current_bytes,
            current_text=current_text,
        )
        if not result.ok:
            raise EvidenceError(f"cited evidence {item_id} failed current-byte validation")

# AC-05-02 attempt-lifecycle bounds.
_MAX_ATTEMPTS = 5
_RETRY_ELIGIBLE_VALUES = frozenset(
    {TerminalState.COMPLETED.value, TerminalState.FAILED.value, TerminalState.CANCELLED.value}
)


def _now(now: datetime | None) -> datetime:
    return now or datetime.now(timezone.utc)


def _still_current(session: Session, prepared: object, generation: int) -> bool:
    """LA-18-01: is ``prepared``/``generation`` (captured earlier) still the session's current
    preparation? Caller MUST already hold ``session.lock``. Identity (``is``), not equality, on
    ``pending_prepared`` — a concurrent prepare/removal always installs a genuinely NEW object
    (never mutates the retained one in place), so identity is the correct "has this specific
    preparation been superseded" check, and it is paired with the generation check so a removal
    that replaces ``pending_prepared`` with an object that happened to compare equal cannot
    slip through as "unchanged" either.
    """
    return session.pending_prepared is prepared and session.generation == generation


def _prepare_inputs_still_current(
    session: Session,
    generation: int,
    history_text: str,
    focus_titles: tuple[str, ...],
) -> bool:
    """LA-18-02B: are the lifecycle generation AND the exact semantic history/focus inputs a
    preparation was built FROM (captured earlier, atomically, under ``session.lock``) still
    current? Caller MUST already hold ``session.lock``.

    A terminal turn commit does NOT bump ``generation`` (only reset/removal/a fresh prepare
    do), but it DOES change ``session.turns`` — and therefore ``history_text()`` — and may
    change ``session.focus_titles``. That is the exact gap Handoff 20 (LA-18-02B) identified: a
    preparation built from history/focus captured before such a commit must not publish a
    snapshot whose bound history is now stale, even though the generation counter alone would
    not detect it. Both signals are required.
    """
    return (
        session.generation == generation
        and session.history_text() == history_text
        and session.focus_titles == focus_titles
    )


def _egress_admissible(
    session: Session,
    prepared: object,
    credentials: object,
    generation: int,
    attempt_id: str,
) -> bool:
    """LA-18-02A-2: caller MUST already hold ``session.lock``. True iff the ENTIRE semantic
    envelope captured at initial admission — preparation identity, the exact credential-
    provider reference, lifecycle generation, and attempt identity — is still exactly what
    admission captured, AND the session still considers this attempt ``in_flight``.

    A concurrent replacement or reset always force-clears ``in_flight`` and
    ``active_attempt_id`` together (``Session._invalidate_lifecycle_locked``), replaces
    ``pending_prepared`` with a genuinely new object, and replaces (or clears)
    ``pending_credentials`` — so this single check catches every case Handoff 21 §3
    enumerates (stale preparation, stale generation, stale attempt identity, cancelled/reset,
    and stale credential-provider binding) without a separate flag.
    """
    return (
        session.pending_prepared is prepared
        and session.pending_credentials is credentials
        and session.generation == generation
        and session.active_attempt_id == attempt_id
        and session.in_flight
    )


def _revalidate_current_bytes(
    snapshot: ContextSnapshot, source_root: Path, notes_by_relpath: dict[str, Note]
) -> None:
    """Revalidate every snapshot item against current source bytes; drift fails closed."""
    resolver = CurrentSourceResolver(source_root)
    for item in snapshot.items:
        note = notes_by_relpath.get(item.relpath)
        if note is None:
            raise DriftError(f"source for {item.item_id} is no longer present")
        current_bytes = resolver.current_bytes(note)
        current_text = current_bytes.decode("utf-8", "replace")
        locator = Locator(
            heading_path=item.heading_path,
            line_start=item.line_start,
            line_end=item.line_end,
        )
        result = validate_passage(
            locator=locator,
            excerpt=item.excerpt,
            source_fingerprint=item.source_fingerprint,
            current_bytes=current_bytes,
            current_text=current_text,
        )
        if not result.ok:
            raise DriftError(f"item {item.item_id} drifted since snapshot; re-prepare required")


class ConversationApplication:
    """The versioned in-process conversation API used by the CLI and tests."""

    contract_version = CONVERSATION_CONTRACT_VERSION

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        # AC-05-02R-2 test-only instrumentation seam: a private hook invoked immediately
        # before the atomic terminal-commit lock is acquired in _execute_attempt — i.e. after
        # provider dispatch AND response interpretation have both completed, but before any
        # session-lifecycle write. Every production call path leaves this a no-op. It exists
        # so a barrier-controlled test can pause a real dispatch at exactly this internal
        # pre-commit seam and run a real concurrent invalidation (reset/prepare replacement/
        # context removal/approval invalidation) against it, then resume and assert the
        # dispatch's own terminal-commit logic detects and defeats the race — without adding
        # a parameter to any public method and without a test ever establishing the result by
        # directly poking session.in_flight/generation/active_attempt_id itself.
        self._pre_commit_seam: Callable[[], None] = lambda: None
        # LA-18-01 test-only instrumentation seams: private hooks invoked immediately before
        # each OTHER lifecycle entry point's own atomic commit-lock acquisition (prepare/
        # replacement, context removal, approval) — the same pattern as _pre_commit_seam
        # above, extended to the rest of the lifecycle-lock protocol. Every production call
        # path leaves each of these a no-op. They exist so a barrier-controlled test can pause
        # a real prepare_turn()/remove_context()/approve() call at exactly its own internal
        # pre-commit seam and run a real concurrent lifecycle operation against it, then resume
        # and assert the real, observable outcome — without adding a parameter to any public
        # method and without a test ever establishing the result by directly poking
        # session.pending_prepared/pending_approval/generation itself.
        self._prepare_commit_seam: Callable[[], None] = lambda: None
        self._remove_context_commit_seam: Callable[[], None] = lambda: None
        self._approve_commit_seam: Callable[[], None] = lambda: None
        # LA-18-02A test-only instrumentation seam: a private hook invoked immediately after
        # attempt admission (session.pending_prepared/pending_approval/pending_credentials read
        # and in_flight/generation/attempt identity claimed, all under one lock acquisition) but
        # BEFORE any credential recheck or materialization. Every production call path leaves
        # this a no-op. It exists so a barrier-controlled test can pause a REAL admitted attempt
        # at exactly this point and run a real concurrent prepare_turn() (which replaces both
        # the preparation and the credential provider) against it, then resume and assert the
        # admitted attempt used only its OWN captured credential reference — never rereading
        # session.pending_credentials — without adding a parameter to any public method.
        self._post_admission_seam: Callable[[], None] = lambda: None
        # LA-18-02A-2 test-only instrumentation seam: a private hook invoked immediately after
        # the SECOND egress-admission lock check has passed (the admitted attempt's entire
        # captured semantic envelope — preparation, credential-provider reference, generation,
        # attempt identity, in_flight — was just reverified atomically) but BEFORE any
        # credential availability recheck, materialization, prompt/provider-request
        # construction, or transport. Every production call path leaves this a no-op. It exists
        # so a barrier-controlled test can pause a REAL egress-admitted attempt at exactly this
        # point and run a real concurrent prepare_turn()/reset() against it, then resume and
        # assert the attempt proceeds using ONLY its already-captured credential — a
        # replacement/reset landing AFTER this point can still defeat the eventual terminal
        # commit, but can no longer prevent or alter the credential/provider access itself.
        self._post_egress_admission_seam: Callable[[], None] = lambda: None

    # ------------------------------------------------------------------ session
    def create_session(
        self,
        workspace_id: str,
        *,
        history_limits: HistoryLimits | None = None,
        session_id: str | None = None,
    ) -> Session:
        limits = history_limits or HistoryLimits()
        if session_id:
            session = Session(
                workspace_id=workspace_id, history_limits=limits, session_id=session_id
            )
        else:
            session = Session(workspace_id=workspace_id, history_limits=limits)
        self._sessions[session.session_id] = session
        session.trace.record(
            "session_created",
            session_id=session.session_id,
            contract_version=self.contract_version,
        )
        return session

    def get_session(self, session_id: str) -> Session:
        session = self._sessions.get(session_id)
        if session is None:
            raise ValidationError("unknown session id")
        return session

    def reset_session(self, session: Session) -> None:
        session.reset()
        session.trace.record("session_reset", session_id=session.session_id)

    def inspect_history(self, session: Session) -> list[dict[str, object]]:
        return [t.to_dict() for t in session.turns]

    # ------------------------------------------------------------------ prepare
    def prepare_turn(
        self,
        session: Session,
        request: PrepareTurnRequest,
        notes: list[Note],
        *,
        credentials: CredentialProvider | None = None,
        local_gateway: LocalReadinessGateway | None = None,
    ) -> ContextSnapshot:
        if request.session_id != session.session_id:
            raise ValidationError("request session_id does not match session")
        if request.workspace_id != session.workspace_id:
            raise ValidationError("request workspace_id does not match session")
        # Decision A (Handoff 08a): for a REMOTE destination, verify credential
        # availability BEFORE any retrieval/graph/context/prompt work. Mock and other
        # non-remote profiles require no credential and never consult one.
        if request.provider_profile.is_remote and (
            credentials is None or not credentials.is_available()
        ):
            raise CredentialUnavailableError("credential unavailable for the remote destination")
        # V05-PT-37 (Handoff 147 §5): for the inactive constrained-local profile,
        # verify readiness + capacity BEFORE any retrieval/graph/context/prompt work —
        # the same "fail closed before the expensive work" seam as the credential
        # check above, gated on ``destination_profile_id`` so every existing (remote/
        # mock) profile is completely unaffected. A caller that supplies the local
        # profile without a gateway is a configuration error (fails closed).
        if request.provider_profile.destination_profile_id == LOCAL_QWEN_PROFILE_ID:
            if local_gateway is None:
                raise LocalNotReadyError(
                    "local_gateway is required to prepare a turn for the local profile",
                    details={"reason": "gateway_not_injected", "retry_eligible": False},
                )
            try:
                local_gateway.check_admission()
            except LocalGatewayBlocked as exc:
                session.trace.record(
                    "local_admission_blocked",
                    session_id=session.session_id,
                    request_id=request.request_id,
                    destination_profile_id=LOCAL_QWEN_PROFILE_ID,
                    reason=exc.details.get("reason"),
                    retry_eligible=exc.details.get("retry_eligible"),
                )
                _raise_typed_local_error(exc)
            session.trace.record(
                "local_admission_checked",
                session_id=session.session_id,
                request_id=request.request_id,
                destination_profile_id=LOCAL_QWEN_PROFILE_ID,
                local_state=local_gateway.state.value,
            )
        session.trace.record(
            "prepare_started",
            session_id=session.session_id,
            request_id=request.request_id,
            is_remote=request.provider_profile.is_remote,
        )
        # LA-18-02B: capture the exact lifecycle generation AND the exact immutable history/
        # focus inputs this preparation is built FROM, atomically, under the lock, before doing
        # any (potentially slow) retrieval/context-construction work with them. A concurrent
        # terminal commit does not bump generation, so the generation check alone cannot detect
        # that the session's bound history advanced while this preparation was being built —
        # the semantic history/focus values must be captured and re-verified explicitly.
        with session.lock:
            captured_generation = session.generation
            captured_history_text = session.history_text()
            captured_focus_titles = session.focus_titles
        # LA-18-01: expensive retrieval/context construction stays OUTSIDE the lifecycle lock
        # (unchanged) — only the PUBLISH of its result is a protocol concern.
        prepared = context_service.prepare(
            request,
            notes,
            focus_titles=captured_focus_titles,
            history_text=captured_history_text,  # AC-05-02: bind history for byte-identical retry
        )
        # Test-only pre-commit seam (LA-18-01): a no-op in every production call path.
        self._prepare_commit_seam()
        # LA-18-01/LA-18-02B/LA-18-02C: verify the captured generation AND the captured
        # semantic history/focus inputs are STILL current; if so, publish the new
        # pending_prepared/pending_credentials, invalidate the old approval/attempt lifecycle,
        # AND record the lifecycle trace event — all as ONE atomic commit under session.lock.
        # No other lock holder (a dispatch's initial claim, another prepare/removal, a reset, or
        # a terminal commit) can ever observe the new preparation paired with the old
        # generation/approval (LA-18-01), a snapshot bound to now-stale history/focus
        # (LA-18-02B), or a "snapshot_created" event racing a concurrent reset's trace
        # replacement (LA-18-02C). A mismatch fails closed instead of publishing.
        with session.lock:
            if not _prepare_inputs_still_current(
                session, captured_generation, captured_history_text, captured_focus_titles
            ):
                raise DriftError(
                    "session history/focus changed while preparing; re-prepare required"
                )
            session.pending_prepared = prepared
            session.pending_credentials = credentials
            session._invalidate_lifecycle_locked()
            snap = prepared.snapshot
            session.trace.record(
                "snapshot_created",
                session_id=session.session_id,
                request_id=request.request_id,
                snapshot_digest=snap.digest,
                items_included=len(snap.items),
                items_omitted=len(snap.safe_omissions),
                excluded_count=as_int(snap.authorization_summary.get("excluded_count", 0)),
            )
        return snap

    def remove_context(self, session: Session, item_id: str) -> ContextSnapshot:
        # LA-18-01: capture the exact prepared identity + generation this removal is computed
        # FROM, atomically, before doing any (potentially slow) work with it.
        with session.lock:
            prepared = session.pending_prepared
            if prepared is None:
                raise ValidationError("no prepared turn to modify")
            captured_generation = session.generation
        prepared.snapshot.verify_integrity()  # AC-05-01: recompute before removal
        new_snapshot = prepared.snapshot.without_item(item_id)
        new_prepared = replace(prepared, snapshot=new_snapshot)
        # Test-only pre-commit seam (LA-18-01): a no-op in every production call path.
        self._remove_context_commit_seam()
        # LA-18-01: verify the captured preparation is STILL the current one, and publish the
        # new preparation + invalidate the approval/attempt lifecycle, as ONE atomic commit. If
        # a concurrent prepare/removal/reset already replaced or invalidated what this removal
        # was computed from, fail closed instead of publishing a snapshot derived from a
        # preparation the session no longer holds.
        with session.lock:
            if not _still_current(session, prepared, captured_generation):
                raise DriftError(
                    "prepared turn was concurrently replaced or reset; re-prepare required"
                )
            session.pending_prepared = new_prepared
            session._invalidate_lifecycle_locked()  # a new snapshot invalidates approval/attempts
            # LA-18-02C: record the lifecycle trace event under the SAME commit lock so a
            # concurrent reset cannot swap session.trace out from under this write and cause a
            # stale "context_removed" event to be attributed to the reset session's new trace.
            session.trace.record(
                "context_removed",
                session_id=session.session_id,
                snapshot_digest=new_snapshot.digest,
                items_included=len(new_snapshot.items),
            )
        return new_snapshot

    # ------------------------------------------------------------------ approve
    def approve(
        self,
        session: Session,
        *,
        actor: str,
        model_role: str = "fast",
        now: datetime | None = None,
        ttl_seconds: int = 300,
    ) -> EgressApproval:
        # LA-18-01: capture the exact prepared identity + generation this approval is built
        # FROM, atomically, before doing any work with it.
        with session.lock:
            prepared = session.pending_prepared
            if prepared is None:
                raise ValidationError("no prepared turn to approve")
            captured_generation = session.generation
        snap = prepared.snapshot
        snap.verify_integrity()  # AC-05-01: recompute before approval
        policy_version = str(snap.policy_summary.get("policy_version", ""))
        approval = create_approval(
            snap,
            actor=actor,
            model_role=model_role,
            policy_version=policy_version,
            approval_time=_now(now),
            ttl_seconds=ttl_seconds,
        )
        # Test-only pre-commit seam (LA-18-01): a no-op in every production call path.
        self._approve_commit_seam()
        # LA-18-01: verify the exact prepared identity, snapshot digest, and generation used to
        # build this approval are STILL current, and publish it, atomically. A concurrent
        # prepare/removal/reset that happened while the approval object was being constructed
        # must defeat this stale approval rather than let it become the session's approval for
        # a different (or already-invalidated) preparation.
        with session.lock:
            if not _still_current(session, prepared, captured_generation):
                raise DriftError(
                    "prepared turn was concurrently replaced or reset; re-approve required"
                )
            session.pending_approval = approval
            # LA-18-02C: record the lifecycle trace event under the SAME commit lock so a
            # concurrent reset cannot swap session.trace out from under this write and cause a
            # stale "approval_created" event to be attributed to the reset session's new trace.
            session.trace.record(
                "approval_created",
                session_id=session.session_id,
                snapshot_digest=snap.digest,
                policy_version=policy_version,
            )
        return approval

    # ------------------------------------------------------------------ dispatch
    def dispatch_turn(
        self,
        session: Session,
        provider: ConversationProvider,
        *,
        now: datetime | None = None,
        cancel: CancellationToken | None = None,
    ) -> TurnResult:
        """Initial dispatch: consumes the single-use approval exactly once (AC-05-02)."""
        return self._run_attempt(session, provider, kind="initial", now=now, cancel=cancel)

    def retry_attempt(
        self,
        session: Session,
        provider: ConversationProvider,
        *,
        now: datetime | None = None,
        cancel: CancellationToken | None = None,
    ) -> TurnResult:
        """Retry the exact approved snapshot as one NEW eligible attempt (AC-05-02)."""
        return self._run_attempt(session, provider, kind="retry", now=now, cancel=cancel)

    def _run_attempt(
        self,
        session: Session,
        provider: ConversationProvider,
        *,
        kind: str,
        now: datetime | None,
        cancel: CancellationToken | None,
    ) -> TurnResult:
        attempt_id = new_attempt_id()
        # ---- AC-05-02R / LA-18-01 lifecycle gate: fail closed BEFORE prompt assembly /
        # provider access. The AUTHORITATIVE reads of pending_prepared/pending_approval are now
        # made inside this SAME lock acquisition (LA-18-01) — not before it — alongside the
        # read-then-write of in_flight/approval_consumed/attempts, so two REAL concurrent
        # callers cannot both observe "not in flight" before either claims it, AND a dispatch
        # can never claim a prepared/approval reference read before the lock that a concurrent
        # prepare_turn()/remove_context() replacement had already superseded by the time this
        # attempt actually started.
        with session.lock:
            prepared = session.pending_prepared
            approval = session.pending_approval
            # LA-18-02A: capture the admitted credential provider in the SAME lock acquisition
            # as prepared/approval/generation/attempt identity. This exact reference is
            # threaded through credential recheck and materialization for the whole attempt;
            # the admitted attempt never rereads session.pending_credentials, so a later
            # prepare_turn() can replace session credential state but cannot alter an
            # already-admitted attempt's semantic (prepared+approval+credential) envelope.
            credentials = session.pending_credentials
            if prepared is None:
                raise ValidationError("no prepared turn to dispatch")
            if approval is None:
                raise ApprovalError("dispatch requires an explicit approval")
            if session.in_flight:
                raise ApprovalError("a dispatch for this turn is already in progress")
            if kind == "initial":
                if session.approval_consumed:
                    raise ApprovalError("approval already used; retry the attempt instead")
            else:
                if not session.attempts:
                    raise ValidationError("no terminal attempt to retry")
                if session.attempts[-1].status not in _RETRY_ELIGIBLE_VALUES:
                    raise ValidationError("last attempt is not retry-eligible")
                if len(session.attempts) >= _MAX_ATTEMPTS:
                    raise ValidationError("attempt limit reached; a fresh prepare is required")
            # Consume permission / mark in-flight and bind this attempt's identity before any
            # prompt or provider work; both generation and active_attempt_id are captured here
            # for the atomic terminal-commit admissibility check (AC-05-02R-2).
            session.in_flight = True
            session.active_attempt_id = attempt_id
            session.last_attempt_id = attempt_id
            if kind == "initial":
                session.approval_consumed = True
            generation = session.generation
        # Test-only pre-commit seam (LA-18-02A): a no-op in every production call path.
        # Invoked immediately after admission, before ANY credential recheck or
        # materialization, so a barrier-controlled test can pause a REAL admitted attempt here
        # and run a real concurrent prepare_turn()/credential replacement against it.
        self._post_admission_seam()
        try:
            return self._execute_attempt(
                session,
                provider,
                prepared,
                approval,
                credentials,
                kind,
                now,
                cancel,
                generation,
                attempt_id,
            )
        finally:
            # AC-05-02R-2 safety net: normally a no-op on the success path, because
            # _execute_attempt's own atomic terminal-commit block already clears in_flight
            # when this attempt is still admissible. It remains essential for any exception
            # raised BEFORE that block runs (a revalidation/approval/policy/credential/cost
            # failure prior to dispatch) — those paths never reach the terminal-commit block,
            # so without this, in_flight would be left permanently set and the session stuck.
            with session.lock:
                # AC-05-02R: only release in_flight if no reset/removal happened meanwhile,
                # and only if this attempt is still the one the session considers active — a
                # reset already force-clears in_flight/active_attempt_id itself; unconditionally
                # clearing again here could erroneously release a NEW attempt's exclusivity
                # that started after the reset.
                if session.generation == generation and session.active_attempt_id == attempt_id:
                    session.in_flight = False

    def _execute_attempt(
        self,
        session: Session,
        provider: ConversationProvider,
        prepared: context_service.PreparedTurn,
        approval: EgressApproval,
        credentials: CredentialProvider | None,
        kind: str,
        now: datetime | None,
        cancel: CancellationToken | None,
        generation: int,
        attempt_id: str,
    ) -> TurnResult:
        snap = prepared.snapshot

        # -------- LA-18-02A-2/A-3: second egress-admission linearization point. Capturing the
        # credential provider at initial admission (LA-18-02A) prevents a concurrent
        # prepare_turn() from SUBSTITUTING the credential this attempt uses, but by itself does
        # nothing to stop the admitted attempt from using that captured credential and reaching
        # the provider even when a replacement, reset, OR cancellation has ALREADY invalidated
        # it — terminal commit / cooperative-cancellation handling converts that to a discarded
        # result, but the unauthorized egress itself would already have happened. Re-verify, at
        # the SAME short decision point, that the ENTIRE admitted semantic envelope is still
        # exactly what admission captured AND that the exact attempt cancellation token has not
        # already won; if either fails, fail closed before any credential availability check,
        # materialization, prompt/provider-request construction, or transport — and emit no
        # credential/provider-attempt trace event for the discarded attempt. Reading
        # ``cancel.cancelled`` is a non-blocking thread-safe property check (never a ``.wait()``
        # call), so this remains a short, non-blocking lock acquisition.
        with session.lock:
            envelope_ok = _egress_admissible(session, prepared, credentials, generation, attempt_id)
            already_cancelled = envelope_ok and cancel is not None and cancel.cancelled
            admissible = envelope_ok and not already_cancelled
            if not admissible:
                message = (
                    "attempt cancelled before egress admission"
                    if already_cancelled
                    else "attempt discarded before egress admission: session lifecycle changed"
                )
                return TurnResult(
                    turn_number=session.peek_turn_number(),
                    request_id=snap.request_id,
                    session_id=session.session_id,
                    snapshot_digest=snap.digest,
                    coverage=Coverage.NONE,
                    attempt=AttemptResult(
                        attempt_id=attempt_id,
                        status=TerminalState.CANCELLED,
                        failure=FailureClass.CANCELLED,
                        message=message,
                    ),
                )
        # Test-only pre-egress-access seam (LA-18-02A-2): a no-op in every production call
        # path. Invoked immediately after egress admission passes, before ANY credential
        # recheck, materialization, prompt/provider-request construction, or transport.
        self._post_egress_admission_seam()

        moment = _now(now)

        # -------- step 8: revalidate approval, policy, eligibility, credential, cost, bytes
        snap.verify_integrity()  # AC-05-01: recompute canonical digest before dispatch
        policy_version = str(snap.policy_summary.get("policy_version", ""))
        approval.check(snap, policy_version=policy_version, now=moment)
        self._recheck_eligibility(snap)
        self._recheck_credential(credentials, snap)
        self._recheck_cost(snap, provider)
        _revalidate_current_bytes(snap, prepared.source_root, prepared.notes_by_relpath)
        session.trace.record(
            "revalidation_passed",
            session_id=session.session_id,
            snapshot_digest=snap.digest,
            attempt_id=attempt_id,
        )

        # -------- step 9: deterministically assemble the prompt within budget (bound history)
        # V05-PT-37: the local profile has its own frozen limits/template/counter
        # (Handoff 147/147b §2-3) and is never mixed with the remote budget path.
        # NOTE: ``ProviderPolicy`` (snapshot.py) is out of the Handoff 148 path ceiling
        # and carries no ``destination_profile_id`` field, so the local/remote branch is
        # keyed off ``provider_id`` (already present on ``ProviderPolicy`` and copied
        # verbatim from ``ProviderProfile.provider_id`` by ``context.py``) instead.
        if snap.provider_policy.provider_id == LOCAL_PROVIDER_ID:
            projection = assemble_local_prompt(snap)
        else:
            projection = assemble_prompt(snap)
        session.trace.record(
            "prompt_assembled",
            session_id=session.session_id,
            attempt_id=attempt_id,
            total_tokens=as_int(projection.budget_report["total_tokens"]),
            input_tokens=as_int(projection.budget_report["input_tokens"]),
            output_reserve_tokens=as_int(projection.budget_report["output_reserve_tokens"]),
        )

        # -------- step 10: dispatch exactly once through the selected adapter
        credential = self._credential(credentials, snap)
        # V05-PT-37: ``diagnostics`` never reaches the wire (ProviderRequest docstring)
        # — it is the only channel through which the local adapter's citation-identity
        # check (``validate_local_response``'s "fake citation" rejection, Handoff 147
        # §4) can see which item ids are actually current-snapshot-authorized. Scoped
        # to the local profile only; every existing (remote/mock) adapter ignores
        # ``diagnostics`` entirely and is unaffected.
        diagnostics: dict[str, object] = {}
        if snap.provider_policy.provider_id == LOCAL_PROVIDER_ID:
            diagnostics["allowed_citation_ids"] = tuple(item.item_id for item in snap.items)
        request = ProviderRequest(
            request_id=snap.request_id,
            attempt_id=attempt_id,
            content=projection.content,
            transport=TransportMetadata(
                provider_id=snap.provider_policy.provider_id,
                model_id=snap.provider_policy.model_id,
                scheme=snap.provider_policy.scheme,
                host=snap.provider_policy.host,
                path=snap.provider_policy.path,
                operation=snap.provider_policy.operation,
                timeout_seconds=snap.provider_policy.timeout_seconds,
                max_input_tokens=snap.provider_policy.max_input_tokens,
            ),
            credential=credential,
            diagnostics=diagnostics,
        )
        session.trace.record(
            "dispatch_started",
            session_id=session.session_id,
            attempt_id=attempt_id,
            provider_id=provider.name,
            model_id=snap.provider_policy.model_id,
        )
        result = provider.dispatch(request, cancel)
        # AC-05-02: honor cancellation even if the provider ignored the token — a provider
        # that returns a completed result cannot produce a second terminal state.
        if cancel is not None and cancel.cancelled and result.status is not TerminalState.CANCELLED:
            result = replace(
                result, status=TerminalState.CANCELLED, text=None, finish_reason="cancelled"
            )

        # -------- steps 11-12: normalize outcome, validate evidence (AC-05-02R-2: response
        # interpretation happens here, WITHOUT holding session.lock, same as provider dispatch
        # above — this can be real file I/O revalidation work and must not block any other
        # session-lock holder such as a concurrent reset()).
        attempt = self._interpret(session, prepared, snap, attempt_id, result)

        # Test-only pre-commit seam (AC-05-02R-2): a no-op in every production call path; see
        # __init__ for what this exists for.
        self._pre_commit_seam()

        # -------- atomic terminal commit (AC-05-02R-2): acquire session.lock exactly once,
        # AFTER both provider work and interpretation are complete, and atomically (1) validate
        # the captured generation AND this attempt's identity are still current, (2) decide
        # whether completion is still admissible, and if so (3) append the terminal attempt,
        # (4) record the single public turn, (5) update focus and the trace terminal event, and
        # (6) clear in_flight — all under the one lock acquisition, so no other lock holder
        # (a reset(), a fresh prepare_turn(), a remove_context()) can observe or interleave a
        # partial mix of these writes. A lifecycle invalidation that happened at ANY point up
        # to and including right now — including one that raced with interpretation itself,
        # which the prior "check staleness before interpreting" ordering could miss — is
        # detected here and discards this late completion instead of writing it in.
        with session.lock:
            admissible = (
                session.generation == generation and session.active_attempt_id == attempt_id
            )
            if not admissible:
                return TurnResult(
                    turn_number=session.peek_turn_number(),
                    request_id=snap.request_id,
                    session_id=session.session_id,
                    snapshot_digest=snap.digest,
                    coverage=Coverage.NONE,
                    attempt=AttemptResult(
                        attempt_id=attempt_id,
                        status=TerminalState.CANCELLED,
                        failure=FailureClass.CANCELLED,
                        message="attempt discarded: session lifecycle was reset before completion",
                        usage=result.usage,
                        cost=result.cost,
                        finish_reason=result.finish_reason,
                        elapsed_ms=result.elapsed_ms,
                    ),
                )
            session.attempts.append(AttemptRecord(attempt_id, attempt.status.value, kind))
            # V05-PT-37 / Handoff 150 §4 (PT37-CTO-03 correction): a completed local-profile
            # attempt carries no ``evidence`` (that taxonomy belongs to the remote/mock claims
            # contract only). It no longer infers an elevated coverage from citations/
            # limitations either — see ``_local_coverage``'s docstring for why that inference
            # was removed rather than tightened. Every completed local turn is unconditionally
            # ``Coverage.NONE``.
            if attempt.evidence is not None:
                coverage = attempt.evidence.coverage
            elif attempt.status is TerminalState.COMPLETED:
                coverage = _local_coverage()
            else:
                coverage = Coverage.NONE
            turn_number = session.peek_turn_number()
            if attempt.status is TerminalState.COMPLETED and attempt.text is not None:
                record = session.record_turn(
                    request_id=snap.request_id,
                    snapshot_digest=snap.digest,
                    user_text=snap.normalized_user_input,
                    answer_text=attempt.text,
                    coverage=coverage.value,
                )
                turn_number = record.turn_number
                session.set_focus(prepared.focus_titles)
            session.trace.record(
                "dispatch_completed"
                if attempt.status is TerminalState.COMPLETED
                else "attempt_failed",
                session_id=session.session_id,
                attempt_id=attempt_id,
                status=attempt.status.value,
                failure=attempt.failure.value if attempt.failure else None,
                coverage=coverage.value,
                usage_provenance=attempt.usage.provenance.value,
                cost_provenance=attempt.cost.provenance.value,
            )
            session.in_flight = False
            return TurnResult(
                turn_number=turn_number,
                request_id=snap.request_id,
                session_id=session.session_id,
                snapshot_digest=snap.digest,
                coverage=coverage,
                attempt=attempt,
            )

    @staticmethod
    def cancel_attempt(cancel: CancellationToken) -> None:
        """Signal cooperative cancellation of an in-flight attempt."""
        cancel.cancel()

    # ------------------------------------------------------------------ internals
    def _recheck_eligibility(self, snap: ContextSnapshot) -> None:
        if not snap.provider_policy.is_remote:
            return
        for item in snap.items:
            if remote_eligibility(item.sensitivity) is RemoteEligibility.DENIED:
                raise PolicyBlockedError(
                    f"item {item.item_id} is not eligible for the remote destination"
                )

    def _recheck_credential(
        self, credentials: CredentialProvider | None, snap: ContextSnapshot
    ) -> None:
        # Decision A: repeated before dispatch. A credential that became unavailable
        # after approval blocks dispatch before prompt assembly or transport.
        # LA-18-02A: ``credentials`` is the exact provider captured at admission time —
        # never a fresh read of session.pending_credentials, which a concurrent
        # prepare_turn() may have already replaced.
        if not snap.provider_policy.is_remote:
            return
        if credentials is None or not credentials.is_available():
            raise CredentialUnavailableError("provider credential is unavailable")

    def _recheck_cost(self, snap: ContextSnapshot, provider: ConversationProvider) -> None:
        estimator = getattr(provider, "estimate_cost_usd", None)
        if not callable(estimator):
            return
        estimate = estimator(snap)
        if estimate is not None and estimate > snap.max_cost_usd_per_request:
            raise PolicyBlockedError(
                f"estimated cost {estimate} exceeds per-request ceiling "
                f"{snap.max_cost_usd_per_request}"
            )

    def _credential(
        self, credentials: CredentialProvider | None, snap: ContextSnapshot
    ) -> Credential | None:
        # The opaque credential materializes only here, at the adapter boundary, for the
        # one approved remote dispatch. It is never placed in the snapshot/approval/trace.
        # LA-18-02A: ``credentials`` is the exact provider captured at admission time — see
        # ``_recheck_credential`` above.
        if not snap.provider_policy.is_remote:
            return None
        return credentials.get() if credentials is not None else None

    def _interpret(
        self,
        session: Session,
        prepared: context_service.PreparedTurn,
        snap: ContextSnapshot,
        attempt_id: str,
        result: NormalizedResult,
    ) -> AttemptResult:
        usage = result.usage
        cost = result.cost
        if result.status is TerminalState.CANCELLED:
            session.trace.record(
                "attempt_cancelled", session_id=session.session_id, attempt_id=attempt_id
            )
            return AttemptResult(
                attempt_id=attempt_id,
                status=TerminalState.CANCELLED,
                failure=FailureClass.CANCELLED,
                message="attempt cancelled before completion",
                usage=usage,
                cost=cost,
                finish_reason=result.finish_reason,
                elapsed_ms=result.elapsed_ms,
            )
        if result.status in (TerminalState.FAILED, TerminalState.BLOCKED):
            default = (
                FailureClass.POLICY_BLOCKED
                if result.status is TerminalState.BLOCKED
                else FailureClass.MALFORMED_RESPONSE
            )
            failure = _FAILURE_BY_CODE.get(result.error_code or "", default)
            return AttemptResult(
                attempt_id=attempt_id,
                status=result.status,
                failure=failure,
                message=result.error_code or "provider returned a non-completed status",
                usage=usage,
                cost=cost,
                finish_reason=result.finish_reason,
                elapsed_ms=result.elapsed_ms,
                details=result.details,
            )
        # V05-PT-37: a completed local-profile attempt is already fully validated by
        # the adapter (``validate_local_response`` — hostile-output boundary, closed
        # schema, unknown-field rejection, duplicate/fake-citation rejection; Handoff
        # 147 §4) BEFORE it can reach COMPLETED. This is therefore a trusted decode of
        # OUR OWN adapter's canonical JSON (``LocalOllamaAdapter.dispatch``), never a
        # re-validation of untrusted model output, and never the remote claims
        # taxonomy (``evidence.validate_response`` expects a `claims` list the local
        # closed schema does not have and never will).
        if snap.provider_policy.provider_id == LOCAL_PROVIDER_ID:
            try:
                payload = json.loads(result.text or "")
                local_answer = payload["answer"]
                local_limitations = tuple(payload.get("limitations") or ())
                local_citations = tuple(payload.get("citations") or ())
                if not isinstance(local_answer, str):
                    raise TypeError("answer is not a string")
            except (ValueError, KeyError, TypeError) as exc:
                return AttemptResult(
                    attempt_id=attempt_id,
                    status=TerminalState.FAILED,
                    failure=FailureClass.LOCAL_OUTPUT_CONTRACT,
                    message="local response could not be decoded after adapter validation",
                    usage=usage,
                    cost=cost,
                    finish_reason=result.finish_reason,
                    elapsed_ms=result.elapsed_ms,
                    details={
                        "reason": "post_validation_decode_failed",
                        "error": type(exc).__name__,
                    },
                )
            # Handoff 150 §4 (PT37-CTO-03): re-validate every cited item against CURRENT
            # source bytes at interpretation time, after the (potentially slow) local
            # inference call — closes the drift window pre-dispatch revalidation (step 8)
            # cannot see. An unknown, removed, or drifted citation fails the WHOLE attempt
            # closed; it can never reach COMPLETED.
            try:
                _revalidate_local_citations(
                    snap, local_citations, prepared.source_root, prepared.notes_by_relpath
                )
            except EvidenceError as exc:
                return AttemptResult(
                    attempt_id=attempt_id,
                    status=TerminalState.FAILED,
                    failure=FailureClass.EVIDENCE_FAILED,
                    message=str(exc),
                    usage=usage,
                    cost=cost,
                    finish_reason=result.finish_reason,
                    elapsed_ms=result.elapsed_ms,
                )
            coverage = _local_coverage()
            # supported_count is 0, never len(local_citations): Handoff 150 §4 prohibits
            # treating citation presence as support. This trace event now records only that
            # every citation named was verified current (not fake, not drifted) — never that
            # any claim in the answer was actually supported by it. See ``_local_coverage``.
            session.trace.record(
                "evidence_validated",
                session_id=session.session_id,
                attempt_id=attempt_id,
                coverage=coverage.value,
                supported_count=0,
                model_knowledge_count=0,
            )
            return AttemptResult(
                attempt_id=attempt_id,
                status=TerminalState.COMPLETED,
                text=local_answer,
                usage=usage,
                cost=cost,
                finish_reason=result.finish_reason,
                elapsed_ms=result.elapsed_ms,
                local_limitations=local_limitations,
                local_citations=local_citations,
            )

        # completed -> validate claim evidence against current bytes
        text = result.text or ""
        try:
            evidence = validate_response(
                snap,
                text,
                source_root=prepared.source_root,
                notes_by_relpath=prepared.notes_by_relpath,
            )
        except EvidenceError as exc:
            return AttemptResult(
                attempt_id=attempt_id,
                status=TerminalState.FAILED,
                failure=FailureClass.EVIDENCE_FAILED,
                message=str(exc),
                usage=usage,
                cost=cost,
                finish_reason=result.finish_reason,
                elapsed_ms=result.elapsed_ms,
            )
        session.trace.record(
            "evidence_validated",
            session_id=session.session_id,
            attempt_id=attempt_id,
            coverage=evidence.coverage.value,
            supported_count=evidence.supported_count,
            model_knowledge_count=evidence.model_knowledge_count,
        )
        # AC-05-05: the stored answer is a SANITIZED rendering of the validated claims; the
        # raw provider payload (``text``) is discarded here and never stored or surfaced.
        answer = answer_from_claims(evidence)
        return AttemptResult(
            attempt_id=attempt_id,
            status=TerminalState.COMPLETED,
            text=answer,
            evidence=evidence,
            usage=usage,
            cost=cost,
            finish_reason=result.finish_reason,
            elapsed_ms=result.elapsed_ms,
        )


__all__ = ["ConversationApplication"]
