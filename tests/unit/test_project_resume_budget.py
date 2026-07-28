"""C7: two hard budgets — deterministic reserve/admit/stop + measured output (ADR-0020 §11).

Covers the boundary matrix: zero/negative capacity, below-minimum reserve, exact boundary,
one-over, oversized-first, multibyte text, stop-order determinism, the trace sub-budget inside
the output budget, text-vs-JSON measurement, and the error-fallback fit. Every budget uses the
released deterministic estimator (whitespace words).
"""
from __future__ import annotations

import json

import pytest

from jarvis_core.project_resume.budget import (
    BudgetConfig,
    BudgetConfigError,
    BudgetItem,
    check_output,
    estimate,
    plan_within_budget,
)
from jarvis_core.project_resume.contract import (
    DEFAULT_OUTPUT_TOKEN_BUDGET,
    DEFAULT_TRACE_TOKEN_SUB_BUDGET,
)

REASON = "evidence budget reached"


def _items(*costs: int) -> list[BudgetItem]:
    return [BudgetItem(key=f"k{i}", tokens=c) for i, c in enumerate(costs)]


# ---------------------------------------------------------------- estimator reuse


def test_estimator_is_whitespace_word_count() -> None:
    assert estimate("one two three") == 3
    assert estimate("") == 0


def test_estimator_counts_multibyte_by_words() -> None:
    # Multibyte characters do not inflate the whitespace-word estimate.
    assert estimate("café résumé naïve") == 3


# ---------------------------------------------------------------- config validation


def test_config_rejects_out_of_range_budgets() -> None:
    with pytest.raises(BudgetConfigError):
        BudgetConfig(evidence_token_budget=1).validate()
    with pytest.raises(BudgetConfigError):
        BudgetConfig(output_token_budget=999_999).validate()


def test_config_rejects_trace_larger_than_output() -> None:
    with pytest.raises(BudgetConfigError):
        BudgetConfig(output_token_budget=1000, trace_token_sub_budget=2000).validate()


def test_default_config_validates() -> None:
    cfg = BudgetConfig().validate()
    assert cfg.output_token_budget == DEFAULT_OUTPUT_TOKEN_BUDGET
    assert cfg.trace_token_sub_budget == DEFAULT_TRACE_TOKEN_SUB_BUDGET


# ---------------------------------------------------------------- capacity boundaries


def test_negative_capacity_fails_closed() -> None:
    with pytest.raises(BudgetConfigError):
        plan_within_budget(_items(1), capacity=-1, omission_reason=REASON)


def test_negative_item_cost_fails_closed() -> None:
    with pytest.raises(BudgetConfigError):
        plan_within_budget(_items(-5), capacity=100, omission_reason=REASON)


def test_zero_capacity_admits_nothing() -> None:
    plan = plan_within_budget(_items(1, 1), capacity=0, omission_reason=REASON)
    assert plan.admitted == ()
    assert plan.omissions[0].count == 2
    assert plan.fits


def test_below_minimum_structure_flags_budget_error() -> None:
    # Mandatory reserve alone exceeds capacity -> minimum_unmet -> caller returns budget_error.
    plan = plan_within_budget(_items(1), capacity=10, reserved=20, omission_reason=REASON)
    assert plan.minimum_unmet
    assert not plan.fits
    assert plan.admitted == ()


def test_exact_boundary_admits_all() -> None:
    plan = plan_within_budget(_items(4, 6), capacity=10, omission_reason=REASON)
    assert [i.key for i in plan.admitted] == ["k0", "k1"]
    assert plan.used == 10
    assert plan.fits
    assert plan.omissions == ()


def test_one_over_omits_the_last() -> None:
    plan = plan_within_budget(_items(4, 7), capacity=10, omission_reason=REASON)
    assert [i.key for i in plan.admitted] == ["k0"]
    assert plan.used == 4
    assert plan.omissions[0].count == 1


def test_oversized_first_admits_nothing() -> None:
    plan = plan_within_budget(_items(50, 1), capacity=10, omission_reason=REASON)
    assert plan.admitted == ()
    assert plan.omissions[0].count == 2  # first and everything after it
    assert not plan.minimum_unmet  # capacity is fine; the item is simply too big


def test_admission_stops_in_priority_order() -> None:
    # Once an item does not fit, admission STOPS — a later smaller item is not admitted out of
    # order, preserving deterministic priority.
    plan = plan_within_budget(_items(6, 7, 1), capacity=10, omission_reason=REASON)
    assert [i.key for i in plan.admitted] == ["k0"]
    assert plan.omissions[0].count == 2


def test_reserve_reduces_available_capacity() -> None:
    plan = plan_within_budget(_items(5, 5), capacity=12, reserved=4, omission_reason=REASON)
    # available = 12 - 4 = 8 -> only the first 5-cost item fits.
    assert [i.key for i in plan.admitted] == ["k0"]
    assert plan.used == 9  # reserved(4) + admitted(5)
    assert plan.fits


# ---------------------------------------------------------------- output budget


def test_output_within_budget_ok() -> None:
    cfg = BudgetConfig(output_token_budget=256, trace_token_sub_budget=64).validate()
    serialized = " ".join(["tok"] * 100)
    check = check_output(serialized, config=cfg)
    assert check.ok
    assert check.output_tokens == 100


def test_output_over_budget_not_ok() -> None:
    cfg = BudgetConfig(output_token_budget=256, trace_token_sub_budget=64).validate()
    serialized = " ".join(["tok"] * 300)
    check = check_output(serialized, config=cfg)
    assert not check.ok
    assert "output budget" in (check.reason or "")


def test_trace_sub_budget_enforced_inside_output() -> None:
    cfg = BudgetConfig(output_token_budget=1000, trace_token_sub_budget=10).validate()
    body = " ".join(["b"] * 50)
    trace = " ".join(["t"] * 40)  # 40 > 10 sub-budget
    serialized = body + " " + trace
    check = check_output(serialized, config=cfg, trace_serialized=trace)
    assert not check.ok
    assert "trace" in (check.reason or "")
    assert check.trace_tokens == 40


def test_trace_within_sub_budget_ok() -> None:
    cfg = BudgetConfig(output_token_budget=1000, trace_token_sub_budget=100).validate()
    body = " ".join(["b"] * 50)
    trace = " ".join(["t"] * 40)
    check = check_output(body + " " + trace, config=cfg, trace_serialized=trace)
    assert check.ok
    assert check.trace_tokens == 40


def test_text_and_json_are_measured_independently() -> None:
    cfg = BudgetConfig(output_token_budget=256, trace_token_sub_budget=64).validate()
    payload = {"a": ["one", "two", "three"], "b": "four five"}
    text_form = "one two three four five"
    json_form = json.dumps(payload)
    text_check = check_output(text_form, config=cfg)
    json_check = check_output(json_form, config=cfg)
    assert text_check.ok and json_check.ok
    # The same semantic content serializes to different token counts per format.
    assert text_check.output_tokens != json_check.output_tokens


def test_error_fallback_payload_fits_minimum() -> None:
    # A bounded budget_error payload must itself fit comfortably within the output budget.
    cfg = BudgetConfig(output_token_budget=256, trace_token_sub_budget=64).validate()
    err = json.dumps({"status": "budget_error", "reason": "minimum structure exceeds budget"})
    assert check_output(err, config=cfg).ok
