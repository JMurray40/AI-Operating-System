"""Authority, temporal, supersession, and conflict ordering (ADR-0019).

Retrieval relevance cannot decide which statement is authoritative or current. This module
lifts discovered evidence into *authority space*: every source is assigned a typed authority
class, a temporal state (dated / undated / stale) derived from explicit source dates and the
request-supplied deterministic evaluation time, and — for one subject at a time — an ordering
that resolves precedence without ever using relevance, recency alone, or a provider.

The accepted authority order (strongest first, ADR-0019) is fixed in
:data:`jarvis_core.project_resume.contract.AUTHORITY_ORDER`. Within a class, records order by
effective-date desc, then source ``updated`` desc, then stable source identity asc, then
passage locator asc. Undated evidence sorts after dated evidence in the same class and is
labeled ``undated``.

Supersession exists *only* when current authorized evidence explicitly establishes it: a
``supersedes`` reference that resolves to a known stable source identity in the same subject
set. Date, title similarity, shared tags, or retrieval rank never establish supersession.
When materially different claims remain supported at the strongest present class and neither
validly supersedes the other, both are retained and marked ``conflicting`` — this module never
merges or silently chooses. Excluded evidence is simply absent from the authorized set, so it
can neither create nor resolve a conflict.

Claims do not exist yet at C5; the assembler (C10) groups evidence by subject and binds the
:class:`SubjectAuthority` outcome onto claims. Full citation validation of a ``supersedes``
passage against current bytes is layered on in C6; here a reference is honored when it resolves
to a known identity in the subject set.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from jarvis_core.models.base import NoteType
from jarvis_core.models.note import Note
from jarvis_core.project_resume.contract import (
    AUTHORITY_ACCEPTED_DECISION,
    AUTHORITY_CURRENT_PRIORITY,
    AUTHORITY_CURRENT_STATE,
    AUTHORITY_DRAFT,
    AUTHORITY_INFERRED,
    AUTHORITY_ORDER,
    AUTHORITY_SESSION_SUMMARY,
    TEMPORAL_DATED,
    TEMPORAL_STALE,
    TEMPORAL_UNDATED,
)
from jarvis_core.project_resume.identity import normalize_selector

# Rank lookup: lower rank == stronger authority.
AUTHORITY_RANK: dict[str, int] = {name: i for i, name in enumerate(AUTHORITY_ORDER)}

# Lifecycle signals (jarvis_core.models.base.Status vocabulary).
_ACCEPTED_STATUSES: frozenset[str] = frozenset({"accepted", "implemented"})
_DRAFT_STATUSES: frozenset[str] = frozenset({"draft", "proposed", "inbox"})

# Frontmatter fields that carry an explicit "effective" date, in preference order. The first
# present, parseable field wins; ``updated`` is a separate, secondary temporal signal.
_EFFECTIVE_DATE_FIELDS: tuple[str, ...] = (
    "effective_date",
    "decision_date",
    "session_date",
    "meeting_date",
    "date",
    "created",
)

# Frontmatter signals of an explicit current priority / next action / milestone.
_PRIORITY_FIELDS: tuple[str, ...] = ("next_action", "milestone")

DEFAULT_STALENESS_THRESHOLD_DAYS = 180


@dataclass(frozen=True)
class AuthorityConfig:
    """Configured, testable authority/temporal thresholds (ADR-0019)."""

    staleness_threshold_days: int = DEFAULT_STALENESS_THRESHOLD_DAYS


@dataclass(frozen=True)
class AuthorityRecord:
    """One evidence source lifted into authority space for a single subject."""

    source_id: str
    relpath: str
    locator: str
    authority_class: str
    effective_date: date | None
    updated_date: date | None
    temporal_state: str  # contract.TEMPORAL_*
    supersedes: tuple[str, ...]  # normalized references this record claims to supersede
    names: frozenset[str] = field(default=frozenset(), compare=False)  # normalized self-names
    superseded_by: str | None = None  # source_id of the validated superseding record, if any

    @property
    def authority_rank(self) -> int:
        return AUTHORITY_RANK[self.authority_class]

    @property
    def is_superseded(self) -> bool:
        return self.superseded_by is not None

    @property
    def is_undated(self) -> bool:
        return self.temporal_state == TEMPORAL_UNDATED

    def with_superseded_by(self, source_id: str | None) -> AuthorityRecord:
        """Return a copy carrying the resolved supersession pointer (records are frozen)."""
        return AuthorityRecord(
            source_id=self.source_id,
            relpath=self.relpath,
            locator=self.locator,
            authority_class=self.authority_class,
            effective_date=self.effective_date,
            updated_date=self.updated_date,
            temporal_state=self.temporal_state,
            supersedes=self.supersedes,
            names=self.names,
            superseded_by=source_id,
        )


@dataclass(frozen=True)
class SubjectAuthority:
    """The resolved authority outcome for one subject's evidence set."""

    ordered: tuple[AuthorityRecord, ...]  # every record, strongest first (superseded included)
    authoritative: AuthorityRecord | None  # the single winner, or None when empty/conflicting
    conflicting: tuple[AuthorityRecord, ...]  # >=2 top-class survivors, else ()
    superseded: tuple[AuthorityRecord, ...]  # records removed by validated supersession

    @property
    def has_conflict(self) -> bool:
        return len(self.conflicting) >= 2


