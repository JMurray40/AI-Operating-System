"""Local, read-only Git activity adapter (ADR-0021, brief §12).

This is the *only* module in Project Resume that may reach a Git subprocess, and it does so
through an injected :class:`ProcessRunner` so every path is deterministically testable without
an installed Git. It is deliberately narrow and is not reusable authority for future commands:

- exactly three fixed command shapes are ever built, always as argument arrays with
  ``shell=False``; no selector, commit text, URI, ref, pathspec, or source metadata is ever
  passed as an argument;
- the child environment is built from an allowlist, never inherited, so credential, config,
  proxy, pager, editor, SSH, and Git directory/worktree/alternates overrides cannot leak in;
- when a grant is present, the invocation points ``GIT_CONFIG_GLOBAL`` at a process-owned,
  single-entry, ephemeral config declaring *exactly the granted root* as ``safe.directory`` so
  an explicitly granted repository owned by a different identity is readable; the config lives
  under a controlled temp root proven outside the repository, carries an established-and-verified
  owner-only permission boundary before the root is written, holds one literal value (never a
  wildcard/comment/newline/include), and is created/verified/removed fail-closed — a snapshot is
  never returned when secure cleanup cannot be proven; system config stays disabled
  (``GIT_CONFIG_NOSYSTEM``), the ambient ``~/.gitconfig`` is never trusted, and the repository's
  own config/ownership is never altered;
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

import contextlib
import ctypes
import os
import shutil
import stat
import subprocess
import sys
import tempfile
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
    askpass, SSH, proxy, credential, pager, editor, and tracing variables cannot leak in.
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


# --------------------------------------------------- request-scoped safe.directory (Handoff 15)
#
# Git honors ``safe.directory`` only from system/global config — never from ``-c`` or the
# environment — so an explicitly granted repository owned by a different identity can be read
# only through a global config file we control. That file is a request-scoped security
# exception, so its whole lifecycle must be fail-closed: it is created under a controlled temp
# root proven outside the repository, with an owner-only permission boundary established AND
# verified before the private root is written, holds exactly one literal ``safe.directory``
# value (never a wildcard/comment/newline/include), and its deletion is proven — a snapshot is
# never returned when secure cleanup cannot be confirmed. ``GIT_CONFIG_NOSYSTEM`` stays set and
# the ambient ``~/.gitconfig`` is never consulted.

# Redacted, allowlisted codes for the two request-scoped security-lifecycle failures. Neither
# message ever contains the temp path, the repository root, or a raw OS error.
CODE_UNAVAILABLE_SECURITY_SETUP = "unavailable_security_setup"
CODE_UNAVAILABLE_CLEANUP_INCOMPLETE = "unavailable_cleanup_incomplete"

_CONFIG_UNSAFE_CHARS = frozenset('"\\\n\r\x00')


class SecureConfigError(Exception):
    """A request-scoped safe.directory config could not be securely created or removed.

    Raised for containment, permission, serialization, and deletion failures. The message is
    internal only and is mapped by the adapter to a redacted, typed unavailable result; it is
    never surfaced to a caller or logged with a private path.
    """


class EphemeralSafeDirectoryStore(Protocol):
    """Injected boundary that owns the request-scoped safe.directory config lifecycle."""

    def create(self, *, safe_root: Path) -> str:
        """Create the owner-only ephemeral config and return its path, or raise on any failure."""
        ...

    def remove(self, config_path: str) -> None:
        """Remove the config and its controlled temp root; raise if deletion cannot be proven."""
        ...


def _safe_config_value(safe_root: Path) -> str:
    """Return a git-config-safe literal for ``safe_root`` or raise for adversarial roots.

    The value is emitted forward-slashed and double-quoted so ``#``/``;``/spaces are literal.
    Roots that could introduce an escape, newline, extra value, or wildcard semantics are
    rejected rather than serialized.
    """
    try:
        value = safe_root.resolve().as_posix()
    except (OSError, ValueError) as exc:
        raise SecureConfigError("repository root could not be resolved") from exc
    if not value:
        raise SecureConfigError("empty repository root")
    if any(ch in value for ch in _CONFIG_UNSAFE_CHARS):
        raise SecureConfigError("repository root contains config-unsafe characters")
    if value == "*" or value.endswith(("/*", "/**")):
        raise SecureConfigError("repository root has wildcard semantics")
    return value


def _within(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
    except ValueError:
        return False
    return True


# ------------------------------------------------------------- owner-only permission boundary

if os.name == "nt":  # pragma: no cover - exercised on the Windows reference platform
    _advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    _SE_FILE_OBJECT = 1
    _OWNER_SECURITY_INFORMATION = 0x00000001
    _DACL_SECURITY_INFORMATION = 0x00000004
    _PROTECTED_DACL_SECURITY_INFORMATION = 0x80000000
    _TOKEN_QUERY = 0x0008
    _TokenUser = 1
    _GENERIC_ALL = 0x10000000
    _SET_ACCESS = 2
    _NO_INHERITANCE = 0x0
    _TRUSTEE_IS_SID = 0
    _TRUSTEE_IS_USER = 1
    _ACCESS_ALLOWED_ACE_TYPE = 0
    _SE_DACL_PROTECTED = 0x1000

    class _TRUSTEE_W(ctypes.Structure):
        _fields_ = [
            ("pMultipleTrustee", ctypes.c_void_p),
            ("MultipleTrusteeOperation", ctypes.c_ulong),
            ("TrusteeForm", ctypes.c_ulong),
            ("TrusteeType", ctypes.c_ulong),
            ("ptstrName", ctypes.c_void_p),
        ]

    class _EXPLICIT_ACCESS_W(ctypes.Structure):
        _fields_ = [
            ("grfAccessPermissions", ctypes.c_ulong),
            ("grfAccessMode", ctypes.c_ulong),
            ("grfInheritance", ctypes.c_ulong),
            ("Trustee", _TRUSTEE_W),
        ]

    class _ACE_HEADER(ctypes.Structure):
        _fields_ = [("AceType", ctypes.c_ubyte), ("AceFlags", ctypes.c_ubyte),
                    ("AceSize", ctypes.c_ushort)]

    class _ACCESS_ALLOWED_ACE(ctypes.Structure):
        _fields_ = [("Header", _ACE_HEADER), ("Mask", ctypes.c_ulong),
                    ("SidStart", ctypes.c_ulong)]

    class _ACL(ctypes.Structure):
        _fields_ = [("AclRevision", ctypes.c_ubyte), ("Sbz1", ctypes.c_ubyte),
                    ("AclSize", ctypes.c_ushort), ("AceCount", ctypes.c_ushort),
                    ("Sbz2", ctypes.c_ushort)]

    class _ACL_SIZE_INFORMATION(ctypes.Structure):
        _fields_ = [("AceCount", ctypes.c_ulong), ("AclBytesInUse", ctypes.c_ulong),
                    ("AclBytesFree", ctypes.c_ulong)]

    # Explicit prototypes so 64-bit HANDLE/PSID/PACL values are never truncated to c_int.
    _PVOID = ctypes.c_void_p
    _kernel32.GetCurrentProcess.restype = _PVOID
    _kernel32.GetCurrentProcess.argtypes = []
    _kernel32.CloseHandle.restype = ctypes.c_int
    _kernel32.CloseHandle.argtypes = [_PVOID]
    _kernel32.LocalFree.restype = _PVOID
    _kernel32.LocalFree.argtypes = [_PVOID]
    _advapi32.OpenProcessToken.restype = ctypes.c_int
    _advapi32.OpenProcessToken.argtypes = [_PVOID, ctypes.c_ulong, ctypes.POINTER(_PVOID)]
    _advapi32.GetTokenInformation.restype = ctypes.c_int
    _advapi32.GetTokenInformation.argtypes = [
        _PVOID, ctypes.c_int, _PVOID, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong),
    ]
    _advapi32.GetLengthSid.restype = ctypes.c_ulong
    _advapi32.GetLengthSid.argtypes = [_PVOID]
    _advapi32.CopySid.restype = ctypes.c_int
    _advapi32.CopySid.argtypes = [ctypes.c_ulong, _PVOID, _PVOID]
    _advapi32.SetEntriesInAclW.restype = ctypes.c_ulong
    _advapi32.SetEntriesInAclW.argtypes = [
        ctypes.c_ulong, ctypes.POINTER(_EXPLICIT_ACCESS_W), _PVOID, ctypes.POINTER(_PVOID),
    ]
    _advapi32.SetNamedSecurityInfoW.restype = ctypes.c_ulong
    _advapi32.SetNamedSecurityInfoW.argtypes = [
        ctypes.c_wchar_p, ctypes.c_int, ctypes.c_ulong, _PVOID, _PVOID, _PVOID, _PVOID,
    ]
    _advapi32.GetNamedSecurityInfoW.restype = ctypes.c_ulong
    _advapi32.GetNamedSecurityInfoW.argtypes = [
        ctypes.c_wchar_p, ctypes.c_int, ctypes.c_ulong, ctypes.POINTER(_PVOID),
        ctypes.POINTER(_PVOID), ctypes.POINTER(_PVOID), ctypes.POINTER(_PVOID),
        ctypes.POINTER(_PVOID),
    ]
    _advapi32.GetSecurityDescriptorControl.restype = ctypes.c_int
    _advapi32.GetSecurityDescriptorControl.argtypes = [
        _PVOID, ctypes.POINTER(ctypes.c_ushort), ctypes.POINTER(ctypes.c_ulong),
    ]
    _advapi32.GetAclInformation.restype = ctypes.c_int
    _advapi32.GetAclInformation.argtypes = [_PVOID, _PVOID, ctypes.c_ulong, ctypes.c_int]
    _advapi32.GetAce.restype = ctypes.c_int
    _advapi32.GetAce.argtypes = [_PVOID, ctypes.c_ulong, ctypes.POINTER(_PVOID)]
    _advapi32.EqualSid.restype = ctypes.c_int
    _advapi32.EqualSid.argtypes = [_PVOID, _PVOID]

    def _current_user_sid() -> bytes:
        token = ctypes.c_void_p()
        if not _advapi32.OpenProcessToken(
            _kernel32.GetCurrentProcess(), _TOKEN_QUERY, ctypes.byref(token)
        ):
            raise SecureConfigError("could not open process token")
        try:
            size = ctypes.c_ulong(0)
            _advapi32.GetTokenInformation(token, _TokenUser, None, 0, ctypes.byref(size))
            buf = ctypes.create_string_buffer(size.value)
            if not _advapi32.GetTokenInformation(
                token, _TokenUser, buf, size, ctypes.byref(size)
            ):
                raise SecureConfigError("could not read token user")
            sid_ptr = ctypes.cast(buf, ctypes.POINTER(ctypes.c_void_p))[0]
            length = _advapi32.GetLengthSid(sid_ptr)
            sid = ctypes.create_string_buffer(length)
            if not _advapi32.CopySid(length, sid, sid_ptr):
                raise SecureConfigError("could not copy sid")
            return sid.raw
        finally:
            _kernel32.CloseHandle(token)

    def _win_set_owner_only(path: str) -> None:
        # No inheritance: the directory and the file are each hardened explicitly, so each object
        # carries exactly one owner-only ACE and no inherited or inherit-only entries.
        sid = ctypes.create_string_buffer(_current_user_sid())
        ea = _EXPLICIT_ACCESS_W()
        ea.grfAccessPermissions = _GENERIC_ALL
        ea.grfAccessMode = _SET_ACCESS
        ea.grfInheritance = _NO_INHERITANCE
        ea.Trustee.TrusteeForm = _TRUSTEE_IS_SID
        ea.Trustee.TrusteeType = _TRUSTEE_IS_USER
        ea.Trustee.ptstrName = ctypes.cast(sid, ctypes.c_void_p)
        new_acl = ctypes.c_void_p()
        if _advapi32.SetEntriesInAclW(1, ctypes.byref(ea), None, ctypes.byref(new_acl)) != 0:
            raise SecureConfigError("could not build owner-only acl")
        try:
            status = _advapi32.SetNamedSecurityInfoW(
                ctypes.c_wchar_p(path), _SE_FILE_OBJECT,
                _DACL_SECURITY_INFORMATION | _PROTECTED_DACL_SECURITY_INFORMATION,
                None, None, new_acl, None,
            )
            if status != 0:
                raise SecureConfigError("could not apply owner-only acl")
        finally:
            _kernel32.LocalFree(new_acl)

    def _win_verify_owner_only(path: str) -> None:
        expected = ctypes.create_string_buffer(_current_user_sid())
        owner = ctypes.c_void_p()
        dacl = ctypes.c_void_p()
        sd = ctypes.c_void_p()
        status = _advapi32.GetNamedSecurityInfoW(
            ctypes.c_wchar_p(path), _SE_FILE_OBJECT,
            _DACL_SECURITY_INFORMATION | _OWNER_SECURITY_INFORMATION,
            ctypes.byref(owner), None, ctypes.byref(dacl), None, ctypes.byref(sd),
        )
        if status != 0:
            raise SecureConfigError("could not read security descriptor")
        try:
            if not dacl.value:
                raise SecureConfigError("null dacl grants everyone")  # NULL DACL == full access
            control = ctypes.c_ushort(0)
            revision = ctypes.c_ulong(0)
            if not _advapi32.GetSecurityDescriptorControl(
                sd, ctypes.byref(control), ctypes.byref(revision)
            ):
                raise SecureConfigError("could not read descriptor control")
            if not control.value & _SE_DACL_PROTECTED:
                raise SecureConfigError("dacl is not protected from inheritance")
            info = _ACL_SIZE_INFORMATION()
            if not _advapi32.GetAclInformation(
                dacl, ctypes.byref(info), ctypes.sizeof(info), 2  # AclSizeInformation
            ):
                raise SecureConfigError("could not read acl information")
            if info.AceCount != 1:
                raise SecureConfigError("dacl grants more than the owner")
            ace_ptr = ctypes.c_void_p()
            if not _advapi32.GetAce(dacl, 0, ctypes.byref(ace_ptr)):
                raise SecureConfigError("could not read ace")
            ace = ctypes.cast(ace_ptr, ctypes.POINTER(_ACCESS_ALLOWED_ACE)).contents
            if ace.Header.AceType != _ACCESS_ALLOWED_ACE_TYPE:
                raise SecureConfigError("dacl contains a non-allow ace")
            ace_address = ace_ptr.value
            if ace_address is None:
                raise SecureConfigError("could not read ace address")
            # SID begins immediately after the ACE header and the 32-bit access mask.
            sid_offset = ctypes.sizeof(_ACE_HEADER) + ctypes.sizeof(ctypes.c_ulong)
            sid_ptr = ctypes.c_void_p(ace_address + sid_offset)
            if not _advapi32.EqualSid(sid_ptr, ctypes.cast(expected, ctypes.c_void_p)):
                raise SecureConfigError("dacl grants an identity other than the owner")
        finally:
            if sd.value:
                _kernel32.LocalFree(sd)


def _establish_owner_only(path: Path) -> None:
    """Establish an owner-only permission boundary on ``path`` (dir or file)."""
    if os.name == "nt":
        _win_set_owner_only(str(path))
        return
    os.chmod(path, 0o700 if path.is_dir() else 0o600)


def _verify_owner_only(path: Path) -> None:
    """Verify the owner-only boundary; raise :class:`SecureConfigError` if it cannot be proven."""
    if os.name == "nt":
        _win_verify_owner_only(str(path))
        return
    mode = stat.S_IMODE(os.stat(path).st_mode)
    if mode & 0o077:
        raise SecureConfigError("permissions are not owner-only")


def _exclusive_write(path: Path, content: str) -> None:
    """Create ``path`` exclusively (never following an existing link) and write ``content``."""
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    flags |= getattr(os, "O_NOFOLLOW", 0)
    flags |= getattr(os, "O_BINARY", 0)
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


class LocalSecureConfigStore:
    """Default :class:`EphemeralSafeDirectoryStore`: owner-only config under a confined temp root.

    ``create`` proves the temp root resolves outside the granted repository (defeating symlink/
    junction/reparse escape), establishes and verifies an owner-only permission boundary before
    writing the single literal ``safe.directory`` value, and creates the file exclusively.
    ``remove`` proves both the file and the temp root are gone, raising otherwise.
    """

    def create(self, *, safe_root: Path) -> str:
        value = _safe_config_value(safe_root)
        temp_dir = Path(tempfile.mkdtemp(prefix="jarvis-safe-dir-"))
        try:
            real_temp = temp_dir.resolve(strict=True)
            real_repo = safe_root.resolve(strict=True)
            if _within(real_temp, real_repo) or _within(real_repo, real_temp):
                raise SecureConfigError("temporary root resolves within the repository")
            _establish_owner_only(real_temp)
            _verify_owner_only(real_temp)
            config_path = real_temp / "safe.gitconfig"
            _exclusive_write(config_path, f'[safe]\n\tdirectory = "{value}"\n')
            _establish_owner_only(config_path)
            _verify_owner_only(config_path)
            return str(config_path)
        except SecureConfigError:
            _best_effort_rmtree(temp_dir)
            raise
        except OSError as exc:
            _best_effort_rmtree(temp_dir)
            raise SecureConfigError("could not create the secure config") from exc

    def remove(self, config_path: str) -> None:
        path = Path(config_path)
        parent = path.parent
        with contextlib.suppress(OSError):
            if path.is_symlink() or path.exists():
                os.unlink(path)
        if path.exists() or path.is_symlink():
            raise SecureConfigError("ephemeral config could not be removed")
        with contextlib.suppress(OSError):
            os.rmdir(parent)
        if parent.exists():
            raise SecureConfigError("ephemeral temp root could not be removed")


def _best_effort_rmtree(path: Path) -> None:
    with contextlib.suppress(OSError):
        for child in path.glob("*"):
            with contextlib.suppress(OSError):
                child.unlink()
        os.rmdir(path)


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
        secure_config_store: EphemeralSafeDirectoryStore | None = None,
    ) -> None:
        self._runner = runner
        self._git = git_executable if git_executable is not None else resolve_git_executable()
        self._threshold_days = staleness_threshold_days
        self._env = build_git_env(self._git) if self._git else {}
        self._secure_config: EphemeralSafeDirectoryStore = (
            secure_config_store if secure_config_store is not None else LocalSecureConfigStore()
        )

    def load_activity(
        self,
        *,
        project_id: str,
        repository_root: Path,
        grant: RepositoryActivityGrant | None,
        evaluation_time: datetime,
    ) -> RepositoryActivityResult:
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
        if not requested.is_dir():
            return RepositoryActivityUnavailable(
                CODE_UNAVAILABLE_NOT_A_REPO, "repository root is not a directory"
            )
        if self._git is None:
            return RepositoryActivityUnavailable(CODE_UNAVAILABLE_NO_GIT, "git is not available")

        # Request-scoped ownership safety (Handoff 15): establish an owner-only ephemeral config
        # declaring exactly the granted root as safe.directory. Setup is fail-closed: any
        # containment/permission/serialization failure returns a typed, redacted result before
        # Git runs, and no config file remains.
        try:
            config_path = self._secure_config.create(safe_root=requested)
        except SecureConfigError:
            return RepositoryActivityUnavailable(
                CODE_UNAVAILABLE_SECURITY_SETUP, "could not establish the secure git environment"
            )
        invocation_env = {**self._env, "GIT_CONFIG_GLOBAL": config_path}
        try:
            result = self._load_activity_with_env(
                requested=requested,
                grant=grant,
                evaluation_time=evaluation_time,
                env=invocation_env,
            )
        except Exception:
            # A raised runner/unexpected error must still remove the exception and never leak.
            try:
                self._secure_config.remove(config_path)
            except SecureConfigError:
                return RepositoryActivityUnavailable(
                    CODE_UNAVAILABLE_CLEANUP_INCOMPLETE,
                    "secure git cleanup could not be verified",
                )
            return RepositoryActivityUnavailable(
                CODE_UNAVAILABLE_PROCESS_ERROR, "repository activity failed"
            )
        # Cleanup is part of the security result: a snapshot is returned only when secure
        # cleanup is proven; otherwise the result is downgraded to a typed, redacted unavailable.
        try:
            self._secure_config.remove(config_path)
        except SecureConfigError:
            return RepositoryActivityUnavailable(
                CODE_UNAVAILABLE_CLEANUP_INCOMPLETE, "secure git cleanup could not be verified"
            )
        return result

    def _load_activity_with_env(
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
