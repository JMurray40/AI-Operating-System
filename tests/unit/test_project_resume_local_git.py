"""C9: local read-only Git adapter — injected-runner + real-Git boundary (ADR-0021, §12).

The injected ProcessRunner exercises success/timeout/overflow/malformed/redaction and the
root-escape/not-a-repo paths without an installed Git. A single real-Git test (routed to the
slow suite by its ``process_boundary`` name) proves the process boundary and that Git state is
unchanged before/after.
"""
from __future__ import annotations

import contextlib
import hashlib
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from jarvis_core.project_resume.local_git import (
    CODE_UNAVAILABLE_CLEANUP_INCOMPLETE,
    CODE_UNAVAILABLE_SECURITY_SETUP,
    LocalGitRepositoryActivityAdapter,
    LocalSecureConfigStore,
    ProcessResult,
    SecureConfigError,
    SubprocessProcessRunner,
    _cmd_head,
    _cmd_log,
    _cmd_toplevel,
    _safe_config_value,
    _verify_owner_only,
    build_git_env,
    parse_log_records,
)
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
    RepositoryActivityGrant,
    RepositoryActivitySnapshot,
)

EVAL = datetime(2026, 7, 27, tzinfo=timezone.utc)
_GIT = "/usr/bin/git"


def _grant(root: Path, *, project_id: str = "project-alpha", max_records: int = 20):
    return RepositoryActivityGrant(
        workspace_id="local", project_id=project_id, repository_root=root, max_records=max_records
    )


def _log_bytes(records: list[tuple[str, str, str, str]]) -> bytes:
    entries = [f"{oid}\x00{iso}\x00{an}\x00{s}\x00" for oid, iso, an, s in records]
    return "\n".join(entries).encode("utf-8")


class FakeRunner:
    """Routes each fixed command shape to a pre-set ProcessResult; records argv + env."""

    def __init__(self, *, toplevel: ProcessResult, head: ProcessResult, log: ProcessResult):
        self._toplevel, self._head, self._log = toplevel, head, log
        self.calls: list[list[str]] = []
        self.envs: list[dict[str, str]] = []
        # Capture the request-scoped global-config path and its content *at call time*
        # (the adapter deletes the ephemeral file after the invocation completes).
        self.global_config_paths: list[str | None] = []
        self.global_config_contents: list[str] = []

    def run(self, argv, *, cwd, env, timeout_seconds, stdout_cap_bytes, stderr_cap_bytes):
        self.calls.append(argv)
        self.envs.append(env)
        gc = env.get("GIT_CONFIG_GLOBAL")
        self.global_config_paths.append(gc)
        self.global_config_contents.append(
            Path(gc).read_text(encoding="utf-8")
            if gc and gc != os.devnull and Path(gc).is_file()
            else ""
        )
        if "--show-toplevel" in argv:
            return self._toplevel
        if "--verify" in argv:
            return self._head
        if "log" in argv:
            return self._log
        raise AssertionError(f"unexpected argv: {argv}")


def _ok_runner(root: Path) -> FakeRunner:
    return FakeRunner(
        toplevel=ProcessResult(0, str(root.resolve()).encode(), b""),
        head=ProcessResult(0, ("a" * 40).encode(), b""),
        log=ProcessResult(
            0, _log_bytes([("a" * 40, "2026-07-25T10:00:00+00:00", "Dev", "recent work")]), b""
        ),
    )


def _adapter(runner, **kw) -> LocalGitRepositoryActivityAdapter:
    return LocalGitRepositoryActivityAdapter(runner, git_executable=_GIT, **kw)


# ---------------------------------------------------------------- happy path


def test_reads_snapshot_via_injected_runner(tmp_path: Path) -> None:
    adapter = _adapter(_ok_runner(tmp_path))
    out = adapter.load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert isinstance(out, RepositoryActivitySnapshot)
    assert out.head_object_id == "a" * 40
    assert [r.subject for r in out.records] == ["recent work"]
    assert out.fingerprint


# ---------------------------------------------------------------- default-denied


def test_no_grant_denied(tmp_path: Path) -> None:
    out = _adapter(_ok_runner(tmp_path)).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=None, evaluation_time=EVAL
    )
    assert out.code == CODE_DENIED_NO_GRANT


def test_root_mismatch_denied(tmp_path: Path) -> None:
    other = tmp_path / "other"
    other.mkdir()
    out = _adapter(_ok_runner(tmp_path)).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(other),
        evaluation_time=EVAL,
    )
    assert out.code == CODE_DENIED_ROOT_MISMATCH


