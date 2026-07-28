"""C8: repository-activity port + deterministic fixture adapter (ADR-0021).

The fixture adapter runs without Git and enforces the default-denied, grant-bound, root-matched
contract the Git adapter (C9) must share. Snapshots sort/cap/fingerprint deterministically and
staleness is computed from the explicit evaluation time.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from jarvis_core.project_resume.repository_activity import (
    CODE_DENIED_NO_GRANT,
    CODE_DENIED_ROOT_MISMATCH,
    CODE_UNAVAILABLE_NOT_A_REPO,
    CODE_UNAVAILABLE_OUTPUT_OVERFLOW,
    FixtureRepositoryActivityAdapter,
    RepositoryActivityFixture,
    RepositoryActivityGrant,
    RepositoryActivitySnapshot,
    RepositoryActivityStale,
    RepositoryActivityUnavailable,
    RepositoryCommitRecord,
    build_snapshot,
    is_stale,
)

EVAL = datetime(2026, 7, 27, tzinfo=timezone.utc)


def _record(
    oid: str, iso: str, author: str = "Dev", subject: str = "work"
) -> RepositoryCommitRecord:
    return RepositoryCommitRecord(
        object_id=oid, committer_iso=iso, author=author, subject=subject
    )


def _grant(root: Path, *, project_id: str = "project-alpha", max_records: int = 20):
    return RepositoryActivityGrant(
        workspace_id="local", project_id=project_id, repository_root=root, max_records=max_records
    )


def _adapter(root: Path, records, *, head: str = "h" * 40, threshold: int = 180):
    fixture = RepositoryActivityFixture(
        repository_id="repo-alpha", head_object_id=head, records=tuple(records)
    )
    return FixtureRepositoryActivityAdapter(
        {str(root): fixture}, staleness_threshold_days=threshold
    )


# ---------------------------------------------------------------- default-denied


def test_no_grant_is_denied(tmp_path: Path) -> None:
    adapter = _adapter(tmp_path, [_record("a" * 40, "2026-07-20T10:00:00+00:00")])
    out = adapter.load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=None, evaluation_time=EVAL
    )
    assert out.kind == "denied"
    assert out.code == CODE_DENIED_NO_GRANT


def test_grant_for_other_project_is_denied(tmp_path: Path) -> None:
    adapter = _adapter(tmp_path, [_record("a" * 40, "2026-07-20T10:00:00+00:00")])
    grant = _grant(tmp_path, project_id="project-other")
    out = adapter.load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=grant, evaluation_time=EVAL
    )
    assert out.kind == "denied"
    assert out.code == CODE_DENIED_ROOT_MISMATCH


def test_grant_for_other_root_is_denied(tmp_path: Path) -> None:
    adapter = _adapter(tmp_path, [_record("a" * 40, "2026-07-20T10:00:00+00:00")])
    other = tmp_path / "elsewhere"
    other.mkdir()
    grant = _grant(other)
    out = adapter.load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=grant, evaluation_time=EVAL
    )
    assert out.kind == "denied"
    assert out.code == CODE_DENIED_ROOT_MISMATCH


# ---------------------------------------------------------------- snapshot


def test_healthy_snapshot_is_sorted_and_capped(tmp_path: Path) -> None:
    records = [
        _record("c" * 40, "2026-07-10T10:00:00+00:00"),
        _record("a" * 40, "2026-07-25T10:00:00+00:00"),
        _record("b" * 40, "2026-07-20T10:00:00+00:00"),
    ]
    adapter = _adapter(tmp_path, records)
    grant = _grant(tmp_path, max_records=2)
    out = adapter.load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=grant, evaluation_time=EVAL
    )
    assert isinstance(out, RepositoryActivitySnapshot)
    # Newest first, capped to 2.
    assert [r.object_id for r in out.records] == ["a" * 40, "b" * 40]
    assert out.fingerprint  # non-empty deterministic fingerprint


def test_fingerprint_is_deterministic_across_input_order(tmp_path: Path) -> None:
    r1 = _record("a" * 40, "2026-07-25T10:00:00+00:00")
    r2 = _record("b" * 40, "2026-07-20T10:00:00+00:00")
    s1 = build_snapshot(
        repository_id="r", head_object_id="h" * 40, records=[r1, r2], max_records=20
    )
    s2 = build_snapshot(
        repository_id="r", head_object_id="h" * 40, records=[r2, r1], max_records=20
    )
    assert s1.fingerprint == s2.fingerprint


def test_missing_fixture_is_unavailable_not_empty(tmp_path: Path) -> None:
    empty = FixtureRepositoryActivityAdapter({})
    grant = _grant(tmp_path)
    out = empty.load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=grant, evaluation_time=EVAL
    )
    assert isinstance(out, RepositoryActivityUnavailable)
    assert out.code == CODE_UNAVAILABLE_NOT_A_REPO


def test_forced_outcome_is_returned(tmp_path: Path) -> None:
    forced = RepositoryActivityUnavailable(CODE_UNAVAILABLE_OUTPUT_OVERFLOW, "overflow")
    fixture = RepositoryActivityFixture(
        repository_id="repo-alpha", head_object_id="h" * 40, forced_outcome=forced
    )
    adapter = FixtureRepositoryActivityAdapter({str(tmp_path): fixture})
    grant = _grant(tmp_path)
    out = adapter.load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=grant, evaluation_time=EVAL
    )
    assert out is forced


# ---------------------------------------------------------------- staleness


def test_old_activity_is_stale(tmp_path: Path) -> None:
    # Newest commit is > 180 days before the evaluation time.
    adapter = _adapter(tmp_path, [_record("a" * 40, "2025-01-01T10:00:00+00:00")], threshold=180)
    grant = _grant(tmp_path)
    out = adapter.load_activity(
        project_id="project-alpha", repository_root=tmp_path, grant=grant, evaluation_time=EVAL
    )
    assert isinstance(out, RepositoryActivityStale)


def test_recent_activity_is_not_stale(tmp_path: Path) -> None:
    snapshot = build_snapshot(
        repository_id="r", head_object_id="h" * 40,
        records=[_record("a" * 40, "2026-07-25T10:00:00+00:00")], max_records=20,
    )
    assert not is_stale(snapshot, evaluation_time=EVAL, threshold_days=180)


def test_fixture_adapter_exposes_no_write_method() -> None:
    # Read-only proof: the port surface is a single read method.
    assert not hasattr(FixtureRepositoryActivityAdapter, "write")
    assert not hasattr(FixtureRepositoryActivityAdapter, "commit")
