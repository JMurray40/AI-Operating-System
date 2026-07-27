"""Read-only, session-only conversational layer over the query engine.

Composed of small collaborators: entity memory, reference resolution, session state,
explanation taxonomy, provenance results, streaming events, and the manager that
orchestrates them. Nothing here persists state or mutates the vault.
"""
from __future__ import annotations

from jarvis_core.conversation.entities import MentionedEntity
from jarvis_core.conversation.explanation import Statement, StatementKind, reasoning_summary
from jarvis_core.conversation.manager import ConversationManager
from jarvis_core.conversation.references import ReferenceResolver, ResolvedInput
from jarvis_core.conversation.results import (
    ConflictNote,
    ConversationAnswer,
    StreamEvent,
    StreamEventKind,
)
from jarvis_core.conversation.session import ConversationSession, Turn
from jarvis_core.conversation.trace import ConversationTrace

__all__ = [
    "ConflictNote",
    "ConversationAnswer",
    "ConversationManager",
    "ConversationSession",
    "ConversationTrace",
    "MentionedEntity",
    "ReferenceResolver",
    "ResolvedInput",
    "Statement",
    "StatementKind",
    "StreamEvent",
    "StreamEventKind",
    "Turn",
    "reasoning_summary",
]
