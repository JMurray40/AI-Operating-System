"""Deterministic, visible reference resolution (R5, C05).

Pure function of visible session focus. A resolved pronoun/ellipsis is recorded as a
*visible assumption* shown before approval — it never silently rewrites intent, and a
materially ambiguous reference is surfaced, not guessed. No excluded state is consulted;
callers pass only authorized, user-visible focus titles.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_PRONOUNS = frozenset({"it", "its", "that", "this", "they", "them", "those", "these"})
_WORD_RE = re.compile(r"[A-Za-z']+")


@dataclass(frozen=True)
class ReferenceAssumption:
    """A visible, deterministic reference-resolution assumption."""

    kind: str  # 'pronoun' | 'ellipsis'
    trigger: str  # the surface token that triggered resolution
    resolved_to: str | None
    status: str  # 'resolved' | 'ambiguous' | 'unresolved'
    basis: str

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "trigger": self.trigger,
            "resolved_to": self.resolved_to,
            "status": self.status,
            "basis": self.basis,
        }


@dataclass(frozen=True)
class ReferenceResolution:
    normalized_text: str
    assumptions: tuple[ReferenceAssumption, ...]

    @property
    def has_ambiguity(self) -> bool:
        return any(a.status == "ambiguous" for a in self.assumptions)


def normalize_user_text(text: str) -> str:
    """Deterministic normalization: strip and collapse internal whitespace."""
    return " ".join(text.split())


def resolve_references(user_text: str, focus_titles: tuple[str, ...]) -> ReferenceResolution:
    """Resolve visible pronouns against the current session focus, deterministically.

    ``focus_titles`` is the ordered, de-duplicated list of user-visible entities the
    session is currently focused on (most recent first). Exactly one focus resolves a
    pronoun; multiple distinct foci mark it ambiguous; none leaves it unresolved.
    """
    normalized = normalize_user_text(user_text)
    tokens = _WORD_RE.findall(normalized.lower())
    triggers = [t for t in tokens if t in _PRONOUNS]
    if not triggers:
        return ReferenceResolution(normalized, ())

    distinct = tuple(dict.fromkeys(focus_titles))  # order-preserving de-dup
    assumptions: list[ReferenceAssumption] = []
    seen: set[str] = set()
    for trig in triggers:
        if trig in seen:
            continue
        seen.add(trig)
        if len(distinct) == 1:
            assumptions.append(
                ReferenceAssumption(
                    kind="pronoun",
                    trigger=trig,
                    resolved_to=distinct[0],
                    status="resolved",
                    basis="single visible session focus",
                )
            )
        elif len(distinct) > 1:
            assumptions.append(
                ReferenceAssumption(
                    kind="pronoun",
                    trigger=trig,
                    resolved_to=None,
                    status="ambiguous",
                    basis=f"{len(distinct)} visible foci; not guessed",
                )
            )
        else:
            assumptions.append(
                ReferenceAssumption(
                    kind="pronoun",
                    trigger=trig,
                    resolved_to=None,
                    status="unresolved",
                    basis="no visible session focus",
                )
            )
    return ReferenceResolution(normalized, tuple(assumptions))


__all__ = [
    "ReferenceAssumption",
    "ReferenceResolution",
    "normalize_user_text",
    "resolve_references",
]
