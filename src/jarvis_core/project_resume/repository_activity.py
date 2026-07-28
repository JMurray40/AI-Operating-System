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

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from jarvis_core.identity import fingerprint_bytes
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


# ==================================================================================
# C8 — the port protocol, the shared snapshot builder, and the fixture adapter (ADR-0021)
#
# Project Resume depends on this narrow port, never on ``subprocess``. Two adapters implement
# it: a deterministic fixture adapter (here, no Git required) and the local read-only Git
# adapter (``local_git``, C9). Both build the snapshot through the SAME normalization and
# fingerprint so a fixture record and a real Git record share one semantic contract. The port
# is denied by default: a request without a matching, frozen grant returns a typed
# ``RepositoryActivityDenied``, never an empty snapshot.
# ==================================================================================

DEFAULT_STALENESS_THRESHOLD_DAYS = 180


class RepositoryActivityPort(Protocol):
    """The one method Project Resume uses to read recent local commit activity (ADR-0021)."""

    def load_activity(
        self,
        *,
        project_id: str,
        repository_root: Path,
        grant: RepositoryActivityGrant | None,
        evaluation_time: datetime,
    ) -> RepositoryActivityResult:
        ...


def _record_bytes(records: tuple[RepositoryCommitRecord, ...]) -> bytes:
    """Exact normalized record bytes used for the snapshot fingerprint (both adapters)."""
    return "\n".join(
        "\x00".join((r.object_id, r.committer_iso, r.author, r.subject)) for r in records
    ).encode("utf-8")


def _committer_key(record: RepositoryCommitRecord) -> tuple[int, str]:
    """Sort key: committer timestamp descending, then object id ascending (ADR-0021)."""
    try:
        ts = datetime.fromisoformat(record.committer_iso).timestamp()
    except ValueError:
        ts = 0.0
    return (-int(ts), record.object_id)


def build_snapshot(
    *,
    repository_id: str,
    head_object_id: str,
    records: tuple[RepositoryCommitRecord, ...] | list[RepositoryCommitRecord],
    max_records: int,
    git_version: str = "",
) -> RepositoryActivitySnapshot:
    """Deterministically sort, cap, and fingerprint records into a revision-bound snapshot."""
    ordered = tuple(sorted(records, key=_committer_key))[:max_records]
    return RepositoryActivitySnapshot(
        repository_id=repository_id,
        head_object_id=head_object_id,
        records=ordered,
        fingerprint=fingerprint_bytes(_record_bytes(ordered)),
        git_version=git_version,
    )


def newest_committer_datetime(
    snapshot: RepositoryActivitySnapshot,
) -> datetime | None:
    """The most recent committer timestamp in a snapshot, or None when empty/unparseable."""
    newest: datetime | None = None
    for record in snapshot.records:
        try:
            parsed = datetime.fromisoformat(record.committer_iso)
        except ValueError:
            continue
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        if newest is None or parsed > newest:
            newest = parsed
    return newest


def is_stale(
    snapshot: RepositoryActivitySnapshot,
    *,
    evaluation_time: datetime,
    threshold_days: int = DEFAULT_STALENESS_THRESHOLD_DAYS,
) -> bool:
    """True when the newest commit is at least ``threshold_days`` old at the evaluation time."""
    newest = newest_committer_datetime(snapshot)
    if newest is None:
        return False
    eval_utc = evaluation_time.astimezone(timezone.utc)
    return (eval_utc - newest.astimezone(timezone.utc)).days >= threshold_days


@dataclass(frozen=True)
class RepositoryActivityFixture:
    """A pre-seeded, deterministic activity fixture for one canonical repository root.

    ``forced_outcome`` lets fixtures deterministically exercise the unavailable/malformed
    degradation paths without an installed Git or a real failure.
    """

    repository_id: str
    head_object_id: str
    records: tuple[RepositoryCommitRecord, ...] = ()
    forced_outcome: RepositoryActivityResult | None = None


class FixtureRepositoryActivityAdapter:
    """A deterministic :class:`RepositoryActivityPort` that runs without Git (ADR-0021).

    Fixtures are keyed by the canonical (resolved) repository-root path string. The adapter
    enforces the same default-denied, grant-bound, root-matched contract the Git adapter must:
    no grant is denied; a grant that does not bind this exact project and root is denied; a
    root with no fixture is ``unavailable`` (never an empty snapshot); a forced outcome is
    returned verbatim; otherwise a healthy snapshot is built and staleness is applied.
    """

    def __init__(
        self,
        fixtures: Mapping[str, RepositoryActivityFixture],
        *,
        staleness_threshold_days: int = DEFAULT_STALENESS_THRESHOLD_DAYS,
    ) -> None:
        self._fixtures = {str(Path(k).resolve()): v for k, v in fixtures.items()}
        self._threshold_days = staleness_threshold_days

    def load_activity(
        self,
        *,
        project_id: str,
        repository_root: Path,
        grant: RepositoryActivityGrant | None,
        evaluation_time: datetime,
    ) -> RepositoryActivityResult:
        if grant is None:
            return RepositoryActivityDenied(
                CODE_DENIED_NO_GRANT, "repository activity denied: no grant"
            )
        requested = str(repository_root.resolve())
        granted = str(grant.repository_root.resolve())
        if grant.project_id != project_id or granted != requested:
            return RepositoryActivityDenied(
                CODE_DENIED_ROOT_MISMATCH,
                "repository activity denied: grant does not bind this project and root",
            )
        fixture = self._fixtures.get(requested)
        if fixture is None:
            return RepositoryActivityUnavailable(
                CODE_UNAVAILABLE_NOT_A_REPO, "repository activity unavailable: no repository"
            )
        if fixture.forced_outcome is not None:
            return fixture.forced_outcome
        snapshot = build_snapshot(
            repository_id=fixture.repository_id,
            head_object_id=fixture.head_object_id,
            records=fixture.records,
            max_records=grant.max_records,
        )
        if is_stale(
            snapshot, evaluation_time=evaluation_time, threshold_days=self._threshold_days
        ):
            return RepositoryActivityStale(
                CODE_STALE, "repository activity is stale relative to the evaluation time"
            )
        return snapshot
