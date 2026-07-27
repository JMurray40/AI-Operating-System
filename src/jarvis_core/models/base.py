"""Controlled vocabularies from VAULT_SCHEMA.md and schemas/note.schema.json."""
from __future__ import annotations

from enum import Enum


class NoteType(str, Enum):
    """Registered durable note types (VAULT_SCHEMA.md)."""

    PROJECT = "project"
    AREA = "area"
    CONCEPT = "concept"
    RESEARCH = "research"
    REFERENCE = "reference"
    PLAYBOOK = "playbook"
    PERSON = "person"
    ORGANIZATION = "organization"
    RESOURCE = "resource"
    DECISION = "decision"
    SESSION_SUMMARY = "session-summary"
    PROMPT = "prompt"
    DAILY = "daily"
    MEETING = "meeting"

    @classmethod
    def from_value(cls, value: str | None) -> NoteType | None:
        """Return the matching type or None if unregistered/missing."""
        if value is None:
            return None
        try:
            return cls(value)
        except ValueError:
            return None


class Status(str, Enum):
    """Registered lifecycle statuses."""

    INBOX = "inbox"
    DRAFT = "draft"
    ACTIVE = "active"
    WAITING = "waiting"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    PUBLISHED = "published"
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    IMPLEMENTED = "implemented"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class Sensitivity(str, Enum):
    """Access classification. Anything above ``internal`` must not cross the
    external trust boundary without explicit policy + approval."""

    PUBLIC = "public"
    INTERNAL = "internal"
    PRIVATE = "private"
    RESTRICTED = "restricted"


class LinkKind(str, Enum):
    """How a reference was expressed in source text or metadata."""

    WIKILINK = "wikilink"
    EMBED = "embed"
    MARKDOWN = "markdown"
    FRONTMATTER = "frontmatter"


# Registered vocabularies as plain sets (used by the vocabulary validation stage).
REGISTERED_TYPES: frozenset[str] = frozenset(t.value for t in NoteType)
REGISTERED_STATUSES: frozenset[str] = frozenset(s.value for s in Status)
REGISTERED_SENSITIVITIES: frozenset[str] = frozenset(s.value for s in Sensitivity)

# Common required frontmatter fields (VAULT_SCHEMA.md "Common contract").
COMMON_REQUIRED_FIELDS: tuple[str, ...] = (
    "id",
    "type",
    "title",
    "status",
    "created",
    "updated",
    "sensitivity",
)

# Type-specific minimum additional required fields (VAULT_SCHEMA.md).
TYPE_REQUIRED_FIELDS: dict[str, tuple[str, ...]] = {
    "project": ("goal", "priority"),
    "resource": ("resource_type", "source_of_truth"),
    "decision": ("decision_date",),
    "session-summary": ("session_date", "provider", "objective"),
    "daily": ("date",),
    "research": ("question", "confidence"),
    "meeting": ("meeting_date",),
}
