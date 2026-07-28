"""Project Resume orchestration (C10, brief §5/§9).

The assembler is *only* orchestration: it wires the released authorized-view / citation
services and the C5-C9 Project Resume modules together and maps their typed outputs into the
frozen :class:`ProjectResumeResult`. It contains no parsing, policy, subprocess, rendering, or
scoring logic of its own — identity selection lives in ``identity``, discovery in ``evidence``,
authority/temporal/supersession/conflict ordering in ``authority``, citation binding in the
reusable query-layer ``CitationFactory`` via ``evidence.bind_source_citation``, the two hard
budgets in ``budget``, local Git activity behind the ``repository_activity`` port, and the safe
trace in ``trace``.

Flow: build the authorized view (duplicate/malformed identity fails closed) → select exactly
one project (ambiguous/not-found/invalid short-circuit) → discover evidence across typed
channels → admit evidence within the evidence budget → lift each admitted source into authority
space and bind it to a current-validated citation → group evidence into the ten fixed sections
by note type, resolving ordering and conflicts *within* each bucket by authority class → add
grant-gated local repository activity → enforce the output budget on the final serialization →
emit a frozen, versioned result with a deterministic status and an optional safe trace.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass

from jarvis_core.identity import DuplicateIdentityError
from jarvis_core.models.base import NoteType
from jarvis_core.models.note import Note
from jarvis_core.project_resume.authority import (
    AuthorityConfig,
    AuthorityRecord,
    build_record,
    resolve_authority,
)
from jarvis_core.project_resume.budget import (
    BudgetConfig,
    BudgetItem,
    check_output,
    estimate,
    plan_within_budget,
)
from jarvis_core.project_resume.contract import (
    AUTHORITY_INFERRED,
    DEFAULT_TRACE_TOKEN_SUB_BUDGET,
    EMPTY_SECTION_NOTE,
    KIND_FACT,
    KIND_INFERENCE,
    KIND_UNKNOWN,
    SECTION_CONFLICTS,
    SECTION_COVERAGE,
    SECTION_CURRENT_STATE,
    SECTION_DECISIONS,
    SECTION_NEXT_ACTION,
    SECTION_OPEN_ITEMS,
    SECTION_ORDER,
    SECTION_PROJECT,
    SECTION_REPOSITORY,
    SECTION_RESOURCES,
    SECTION_SESSIONS,
    STATUS_AMBIGUOUS,
    STATUS_BUDGET_ERROR,
    STATUS_COMPLETE,
    STATUS_INVALID_IDENTITY,
    STATUS_NOT_FOUND,
    STATUS_PARTIAL,
    SUPPORT_CONFLICTING,
    SUPPORT_INCOMPLETE,
    SUPPORT_SUPPORTED,
    TEMPORAL_DATED,
)
from jarvis_core.project_resume.evidence import (
    DiscoveredSource,
    DiscoveryBounds,
    EvidenceBinding,
    bind_source_citation,
    discover_evidence,
    evidence_id_for,
    summarize_coverage,
)
from jarvis_core.project_resume.identity import (
    SELECTION_AMBIGUOUS,
    SELECTION_INVALID,
    SELECTION_NOT_FOUND,
    SELECTION_SELECTED,
    select_project,
)
from jarvis_core.project_resume.repository_activity import (
    RepositoryActivityGrant,
    RepositoryActivityPort,
    RepositoryActivitySnapshot,
)
from jarvis_core.project_resume.request import ProjectResumeRequest
from jarvis_core.project_resume.results import (
    BriefingClaim,
    BriefingSection,
    Conflict,
    CoverageSummary,
    EvidenceCitation,
    Limitation,
    Omission,
    ProjectIdentity,
    ProjectResumeResult,
    RepositoryCitation,
)
from jarvis_core.project_resume.trace import ProjectResumeTrace, workspace_fingerprint
from jarvis_core.query.authorized import build_authorized_view
from jarvis_core.query.evidence import CitationFactory, CurrentSourceResolver
from jarvis_core.query.index import LexicalIndex
from jarvis_core.query.ranking import Ranker, RankingWeights
from jarvis_core.query.tokenizer import token_set
from jarvis_core.relationships.resolver import RelationshipResolver

__all__ = ["assemble"]

# Section display order rank for deterministic priority (project strongest).
_SECTION_RANK: dict[str, int] = {key: i for i, (key, _title) in enumerate(SECTION_ORDER)}

# Fixed-limit for a single claim's collapsed text (deterministic, never a provider).
_CLAIM_TEXT_MAX = 240


def _one_line(text: str) -> str:
    """Collapse whitespace and bound a validated excerpt into deterministic claim text."""
    collapsed = " ".join(text.split())
    return collapsed[:_CLAIM_TEXT_MAX]


def _serialize(obj: object) -> str:
    """Serialize in the *emitted* JSON form so budget measurement matches real output.

    The released estimator counts whitespace-delimited words, so the budget must be measured
    against the same indented serialization the renderer emits (``render_json``); a compact form
    would undercount and let over-budget results through.
    """
    return json.dumps(obj, ensure_ascii=False, indent=2, default=str)


def _has_priority_signal(note: Note) -> bool:
    return bool(note.frontmatter_list("next_action") or note.frontmatter_list("milestone"))


def _bucket_for(note: Note) -> str:
    """Route one evidence note to exactly one content section by note type (brief §9).

    Note *type* selects the bucket; authority *class* (accepted vs draft, etc.) resolves
    ordering and conflicts within the bucket, so an accepted decision and a competing draft
    land in the same 'Accepted decisions' subject and the accepted one wins (ADR-0019, A4).
    """
    t = note.type
    if t is NoteType.PROJECT:
        return SECTION_CURRENT_STATE
    if t is NoteType.DECISION:
        return SECTION_DECISIONS
    if t in (NoteType.SESSION_SUMMARY, NoteType.MEETING, NoteType.DAILY):
        return SECTION_SESSIONS
    if t in (NoteType.RESOURCE, NoteType.REFERENCE):
        return SECTION_RESOURCES
    if _has_priority_signal(note):
        return SECTION_NEXT_ACTION
    return SECTION_OPEN_ITEMS


def _evidence_terms(project_identity: ProjectIdentity, note: Note) -> frozenset[str]:
    """Deterministic material terms binding a source's passage to the selected project."""
    terms: set[str] = set()
    terms |= token_set(project_identity.title or "")
    terms |= token_set(note.title or "")
    for value in (*note.frontmatter_list("next_action"), *note.frontmatter_list("milestone")):
        terms |= token_set(value)
    return frozenset(terms)


