"""Bounded, volatile, session-only state with deterministic eviction (ADR-0022, R1).

A session holds ordered turns, visible entity focus, the safe trace, and the two-phase
pending state (prepared snapshot + approval + last attempt). Public turn numbers start at
1. Capacity is bounded by turns/tokens/bytes; eviction is deterministic (oldest-first) and
visible, and cannot retain hidden provider or source content. Nothing is persisted; a reset
or process exit erases everything.
"""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field

from jarvis_core.conversation.approval import EgressApproval
from jarvis_core.conversation.context import PreparedTurn
from jarvis_core.conversation.request import HistoryLimits
from jarvis_core.conversation.trace import Trace
from jarvis_core.providers.conversation import CredentialProvider


@dataclass(frozen=True)
class AttemptRecord:
    """A terminal dispatch attempt in the single-use approval lifecycle (AC-05-02)."""

    attempt_id: str
    status: str  # TerminalState value
    kind: str  # 'initial' | 'retry'


@dataclass(frozen=True)
class TurnRecord:
    """A minimal, safe record of a completed turn (no excerpts, no raw payload)."""

    turn_number: int
    request_id: str
    snapshot_digest: str
    user_text: str
    answer_text: str
    coverage: str
    tokens: int
    bytes_len: int

    def to_dict(self) -> dict[str, object]:
        return {
            "turn_number": self.turn_number,
            "request_id": self.request_id,
            "snapshot_digest": self.snapshot_digest,
            "coverage": self.coverage,
        }


@dataclass
class Session:
    """Volatile per-conversation state. Not durable; not logged."""

    workspace_id: str
    history_limits: HistoryLimits
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    turns: list[TurnRecord] = field(default_factory=list)
    focus_titles: tuple[str, ...] = ()
    trace: Trace = field(default_factory=Trace)
    evictions: list[dict[str, object]] = field(default_factory=list)
    _next_turn: int = 1
    pending_prepared: PreparedTurn | None = None
    pending_approval: EgressApproval | None = None
    pending_credentials: CredentialProvider | None = None
    last_attempt_id: str | None = None
    # AC-05-02R single-use approval / attempt lifecycle
    attempts: list[AttemptRecord] = field(default_factory=list)
    approval_consumed: bool = False
    in_flight: bool = False
    # AC-05-02R: guards the check-then-set of in_flight/approval_consumed/attempts so real
    # concurrent callers cannot both observe "not in flight" before either claims it (a bare
    # bool has a TOCTOU race under genuine simultaneous threads, not just sequential tests).
    lock: threading.Lock = field(default_factory=threading.Lock, compare=False, repr=False)
    # AC-05-02R: bumped by every lifecycle invalidation (reset, context removal, a fresh
    # prepare). An attempt captures the generation it started under; on completion it only
    # writes turns/attempts/in_flight back to the session if the generation is unchanged, so
    # a reset/removal that happens while a dispatch is still physically in flight on another
    # thread defeats that late completion instead of silently resurrecting stale state.
    generation: int = 0

    # ---------------------------------------------------------------- turn numbering
    def peek_turn_number(self) -> int:
        return self._next_turn

    def _advance_turn(self) -> int:
        n = self._next_turn
        self._next_turn += 1
        return n

    # ---------------------------------------------------------------- focus
    def set_focus(self, titles: tuple[str, ...]) -> None:
        # Deduplicate preserving order; bound to a small visible window.
        self.focus_titles = tuple(dict.fromkeys(titles))[:16]

    # ---------------------------------------------------------------- history
    def record_turn(
        self,
        *,
        request_id: str,
        snapshot_digest: str,
        user_text: str,
        answer_text: str,
        coverage: str,
    ) -> TurnRecord:
        record = TurnRecord(
            turn_number=self._advance_turn(),
            request_id=request_id,
            snapshot_digest=snapshot_digest,
            user_text=user_text,
            answer_text=answer_text,
            coverage=coverage,
            tokens=len(user_text.split()) + len(answer_text.split()),
            bytes_len=len(user_text.encode("utf-8")) + len(answer_text.encode("utf-8")),
        )
        self.turns.append(record)
        self._evict_if_needed()
        return record

    def _evict_if_needed(self) -> None:
        limits = self.history_limits
        while self.turns and (
            len(self.turns) > limits.max_turns
            or sum(t.tokens for t in self.turns) > limits.max_history_tokens
            or sum(t.bytes_len for t in self.turns) > limits.max_history_bytes
        ):
            if len(self.turns) == 1:
                # A single turn already exceeds a byte/token cap; keep it but record the
                # visible over-limit note rather than looping forever.
                self.evictions.append(
                    {"evicted_turn": self.turns[0].turn_number, "reason": "single_turn_over_limit"}
                )
                break
            dropped = self.turns.pop(0)
            self.evictions.append({"evicted_turn": dropped.turn_number, "reason": "history_limit"})

    def history_text(self) -> str:
        """A bounded, safe history serialization (digests/coverage only, no excerpts)."""
        return "\n".join(f"turn {t.turn_number}: coverage={t.coverage}" for t in self.turns)

    # ---------------------------------------------------------------- lifecycle
    def reset_lifecycle(self) -> None:
        """Invalidate any approval + attempt lifecycle (a new prepare/removal happened)."""
        self.pending_approval = None
        self.attempts.clear()
        self.approval_consumed = False
        self.in_flight = False
        # AC-05-02R: every invalidation is a new generation so a still-running attempt from
        # before this call can detect it happened and defeat its own late completion.
        self.generation += 1

    def clear_pending(self) -> None:
        self.pending_prepared = None
        self.pending_credentials = None
        self.last_attempt_id = None
        self.reset_lifecycle()

    def reset(self) -> None:
        self.turns.clear()
        self.evictions.clear()
        self.focus_titles = ()
        self.trace = Trace()
        self._next_turn = 1
        self.clear_pending()


def new_attempt_id() -> str:
    return "att-" + uuid.uuid4().hex[:16]


__all__ = ["AttemptRecord", "Session", "TurnRecord", "new_attempt_id"]
