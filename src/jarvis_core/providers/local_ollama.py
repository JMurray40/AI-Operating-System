"""Inactive, dependency-injected local Ollama gateway (V05-PT-37; Handoff 147/147b/148).

This module is the "Core-local provider gateway" referenced by Handoff 147 §5: it owns
the local-sensitive profile's fixed identity, frozen numeric contract, readiness/
capacity state machine, the exact prompt template and canonical-serialization rules,
and the hostile-output validation boundary. It is inactive by default (nothing in this
package constructs or wires it automatically) and every seam — capacity sampling, the
clock, the token counter, and the HTTP transport — is dependency-injected so tests
exercise it with fakes/synthetic fixtures only. No test or production call in *this*
task may load a model or contact the live loopback endpoint (Handoff 148 §3); the
``Transport`` protocol reused here (from :mod:`jarvis_core.providers.transport`) is
exercised only by fakes.

Dependency direction (matches ``providers.conversation``'s own module docstring: "the
dependency direction is one-way, conversation depends on providers, never the
reverse"): this module imports nothing from :mod:`jarvis_core.conversation`. Every
type a caller in ``conversation`` needs — ``LocalReadinessState``, ``LocalLimits``,
``LocalWarmClass``, the numeric constants, and the errors below — is defined here and
re-exported by ``conversation.contract``/``conversation.request``, exactly like
``TerminalState``/``UsageProvenance`` already are today. Internal failures raise the
single :class:`LocalGatewayBlocked` (a bare ``code`` string plus safe ``details``);
callers in ``conversation.application`` translate ``code`` into the matching typed
``conversation.contract`` error/``FailureClass`` member.

Scope note (deviation, recorded for the Handoff 149 return): the real
``qwen2-tokenizer-bpe/v1`` artifact and its SHA-256 (Handoff 147b §2.1) are not
available under a mocks/synthetic-fixtures-only authorization (no install/download is
permitted). ``SyntheticTokenCounter`` implements the counting contract's *interface*
and the structural canonical-serialization rules (NFC, LF-only, no NUL, no reserved
role token, JSON canonicalization) deterministically, but its per-token arithmetic is
a synthetic stand-in, not the pinned BPE tokenizer. Binding the real artifact is
explicitly later Engineering-brief work per 147b §2.1.
"""

from __future__ import annotations

import json
import re
import threading
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Protocol, runtime_checkable

from jarvis_core.providers.conversation import (
    CancellationToken,
    Cost,
    NormalizedResult,
    ProviderRequest,
    TerminalState,
    Usage,
    UsageProvenance,
)
from jarvis_core.providers.transport import (
    Transport,
    TransportCancelled,
    TransportError,
    TransportRequest,
    TransportTimeout,
)

ADAPTER_VERSION = "jarvis.provider.local-ollama.v0.5.0"
PROVIDER_ID = "local-ollama"

# V05-PT-37: fixed identity of the inactive constrained-qwen local profile (Handoff
# 147 §1). A ``ProviderProfile.destination_profile_id`` equal to this constant is how
# the application layer recognizes the local-sensitive route.
LOCAL_QWEN_PROFILE_ID = "local-sensitive-conversation/qwen25-7b-constrained-v1"

# Redacted, taxonomic error codes this adapter may set on a non-completed
# ``NormalizedResult`` (mirrors the existing ``ERROR_*`` pattern in
# ``providers.conversation``; deliberately bare strings — this module never imports
# ``FailureClass``, keeping the dependency direction providers -> nothing).
ERROR_LOCAL_NOT_READY = "blocked_local_not_ready"
ERROR_LOCAL_UNAVAILABLE = "blocked_local_unavailable"
ERROR_LOCAL_CAPACITY = "blocked_local_capacity"
ERROR_LOCAL_CONTEXT_LIMIT = "blocked_local_context_limit"
ERROR_LOCAL_TIMEOUT = "blocked_local_timeout"
ERROR_LOCAL_UNSAFE_OUTPUT = "blocked_local_unsafe_output"
ERROR_LOCAL_OUTPUT_CONTRACT = "blocked_local_output_contract"
ERROR_LOCAL_POLICY_DRIFT = "blocked_policy_drift"


class LocalGatewayBlocked(Exception):
    """The one exception this module raises. ``code`` is one of the ``ERROR_LOCAL_*``
    strings above; ``details`` holds only fixed safe fields (never raw runtime/model/
    host/error text). Callers in ``conversation.application`` translate ``code`` into
    the matching typed ``conversation.contract`` error / ``FailureClass`` member.
    """

    def __init__(
        self, code: str, message: str, *, details: dict[str, object] | None = None
    ) -> None:
        super().__init__(message)
        self.code = code
        self.details: dict[str, object] = dict(details or {})


class LocalReadinessState(str, Enum):
    """Categorical local-profile lifecycle states (Handoff 147 §3.2). Closed taxonomy."""

    COLD = "cold"
    WARMING = "warming"
    READY = "ready"
    NOT_READY = "not_ready"
    UNAVAILABLE = "unavailable"


class LocalWarmClass(str, Enum):
    """Supported warm latency classes for the local profile (Handoff 147 §3.1)."""

    LOCAL_S = "LOCAL-S"
    LOCAL_MAX = "LOCAL-MAX"


@dataclass(frozen=True)
class LocalWarmClassSpec:
    """Fixed per-class prompt/output/deadline envelope (147 §3.1, corrected by 147b §2.3)."""

    prompt_tokens_max: int
    num_predict: int
    per_attempt_deadline_seconds: float
    warm_p50_seconds: float
    warm_p95_seconds: float


# 147b §2.3 supersedes 147 §3.1's per-class num_predict (128/256, not a shared 256).
LOCAL_WARM_CLASS_SPECS: dict[LocalWarmClass, LocalWarmClassSpec] = {
    LocalWarmClass.LOCAL_S: LocalWarmClassSpec(
        prompt_tokens_max=1024,
        num_predict=128,
        per_attempt_deadline_seconds=35.0,
        warm_p50_seconds=10.0,
        warm_p95_seconds=25.0,
    ),
    LocalWarmClass.LOCAL_MAX: LocalWarmClassSpec(
        prompt_tokens_max=4096,
        num_predict=256,
        per_attempt_deadline_seconds=60.0,
        warm_p50_seconds=20.0,
        warm_p95_seconds=45.0,
    ),
}