@dataclass(frozen=True)
class _Bound:
    """An admitted source with its authority record and current-validated binding."""

    source: DiscoveredSource
    record: AuthorityRecord
    binding: EvidenceBinding
    bucket: str


def assemble(
    notes: list[Note],
    request: ProjectResumeRequest,
    *,
    repository_port: RepositoryActivityPort | None = None,
    bounds: DiscoveryBounds | None = None,
    authority_config: AuthorityConfig | None = None,
    weights: RankingWeights | None = None,
) -> ProjectResumeResult:
    """Assemble a complete, frozen Project Resume result for one validated request."""
    authority_config = authority_config or AuthorityConfig()
    budget_config = BudgetConfig(
        evidence_token_budget=request.evidence_token_budget,
        output_token_budget=request.output_token_budget,
        trace_token_sub_budget=min(DEFAULT_TRACE_TOKEN_SUB_BUDGET, request.output_token_budget),
    ).validate()
    timings: dict[str, float] = {}

    # 1) Authorized view + exact identity selection. Duplicate/malformed identity fails closed.
    t0 = time.perf_counter()
    try:
        view = build_authorized_view(notes, request.authorization_scope)
    except DuplicateIdentityError:
        return _terminal(request, STATUS_INVALID_IDENTITY, excluded_count=0, timings=timings)
    selection = select_project(view, request.project_selector)
    timings["select_ms"] = (time.perf_counter() - t0) * 1000.0

    if selection.status == SELECTION_INVALID:
        return _terminal(request, STATUS_INVALID_IDENTITY, view.excluded_count, timings)
    if selection.status == SELECTION_NOT_FOUND:
        return _terminal(request, STATUS_NOT_FOUND, view.excluded_count, timings)
    if selection.status == SELECTION_AMBIGUOUS:
        return _terminal(
            request, STATUS_AMBIGUOUS, view.excluded_count, timings,
            candidates=selection.candidates, selection_reason=selection.reason,
        )
    assert selection.status == SELECTION_SELECTED and selection.identity is not None
    identity = selection.identity

    # 2) Compose the released query-layer collaborators (no logic duplicated here).
    resolver = CurrentSourceResolver(request.source_root)
    factory = CitationFactory(view.identities, resolver)
    report = RelationshipResolver(view.notes).resolve_all()
    index = LexicalIndex(view.notes)
    ranker = Ranker(index, report, weights)
    by_relpath = {n.relpath: n for n in view.notes}
    project_note = by_relpath[identity.relpath]

    # 3) Discover evidence across typed channels.
    t1 = time.perf_counter()
    discovery = discover_evidence(
        view=view, report=report, index=index, ranker=ranker,
        project_note=project_note, project_identity=identity, bounds=bounds,
    )
    timings["discover_ms"] = (time.perf_counter() - t1) * 1000.0
    omissions: list[Omission] = list(discovery.omissions)

    # 4) Bind every discovered source to a current-validated citation, then admit within the
    #    EVIDENCE budget in deterministic priority order (canonical/section rank, discovery order).
    t2 = time.perf_counter()
    prelim: list[_Bound] = []
    for source in discovery.sources:
        note = source.note
        binding = bind_source_citation(
            source, factory=factory,
            evidence_terms=_evidence_terms(identity, note),
            reason=source.channel_reason,
        )
        record = build_record(
            note=note, source_id=source.source_id, relpath=source.relpath,
            locator=source.relpath, evaluation_time=request.evaluation_time,
            config=authority_config,
        )
        prelim.append(_Bound(source, record, binding, _bucket_for(note)))

    def _priority(pair: tuple[int, _Bound]) -> tuple[int, int]:
        order_index, b = pair
        return (_SECTION_RANK[b.bucket], order_index)

    ordered = [b for _i, b in sorted(enumerate(prelim), key=_priority)]
    evidence_items = [
        BudgetItem(key=evidence_id_for(b.source), tokens=_evidence_cost(b))
        for b in ordered
    ]
    evidence_plan = plan_within_budget(
        evidence_items, capacity=budget_config.evidence_token_budget, reserved=0,
        omission_reason="evidence budget reached", channel=None,
    )
    admitted_keys = {item.key for item in evidence_plan.admitted}
    admitted = [b for b in ordered if evidence_id_for(b.source) in admitted_keys]
    omissions.extend(evidence_plan.omissions)
    timings["bind_ms"] = (time.perf_counter() - t2) * 1000.0

    # 5) Build claims/sections/conflicts by bucket; ordering + conflicts resolved by authority.
    section_claims: dict[str, list[BriefingClaim]] = {key: [] for key, _t in SECTION_ORDER}
    citations: dict[str, EvidenceCitation] = {}
    conflicts: list[Conflict] = []
    limitations: list[Limitation] = []
    by_source_id = {b.source.source_id: b for b in admitted}

    # Project identity claim (always cites the selected project note).
    project_bound = by_source_id.get(identity.source_id)
    if project_bound is not None:
        claim = _make_claim(
            project_bound, section=SECTION_PROJECT, position=0,
            authority_class=project_bound.record.authority_class,
        )
        section_claims[SECTION_PROJECT].append(claim)
        _record_citation(citations, project_bound)

    # Group admitted sources by content bucket and resolve authority within each.
    buckets: dict[str, list[_Bound]] = {}
    for b in admitted:
        buckets.setdefault(b.bucket, []).append(b)

    for bucket, members in buckets.items():
        subject = resolve_authority(tuple(m.record for m in members), config=authority_config)
        conflicting_ids = {r.source_id for r in subject.conflicting}
        ordered_members = [
            by_source_id[r.source_id] for r in subject.ordered if r.source_id in by_source_id
        ]
        for b in ordered_members:
            forced = SUPPORT_CONFLICTING if b.source.source_id in conflicting_ids else None
            claim = _make_claim(
                b, section=bucket, position=len(section_claims[bucket]),
                authority_class=b.record.authority_class, forced_support=forced,
            )
            section_claims[bucket].append(claim)
            _record_citation(citations, b)

        supported_conflicts = [
            b for b in members
            if b.source.source_id in conflicting_ids and b.binding.is_supported
        ]
        if len(supported_conflicts) >= 2:
            conflicts.append(
                Conflict(
                    conflict_id=f"cf:{bucket}",
                    subject=bucket,
                    claim_ids=tuple(
                        _claim_id(bucket, b.source.source_id) for b in supported_conflicts
                    ),
                    evidence_ids=tuple(
                        evidence_id_for(b.source) for b in supported_conflicts
                    ),
                    note=(
                        "two or more supported material claims conflict "
                        "without valid supersession"
                    ),
                )
            )

    # 6) Grant-gated local repository activity (denied by default; port only called with a grant).
    repository_citations: list[RepositoryCitation] = []
    repository_kind: str | None = None
    grant = request.repository_activity_grant
    if grant is not None and repository_port is not None:
        t3 = time.perf_counter()
        repo_result = repository_port.load_activity(
            project_id=identity.source_id,
            repository_root=grant.repository_root,
            grant=grant,
            evaluation_time=request.evaluation_time,
        )
        timings["repository_ms"] = (time.perf_counter() - t3) * 1000.0
        repository_kind = repo_result.kind
        if isinstance(repo_result, RepositoryActivitySnapshot):
            repository_citations, repo_claims = _repository_claims(repo_result, grant)
            section_claims[SECTION_REPOSITORY].extend(repo_claims)
        else:
            limitations.append(
                Limitation(code=repo_result.code, message=repo_result.message)
            )

    # 7) Coverage + section note-only meta sections + limitations for incomplete claims.
    all_claims = [c for key, _t in SECTION_ORDER for c in section_claims[key]]
    coverage = _coverage(all_claims)
    _add_temporal_limitations(admitted, limitations)

    sections = _build_sections(section_claims, coverage, conflicts, limitations, omissions)

    result = ProjectResumeResult(
        request_id=request.request_id,
        status=STATUS_COMPLETE,  # provisional; corrected after the output budget check
        coverage=coverage,
        project_identity=identity,
        sections=sections,
        citations=tuple(sorted(citations.values(), key=lambda c: c.evidence_id)),
        repository_citations=tuple(repository_citations),
        conflicts=tuple(conflicts),
        omissions=tuple(omissions),
        limitations=tuple(limitations),
    )

    # 8) Output budget on the final serialization; shed lowest-priority claims or fail closed.
    trace = (
        _build_trace(request, view, identity, selection.reason, discovery, admitted,
                     repository_kind, coverage, budget_config, timings)
        if request.trace_requested else None
    )
    return _apply_output_budget(result, trace, budget_config, section_claims, omissions)


