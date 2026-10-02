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
class _Session:
    generation: int = 0
    closed: bool = False
    active_request: str | None = None
    terminal: set[str] = field(default_factory=set)
    cancellation: threading.Event = field(default_factory=threading.Event)
    lock: threading.Lock = field(default_factory=threading.Lock)


class PersonalRecallApplication:
    contract_version = PERSONAL_RECALL_CONTRACT_VERSION

    def __init__(self, binding: RecallWorkspaceBinding) -> None:
        self._binding = binding
        self._sessions: dict[str, _Session] = {}
        self._lock = threading.Lock()

    def open_session(self) -> RecallSessionRef:
        with self._lock:
            if len(self._sessions) >= 16:
                raise RuntimeError("session limit")
            identity = uuid.uuid4().hex
            self._sessions[identity] = _Session()
        return RecallSessionRef(identity, 0)

    def _session(self, ref: RecallSessionRef) -> _Session | None:
        with self._lock:
            value = self._sessions.get(ref.session_instance)
        return (
            value
            if value is not None and value.generation == ref.generation and not value.closed
            else None
        )

    def reset(self, session: RecallSessionRef) -> RecallSessionRef:
        current = self._session(session)
        if current is None:
            return session
        with current.lock:
            current.cancellation.set()
            current.generation += 1
            current.active_request = None
            current.terminal.clear()
            current.cancellation = threading.Event()
            return RecallSessionRef(session.session_instance, current.generation)

    def close(self, session: RecallSessionRef) -> None:
        with self._lock:
            current = self._sessions.get(session.session_instance)
        if current is not None:
            with current.lock:
                current.cancellation.set()
                current.closed = True
                current.active_request = None

    def cancel(self, session: RecallSessionRef, request_id: str) -> RecallCancelResult:
        current = self._session(session)
        if current is None:
            return RecallCancelResult(request_id, RecallCancelStatus.UNKNOWN_REQUEST)
        with current.lock:
            if request_id in current.terminal:
                return RecallCancelResult(request_id, RecallCancelStatus.ALREADY_TERMINAL)
            if current.active_request != request_id:
                return RecallCancelResult(request_id, RecallCancelStatus.UNKNOWN_REQUEST)
            current.cancellation.set()
            return RecallCancelResult(request_id, RecallCancelStatus.REQUESTED)

    def recall(
        self,
        session: RecallSessionRef,
        request: RecallRequest,
        cancellation: RecallCancellation,
    ) -> RecallResult:
        current = self._session(session)
        if current is None:
            return self._failure(session, request.request_id, RecallErrorCode.SESSION_INVALID)
        try:
            request.validate()
        except (ValueError, TypeError):
            return self._failure(session, request.request_id, RecallErrorCode.INVALID_REQUEST)
        with current.lock:
            if current.active_request is not None:
                return self._failure(session, request.request_id, RecallErrorCode.BUSY)
            current.active_request = request.request_id
            current.cancellation.clear()
            generation = current.generation
        combined = _CombinedCancellation(cancellation, current.cancellation)
        try:
            result = self._execute(session, generation, request, combined)
        finally:
            with current.lock:
                if current.active_request == request.request_id:
                    current.active_request = None
                    current.terminal.add(request.request_id)
        with current.lock:
            if current.generation != generation or current.closed or combined.is_requested():
                return self._failure(
                    session, request.request_id, RecallErrorCode.CANCELLED, RecallStatus.CANCELLED
                )
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
                limitations.append(
                    "NO_MATCH" if request.question.strip() else "NO_SEARCHABLE_TERMS"
                )
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
        except Exception:
            return self._failure(session, request.request_id, RecallErrorCode.INTERNAL_FAILURE)

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
        text = str(exc)
        if "duplicate" in text:
            return RecallErrorCode.DUPLICATE_IDENTITY
        if "parse" in text:
            return RecallErrorCode.MALFORMED_SOURCE
        if "limit" in text or "deadline" in text:
            return RecallErrorCode.RESOURCE_LIMIT
        if "fingerprint" in text or "changed" in text:
            return RecallErrorCode.STALE_SOURCE
        if "unavailable" in text or "read_failed" in text:
            return RecallErrorCode.SOURCE_UNAVAILABLE
        return RecallErrorCode.SOURCE_BOUNDARY