def select_warm_class(prompt_tokens: int) -> LocalWarmClass:
    """Select the exact supported class for a counted prompt (147 Table 3.1).

    ``prompt_tokens`` must already have passed the ``LOCAL_LIMITS.prompt_tokens_max``
    boundary check (``ERROR_LOCAL_CONTEXT_LIMIT`` otherwise) — this only chooses
    between the two supported envelopes for an in-budget prompt.
    """
    if prompt_tokens <= LOCAL_WARM_CLASS_SPECS[LocalWarmClass.LOCAL_S].prompt_tokens_max:
        return LocalWarmClass.LOCAL_S
    return LocalWarmClass.LOCAL_MAX


@dataclass(frozen=True)
class LocalLimits:
    """Frozen prospective numeric limits for the local profile (147 §3, corrected 147b §2.3).

    All counts are pre-provider: Core must reject before prompt assembly/provider
    access on any violation, making zero provider requests. These are intentionally
    distinct from ``conversation.request.Budgets``/``HistoryLimits`` (the existing
    remote-profile budgets), never shared or reused across profiles.
    """

    prompt_tokens_max: int = 4096
    context_tokens_max: int = 3072
    user_text_tokens_max: int = 512
    user_text_bytes_max: int = 4096
    history_tokens_max: int = 256
    context_items_max: int = 12
    provider_num_ctx: int = 4352  # 147b §2.3: fixed 4,096 + 256 for both classes
    raw_response_bytes_max: int = 16384
    answer_bytes_max: int = 8192
    citations_max: int = 12
    in_flight_max_per_process: int = 1
    automatic_retry_max: int = 0


LOCAL_LIMITS = LocalLimits()

# ------------------------------------------------------------------ 147b §3: capacity
ADMISSION_MIN_AVAIL_BYTES = 8 * 1024**3  # 8 GiB
ADMISSION_MAX_LOAD_PERCENT = 80
ADMISSION_SAMPLES = 3
RUNTIME_MIN_AVAIL_BYTES = 6 * 1024**3  # 6 GiB
RUNTIME_LOSS_LOAD_PERCENT = 85  # loss triggers at >=85 (reported ceiling is 84; see below)
RUNTIME_MAX_LOAD_PERCENT_REPORTED = 84  # highest ALLOWED runtime value (147b §3.3)
RUNTIME_SAMPLES = 3
RECOVERY_MIN_AVAIL_BYTES = 10 * 1024**3  # 10 GiB
RECOVERY_MAX_LOAD_PERCENT = 75
RECOVERY_SAMPLES = 10
RECOVERY_INTERVAL_SECONDS = 3.0

# ------------------------------------------------------------------ 147/147b §3.2: readiness
READY_EXPIRY_SECONDS = 600.0  # 10 minutes
COLD_TO_READY_CEILING_SECONDS = 90.0
READINESS_PROBE_DEADLINE_SECONDS = 60.0


@dataclass(frozen=True)
class MemoryObservation:
    """One ``GlobalMemoryStatusEx``-shaped sample (147b §3)."""

    avail_phys_bytes: int
    memory_load_percent: int


@runtime_checkable
class CapacityProbe(Protocol):
    """Injected capacity source. The production Windows probe is out of scope here
    (mocks/synthetic fixtures only, Handoff 148 §3); tests use ``SyntheticCapacityProbe``.
    """

    def sample(self) -> MemoryObservation | None:
        """Return one observation, or ``None`` if the metric is unavailable."""
        ...


class SyntheticCapacityProbe:
    """A deterministic, queue-driven ``CapacityProbe`` test double."""

    def __init__(self, observations: list[MemoryObservation | None] | None = None) -> None:
        self._queue: list[MemoryObservation | None] = list(observations or [])

    def push(self, observation: MemoryObservation | None) -> None:
        self._queue.append(observation)

    def sample(self) -> MemoryObservation | None:
        if not self._queue:
            return None  # an exhausted synthetic queue reads as "metric unavailable"
        return self._queue.pop(0)


@runtime_checkable
class Clock(Protocol):
    """Injected monotonic-seconds clock so lifecycle/expiry tests never sleep for real."""

    def monotonic(self) -> float: ...


class SyntheticClock:
    """A settable, deterministic ``Clock`` test double."""

    def __init__(self, start: float = 0.0) -> None:
        self._now = start

    def monotonic(self) -> float:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now += seconds


def _capacity_details(
    *,
    reason: str,
    observation: MemoryObservation,
    required_mib: int,
    max_load: int,
    consecutive: int,
) -> dict[str, object]:
    return {
        "reason": reason,
        "available_mib": observation.avail_phys_bytes // 1_048_576,
        "required_available_mib": required_mib,
        "memory_load_percent": observation.memory_load_percent,
        "maximum_memory_load_percent": max_load,
        "consecutive_observations": consecutive,
        "recovery_observations_required": RECOVERY_SAMPLES,
        "retry_eligible": True,
    }


