"""Conversation application API and terminal-state machine (ADR-0022/0023, H07 §8).

Owns the versioned commands and the *only* accepted remote-turn ordering. Every failure
prevents all later steps. No provider or network call occurs before dispatch. Retry reuses
the exact snapshot digest and approval, creates a new attempt id, and repeats every
pre-dispatch validation; drift blocks retry and requires a fresh prepare.
"""

from __future__ import annotations

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
    PolicyBlockedError,
    RemoteEligibility,
    ValidationError,
    as_int,
    remote_eligibility,
)
from jarvis_core.conversation.evidence import validate_response
from jarvis_core.conversation.prompt import assemble_prompt
from jarvis_core.conversation.request import HistoryLimits, PrepareTurnRequest
from jarvis_core.conversation.results import AttemptResult, TurnResult
from jarvis_core.conversation.session import Session, new_attempt_id
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
}


def _now(now: datetime | None) -> datetime:
    return now or datetime.now(timezone.utc)


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
        session.pending_credentials = credentials
        session.trace.record(
            "prepare_started",
            session_id=session.session_id,
            request_id=request.request_id,
            is_remote=request.provider_profile.is_remote,
        )
        prepared = context_service.prepare(request, notes, focus_titles=session.focus_titles)
        session.pending_prepared = prepared
        session.pending_approval = None
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
        prepared = session.pending_prepared
        if prepared is None:
            raise ValidationError("no prepared turn to modify")
        new_snapshot = prepared.snapshot.without_item(item_id)
        session.pending_prepared = replace(prepared, snapshot=new_snapshot)
        session.pending_approval = None  # any prior approval is invalidated
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
        prepared = session.pending_prepared
        if prepared is None:
            raise ValidationError("no prepared turn to approve")
        snap = prepared.snapshot
        policy_version = str(snap.policy_summary.get("policy_version", ""))
        approval = create_approval(
            snap,
            actor=actor,
            model_role=model_role,
            policy_version=policy_version,
            approval_time=_now(now),
            ttl_seconds=ttl_seconds,
        )
        session.pending_approval = approval
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
        prepared = session.pending_prepared
        approval = session.pending_approval
        if prepared is None:
            raise ValidationError("no prepared turn to dispatch")
        if approval is None:
            raise ApprovalError("dispatch requires an explicit approval")
        snap = prepared.snapshot
        attempt_id = new_attempt_id()
        session.last_attempt_id = attempt_id
        moment = _now(now)

        # -------- step 8: revalidate approval, policy, eligibility, credential, cost, bytes
        policy_version = str(snap.policy_summary.get("policy_version", ""))
        approval.check(snap, policy_version=policy_version, now=moment)
        self._recheck_eligibility(snap)
        self._recheck_credential(session, snap)
        self._recheck_cost(snap, provider)
        _revalidate_current_bytes(snap, prepared.source_root, prepared.notes_by_relpath)
        session.trace.record(
            "revalidation_passed",
            session_id=session.session_id,
            snapshot_digest=snap.digest,
            attempt_id=attempt_id,
        )

        # -------- step 9: deterministically assemble the prompt within budget
        projection = assemble_prompt(snap, history_text=session.history_text())
        session.trace.record(
            "prompt_assembled",
            session_id=session.session_id,
            attempt_id=attempt_id,
            total_tokens=as_int(projection.budget_report["total_tokens"]),
            input_tokens=as_int(projection.budget_report["input_tokens"]),
            output_reserve_tokens=as_int(projection.budget_report["output_reserve_tokens"]),
        )

        # -------- step 10: dispatch exactly once through the selected adapter
        credential = self._credential(session, snap)
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
        )
        session.trace.record(
            "dispatch_started",
            session_id=session.session_id,
            attempt_id=attempt_id,
            provider_id=provider.name,
            model_id=snap.provider_policy.model_id,
        )
        result = provider.dispatch(request, cancel)

        # -------- steps 11-12: normalize outcome, validate evidence, record turn
        attempt = self._interpret(session, prepared, snap, attempt_id, result)
        coverage = attempt.evidence.coverage if attempt.evidence is not None else Coverage.NONE
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
            "dispatch_completed" if attempt.status is TerminalState.COMPLETED else "attempt_failed",
            session_id=session.session_id,
            attempt_id=attempt_id,
            status=attempt.status.value,
            failure=attempt.failure.value if attempt.failure else None,
            coverage=coverage.value,
            usage_provenance=attempt.usage.provenance.value,
            cost_provenance=attempt.cost.provenance.value,
        )
        return TurnResult(
            turn_number=turn_number,
            request_id=snap.request_id,
            session_id=session.session_id,
            snapshot_digest=snap.digest,
            coverage=coverage,
            attempt=attempt,
        )

    def retry_attempt(
        self,
        session: Session,
        provider: ConversationProvider,
        *,
        now: datetime | None = None,
        cancel: CancellationToken | None = None,
    ) -> TurnResult:
        """Retry the exact approved snapshot as a new attempt; drift blocks it."""
        if session.pending_prepared is None or session.pending_approval is None:
            raise ValidationError("no approved turn to retry")
        return self.dispatch_turn(session, provider, now=now, cancel=cancel)

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

    def _recheck_credential(self, session: Session, snap: ContextSnapshot) -> None:
        # Decision A: repeated before dispatch. A credential that became unavailable
        # after approval blocks dispatch before prompt assembly or transport.
        if not snap.provider_policy.is_remote:
            return
        creds = session.pending_credentials
        if creds is None or not creds.is_available():
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

    def _credential(self, session: Session, snap: ContextSnapshot) -> Credential | None:
        # The opaque credential materializes only here, at the adapter boundary, for the
        # one approved remote dispatch. It is never placed in the snapshot/approval/trace.
        if not snap.provider_policy.is_remote:
            return None
        creds = session.pending_credentials
        return creds.get() if creds is not None else None

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
        return AttemptResult(
            attempt_id=attempt_id,
            status=TerminalState.COMPLETED,
            text=text,
            evidence=evidence,
            usage=usage,
            cost=cost,
            finish_reason=result.finish_reason,
            elapsed_ms=result.elapsed_ms,
        )


__all__ = ["ConversationApplication"]
