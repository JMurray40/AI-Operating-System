"""Frozen, versioned semantic result types for v0.4 Project Resume (ADR-0020).

Every type has deterministic ``to_dict()`` serialization with a fixed field order and no
runtime-only object representations, so identical inputs yield byte-identical structured
output (timings live only in the separate trace/diagnostics field). Vault evidence reuses
the v0.3.1 passage-and-revision :class:`~jarvis_core.query.results.Citation` (ADR-0016);
local Git evidence uses the same trust shape at a different source boundary (ADR-0021).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_core.project_resume.contract import (
    COVERAGE_NONE,
    PROJECT_RESUME_CONTRACT_VERSION,
    REPOSITORY_ACTIVITY_CONTRACT_VERSION,
)
from jarvis_core.query.results import Citation


@dataclass(frozen=True)
class ProjectIdentity:
    """The exactly-selected project's stable identity and the tier that selected it."""

    source_id: str
    identity_kind: str  # 'explicit' | 'path_derived'
    title: str
    relpath: str
    tier: str  # one of contract.IDENTITY_TIERS

    def to_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "identity_kind": self.identity_kind,
            "title": self.title,
            "relpath": self.relpath,
            "tier": self.tier,
        }


@dataclass(frozen=True)
class EvidenceCitation:
    """A vault evidence citation: a discovery channel plus a validated passage citation."""

    evidence_id: str
    channel: str
    channel_reason: str
    citation: Citation

    def to_dict(self) -> dict[str, object]:
        return {
            "evidence_id": self.evidence_id,
            "kind": "vault",
            "channel": self.channel,
            "channel_reason": self.channel_reason,
            "citation": self.citation.to_dict(),
        }


@dataclass(frozen=True)
class RepositoryCitation:
    """A local Git evidence citation, revision-bound to an exact object/HEAD (ADR-0021)."""

    evidence_id: str
    repository_id: str
    head_object_id: str
    record_object_id: str
    committer_iso: str
    author: str
    subject_excerpt: str
    snapshot_fingerprint: str
    record_index: int
    contract_version: str = REPOSITORY_ACTIVITY_CONTRACT_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "evidence_id": self.evidence_id,
            "kind": "repository",
            "contract_version": self.contract_version,
            "repository_id": self.repository_id,
            "head_object_id": self.head_object_id,
            "record_object_id": self.record_object_id,
            "committer_iso": self.committer_iso,
            "author": self.author,
            "subject_excerpt": self.subject_excerpt,
            "snapshot_fingerprint": self.snapshot_fingerprint,
            "record_index": self.record_index,
        }


@dataclass(frozen=True)
class BriefingClaim:
    """A single material statement with typed authority/temporal/support state (ADR-0019/0020)."""

    claim_id: str
    section: str
    position: int
    text: str
    statement_kind: str  # fact | inference | unknown
    authority_class: str
    temporal_state: str  # dated | undated | stale
    support_state: str  # supported | incomplete | conflicting
    evidence_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "claim_id": self.claim_id,
            "section": self.section,
            "position": self.position,
            "text": self.text,
            "statement_kind": self.statement_kind,
            "authority_class": self.authority_class,
            "temporal_state": self.temporal_state,
            "support_state": self.support_state,
            "evidence_ids": list(self.evidence_ids),
        }


@dataclass(frozen=True)
class BriefingSection:
    """One of the ten fixed sections; ``note`` is set when there is no supported evidence."""

    key: str
    title: str
    position: int
    claims: tuple[BriefingClaim, ...] = ()
    note: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "key": self.key,
            "title": self.title,
            "position": self.position,
            "claims": [c.to_dict() for c in self.claims],
            "note": self.note,
        }


@dataclass(frozen=True)
class Conflict:
    """Two or more supported, materially different claims that do not validly supersede."""

    conflict_id: str
    subject: str
    claim_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    note: str

    def to_dict(self) -> dict[str, object]:
        return {
            "conflict_id": self.conflict_id,
            "subject": self.subject,
            "claim_ids": list(self.claim_ids),
            "evidence_ids": list(self.evidence_ids),
            "note": self.note,
        }


@dataclass(frozen=True)
class Omission:
    """A bounded, non-disclosing safe aggregate of what was not included and why."""

    reason: str
    count: int
    channel: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {"reason": self.reason, "count": self.count, "channel": self.channel}


@dataclass(frozen=True)
class Limitation:
    """A visible limitation (unknown, unavailable dependency, staleness, degradation)."""

    code: str
    message: str

    def to_dict(self) -> dict[str, object]:
        return {"code": self.code, "message": self.message}


@dataclass(frozen=True)
class CoverageSummary:
    """Answer-level coverage with supported/incomplete/conflicting counts (ADR-0020)."""

    label: str = COVERAGE_NONE
    supported: int = 0
    incomplete: int = 0
    conflicting: int = 0
    note: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "label": self.label,
            "supported": self.supported,
            "incomplete": self.incomplete,
            "conflicting": self.conflicting,
            "note": self.note,
        }


@dataclass(frozen=True)
class ProjectResumeResult:
    """The complete, frozen, versioned Project Resume result (ADR-0020 §6)."""

    request_id: str
    status: str
    coverage: CoverageSummary
    project_identity: ProjectIdentity | None = None
    sections: tuple[BriefingSection, ...] = ()
    citations: tuple[EvidenceCitation, ...] = ()
    repository_citations: tuple[RepositoryCitation, ...] = ()
    conflicts: tuple[Conflict, ...] = ()
    omissions: tuple[Omission, ...] = ()
    limitations: tuple[Limitation, ...] = ()
    trace: dict[str, object] | None = None
    contract_version: str = PROJECT_RESUME_CONTRACT_VERSION

    # Safe ambiguous candidates (ADR-0018); only populated for status 'ambiguous'.
    candidates: tuple[ProjectIdentity, ...] = field(default=())

    def to_dict(self) -> dict[str, object]:
        return {
            "contract_version": self.contract_version,
            "request_id": self.request_id,
            "status": self.status,
            "project_identity": (
                self.project_identity.to_dict() if self.project_identity is not None else None
            ),
            "candidates": [c.to_dict() for c in self.candidates],
            "sections": [s.to_dict() for s in self.sections],
            "citations": [c.to_dict() for c in self.citations],
            "repository_citations": [c.to_dict() for c in self.repository_citations],
            "conflicts": [c.to_dict() for c in self.conflicts],
            "omissions": [o.to_dict() for o in self.omissions],
            "limitations": [limit.to_dict() for limit in self.limitations],
            "coverage": self.coverage.to_dict(),
            "trace": self.trace,
        }
