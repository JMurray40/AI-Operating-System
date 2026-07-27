"""Trace mode: a full, inspectable record of how an answer was produced.

A :class:`QueryTrace` captures every decision the engine made -- parsed intent, candidate
notes, ranking explanations, the context that was selected and what was excluded, the
provider used, per-stage timings, and token counts. It is invaluable for debugging why a
question returned what it did. Rendering is deterministic except for the timing block,
which is real wall-clock data and therefore only shown, never asserted on.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_core.query.context_builder import QueryContext
from jarvis_core.query.intent import ParsedQuery
from jarvis_core.query.ranking import ScoredNote


@dataclass
class QueryTrace:
    """Everything needed to explain and debug a single query run."""

    parsed: ParsedQuery
    candidates: tuple[str, ...] = ()
    ranked: tuple[ScoredNote, ...] = ()
    excluded_candidates: tuple[str, ...] = ()
    context: QueryContext | None = None
    provider: str = "none"
    timings_ms: dict[str, float] = field(default_factory=dict)
    token_counts: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "query": self.parsed.question,
            "parsed": self.parsed.to_dict(),
            "candidates": list(self.candidates),
            "ranked": [
                {
                    "relpath": s.relpath,
                    "score": round(s.score, 4),
                    "confidence": s.confidence,
                    "reasons": list(s.explanation.reasons()),
                }
                for s in self.ranked
            ],
            "excluded_candidates": list(self.excluded_candidates),
            "context": self.context.to_dict() if self.context else None,
            "provider": self.provider,
            "timings_ms": {k: round(v, 3) for k, v in self.timings_ms.items()},
            "token_counts": self.token_counts,
        }

    def render_text(self) -> str:
        """Human-readable trace for the terminal."""
        lines: list[str] = []
        lines.append("== TRACE ==")
        lines.append(f"Query        : {self.parsed.question}")
        lines.append(f"Intent       : {self.parsed.intent.value}")
        lines.append(f"Terms        : {', '.join(self.parsed.terms) or '(none)'}")
        if self.parsed.target:
            lines.append(f"Target       : {self.parsed.target}")
        if self.parsed.left or self.parsed.right:
            lines.append(f"Entities     : {self.parsed.left} <-> {self.parsed.right}")
        lines.append(f"Candidates   : {len(self.candidates)}")
        lines.append("Ranking      :")
        if self.ranked:
            for i, s in enumerate(self.ranked, 1):
                reasons = ", ".join(s.explanation.reasons()) or "-"
                lines.append(
                    f"  {i:>2}. {s.relpath}  score={s.score:g} "
                    f"conf={s.confidence:g}  [{reasons}]"
                )
        else:
            lines.append("  (no ranked matches)")
        if self.excluded_candidates:
            lines.append(f"Excluded     : {', '.join(self.excluded_candidates)}")
        if self.context is not None:
            lines.append(
                f"Context      : {len(self.context.included)} note(s), "
                f"{self.context.total_tokens}/{self.context.token_budget} tokens"
            )
            for c in self.context.included:
                lines.append(f"  + [{c.role}] {c.relpath} ({c.tokens} tok)")
            for x in self.context.excluded:
                lines.append(f"  - {x.relpath} ({x.reason})")
        lines.append(f"Provider     : {self.provider}")
        if self.token_counts:
            counts = ", ".join(f"{k}={v}" for k, v in sorted(self.token_counts.items()))
            lines.append(f"Tokens       : {counts}")
        if self.timings_ms:
            timings = ", ".join(
                f"{k}={v:.3f}ms" for k, v in sorted(self.timings_ms.items())
            )
            lines.append(f"Timing       : {timings}")
        return "\n".join(lines)
