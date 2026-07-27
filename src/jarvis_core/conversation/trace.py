"""Conversation-aware trace: conversation state plus the underlying query trace."""
from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_core.conversation.entities import MentionedEntity
from jarvis_core.conversation.references import ResolvedInput
from jarvis_core.query.trace import QueryTrace


@dataclass
class ConversationTrace:
    """Everything needed to explain a single conversational turn."""

    turn_index: int
    resolved: ResolvedInput
    entity_stack: tuple[MentionedEntity, ...] = ()
    query_trace: QueryTrace | None = None
    provider: str = "none"
    status: str = "completed"
    timings_ms: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "turn_index": self.turn_index,
            "resolved": self.resolved.to_dict(),
            "entity_stack": [e.to_dict() for e in self.entity_stack],
            "provider": self.provider,
            "status": self.status,
            "timings_ms": {k: round(v, 3) for k, v in self.timings_ms.items()},
            "query_trace": self.query_trace.to_dict() if self.query_trace else None,
        }

    def render_text(self) -> str:
        lines: list[str] = []
        lines.append("== CONVERSATION TRACE ==")
        lines.append(f"Turn         : {self.turn_index}")
        lines.append(f"Raw input    : {self.resolved.raw}")
        lines.append(f"Effective    : {self.resolved.effective_query}")
        if self.resolved.pronouns:
            lines.append(f"Pronouns     : {', '.join(self.resolved.pronouns)}")
        if self.resolved.focus:
            lines.append(f"Focus entity : {self.resolved.focus.title}")
        if self.resolved.assumptions:
            for a in self.resolved.assumptions:
                lines.append(f"Assumption   : {a}")
        if self.entity_stack:
            names = ", ".join(e.title for e in self.entity_stack[:5])
            lines.append(f"Entity memory: {names}")
        lines.append(f"Provider     : {self.provider}")
        lines.append(f"Status       : {self.status}")
        if self.query_trace is not None:
            lines.append("")
            lines.append(self.query_trace.render_text())
        return "\n".join(lines)
