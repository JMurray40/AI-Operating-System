"""Centralized, deterministic sensitivity ordering with fail-closed semantics.

Sensitivity ranks from least to most restricted. A note is within a ceiling only when its
label is *known* and ranks at or below the ceiling. Unknown, missing, or invalid labels
fail closed (they are treated as not-permitted), never as unrestricted (ADR-0015).
"""
from __future__ import annotations

from jarvis_core.policy.errors import PolicyError

# Least -> most restricted. The only known labels; anything else fails closed.
_ORDER: tuple[str, ...] = ("public", "internal", "private", "restricted")
_RANK: dict[str, int] = {label: i for i, label in enumerate(_ORDER)}

KNOWN_SENSITIVITIES: frozenset[str] = frozenset(_ORDER)


def ceiling_rank(label: str) -> int:
    """Rank for a *scope ceiling*. The ceiling must be a known label or this fails closed."""
    norm = (label or "").strip().lower()
    if norm not in _RANK:
        raise PolicyError(f"unknown sensitivity ceiling: {label!r}")
    return _RANK[norm]


def within_ceiling(note_label: str | None, ceiling: str) -> bool:
    """True only if ``note_label`` is a known sensitivity at or below ``ceiling``.

    Unknown or missing note labels return False (fail closed): a note whose sensitivity we
    cannot verify must not be treated as unrestricted.
    """
    ceiling_r = ceiling_rank(ceiling)  # validates the ceiling; raises on unknown
    norm = (note_label or "").strip().lower()
    if norm not in _RANK:
        return False
    return _RANK[norm] <= ceiling_r
