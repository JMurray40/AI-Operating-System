"""Deterministic text and JSON rendering of a Project Resume result (brief §9).

Text and JSON consume the *same* frozen semantic result, so they can never disagree. A
supported claim and an incomplete reference are structurally and visibly distinct; a passage
citation is never rendered as ``L0-L0`` (an incomplete reference shows identity + revision
only); inference, conflict, staleness, unavailable dependency, and unknown are labelled; and an
empty content section states "no supported evidence available" rather than asserting none
exist. Ambiguous, not-found, invalid-identity, policy, and budget outcomes map to stable,
distinct process exit codes. No result text is produced through a provider — every rendered
statement is either a validated excerpt or an explicit structural label.
"""
from __future__ import annotations

import json

from jarvis_core.project_resume.contract import (
    AUTHORITY_INFERRED,
    KIND_INFERENCE,
    KIND_UNKNOWN,
    STATUS_AMBIGUOUS,
    STATUS_BUDGET_ERROR,
    STATUS_COMPLETE,
    STATUS_FAILED,
    STATUS_INVALID_IDENTITY,
    STATUS_NOT_FOUND,
    STATUS_PARTIAL,
    STATUS_POLICY_ERROR,
    SUPPORT_CONFLICTING,
    SUPPORT_INCOMPLETE,
    SUPPORT_SUPPORTED,
    TEMPORAL_STALE,
    TEMPORAL_UNDATED,
)
from jarvis_core.project_resume.results import (
    BriefingClaim,
    EvidenceCitation,
    ProjectResumeResult,
    RepositoryCitation,
)

__all__ = ["EXIT_CODES", "exit_code_for", "render_json", "render_text"]

# Stable, distinct process exit codes (brief §9). Success (complete/partial) is 0.
EXIT_CODES: dict[str, int] = {
    STATUS_COMPLETE: 0,
    STATUS_PARTIAL: 0,
    STATUS_FAILED: 1,
    STATUS_AMBIGUOUS: 3,
    STATUS_NOT_FOUND: 4,
    STATUS_INVALID_IDENTITY: 5,
    STATUS_POLICY_ERROR: 6,
    STATUS_BUDGET_ERROR: 7,
}


def exit_code_for(status: str) -> int:
    """Map a result status to its stable process exit code (unknown statuses fail with 1)."""
    return EXIT_CODES.get(status, 1)


def render_json(result: ProjectResumeResult) -> str:
    """Render the canonical, human-readable JSON form of the frozen result."""
    return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)


# ------------------------------------------------------------------ text rendering


def _vault_citation_label(cit: EvidenceCitation) -> str:
    c = cit.citation
    loc = c.locator
    revision = c.source_fingerprint[:12]
    # A validated passage has a real line span; an incomplete reference must NEVER show L0-L0.
    if c.coverage == "supported" and (loc.line_start or loc.line_end):
        where = " > ".join(loc.heading_path) if loc.heading_path else "(frontmatter)"
        return f"{c.title} [{where} L{loc.line_start}-L{loc.line_end}] @{revision}"
    return f"{c.title} [identity+revision only] @{revision}"


def _repository_citation_label(rc: RepositoryCitation) -> str:
    return (
        f"{rc.repository_id}@{rc.record_object_id[:12]} {rc.committer_iso} "
        f"<{rc.author}> #{rc.snapshot_fingerprint[:12]}"
    )


def _citation_index(result: ProjectResumeResult) -> dict[str, str]:
    index: dict[str, str] = {}
    for cit in result.citations:
        index[cit.evidence_id] = _vault_citation_label(cit)
    for rc in result.repository_citations:
        index[rc.evidence_id] = _repository_citation_label(rc)
    return index


def _claim_markers(claim: BriefingClaim) -> list[str]:
    markers: list[str] = []
    if claim.support_state == SUPPORT_CONFLICTING:
        markers.append("conflict")
    elif claim.support_state == SUPPORT_INCOMPLETE:
        markers.append("unverified")
    elif claim.support_state == SUPPORT_SUPPORTED:
        markers.append("supported")
    if claim.statement_kind == KIND_INFERENCE or claim.authority_class == AUTHORITY_INFERRED:
        markers.append("inference")
    if claim.statement_kind == KIND_UNKNOWN:
        markers.append("unknown")
    if claim.temporal_state == TEMPORAL_STALE:
        markers.append("stale")
    elif claim.temporal_state == TEMPORAL_UNDATED:
        markers.append("undated")
    return markers


def _render_claim(claim: BriefingClaim, citations: dict[str, str]) -> list[str]:
    markers = _claim_markers(claim)
    tag = f"[{', '.join(markers)}] " if markers else ""
    lines = [f"  - {tag}{claim.text}"]
    if claim.evidence_ids:
        for evidence_id in claim.evidence_ids:
            label = citations.get(evidence_id, f"(evidence {evidence_id})")
            lines.append(f"      · {label}")
    else:
        lines.append("      · (no current-valid citation)")
    return lines


def _render_header(result: ProjectResumeResult) -> list[str]:
    lines = ["== PROJECT RESUME =="]
    lines.append(f"Status  : {result.status}")
    lines.append(f"Request : {result.request_id}")
    identity = result.project_identity
    if identity is not None:
        lines.append(f"Project : {identity.title} ({identity.relpath}) [tier={identity.tier}]")
    if result.candidates:
        lines.append("Ambiguous candidates (no project selected):")
        for cand in result.candidates:
            lines.append(f"  - {cand.title} ({cand.relpath}) [{cand.source_id}]")
    cov = result.coverage
    lines.append(
        f"Coverage: {cov.label} (supported={cov.supported} "
        f"incomplete={cov.incomplete} conflicting={cov.conflicting})"
    )
    return lines


def render_text(result: ProjectResumeResult) -> str:
    """Render the deterministic plain-text briefing from the frozen semantic result."""
    citations = _citation_index(result)
    lines = _render_header(result)

    for section in result.sections:
        lines.append("")
        lines.append(f"# {section.title}")
        if section.claims:
            for claim in section.claims:
                lines.extend(_render_claim(claim, citations))
        elif section.note:
            lines.append(f"  ({section.note})")
        else:
            lines.append("  (no supported evidence available)")

    if result.conflicts:
        lines.append("")
        lines.append("# Conflicts (retained, not resolved)")
        for conflict in result.conflicts:
            lines.append(f"  - {conflict.subject}: {conflict.note}")
            for evidence_id in conflict.evidence_ids:
                label = citations.get(evidence_id, f"(evidence {evidence_id})")
                lines.append(f"      · {label}")

    if result.limitations:
        lines.append("")
        lines.append("# Limitations")
        for limitation in result.limitations:
            lines.append(f"  - [{limitation.code}] {limitation.message}")

    if result.omissions:
        lines.append("")
        lines.append("# Omissions (bounded, non-disclosing)")
        for omission in result.omissions:
            channel = f" channel={omission.channel}" if omission.channel else ""
            lines.append(f"  - {omission.reason}: {omission.count}{channel}")

    return "\n".join(lines)
