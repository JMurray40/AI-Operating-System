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
import hashlib
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
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
CODE_UNAVAILABLE_SECURITY_INTEGRITY = "unavailable_security_integrity"

_CONFIG_UNSAFE_CHARS = frozenset('"\\\n\r\x00')
_STALE_CONFIG_MAX_AGE_SECONDS = 3600.0


class SecureConfigError(Exception):
    """A request-scoped safe.directory config could not be securely created, verified, or removed.

    Raised for containment, permission, serialization, integrity, and deletion failures. The
    message is internal only and is mapped by the adapter to a redacted, typed unavailable
    result; it is never surfaced to a caller or logged with a private path.
    """


class SecureConfigCleanupError(SecureConfigError):
    """Removal of a request-scoped config or its temp root could not be proven.

    Distinct from a plain setup failure: a security exception (possibly holding the private
    canonical root) may remain on disk, so the adapter reports ``unavailable_cleanup_incomplete``
    rather than ``unavailable_security_setup``.
    """


@dataclass(frozen=True)
class _ConfigRecord:
    """The at-creation identity/content fingerprint used to detect substitution before use."""

    dev: int
    ino: int
    parent_dev: int
    parent_ino: int
    sha256: str


class EphemeralSafeDirectoryStore(Protocol):
    """Injected boundary that owns the request-scoped safe.directory config lifecycle."""

    def create(self, *, safe_root: Path) -> str:
        """Create the owner-only ephemeral config and return its path, or raise on any failure."""
        ...

    def verify(self, config_path: str) -> None:
        """Re-prove file/parent identity, exact bytes, owner, and ACL; raise on any mismatch."""
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


# The exact intended owner-only security descriptor (platform-independent predicate below).
_OWNER_ONLY_ACE_TYPE = 0  # ACCESS_ALLOWED_ACE_TYPE
_OWNER_ONLY_ACE_MASK = 0x1F01FF  # FILE_ALL_ACCESS — explicit specific rights
_OWNER_ONLY_ACE_FLAGS = 0  # no inheritance