# ---------------------------------------------------------------- degradation paths


def test_not_a_repository_unavailable(tmp_path: Path) -> None:
    runner = FakeRunner(
        toplevel=ProcessResult(128, b"", b"fatal: not a git repository"),
        head=ProcessResult(0, b"", b""), log=ProcessResult(0, b"", b""),
    )
    out = _adapter(runner).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert out.code == CODE_UNAVAILABLE_NOT_A_REPO


def test_root_escape_denied(tmp_path: Path) -> None:
    # toplevel resolves OUTSIDE the granted root (parent / submodule / linked worktree / bare).
    escaped = tmp_path.parent
    runner = FakeRunner(
        toplevel=ProcessResult(0, str(escaped).encode(), b""),
        head=ProcessResult(0, ("a" * 40).encode(), b""), log=ProcessResult(0, b"", b""),
    )
    out = _adapter(runner).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert out.code == CODE_DENIED_ROOT_ESCAPE


def test_timeout_is_unavailable(tmp_path: Path) -> None:
    runner = FakeRunner(
        toplevel=ProcessResult(-1, b"", b"", timed_out=True),
        head=ProcessResult(0, b"", b""), log=ProcessResult(0, b"", b""),
    )
    out = _adapter(runner).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert out.code == CODE_UNAVAILABLE_TIMEOUT


def test_output_overflow_is_unavailable(tmp_path: Path) -> None:
    runner = FakeRunner(
        toplevel=ProcessResult(0, str(tmp_path.resolve()).encode(), b""),
        head=ProcessResult(0, ("a" * 40).encode(), b""),
        log=ProcessResult(0, b"x", b"", stdout_overflow=True),
    )
    out = _adapter(runner).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert out.code == CODE_UNAVAILABLE_OUTPUT_OVERFLOW


def test_malformed_records_end_to_end(tmp_path: Path) -> None:
    runner = FakeRunner(
        toplevel=ProcessResult(0, str(tmp_path.resolve()).encode(), b""),
        head=ProcessResult(0, ("a" * 40).encode(), b""),
        log=ProcessResult(0, b"deadbeef\x00not-a-date\x00Dev\x00subj\x00", b""),
    )
    out = _adapter(runner).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert out.code == CODE_MALFORMED_RECORD


def test_missing_git_is_unavailable(tmp_path: Path) -> None:
    adapter = _adapter(_ok_runner(tmp_path))
    adapter._git = None  # simulate git not installed
    out = adapter.load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert out.code == CODE_UNAVAILABLE_NO_GIT


# ---------------------------------------------------------------- redaction


def test_degradation_messages_do_not_leak_paths(tmp_path: Path) -> None:
    runner = FakeRunner(
        toplevel=ProcessResult(128, b"", f"fatal: {tmp_path}/secret".encode()),
        head=ProcessResult(0, b"", b""), log=ProcessResult(0, b"", b""),
    )
    out = _adapter(runner).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert str(tmp_path) not in out.message
    assert "secret" not in out.message


# ---------------------------------------------------------------- env allowlist


def test_env_allowlist_excludes_inherited_git_vars() -> None:
    env = build_git_env(_GIT)
    assert env["PATH"] == "/usr/bin"
    assert env["GIT_CONFIG_NOSYSTEM"] == "1"
    assert env["GIT_TERMINAL_PROMPT"] == "0"
    assert env["PAGER"] == "cat"
    assert env["LC_ALL"] == "C"
    for leaked in ("GIT_DIR", "GIT_WORK_TREE", "GIT_ASKPASS", "SSH_AUTH_SOCK",
                   "GIT_CONFIG", "HTTP_PROXY", "GIT_SSH"):
        assert leaked not in env


def test_runner_receives_allowlisted_env(tmp_path: Path) -> None:
    runner = _ok_runner(tmp_path)
    _adapter(runner).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert runner.envs, "runner was invoked"
    assert "GIT_DIR" not in runner.envs[0]
    assert runner.envs[0]["GIT_CONFIG_NOSYSTEM"] == "1"


# ---------------------------------------------------------------- request-scoped safe.directory


