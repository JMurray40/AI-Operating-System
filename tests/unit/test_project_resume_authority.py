"""C5: authority classes, temporal state, supersession, and conflicts (ADR-0019, §10).

Covers the eight §10 cases at the evidence-record level plus the classification, date
extraction, staleness-threshold, and ordering primitives they rest on. Authority never uses
retrieval relevance; the evaluation time is always explicit and deterministic.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

from jarvis_core.models.note import Note
from jarvis_core.project_resume.authority import (
    AuthorityConfig,
    AuthorityRecord,
    build_record,
    classify_authority,
    compute_temporal_state,
    extract_dates,
    order_records,
    resolve_authority,
)
from jarvis_core.project_resume.contract import (
    AUTHORITY_ACCEPTED_DECISION,
    AUTHORITY_CURRENT_PRIORITY,
    AUTHORITY_CURRENT_STATE,
    AUTHORITY_DRAFT,
    AUTHORITY_INFERRED,
    AUTHORITY_SESSION_SUMMARY,
    TEMPORAL_DATED,
    TEMPORAL_STALE,
    TEMPORAL_UNDATED,
)

EVAL = datetime(2026, 7, 27, tzinfo=timezone.utc)


def _note(front: dict[str, object], *, relpath: str = "n.md") -> Note:
    return Note(path=Path(relpath), relpath=relpath, frontmatter=front, body="")


def _rec(
    source_id: str,
    authority_class: str,
    *,
    effective: date | None = None,
    updated: date | None = None,
    temporal: str = TEMPORAL_DATED,
    supersedes: tuple[str, ...] = (),
    names: frozenset[str] | None = None,
    locator: str = "",
) -> AuthorityRecord:
    return AuthorityRecord(
        source_id=source_id,
        relpath=f"{source_id}.md",
        locator=locator or f"{source_id}.md",
        authority_class=authority_class,
        effective_date=effective,
        updated_date=updated,
        temporal_state=temporal,
        supersedes=supersedes,
        names=names if names is not None else frozenset({source_id}),
    )


# ---------------------------------------------------------------- classification


def test_classifies_accepted_decision() -> None:
    note = _note({"type": "decision", "status": "accepted", "decision_date": "2026-07-01"})
    assert classify_authority(note) == AUTHORITY_ACCEPTED_DECISION


def test_draft_decision_is_draft_not_authority() -> None:
    # A newer *draft* decision must not read as an accepted decision (recency is not authority).
    note = _note({"type": "decision", "status": "draft"})
    assert classify_authority(note) == AUTHORITY_DRAFT


def test_project_note_is_current_state() -> None:
    note = _note({"type": "project", "status": "active", "priority": "high"})
    assert classify_authority(note) == AUTHORITY_CURRENT_STATE


def test_session_summary_class() -> None:
    note = _note({"type": "session-summary", "status": "active"})
    assert classify_authority(note) == AUTHORITY_SESSION_SUMMARY


def test_next_action_signal_is_current_priority() -> None:
    note = _note({"type": "concept", "status": "active", "next_action": "ship the CLI"})
    assert classify_authority(note) == AUTHORITY_CURRENT_PRIORITY


def test_unmarked_note_falls_back_to_inferred() -> None:
    note = _note({"type": "concept", "status": "active"})
    assert classify_authority(note) == AUTHORITY_INFERRED


# ---------------------------------------------------------------- dates & staleness


def test_extract_prefers_effective_over_updated() -> None:
    note = _note({"decision_date": "2026-06-01", "updated": "2026-07-20"})
    effective, updated = extract_dates(note)
    assert effective == date(2026, 6, 1)
    assert updated == date(2026, 7, 20)


def test_undated_when_no_recognized_date() -> None:
    assert compute_temporal_state(None, None, evaluation_time=EVAL, config=AuthorityConfig()) == (
        TEMPORAL_UNDATED
    )


def test_staleness_exact_threshold_is_stale() -> None:
    cfg = AuthorityConfig(staleness_threshold_days=180)
    at_threshold = date(2026, 7, 27) - _days(180)
    assert compute_temporal_state(at_threshold, None, evaluation_time=EVAL, config=cfg) == (
        TEMPORAL_STALE
    )


def test_staleness_one_day_inside_threshold_is_dated() -> None:
    cfg = AuthorityConfig(staleness_threshold_days=180)
    inside = date(2026, 7, 27) - _days(179)
    assert compute_temporal_state(inside, None, evaluation_time=EVAL, config=cfg) == TEMPORAL_DATED


def _days(n: int):
    from datetime import timedelta

    return timedelta(days=n)


# ---------------------------------------------------------------- ordering


def test_undated_sorts_after_dated_in_same_class() -> None:
    dated = _rec("d1", AUTHORITY_SESSION_SUMMARY, effective=date(2026, 1, 1))
    undated = _rec("d2", AUTHORITY_SESSION_SUMMARY, effective=None, temporal=TEMPORAL_UNDATED)
    ordered = order_records((undated, dated))
    assert [r.source_id for r in ordered] == ["d1", "d2"]


def test_within_class_orders_by_effective_date_desc() -> None:
    older = _rec("a", AUTHORITY_ACCEPTED_DECISION, effective=date(2026, 1, 1))
    newer = _rec("b", AUTHORITY_ACCEPTED_DECISION, effective=date(2026, 6, 1))
    ordered = order_records((older, newer))
    assert [r.source_id for r in ordered] == ["b", "a"]


# ---------------------------------------------------------------- §10 case 1


def test_accepted_decision_outranks_newer_draft() -> None:
    accepted = _rec("dec", AUTHORITY_ACCEPTED_DECISION, effective=date(2026, 1, 1))
    newer_draft = _rec("draft", AUTHORITY_DRAFT, effective=date(2026, 7, 1))
    out = resolve_authority((newer_draft, accepted))
    assert out.authoritative is not None
    assert out.authoritative.source_id == "dec"
    assert not out.has_conflict


# ---------------------------------------------------------------- §10 case 2


def test_current_state_outranks_older_session() -> None:
    state = _rec("proj", AUTHORITY_CURRENT_STATE, effective=date(2026, 7, 1))
    old_session = _rec("sess", AUTHORITY_SESSION_SUMMARY, effective=date(2026, 3, 1))
    out = resolve_authority((old_session, state))
    assert out.authoritative is not None
    assert out.authoritative.source_id == "proj"
    assert not out.has_conflict


# ---------------------------------------------------------------- §10 case 3


def test_supersession_with_evidence_removes_the_superseded() -> None:
    old = _rec("dec-old", AUTHORITY_ACCEPTED_DECISION, effective=date(2026, 1, 1),
               names=frozenset({"dec-old"}))
    new = _rec("dec-new", AUTHORITY_ACCEPTED_DECISION, effective=date(2026, 6, 1),
               supersedes=("dec-old",), names=frozenset({"dec-new"}))
    out = resolve_authority((old, new))
    assert out.authoritative is not None
    assert out.authoritative.source_id == "dec-new"
    assert not out.has_conflict
    assert [r.source_id for r in out.superseded] == ["dec-old"]


# ---------------------------------------------------------------- §10 case 4


def test_two_accepted_decisions_without_supersession_conflict() -> None:
    a = _rec("dec-a", AUTHORITY_ACCEPTED_DECISION, effective=date(2026, 1, 1),
             names=frozenset({"dec-a"}))
    b = _rec("dec-b", AUTHORITY_ACCEPTED_DECISION, effective=date(2026, 6, 1),
             names=frozenset({"dec-b"}))
    out = resolve_authority((a, b))
    assert out.authoritative is None
    assert out.has_conflict
    assert {r.source_id for r in out.conflicting} == {"dec-a", "dec-b"}


# ---------------------------------------------------------------- §10 case 5


def test_two_supported_material_conflicts_are_both_retained() -> None:
    a = _rec("state-a", AUTHORITY_CURRENT_STATE, effective=date(2026, 5, 1))
    b = _rec("state-b", AUTHORITY_CURRENT_STATE, effective=date(2026, 5, 1))
    out = resolve_authority((a, b))
    assert out.has_conflict
    assert len(out.conflicting) == 2
    # Retain-both: neither is dropped from the ordering.
    assert {r.source_id for r in out.ordered} == {"state-a", "state-b"}


# ---------------------------------------------------------------- §10 case 6


def test_undated_evidence_is_labeled_and_ordered_last() -> None:
    note = _note({"type": "session-summary", "status": "active"})  # no dates
    rec = build_record(
        note=note, source_id="s", relpath="s.md", locator="s.md", evaluation_time=EVAL
    )
    assert rec.temporal_state == TEMPORAL_UNDATED
    dated = _rec("dated", AUTHORITY_SESSION_SUMMARY, effective=date(2026, 1, 1))
    ordered = order_records((rec, dated))
    assert ordered[-1].source_id == "s"


# ---------------------------------------------------------------- §10 case 7


def test_stale_at_exact_threshold_via_build_record() -> None:
    note = _note(
        {"type": "decision", "status": "accepted", "decision_date": "2026-01-28"}
    )  # exactly 180 days before 2026-07-27
    rec = build_record(
        note=note, source_id="d", relpath="d.md", locator="d.md", evaluation_time=EVAL,
        config=AuthorityConfig(staleness_threshold_days=180),
    )
    assert rec.temporal_state == TEMPORAL_STALE


# ---------------------------------------------------------------- §10 case 8


def test_excluded_evidence_cannot_resolve_conflict() -> None:
    # The superseding decision that WOULD resolve the conflict is excluded from the authorized
    # set, so it is simply absent. The two remaining accepted decisions still conflict.
    a = _rec("dec-a", AUTHORITY_ACCEPTED_DECISION, effective=date(2026, 1, 1),
             names=frozenset({"dec-a"}))
    b = _rec("dec-b", AUTHORITY_ACCEPTED_DECISION, effective=date(2026, 2, 1),
             names=frozenset({"dec-b"}))
    # 'dec-super' (supersedes both) is NOT included — it was excluded by authorization.
    out = resolve_authority((a, b))
    assert out.has_conflict
    assert {r.source_id for r in out.conflicting} == {"dec-a", "dec-b"}


def test_superseded_record_cannot_exert_supersession() -> None:
    # C supersedes B, B supersedes A. C is authoritative; B is superseded and so its own
    # supersession of A must not count -> A survives, no false authority resurrection.
    a = _rec("a", AUTHORITY_ACCEPTED_DECISION, effective=date(2026, 1, 1), names=frozenset({"a"}))
    b = _rec("b", AUTHORITY_ACCEPTED_DECISION, effective=date(2026, 2, 1),
             supersedes=("a",), names=frozenset({"b"}))
    c = _rec("c", AUTHORITY_ACCEPTED_DECISION, effective=date(2026, 3, 1),
             supersedes=("b",), names=frozenset({"c"}))
    out = resolve_authority((a, b, c))
    superseded_ids = {r.source_id for r in out.superseded}
    assert "b" in superseded_ids
    assert "a" not in superseded_ids
