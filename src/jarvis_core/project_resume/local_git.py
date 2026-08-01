"""Local, read-only Git activity adapter (ADR-0021, brief §12; Handoff 22 Option A).

This is the *only* module in Project Resume that may reach a Git subprocess, and it does so
through an injected :class:`ProcessRunner` so every path is deterministically testable without
an installed Git. It is deliberately narrow and is not reusable authority for future commands:

- exactly three fixed command shapes are ever built, always as argument arrays with
  ``shell=False``; no selector, commit text, URI, ref, pathspec, or source metadata is ever
  passed as an argument;
- the child environment is built from an allowlist, never inherited, so credential, config,
  proxy, pager, editor, SSH, and Git directory/worktree/alternates overrides cannot leak in;
- for an authorized request, and only after authorization, identity, canonical-root, and
  Git-version validation succeed, the three commands receive exactly one command-scope
  configuration value via the environment (``GIT_CONFIG_COUNT=1`` / ``GIT_CONFIG_KEY_0=
  safe.directory`` / ``GIT_CONFIG_VALUE_0=<exact canonical granted root>``). This is a
  request-scoped authorization projection so an explicitly granted repository owned by a
  different identity is readable; ``GIT_CONFIG_NOSYSTEM=1`` stays set, ``GIT_CONFIG_GLOBAL``
  stays bound to the platform null device, ambient ``GIT_CONFIG_*`` is never inherited, and no
  persistent or temporary Git configuration file is ever created;
- granted repository activity requires Git 2.38.0 or newer (command-scope configuration and
  the ``safe.directory`` protected-config rule). A missing, unparsable, or below-floor version
  fails closed with a typed, redacted unavailable result and runs no repository command;
- records/timeout/stdout/stderr are hard-capped; overflow and timeout return typed
  ``unavailable`` rather than partial data;
- ``rev-parse --show-toplevel`` must canonicalize to exactly the granted root, so parent,
  sibling, bare, submodule, and linked-worktree roots are rejected;
- the NUL-delimited log is parsed as exact 4-field groups; any malformed field count, object
  id, or timestamp returns ``malformed`` and never partial output;
- all failures are classified to an allowlisted redacted code/message — never raw stderr,
  absolute paths, usernames, remotes, environment, or command lines; and
- nothing retries, and the adapter exposes no write method.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Protocol

from jarvis_core.project_resume.repository_activity import (
    CODE_DENIED_NO_GRANT,
    CODE_DENIED_ROOT_ESCAPE,
    CODE_DENIED_ROOT_MISMATCH,
    CODE_MALFORMED_RECORD,
    CODE_UNAVAILABLE_NO_GIT,
    CODE_UNAVAILABLE_NOT_A_REPO,
    CODE_UNAVAILABLE_OUTPUT_OVERFLOW,
    CODE_UNAVAILABLE_PROCESS_ERROR,
    CODE_UNAVAILABLE_TIMEOUT,
    DEFAULT_STALENESS_THRESHOLD_DAYS,
    RepositoryActivityDenied,
    RepositoryActivityGrant,
    RepositoryActivityMalformed,
    RepositoryActivityResult,
    RepositoryActivityStale,
    RepositoryActivityUnavailable,
    RepositoryCommitRecord,
    build_snapshot,
    is_stale,
)

_NUL = "\x00"
_VALID_OID_LENGTHS = (40, 64)  # sha1 / sha256 hex

# Minimum Git that respects command-scope ``safe.directory`` (Handoff 22 §3).
MINIMUM_GIT_VERSION = (2, 38, 0)

# Redacted, allowlisted codes for the two command-scope preconditions (Handoff 22 §4).
CODE_UNAVAILABLE_UNSUPPORTED_GIT = "unavailable_unsupported_git"
CODE_UNAVAILABLE_ENVIRONMENT_INTEGRITY = "unavailable_environment_integrity"

# Raw path: reject control/quote characters (but not backslash — a legitimate Windows separator).
_RAW_UNSAFE_CHARS = frozenset('"\n\r\x00')
# Final forward-slash value: a backslash here would be a config escape, so reject it too.
_CONFIG_VALUE_UNSAFE_CHARS = frozenset('"\\\n\r\x00')


@dataclass(frozen=True)
class ProcessResult:
    """The typed, capped outcome of one injected process invocation."""

    returncode: int
    stdout: bytes
    stderr: bytes
    timed_out: bool = False
    stdout_overflow: bool = False


class ProcessRunner(Protocol):
    """Injected process boundary (ADR-0021): fixed argv, no shell, allowlisted env, capped."""

    def run(
        self,
        argv: list[str],
        *,
        cwd: Path,
        env: dict[str, str],
        timeout_seconds: float,
        stdout_cap_bytes: int,
        stderr_cap_bytes: int,
    ) -> ProcessResult:
        ...


class SubprocessProcessRunner:
    """The real :class:`ProcessRunner`: ``subprocess`` with ``shell=False`` and hard caps."""

    def run(
        self,
        argv: list[str],
        *,
        cwd: Path,
        env: dict[str, str],
        timeout_seconds: float,
        stdout_cap_bytes: int,
        stderr_cap_bytes: int,
    ) -> ProcessResult:
        try:
            completed = subprocess.run(
                argv,
                cwd=str(cwd),
                env=env,
                capture_output=True,
                shell=False,
                timeout=timeout_seconds,
                check=False,
                start_new_session=(os.name != "nt"),
            )
        except subprocess.TimeoutExpired:
            return ProcessResult(returncode=-1, stdout=b"", stderr=b"", timed_out=True)
        except (OSError, ValueError):
            return ProcessResult(returncode=-1, stdout=b"", stderr=b"")
        out = completed.stdout or b""
        err = completed.stderr or b""
        overflow = len(out) > stdout_cap_bytes
        return ProcessResult(
            returncode=completed.returncode,
            stdout=out[:stdout_cap_bytes],
            stderr=err[:stderr_cap_bytes],
            stdout_overflow=overflow,
        )


def resolve_git_executable(
    which: Callable[[str], str | None] = shutil.which,
) -> str | None:
    """Locate the approved Git executable once, or return None when Git is unavailable."""
    return which("git")


def build_git_env(git_executable: str, *, tmp_dir: str | None = None) -> dict[str, str]:
    """Build the child environment from an allowlist — never inherited (ADR-0021).

    Includes only the platform process essentials plus the fixed Git-neutralizing variables.
    Because the map is built from scratch, inherited ``GIT_DIR``/``GIT_WORK_TREE``/alternates,
    askpass, SSH, proxy, credential, pager, editor, tracing, and ambient ``GIT_CONFIG_*``
    variables cannot leak in.
    """
    git_dir = os.path.dirname(git_executable) or os.getcwd()
    tmp = tmp_dir or os.environ.get("TMPDIR") or "/tmp"
    env: dict[str, str] = {
        "PATH": git_dir,
        "TMP": tmp,
        "TEMP": tmp,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_PAGER": "cat",
        "PAGER": "cat",
        "LC_ALL": "C",
        "LANG": "C",
        "TZ": "UTC",
    }
    if os.name == "nt":  # Windows platform essentials only
        for key in ("SystemRoot", "COMSPEC", "PATHEXT"):
            value = os.environ.get(key)
            if value is not None:
                env[key] = value
    return env


# ------------------------------------------------------- command-scope safe.directory (§4)


def _canonical_safe_directory_value(root: Path) -> str | None:
    """Return the exact canonical granted root for ``safe.directory``, or None if unusable.

    The value is the canonicalized root in git's forward-slash form. Empty, wildcard,
    interpolation, and CR/LF/NUL/escape representations are rejected (Handoff 22 §4.6); it is
    never a parent, child, prefix, or pattern (§4.5).
    """
    raw = str(root)
    # Reject adversarial/noncanonical raw forms before canonicalization (resolve() would mask an
    # empty value as the cwd and absolutize a leading "~").
    if not raw or raw == "*" or raw.startswith("~") or "%(" in raw:
        return None
    if not root.is_absolute():  # reject ambiguous relative paths (§4.4)
        return None
    if any(ch in raw for ch in _RAW_UNSAFE_CHARS):
        return None
    try:
        value = root.resolve().as_posix()
    except (OSError, ValueError):
        return None
    if not value or value == "*" or value.endswith(("/*", "/**")):
        return None
    if any(ch in value for ch in _CONFIG_VALUE_UNSAFE_CHARS) or "%(" in value:
        return None
    return value


def _command_scope_env(base_env: dict[str, str], value: str) -> dict[str, str]:
    """Project exactly one command-scope ``safe.directory`` value onto the allowlisted env.

    The base env already excludes ambient ``GIT_CONFIG_*`` (built from scratch) and keeps
    ``GIT_CONFIG_NOSYSTEM=1`` and the null global config, so only the exact triplet reaches Git.
    """
    env = dict(base_env)
    env["GIT_CONFIG_COUNT"] = "1"
    env["GIT_CONFIG_KEY_0"] = "safe.directory"
    env["GIT_CONFIG_VALUE_0"] = value
    return env


def parse_git_version(text: str) -> tuple[int, int, int] | None:
    """Parse ``git version X.Y[.Z]...`` into a ``(major, minor, patch)`` tuple, or None."""
    match = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", text)
    if not match:
        return None
    major, minor, patch = match.group(1), match.group(2), match.group(3)
    return (int(major), int(minor), int(patch) if patch is not None else 0)


# ------------------------------------------------------------------ fixed command shapes


def _cmd_toplevel(git: str, root: Path) -> list[str]:
    return [git, "--no-pager", "-C", str(root), "rev-parse", "--show-toplevel"]


def _cmd_head(git: str, root: Path) -> list[str]:
    return [
        git, "--no-pager", "--no-replace-objects", "-C", str(root),
        "rev-parse", "--verify", "HEAD",
    ]


def _cmd_log(git: str, root: Path, max_count: int) -> list[str]:
    return [
        git, "--no-pager", "--no-replace-objects",
        "-c", "color.ui=false", "-c", "core.pager=cat", "-c", "core.fsmonitor=false",
        "-c", "i18n.logOutputEncoding=UTF-8", "-C", str(root),
        "log", "--no-color", "--no-decorate", "--first-parent", "--date=iso-strict",
        "--pretty=format:%H%x00%cI%x00%an%x00%s%x00", f"--max-count={max_count}", "HEAD",
    ]


def _cmd_version(git: str) -> list[str]:
    # Non-repository capability diagnostic (Handoff 22 §3): establishes the version only.
    return [git, "--no-pager", "--version"]


# ------------------------------------------------------------------ parsing / validation


def _valid_object_id(value: str) -> bool:
    return len(value) in _VALID_OID_LENGTHS and all(c in "0123456789abcdef" for c in value)


def _valid_iso(value: str) -> bool:
    try:
        datetime.fromisoformat(value)
    except ValueError:
        return False
    return True


def parse_log_records(stdout: bytes) -> tuple[RepositoryCommitRecord, ...] | None:
    """Parse the fixed NUL log into exact 4-field records, or None when malformed.

    Invalid UTF-8, a field count that is not a multiple of four, an invalid object id, or an
    invalid committer timestamp all fail closed (partial output is never accepted).
    """
    try:
        text = stdout.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if not text.strip():
        return ()
    parts = text.split(_NUL)
    # A trailing record terminator leaves a final empty/newline artifact; drop only that.
    if parts and parts[-1] in ("", "\n"):
        parts.pop()
    if not parts or len(parts) % 4 != 0:
        return None
    records: list[RepositoryCommitRecord] = []
    for i in range(0, len(parts), 4):
        object_id = parts[i].lstrip("\n")  # strip the inter-record newline joiner
        committer_iso, author, subject = parts[i + 1], parts[i + 2], parts[i + 3]
        if not _valid_object_id(object_id) or not _valid_iso(committer_iso):
            return None
        records.append(
            RepositoryCommitRecord(
                object_id=object_id, committer_iso=committer_iso,
                author=author, subject=subject,
            )
        )
    return tuple(records)


class LocalGitRepositoryActivityAdapter:
    """The local read-only Git :class:`~...repository_activity.RepositoryActivityPort` adapter."""

    def __init__(
        self,
        runner: ProcessRunner,
        *,
        git_executable: str | None = None,
        staleness_threshold_days: int = DEFAULT_STALENESS_THRESHOLD_DAYS,
    ) -> None:
        self._runner = runner
        self._git = git_executable if git_executable is not None else resolve_git_executable()
        self._threshold_days = staleness_threshold_days
        self._env = build_git_env(self._git) if self._git else {}

    def load_activity(
        self,
        *,
        project_id: str,
        repository_root: Path,
        grant: RepositoryActivityGrant | None,
        evaluation_time: datetime,
    ) -> RepositoryActivityResult:
        # 1) Authorization and identity, before any subprocess (ADR-0021, §4.1-4.2).
        if grant is None:
            return RepositoryActivityDenied(CODE_DENIED_NO_GRANT, "repository activity denied")
        try:
            requested = repository_root.resolve()
            granted = grant.repository_root.resolve()
        except OSError:
            return RepositoryActivityDenied(CODE_DENIED_ROOT_ESCAPE, "repository root unresolved")
        if grant.project_id != project_id or granted != requested:
            return RepositoryActivityDenied(
                CODE_DENIED_ROOT_MISMATCH, "grant does not bind this project and root"
            )
        # 2) Canonical root must be an existing directory (§4.4).
        if not requested.is_dir():
            return RepositoryActivityUnavailable(
                CODE_UNAVAILABLE_NOT_A_REPO, "repository root is not a directory"
            )
        if self._git is None:
            return RepositoryActivityUnavailable(CODE_UNAVAILABLE_NO_GIT, "git is not available")

        # 3) Git-version floor for granted repository activity (§3). Fail closed otherwise.
        version = self._detect_git_version(requested)
        if version is None or version < MINIMUM_GIT_VERSION:
            return RepositoryActivityUnavailable(
                CODE_UNAVAILABLE_UNSUPPORTED_GIT, "git version is unavailable or below the floor"
            )

        # 4) Exact canonical command-scope value (§4.5-4.6).
        value = _canonical_safe_directory_value(requested)
        if value is None:
            return RepositoryActivityUnavailable(
                CODE_UNAVAILABLE_ENVIRONMENT_INTEGRITY,
                "repository root is not a valid configuration value",
            )
        env = _command_scope_env(self._env, value)

        # 5) The three accepted read-only commands, under the command-scope environment.
        return self._run_repository_activity(
            requested=requested, grant=grant, evaluation_time=evaluation_time, env=env
        )

    def _detect_git_version(self, cwd: Path) -> tuple[int, int, int] | None:
        """Establish the Git version via the fixed non-repository ``--version`` diagnostic."""
        assert self._git is not None  # guarded by the caller
        result = self._runner.run(
            _cmd_version(self._git),
            cwd=cwd,
            env=self._env,
            timeout_seconds=5.0,
            stdout_cap_bytes=4096,
            stderr_cap_bytes=1024,
        )
        if result.timed_out or result.returncode != 0:
            return None
        return parse_git_version(result.stdout.decode("utf-8", errors="replace"))

    def _run_repository_activity(
        self,
        *,
        requested: Path,
        grant: RepositoryActivityGrant,
        evaluation_time: datetime,
        env: dict[str, str],
    ) -> RepositoryActivityResult:
        assert self._git is not None  # guarded by the caller

        # 1) Repository-root verification: toplevel must canonicalize to exactly the grant root.
        top = self._invoke(_cmd_toplevel(self._git, requested), env, grant)
        if not isinstance(top, ProcessResult):
            return top  # already a typed degradation
        if top.returncode != 0:
            return RepositoryActivityUnavailable(
                CODE_UNAVAILABLE_NOT_A_REPO, "path is not a git repository"
            )
        toplevel_raw = top.stdout.decode("utf-8", errors="replace").strip()
        try:
            toplevel = Path(toplevel_raw).resolve()
        except OSError:
            return RepositoryActivityDenied(CODE_DENIED_ROOT_ESCAPE, "toplevel unresolved")
        if toplevel != requested:
            # parent / submodule / linked-worktree / bare -> escapes the granted root
            return RepositoryActivityDenied(
                CODE_DENIED_ROOT_ESCAPE, "resolved repository root escapes the granted root"
            )

        # 2) Current HEAD object identity.
        head = self._invoke(_cmd_head(self._git, requested), env, grant)
        if not isinstance(head, ProcessResult):
            return head
        if head.returncode != 0:
            return RepositoryActivityUnavailable(
                CODE_UNAVAILABLE_PROCESS_ERROR, "could not resolve HEAD"
            )
        head_object_id = head.stdout.decode("utf-8", errors="replace").strip()
        if not _valid_object_id(head_object_id):
            return RepositoryActivityMalformed(CODE_MALFORMED_RECORD, "invalid HEAD object id")

        # 3) Bounded first-parent commit activity.
        log = self._invoke(_cmd_log(self._git, requested, grant.max_records), env, grant)
        if not isinstance(log, ProcessResult):
            return log
        if log.returncode != 0:
            return RepositoryActivityUnavailable(
                CODE_UNAVAILABLE_PROCESS_ERROR, "could not read commit activity"
            )
        records = parse_log_records(log.stdout)
        if records is None:
            return RepositoryActivityMalformed(CODE_MALFORMED_RECORD, "malformed commit records")
        if len(records) > grant.max_records:
            return RepositoryActivityMalformed(CODE_MALFORMED_RECORD, "record cap exceeded")

        snapshot = build_snapshot(
            repository_id=head_object_id,
            head_object_id=head_object_id,
            records=records,
            max_records=grant.max_records,
        )
        if is_stale(
            snapshot, evaluation_time=evaluation_time, threshold_days=self._threshold_days
        ):
            return RepositoryActivityStale("stale", "repository activity is stale")
        return snapshot

    def _invoke(
        self, argv: list[str], env: dict[str, str], grant: RepositoryActivityGrant
    ) -> ProcessResult | RepositoryActivityUnavailable:
        """Run one fixed command; map timeout/overflow to typed, redacted unavailable results."""
        cwd = grant.repository_root.resolve()
        result = self._runner.run(
            argv,
            cwd=cwd,
            env=env,
            timeout_seconds=min(grant.timeout_seconds, 10.0),
            stdout_cap_bytes=grant.stdout_cap_bytes,
            stderr_cap_bytes=grant.stderr_cap_bytes,
        )
        if result.timed_out:
            return RepositoryActivityUnavailable(CODE_UNAVAILABLE_TIMEOUT, "git command timed out")
        if result.stdout_overflow:
            return RepositoryActivityUnavailable(
                CODE_UNAVAILABLE_OUTPUT_OVERFLOW, "git output exceeded the cap"
            )
        return result


def running_on_reference_platform() -> bool:
    """Best-effort check that the current platform matches the §18 reference profile."""
    return sys.platform.startswith("win")
