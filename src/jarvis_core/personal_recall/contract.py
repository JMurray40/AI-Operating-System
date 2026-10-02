"""Closed public contract for fixture-only Personal Recall."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path, PurePosixPath
from typing import Protocol

PERSONAL_RECALL_CONTRACT_VERSION = "jarvis.personal-recall.v1"


class RecallStatus(str, Enum):
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RecallErrorCode(str, Enum):
    INVALID_REQUEST = "INVALID_REQUEST"
    SCOPE_DENIED = "SCOPE_DENIED"
    POLICY_CHANGED = "POLICY_CHANGED"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    MALFORMED_SOURCE = "MALFORMED_SOURCE"
    STALE_SOURCE = "STALE_SOURCE"
    SOURCE_BOUNDARY = "SOURCE_BOUNDARY"
    DUPLICATE_IDENTITY = "DUPLICATE_IDENTITY"
    RESOURCE_LIMIT = "RESOURCE_LIMIT"
    BUSY = "BUSY"
    SESSION_INVALID = "SESSION_INVALID"
    CANCELLED = "CANCELLED"
    INTERNAL_FAILURE = "INTERNAL_FAILURE"


class RecallCancelStatus(str, Enum):
    REQUESTED = "requested"
    ALREADY_TERMINAL = "already_terminal"
    UNKNOWN_REQUEST = "unknown_request"


class RecallCancellation(Protocol):
    def is_requested(self) -> bool: ...


@dataclass(frozen=True)
class RecallWorkspaceBinding:
    mode: str
    fixture_root: Path
    policy_path: Path
    policy_sha256: str
    expected_policy_id: str
    expected_policy_version: str
    expected_workspace_id: str
    root_digest: str

    def __post_init__(self) -> None:
        if self.mode != "synthetic":
            raise ValueError("unsupported recall binding mode")
        if not self.fixture_root.is_absolute() or not self.policy_path.is_absolute():
            raise ValueError("recall binding paths must be absolute")
        for value in (self.policy_sha256, self.root_digest):
            if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
                raise ValueError("invalid binding digest")
        if not all(
            (self.expected_policy_id, self.expected_policy_version, self.expected_workspace_id)
        ):
            raise ValueError("invalid binding identity")


@dataclass(frozen=True)
class RecallSessionRef:
    session_instance: str
    generation: int


@dataclass(frozen=True)
class RecallRequest:
    contract_version: str
    request_id: str
    question: str
    max_results: int = 5

    def validate(self) -> None:
        if self.contract_version != PERSONAL_RECALL_CONTRACT_VERSION:
            raise ValueError("contract")
        if (
            not (1 <= len(self.request_id) <= 64)
            or not self.request_id.isascii()
            or not all(c.isalnum() or c in "_-" for c in self.request_id)
        ):
            raise ValueError("request_id")
        if not self.question.strip() or len(self.question) > 2_000:
            raise ValueError("question")
        if isinstance(self.max_results, bool) or not 1 <= self.max_results <= 5:
            raise ValueError("max_results")


@dataclass(frozen=True)
class RecallLocator:
    heading_path: tuple[str, ...]
    line_start: int
    line_end: int


@dataclass(frozen=True)
class RecallCandidate:
    rank: int
    source_id: str
    source_identity_kind: str
    title: str
    relative_path: str
    sensitivity: str
    revision_fingerprint: str
    locator: RecallLocator
    excerpt: str
    relative_relevance: float | None
    reason: str
    citation_coverage: str

    def __post_init__(self) -> None:
        path = PurePosixPath(self.relative_path)
        if path.is_absolute() or ".." in path.parts or "\\" in self.relative_path:
            raise ValueError("relative_path")
        if not 1 <= self.rank <= 5 or len(self.source_id) > 512 or len(self.title) > 256:
            raise ValueError("candidate bounds")
        if len(self.relative_path) > 1_024 or len(self.reason) > 512 or len(self.excerpt) > 600:
            raise ValueError("candidate bounds")
        if len(self.locator.heading_path) > 64 or any(
            len(v) > 256 for v in self.locator.heading_path
        ):
            raise ValueError("locator bounds")
        if self.relative_relevance is not None and not 0 <= self.relative_relevance <= 1:
            raise ValueError("relevance")


@dataclass(frozen=True)
class RecallResult:
    contract_version: str
    session_instance: str
    generation: int
    request_id: str
    status: RecallStatus
    result_type: str = "ranked_retrieval_candidates"
    resolution: str = "unresolved"
    answer_claim: str = "none"
    mode: str = "retrieve_only"
    destination: str = "local_no_provider"
    sensitivity_ceiling: str = "private"
    policy_id: str = ""
    policy_version: str = ""
    policy_digest: str = ""
    root_digest: str = ""
    coverage: str = "none"
    limitations: tuple[str, ...] = ()
    candidates: tuple[RecallCandidate, ...] = ()
    error_code: RecallErrorCode | None = None


@dataclass(frozen=True)
class RecallCancelResult:
    request_id: str
    status: RecallCancelStatus