# ------------------------------------------------------------------ classification


def classify_authority(note: Note) -> str:
    """Assign a note to exactly one authority class (ADR-0019, strongest applicable signal).

    A draft/proposed note is always ``draft`` regardless of type: draft recency is never
    authority. Otherwise an accepted/implemented decision is an ``accepted_decision``; a project
    note is the canonical ``current_state`` passage; a note carrying an explicit next-action or
    milestone signal is ``current_priority``; a session summary is ``session_summary``; anything
    else falls back to ``inferred``.
    """
    status = (note.status or "").strip().lower()
    if status in _DRAFT_STATUSES:
        return AUTHORITY_DRAFT
    if note.type is NoteType.DECISION and status in _ACCEPTED_STATUSES:
        return AUTHORITY_ACCEPTED_DECISION
    if note.type is NoteType.PROJECT:
        return AUTHORITY_CURRENT_STATE
    if _has_priority_signal(note):
        return AUTHORITY_CURRENT_PRIORITY
    if note.type is NoteType.SESSION_SUMMARY:
        return AUTHORITY_SESSION_SUMMARY
    return AUTHORITY_INFERRED


def _has_priority_signal(note: Note) -> bool:
    return any(note.frontmatter_list(key) for key in _PRIORITY_FIELDS)


# ------------------------------------------------------------------ temporal state


def _parse_date(value: object) -> date | None:
    """Parse a frontmatter date value to a ``date``; return None if absent/malformed.

    Accepts ``date``/``datetime`` objects (some YAML loaders type these directly) and ISO-8601
    strings, tolerating a trailing ``Z`` and a full timestamp. Never raises.
    """
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        return None
    raw = value.strip()
    if not raw:
        return None
    normalized = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        return datetime.fromisoformat(normalized).date()
    except ValueError:
        try:
            return date.fromisoformat(normalized[:10])
        except ValueError:
            return None


def extract_dates(note: Note) -> tuple[date | None, date | None]:
    """Return ``(effective_date, updated_date)`` from explicit frontmatter, never wall clock."""
    effective: date | None = None
    for key in _EFFECTIVE_DATE_FIELDS:
        effective = _parse_date(note.frontmatter.get(key))
        if effective is not None:
            break
    updated = _parse_date(note.frontmatter.get("updated"))
    return effective, updated


def compute_temporal_state(
    effective: date | None,
    updated: date | None,
    *,
    evaluation_time: datetime,
    config: AuthorityConfig,
) -> str:
    """Classify temporal state from explicit dates and the deterministic evaluation time.

    The primary date is the effective date when present, otherwise the ``updated`` date. With no
    date at all the record is ``undated``. Otherwise the record is ``stale`` once its age reaches
    the configured threshold (``age_days >= threshold``; the exact threshold is stale), else
    ``dated``.
    """
    primary = effective or updated
    if primary is None:
        return TEMPORAL_UNDATED
    eval_date = evaluation_time.astimezone(timezone.utc).date()
    age_days = (eval_date - primary).days
    if age_days >= config.staleness_threshold_days:
        return TEMPORAL_STALE
    return TEMPORAL_DATED


# ------------------------------------------------------------------ record building


def _self_names(note: Note, source_id: str) -> frozenset[str]:
    names = {normalize_selector(source_id)} if source_id else set()
    for candidate in note.names():
        n = normalize_selector(candidate)
        if n:
            names.add(n)
    return frozenset(names)


def build_record(
    *,
    note: Note,
    source_id: str,
    relpath: str,
    locator: str,
    evaluation_time: datetime,
    config: AuthorityConfig | None = None,
) -> AuthorityRecord:
    """Lift one authorized evidence source into an :class:`AuthorityRecord` (no supersession)."""
    config = config or AuthorityConfig()
    effective, updated = extract_dates(note)
    temporal = compute_temporal_state(
        effective, updated, evaluation_time=evaluation_time, config=config
    )
    supersedes = tuple(
        sorted({normalize_selector(r) for r in note.frontmatter_list("supersedes") if r})
    )
    return AuthorityRecord(
        source_id=source_id,
        relpath=relpath,
        locator=locator,
        authority_class=classify_authority(note),
        effective_date=effective,
        updated_date=updated,
        temporal_state=temporal,
        supersedes=supersedes,
        names=_self_names(note, source_id),
    )


