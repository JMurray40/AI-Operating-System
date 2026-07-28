"""Repository-activity contract types: grant, snapshot, and typed degradation (ADR-0021).

This module defines the *data contracts* for the request-scoped, local, read-only Git
capability. The port protocol, the deterministic fixture adapter, and the local Git process
adapter are added in later increments (``local_git`` and the port wiring); the value types
here are stable, frozen, and deterministic so the request/result contracts can depend on
them without importing subprocess behavior.

Repository activity is denied by default and only ever available with an explicit, frozen,
request-scoped grant that binds one canonical repository root to one selected project for a
single invocation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from jarvis_core.project_resume.contract import REPOSITORY_ACTIVITY_CONTRACT_VERSION

# The single permitted operation (ADR-0021). No other Git operation is representable.
OPERATION_READ_RECENT_COMMITS = "read_recent_commits"

# Hard caps (ADR-0021). Grants may narrow but never exceed these.
MAX_RECORDS_HARD_CAP = 50
TIMEOUT_HARD_CAP_SECONDS = 10.0
DEFAULT_TIMEOUT_SECONDS = 5.0
STDOUT_CAP_BYTES = 1_048_576  # 1 MiB
STDERR_CAP_BYTES = 8_192  # 8 KiB

# Redacted, allowlisted degradation codes. Raw stderr/paths/creds are never surfaced.
CODE_DENIED_NO_GRANT = "denied_no_grant"
CODE_DENIED_ROOT_MISMATCH = "denied_root_mismatch"
CODE_DENIED_ROOT_ESCAPE = "denied_root_escape"
CODE_UNAVAILABLE_NO_GIT = "unavailable_no_git"
CODE_UNAVAILABLE_TIMEOUT = "unavailable_timeout"
CODE_UNAVAILABLE_OUTPUT_OVERFLOW = "unavailable_output_overflow"
CODE_UNAVAILABLE_NOT_A_REPO = "unavailable_not_a_repository"
CODE_UNAVAILABLE_PROCESS_ERROR = "unavailable_process_error"
CODE_MALFORMED_RECORD = "malformed_record"
CODE_STALE = "stale"


@dataclass(frozen=True)
class RepositoryActivityGrant:
    """A frozen, request-scoped authorization to read recent local commits (ADR-0021)."""

    workspace_id: str
    project_id: str
    repository_root: Path
    operation: str = OPERATION_READ_RECENT_COMMITS
    max_records: int = 20
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    stdout_cap_bytes: int = STDOUT_CAP_BYTES
    stderr_cap_bytes: int = STDERR_CAP_BYTES
    contract_version: str = REPOSITORY_ACTIVITY_CONTRACT_VERSION

    def __post_init__(self) -> None:
        if self.operation != OPERATION_READ_RECENT_COMMITS:
            raise ValueError(f"unsupported repository operation: {self.operation!r}")
        if not (1 <= self.max_records <= MAX_RECORDS_HARD_CAP):
            raise ValueError(f"max_records must be 1..{MAX_RECORDS_HARD_CAP}")
        if not (0 < self.timeout_seconds <= TIMEOUT_HARD_CAP_SECONDS):
            raise ValueError(f"timeout_seconds must be in (0, {TIMEOUT_HARD_CAP_SECONDS}]")
        if self.stdout_cap_bytes <= 0 or self.stdout_cap_bytes > STDOUT_CAP_BYTES:
            raise ValueError("stdout_cap_bytes out of range")
        if self.stderr_cap_bytes <= 0 or self.stderr_cap_bytes > STDERR_CAP_BYTES:
            raise ValueError("stderr_cap_bytes out of range")

    def to_dict(self) -> dict[str, object]:
        # Note: repository_root is intentionally omitted from any request-visible/trace
        # serialization elsewhere; it is included here only for internal diagnostics and is
        # never emitted in a result or trace (ADR-0021 redaction).
        return {
            "contract_version": self.contract_version,
            "workspace_id": self.workspace_id,
            "project_id": self.project_id,
            "operation": self.operation,
            "max_records": self.max_records,
            "timeout_seconds": self.timeout_seconds,
        }


@dataclass(frozen=True)
class RepositoryCommitRecord:
    """One first-parent commit record, parsed from the fixed NUL-delimited log format."""

    object_id: str
    committer_iso: str
    author: str
    subject: str

    def to_dict(self) -> dict[str, object]:
        return {
            "object_id": self.object_id,
            "committer_iso": self.committer_iso,
            "author": self.author,
            "subject": self.subject,
        }


@dataclass(frozen=True)
class RepositoryActivitySnapshot:
    """A validated, revision-bound snapshot of recent local commit activity."""

    repository_id: str
    head_object_id: str
    records: tuple[RepositoryCommitRecord, ...]
    fingerprint: str  # sha256 over exact normalized record bytes
    git_version: str = ""  # recorded in diagnostics only
    contract_version: str = REPOSITORY_ACTIVITY_CONTRACT_VERSION

    kind: str = field(default="snapshot", init=False)

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "contract_version": self.contract_version,
            "repository_id": self.repository_id,
            "head_object_id": self.head_object_id,
            "records": [r.to_dict() for r in self.records],
            "fingerprint": self.fingerprint,
        }


@dataclass(frozen=True)
class _TypedDegradation:
    """Base for the typed non-snapshot outcomes (redacted code + safe message)."""

    code: str
    message: str
    contract_version: str = REPOSITORY_ACTIVITY_CONTRACT_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "contract_version": self.contract_version,
            "code": self.code,
            "message": self.message,
        }

    @property
    def kind(self) -> str:  # pragma: no cover - overridden by subclasses
        return "degradation"


@dataclass(frozen=True)
class RepositoryActivityDenied(_TypedDegradation):
    @property
    def kind(self) -> str:
        return "denied"


@dataclass(frozen=True)
class RepositoryActivityUnavailable(_TypedDegradation):
    @property
    def kind(self) -> str:
        return "unavailable"


@dataclass(frozen=True)
class RepositoryActivityMalformed(_TypedDegradation):
    @property
    def kind(self) -> str:
        return "malformed"


@dataclass(frozen=True)
class RepositoryActivityStale(_TypedDegradation):
    @property
    def kind(self) -> str:
        return "stale"


# The typed union returned by the port (ADR-0021).
RepositoryActivityResult = (
    RepositoryActivitySnapshot
    | RepositoryActivityDenied
    | RepositoryActivityUnavailable
    | RepositoryActivityMalformed
    | RepositoryActivityStale
)