def _check_owner_only(
    *,
    owner_matches: bool,
    dacl_protected: bool,
    ace_count: int,
    ace_type: int,
    ace_flags: int,
    ace_mask: int,
    trustee_matches: bool,
) -> None:
    """Raise :class:`SecureConfigError` unless the descriptor is exactly the owner-only form.

    Pure and platform-independent so the owner-SID, protection, ACE count/type/flags/mask, and
    trustee predicates are directly and deterministically testable without real ACLs.
    """
    if not owner_matches:
        raise SecureConfigError("owner is not the current user")
    if not dacl_protected:
        raise SecureConfigError("dacl is not protected from inheritance")
    if ace_count != 1:
        raise SecureConfigError("dacl does not grant exactly the owner")
    if ace_type != _OWNER_ONLY_ACE_TYPE:
        raise SecureConfigError("dacl contains a non-allow ace")
    if ace_flags != _OWNER_ONLY_ACE_FLAGS:
        raise SecureConfigError("ace carries inheritance flags")
    if ace_mask != _OWNER_ONLY_ACE_MASK:
        raise SecureConfigError("ace access mask is not the intended owner-only rights")
    if not trustee_matches:
        raise SecureConfigError("dacl grants an identity other than the owner")


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
    _FILE_ALL_ACCESS = 0x1F01FF  # explicit specific rights (no generic mapping ambiguity)
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
        ea.grfAccessPermissions = _FILE_ALL_ACCESS
        ea.grfAccessMode = _SET_ACCESS
        ea.grfInheritance = _NO_INHERITANCE
        ea.Trustee.TrusteeForm = _TRUSTEE_IS_SID
        ea.Trustee.TrusteeType = _TRUSTEE_IS_USER
        ea.Trustee.ptstrName = ctypes.cast(sid, ctypes.c_void_p)
        new_acl = ctypes.c_void_p()
        if _advapi32.SetEntriesInAclW(1, ctypes.byref(ea), None, ctypes.byref(new_acl)) != 0:
            raise SecureConfigError("could not build owner-only acl")
        try:
            # Set both OWNER (to the current user) and a PROTECTED owner-only DACL in one call.
            status = _advapi32.SetNamedSecurityInfoW(
                ctypes.c_wchar_p(path), _SE_FILE_OBJECT,
                _OWNER_SECURITY_INFORMATION
                | _DACL_SECURITY_INFORMATION
                | _PROTECTED_DACL_SECURITY_INFORMATION,
                ctypes.cast(sid, ctypes.c_void_p), None, new_acl, None,
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
            owner_matches = bool(owner.value) and bool(
                _advapi32.EqualSid(owner, ctypes.cast(expected, ctypes.c_void_p))
            )
            if not dacl.value:
                raise SecureConfigError("null dacl grants everyone")  # NULL DACL == full access
            control = ctypes.c_ushort(0)
            revision = ctypes.c_ulong(0)
            if not _advapi32.GetSecurityDescriptorControl(
                sd, ctypes.byref(control), ctypes.byref(revision)
            ):
                raise SecureConfigError("could not read descriptor control")
            dacl_protected = bool(control.value & _SE_DACL_PROTECTED)
            info = _ACL_SIZE_INFORMATION()
            if not _advapi32.GetAclInformation(
                dacl, ctypes.byref(info), ctypes.sizeof(info), 2  # AclSizeInformation
            ):
                raise SecureConfigError("could not read acl information")
            ace_count = int(info.AceCount)
            ace_type = ace_flags = -1
            ace_mask = 0
            trustee_matches = False
            if ace_count >= 1:
                ace_ptr = ctypes.c_void_p()
                if not _advapi32.GetAce(dacl, 0, ctypes.byref(ace_ptr)):
                    raise SecureConfigError("could not read ace")
                ace = ctypes.cast(ace_ptr, ctypes.POINTER(_ACCESS_ALLOWED_ACE)).contents
                ace_type = int(ace.Header.AceType)
                ace_flags = int(ace.Header.AceFlags)
                ace_mask = int(ace.Mask)
                ace_address = ace_ptr.value
                if ace_address is None:
                    raise SecureConfigError("could not read ace address")
                # SID begins immediately after the ACE header and the 32-bit access mask.
                sid_offset = ctypes.sizeof(_ACE_HEADER) + ctypes.sizeof(ctypes.c_ulong)
                sid_ptr = ctypes.c_void_p(ace_address + sid_offset)
                trustee_matches = bool(
                    _advapi32.EqualSid(sid_ptr, ctypes.cast(expected, ctypes.c_void_p))
                )
            _check_owner_only(
                owner_matches=owner_matches, dacl_protected=dacl_protected, ace_count=ace_count,
                ace_type=ace_type, ace_flags=ace_flags, ace_mask=ace_mask,
                trustee_matches=trustee_matches,
            )
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


def _remove_tree_proven(path: Path) -> bool:
    """Remove ``path`` and its immediate children; return whether it is provably gone."""
    with contextlib.suppress(OSError):
        for child in path.glob("*"):
            with contextlib.suppress(OSError):
                if child.is_dir() and not child.is_symlink():
                    _remove_tree_proven(child)
                else:
                    child.unlink()
        os.rmdir(path)
    return not path.exists()


def _sweep_stale_configs(base: Path) -> None:
    """Bounded recovery: remove leftover request dirs an interrupted run may have stranded."""
    now = time.time()
    with contextlib.suppress(OSError):
        for entry in base.glob("jarvis-safe-dir-*"):
            with contextlib.suppress(OSError):
                if entry.is_dir() and (now - entry.stat().st_mtime) > _STALE_CONFIG_MAX_AGE_SECONDS:
                    _remove_tree_proven(entry)


def _owner_controlled_base(real_repo: Path) -> Path:
    """Return an explicit, validated, owner-only temp base proven outside the repository.

    The base is validated (and re-hardened) *before* any per-request directory is created, so
    a hostile ambient ``TMP``/``TEMP`` pointing inside the repository fails closed without any
    repository-local write. Symlink/junction/reparse escape is defeated by ``resolve(strict)``.
    """
    try:
        real_base = Path(tempfile.gettempdir()).resolve(strict=True)
    except OSError as exc:
        raise SecureConfigError("temporary base is unavailable") from exc
    # The base must not live inside the repository (that would make the per-request dir a
    # repository write). The repository legitimately may live under the system temp base, so the
    # reverse containment is not an error; per-request-directory confinement is checked in create.
    if _within(real_base, real_repo):
        raise SecureConfigError("temporary base resolves within the repository")
    root = real_base / "jarvis-safe-root"
    with contextlib.suppress(FileExistsError):
        root.mkdir(mode=0o700)
    try:
        real_root = root.resolve(strict=True)
    except OSError as exc:
        raise SecureConfigError("controlled temporary root is unavailable") from exc
    if _within(real_root, real_repo):
        raise SecureConfigError("controlled temporary root resolves within the repository")
    _establish_owner_only(real_root)  # re-assert owner-only ownership (defeats squatting)
    _verify_owner_only(real_root)
    return real_root


def _fingerprint(path: Path, content: str) -> _ConfigRecord:
    st = path.stat()
    pst = path.parent.stat()
    return _ConfigRecord(
        dev=st.st_dev, ino=st.st_ino, parent_dev=pst.st_dev, parent_ino=pst.st_ino,
        sha256=hashlib.sha256(content.encode("utf-8")).hexdigest(),
    )


class LocalSecureConfigStore:
    """Default :class:`EphemeralSafeDirectoryStore` (Handoff 17).

    ``create`` selects an explicit owner-controlled temp base proven outside the repository,
    creates a per-request directory inside it, establishes+verifies an owner-only Windows ACL
    (owner SID == current user; one protected ACCESS_ALLOWED ACE with the exact rights, no
    inheritance) before writing exactly one literal ``safe.directory`` value, creates the file
    exclusively, and records an identity/content fingerprint. ``verify`` re-proves that
    fingerprint plus the owner/ACL at the process boundary and again before cleanup, so a
    same-owner substitution between creation and Git consumption is detected and stops the
    result. ``create`` and ``remove`` prove deletion or raise :class:`SecureConfigCleanupError`.
    """

    def __init__(self) -> None:
        self._records: dict[str, _ConfigRecord] = {}

    def create(self, *, safe_root: Path) -> str:
        value = _safe_config_value(safe_root)
        try:
            real_repo = safe_root.resolve(strict=True)
        except OSError as exc:
            raise SecureConfigError("repository root could not be resolved") from exc
        base = _owner_controlled_base(real_repo)
        _sweep_stale_configs(base)
        temp_dir = Path(tempfile.mkdtemp(prefix="jarvis-safe-dir-", dir=str(base)))
        try:
            real_temp = temp_dir.resolve(strict=True)
            if _within(real_temp, real_repo) or _within(real_repo, real_temp):
                raise SecureConfigError("temporary root resolves within the repository")
            _establish_owner_only(real_temp)
            _verify_owner_only(real_temp)
            config_path = real_temp / "safe.gitconfig"
            content = f'[safe]\n\tdirectory = "{value}"\n'
            _exclusive_write(config_path, content)
            _establish_owner_only(config_path)
            _verify_owner_only(config_path)
            self._records[str(config_path)] = _fingerprint(config_path, content)
            return str(config_path)
        except SecureConfigError:
            if not _remove_tree_proven(temp_dir):
                raise SecureConfigCleanupError("secure config artifact could not be removed") \
                    from None
            raise
        except OSError as exc:
            if not _remove_tree_proven(temp_dir):
                raise SecureConfigCleanupError("secure config artifact could not be removed") \
                    from exc
            raise SecureConfigError("could not create the secure config") from exc

    def verify(self, config_path: str) -> None:
        record = self._records.get(config_path)
        if record is None:
            raise SecureConfigError("unknown secure config")
        path = Path(config_path)
        try:
            st = path.stat()
            pst = path.parent.stat()
        except OSError as exc:
            raise SecureConfigError("secure config is not accessible") from exc
        if (st.st_dev, st.st_ino) != (record.dev, record.ino):
            raise SecureConfigError("secure config identity changed")
        if (pst.st_dev, pst.st_ino) != (record.parent_dev, record.parent_ino):
            raise SecureConfigError("secure config parent identity changed")
        try:
            data = path.read_bytes()
        except OSError as exc:
            raise SecureConfigError("secure config is not readable") from exc
        if hashlib.sha256(data).hexdigest() != record.sha256:
            raise SecureConfigError("secure config content changed")
        _verify_owner_only(path)
        _verify_owner_only(path.parent)

    def remove(self, config_path: str) -> None:
        path = Path(config_path)
        parent = path.parent
        self._records.pop(config_path, None)
        with contextlib.suppress(OSError):
            if path.is_symlink() or path.exists():
                os.unlink(path)
        if path.exists() or path.is_symlink():
            raise SecureConfigCleanupError("ephemeral config could not be removed")
        with contextlib.suppress(OSError):
            os.rmdir(parent)
        if parent.exists():
            raise SecureConfigCleanupError("ephemeral temp root could not be removed")


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

        # Request-scoped ownership safety (Handoffs 15/17): establish an owner-only ephemeral
        # config declaring exactly the granted root as safe.directory, under a controlled temp
        # root proven outside the repository. Setup is fail-closed: a proven-clean setup failure
        # returns unavailable_security_setup; a setup failure whose artifact could not be proven
        # removed returns the distinct unavailable_cleanup_incomplete.
        try:
            config_path = self._secure_config.create(safe_root=requested)
        except SecureConfigCleanupError:
            return RepositoryActivityUnavailable(
                CODE_UNAVAILABLE_CLEANUP_INCOMPLETE, "secure git cleanup could not be verified"
            )
        except SecureConfigError:
            return RepositoryActivityUnavailable(
                CODE_UNAVAILABLE_SECURITY_SETUP, "could not establish the secure git environment"
            )
        invocation_env = {**self._env, "GIT_CONFIG_GLOBAL": config_path}
        integrity_failed = False
        try:
            self._secure_config.verify(config_path)  # process boundary: pre-Git identity/ACL proof
            result: RepositoryActivityResult = self._load_activity_with_env(
                requested=requested,
                grant=grant,
                evaluation_time=evaluation_time,
                env=invocation_env,
            )
        except SecureConfigError:
            integrity_failed = True
            result = RepositoryActivityUnavailable(
                CODE_UNAVAILABLE_SECURITY_INTEGRITY, "secure git environment integrity check failed"
            )
        except Exception:  # any raised runner/unexpected error must not leak; still clean up
            integrity_failed = True
            result = RepositoryActivityUnavailable(
                CODE_UNAVAILABLE_PROCESS_ERROR, "repository activity failed"
            )
        # Re-prove identity/content/owner/ACL before cleanup: a same-owner substitution during
        # Git consumption is detected here and must stop the snapshot from being returned.
        if not integrity_failed:
            try:
                self._secure_config.verify(config_path)
            except SecureConfigError:
                result = RepositoryActivityUnavailable(
                    CODE_UNAVAILABLE_SECURITY_INTEGRITY,
                    "secure git environment integrity check failed",
                )
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
