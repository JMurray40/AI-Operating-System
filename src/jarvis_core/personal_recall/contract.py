"""Closed public contract for fixture-only Personal Recall."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Protocol

PERSONAL_RECALL_CONTRACT_VERSION = "jarvis.personal-recall.v1"
_SENSITIVITIES = frozenset({"public", "internal", "private"})
_IDENTITY_KINDS = frozenset({"explicit", "path_derived"})
_COVERAGES = frozenset({"complete", "partial", "incomplete", "none", "supported"})
_RESULT_COVERAGES = frozenset({"complete", "partial", "incomplete", "none"})
_LIMITATIONS = frozenset(
    {
        "RETRIEVE_ONLY",
        "LEXICAL_SEARCH",
        "TOP_K_LIMIT",
        "AUTHORIZED_SCOPE_ONLY",
        "NO_MATCH",
        "NO_SEARCHABLE_TERMS",
    }
)
_FINGERPRINT = "sha256:"


def _text(value: object, name: str, *, maximum: int, minimum: int = 0) -> str:
    if type(value) is not str or not minimum <= len(value) <= maximum:
        raise ValueError(name)
    return value


def _fingerprint(value: object, name: str) -> str:
    text = _text(value, name, maximum=71, minimum=71)
    if not text.startswith(_FINGERPRINT) or any(
        character not in "0123456789abcdef" for character in text[7:]
    ):
        raise ValueError(name)
    return text


def _relative_path(value: object) -> str:
    text = _text(value, "relative_path", maximum=1_024, minimum=1)
    windows = PureWindowsPath(text)
    posix = PurePosixPath(text)
    if (
        windows.is_absolute()
        or posix.is_absolute()
        or windows.drive
        or windows.root
        or "\\" in text
        or ".." in windows.parts
        or ".." in posix.parts
    ):
        raise ValueError("relative_path")
    return text


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

    def __post_init__(self) -> None:
        if type(self.heading_path) is not tuple or len(self.heading_path) > 64:
            raise ValueError("heading_path")
        for value in self.heading_path:
            _text(value, "heading", maximum=256)
        for name in ("line_start", "line_end"):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise ValueError(name)
        supported = self.line_start > 0 or self.line_end > 0
        if supported and (self.line_start < 1 or self.line_end < self.line_start):
            raise ValueError("locator")
        if not supported and (self.line_start, self.line_end) != (0, 0):
            raise ValueError("locator")


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
        if type(self.rank) is not int or not 1 <= self.rank <= 5:
            raise ValueError("rank")
        _text(self.source_id, "source_id", maximum=512, minimum=1)
        if self.source_identity_kind not in _IDENTITY_KINDS:
            raise ValueError("source_identity_kind")
        _text(self.title, "title", maximum=256)
        _relative_path(self.relative_path)
        if self.sensitivity not in _SENSITIVITIES:
            raise ValueError("sensitivity")
        _fingerprint(self.revision_fingerprint, "revision_fingerprint")
        if type(self.locator) is not RecallLocator:
            raise ValueError("locator")
        excerpt = _text(self.excerpt, "excerpt", maximum=600)
        if excerpt.count("\n") > 5:
            raise ValueError("excerpt")
        supported = self.locator.line_start > 0
        if supported and not excerpt:
            raise ValueError("excerpt")
        if not supported and excerpt:
            raise ValueError("excerpt")
        _text(self.reason, "reason", maximum=512)
        if self.citation_coverage not in _COVERAGES:
            raise ValueError("citation_coverage")
        relevance = self.relative_relevance
        if relevance is not None and (
            type(relevance) not in (int, float)
            or isinstance(relevance, bool)
            or not math.isfinite(relevance)
            or not 0 <= relevance <= 1
        ):
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

    def __post_init__(self) -> None:
        if self.contract_version != PERSONAL_RECALL_CONTRACT_VERSION:
            raise ValueError("contract")
        _text(self.session_instance, "session_instance", maximum=128, minimum=1)
        if type(self.generation) is not int or self.generation < 0:
            raise ValueError("generation")
        _text(self.request_id, "request_id", maximum=64, minimum=1)
        if type(self.status) is not RecallStatus:
            raise ValueError("status")
        if (
            self.result_type != "ranked_retrieval_candidates"
            or self.resolution != "unresolved"
            or self.answer_claim != "none"
            or self.mode != "retrieve_only"
            or self.destination != "local_no_provider"
            or self.sensitivity_ceiling != "private"
        ):
            raise ValueError("result constants")
        for name in ("policy_id", "policy_version"):
            _text(getattr(self, name), name, maximum=256)
        for name in ("policy_digest", "root_digest"):
            value = getattr(self, name)
            if value and (len(value) != 64 or any(c not in "0123456789abcdef" for c in value)):
                raise ValueError(name)
        if self.coverage not in _RESULT_COVERAGES:
            raise ValueError("coverage")
        if type(self.limitations) is not tuple or any(
            item not in _LIMITATIONS for item in self.limitations
        ):
            raise ValueError("limitations")
        if (
            type(self.candidates) is not tuple
            or len(self.candidates) > 5
            or any(type(item) is not RecallCandidate for item in self.candidates)
        ):
            raise ValueError("candidates")
        if self.status is not RecallStatus.COMPLETED and self.candidates:
            raise ValueError("candidates")
        if self.error_code is None:
            if self.status is not RecallStatus.COMPLETED:
                raise ValueError("error_code")
        elif type(self.error_code) is not RecallErrorCode or self.status is RecallStatus.COMPLETED:
            raise ValueError("error_code")


@dataclass(frozen=True)
class RecallCancelResult:
    request_id: str
    status: RecallCancelStatus
