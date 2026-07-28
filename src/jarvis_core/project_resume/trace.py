"""Project Resume-safe trace composition (ADR-0015/0019/0020, brief §14).

The trace is an *output channel* and receives the same non-disclosure treatment as the
briefing itself: excluded (unauthorized) sources are never identified, quoted, or counted by
sensitive category — only a single aggregate ``excluded_count`` appears — and rejected
ambiguity candidates are never listed. Every structured field is deterministic for identical
snapshot, scope, request, and configuration; only ``timings_ms`` is nondeterministic and is
therefore kept isolated in its own field so the semantic result stays byte-identical.

The trace records the required provenance for A8: the request ID, the workspace fingerprint,
the Project Resume / trace / repository-activity contract versions plus the index version,
the safe authorization summary, the aggregate excluded count, the exact evaluation time, the
selection tier/reason, the discovery channels used, the *included* evidence identities (each
already a safe identity+revision token, never a path), the coverage label, the configured
budgets and measured token counts, and the bounded omission reasons.
"""
from __future__ import annotations

import hashlib
from collections.abc import Iterable
from dataclasses import dataclass, field

from jarvis_core.models.note import Note
from jarvis_core.project_resume.contract import (
    PROJECT_RESUME_CONTRACT_VERSION,
    PROJECT_RESUME_TRACE_VERSION,
    REPOSITORY_ACTIVITY_CONTRACT_VERSION,
)
from jarvis_core.query.contract import INDEX_VERSION


def workspace_fingerprint(notes: Iterable[Note]) -> str:
    """A stable fingerprint over the authorized notes' relpaths + revision fingerprints.

    Mirrors the released query-engine workspace fingerprint: identical authorized snapshots
    yield an identical value, and it discloses no content — only stable relpaths and revision
    hashes of already-authorized sources.
    """
    h = hashlib.sha256()
    for n in sorted(notes, key=lambda n: n.relpath):
        h.update(n.relpath.encode("utf-8"))
        h.update(b"\0")
        h.update(n.source_fingerprint.encode("utf-8"))
        h.update(b"\0")
    return "sha256:" + h.hexdigest()


@dataclass(frozen=True)
class ProjectResumeTrace:
    """A frozen, non-disclosing trace of one Project Resume evaluation."""

    request_id: str
    status: str
    evaluation_time_iso: str
    workspace_fingerprint: str
    authorization: dict[str, object]
    excluded_count: int
    selection_tier: str | None
    selection_reason: str
    channels_used: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    repository_kind: str | None
    coverage_label: str
    budgets: dict[str, int]
    token_counts: dict[str, int]
    omission_reasons: tuple[str, ...]
    contract_version: str = PROJECT_RESUME_TRACE_VERSION
    project_resume_contract_version: str = PROJECT_RESUME_CONTRACT_VERSION
    repository_activity_contract_version: str = REPOSITORY_ACTIVITY_CONTRACT_VERSION
    index_version: str = INDEX_VERSION
    timings_ms: dict[str, float] = field(default_factory=dict)

    def to_dict(self, *, include_timings: bool = True) -> dict[str, object]:
        """Serialize with a fixed field order; timings are isolated and optional.

        ``include_timings=False`` yields the fully deterministic projection used for the
        byte-identical determinism guarantee and for measuring the trace against its
        sub-budget without a nondeterministic timing contribution.
        """
        data: dict[str, object] = {
            "contract_version": self.contract_version,
            "project_resume_contract_version": self.project_resume_contract_version,
            "repository_activity_contract_version": self.repository_activity_contract_version,
            "index_version": self.index_version,
            "request_id": self.request_id,
            "status": self.status,
            "evaluation_time": self.evaluation_time_iso,
            "workspace_fingerprint": self.workspace_fingerprint,
            "authorization": self.authorization,
            "excluded_count": self.excluded_count,
            "selection_tier": self.selection_tier,
            "selection_reason": self.selection_reason,
            "channels_used": list(self.channels_used),
            "evidence_ids": list(self.evidence_ids),
            "repository_kind": self.repository_kind,
            "coverage": self.coverage_label,
            "budgets": dict(self.budgets),
            "token_counts": dict(self.token_counts),
            "omission_reasons": list(self.omission_reasons),
        }
        if include_timings:
            data["timings_ms"] = {k: round(v, 3) for k, v in sorted(self.timings_ms.items())}
        return data

    def render_text(self) -> str:
        """A compact, non-disclosing text rendering of the trace."""
        auth = self.authorization
        lines = ["== TRACE =="]
        lines.append(f"Trace ver    : {self.contract_version}")
        lines.append(f"Resume ver   : {self.project_resume_contract_version}")
        lines.append(f"Repo ver     : {self.repository_activity_contract_version}")
        lines.append(f"Index        : {self.index_version}")
        lines.append(f"Request      : {self.request_id}")
        lines.append(f"Status       : {self.status}")
        lines.append(f"Evaluated at : {self.evaluation_time_iso}")
        lines.append(f"Workspace fp : {self.workspace_fingerprint}")
        lines.append(
            "Authorization: policy={} v{} workspace={} max_sensitivity={}".format(
                auth.get("policy_id"), auth.get("policy_version"),
                auth.get("workspace_id"), auth.get("max_sensitivity"),
            )
        )
        lines.append(f"Excluded     : {self.excluded_count} (aggregate; identities withheld)")
        lines.append(f"Selection    : tier={self.selection_tier} ({self.selection_reason})")
        lines.append(f"Channels     : {', '.join(self.channels_used) or '(none)'}")
        lines.append(f"Evidence     : {len(self.evidence_ids)} included")
        lines.append(f"Repository   : {self.repository_kind or '(none)'}")
        lines.append(f"Coverage     : {self.coverage_label}")
        budgets = ", ".join(f"{k}={v}" for k, v in sorted(self.budgets.items()))
        lines.append(f"Budgets      : {budgets}")
        counts = ", ".join(f"{k}={v}" for k, v in sorted(self.token_counts.items()))
        lines.append(f"Tokens       : {counts}")
        if self.omission_reasons:
            lines.append(f"Omissions    : {'; '.join(self.omission_reasons)}")
        if self.timings_ms:
            timings = ", ".join(
                f"{k}={round(v, 3)}" for k, v in sorted(self.timings_ms.items())
            )
            lines.append(f"Timings (ms) : {timings}")
        return "\n".join(lines)