def test_granted_root_injects_request_scoped_safe_directory(tmp_path: Path) -> None:
    """A granted invocation carries a process-owned global config declaring exactly the
    granted root as safe, while system/ambient-global config stay untrusted."""
    runner = _ok_runner(tmp_path)
    out = _adapter(runner).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert isinstance(out, RepositoryActivitySnapshot)
    # Every invocation saw a real, process-owned global config file (not os.devnull).
    assert runner.global_config_paths and all(
        p and p != os.devnull for p in runner.global_config_paths
    )
    content = runner.global_config_contents[0]
    assert "safe" in content and "directory" in content
    # Scoped to exactly the granted root, written with forward slashes (git config safe form).
    assert tmp_path.resolve().as_posix() in content
    # The ownership opt-out is NOT the broad wildcard.
    assert "directory = *" not in content
    # Ambient system/global config remain untrusted.
    for env in runner.envs:
        assert env["GIT_CONFIG_NOSYSTEM"] == "1"


def test_safe_directory_config_is_ephemeral_and_cleaned_up(tmp_path: Path) -> None:
    runner = _ok_runner(tmp_path)
    _adapter(runner).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    seen = {p for p in runner.global_config_paths if p}
    assert seen, "a request-scoped global config was used"
    for path in seen:
        assert not Path(path).exists(), "ephemeral safe.directory config must be removed"


def test_base_env_without_root_does_not_trust_a_global_config() -> None:
    """The rootless base env (used e.g. for `git --version`) still neutralizes global config."""
    env = build_git_env(_GIT)
    assert env["GIT_CONFIG_GLOBAL"] == os.devnull
    assert env["GIT_CONFIG_NOSYSTEM"] == "1"


# ---------------------------------------------------------------- fail-closed config lifecycle


class RecordingStore:
    """A deterministic EphemeralSafeDirectoryStore double.

    Creates a real (non-hardened) config file so the injected runner can observe the env, and
    can force create/remove failures to exercise the fail-closed lifecycle without real ACLs.
    """

    def __init__(self, *, fail_create: bool = False, fail_remove: bool = False) -> None:
        self.creates = 0
        self.removes = 0
        self.fail_create = fail_create
        self.fail_remove = fail_remove
        self.created_paths: list[str] = []

    def create(self, *, safe_root: Path) -> str:
        self.creates += 1
        if self.fail_create:
            raise SecureConfigError("forced setup failure")
        d = Path(tempfile.mkdtemp(prefix="rec-safe-dir-"))
        p = d / "safe.gitconfig"
        p.write_text(
            f'[safe]\n\tdirectory = "{safe_root.resolve().as_posix()}"\n', encoding="utf-8"
        )
        self.created_paths.append(str(p))
        return str(p)

    def remove(self, config_path: str) -> None:
        self.removes += 1
        if self.fail_remove:
            raise SecureConfigError("forced cleanup failure")
        Path(config_path).unlink(missing_ok=True)
        with contextlib.suppress(OSError):
            os.rmdir(Path(config_path).parent)


class _RaisingRunner:
    def run(self, argv, *, cwd, env, timeout_seconds, stdout_cap_bytes, stderr_cap_bytes):
        raise RuntimeError("unexpected runner failure")


def test_pre_git_denials_never_create_a_config(tmp_path: Path) -> None:
    other = tmp_path / "other"
    other.mkdir()
    missing = tmp_path / "missing"
    cases = [
        (None, tmp_path),  # no grant
        (_grant(other), tmp_path),  # root mismatch
        (_grant(missing), missing),  # missing root (also mismatch-free)
    ]
    for grant, root in cases:
        store = RecordingStore()
        runner = _ok_runner(tmp_path)
        _adapter(runner, secure_config_store=store).load_activity(
            project_id="project-alpha", repository_root=root, grant=grant, evaluation_time=EVAL,
        )
        assert store.creates == 0, "no ephemeral config before grant/root/git checks pass"
        assert runner.calls == [], "git must not run"


def test_missing_git_creates_no_config(tmp_path: Path) -> None:
    store = RecordingStore()
    adapter = _adapter(_ok_runner(tmp_path), secure_config_store=store)
    adapter._git = None
    out = adapter.load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert out.code == CODE_UNAVAILABLE_NO_GIT
    assert store.creates == 0


def test_security_setup_failure_blocks_git(tmp_path: Path) -> None:
    store = RecordingStore(fail_create=True)
    runner = _ok_runner(tmp_path)
    out = _adapter(runner, secure_config_store=store).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert out.code == CODE_UNAVAILABLE_SECURITY_SETUP
    assert runner.calls == [], "git must never run when the secure config cannot be established"