class LocalReadinessGateway:
    """The local profile's process-scoped readiness/capacity/in-flight state machine.

    One instance is meant to be constructed once per process and shared by every
    caller (Handoff 147 §3: "one in-flight local attempt per process; no queue").
    Every method that mutates state is protected by an internal lock so concurrent
    callers observe a consistent state machine, matching the existing Core session
    lifecycle's own locking discipline (``conversation.session.Session``).
    """

    def __init__(self, *, capacity_probe: CapacityProbe, clock: Clock) -> None:
        self._capacity_probe = capacity_probe
        self._clock = clock
        self._lock = threading.Lock()
        self._state = LocalReadinessState.COLD
        self._ready_since: float | None = None
        self._warming_started: float | None = None
        self._runtime_violations = 0
        self._recovery_progress = 0
        self._in_flight = False

    @property
    def state(self) -> LocalReadinessState:
        with self._lock:
            return self._state

    # ------------------------------------------------------------------ cold -> ready
    def begin_warming(self) -> None:
        """Enter ``WARMING`` from ``COLD``/``NOT_READY``/``UNAVAILABLE``, synthetic-only."""
        with self._lock:
            if self._state not in (
                LocalReadinessState.COLD,
                LocalReadinessState.NOT_READY,
                LocalReadinessState.UNAVAILABLE,
            ):
                raise LocalGatewayBlocked(
                    ERROR_LOCAL_NOT_READY,
                    f"cannot begin warming from state {self._state.value}",
                    details={"reason": "invalid_transition", "state": self._state.value},
                )
            self._state = LocalReadinessState.WARMING
            self._warming_started = self._clock.monotonic()
            self._runtime_violations = 0

    def complete_warm_up(
        self,
        *,
        min_probe_ok: bool,
        min_probe_elapsed_seconds: float,
        max_probe_ok: bool,
        max_probe_elapsed_seconds: float,
    ) -> None:
        """Finish the exact READY-MIN then READY-MAX ordering (147b §4.1).

        Both probes are supplied by the caller as already-validated outcomes (full
        hostile-output/citation/output-count validation happens through the normal
        response boundary, not here) — this method enforces only the *readiness*
        deadlines and ordering. Any failure leaves the gateway ``UNAVAILABLE``; no
        automatic retry.
        """
        with self._lock:
            if self._state is not LocalReadinessState.WARMING or self._warming_started is None:
                raise LocalGatewayBlocked(
                    ERROR_LOCAL_NOT_READY,
                    "complete_warm_up called outside an active warm-up",
                    details={"reason": "invalid_transition", "state": self._state.value},
                )
            started = self._warming_started
            now = self._clock.monotonic()
            failure: LocalGatewayBlocked | None = None
            if not min_probe_ok or min_probe_elapsed_seconds > READINESS_PROBE_DEADLINE_SECONDS:
                failure = LocalGatewayBlocked(
                    ERROR_LOCAL_UNAVAILABLE,
                    "READY-MIN probe failed or exceeded its 60s deadline",
                    details={"reason": "min_probe_failed", "elapsed_s": min_probe_elapsed_seconds},
                )
            elif not max_probe_ok or max_probe_elapsed_seconds > READINESS_PROBE_DEADLINE_SECONDS:
                failure = LocalGatewayBlocked(
                    ERROR_LOCAL_UNAVAILABLE,
                    "READY-MAX probe failed or exceeded its 60s deadline",
                    details={"reason": "max_probe_failed", "elapsed_s": max_probe_elapsed_seconds},
                )
            elif (now - started) > COLD_TO_READY_CEILING_SECONDS:
                failure = LocalGatewayBlocked(
                    ERROR_LOCAL_UNAVAILABLE,
                    "cold-to-ready sequence exceeded its 90s ceiling",
                    details={"reason": "cold_to_ready_ceiling", "elapsed_s": now - started},
                )
            if failure is not None:
                self._state = LocalReadinessState.UNAVAILABLE
                self._warming_started = None
                raise failure
            self._state = LocalReadinessState.READY
            self._ready_since = now
            self._warming_started = None

    # -------------------------------------------------------------- pre-retrieval / pre-dispatch
    def check_admission(self) -> None:
        """Verify readiness + capacity BEFORE retrieval/prompt assembly/provider access.

        Raises exactly one typed error and otherwise returns ``None``. Sampling a
        capacity violation leaves readiness UNCHANGED (147b §3.1); an exhausted or
        unavailable metric makes the profile ``unavailable`` rather than guessed.
        """
        with self._lock:
            if self._in_flight:
                # 147 §3: one in-flight attempt per process, no queue. Not one of the
                # seven named public outcomes; treated conservatively as "not ready to
                # accept a new attempt right now" rather than inventing an unlisted
                # FailureClass member. Flagged as an explicit deviation in Handoff 149.
                raise LocalGatewayBlocked(
                    ERROR_LOCAL_NOT_READY,
                    "a local attempt is already in flight for this process; no queue",
                    details={"reason": "in_flight", "retry_eligible": True},
                )
            if self._state is LocalReadinessState.UNAVAILABLE:
                raise LocalGatewayBlocked(
                    ERROR_LOCAL_UNAVAILABLE,
                    "local profile is unavailable", details={"reason": "unavailable"}
                )
            if self._state in (LocalReadinessState.COLD, LocalReadinessState.WARMING):
                raise LocalGatewayBlocked(
                    ERROR_LOCAL_NOT_READY,
                    f"local profile is {self._state.value}",
                    details={"reason": self._state.value, "retry_eligible": True},
                )
            if self._state is LocalReadinessState.NOT_READY:
                raise LocalGatewayBlocked(
                    ERROR_LOCAL_NOT_READY,
                    "local profile is not ready",
                    details={"reason": "not_ready", "retry_eligible": True},
                )
            # READY: check the 10-minute expiry before spending a capacity sample.
            assert self._ready_since is not None
            now = self._clock.monotonic()
            if (now - self._ready_since) > READY_EXPIRY_SECONDS:
                self._state = LocalReadinessState.NOT_READY
                raise LocalGatewayBlocked(
                    ERROR_LOCAL_NOT_READY,
                    "readiness expired (10 minutes since the last successful validated turn)",
                    details={"reason": "expired", "retry_eligible": True},
                )
            self._check_admission_capacity_locked()

    def _check_admission_capacity_locked(self) -> None:
        last_observation: MemoryObservation | None = None
        for index in range(1, ADMISSION_SAMPLES + 1):
            observation = self._capacity_probe.sample()
            if observation is None:
                self._state = LocalReadinessState.UNAVAILABLE
                raise LocalGatewayBlocked(
                    ERROR_LOCAL_UNAVAILABLE,
                    "capacity metric unavailable", details={"reason": "metric_unavailable"}
                )
            last_observation = observation
            violates = (
                observation.avail_phys_bytes < ADMISSION_MIN_AVAIL_BYTES
                or observation.memory_load_percent > ADMISSION_MAX_LOAD_PERCENT
            )
            if violates:
                raise LocalGatewayBlocked(
                    ERROR_LOCAL_CAPACITY,
                    "insufficient capacity for admission",
                    details=_capacity_details(
                        reason="admission_memory",
                        observation=observation,
                        required_mib=ADMISSION_MIN_AVAIL_BYTES // 1_048_576,
                        max_load=ADMISSION_MAX_LOAD_PERCENT,
                        consecutive=index,
                    ),
                )
        assert last_observation is not None

    # ------------------------------------------------------------------ in-flight (147 §3)
    def begin_attempt(self) -> None:
        with self._lock:
            if self._in_flight:
                raise LocalGatewayBlocked(
                    ERROR_LOCAL_NOT_READY,
                    "a local attempt is already in flight for this process; no queue",
                    details={"reason": "in_flight", "retry_eligible": True},
                )
            self._in_flight = True

    def end_attempt(self, *, success: bool) -> None:
        with self._lock:
            self._in_flight = False
            if success and self._state is LocalReadinessState.READY:
                self._ready_since = self._clock.monotonic()

    # ------------------------------------------------------------------ runtime capacity loss
    def observe_runtime_capacity(self, observation: MemoryObservation | None) -> bool:
        """Feed one runtime capacity sample; return True iff readiness was just lost.

        147b §3.1: while ``ready`` or an attempt is in flight, sample once per second;
        three CONSECUTIVE violating samples cause readiness loss (cancel the in-flight
        attempt, discard the response, publish nothing, enter ``not_ready``).
        Cancellation failure enters ``unavailable`` — modeled here by the caller
        invoking :meth:`mark_cancellation_failed` if cooperative cancellation itself
        fails.
        """
        with self._lock:
            if self._state not in (LocalReadinessState.READY,) and not self._in_flight:
                return False
            if observation is None:
                self._state = LocalReadinessState.UNAVAILABLE
                self._runtime_violations = 0
                return True
            violates = (
                observation.avail_phys_bytes < RUNTIME_MIN_AVAIL_BYTES
                or observation.memory_load_percent >= RUNTIME_LOSS_LOAD_PERCENT
            )
            if not violates:
                self._runtime_violations = 0
                return False
            self._runtime_violations += 1
            if self._runtime_violations >= RUNTIME_SAMPLES:
                self._state = LocalReadinessState.NOT_READY
                self._runtime_violations = 0
                return True
            return False

    def mark_cancellation_failed(self) -> None:
        with self._lock:
            self._state = LocalReadinessState.UNAVAILABLE

    def mark_output_contract_violation(self) -> None:
        """Handoff 150 §3 (PT37-CTO-02): any mismatch between the request Jarvis sent
        (exact model identity, ``stream=false``, ``num_ctx``, class-specific
        ``num_predict``) and the parsed Ollama response envelope (returned model,
        ``prompt_eval_count``, ``eval_count``, ``done_reason``) means the provider
        itself is behaving unexpectedly for this fixed contract -- the raw content is
        discarded (never retained, never returned) and the gateway falls back to
        ``not_ready`` rather than staying ``ready`` for a provider that just failed to
        honor its own frozen envelope. Distinct from ``mark_cancellation_failed``
        (``unavailable``): an output-contract violation is retry-eligible after a
        fresh readiness sequence, not a hard failure."""
        with self._lock:
            self._state = LocalReadinessState.NOT_READY

    # ------------------------------------------------------------------ recovery (147b §3.2)
    def begin_recovery(self) -> None:
        with self._lock:
            self._recovery_progress = 0

    def observe_recovery_sample(self, observation: MemoryObservation | None) -> bool:
        """Feed one 3-second-interval recovery sample; return True once recovered.

        10 consecutive samples all meeting the 10 GiB / <=75% bar are required; any
        violating sample resets the consecutive count to zero (147b §3.2). Recovery
        alone does not re-enter ``ready`` — the full identity/confinement/probe
        sequence (``begin_warming``/``complete_warm_up``) must still run.
        """
        with self._lock:
            ok = (
                observation is not None
                and observation.avail_phys_bytes >= RECOVERY_MIN_AVAIL_BYTES
                and observation.memory_load_percent <= RECOVERY_MAX_LOAD_PERCENT
            )
            if not ok:
                self._recovery_progress = 0
                return False
            self._recovery_progress += 1
            return self._recovery_progress >= RECOVERY_SAMPLES