# ------------------------------------------------------------------ claim helpers


def _claim_id(section: str, source_id: str) -> str:
    return f"cl:{section}:{source_id}"


def _make_claim(
    b: _Bound,
    *,
    section: str,
    position: int,
    authority_class: str,
    forced_support: str | None = None,
) -> BriefingClaim:
    """Build one claim; supported text is the current-validated excerpt (never a provider)."""
    citation = b.binding.citation
    if b.binding.is_supported and citation is not None:
        text = _one_line(citation.citation.excerpt) or (b.source.note.title or b.source.relpath)
        kind = KIND_INFERENCE if authority_class == AUTHORITY_INFERRED else KIND_FACT
        support = SUPPORT_SUPPORTED
    else:
        text = b.source.note.title or b.source.relpath
        kind = KIND_UNKNOWN
        support = SUPPORT_INCOMPLETE
    if forced_support is not None:
        support = forced_support
    evidence_ids = (evidence_id_for(b.source),) if citation is not None else ()
    return BriefingClaim(
        claim_id=_claim_id(section, b.source.source_id),
        section=section,
        position=position,
        text=text,
        statement_kind=kind,
        authority_class=authority_class,
        temporal_state=b.record.temporal_state,
        support_state=support,
        evidence_ids=evidence_ids,
    )


