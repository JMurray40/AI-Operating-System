"""Read-only knowledge repository abstraction.

Application services depend on this Protocol, not on raw filesystem calls, so a
different backing store (e.g. a future indexed service) can replace it without
touching domain logic. There is deliberately no write method: this layer is
read-only by design (see docs/adr and the safety constraints).
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from jarvis_core.models.note import Note


@runtime_checkable
class KnowledgeRepository(Protocol):
    """A read-only source of parsed notes."""

    def discover(self) -> list[Note]:
        """Return all parsed notes in scope (deterministic order)."""

    def all_notes(self) -> list[Note]:
        """Return the cached notes, discovering on first use."""
