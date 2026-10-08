"""Bounded, provider-free Personal Recall application service."""

from __future__ import annotations

import hashlib
import threading
import time
import uuid
from dataclasses import dataclass, field

from jarvis_core.models.context import ContextPackage
from jarvis_core.personal_recall.contract import (
    PERSONAL_RECALL_CONTRACT_VERSION,
    RecallCancellation,
    RecallCancelResult,
    RecallCancelStatus,
    RecallCandidate,
    RecallErrorCode,
    RecallLocator,
    RecallRequest,
    RecallResult,
    RecallSessionRef,
    RecallStatus,
    RecallWorkspaceBinding,
)
from jarvis_core.personal_recall.corpus import (
    acquire_sources,
    build_corpus_from_acquired,
    inventory_sources,
)
from jarvis_core.personal_recall.policy import load_policy
from jarvis_core.policy.errors import PolicyError
from jarvis_core.policy.scope import AuthorizationScope
from jarvis_core.providers.base import ProviderResponse
from jarvis_core.query.engine import QueryEngine
from jarvis_core.query.passages import validate_against_text

_MAX_SESSIONS = 8
_POLICY_CODES = {
    "source_boundary:cancelled": RecallErrorCode.CANCELLED,
    "source_boundary:duplicate_identity": RecallErrorCode.DUPLICATE_IDENTITY,
    "source_boundary:parse_input": RecallErrorCode.MALFORMED_SOURCE,
    "source_boundary:parse_failure": RecallErrorCode.MALFORMED_SOURCE,
    "source_boundary:resource_limit": RecallErrorCode.RESOURCE_LIMIT,
    "source_boundary:deadline": RecallErrorCode.RESOURCE_LIMIT,
    "source_boundary:fingerprint_changed": RecallErrorCode.STALE_SOURCE,
    "source_boundary:changed_during_read": RecallErrorCode.STALE_SOURCE,
    "source_boundary:changed_path": RecallErrorCode.STALE_SOURCE,
    "source_boundary:metadata_unavailable": RecallErrorCode.SOURCE_UNAVAILABLE,
    "source_boundary:read_failed": RecallErrorCode.SOURCE_UNAVAILABLE,
    "source_boundary:scan_failed": RecallErrorCode.SOURCE_UNAVAILABLE,
    "source_boundary:resolve_failed": RecallErrorCode.SOURCE_UNAVAILABLE,
    "preflight:root_unavailable": RecallErrorCode.SOURCE_UNAVAILABLE,
    "preflight:include_unavailable": RecallErrorCode.SOURCE_UNAVAILABLE,
    "source_boundary:unclassified": RecallErrorCode.SCOPE_DENIED,
    "source_boundary:reparse": RecallErrorCode.SOURCE_BOUNDARY,
    "source_boundary:escape": RecallErrorCode.SOURCE_BOUNDARY,
    "preflight:root_reparse": RecallErrorCode.SOURCE_BOUNDARY,
    "preflight:include_boundary": RecallErrorCode.SOURCE_BOUNDARY,
}


class _DenyProvider:
    name = "recall-deny-provider"

    def summarize(self, package: ContextPackage, model_role: str = "fast") -> ProviderResponse:
        raise RuntimeError("provider disabled")


class _CombinedCancellation:
    def __init__(self, external: RecallCancellation, local: threading.Event) -> None:
        self._external = external
        self._local = local

    def is_requested(self) -> bool:
        return self._local.is_set() or self._external.is_requested()


@dataclass
class _Operation:
    request_id: str
    generation: int
    cancellation: threading.Event = field(default_factory=threading.Event)
    terminal: RecallResult | None = None


@dataclass
class _Session:
    generation: int = 0
    closed: bool = False
    active: _Operation | None = None
    terminal: dict[str, RecallResult] = field(default_factory=dict)
    seen_request_ids: set[str] = field(default_factory=set)
    lock: threading.Lock = field(default_factory=threading.Lock)