def _record_citation(citations: dict[str, EvidenceCitation], b: _Bound) -> None:
    citation = b.binding.citation
    if citation is not None:
        citations[citation.evidence_id] = citation


def _evidence_cost(b: _Bound) -> int:
    citation = b.binding.citation
    payload: object = (
        citation.to_dict() if citation is not None
        else {"evidence_id": evidence_id_for(b.source)}
    )
    return estimate(_serialize(payload))


def _repository_claims(
    snapshot: RepositoryActivitySnapshot, grant: RepositoryActivityGrant
) -> tuple[list[RepositoryCitation], list[BriefingClaim]]:
    """Build revision-bound repository citations and their supported activity claims."""
    citations: list[RepositoryCitation] = []
    claims: list[BriefingClaim] = []
    for index, record in enumerate(snapshot.records[: grant.max_records]):
        evidence_id = f"rev:{snapshot.repository_id}:{record.object_id[:12]}"
        citations.append(
            RepositoryCitation(
                evidence_id=evidence_id,
                repository_id=snapshot.repository_id,
                head_object_id=snapshot.head_object_id,
                record_object_id=record.object_id,
                committer_iso=record.committer_iso,
                author=record.author,
                subject_excerpt=_one_line(record.subject),
                snapshot_fingerprint=snapshot.fingerprint,
                record_index=index,
            )
        )
        claims.append(
            BriefingClaim(
                claim_id=f"cl:{SECTION_REPOSITORY}:{record.object_id[:12]}",
                section=SECTION_REPOSITORY,
                position=index,
                text=_one_line(record.subject) or record.object_id[:12],
                statement_kind=KIND_FACT,
                authority_class=AUTHORITY_INFERRED,
                temporal_state=TEMPORAL_DATED,
                support_state=SUPPORT_SUPPORTED,
                evidence_ids=(evidence_id,),
            )
        )
    return citations, claims