# ------------------------------------------------------------------ 147b §2.2: canonical text
_RESERVED_ROLE_TOKENS = ("<|im_start|>", "<|im_end|>")


def validate_canonical_text(text: str, *, field_name: str) -> None:
    """Reject non-UTF-8-safe/non-NFC/CR/NUL/reserved-token content (147b §2.2).

    Core does not normalize or escape silently; any violation is a policy-drift
    block before retrieval or prompt assembly.
    """
    if "\x00" in text:
        raise LocalGatewayBlocked(
            ERROR_LOCAL_POLICY_DRIFT,
            f"{field_name} contains NUL", details={"reason": "nul_byte", "field": field_name}
        )
    if "\r" in text:
        raise LocalGatewayBlocked(
            ERROR_LOCAL_POLICY_DRIFT,
            f"{field_name} is not LF-only", details={"reason": "cr_present", "field": field_name}
        )
    if unicodedata.normalize("NFC", text) != text:
        raise LocalGatewayBlocked(
            ERROR_LOCAL_POLICY_DRIFT,
            f"{field_name} is not Unicode NFC", details={"reason": "non_nfc", "field": field_name}
        )
    for token in _RESERVED_ROLE_TOKENS:
        if token in text:
            raise LocalGatewayBlocked(
                ERROR_LOCAL_POLICY_DRIFT,
                f"{field_name} contains a reserved role token",
                details={"reason": "reserved_token", "field": field_name},
            )


def canonical_json(obj: object) -> str:
    """UTF-8, no BOM, sorted keys, ``,``/``:`` separators, non-ASCII encoded directly."""
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


# ------------------------------------------------------------------ 147b §2.1: counting (synthetic)
@runtime_checkable
class TokenCounter(Protocol):
    """Injected counter. See module docstring: no real BPE tokenizer in this task."""

    def count(self, text: str) -> int: ...


class SyntheticTokenCounter:
    """Deterministic, dependency-free stand-in for ``qwen2-tokenizer-bpe/v1``.

    NOT the pinned tokenizer (module docstring). Whitespace/punctuation-aware so it
    is stable and reproducible for boundary tests, but it must never be presented as
    a conformance-corpus-validated count.
    """

    _WORD_OR_PUNCT_RE = re.compile(r"[^\W_]+|[^\w\s]", re.UNICODE)

    def count(self, text: str) -> int:
        """Every word-run and every punctuation character counts as one token.

        Stable and deterministic for the same input; not the real BPE tokenizer.
        """
        if not text or not text.strip():
            return 0
        return len(self._WORD_OR_PUNCT_RE.findall(text))


# ------------------------------------------------------------------ 147b §2.2: prompt template
_SYSTEM_TEMPLATE = "<|im_start|>system\n{system}<|im_end|>\n"
_USER_TEMPLATE = "<|im_start|>user\n{user}<|im_end|>\n"
_ASSISTANT_PREFIX = "<|im_start|>assistant\n"


def build_qwen_prompt(*, system_instruction: str, user_text: str) -> str:
    """The exact provider prompt (147b §2.2). No BOS/EOS outside this template."""
    return (
        _SYSTEM_TEMPLATE.format(system=system_instruction)
        + _USER_TEMPLATE.format(user=user_text)
        + _ASSISTANT_PREFIX
    )


# ------------------------------------------------------------------ 147 §4: hostile-output boundary
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_BIDI_OVERRIDE_RE = re.compile("[‪-‮⁦-⁩]")
_SCRIPT_MARKUP_RE = re.compile(
    r"<\s*(script|iframe|object|embed|style)\b|on\w+\s*=|javascript:|data:text/html",
    re.IGNORECASE,
)
_URI_SCHEME_RE = re.compile(r"\b(?:file|ftp|javascript|data|vbscript)://", re.IGNORECASE)
_ABS_OR_TRAVERSAL_PATH_RE = re.compile(
    r"(?:(?<=[\s(\"'])|^)/[^\s\"']+"  # absolute POSIX path
    r"|[A-Za-z]:\\[^\s\"']*"  # absolute Windows path (C:\...)
    r"|\\\\[^\s\"']+"  # UNC path (\\server\share)
    r"|\.\./|\.\.\\"  # path traversal
)
_SECRET_LIKE_RE = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|\bAKIA[0-9A-Z]{16}\b"
    r"|\bsk-[A-Za-z0-9]{16,}\b"
    r"|\bghp_[A-Za-z0-9]{20,}\b"
    r"|\bxox[abpr]-[A-Za-z0-9-]{10,}\b"
)
_PROVIDER_ERROR_SYNTAX_RE = re.compile(
    r"\btraceback \(most recent call last\)|\bstack trace\b|\bexception in thread\b",
    re.IGNORECASE,
)

