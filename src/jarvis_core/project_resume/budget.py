"""Two independent hard budgets for Project Resume (ADR-0020 §11, brief §11).

Project Resume enforces an *evidence* budget (every selected passage/record and its evidence
wrapper) and an *output* budget (the complete serialized text or JSON result, including
headings, labels, claim text, separators, citations, conflicts, omissions, limitations,
coverage, and the requested trace). Both use the released deterministic estimator
:func:`jarvis_core.query.context_builder.estimate_tokens`; Project Resume never invents a new
token model.

Allocation is deterministic: reserve mandatory structural overhead, then admit items in the
caller's priority order, stopping *before* the first item that would exceed the remaining
capacity and recording a bounded, non-disclosing omission for the remainder. The final
serialized form is measured before emission; if the mandatory minimum cannot fit, the caller
returns a bounded ``budget_error`` rather than truncating a serialized string (which could
sever a citation or produce invalid JSON). The trace is charged against a declared sub-budget
that lives *inside* the output budget, so a trace can never silently expand the ordinary
result.
"""
from __future__ import annotations

from dataclasses import dataclass

from jarvis_core.project_resume.contract import (
    DEFAULT_EVIDENCE_TOKEN_BUDGET,
    DEFAULT_OUTPUT_TOKEN_BUDGET,
    DEFAULT_TRACE_TOKEN_SUB_BUDGET,
    EVIDENCE_BUDGET_MAX,
    EVIDENCE_BUDGET_MIN,
    OUTPUT_BUDGET_MAX,
    OUTPUT_BUDGET_MIN,
)
from jarvis_core.project_resume.results import Omission
from jarvis_core.query.context_builder import estimate_tokens


class BudgetConfigError(ValueError):
    """A budget configuration outside its accepted bounds (fail-closed)."""


def estimate(text: str) -> int:
    """The released deterministic token estimate for a serialized fragment or whole result."""
    return estimate_tokens(text)


@dataclass(frozen=True)
class BudgetConfig:
    """The three configured budgets; the trace sub-budget lives inside the output budget."""

    evidence_token_budget: int = DEFAULT_EVIDENCE_TOKEN_BUDGET
    output_token_budget: int = DEFAULT_OUTPUT_TOKEN_BUDGET
    trace_token_sub_budget: int = DEFAULT_TRACE_TOKEN_SUB_BUDGET

    def validate(self) -> BudgetConfig:
        """Return self if every budget is in range and the trace sub-budget fits inside output."""
        if not (EVIDENCE_BUDGET_MIN <= self.evidence_token_budget <= EVIDENCE_BUDGET_MAX):
            raise BudgetConfigError(
                f"evidence budget must be {EVIDENCE_BUDGET_MIN}..{EVIDENCE_BUDGET_MAX}"
            )
        if not (OUTPUT_BUDGET_MIN <= self.output_token_budget <= OUTPUT_BUDGET_MAX):
            raise BudgetConfigError(
                f"output budget must be {OUTPUT_BUDGET_MIN}..{OUTPUT_BUDGET_MAX}"
            )
        if not (0 <= self.trace_token_sub_budget <= self.output_token_budget):
            raise BudgetConfigError("trace sub-budget must be 0..output_token_budget")
        return self


@dataclass(frozen=True)
class BudgetItem:
    """One budgetable unit (a passage+wrapper, a record, a claim) with its estimated cost."""

    key: str
    tokens: int


@dataclass(frozen=True)
class BudgetPlan:
    """A deterministic admit-until-full plan with bounded omissions and the used total."""

    admitted: tuple[BudgetItem, ...]
    omissions: tuple[Omission, ...]
    used: int
    capacity: int
    minimum_unmet: bool = False  # mandatory reserve alone exceeds capacity -> budget_error

    @property
    def fits(self) -> bool:
        return self.used <= self.capacity and not self.minimum_unmet


def plan_within_budget(
    items: tuple[BudgetItem, ...] | list[BudgetItem],
    *,
    capacity: int,
    reserved: int = 0,
    omission_reason: str,
    channel: str | None = None,
) -> BudgetPlan:
    """Reserve mandatory overhead, then admit items in order, stopping at the first overflow.

    ``capacity`` and ``reserved`` must be non-negative and item costs must be non-negative
    (fail-closed). When the mandatory ``reserved`` overhead alone exceeds ``capacity`` the plan
    admits nothing and flags ``minimum_unmet`` so the caller can return ``budget_error``.
    Admission stops before the first item that would exceed the remaining capacity; the
    remainder is recorded as one bounded, non-disclosing omission.
    """
    if capacity < 0:
        raise BudgetConfigError(f"capacity must be non-negative, got {capacity}")
    if reserved < 0:
        raise BudgetConfigError(f"reserved must be non-negative, got {reserved}")
    seq = list(items)
    for it in seq:
        if it.tokens < 0:
            raise BudgetConfigError(f"item {it.key!r} has negative token cost {it.tokens}")

    if reserved > capacity:
        omissions = (
            (Omission(reason=omission_reason, count=len(seq), channel=channel),) if seq else ()
        )
        return BudgetPlan((), omissions, reserved, capacity, minimum_unmet=True)

    available = capacity - reserved
    admitted: list[BudgetItem] = []
    used = 0
    dropped = 0
    for i, it in enumerate(seq):
        if used + it.tokens <= available:
            admitted.append(it)
            used += it.tokens
        else:
            dropped = len(seq) - i
            break

    omissions = (
        (Omission(reason=omission_reason, count=dropped, channel=channel),) if dropped else ()
    )
    return BudgetPlan(tuple(admitted), omissions, reserved + used, capacity)


@dataclass(frozen=True)
class OutputBudgetCheck:
    """The measured-before-emission verdict for a fully serialized result."""

    ok: bool
    output_tokens: int
    trace_tokens: int
    reason: str | None = None


def check_output(
    serialized: str,
    *,
    config: BudgetConfig,
    trace_serialized: str | None = None,
) -> OutputBudgetCheck:
    """Measure the final serialization and verify both the output budget and trace sub-budget.

    ``serialized`` is the complete result exactly as it will be emitted (already including any
    trace), so :func:`estimate` counts everything. When a trace is present its own serialized
    fragment is measured separately against the sub-budget that lives inside the output budget.
    A failing check must lead the caller to a bounded ``budget_error`` — never to truncating
    ``serialized`` after the fact.
    """
    output_tokens = estimate(serialized)
    trace_tokens = estimate(trace_serialized) if trace_serialized else 0
    if trace_serialized is not None and trace_tokens > config.trace_token_sub_budget:
        return OutputBudgetCheck(
            False, output_tokens, trace_tokens,
            "trace exceeds the declared trace sub-budget",
        )
    if output_tokens > config.output_token_budget:
        return OutputBudgetCheck(
            False, output_tokens, trace_tokens, "serialized output exceeds the output budget"
        )
    return OutputBudgetCheck(True, output_tokens, trace_tokens, None)
