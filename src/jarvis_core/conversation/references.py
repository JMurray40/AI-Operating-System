"""Deterministic reference resolution for conversational follow-ups.

Resolves pronouns ("it", "they", "its", ...) and elliptical questions ("what are its
risks?") to the entity currently under discussion, using only the session's entity stack.
No ML, no persistence: resolution is a pure function of (input, recent entities), so a
given conversation always resolves the same way.

Retrieved note text is treated as *data*, never as instructions (Chat PRD, req. 9): this
module only ever reads titles/relpaths from the entity stack, never executes note content.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from jarvis_core.conversation.entities import MentionedEntity
from jarvis_core.query.tokenizer import token_set

# Pronouns that signal the user is referring to a previously mentioned entity.
_SUBJECT_PRONOUNS = frozenset(
    {"it", "its", "it's", "this", "that", "they", "them", "their", "theirs",
     "he", "him", "his", "she", "her", "hers", "one"}
)
_PRONOUN_RE = re.compile(r"\b(" + "|".join(sorted(map(re.escape, _SUBJECT_PRONOUNS))) + r")\b")


@dataclass(frozen=True)
class ResolvedInput:
    """The outcome of resolving a raw user turn against conversation memory."""

    raw: str
    effective_query: str
    focus: MentionedEntity | None = None
    assumptions: tuple[str, ...] = ()
    ambiguous: bool = False
    pronouns: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        return {
            "raw": self.raw,
            "effective_query": self.effective_query,
            "focus": self.focus.to_dict() if self.focus else None,
            "assumptions": list(self.assumptions),
            "ambiguous": self.ambiguous,
            "pronouns": list(self.pronouns),
        }


class ReferenceResolver:
    """Resolves pronouns/ellipsis to the most recent in-focus entity."""

    def resolve(self, text: str, entity_stack: list[MentionedEntity]) -> ResolvedInput:
        raw = text.strip()
        pronouns = tuple(dict.fromkeys(_PRONOUN_RE.findall(raw.lower())))
        # If the user named an entity explicitly, prefer that: no substitution needed.
        names_known_entity = any(
            e.title.lower() in raw.lower() for e in entity_stack
        )
        if not pronouns or not entity_stack or names_known_entity:
            return ResolvedInput(raw=raw, effective_query=raw, pronouns=pronouns)

        focus = entity_stack[0]  # most recent
        assumptions = [f"'{pronouns[0]}' refers to '{focus.title}' (most recently discussed)"]
        # Ambiguous only when recent memory spans *unrelated* topics — i.e. the focus title
        # shares no token with another recent entity. A cluster of related notes (all about
        # the same subject) is not ambiguous.
        focus_tokens = token_set(focus.title)
        ambiguous = any(
            e.relpath != focus.relpath and not (focus_tokens & token_set(e.title))
            for e in entity_stack[:3]
        )
        if ambiguous:
            assumptions.append(
                "recent topics were unrelated; chose the most recent entity deterministically"
            )
        # Append the focus title so lexical retrieval anchors on the topic. The original
        # text is preserved for display and intent parsing.
        effective = f"{raw} {focus.title}"
        return ResolvedInput(
            raw=raw,
            effective_query=effective,
            focus=focus,
            assumptions=tuple(assumptions),
            ambiguous=ambiguous,
            pronouns=pronouns,
        )