_HOSTILE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("control_char", _CONTROL_CHARS_RE),
    ("bidi_override", _BIDI_OVERRIDE_RE),
    ("script_or_markup", _SCRIPT_MARKUP_RE),
    ("uri_scheme", _URI_SCHEME_RE),
    ("path_like", _ABS_OR_TRAVERSAL_PATH_RE),
    ("secret_like", _SECRET_LIKE_RE),
    ("provider_error_syntax", _PROVIDER_ERROR_SYNTAX_RE),
)

# V05-PT-37 / Handoff 151, 151a (PT37-CTO-03 closure): the closed local response
# shape is amended from the flat ``{"answer","limitations","citations"}`` (147/150)
# to ``{"claims": [{"text","type","evidence"}, ...], "limitations": [str, ...]}`` --
# structurally mirroring the remote/mock claims taxonomy's field names so the
# validated shape can be routed unchanged into ``evidence.validate_response``
# (Handoff 151 §3, 151a §3 item 2). ``_ALLOWED_CLAIM_TYPES`` is a LITERAL duplicate
# of ``jarvis_core.conversation.contract.EvidenceType``'s exact value strings, never
# an import: providers must never depend on conversation (conversation -> providers
# is the only allowed dependency direction; contract.py itself re-exports
# ``LocalReadinessState`` FROM this module for the same reason, in the other
# direction). This module only proves the value is one of the five recognized
# taxonomy strings; it never itself decides fact/inference exact-support -- that
# stays exclusively in ``evidence.validate_response``, the single source of truth
# for the taxonomy.
_ALLOWED_RESPONSE_KEYS = frozenset({"claims", "limitations"})
_ALLOWED_CLAIM_KEYS = frozenset({"text", "type", "evidence"})
_ALLOWED_CLAIM_TYPES = frozenset(
    {"fact", "inference", "model_knowledge", "unknown", "assumption"}
)


def _reject_hostile_text(text: str, *, field_name: str) -> None:
    for name, pattern in _HOSTILE_PATTERNS:
        if pattern.search(text):
            raise LocalGatewayBlocked(
                ERROR_LOCAL_UNSAFE_OUTPUT,
                f"{field_name} contains hostile content ({name})",
                details={"reason": name, "field": field_name},
            )


@dataclass(frozen=True)
class LocalClaim:
    """One validated claim in the closed local response shape (147 §4, amended by
    Handoff 151/151a). ``type`` is checked only against the literal
    ``_ALLOWED_CLAIM_TYPES`` allowlist here -- the real taxonomy/support semantics
    are applied once, downstream, by ``evidence.validate_response``.
    """

    text: str
    type: str
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class LocalResponse:
    """The validated, closed local response shape (147 §4, amended by Handoff 151/151a)."""

    claims: tuple[LocalClaim, ...]
    limitations: tuple[str, ...]


