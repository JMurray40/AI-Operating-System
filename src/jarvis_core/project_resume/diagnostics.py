"""Read-only diagnostics and derived-state recovery for Project Resume (brief §21, A12).

Project Resume keeps no persisted index: the authorized view, lexical index, and relationship
graph are *derived* projections rebuilt in memory from canonical sources on every invocation.
"Recovering from a corrupt or missing derived index" is therefore inherent — the next run simply
reconstructs it from canonical sources — and this module makes that explicit by performing the
rebuild and reporting the resulting index version and workspace fingerprint. It also diagnoses
the environment (supported runtime, readable vault, Git availability and version) and, when a
repository root is supplied, probes it through the same local read-only Git adapter the runtime
uses, so a denied/escaping root or a non-repository is reported with the adapter's redacted code.

Every check is strictly read-only: it never writes to, repairs, or migrates canonical sources.
A recovery procedure that modified canonical sources would be release-blocking (§21).
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from jarvis_core.identity import DuplicateIdentityError
from jarvis_core.models.note import Note
from jarvis_core.policy.scope import AuthorizationScope
from jarvis_core.project_resume.local_git import (
    LocalGitRepositoryActivityAdapter,
    SubprocessProcessRunner,
    build_git_env,
    resolve_git_executable,
)
from jarvis_core.project_resume.repository_activity import (
    CODE_UNAVAILABLE_NO_GIT,
    RepositoryActivityGrant,
    RepositoryActivitySnapshot,
    RepositoryActivityStale,
    RepositoryActivityUnavailable,
)
from jarvis_core.project_resume.trace import workspace_fingerprint
from jarvis_core.query.authorized import build_authorized_view
from jarvis_core.query.contract import INDEX_VERSION
from jarvis_core.query.index import LexicalIndex
from jarvis_core.relationships.resolver import RelationshipResolver

STATUS_OK = "ok"
STATUS_WARN = "warn"
STATUS_FAIL = "fail"

_SEVERITY = {STATUS_OK: 0, STATUS_WARN: 1, STATUS_FAIL: 2}

_MIN_PYTHON = (3, 10)


@dataclass(frozen=True)
class DiagnosticCheck:
    """One read-only diagnostic result with a redacted, non-disclosing message."""

    name: str
    status: str  # STATUS_OK | STATUS_WARN | STATUS_FAIL
    message: str
    detail: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class DiagnosticsReport:
    """The ordered diagnostic checks plus the worst-case overall status."""

    checks: tuple[DiagnosticCheck, ...]

    @property
    def overall_status(self) -> str:
        worst = STATUS_OK
        for check in self.checks:
            if _SEVERITY[check.status] > _SEVERITY[worst]:
                worst = check.status
        return worst

    def to_dict(self) -> dict[str, object]:
        return {
            "overall_status": self.overall_status,
            "checks": [c.to_dict() for c in self.checks],
        }

    def render_text(self) -> str:
        symbol = {STATUS_OK: "OK  ", STATUS_WARN: "WARN", STATUS_FAIL: "FAIL"}
        lines = ["== RESUME DOCTOR =="]
        lines.append(f"Overall: {self.overall_status}")
        for check in self.checks:
            lines.append(f"[{symbol[check.status]}] {check.name}: {check.message}")
        return "\n".join(lines)


def _check_runtime() -> DiagnosticCheck:
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info[:2] < _MIN_PYTHON:
        return DiagnosticCheck(
            "runtime", STATUS_FAIL,
            f"Python {version} is below the supported minimum {_MIN_PYTHON[0]}.{_MIN_PYTHON[1]}",
            {"python_version": version},
        )
    return DiagnosticCheck(
        "runtime", STATUS_OK, f"Python {version} is supported", {"python_version": version}
    )


def _check_vault(notes: list[Note]) -> DiagnosticCheck:
    if not notes:
        return DiagnosticCheck(
            "vault", STATUS_FAIL,
            "no readable notes were discovered in the vault", {"note_count": 0},
        )
    parse_errors = sum(len(n.parse_errors) for n in notes)
    if parse_errors:
        return DiagnosticCheck(
            "vault", STATUS_WARN,
            f"{len(notes)} notes discovered with {parse_errors} parse issue(s)",
            {"note_count": len(notes), "parse_errors": parse_errors},
        )
    return DiagnosticCheck(
        "vault", STATUS_OK, f"{len(notes)} notes discovered and readable",
        {"note_count": len(notes), "parse_errors": 0},
    )


def _check_derived_state(notes: list[Note], scope: AuthorizationScope) -> DiagnosticCheck:
    """Rebuild the derived projections from canonical sources and report their fingerprint.

    This is the explicit derived-state rebuild/recovery (§21 items 5-6): the authorized view,
    lexical index, and relationship graph are reconstructed in memory from canonical sources. A
    duplicate/malformed identity state fails closed without disclosing the colliding sources.
    """
    try:
        view = build_authorized_view(notes, scope)
    except DuplicateIdentityError:
        return DiagnosticCheck(
            "derived_state", STATUS_FAIL,
            "derived state cannot be rebuilt: invalid (duplicate) identity state in canonical "
            "sources",
            {"index_version": INDEX_VERSION},
        )
    index = LexicalIndex(view.notes)
    report = RelationshipResolver(view.notes).resolve_all()
    fingerprint = workspace_fingerprint(view.notes)
    return DiagnosticCheck(
        "derived_state", STATUS_OK,
        "derived state rebuilt from canonical sources (never persisted; self-heals each run)",
        {
            "index_version": INDEX_VERSION,
            "workspace_fingerprint": fingerprint,
            "authorized_notes": len(view.notes),
            "excluded_count": view.excluded_count,
            "index_vocabulary": index.vocabulary_size,
            "graph_edges": len(report.edges),
        },
    )


def _check_git(source_root: Path, git_executable: str | None) -> tuple[DiagnosticCheck, str | None]:
    """Report Git availability and version (missing Git is a warning, not a failure)."""
    git = git_executable if git_executable is not None else resolve_git_executable()
    if git is None:
        return (
            DiagnosticCheck(
                "git", STATUS_WARN,
                "Git is unavailable; repository activity will be denied, local vault briefings "
                "are unaffected",
                {"available": False},
            ),
            None,
        )
    version = ""
    try:
        result = SubprocessProcessRunner().run(
            [git, "--version"], cwd=source_root, env=build_git_env(git),
            timeout_seconds=5.0, stdout_cap_bytes=4096, stderr_cap_bytes=1024,
        )
        if result.returncode == 0:
            version = result.stdout.decode("utf-8", errors="replace").strip()
    except OSError:
        version = ""
    return (
        DiagnosticCheck(
            "git", STATUS_OK, f"Git is available ({version or 'version unknown'})",
            {"available": True, "version": version},
        ),
        git,
    )


def _check_repository_root(
    repository_root: Path,
    *,
    git_executable: str | None,
    evaluation_time: datetime,
) -> DiagnosticCheck:
    """Probe an optional repository root through the local read-only Git adapter.

    Uses a self-bound diagnostic grant so the adapter's exact denial/escape/not-a-repo logic is
    exercised; the returned message is already redacted (no absolute paths, stderr, or remotes).
    """
    if not repository_root.is_dir():
        return DiagnosticCheck(
            "repository_root", STATUS_FAIL,
            "repository root is not an existing directory", {"is_dir": False},
        )
    adapter = LocalGitRepositoryActivityAdapter(
        SubprocessProcessRunner(), git_executable=git_executable
    )
    grant = RepositoryActivityGrant(
        workspace_id="diagnostic", project_id="diagnostic", repository_root=repository_root
    )
    result = adapter.load_activity(
        project_id="diagnostic", repository_root=repository_root,
        grant=grant, evaluation_time=evaluation_time,
    )
    if isinstance(result, RepositoryActivitySnapshot):
        return DiagnosticCheck(
            "repository_root", STATUS_OK,
            f"repository readable (HEAD {result.head_object_id[:12]}, "
            f"{len(result.records)} recent commit(s))",
            {"kind": result.kind, "records": len(result.records)},
        )
    if isinstance(result, RepositoryActivityStale):
        return DiagnosticCheck(
            "repository_root", STATUS_WARN, f"repository activity is stale: {result.message}",
            {"kind": result.kind, "code": result.code},
        )
    if isinstance(result, RepositoryActivityUnavailable) and result.code == CODE_UNAVAILABLE_NO_GIT:
        return DiagnosticCheck(
            "repository_root", STATUS_WARN, f"repository unavailable: {result.message}",
            {"kind": result.kind, "code": result.code},
        )
    # Denied (root mismatch/escape), not-a-repository, timeout/overflow/process, or malformed.
    return DiagnosticCheck(
        "repository_root", STATUS_FAIL, f"repository root rejected: {result.message}",
        {"kind": result.kind, "code": result.code},
    )


def run_diagnostics(
    notes: list[Note],
    *,
    scope: AuthorizationScope,
    source_root: Path,
    repository_root: Path | None = None,
    git_executable: str | None = None,
    evaluation_time: datetime | None = None,
) -> DiagnosticsReport:
    """Run the read-only Project Resume diagnostics and derived-state rebuild (§21)."""
    evaluation_time = evaluation_time or datetime.now(timezone.utc)
    checks: list[DiagnosticCheck] = [
        _check_runtime(),
        _check_vault(notes),
        _check_derived_state(notes, scope),
    ]
    git_check, resolved_git = _check_git(source_root, git_executable)
    checks.append(git_check)
    if repository_root is not None:
        checks.append(
            _check_repository_root(
                repository_root, git_executable=resolved_git, evaluation_time=evaluation_time
            )
        )
    return DiagnosticsReport(tuple(checks))
