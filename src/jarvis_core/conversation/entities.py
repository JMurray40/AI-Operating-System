"""Lightweight value types for conversation entity memory (session-only).

An entity is a note that has been referenced in the conversation. The session keeps a
most-recent-first stack of these so pronouns and elliptical follow-ups can be resolved to
the topic under discussion. Nothing here is persisted.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MentionedEntity:
    """A note referenced in the conversation, with the turn that surfaced it."""

    relpath: str
    title: str
    id: str | None
    turn: int

    def to_dict(self) -> dict[str, object]:
        return {"relpath": self.relpath, "title": self.title, "id": self.id, "turn": self.turn}