def validate_local_response(
    raw_bytes: bytes,
    *,
    allowed_citation_ids: frozenset[str],
    limits: LocalLimits = LOCAL_LIMITS,
) -> LocalResponse:
    """The complete hostile-output validation boundary (147 §4), amended by Handoff
    151/151a (V05-PT-37 PT37-CTO-03 closure).

    This proves only the LOCAL closed-schema/hostile-content boundary -- shape,
    per-claim taxonomy-string allowlist, per-claim-text/per-limitation hostile-
    content and (claim text only, mirroring the retired ``answer`` field's prior
    scope) canonical-text rules, and citation-id-exists-in-allowlist. It never
    performs current-byte revalidation, exact-support matching, or coverage
    derivation -- ``application.py`` routes this validated shape unchanged into
    ``evidence.validate_response``, the sole owner of that taxonomy (Handoff 151a
    §3 item 2).

    Retains raw bytes only for the duration of this call (no bounded buffer is
    retained by the caller beyond it); raises exactly one typed error on any
    violation and never returns a partially-sanitized value ("no substring
    surgery"). The caller must discard ``raw_bytes`` immediately after this call
    whether it raises or returns.
    """
    if len(raw_bytes) > limits.raw_response_bytes_max:
        raise LocalGatewayBlocked(
            ERROR_LOCAL_OUTPUT_CONTRACT,
            "raw response exceeds the bounded validation buffer",
            details={
                "reason": "raw_bytes_exceeded",
                "actual": len(raw_bytes),
                "limit": limits.raw_response_bytes_max,
            },
        )
    try:
        text = raw_bytes.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise LocalGatewayBlocked(
            ERROR_LOCAL_OUTPUT_CONTRACT,
            "raw response is not valid UTF-8", details={"reason": "invalid_utf8"}
        ) from exc
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as exc:
        raise LocalGatewayBlocked(
            ERROR_LOCAL_OUTPUT_CONTRACT,
            "raw response is not a valid JSON object", details={"reason": "invalid_json"}
        ) from exc
    if not isinstance(obj, dict):
        raise LocalGatewayBlocked(
            ERROR_LOCAL_OUTPUT_CONTRACT,
            "raw response is not a JSON object", details={"reason": "not_an_object"}
        )
    extra_keys = set(obj.keys()) - _ALLOWED_RESPONSE_KEYS
    if extra_keys:
        # PT37-CTO-05: the unknown key NAMES themselves are untrusted provider/model-
        # controlled text (this is the same closed response an adversarial local model
        # could shape) -- only a count is recorded in details, never the literal key
        # strings, mirroring the envelope unknown-fields check below. Never a raw-
        # content leak channel.
        raise LocalGatewayBlocked(
            ERROR_LOCAL_OUTPUT_CONTRACT,
            "raw response has unknown fields",
            details={"reason": "unknown_fields", "count": len(extra_keys)},
        )
    raw_claims = obj.get("claims")
    limitations = obj.get("limitations", [])
    if not isinstance(raw_claims, list):
        raise LocalGatewayBlocked(
            ERROR_LOCAL_OUTPUT_CONTRACT,
            "claims field is missing or wrong-typed", details={"reason": "claims_wrong_type"}
        )
    if not raw_claims:
        raise LocalGatewayBlocked(
            ERROR_LOCAL_OUTPUT_CONTRACT,
            "claims field is empty", details={"reason": "claims_empty"}
        )
    if not isinstance(limitations, list) or not all(isinstance(x, str) for x in limitations):
        raise LocalGatewayBlocked(
            ERROR_LOCAL_OUTPUT_CONTRACT,
            "limitations field is wrong-typed", details={"reason": "limitations_wrong_type"}
        )

    claims: list[LocalClaim] = []
    total_citation_refs = 0
    for index, raw_claim in enumerate(raw_claims):
        if not isinstance(raw_claim, dict):
            raise LocalGatewayBlocked(
                ERROR_LOCAL_OUTPUT_CONTRACT,
                "claim is not an object",
                details={"reason": "claim_not_an_object", "index": index},
            )
        claim_extra_keys = set(raw_claim.keys()) - _ALLOWED_CLAIM_KEYS
        if claim_extra_keys:
            # PT37-CTO-05: same rationale as the top-level unknown-fields check above --
            # only a count and the (Core-computed, safe) numeric claim index are
            # recorded, never the untrusted key names themselves.
            raise LocalGatewayBlocked(
                ERROR_LOCAL_OUTPUT_CONTRACT,
                "claim has unknown fields",
                details={
                    "reason": "claim_unknown_fields",
                    "index": index,
                    "count": len(claim_extra_keys),
                },
            )
        claim_text = raw_claim.get("text")
        claim_type = raw_claim.get("type")
        claim_evidence = raw_claim.get("evidence", [])
        if not isinstance(claim_text, str):
            raise LocalGatewayBlocked(
                ERROR_LOCAL_OUTPUT_CONTRACT,
                "claim text is missing or wrong-typed",
                details={"reason": "claim_text_wrong_type", "index": index},
            )
        if not isinstance(claim_type, str) or claim_type not in _ALLOWED_CLAIM_TYPES:
            raise LocalGatewayBlocked(
                ERROR_LOCAL_OUTPUT_CONTRACT,
                "claim type is missing, wrong-typed, or not a recognized claim type",
                details={"reason": "claim_type_invalid", "index": index},
            )
        if not isinstance(claim_evidence, list) or not all(
            isinstance(x, str) for x in claim_evidence
        ):
            raise LocalGatewayBlocked(
                ERROR_LOCAL_OUTPUT_CONTRACT,
                "claim evidence is wrong-typed",
                details={"reason": "claim_evidence_wrong_type", "index": index},
            )
        if len(claim_evidence) != len(set(claim_evidence)):
            raise LocalGatewayBlocked(
                ERROR_LOCAL_OUTPUT_CONTRACT,
                "duplicate evidence ids within one claim",
                details={"reason": "duplicate_claim_evidence", "index": index},
            )
        if len(claim_text.encode("utf-8")) > limits.answer_bytes_max:
            raise LocalGatewayBlocked(
                ERROR_LOCAL_OUTPUT_CONTRACT,
                "claim text exceeds the validated answer-text byte limit",
                details={
                    "reason": "claim_text_bytes_exceeded",
                    "index": index,
                    "limit": limits.answer_bytes_max,
                },
            )
        for citation_id in claim_evidence:
            if citation_id not in allowed_citation_ids:
                # PT37-CTO-07: citation_id is an arbitrary, untrusted string supplied by the
                # local model in the raw response -- the same class of raw-content leak
                # channel PT37-CTO-05 closed for unknown key names. Only the fixed reason and
                # the Core-computed, safe numeric claim index are recorded; the untrusted
                # identifier itself must never cross into details.
                raise LocalGatewayBlocked(
                    ERROR_LOCAL_UNSAFE_OUTPUT,
                    "citation id is absent from the immutable current snapshot",
                    details={
                        "reason": "fake_citation",
                        "index": index,
                    },
                )
        _reject_hostile_text(claim_text, field_name=f"claims[{index}].text")
        validate_canonical_text(claim_text, field_name=f"claims[{index}].text")
        total_citation_refs += len(claim_evidence)
        claims.append(
            LocalClaim(text=claim_text, type=claim_type, evidence=tuple(claim_evidence))
        )

    if total_citation_refs > limits.citations_max:
        raise LocalGatewayBlocked(
            ERROR_LOCAL_OUTPUT_CONTRACT,
            "too many citations",
            details={
                "reason": "citations_exceeded",
                "actual": total_citation_refs,
                "limit": limits.citations_max,
            },
        )
    for limitation in limitations:
        _reject_hostile_text(limitation, field_name="limitations")

    return LocalResponse(claims=tuple(claims), limitations=tuple(limitations))


_ALLOWED_ENVELOPE_KEYS = frozenset(
    {
        "model",
        "created_at",
        "response",
        "done",
        "done_reason",
        "context",
        "total_duration",
        "load_duration",
        "prompt_eval_count",
        "prompt_eval_duration",
        "eval_count",
        "eval_duration",
    }
)
# Handoff 150 §3 (PT37-CTO-02): the only terminal reason accepted as a genuine
# completion for this fixed, non-streaming contract. Any other value (``"length"``
# truncation, ``"load"``, an unset/unknown reason, and so on) is a provider-window
# contract mismatch, not a completion -- explicit judgment call recorded for Handoff
# 149/150's return, since 147/147b freeze ``eval_count <= num_predict`` and a
# ``done_reason`` check but do not enumerate every possible Ollama terminal string.
_ACCEPTED_DONE_REASON = "stop"


@dataclass(frozen=True)
class _OllamaEnvelopeOk:
    """The extracted, still-untrusted local-schema payload bytes, once the envelope
    itself (model identity, counts, terminal reason) has been verified against the
    exact request Jarvis sent. Callers must still run this through
    :func:`validate_local_response` before treating it as safe."""

    response_bytes: bytes


