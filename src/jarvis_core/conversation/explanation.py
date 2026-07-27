"""Explanation taxonomy: make the *kind* of each claim explicit.

Jarvis distinguishes what it knows from how it knows it. Every element of an answer is
tagged as one of five kinds so the user can tell a retrieved fact from an inference or an
assumption. This is deterministic labelling over the retrieval result, not model output.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class StatementKind(str, Enum):
    FACT = "fact"                 # directly stated in a source note
    INFERENCE = "inference"       # derived from ranking/proximity, not stated verbatim
    RELATIONSHIP = "relationship" # a resolved graph edge between notes
    UNKNOWN = "unknown"           # asked for, not found in the vault
    ASSUMPTION = "assumption"     # a resolution choice Jarvis made (e.g., pronoun target)


@dataclass(frozen=True)
class Statement:
    """One tagged element of an answer's basis."""

    kind: StatementKind
    text: str
    source: str | None = None  # relpath, when the statement is grounded in a note

    def to_dict(self) -> dict[str, object]:
        return {"kind": self.kind.value, "text": self.text, "source": self.source}


def reasoning_summary(statements: tuple[Statement, ...]) -> str:
    """A one-line, human-readable summary of how the answer was reached."""
    counts: dict[str, int] = {}
    for s in statements:
        counts[s.kind.value] = counts.get(s.kind.value, 0) + 1
    if not counts:
        return "No supporting evidence found."
    order = ["fact", "relationship", "inference", "assumption", "unknown"]
    parts = [f"{counts[k]} {k}(s)" for k in order if k in counts]
    return "Answer based on " + ", ".join(parts) + "."