def _coverage(claims: list[BriefingClaim]) -> CoverageSummary:
    supported = sum(1 for c in claims if c.support_state == SUPPORT_SUPPORTED)
    incomplete = sum(1 for c in claims if c.support_state == SUPPORT_INCOMPLETE)
    conflicting = sum(1 for c in claims if c.support_state == SUPPORT_CONFLICTING)
    return summarize_coverage(supported=supported, incomplete=incomplete, conflicting=conflicting)


def _add_temporal_limitations(admitted: list[_Bound], limitations: list[Limitation]) -> None:
    stale = sum(1 for b in admitted if b.record.temporal_state == "stale")
    if stale:
        limitations.append(
            Limitation(code="stale_evidence", message=f"{stale} evidence source(s) are stale")
        )


# ------------------------------------------------------------------ sections + status


def _build_sections(
    section_claims: dict[str, list[BriefingClaim]],
    coverage: CoverageSummary,
    conflicts: list[Conflict],
    limitations: list[Limitation],
    omissions: list[Omission],
) -> tuple[BriefingSection, ...]:
    """Assemble the ten fixed sections; empty content sections carry the neutral note."""
    sections: list[BriefingSection] = []
    for position, (key, title) in enumerate(SECTION_ORDER):
        claims = tuple(section_claims.get(key, ()))
        note: str | None = None
        if key == SECTION_CONFLICTS:
            note = _conflicts_note(conflicts, limitations)
        elif key == SECTION_COVERAGE:
            note = _coverage_note(coverage, omissions)
        elif not claims:
            note = EMPTY_SECTION_NOTE
        sections.append(
            BriefingSection(key=key, title=title, position=position, claims=claims, note=note)
        )
    return tuple(sections)


def _conflicts_note(conflicts: list[Conflict], limitations: list[Limitation]) -> str:
    if not conflicts and not limitations:
        return EMPTY_SECTION_NOTE
    return (
        f"{len(conflicts)} unresolved conflict(s); {len(limitations)} limitation(s) "
        "— see conflicts and limitations"
    )