def test_cleanup_failure_downgrades_snapshot_to_unavailable(tmp_path: Path) -> None:
    store = RecordingStore(fail_remove=True)
    out = _adapter(_ok_runner(tmp_path), secure_config_store=store).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert not isinstance(out, RepositoryActivitySnapshot)
    assert out.code == CODE_UNAVAILABLE_CLEANUP_INCOMPLETE
    assert store.creates == 1 and store.removes == 1


def test_success_removes_config_before_returning(tmp_path: Path) -> None:
    store = RecordingStore()
    out = _adapter(_ok_runner(tmp_path), secure_config_store=store).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert isinstance(out, RepositoryActivitySnapshot)
    assert store.removes == 1
    assert store.created_paths and not Path(store.created_paths[0]).exists()


def test_raised_runner_exception_removes_config(tmp_path: Path) -> None:
    store = RecordingStore()
    out = _adapter(_RaisingRunner(), secure_config_store=store).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert out.code == CODE_UNAVAILABLE_PROCESS_ERROR
    assert store.removes == 1
    assert store.created_paths and not Path(store.created_paths[0]).exists()


@pytest.mark.parametrize(
    "runner_factory",
    [
        lambda p: FakeRunner(  # not-a-repository
            toplevel=ProcessResult(128, b"", b"fatal"),
            head=ProcessResult(0, b"", b""), log=ProcessResult(0, b"", b""),
        ),
        lambda p: FakeRunner(  # root escape
            toplevel=ProcessResult(0, str(p.parent).encode(), b""),
            head=ProcessResult(0, ("a" * 40).encode(), b""), log=ProcessResult(0, b"", b""),
        ),
        lambda p: FakeRunner(  # timeout
            toplevel=ProcessResult(-1, b"", b"", timed_out=True),
            head=ProcessResult(0, b"", b""), log=ProcessResult(0, b"", b""),
        ),
        lambda p: FakeRunner(  # overflow
            toplevel=ProcessResult(0, str(p.resolve()).encode(), b""),
            head=ProcessResult(0, ("a" * 40).encode(), b""),
            log=ProcessResult(0, b"x", b"", stdout_overflow=True),
        ),
        lambda p: FakeRunner(  # malformed log
            toplevel=ProcessResult(0, str(p.resolve()).encode(), b""),
            head=ProcessResult(0, ("a" * 40).encode(), b""),
            log=ProcessResult(0, b"deadbeef\x00not-a-date\x00Dev\x00s\x00", b""),
        ),
    ],
)
def test_every_degradation_path_removes_the_config(tmp_path: Path, runner_factory) -> None:
    store = RecordingStore()
    out = _adapter(runner_factory(tmp_path), secure_config_store=store).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert not isinstance(out, RepositoryActivitySnapshot)
    assert store.creates == 1 and store.removes == 1
    assert store.created_paths and not Path(store.created_paths[0]).exists()


def test_command_arrays_never_carry_safe_directory(tmp_path: Path) -> None:
    """The fix is environment-only: safe.directory never enters an argv (fixed shapes intact)."""
    runner = _ok_runner(tmp_path)
    _adapter(runner, secure_config_store=RecordingStore()).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    for argv in runner.calls:
        assert not any("safe.directory" in part for part in argv)


# ---------------------------------------------------------------- config serialization


def test_safe_config_value_accepts_plain_root(tmp_path: Path) -> None:
    assert _safe_config_value(tmp_path) == tmp_path.resolve().as_posix()


@pytest.mark.parametrize(
    "raw",
    [
        "C:/repo/with\nnewline",
        'C:/repo/with"quote',
        "C:/repo/*",
        "C:/repo/**",
        "*",
        "C:/repo/with\x00nul",
    ],
)
def test_safe_config_value_rejects_adversarial_roots(raw: str) -> None:
    with pytest.raises(SecureConfigError):
        _safe_config_value(Path(raw))


# ---------------------------------------------------------------- command shapes


def test_only_three_fixed_command_shapes(tmp_path: Path) -> None:
    runner = _ok_runner(tmp_path)
    _adapter(runner).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert len(runner.calls) == 3
    for argv in runner.calls:
        assert argv[0] == _GIT
        assert "-C" in argv  # always operates via -C <root>, never a cwd-relative guess


def test_log_command_shape_is_exact() -> None:
    argv = _cmd_log(_GIT, Path("/repo"), 20)
    assert argv[-3:] == ["--pretty=format:%H%x00%cI%x00%an%x00%s%x00", "--max-count=20", "HEAD"]
    assert "--first-parent" in argv
    assert "--date=iso-strict" in argv
    assert "--no-color" in argv