def _parse_and_verify_ollama_envelope(
    raw_bytes: bytes,
    *,
    expected_model: str,
    expected_prompt_tokens: int,
    num_predict_limit: int,
    limits: LocalLimits = LOCAL_LIMITS,
) -> _OllamaEnvelopeOk:
    """Handoff 150 §3 (PT37-CTO-02): parse the real, non-streaming Ollama
    ``/api/generate`` completion envelope and verify it against the EXACT request
    this adapter sent -- returned ``model``, ``prompt_eval_count`` (must equal the
    counted prompt Jarvis actually sent), ``eval_count`` (must not exceed the
    class-specific ``num_predict`` reserve Jarvis actually requested), and
    ``done_reason`` (must be a genuine completion, not a truncation/load/other
    outcome). Any parse failure or mismatch raises exactly one typed
    ``ERROR_LOCAL_OUTPUT_CONTRACT`` error; the raw envelope is never retained or
    returned on any path -- the caller (``LocalOllamaAdapter.dispatch``) discards it
    and falls back the gateway to ``not_ready`` in every failure case."""
    if len(raw_bytes) > limits.raw_response_bytes_max:
        raise LocalGatewayBlocked(
            ERROR_LOCAL_OUTPUT_CONTRACT,
            "raw envelope exceeds the bounded validation buffer",
            details={
                "reason": "envelope_bytes_exceeded",
                "actual": len(raw_bytes),
                "limit": limits.raw_response_bytes_max,
            },
        )
    try:
        text = raw_bytes.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise LocalGatewayBlocked(
            ERROR_LOCAL_OUTPUT_CONTRACT,
            "raw envelope is not valid UTF-8",
            details={"reason": "envelope_invalid_utf8"},
        ) from exc
    try:
        envelope = json.loads(text)
    except json.JSONDecodeError as exc:
        raise LocalGatewayBlocked(
            ERROR_LOCAL_OUTPUT_CONTRACT,
            "raw envelope is not a valid JSON object",
            details={"reason": "envelope_invalid_json"},
        ) from exc
    if not isinstance(envelope, dict):
        raise LocalGatewayBlocked(
            ERROR_LOCAL_OUTPUT_CONTRACT,
            "raw envelope is not a JSON object",
            details={"reason": "envelope_not_an_object"},
        )
    extra_keys = set(envelope.keys()) - _ALLOWED_ENVELOPE_KEYS
    if extra_keys:
        # The unknown key NAMES themselves are untrusted provider-controlled text
        # (this is the same envelope an adversarial/misbehaving provider could
        # shape) -- only a count is recorded in details, never the literal key
        # strings, so this failure path cannot become a raw-content leak channel.
        raise LocalGatewayBlocked(
            ERROR_LOCAL_OUTPUT_CONTRACT,
            "raw envelope has unknown fields",
            details={"reason": "envelope_unknown_fields", "count": len(extra_keys)},
        )
    response_text = envelope.get("response")
    if not isinstance(response_text, str):
        raise LocalGatewayBlocked(
            ERROR_LOCAL_OUTPUT_CONTRACT,
            "envelope response field is missing or wrong-typed",
            details={"reason": "envelope_response_wrong_type"},
        )
    if envelope.get("model") != expected_model:
        raise LocalGatewayBlocked(
            ERROR_LOCAL_OUTPUT_CONTRACT,
            "envelope model identity does not match the exact request",
            details={"reason": "envelope_model_mismatch"},
        )
    if envelope.get("done") is not True:
        raise LocalGatewayBlocked(
            ERROR_LOCAL_OUTPUT_CONTRACT,
            "envelope is not a completed non-streaming response",
            details={"reason": "envelope_not_done"},
        )
    if envelope.get("done_reason") != _ACCEPTED_DONE_REASON:
        raise LocalGatewayBlocked(
            ERROR_LOCAL_OUTPUT_CONTRACT,
            "envelope terminal reason is not an accepted completion",
            details={"reason": "envelope_done_reason_mismatch"},
        )
    prompt_eval_count = envelope.get("prompt_eval_count")
    if (
        not isinstance(prompt_eval_count, int)
        or isinstance(prompt_eval_count, bool)
        or prompt_eval_count != expected_prompt_tokens
    ):
        raise LocalGatewayBlocked(
            ERROR_LOCAL_OUTPUT_CONTRACT,
            "envelope prompt_eval_count does not match the exact counted prompt",
            details={"reason": "envelope_prompt_eval_count_mismatch"},
        )
    eval_count = envelope.get("eval_count")
    if (
        not isinstance(eval_count, int)
        or isinstance(eval_count, bool)
        or eval_count < 0
        or eval_count > num_predict_limit
    ):
        raise LocalGatewayBlocked(
            ERROR_LOCAL_OUTPUT_CONTRACT,
            "envelope eval_count exceeds the class-specific num_predict reserve",
            details={"reason": "envelope_eval_count_exceeded"},
        )
    return _OllamaEnvelopeOk(response_bytes=response_text.encode("utf-8"))