def _coverage_note(coverage: CoverageSummary, omissions: list[Omission]) -> str:
    return (
        f"coverage={coverage.label}; supported={coverage.supported} "
        f"incomplete={coverage.incomplete} conflicting={coverage.conflicting}; "
        f"omissions={len(omissions)}"
    )


def _status_for(coverage: CoverageSummary, *, dropped: bool) -> str:
    if dropped:
        return STATUS_PARTIAL
    if coverage.conflicting or coverage.incomplete:
        return STATUS_PARTIAL
    if coverage.supported:
        return STATUS_COMPLETE
    return STATUS_PARTIAL


# ------------------------------------------------------------------ terminal results


def _terminal(
    request: ProjectResumeRequest,
    status: str,
    excluded_count: int,
    timings: dict[str, float],
    *,
    candidates: tuple[ProjectIdentity, ...] = (),
    selection_reason: str = "",
) -> ProjectResumeResult:
    """A safe terminal result for ambiguous/not-found/invalid identity (no evidence work)."""
    sections = _build_sections(
        {key: [] for key, _t in SECTION_ORDER}, CoverageSummary(), [], [], []
    )
    trace = None
    if request.trace_requested:
        trace = ProjectResumeTrace(
            request_id=request.request_id,
            status=status,
            evaluation_time_iso=request.evaluation_time_iso,
            workspace_fingerprint="",
            authorization={
                k: v for k, v in request.authorization_scope.trace_summary().items()
                if k != "request_id"
            },
            excluded_count=excluded_count,
            selection_tier=None,
            selection_reason=selection_reason,
            channels_used=(),
            evidence_ids=(),
            repository_kind=None,
            coverage_label=CoverageSummary().label,
            budgets={
                "evidence": request.evidence_token_budget,
                "output": request.output_token_budget,
            },
            token_counts={},
            omission_reasons=(),
            timings_ms=dict(timings),
        ).to_dict()
    return ProjectResumeResult(
        request_id=request.request_id,
        status=status,
        coverage=CoverageSummary(),
        project_identity=None,
        sections=sections,
        candidates=candidates,
        trace=trace,
    )


# ------------------------------------------------------------------ trace


def _build_trace(
    request: ProjectResumeRequest,
    view: object,
    identity: ProjectIdentity,
    selection_reason: str,
    discovery: object,
    admitted: list[_Bound],
    repository_kind: str | None,
    coverage: CoverageSummary,
    budget_config: BudgetConfig,
    timings: dict[str, float],
) -> ProjectResumeTrace:
    channels = tuple(sorted({b.source.channel for b in admitted}))
    evidence_ids = tuple(sorted(evidence_id_for(b.source) for b in admitted))
    omission_reasons = tuple(
        sorted({o.reason for o in getattr(discovery, "omissions", ())})
    )
    return ProjectResumeTrace(
        request_id=request.request_id,
        status="",  # set by caller context; filled below
        evaluation_time_iso=request.evaluation_time_iso,
        workspace_fingerprint=workspace_fingerprint(getattr(view, "notes", ())),
        authorization={
            k: v for k, v in request.authorization_scope.trace_summary().items()
            if k != "request_id"
        },
        excluded_count=getattr(view, "excluded_count", 0),
        selection_tier=identity.tier,
        selection_reason=selection_reason,
        channels_used=channels,
        evidence_ids=evidence_ids,
        repository_kind=repository_kind,
        coverage_label=coverage.label,
        budgets={
            "evidence": budget_config.evidence_token_budget,
            "output": budget_config.output_token_budget,
            "trace_sub": budget_config.trace_token_sub_budget,
        },
        token_counts={},
        omission_reasons=omission_reasons,
        timings_ms=dict(timings),
    )


# ------------------------------------------------------------------ output budget