class PersonalRecallApplication:
    contract_version = PERSONAL_RECALL_CONTRACT_VERSION

    def __init__(self, binding: RecallWorkspaceBinding) -> None:
        self._binding = binding
        self._sessions: dict[str, _Session] = {}
        self._lock = threading.Lock()

    def open_session(self) -> RecallSessionRef:
        with self._lock:
            closed = [
                identity
                for identity, session in self._sessions.items()
                if session.closed
            ]
            for identity in closed:
                del self._sessions[identity]
            if len(self._sessions) >= _MAX_SESSIONS:
                raise RuntimeError("session limit")
            identity = uuid.uuid4().hex
            self._sessions[identity] = _Session()
        return RecallSessionRef(identity, 0)

    def _live(self, ref: RecallSessionRef) -> _Session | None:
        with self._lock:
            value = self._sessions.get(ref.session_instance)
        if value is None or value.closed or value.generation != ref.generation:
            return None
        return value

    def reset(self, session: RecallSessionRef) -> RecallSessionRef:
        with self._lock:
            current = self._sessions.get(session.session_instance)
        if current is None or current.closed or current.generation != session.generation:
            return session
        with current.lock:
            if current.closed or current.generation != session.generation:
                return session
            if current.active is not None:
                current.active.cancellation.set()
            current.generation += 1
            current.active = None
            current.terminal.clear()
            # Retain seen_request_ids across generations to prevent replay.
            return RecallSessionRef(session.session_instance, current.generation)

    def close(self, session: RecallSessionRef) -> None:
        with self._lock:
            current = self._sessions.get(session.session_instance)
        if current is None:
            return
        with current.lock:
            if current.active is not None:
                current.active.cancellation.set()
            current.closed = True
            current.active = None

    def cancel(self, session: RecallSessionRef, request_id: str) -> RecallCancelResult:
        current = self._live(session)
        if current is None:
            return RecallCancelResult(request_id, RecallCancelStatus.UNKNOWN_REQUEST)
        with current.lock:
            if current.generation != session.generation or current.closed:
                return RecallCancelResult(request_id, RecallCancelStatus.UNKNOWN_REQUEST)
            published = current.terminal.get(request_id)
            if published is not None:
                return RecallCancelResult(request_id, RecallCancelStatus.ALREADY_TERMINAL)
            active = current.active
            if active is None or active.request_id != request_id:
                return RecallCancelResult(request_id, RecallCancelStatus.UNKNOWN_REQUEST)
            active.cancellation.set()
            return RecallCancelResult(request_id, RecallCancelStatus.REQUESTED)

    def recall(
        self,
        session: RecallSessionRef,
        request: RecallRequest,
        cancellation: RecallCancellation,
    ) -> RecallResult:
        current = self._live(session)
        if current is None:
            return self._failure(session, request.request_id, RecallErrorCode.SESSION_INVALID)
        try:
            request.validate()
        except (ValueError, TypeError):
            return self._failure(session, request.request_id, RecallErrorCode.INVALID_REQUEST)
        with current.lock:
            if current.closed or current.generation != session.generation:
                return self._failure(session, request.request_id, RecallErrorCode.SESSION_INVALID)
            if (
                request.request_id in current.terminal
                or request.request_id in current.seen_request_ids
                or (current.active is not None and current.active.request_id == request.request_id)
            ):
                return self._failure(session, request.request_id, RecallErrorCode.BUSY)
            if current.active is not None:
                return self._failure(session, request.request_id, RecallErrorCode.BUSY)
            operation = _Operation(request.request_id, current.generation)
            current.active = operation
            current.seen_request_ids.add(request.request_id)
        combined = _CombinedCancellation(cancellation, operation.cancellation)
        try:
            result = self._execute(session, operation.generation, request, combined)
        except Exception:
            result = self._failure(session, request.request_id, RecallErrorCode.INTERNAL_FAILURE)
        return self._publish(current, operation, result, combined)

    def _publish(
        self,
        current: _Session,
        operation: _Operation,
        result: RecallResult,
        cancellation: RecallCancellation,
    ) -> RecallResult:
        """Publish exactly one terminal result for this operation, under its session lock."""
        with current.lock:
            superseded = (
                current.closed
                or current.generation != operation.generation
                or operation.cancellation.is_set()
                or cancellation.is_requested()
            )
            if superseded and result.status is not RecallStatus.CANCELLED:
                result = self._failure(
                    RecallSessionRef(result.session_instance, operation.generation),
                    operation.request_id,
                    RecallErrorCode.CANCELLED,
                    RecallStatus.CANCELLED,
                )
            operation.terminal = result
            if current.active is operation:
                current.active = None
            if current.generation == operation.generation and not current.closed:
                current.terminal[operation.request_id] = result
            return result

    def _execute(
        self,
        session: RecallSessionRef,
        generation: int,
        request: RecallRequest,
        cancellation: RecallCancellation,
    ) -> RecallResult:
        deadline = time.monotonic() + 10.0
        try:
            policy_bytes = self._binding.policy_path.read_bytes()
            if hashlib.sha256(policy_bytes).hexdigest() != self._binding.policy_sha256:
                return self._failure(session, request.request_id, RecallErrorCode.POLICY_CHANGED)
            policy = load_policy(self._binding.policy_path)
            if (
                policy.policy_id != self._binding.expected_policy_id
                or policy.policy_version != self._binding.expected_policy_version
                or policy.workspace_id != self._binding.expected_workspace_id
                or policy.vault_root.resolve() != self._binding.fixture_root.resolve()
                or hashlib.sha256(str(policy.vault_root.resolve()).encode()).hexdigest()
                != self._binding.root_digest
            ):
                return self._failure(session, request.request_id, RecallErrorCode.POLICY_CHANGED)
            inventory = inventory_sources(
                policy,
                max_files=1_000,
                max_file_bytes=1_048_576,
                max_total_bytes=16_777_216,
                deadline=deadline,
                cancellation=cancellation,
            )
            acquired = acquire_sources(
                policy,
                inventory,
                max_file_bytes=1_048_576,
                max_total_bytes=16_777_216,
                deadline=deadline,
                cancellation=cancellation,
            )
            notes = build_corpus_from_acquired(policy, acquired)
            scope = AuthorizationScope(
                workspace_id=policy.workspace_id,
                max_sensitivity=policy.max_sensitivity,
                request_id=request.request_id,
                allowed_path_prefixes=policy.include_roots,
                policy_id=policy.policy_id,
                policy_version=policy.policy_version,
            )
            if cancellation.is_requested():
                return self._failure(
                    session, request.request_id, RecallErrorCode.CANCELLED, RecallStatus.CANCELLED
                )
            engine = QueryEngine(
                notes, scope=scope, source_root=policy.vault_root, provider=_DenyProvider()
            )
            answer = engine.search(request.question, limit=request.max_results)
            final_inventory = inventory_sources(
                policy,
                max_files=1_000,
                max_file_bytes=1_048_576,
                max_total_bytes=16_777_216,
                deadline=deadline,
                cancellation=cancellation,
            )
            if final_inventory != inventory:
                return self._failure(session, request.request_id, RecallErrorCode.STALE_SOURCE)
            by_path = {note.relpath: note for note in notes}
            candidates: list[RecallCandidate] = []
            for rank, citation in enumerate(answer.citations, 1):
                note = by_path.get(citation.relpath)
                if note is None or citation.source_fingerprint != note.source_fingerprint:
                    return self._failure(session, request.request_id, RecallErrorCode.STALE_SOURCE)
                check = validate_against_text(citation.locator, citation.excerpt, note.source_text)
                if not check.ok:
                    return self._failure(session, request.request_id, RecallErrorCode.STALE_SOURCE)
                candidates.append(
                    RecallCandidate(
                        rank,
                        citation.source_id,
                        citation.source_identity_kind,
                        citation.title,
                        citation.relpath,
                        str(note.frontmatter["sensitivity"]),
                        citation.source_fingerprint,
                        RecallLocator(
                            tuple(citation.locator.heading_path),
                            citation.locator.line_start,
                            citation.locator.line_end,
                        ),
                        citation.excerpt,
                        citation.relative_relevance,
                        citation.reason,
                        citation.coverage,
                    )
                )
            limitations = [
                "RETRIEVE_ONLY",
                "LEXICAL_SEARCH",
                "TOP_K_LIMIT",
                "AUTHORIZED_SCOPE_ONLY",
            ]
            if not candidates:
                limitations.append("NO_MATCH")
            coverage = answer.citation_coverage()["label"]
            if not isinstance(coverage, str):
                return self._failure(session, request.request_id, RecallErrorCode.INTERNAL_FAILURE)
            return RecallResult(
                PERSONAL_RECALL_CONTRACT_VERSION,
                session.session_instance,
                generation,
                request.request_id,
                RecallStatus.COMPLETED,
                policy_id=policy.policy_id,
                policy_version=policy.policy_version,
                policy_digest=self._binding.policy_sha256,
                root_digest=self._binding.root_digest,
                coverage=coverage,
                limitations=tuple(limitations),
                candidates=tuple(candidates),
            )
        except PolicyError as exc:
            return self._failure(session, request.request_id, self._map_policy(exc))
        except (OSError, UnicodeError):
            return self._failure(session, request.request_id, RecallErrorCode.SOURCE_UNAVAILABLE)

    def _failure(
        self,
        session: RecallSessionRef,
        request_id: str,
        code: RecallErrorCode,
        status: RecallStatus = RecallStatus.FAILED,
    ) -> RecallResult:
        return RecallResult(
            PERSONAL_RECALL_CONTRACT_VERSION,
            session.session_instance,
            session.generation,
            request_id,
            status,
            policy_digest=self._binding.policy_sha256,
            root_digest=self._binding.root_digest,
            limitations=("RETRIEVE_ONLY",),
            error_code=code,
        )

    @staticmethod
    def _map_policy(exc: PolicyError) -> RecallErrorCode:
        return _POLICY_CODES.get(str(exc), RecallErrorCode.INTERNAL_FAILURE)
