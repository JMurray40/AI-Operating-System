"""Versioned, non-disclosing trace of a single query (R6, ADR-0015).

The trace is an output channel and receives the same non-disclosure treatment as answers:
excluded sources are never identified, quoted, or counted by sensitive category — only a
single aggregate ``excluded_count`` appears. Deterministic structured fields are stable for
identical snapshot, scope, request, and configuration; only timing is nondeterministic.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_core.query.context_builder import QueryContext
from jarvis_core.query.intent import ParsedQuery
from jarvis_core.query.ranking import ScoredNote


@dataclass
class QueryTrace:
    """Everything needed to explain and debug a query, safely."""

    parsed: ParsedQuery
    contract_version: str = ""
    index_version: str = ""
    request_id: str = ""
    workspace_fingerprint: str = ""
    authorization: dict[str, object] = field(default_factory=dict)
    excluded_count: int = 0
    provider: str = "none"
    prompt_version: str = "none"
    candidates: tuple[str, ...] = ()
    ranked: tuple[ScoredNote, ...] = ()
    context: QueryContext | None = None
    timings_ms: dict[str, float] = field(default_factory=dict)
    token_counts: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "contract_version": self.contract_version,
            "index_version": self.index_version,
            "request_id": self.request_id,
            "workspace_fingerprint": self.workspace_fingerprint,
            "authorization": self.authorization,
            "excluded_count": self.excluded_count,
            "provider": self.provider,
            "prompt_version": self.prompt_version,
            "query": self.parsed.question,
            "parsed": self.parsed.to_dict(),
            "candidates": list(self.candidates),
            "ranked": [
                {
                    "relpath": s.relpath,
                    "score": round(s.score, 4),
                    "relative_relevance": s.relative_relevance,
                    "reasons": list(s.explanation.reasons()),
                }
                for s in self.ranked
            ],
            "context": self.context.to_dict() if self.context else None,
            "token_counts": self.token_counts,
            "timings_ms": {k: round(v, 3) for k, v in self.timings_ms.items()},
        }

    def render_text(self) -> str:
        lines = ["== TRACE =="]
        lines.append(f"Contract     : {self.contract_version}")
        lines.append(f"Index        : {self.index_version}")
        lines.append(f"Request      : {self.request_id}")
        lines.append(f"Workspace fp : {self.workspace_fingerprint}")
        auth = self.authorization
        lines.append(
            "Authorization: policy={} v{} workspace={} max_sensitivity={}".format(
                auth.get("policy_id"), auth.get("policy_version"),
                auth.get("workspace_id"), auth.get("max_sensitivity"),
            )
        )
        lines.append(f"Excluded     : {self.excluded_count} (aggregate; identities withheld)")
        lines.append(f"Query        : {self.parsed.question}")
        lines.append(f"Intent       : {self.parsed.intent.value}")
        lines.append(f"Terms        : {', '.join(self.parsed.terms) or '(none)'}")
        lines.append(f"Candidates   : {len(self.candidates)}")
        lines.append("Ranking (relative relevance):")
        if self.ranked:
            for i, s in enumerate(self.ranked, 1):
                reasons = ", ".join(s.explanation.reasons()) or "-"
                lines.append(
                    f"  {i:>2}. {s.relpath}  score={s.score:g} "
                    f"rel={s.relative_relevance:g}  [{reasons}]"
                )
        else:
            lines.append("  (no ranked matches)")
        if self.context is not None:
            c = self.context
            lines.append(
                f"Context      : {len(c.included)} note(s), "
                f"{c.total_tokens}/{c.token_budget} tokens, {len(c.excluded)} omitted"
            )
            for ch in c.included:
                flag = " (truncated)" if ch.truncated else ""
                lines.append(f"  + [{ch.role}] {ch.relpath} ({ch.tokens} tok){flag}")
            for x in c.excluded:
                lines.append(f"  - {x.relpath} ({x.reason})")
        lines.append(f"Provider     : {self.provider}  prompt={self.prompt_version}")
        if self.timings_ms:
            t = ", ".join(f"{k}={v:.3f}ms" for k, v in sorted(self.timings_ms.items()))
            lines.append(f"Timing       : {t}")
        return "\n".join(lines)
