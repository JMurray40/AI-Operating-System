"""Evidence discovery channels for a selected project (ADR-0015/0016, brief §8).

After exact project selection, evidence is discovered through typed channels over the
*authorized view* only: the canonical project passage, notes whose typed ``projects``
metadata resolves to the selected stable identity, authorized outgoing/incoming
relationships, and query retrieval materially bound to the selected project. Each selected
source records its channel and reason. Sources are deduplicated by stable source identity
plus current fingerprint, graph-selected and relevance-ranked sources stay distinct, cycles
terminate by visited identity, and channel/total bounds are enforced with reported,
non-disclosing omissions.

Local repository activity is a separate, grant-gated channel handled by the assembler
through the repository-activity port; it is not discovered here.

This module also binds claims to validated current citations (C6) via the reusable
query-layer citation service, so Project Resume never reimplements citation logic.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_core.models.note import Note
from jarvis_core.project_resume.contract import (
    CHANNEL_CANONICAL,
    CHANNEL_METADATA,
    CHANNEL_RELATIONSHIP,
    CHANNEL_RETRIEVAL,
    COVERAGE_COMPLETE,
    COVERAGE_INCOMPLETE,
    COVERAGE_NONE,
    COVERAGE_PARTIAL,
    SUPPORT_INCOMPLETE,
    SUPPORT_SUPPORTED,
)
from jarvis_core.project_resume.identity import normalize_selector
from jarvis_core.project_resume.results import (
    CoverageSummary,
    EvidenceCitation,
    Omission,
    ProjectIdentity,
)
from jarvis_core.query.authorized import AuthorizedView
from jarvis_core.query.evidence import CitationFactory
from jarvis_core.query.index import LexicalIndex
from jarvis_core.query.ranking import Ranker
from jarvis_core.query.tokenizer import token_set
from jarvis_core.relationships.resolver import ResolutionReport


@dataclass(frozen=True)
class DiscoveryBounds:
    """Configured, testable safety bounds for evidence discovery (brief §8)."""

    max_graph_depth: int = 2
    max_fan_out: int = 25
    max_sources_per_channel: int = 25
    max_total_candidates: int = 100


@dataclass(frozen=True)
class DiscoveredSource:
    """One authorized evidence source, tagged with the channel that first discovered it."""

    relpath: str
    source_id: str
    source_fingerprint: str
    channel: str
    channel_reason: str
    note: Note = field(repr=False, compare=False, default=None)  # type: ignore[assignment]


@dataclass(frozen=True)
class DiscoveryResult:
    """Deduplicated discovered sources plus bounded, non-disclosing omissions."""

    sources: tuple[DiscoveredSource, ...]
    omissions: tuple[Omission, ...]


def _project_terms(project_note: Note, project_identity: ProjectIdentity) -> frozenset[str]:
    terms: set[str] = set()
    terms |= token_set(project_note.title or "")
    terms |= token_set(project_identity.title or "")
    if project_note.id:
        terms |= token_set(project_note.id)
    terms |= token_set(project_note.path.stem)
    return frozenset(terms)


def discover_evidence(
    *,
    view: AuthorizedView,
    report: ResolutionReport,
    index: LexicalIndex,
    ranker: Ranker,
    project_note: Note,
    project_identity: ProjectIdentity,
    bounds: DiscoveryBounds | None = None,
) -> DiscoveryResult:
    """Discover authorized evidence for the selected project across typed channels."""
    bounds = bounds or DiscoveryBounds()
    by_relpath = {n.relpath: n for n in view.notes}
    identities = view.identities
    project_relpath = project_note.relpath

    selected: list[DiscoveredSource] = []
    omissions: list[Omission] = []
    # Dedup by stable identity + current fingerprint; a note keeps its FIRST (strongest) channel.
    claimed: set[tuple[str, str]] = set()

    def key(n: Note) -> tuple[str, str]:
        return (identities[n.relpath].source_id, n.source_fingerprint)

    def add(n: Note, channel: str, reason: str) -> bool:
        k = key(n)
        if k in claimed:
            return False
        claimed.add(k)
        ident = identities[n.relpath]
        selected.append(
            DiscoveredSource(
                relpath=n.relpath, source_id=ident.source_id,
                source_fingerprint=n.source_fingerprint, channel=channel,
                channel_reason=reason, note=n,
            )
        )
        return True

    def add_channel(channel: str, notes: list[Note], reason: str) -> None:
        added = 0
        for n in notes:
            if added >= bounds.max_sources_per_channel:
                dropped = len(notes) - added
                if dropped > 0:
                    omissions.append(
                        Omission(reason="channel source cap reached", count=dropped,
                                 channel=channel)
                    )
                break
            if len(claimed) >= bounds.max_total_candidates:
                omissions.append(
                    Omission(reason="total candidate cap reached", count=1, channel=channel)
                )
                break
            if add(n, channel, reason):
                added += 1

    # 1) Canonical project passage — always the selected project note itself.
    add_channel(CHANNEL_CANONICAL, [project_note], "selected canonical project note")

    # 2) Typed `projects` metadata resolving to the selected stable identity. A reference
    # resolves to the selected project when it exactly matches (after accepted normalization)
    # one of the project's own names: canonical id, title, alias, or filename stem.
    project_names = {
        normalize_selector(x)
        for x in (
            project_identity.source_id,
            project_note.id or "",
            project_note.title or "",
            project_note.path.stem,
            *project_note.aliases,
        )
        if x
    }
    meta: list[Note] = []
    for n in sorted(view.notes, key=lambda x: x.relpath):
        if n.relpath == project_relpath:
            continue
        refs = n.frontmatter_list("projects")
        if any(normalize_selector(r) in project_names for r in refs):
            meta.append(n)
    add_channel(CHANNEL_METADATA, meta, "typed projects metadata references the selected project")

    # 3) Authorized relationships — bounded BFS over outgoing/incoming links.
    graph: list[Note] = []
    visited: set[str] = {project_relpath}
    frontier = [project_relpath]
    depth = 0
    while frontier and depth < bounds.max_graph_depth:
        nxt: list[str] = []
        for rp in frontier:
            neighbours = sorted(set(report.outgoing(rp)) | set(report.incoming(rp)))
            fan = 0
            for tgt in neighbours:
                if fan >= bounds.max_fan_out:
                    omissions.append(
                        Omission(reason="relationship fan-out cap reached", count=1,
                                 channel=CHANNEL_RELATIONSHIP)
                    )
                    break
                if tgt in visited or tgt not in by_relpath:
                    continue
                visited.add(tgt)
                nxt.append(tgt)
                graph.append(by_relpath[tgt])
                fan += 1
        frontier = nxt
        depth += 1
    add_channel(CHANNEL_RELATIONSHIP, graph, "authorized relationship to the selected project")

    # 4) Query retrieval materially bound to the selected project (discovery only, ADR-0014).
    terms = list(_project_terms(project_note, project_identity))
    retrieval: list[Note] = []
    if terms:
        candidates = index.candidates(terms)
        ranked = ranker.rank(terms, candidates, phrase=project_identity.title)
        for scored in ranked:
            match = by_relpath.get(scored.relpath)
            if match is not None and match.relpath != project_relpath:
                retrieval.append(match)
    add_channel(CHANNEL_RETRIEVAL, retrieval, "retrieval materially bound to the selected project")

    return DiscoveryResult(sources=tuple(selected), omissions=tuple(omissions))


# ==================================================================================
# C6 — claim-to-current-citation binding (ADR-0020, brief §9)
#
# Every material claim must be bound to at least one citation validated against CURRENT
# source bytes immediately before emission. Binding never reimplements citation logic: it
# delegates to the reusable query-layer :class:`CitationFactory`, which re-reads the current
# source within the resolved root and validates fingerprint + locator + heading path +
# excerpt. A source that changed, was deleted, is unreadable, or escaped the root fails the
# fingerprint/path check and yields no supported citation, so the claim is marked incomplete
# rather than silently dropped. Metadata-derived claims pass the metadata signal as the
# evidence terms, so ``locate`` cites the metadata-bearing frontmatter locator, not an
# unrelated body passage.
# ==================================================================================


def evidence_id_for(source: DiscoveredSource) -> str:
    """A deterministic evidence id: stable identity + the exact revision it was seen at."""
    return f"ev:{source.source_id}:{source.source_fingerprint[:12]}"


@dataclass(frozen=True)
class EvidenceBinding:
    """The outcome of binding one source to current-validated evidence for a claim."""

    source: DiscoveredSource
    citation: EvidenceCitation | None
    support_state: str  # SUPPORT_SUPPORTED | SUPPORT_INCOMPLETE

    @property
    def is_supported(self) -> bool:
        return self.support_state == SUPPORT_SUPPORTED


def bind_source_citation(
    source: DiscoveredSource,
    *,
    factory: CitationFactory,
    evidence_terms: frozenset[str],
    relevance: float | None = None,
    reason: str | None = None,
) -> EvidenceBinding:
    """Bind one discovered source to a validated current citation (ADR-0020).

    Returns a ``supported`` binding only when the material claim-supporting passage validates
    against current bytes. Otherwise falls back to an identity+revision ``incomplete``
    reference when the source is still current, and to no citation at all when the source is
    stale/deleted/unreadable/escaped — in every non-supported case the claim is ``incomplete``,
    never presented as supported.
    """
    note = source.note
    why = reason if reason is not None else source.channel_reason

    supported = factory.make(
        note, evidence_terms, relevance=relevance, reason=why, material=True
    )
    if supported is not None and supported.coverage == "supported":
        citation = EvidenceCitation(
            evidence_id=evidence_id_for(source),
            channel=source.channel,
            channel_reason=why,
            citation=supported,
        )
        return EvidenceBinding(source, citation, SUPPORT_SUPPORTED)

    # No validated material passage: fall back to a bare identity+revision reference, which the
    # factory emits only when the source is still current (fingerprint matches).
    incomplete = factory.make(
        note, evidence_terms, relevance=relevance, reason=why, material=False
    )
    if incomplete is not None:
        citation = EvidenceCitation(
            evidence_id=evidence_id_for(source),
            channel=source.channel,
            channel_reason=why,
            citation=incomplete,
        )
        return EvidenceBinding(source, citation, SUPPORT_INCOMPLETE)

    # Stale / deleted / unreadable / escaped: the claim keeps no current-valid evidence.
    return EvidenceBinding(source, None, SUPPORT_INCOMPLETE)


def summarize_coverage(
    *, supported: int, incomplete: int, conflicting: int
) -> CoverageSummary:
    """Answer-level coverage label from supported/incomplete/conflicting claim counts.

    Mirrors the released query coverage labels (ADR-0020) and additionally degrades to
    ``partial`` whenever any claim conflicts, so an unresolved conflict never reads as
    ``complete``.
    """
    if supported and not incomplete and not conflicting:
        label = COVERAGE_COMPLETE
    elif supported:
        label = COVERAGE_PARTIAL
    elif incomplete or conflicting:
        label = COVERAGE_INCOMPLETE
    else:
        label = COVERAGE_NONE
    note = (
        None
        if label in (COVERAGE_COMPLETE, COVERAGE_NONE)
        else "one or more claims are incomplete or in unresolved conflict"
    )
    return CoverageSummary(
        label=label,
        supported=supported,
        incomplete=incomplete,
        conflicting=conflicting,
        note=note,
    )