def test_toplevel_and_head_shapes() -> None:
    assert _cmd_toplevel(_GIT, Path("/r"))[-2:] == ["rev-parse", "--show-toplevel"]
    assert _cmd_head(_GIT, Path("/r"))[-3:] == ["rev-parse", "--verify", "HEAD"]


# ---------------------------------------------------------------- parser edge cases


def test_parser_multiple_records_and_trailing_newline() -> None:
    data = _log_bytes([
        ("a" * 40, "2026-07-25T10:00:00+00:00", "Dev", "one"),
        ("b" * 40, "2026-07-20T10:00:00+00:00", "Dev", "two"),
    ])
    records = parse_log_records(data)
    assert records is not None
    assert [r.object_id for r in records] == ["a" * 40, "b" * 40]
    assert [r.subject for r in records] == ["one", "two"]


def test_parser_empty_is_empty_tuple() -> None:
    assert parse_log_records(b"") == ()


def test_parser_bad_field_count_is_malformed() -> None:
    assert parse_log_records(b"a\x00b\x00c\x00") is None  # 3 fields


def test_parser_bad_object_id_is_malformed() -> None:
    assert parse_log_records(b"zzz\x002026-07-25T10:00:00+00:00\x00Dev\x00s\x00") is None


def test_parser_invalid_utf8_is_malformed() -> None:
    assert parse_log_records(b"\xff\xfe\x00x\x00y\x00z\x00") is None


# ---------------------------------------------------------------- real git (slow suite)


