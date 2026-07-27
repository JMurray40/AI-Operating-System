"""In-memory conversation session state (never persisted).

Holds the ordered turns and a most-recent-first entity stack for reference resolution,
plus token accounting over the running history. Session memory exists only for the active
process: there is no disk write, no conversation log, and no vault mutation (v0.4 brief).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_core.conversation.entities import MentionedEntity
from jarvis_core.query.context_builder import estimate_tokens


@dataclass(frozen=True)
class Turn:
    """One user input and the answer produced for it."""

    index: int
    user_input: str
    effective_query: str
    answer_text: str
    entities: tuple[MentionedEntity, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "index": self.index,
            "user_input": self.user_input,
            "effective_query": self.effective_query,
            "answer_text": self.answer_text,
            "entities": [e.to_dict() for e in self.entities],
        }


@dataclass
class ConversationSession:
    """Mutable, in-memory conversation state for a single active session."""

    history_token_budget: int = 1500
    _turns: list[Turn] = field(default_factory=list)
    _entity_stack: list[MentionedEntity] = field(default_factory=list)

    @property
    def turn_count(self) -> int:
        return len(self._turns)

    @property
    def entity_stack(self) -> list[MentionedEntity]:
        """Most-recent-first list of entities referenced so far (a copy)."""
        return list(self._entity_stack)

    def focus(self) -> MentionedEntity | None:
        return self._entity_stack[0] if self._entity_stack else None

    def record(
        self,
        user_input: str,
        effective_query: str,
        answer_text: str,
        entities: list[MentionedEntity],
    ) -> Turn:
        """Append a completed turn and push its entities to the front of the stack."""
        turn = Turn(
            index=len(self._turns),
            user_input=user_input,
            effective_query=effective_query,
            answer_text=answer_text,
            entities=tuple(entities),
        )
        self._turns.append(turn)
        # Push newest entities to the front, de-duplicated by relpath (most recent wins).
        # Iterate in reverse so the highest-ranked entity (entities[0]) ends up at the front
        # and becomes the conversational focus for pronoun resolution.
        for ent in reversed(entities):
            self._entity_stack = [e for e in self._entity_stack if e.relpath != ent.relpath]
            self._entity_stack.insert(0, ent)
        return turn

    def history(self) -> list[Turn]:
        return list(self._turns)

    def recent_history(self, budget: int | None = None) -> list[Turn]:
        """Trailing turns whose combined answer text fits the token budget."""
        limit = self.history_token_budget if budget is None else budget
        chosen: list[Turn] = []
        used = 0
        for turn in reversed(self._turns):
            cost = estimate_tokens(turn.user_input) + estimate_tokens(turn.answer_text)
            if used + cost > limit and chosen:
                break
            chosen.append(turn)
            used += cost
        chosen.reverse()
        return chosen

    def reset(self) -> None:
        """Clear all session state (turns and entity memory)."""
        self._turns.clear()
        self._entity_stack.clear()