# ------------------------------------------------------------------ adapter
class LocalOllamaAdapter:
    """The ``ConversationProvider``-shaped local adapter. Inactive unless constructed
    and injected explicitly by a caller (Voice), per Handoff 148 §3.
    """

    name = PROVIDER_ID
    adapter_version = ADAPTER_VERSION

    def __init__(
        self,
        *,
        gateway: LocalReadinessGateway,
        transport: Transport,
        enabled: bool = False,
    ) -> None:
        self.gateway = gateway
        self._transport = transport
        self.enabled = enabled

    def dispatch(
        self,
        request: ProviderRequest,
        cancel: CancellationToken | None = None,
    ) -> NormalizedResult:
        if not self.enabled:
            return self._blocked(request, ERROR_LOCAL_UNAVAILABLE, {"reason": "adapter_disabled"})
        try:
            self.gateway.check_admission()  # 147b §3.1: sampled again immediately before dispatch
        except LocalGatewayBlocked as exc:
            return self._blocked(request, exc.code, exc.details)

        self.gateway.begin_attempt()
        succeeded = False
        try:
            if cancel is not None and cancel.cancelled:
                return NormalizedResult(
                    status=TerminalState.CANCELLED,
                    provider_id=request.transport.provider_id,
                    model_id=request.transport.model_id,
                    adapter_version=self.adapter_version,
                    finish_reason="cancelled",
                )
            prompt = build_qwen_prompt(
                system_instruction=request.content.system_instruction,
                user_text=request.content.user_text,
            )
            # Handoff 150 §3 (PT37-CTO-02): send the EXACT non-streaming Ollama
            # ``/api/generate`` request envelope -- exact model identity,
            # ``stream=false``, the fixed ``num_ctx`` (147b §2.3), and the
            # class-specific ``num_predict`` this exact call is bound to (already
            # selected per-prompt by ``assemble_local_prompt``/``select_warm_class``,
            # carried here as ``request.content.max_output_tokens``) -- rather than
            # the bare ``{"prompt", "num_predict"}`` body the prior implementation
            # sent, which never proved the provider was even running the pinned
            # model or context window.
            # Same deterministic synthetic counter Core used at prompt-assembly time
            # (``assemble_local_prompt``) to pick this exact ``num_predict`` reserve
            # -- recomputed independently here (never trusted from the caller) so the
            # comparison below is against a value this adapter itself derived from
            # the exact prompt it is about to send.
            expected_prompt_tokens = SyntheticTokenCounter().count(prompt)
            body = canonical_json(
                {
                    "model": request.transport.model_id,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_ctx": LOCAL_LIMITS.provider_num_ctx,
                        "num_predict": request.content.max_output_tokens,
                    },
                }
            )
            transport_request = TransportRequest(
                method="POST",
                scheme="http",
                host=request.transport.host,
                path=request.transport.path,
                headers={"content-type": "application/json"},
                body=body.encode("utf-8"),
                timeout_seconds=request.transport.timeout_seconds,
            )
            try:
                response = self._transport.send(transport_request, cancel)
            except TransportTimeout:
                return self._blocked(
                    request, ERROR_LOCAL_TIMEOUT, {"reason": "provider_timeout"}
                )
            except TransportCancelled:
                return NormalizedResult(
                    status=TerminalState.CANCELLED,
                    provider_id=request.transport.provider_id,
                    model_id=request.transport.model_id,
                    adapter_version=self.adapter_version,
                    finish_reason="cancelled",
                )
            except TransportError:
                return self._blocked(
                    request, ERROR_LOCAL_UNAVAILABLE, {"reason": "transport_error"}
                )

            # Handoff 150 §3: parse and verify the real Ollama completion envelope
            # (returned model, prompt_eval_count, eval_count, done_reason) BEFORE
            # treating anything in it as the local closed-schema answer. On any
            # mismatch the raw envelope is discarded (never retained/returned) and
            # the gateway falls back to ``not_ready`` -- a provider that fails to
            # honor its own frozen request/response contract is not safe to keep
            # treating as ``ready``.
            try:
                envelope_ok = _parse_and_verify_ollama_envelope(
                    response.body,
                    expected_model=request.transport.model_id,
                    expected_prompt_tokens=expected_prompt_tokens,
                    num_predict_limit=request.content.max_output_tokens,
                )
            except LocalGatewayBlocked as exc:
                self.gateway.mark_output_contract_violation()
                return self._blocked(request, exc.code, exc.details)

            # Handoff 150 §5 (PT37-CTO-04): pre-existing strict-typing gap, closed while
            # actually running the configured Core type checker for the first time this
            # correction round -- ``diagnostics`` is typed ``Mapping[str, object]`` (it must
            # accept arbitrary per-adapter data), so mypy cannot see through the ``.get(...)``
            # to a concrete iterable of ids. Narrow with a real runtime check rather than a
            # blind cast: an unexpected shape here fails closed to an empty allowlist (every
            # citation gets rejected as fake) instead of raising or trusting untyped data.
            raw_allowed_ids = request.diagnostics.get("allowed_citation_ids", ())
            allowed_citations = (
                frozenset(raw_allowed_ids)
                if isinstance(raw_allowed_ids, (tuple, list, frozenset, set))
                else frozenset()
            )
            try:
                validated = validate_local_response(
                    envelope_ok.response_bytes, allowed_citation_ids=allowed_citations
                )
            except LocalGatewayBlocked as exc:
                return self._blocked(request, exc.code, exc.details)

            succeeded = True
            # V05-PT-37 / Handoff 151, 151a: re-serialize the validated closed shape as
            # canonical JSON in the SAME ``{"claims": [...], "limitations": [...]}``
            # form ``evidence.validate_response`` expects, so ``application.py`` can
            # route it in unchanged (Handoff 151a §3 item 2) instead of decoding a
            # local-only shape.
            answer_text = canonical_json(
                {
                    "claims": [
                        {"text": c.text, "type": c.type, "evidence": list(c.evidence)}
                        for c in validated.claims
                    ],
                    "limitations": list(validated.limitations),
                }
            )
            return NormalizedResult(
                status=TerminalState.COMPLETED,
                provider_id=request.transport.provider_id,
                model_id=request.transport.model_id,
                adapter_version=self.adapter_version,
                text=answer_text,
                finish_reason="stop",
                usage=Usage(None, None, UsageProvenance.UNKNOWN),
                cost=Cost(0.0, "USD", "local", UsageProvenance.ESTIMATED),
            )
        finally:
            self.gateway.end_attempt(success=succeeded)

    def _blocked(
        self, request: ProviderRequest, error_code: str, details: Mapping[str, object]
    ) -> NormalizedResult:
        return NormalizedResult(
            status=TerminalState.BLOCKED,
            provider_id=request.transport.provider_id,
            model_id=request.transport.model_id,
            adapter_version=self.adapter_version,
            finish_reason="blocked",
            error_code=error_code,
            details=dict(details),
        )


__all__ = [
    "ADAPTER_VERSION",
    "ADMISSION_MAX_LOAD_PERCENT",
    "ADMISSION_MIN_AVAIL_BYTES",
    "ADMISSION_SAMPLES",
    "COLD_TO_READY_CEILING_SECONDS",
    "ERROR_LOCAL_CAPACITY",
    "ERROR_LOCAL_CONTEXT_LIMIT",
    "ERROR_LOCAL_NOT_READY",
    "ERROR_LOCAL_OUTPUT_CONTRACT",
    "ERROR_LOCAL_POLICY_DRIFT",
    "ERROR_LOCAL_TIMEOUT",
    "ERROR_LOCAL_UNAVAILABLE",
    "ERROR_LOCAL_UNSAFE_OUTPUT",
    "LOCAL_LIMITS",
    "LOCAL_QWEN_PROFILE_ID",
    "LOCAL_WARM_CLASS_SPECS",
    "PROVIDER_ID",
    "READINESS_PROBE_DEADLINE_SECONDS",
    "READY_EXPIRY_SECONDS",
    "RECOVERY_INTERVAL_SECONDS",
    "RECOVERY_MAX_LOAD_PERCENT",
    "RECOVERY_MIN_AVAIL_BYTES",
    "RECOVERY_SAMPLES",
    "RUNTIME_LOSS_LOAD_PERCENT",
    "RUNTIME_MAX_LOAD_PERCENT_REPORTED",
    "RUNTIME_MIN_AVAIL_BYTES",
    "RUNTIME_SAMPLES",
    "CapacityProbe",
    "Clock",
    "LocalClaim",
    "LocalGatewayBlocked",
    "LocalLimits",
    "LocalOllamaAdapter",
    "LocalReadinessGateway",
    "LocalReadinessState",
    "LocalResponse",
    "LocalWarmClass",
    "LocalWarmClassSpec",
    "MemoryObservation",
    "SyntheticCapacityProbe",
    "SyntheticClock",
    "SyntheticTokenCounter",
    "TokenCounter",
    "build_qwen_prompt",
    "canonical_json",
    "select_warm_class",
    "validate_canonical_text",
    "validate_local_response",
]
