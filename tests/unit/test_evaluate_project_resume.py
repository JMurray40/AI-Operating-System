"""QF-02: the A11 correctly-sourced metric in scripts/evaluate_project_resume.py.

Covers example exclusion, weighted (sum/sum) aggregation, zero-denominator null semantics, the
five reported states, the 0.90/0.95 boundaries, malformed/negative/inconsistent/over-numerator
rejection, citation-defect separation, and sampling-metadata privacy. The evaluator is a script
(not a package module); it is loaded by path.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "evaluate_project_resume.py"
_spec = importlib.util.spec_from_file_location("evaluate_project_resume", _SCRIPT)
assert _spec and _spec.loader
ev = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ev)

FIELDS = [
    "id",
    "useful",
    "citation_defects",
    "material_claims_reviewed",
    "material_claims_correctly_sourced",
    "sampling_procedure",
    "sampling_size",
]


def row(
    rid, reviewed, correct, *, size=None, proc="first N per briefing", useful="yes", defects="0"
):
    return {
        "id": rid,
        "useful": useful,
        "citation_defects": defects,
        "material_claims_reviewed": str(reviewed),
        "material_claims_correctly_sourced": str(correct),
        "sampling_procedure": proc,
        "sampling_size": str(reviewed if size is None else size),
    }


def _src(rows):
    return ev.summarize_sourcing(rows, FIELDS)


# ---------------------------------------------------------------- example exclusion / load


def test_examples_and_comments_skipped(tmp_path: Path) -> None:
    log = tmp_path / "log.tsv"
    log.write_text(
        "\t".join(FIELDS)
        + "\n"
        + "\t".join(["EXAMPLE-1", "yes", "0", "10", "10", "p", "10"])
        + "\n"
        + "\t".join(["# comment", "yes", "0", "10", "10", "p", "10"])
        + "\n"
        + "\t".join(["R1", "yes", "0", "10", "9", "p", "10"])
        + "\n",
        encoding="utf-8",
    )
    rows, fieldnames = ev.load(log)
    assert [r["id"] for r in rows] == ["R1"]  # EXAMPLE and # rows excluded
    assert ev._REVIEWED in fieldnames


# ---------------------------------------------------------------- weighted aggregation


def test_weighted_rate_is_sum_over_sum_not_average_of_rates() -> None:
    # per-row rates 1.0 and 0.9 average to 0.95; the weighted rate is 91/100 = 0.91.
    out = _src([row("R1", 10, 10), row("R2", 90, 81)])
    assert out["material_claims_reviewed"] == 100
    assert out["material_claims_correctly_sourced"] == 91
    assert out["correctly_sourced_rate"] == 0.91
    assert out["sourcing_state"] == "in_target_band"
    assert out["meets_sourcing_min"] is True


# ---------------------------------------------------------------- five states


def test_no_rows_state() -> None:
    out = _src([])
    assert out["sourcing_state"] == "no_rows"
    assert out["correctly_sourced_rate"] is None
    assert out["meets_sourcing_min"] is None


def test_zero_denominator_state() -> None:
    out = _src([row("R1", 0, 0, size=0)])
    assert out["sourcing_state"] == "zero_denominator"
    assert out["correctly_sourced_rate"] is None
    assert out["meets_sourcing_min"] is None
    assert out["material_claims_reviewed"] == 0


def test_below_target_state() -> None:
    out = _src([row("R1", 100, 89)])
    assert out["correctly_sourced_rate"] == 0.89
    assert out["sourcing_state"] == "below_target"
    assert out["meets_sourcing_min"] is False


def test_090_boundary_in_band_and_meets() -> None:
    out = _src([row("R1", 100, 90)])
    assert out["correctly_sourced_rate"] == 0.9
    assert out["sourcing_state"] == "in_target_band"
    assert out["meets_sourcing_min"] is True


def test_095_boundary_in_band_and_meets() -> None:
    out = _src([row("R1", 100, 95)])
    assert out["correctly_sourced_rate"] == 0.95
    assert out["sourcing_state"] == "in_target_band"
    assert out["meets_sourcing_min"] is True


def test_above_095_not_a_failure() -> None:
    out = _src([row("R1", 100, 99)])
    assert out["correctly_sourced_rate"] == 0.99
    assert out["sourcing_state"] == "above_target"
    assert out["meets_sourcing_min"] is True


# ---------------------------------------------------------------- validation rejection


@pytest.mark.parametrize(
    "bad",
    [
        {"reviewed": "x", "correct": 1},  # non-integer
        {"reviewed": -1, "correct": 0},  # negative
        {"reviewed": 5, "correct": 6},  # correctly sourced exceeds reviewed
        {"reviewed": 6, "correct": 6, "size": 5},  # reviewed exceeds declared sample
        {"reviewed": 5, "correct": 5, "proc": ""},  # missing sampling procedure
    ],
)
def test_invalid_rows_raise_sourcing_error(bad: dict) -> None:
    r = row(
        "R1",
        bad.get("reviewed", 5),
        bad.get("correct", 5),
        size=bad.get("size"),
        proc=bad.get("proc", "p"),
    )
    with pytest.raises(ev.SourcingError):
        _src([r])


def test_missing_required_field_raises() -> None:
    r = row("R1", 5, 5)
    r["material_claims_reviewed"] = ""  # required, present but empty
    with pytest.raises(ev.SourcingError):
        _src([r])


# ---------------------------------------------------------------- separation and privacy


def test_citation_defects_do_not_affect_sourcing() -> None:
    rows = [row("R1", 10, 10, defects="7")]
    out = ev.summarize(rows, FIELDS)
    assert out["total_citation_defects"] == 7  # separate diagnostic
    assert out["material_claims_reviewed"] == 10
    assert out["material_claims_correctly_sourced"] == 10
    assert out["correctly_sourced_rate"] == 1.0


def test_sampling_metadata_is_counts_only_no_text() -> None:
    out = _src([row("R1", 8, 8, proc="secret sampling note names here", size=8)])
    sampling = out["sampling"]
    assert set(sampling) == {"declared_sample_total", "procedures_declared", "reconciled"}
    assert sampling["declared_sample_total"] == 8
    assert sampling["procedures_declared"] == 1
    # the procedure text must not appear anywhere in the emitted summary
    assert "secret sampling note names here" not in str(out)


def test_sourcing_absent_columns_is_zero_denominator() -> None:
    rows = [{"id": "R1", "useful": "yes"}]
    out = ev.summarize_sourcing(rows, ["id", "useful"])  # no sourcing columns collected
    assert out["correctly_sourced_rate"] is None
    assert out["sourcing_state"] == "zero_denominator"