# ------------------------------------------------------------------ ordering


def _order_key(rec: AuthorityRecord) -> tuple[int, int, object, int, object, str, str]:
    """Deterministic sort key: authority, then dated-before-undated, then the within-class rules.

    ``date.toordinal()`` is negated so *descending* date becomes an ascending sort component,
    and ``None`` dates sort last within their class (undated after dated).
    """
    has_effective = rec.effective_date is not None
    eff = -rec.effective_date.toordinal() if rec.effective_date is not None else 0
    has_updated = rec.updated_date is not None
    upd = -rec.updated_date.toordinal() if rec.updated_date is not None else 0
    return (
        rec.authority_rank,
        0 if has_effective else 1,  # dated (effective) before undated in the same class
        eff,
        0 if has_updated else 1,
        upd,
        rec.source_id,
        rec.locator,
    )


def order_records(records: tuple[AuthorityRecord, ...]) -> tuple[AuthorityRecord, ...]:
    """Order records strongest-authority-first per ADR-0019 (relevance never participates)."""
    return tuple(sorted(records, key=_order_key))


# ------------------------------------------------------------------ supersession


def _resolve_supersession(
    records: tuple[AuthorityRecord, ...],
) -> tuple[AuthorityRecord, ...]:
    """Mark records superseded by a validated ``supersedes`` reference to a known identity.

    A reference is honored only when it resolves to another record's stable identity in the same
    subject set, and only a non-superseded record may supersede another (so a superseded chain
    cannot resurrect authority). Resolution runs to a bounded fixpoint for determinism; on a
    mutual/cyclic reference the stronger record by :func:`_order_key` wins and the weaker is
    superseded.
    """
    # Map every normalized name to its owning record's source_id.
    name_to_id: dict[str, str] = {}
    for rec in records:
        for name in rec.names:
            name_to_id.setdefault(name, rec.source_id)

    by_id = {r.source_id: r for r in records}
    order_index = {r.source_id: i for i, r in enumerate(order_records(records))}
    superseded_by: dict[str, str] = {}

    # Bounded fixpoint: at most len(records) passes suffices to settle chains.
    for _ in range(len(records) + 1):
        changed = False
        for rec in records:
            if rec.source_id in superseded_by:
                continue  # a superseded record cannot exert supersession
            for ref in rec.supersedes:
                target_id = name_to_id.get(ref)
                if target_id is None or target_id == rec.source_id:
                    continue
                if by_id.get(target_id) is None:
                    continue
                current = superseded_by.get(target_id)
                if current is None:
                    superseded_by[target_id] = rec.source_id
                    changed = True
                elif order_index[rec.source_id] < order_index[current]:
                    # Prefer the stronger superseder deterministically.
                    superseded_by[target_id] = rec.source_id
                    changed = True
        if not changed:
            break

    # Drop supersession asserted by a record that itself became superseded.
    resolved = {
        tid: sid for tid, sid in superseded_by.items() if sid not in superseded_by
    }
    return tuple(rec.with_superseded_by(resolved.get(rec.source_id)) for rec in records)


# ------------------------------------------------------------------ subject resolution


def resolve_authority(
    records: tuple[AuthorityRecord, ...] | list[AuthorityRecord],
    *,
    config: AuthorityConfig | None = None,
) -> SubjectAuthority:
    """Resolve authority for one subject: supersession, ordering, winner, and conflicts.

    The strongest authority class present among non-superseded survivors decides the subject. A
    single survivor at that class is authoritative; two or more are retained and marked
    conflicting (ADR-0019 retain-both). Nothing is merged and nothing is silently chosen.
    """
    _ = config  # thresholds are applied at record-build time; kept for API symmetry
    resolved = _resolve_supersession(tuple(records))
    ordered = order_records(resolved)

    superseded = tuple(r for r in ordered if r.is_superseded)
    survivors = tuple(r for r in ordered if not r.is_superseded)

    if not survivors:
        return SubjectAuthority(
            ordered=ordered, authoritative=None, conflicting=(), superseded=superseded
        )

    top_rank = min(r.authority_rank for r in survivors)
    top = tuple(r for r in survivors if r.authority_rank == top_rank)

    if len(top) == 1:
        return SubjectAuthority(
            ordered=ordered, authoritative=top[0], conflicting=(), superseded=superseded
        )
    return SubjectAuthority(
        ordered=ordered, authoritative=None, conflicting=top, superseded=superseded
    )