def _apply_output_budget(
    result: ProjectResumeResult,
    trace: ProjectResumeTrace | None,
    budget_config: BudgetConfig,
    section_claims: dict[str, list[BriefingClaim]],
    omissions: list[Omission],
) -> ProjectResumeResult:
    """Measure the final serialization; shed lowest-priority claims or fail closed.

    A trace is charged against its sub-budget which lives *inside* the output budget. When even
    the claimless skeleton cannot fit, a bounded ``budget_error`` is returned rather than
    truncating a serialized string (which could sever a citation or invalidate JSON).
    """
    working = {key: list(section_claims.get(key, ())) for key, _t in SECTION_ORDER}
    dropped = 0

    while True:
        current = _rebuild(result, working, omissions, dropped, trace)
        trace_serialized = (
            _serialize(current.trace) if current.trace is not None else None
        )
        check = check_output(
            _serialize(current.to_dict()),
            config=budget_config,
            trace_serialized=trace_serialized,
        )
        if check.ok:
            return current
        victim = _lowest_priority_claim(working)
        if victim is None:
            return _budget_error(result)
        section_key, idx = victim
        working[section_key].pop(idx)
        dropped += 1


def _lowest_priority_claim(working: dict[str, list[BriefingClaim]]) -> tuple[str, int] | None:
    """Pick the least-authoritative claim to shed: weakest section, then last position."""
    for key, _title in reversed(SECTION_ORDER):
        claims = working.get(key, [])
        if claims:
            return key, len(claims) - 1
    return None


def _rebuild(
    base: ProjectResumeResult,
    working: dict[str, list[BriefingClaim]],
    omissions: list[Omission],
    dropped: int,
    trace: ProjectResumeTrace | None,
) -> ProjectResumeResult:
    """Rebuild a result from the surviving claims, recomputing coverage, status, and trace."""
    all_claims = [c for key, _t in SECTION_ORDER for c in working[key]]
    coverage = _coverage(all_claims)
    out_omissions = list(omissions)
    if dropped:
        out_omissions.append(
            Omission(reason="output budget reached", count=dropped, channel=None)
        )
    sections = _build_sections(
        working, coverage, list(base.conflicts), list(base.limitations), out_omissions
    )
    status = _status_for(coverage, dropped=bool(dropped))
    trace_dict = None
    if trace is not None:
        token_counts = {"claims": len(all_claims), "dropped": dropped}
        trace_dict = _finalize_trace(trace, status, coverage, token_counts)
    return ProjectResumeResult(
        request_id=base.request_id,
        status=status,
        coverage=coverage,
        project_identity=base.project_identity,
        sections=sections,
        citations=base.citations,
        repository_citations=base.repository_citations,
        conflicts=base.conflicts,
        omissions=tuple(out_omissions),
        limitations=base.limitations,
        trace=trace_dict,
    )


def _finalize_trace(
    trace: ProjectResumeTrace,
    status: str,
    coverage: CoverageSummary,
    token_counts: dict[str, int],
) -> dict[str, object]:
    final = ProjectResumeTrace(
        request_id=trace.request_id,
        status=status,
        evaluation_time_iso=trace.evaluation_time_iso,
        workspace_fingerprint=trace.workspace_fingerprint,
        authorization=trace.authorization,
        excluded_count=trace.excluded_count,
        selection_tier=trace.selection_tier,
        selection_reason=trace.selection_reason,
        channels_used=trace.channels_used,
        evidence_ids=trace.evidence_ids,
        repository_kind=trace.repository_kind,
        coverage_label=coverage.label,
        budgets=trace.budgets,
        token_counts=token_counts,
        omission_reasons=trace.omission_reasons,
        timings_ms=trace.timings_ms,
    )
    return final.to_dict()


def _budget_error(base: ProjectResumeResult) -> ProjectResumeResult:
    """A bounded, minimal budget_error result (no trace, no claims, identity retained)."""
    sections = _build_sections(
        {key: [] for key, _t in SECTION_ORDER}, CoverageSummary(), [], [], []
    )
    return ProjectResumeResult(
        request_id=base.request_id,
        status=STATUS_BUDGET_ERROR,
        coverage=CoverageSummary(),
        project_identity=base.project_identity,
        sections=sections,
        limitations=(
            Limitation(
                code="output_budget_too_small",
                message="output budget too small for a minimal briefing",
            ),
        ),
    )
