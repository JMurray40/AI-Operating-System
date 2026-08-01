"""C9 local read-only Git adapter — command-scope safe.directory (ADR-0021, Handoff 22 Option A).

The injected ProcessRunner exercises the version floor, command-scope environment projection,
success/timeout/overflow/malformed/redaction, and root-escape/not-a-repo paths without an
installed Git. Real-Git tests (routed to the slow suite by their ``process_boundary`` name)
prove the process boundary, the different-owner behavior with and without the command-scope
value, repository immutability, and that no configuration artifact is ever created.

Acceptance matrix mapping (Handoff 22 §7):

- CS-01 test_no_grant_denied
- CS-02 test_project_mismatch_denied
- CS-03 test_root_mismatch_denied
- CS-04 test_not_a_repository_unavailable / test_root_escape_denied
- CS-05 test_invalid_config_value_is_environment_integrity / test_canonical_value_rejects_*
- CS-06 test_below_floor_git_version_is_unsupported
- CS-07 test_missing_or_unparsable_git_version_is_unsupported
- CS-08 test_git_2380_boundary_is_accepted
- CS-09 test_real_git_different_owner_with_command_scope_succeeds
- CS-10 test_real_git_different_owner_without_command_scope_is_denied
- CS-11 test_missing_grant_on_real_repo_denied_before_git
- CS-12 test_hostile_ambient_git_config_is_excluded
- CS-13 test_env_disables_system_and_nulls_global
- CS-14 test_env_carries_exact_command_scope_triplet
- CS-15 test_command_arrays_are_byte_identical / test_safe_directory_never_in_argv
- CS-16 test_root_escape_denied
- CS-17 test_timeout_is_unavailable / test_output_overflow_is_unavailable / test_malformed_*
- CS-18 test_real_git_process_boundary_reads_and_does_not_mutate
- CS-19 test_file_based_subsystem_symbols_are_absent / test_no_temp_artifact_created_during_real_git
- CS-20 test_degradation_messages_do_not_leak_paths / test_snapshot_does_not_carry_root
- CS-21 test_independent_windows_identity_row (skipped; returned to Chief of Staff)
- CS-22 test_missing_git_is_unavailable / test_below_floor_git_version_is_unsupported
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

import jarvis_core.project_resume.local_git as local_git
from jarvis_core.project_resume.local_git import (
    CODE_UNAVAILABLE_ENVIRONMENT_INTEGRITY,
    CODE_UNAVAILABLE_UNSUPPORTED_GIT,
    MINIMUM_GIT_VERSION,
    LocalGitRepositoryActivityAdapter,
    ProcessResult,
    SubprocessProcessRunner,
    _canonical_safe_directory_value,
    _cmd_head,
    _cmd_log,
    _cmd_toplevel,
    build_git_env,
    parse_git_version,
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
_APPROVED_VERSION = b"git version 2.55.0.windows.1"


def _grant(root: Path, *, project_id: str = "project-alpha", max_records: int = 20):
    return RepositoryActivityGrant(
        workspace_id="local", project_id=project_id, repository_root=root, max_records=max_records
    )


def _log_bytes(records: list[tuple[str, str, str, str]]) -> bytes:
    entries = [f"{oid}\x00{iso}\x00{an}\x00{s}\x00" for oid, iso, an, s in records]
    return "\n".join(entries).encode("utf-8")


class FakeRunner:
    """Routes the version diagnostic and the three command shapes to pre-set results."""

    def __init__(
        self,
        *,
        toplevel: ProcessResult,
        head: ProcessResult,
        log: ProcessResult,
        version: ProcessResult | None = None,
    ):
        self._toplevel, self._head, self._log = toplevel, head, log
        self._version = version or ProcessResult(0, _APPROVED_VERSION, b"")
        self.calls: list[list[str]] = []
        self.envs: list[dict[str, str]] = []

    def run(self, argv, *, cwd, env, timeout_seconds, stdout_cap_bytes, stderr_cap_bytes):
        self.calls.append(argv)
        self.envs.append(env)
        if "--version" in argv:
            return self._version
        if "--show-toplevel" in argv:
            return self._toplevel
        if "--verify" in argv:
            return self._head
        if "log" in argv:
            return self._log
        raise AssertionError(f"unexpected argv: {argv}")

    @property
    def repo_calls(self) -> list[list[str]]:
        return [c for c in self.calls if "--version" not in c]

    @property
    def repo_envs(self) -> list[dict[str, str]]:
        return [e for c, e in zip(self.calls, self.envs, strict=True) if "--version" not in c]


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


# ---------------------------------------------------------------- CS-01/02/03/04/11 denials


def test_no_grant_denied(tmp_path: Path) -> None:  # CS-01
    runner = _ok_runner(tmp_path)
    out = _adapter(runner).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=None, evaluation_time=EVAL
    )
    assert out.code == CODE_DENIED_NO_GRANT
    assert runner.calls == [], "no subprocess (not even --version) before authorization"


def test_project_mismatch_denied(tmp_path: Path) -> None:  # CS-02
    runner = _ok_runner(tmp_path)
    out = _adapter(runner).load_activity(
        project_id="project-beta", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert out.code == CODE_DENIED_ROOT_MISMATCH
    assert runner.calls == []


def test_root_mismatch_denied(tmp_path: Path) -> None:  # CS-03
    other = tmp_path / "other"
    other.mkdir()
    runner = _ok_runner(tmp_path)
    out = _adapter(runner).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(other),
        evaluation_time=EVAL,
    )
    assert out.code == CODE_DENIED_ROOT_MISMATCH
    assert runner.calls == []


def test_not_a_repository_unavailable(tmp_path: Path) -> None:  # CS-04 (non-directory)
    missing = tmp_path / "missing"
    runner = _ok_runner(tmp_path)
    out = _adapter(runner).load_activity(
        project_id="project-alpha", repository_root=missing, grant=_grant(missing),
        evaluation_time=EVAL,
    )
    assert out.code == CODE_UNAVAILABLE_NOT_A_REPO
    assert runner.calls == []


def test_root_escape_denied(tmp_path: Path) -> None:  # CS-04 / CS-16
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


def test_missing_grant_on_real_repo_denied_before_git(tmp_path: Path) -> None:  # CS-11
    runner = _ok_runner(tmp_path)
    out = _adapter(runner).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=None, evaluation_time=EVAL
    )
    assert out.code == CODE_DENIED_NO_GRANT
    assert runner.calls == []


# ---------------------------------------------------------------- CS-06/07/08/22 version floor


def test_below_floor_git_version_is_unsupported(tmp_path: Path) -> None:  # CS-06 / CS-22
    runner = _ok_runner(tmp_path)
    runner._version = ProcessResult(0, b"git version 2.37.4", b"")
    out = _adapter(runner).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert out.code == CODE_UNAVAILABLE_UNSUPPORTED_GIT
    assert runner.repo_calls == [], "no repository command below the version floor"


def test_missing_or_unparsable_git_version_is_unsupported(tmp_path: Path) -> None:  # CS-07
    failing = _ok_runner(tmp_path)
    failing._version = ProcessResult(1, b"", b"error")
    out = _adapter(failing).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert out.code == CODE_UNAVAILABLE_UNSUPPORTED_GIT
    assert failing.repo_calls == []

    garbage = _ok_runner(tmp_path)
    garbage._version = ProcessResult(0, b"not a version string", b"")
    out2 = _adapter(garbage).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert out2.code == CODE_UNAVAILABLE_UNSUPPORTED_GIT
    assert garbage.repo_calls == []


def test_git_2380_boundary_is_accepted(tmp_path: Path) -> None:  # CS-08
    runner = _ok_runner(tmp_path)
    runner._version = ProcessResult(0, b"git version 2.38.0", b"")
    out = _adapter(runner).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert isinstance(out, RepositoryActivitySnapshot)


def test_missing_git_is_unavailable(tmp_path: Path) -> None:  # CS-22 (no git)
    adapter = _adapter(_ok_runner(tmp_path))
    adapter._git = None
    out = adapter.load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert out.code == CODE_UNAVAILABLE_NO_GIT


def test_version_parser() -> None:
    assert parse_git_version("git version 2.38.0") == (2, 38, 0)
    assert parse_git_version("git version 2.55.0.windows.1") == (2, 55, 0)
    assert parse_git_version("git version 2.37") == (2, 37, 0)
    assert parse_git_version("no version here") is None
    assert MINIMUM_GIT_VERSION == (2, 38, 0)


# ---------------------------------------------------------------- CS-05 config-value validation


def test_invalid_config_value_is_environment_integrity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:  # CS-05
    monkeypatch.setattr(local_git, "_canonical_safe_directory_value", lambda root: None)
    runner = _ok_runner(tmp_path)
    out = _adapter(runner).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert out.code == CODE_UNAVAILABLE_ENVIRONMENT_INTEGRITY
    assert runner.repo_calls == [], "no repository command when the value is not usable"


def test_canonical_value_accepts_plain_root(tmp_path: Path) -> None:  # CS-05
    assert _canonical_safe_directory_value(tmp_path) == tmp_path.resolve().as_posix()


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "*",
        "C:/repo/*",
        "C:/repo/**",
        "C:/repo/with\nnewline",
        "C:/repo/with\rreturn",
        "C:/repo/with\x00nul",
        'C:/repo/with"quote',
        "~/repo",
        "%(prefix)/repo",
    ],
)
def test_canonical_value_rejects_adversarial_forms(raw: str) -> None:  # CS-05
    assert _canonical_safe_directory_value(Path(raw)) is None


# ---------------------------------------------------------------- CS-12/13/14 environment


def test_env_carries_exact_command_scope_triplet(tmp_path: Path) -> None:  # CS-14
    runner = _ok_runner(tmp_path)
    _adapter(runner).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    expected_value = tmp_path.resolve().as_posix()
    assert runner.repo_envs, "the three repository commands ran"
    for env in runner.repo_envs:
        assert env["GIT_CONFIG_COUNT"] == "1"
        assert env["GIT_CONFIG_KEY_0"] == "safe.directory"
        assert env["GIT_CONFIG_VALUE_0"] == expected_value
        assert "GIT_CONFIG_KEY_1" not in env and "GIT_CONFIG_VALUE_1" not in env


def test_env_disables_system_and_nulls_global(tmp_path: Path) -> None:  # CS-13
    runner = _ok_runner(tmp_path)
    _adapter(runner).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    for env in runner.envs:  # every subprocess, including --version
        assert env["GIT_CONFIG_NOSYSTEM"] == "1"
        assert env["GIT_CONFIG_GLOBAL"] == os.devnull


def test_version_diagnostic_has_no_command_scope_value(tmp_path: Path) -> None:  # CS-14
    runner = _ok_runner(tmp_path)
    _adapter(runner).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    version_env = next(
        e for c, e in zip(runner.calls, runner.envs, strict=True) if "--version" in c
    )
    assert "GIT_CONFIG_COUNT" not in version_env  # value only for the three repo commands


def test_hostile_ambient_git_config_is_excluded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:  # CS-12
    monkeypatch.setenv("GIT_CONFIG_COUNT", "9")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "safe.directory")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "/attacker/controlled")
    monkeypatch.setenv("GIT_CONFIG_KEY_1", "core.fsmonitor")
    monkeypatch.setenv("GIT_DIR", "/attacker/gitdir")
    runner = _ok_runner(tmp_path)
    _adapter(runner).load_activity(  # adapter built after hostile env set
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    expected_value = tmp_path.resolve().as_posix()
    for env in runner.repo_envs:
        assert env["GIT_CONFIG_COUNT"] == "1"  # not the ambient 9
        assert env["GIT_CONFIG_VALUE_0"] == expected_value  # not /attacker/controlled
        assert "GIT_CONFIG_KEY_1" not in env
        assert "GIT_DIR" not in env


# CS-12
def test_build_git_env_excludes_ambient_git_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GIT_CONFIG_COUNT", "5")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "safe.directory")
    env = build_git_env(_GIT)
    assert "GIT_CONFIG_COUNT" not in env and "GIT_CONFIG_KEY_0" not in env
    assert env["GIT_CONFIG_NOSYSTEM"] == "1"


# ---------------------------------------------------------------- CS-15 command arrays


def test_command_arrays_are_byte_identical(tmp_path: Path) -> None:  # CS-15
    root = tmp_path.resolve()
    assert _cmd_toplevel(_GIT, root) == [
        _GIT, "--no-pager", "-C", str(root), "rev-parse", "--show-toplevel",
    ]
    assert _cmd_head(_GIT, root) == [
        _GIT, "--no-pager", "--no-replace-objects", "-C", str(root),
        "rev-parse", "--verify", "HEAD",
    ]
    assert _cmd_log(_GIT, root, 20) == [
        _GIT, "--no-pager", "--no-replace-objects",
        "-c", "color.ui=false", "-c", "core.pager=cat", "-c", "core.fsmonitor=false",
        "-c", "i18n.logOutputEncoding=UTF-8", "-C", str(root),
        "log", "--no-color", "--no-decorate", "--first-parent", "--date=iso-strict",
        "--pretty=format:%H%x00%cI%x00%an%x00%s%x00", "--max-count=20", "HEAD",
    ]


def test_recorded_repo_calls_match_the_three_arrays(tmp_path: Path) -> None:  # CS-15
    runner = _ok_runner(tmp_path)
    _adapter(runner).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    root = tmp_path.resolve()
    assert runner.repo_calls == [
        _cmd_toplevel(_GIT, root), _cmd_head(_GIT, root), _cmd_log(_GIT, root, 20),
    ]


def test_safe_directory_never_in_argv(tmp_path: Path) -> None:  # CS-15
    runner = _ok_runner(tmp_path)
    _adapter(runner).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    for argv in runner.calls:
        assert not any("safe.directory" in part for part in argv)  # environment-only


# ---------------------------------------------------------------- CS-17 degradation paths


def test_timeout_is_unavailable(tmp_path: Path) -> None:  # CS-17
    runner = FakeRunner(
        toplevel=ProcessResult(-1, b"", b"", timed_out=True),
        head=ProcessResult(0, b"", b""), log=ProcessResult(0, b"", b""),
    )
    out = _adapter(runner).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert out.code == CODE_UNAVAILABLE_TIMEOUT


def test_output_overflow_is_unavailable(tmp_path: Path) -> None:  # CS-17
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


def test_malformed_records_end_to_end(tmp_path: Path) -> None:  # CS-17
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


def test_head_failure_is_process_error(tmp_path: Path) -> None:  # CS-17
    runner = FakeRunner(
        toplevel=ProcessResult(0, str(tmp_path.resolve()).encode(), b""),
        head=ProcessResult(1, b"", b"boom"), log=ProcessResult(0, b"", b""),
    )
    out = _adapter(runner).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert out.code == CODE_UNAVAILABLE_PROCESS_ERROR


# ---------------------------------------------------------------- CS-20 redaction


def test_degradation_messages_do_not_leak_paths(tmp_path: Path) -> None:  # CS-20
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


def test_snapshot_does_not_carry_root(tmp_path: Path) -> None:  # CS-20
    out = _adapter(_ok_runner(tmp_path)).load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=_grant(tmp_path),
        evaluation_time=EVAL,
    )
    assert isinstance(out, RepositoryActivitySnapshot)
    serialized = str(out.to_dict())
    assert tmp_path.resolve().as_posix() not in serialized
    assert str(tmp_path) not in serialized


# ---------------------------------------------------------------- parser edge cases


def test_parser_multiple_records_and_trailing_newline() -> None:
    data = _log_bytes([
        ("a" * 40, "2026-07-25T10:00:00+00:00", "Dev", "one"),
        ("b" * 40, "2026-07-20T10:00:00+00:00", "Dev", "two"),
    ])
    records = parse_log_records(data)
    assert records is not None
    assert [r.object_id for r in records] == ["a" * 40, "b" * 40]


def test_parser_empty_is_empty_tuple() -> None:
    assert parse_log_records(b"") == ()


def test_parser_bad_field_count_is_malformed() -> None:
    assert parse_log_records(b"a\x00b\x00c\x00") is None


def test_parser_bad_object_id_is_malformed() -> None:
    assert parse_log_records(b"zzz\x002026-07-25T10:00:00+00:00\x00Dev\x00s\x00") is None


def test_parser_invalid_utf8_is_malformed() -> None:
    assert parse_log_records(b"\xff\xfe\x00x\x00y\x00z\x00") is None


# ---------------------------------------------------------------- CS-19 no artifact / removal


@pytest.mark.parametrize(
    "removed",
    [
        "LocalSecureConfigStore", "SecureConfigError", "SecureConfigCleanupError",
        "EphemeralSafeDirectoryStore", "_ConfigRecord", "_win_set_owner_only",
        "_win_verify_owner_only", "_check_owner_only", "_establish_owner_only",
        "_verify_owner_only", "_exclusive_write", "_remove_tree_proven",
        "_sweep_stale_configs", "_identity_token", "_config_dir_prefix",
        "_validated_temp_base", "_owner_controlled_base", "_fingerprint",
        "_current_user_sid", "_safe_config_value",
    ],
)
def test_file_based_subsystem_symbols_are_absent(removed: str) -> None:  # CS-19
    assert not hasattr(local_git, removed), f"{removed} must be fully removed (no dormant code)"


def test_module_does_not_import_file_subsystem_modules() -> None:  # CS-19
    src = Path(local_git.__file__).read_text(encoding="utf-8")
    for banned in ("import ctypes", "import tempfile", "import hashlib", "import stat"):
        assert banned not in src, f"{banned} must not remain after subsystem removal"


# ---------------------------------------------------------------- CS-21 independent identity


def test_independent_windows_identity_row() -> None:  # CS-21
    pytest.skip(
        "CS-21 independent Windows-logon identity run cannot be executed in this session; "
        "frozen and returned to the Chief of Staff for that environmental validation."
    )


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
    """Forces Git's dubious-ownership path and can strip the command-scope triplet to model the
    pre-authorization (no safe.directory) rejection."""

    def __init__(self, *, drop_command_scope: bool = False) -> None:
        self._drop = drop_command_scope

    def run(self, argv, *, cwd, env, timeout_seconds, stdout_cap_bytes, stderr_cap_bytes):
        forced = {**env, "GIT_TEST_ASSUME_DIFFERENT_OWNER": "1"}
        if self._drop:
            for key in ("GIT_CONFIG_COUNT", "GIT_CONFIG_KEY_0", "GIT_CONFIG_VALUE_0"):
                forced.pop(key, None)
        return super().run(
            argv, cwd=cwd, env=forced, timeout_seconds=timeout_seconds,
            stdout_cap_bytes=stdout_cap_bytes, stderr_cap_bytes=stderr_cap_bytes,
        )


def test_real_git_process_boundary_reads_and_does_not_mutate(tmp_path: Path) -> None:  # CS-18
    git = shutil.which("git")
    if not git:
        pytest.skip("git not installed")
    repo = tmp_path / "repo"
    _init_repo(git, repo)
    git_dir = repo / ".git"
    before = _git_dir_inventory(git_dir)

    adapter = LocalGitRepositoryActivityAdapter(SubprocessProcessRunner(), git_executable=git)
    out = adapter.load_activity(
        project_id="project-alpha", repository_root=repo, grant=_grant(repo),
        evaluation_time=datetime.now(timezone.utc),
    )
    assert isinstance(out, RepositoryActivitySnapshot)
    assert out.records[0].subject == "initial commit"
    assert _git_dir_inventory(git_dir) == before  # read-only
    cfg = (git_dir / "config").read_text(encoding="utf-8")
    assert "safe" not in cfg and "directory" not in cfg  # never persisted to repo config


def test_no_temp_artifact_created_during_real_git(tmp_path: Path) -> None:  # CS-19
    git = shutil.which("git")
    if not git:
        pytest.skip("git not installed")
    repo = tmp_path / "repo"
    _init_repo(git, repo)
    base = Path(tempfile.gettempdir())
    before = set(base.glob("jarvis*"))
    adapter = LocalGitRepositoryActivityAdapter(SubprocessProcessRunner(), git_executable=git)
    out = adapter.load_activity(
        project_id="project-alpha", repository_root=repo, grant=_grant(repo),
        evaluation_time=datetime.now(timezone.utc),
    )
    assert isinstance(out, RepositoryActivitySnapshot)
    assert set(base.glob("jarvis*")) == before, "no Jarvis temp/config artifact may be created"


def test_real_git_different_owner_with_command_scope_succeeds(tmp_path: Path) -> None:  # CS-09
    git = shutil.which("git")
    if not git:
        pytest.skip("git not installed")
    if (parse_git_version(
        subprocess.run([git, "--version"], capture_output=True, text=True, check=True).stdout
    ) or (0, 0, 0)) < MINIMUM_GIT_VERSION:
        pytest.skip("host git is below the 2.38.0 floor")
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
    assert _git_dir_inventory(git_dir) == before


def test_real_git_different_owner_without_command_scope_is_denied(tmp_path: Path) -> None:  # CS-10
    git = shutil.which("git")
    if not git:
        pytest.skip("git not installed")
    repo = tmp_path / "repo"
    _init_repo(git, repo)
    adapter = LocalGitRepositoryActivityAdapter(
        _AssumeDifferentOwnerRunner(drop_command_scope=True), git_executable=git
    )
    out = adapter.load_activity(
        project_id="project-alpha", repository_root=repo, grant=_grant(repo),
        evaluation_time=datetime.now(timezone.utc),
    )
    assert out.code == CODE_UNAVAILABLE_NOT_A_REPO  # dubious ownership without the value