def _git_dir_inventory(git_dir: Path) -> dict[str, str]:
    inv: dict[str, str] = {}
    for name in ("HEAD", "config", "index"):
        p = git_dir / name
        if p.is_file():
            inv[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    refs = git_dir / "refs"
    if refs.is_dir():
        inv["refs"] = ",".join(sorted(str(x.relative_to(refs)) for x in refs.rglob("*")))
    return inv


def test_real_git_process_boundary_reads_and_does_not_mutate(tmp_path: Path) -> None:
    git = shutil.which("git")
    if not git:
        pytest.skip("git not installed")
    repo = tmp_path / "repo"
    repo.mkdir()

    def _git(*args: str) -> None:
        subprocess.run(
            [git, "-c", "user.name=Dev", "-c", "user.email=dev@example.com",
             "-c", "commit.gpgsign=false", "-C", str(repo), *args],
            check=True, capture_output=True,
        )

    _git("init", "-q")
    (repo / "f.txt").write_text("hello\n", encoding="utf-8")
    _git("add", "f.txt")
    _git("commit", "-q", "-m", "initial commit")

    git_dir = repo / ".git"
    before = _git_dir_inventory(git_dir)

    adapter = LocalGitRepositoryActivityAdapter(SubprocessProcessRunner(), git_executable=git)
    out = adapter.load_activity(
        project_id="project-alpha", repository_root=repo, grant=_grant(repo),
        evaluation_time=datetime.now(timezone.utc),
    )
    assert isinstance(out, RepositoryActivitySnapshot)
    assert len(out.records) == 1
    assert out.records[0].subject == "initial commit"
    assert len(out.head_object_id) in (40, 64)

    after = _git_dir_inventory(git_dir)
    assert before == after  # read-only: HEAD/config/index/refs unchanged


def _init_repo(git: str, repo: Path) -> None:
    repo.mkdir()

    def _git(*args: str) -> None:
        subprocess.run(
            [git, "-c", "user.name=Dev", "-c", "user.email=dev@example.com",
             "-c", "commit.gpgsign=false", "-C", str(repo), *args],
            check=True, capture_output=True,
        )

    _git("init", "-q")
    (repo / "f.txt").write_text("hello\n", encoding="utf-8")
    _git("add", "f.txt")
    _git("commit", "-q", "-m", "initial commit")


class _AssumeDifferentOwnerRunner(SubprocessProcessRunner):
    """Forces Git's dubious-ownership path (owner != caller) via its test hook, and can
    optionally override the request-scoped global config back to devnull to model the
    pre-fix rejection."""

    def __init__(self, *, drop_safe_directory: bool = False) -> None:
        self._drop = drop_safe_directory

    def run(self, argv, *, cwd, env, timeout_seconds, stdout_cap_bytes, stderr_cap_bytes):
        forced = {**env, "GIT_TEST_ASSUME_DIFFERENT_OWNER": "1"}
        if self._drop:
            forced["GIT_CONFIG_GLOBAL"] = os.devnull
        return super().run(
            argv, cwd=cwd, env=forced, timeout_seconds=timeout_seconds,
            stdout_cap_bytes=stdout_cap_bytes, stderr_cap_bytes=stderr_cap_bytes,
        )


def test_real_git_process_boundary_granted_root_readable_under_dubious_ownership(
    tmp_path: Path,
) -> None:
    """Ownership-safe success path: a repository the runtime identity does not own is still
    readable because the invocation declares exactly the granted root as safe."""
    git = shutil.which("git")
    if not git:
        pytest.skip("git not installed")
    repo = tmp_path / "repo"
    _init_repo(git, repo)
    git_dir = repo / ".git"
    before = _git_dir_inventory(git_dir)

    adapter = LocalGitRepositoryActivityAdapter(
        _AssumeDifferentOwnerRunner(), git_executable=git
    )
    out = adapter.load_activity(
        project_id="project-alpha", repository_root=repo, grant=_grant(repo),
        evaluation_time=datetime.now(timezone.utc),
    )
    assert isinstance(out, RepositoryActivitySnapshot)
    assert out.records[0].subject == "initial commit"
    # Ownership handling must not mutate the repository or its config.
    assert _git_dir_inventory(git_dir) == before
    cfg = (git_dir / "config").read_text(encoding="utf-8")
    assert "safe" not in cfg and "directory" not in cfg  # never persisted to repo config


def test_real_git_process_boundary_dubious_ownership_without_grant_scope_is_rejected(
    tmp_path: Path,
) -> None:
    """Rejection path: with the request-scoped safe.directory removed, a non-owned repo is
    still rejected as not-a-repository — the ownership check is not globally disabled."""
    git = shutil.which("git")
    if not git:
        pytest.skip("git not installed")
    repo = tmp_path / "repo"
    _init_repo(git, repo)

    adapter = LocalGitRepositoryActivityAdapter(
        _AssumeDifferentOwnerRunner(drop_safe_directory=True), git_executable=git
    )
    out = adapter.load_activity(
        project_id="project-alpha", repository_root=repo, grant=_grant(repo),
        evaluation_time=datetime.now(timezone.utc),
    )
    assert out.code == CODE_UNAVAILABLE_NOT_A_REPO


# ------------------------------------------------- real secure-config store (process boundary)


def test_secure_store_config_parses_to_exactly_one_literal(tmp_path: Path) -> None:
    """Git parses the generated config to exactly one literal safe.directory == granted root."""
    git = shutil.which("git")
    if not git:
        pytest.skip("git not installed")
    repo = tmp_path / "repo"
    repo.mkdir()
    store = LocalSecureConfigStore()
    path = store.create(safe_root=repo)
    try:
        listed = subprocess.run(
            [git, "config", "--file", path, "--list"],
            capture_output=True, text=True, check=True,
        )
        entries = [line for line in listed.stdout.splitlines() if line.strip()]
        assert entries == [f"safe.directory={repo.resolve().as_posix()}"]
        values = subprocess.run(
            [git, "config", "--file", path, "--get-all", "safe.directory"],
            capture_output=True, text=True, check=True,
        )
        got = [line for line in values.stdout.splitlines() if line.strip()]
        assert got == [repo.resolve().as_posix()]
    finally:
        store.remove(path)
    assert not Path(path).exists()


def test_secure_store_establishes_and_verifies_owner_only_permissions(tmp_path: Path) -> None:
    if os.name != "nt":
        pytest.skip("Windows ACL boundary is the supported reference platform")
    repo = tmp_path / "repo"
    repo.mkdir()
    store = LocalSecureConfigStore()
    path = store.create(safe_root=repo)
    try:
        # create() already verified; re-verify independently that the property holds on disk.
        _verify_owner_only(Path(path))
        _verify_owner_only(Path(path).parent)
    finally:
        store.remove(path)


def test_secure_store_rejects_temp_root_resolving_into_repository(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    sneaky = repo / "sneaky-temp"

    def _fake_mkdtemp(*args: object, **kwargs: object) -> str:
        sneaky.mkdir()
        return str(sneaky)

    monkeypatch.setattr(
        "jarvis_core.project_resume.local_git.tempfile.mkdtemp", _fake_mkdtemp
    )
    store = LocalSecureConfigStore()
    with pytest.raises(SecureConfigError):
        store.create(safe_root=repo)
    assert not sneaky.exists(), "the rejected temp root must be cleaned up"
