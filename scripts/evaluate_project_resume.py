"""Aggregate the v0.4 Project Resume dogfood scorecard (offline, no telemetry).

Reads a local UTF-8 tab-separated dogfood log (A11) and computes the release-readiness summary:
usefulness rate, median time-to-orientation and estimated time saved, the weighted
correctly-sourced rate for manually reviewed material claims, the citation-defect diagnostic, and
outcome mix. It is a *release/evaluation* tool: it only reads a file the user points it at, sends
nothing anywhere, and never touches the vault. Rows whose id begins with ``EXAMPLE`` or ``#`` are
treated as template placeholders and skipped.

Correctly-sourced metric (Product Owner, weighted; never an average of per-row percentages):

    correctly_sourced_rate = sum(material_claims_correctly_sourced) / sum(material_claims_reviewed)

A zero reviewed-claim denominator yields JSON ``null`` for the rate and for the threshold result
(valid evidence of no review, never a threshold pass/fail). ``citation_defects`` is a separate
diagnostic and never contributes to the numerator or denominator. The minimum technical threshold
is 0.90 and the 0.90-0.95 target band is reported only once a non-zero denominator exists; a rate
above 0.95 is not a failure. The eight-week A11 outcome remains PENDING until Product
Owner-approved collection completes; this tool only summarizes the given data.

    python scripts/evaluate_project_resume.py [path/to/log.tsv] [--json]
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_LOG = _ROOT / "evaluations" / "v0.4-project-resume-dogfood-template.tsv"

_USEFUL_TARGET = 0.80  # A11: at least 80% of rated briefings useful
_TIME_SAVED_TARGET_MIN = 15  # A11: 15-30 min saved per meaningful project switch
_SOURCING_MIN = 0.90  # A11: minimum technical correctly-sourced threshold
_SOURCING_BAND = (0.90, 0.95)  # A11: reported target band (a rate above 0.95 is not a failure)

_REVIEWED = "material_claims_reviewed"
_CORRECT = "material_claims_correctly_sourced"
_SAMPLING_PROC = "sampling_procedure"
_SAMPLING_SIZE = "sampling_size"


class SourcingError(ValueError):
    """A collected row violated the A11 correctly-sourced validation rules (offline error)."""


def _skip(row_id: str) -> bool:
    return row_id.startswith("EXAMPLE") or row_id.startswith("#") or not row_id.strip()


def _to_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _nonneg_int(row: dict[str, str], key: str) -> int | None:
    raw = (row.get(key) or "").strip()
    if raw == "":
        return None
    try:
        value = int(raw)
    except ValueError as exc:
        raise SourcingError(
            f"row {row.get('id', '?')}: {key} must be a non-negative integer (got {raw!r})"
        ) from exc
    if value < 0:
        raise SourcingError(f"row {row.get('id', '?')}: {key} must be non-negative (got {value})")
    return value


def load(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        fieldnames = list(reader.fieldnames or [])
        rows = [r for r in reader if not _skip(r.get("id", ""))]
    return rows, fieldnames


def summarize_sourcing(rows: list[dict[str, str]], fieldnames: list[str]) -> dict[str, object]:
    """Weighted correctly-sourced metric with validation and explicit five-state reporting.

    Raises :class:`SourcingError` for malformed, negative, inconsistent, or over-numerator rows.
    Sampling metadata is emitted only as counts; no claim text, citation text, or procedure text
    leaves this tool.
    """
    collected = _REVIEWED in fieldnames
    reviewed_sum = correct_sum = sample_sum = sourcing_rows = procedures = 0
    if collected:
        for row in rows:
            rid = row.get("id", "?")
            reviewed = _nonneg_int(row, _REVIEWED)
            correct = _nonneg_int(row, _CORRECT)
            size = _nonneg_int(row, _SAMPLING_SIZE)
            procedure = (row.get(_SAMPLING_PROC) or "").strip()
            if reviewed is None:
                raise SourcingError(f"row {rid}: {_REVIEWED} is required")
            if correct is None:
                raise SourcingError(f"row {rid}: {_CORRECT} is required")
            if correct > reviewed:
                raise SourcingError(
                    f"row {rid}: correctly sourced ({correct}) exceeds reviewed ({reviewed})"
                )
            if not procedure:
                raise SourcingError(f"row {rid}: {_SAMPLING_PROC} is required and non-empty")
            if size is None:
                raise SourcingError(f"row {rid}: {_SAMPLING_SIZE} is required")
            if reviewed > size:
                raise SourcingError(
                    f"row {rid}: reviewed ({reviewed}) exceeds declared {_SAMPLING_SIZE} ({size})"
                )
            reviewed_sum += reviewed
            correct_sum += correct
            sample_sum += size
            procedures += 1
            if reviewed > 0:
                sourcing_rows += 1

    if reviewed_sum == 0:
        rate: float | None = None
        state = "no_rows" if not rows else "zero_denominator"
        meets: bool | None = None
    else:
        rate = round(correct_sum / reviewed_sum, 4)
        if rate < _SOURCING_MIN:
            state = "below_target"
        elif rate <= _SOURCING_BAND[1]:
            state = "in_target_band"
        else:
            state = "above_target"
        meets = rate >= _SOURCING_MIN

    return {
        "material_claims_reviewed": reviewed_sum,
        "material_claims_correctly_sourced": correct_sum,
        "correctly_sourced_rate": rate,
        "sourcing_target_min": _SOURCING_MIN,
        "sourcing_target_band": list(_SOURCING_BAND),
        "meets_sourcing_min": meets,
        "sourcing_state": state,
        "sourcing_rows_with_review": sourcing_rows,
        "sampling": {
            "declared_sample_total": sample_sum,
            "procedures_declared": procedures,
            "reconciled": True,
        },
    }


def summarize(rows: list[dict[str, str]], fieldnames: list[str]) -> dict[str, object]:
    rated = [r for r in rows if r.get("useful", "").strip().lower() in ("yes", "no")]
    useful = [r for r in rated if r["useful"].strip().lower() == "yes"]
    orientation = [
        v for r in rows if (v := _to_float(r.get("time_to_orientation_min", ""))) is not None
    ]
    saved = [v for r in rows if (v := _to_float(r.get("est_time_saved_min", ""))) is not None]
    defects = [v for r in rows if (v := _to_float(r.get("citation_defects", ""))) is not None]
    outcomes: dict[str, int] = {}
    for r in rows:
        key = (r.get("outcome", "") or "unspecified").strip() or "unspecified"
        outcomes[key] = outcomes.get(key, 0) + 1

    useful_rate = (len(useful) / len(rated)) if rated else None
    median_saved = statistics.median(saved) if saved else None
    summary: dict[str, object] = {
        "rows": len(rows),
        "rated": len(rated),
        "useful": len(useful),
        "useful_rate": round(useful_rate, 4) if useful_rate is not None else None,
        "median_time_to_orientation_min": (
            round(statistics.median(orientation), 2) if orientation else None
        ),
        "median_time_saved_min": round(median_saved, 2) if median_saved is not None else None,
        "total_citation_defects": int(sum(defects)) if defects else 0,
        "outcomes": dict(sorted(outcomes.items())),
        "meets_useful_target": (useful_rate is not None and useful_rate >= _USEFUL_TARGET),
        "meets_time_saved_target": (
            median_saved is not None and median_saved >= _TIME_SAVED_TARGET_MIN
        ),
    }
    summary.update(summarize_sourcing(rows, fieldnames))
    return summary


def _print_text(path: Path, s: dict[str, object]) -> None:
    print(f"# v0.4 Project Resume dogfood scorecard — {path.name}")
    print(
        "# NOTE: dataset summary only; the A11 release gate is validated on the eight-week "
        "dogfood window and remains PENDING.\n"
    )
    if s["rows"] == 0:
        print(
            "No rated rows found (template placeholders are skipped). Collect dogfood data "
            "and re-run."
        )
        return
    print(f"Rows (excl. examples) : {s['rows']}")
    print(f"Rated (useful yes/no) : {s['rated']}")
    rate = s["useful_rate"]
    print(
        f"Useful rate           : {rate if rate is not None else 'n/a'} "
        f"(target >= {_USEFUL_TARGET})"
    )
    print(f"Median time to orient : {s['median_time_to_orientation_min']} min")
    print(
        f"Median time saved     : {s['median_time_saved_min']} min "
        f"(target >= {_TIME_SAVED_TARGET_MIN})"
    )
    csr = s["correctly_sourced_rate"]
    print(
        f"Correctly-sourced rate: {csr if csr is not None else 'n/a (no reviewed claims)'} "
        f"[{s['material_claims_correctly_sourced']}/{s['material_claims_reviewed']}] "
        f"(min >= {_SOURCING_MIN}, band {_SOURCING_BAND[0]}-{_SOURCING_BAND[1]})"
    )
    print(f"Sourcing state        : {s['sourcing_state']}")
    print(f"Meets sourcing min    : {s['meets_sourcing_min']}")
    print(f"Citation defects      : {s['total_citation_defects']} (separate diagnostic)")
    print(f"Outcomes              : {s['outcomes']}")
    print(f"Meets useful target   : {s['meets_useful_target']}")
    print(f"Meets time-saved target: {s['meets_time_saved_target']}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "log",
        nargs="?",
        default=str(_DEFAULT_LOG),
        help="Path to the dogfood TSV log (default: the template).",
    )
    ap.add_argument("--json", action="store_true", help="Emit the summary as JSON.")
    args = ap.parse_args()
    path = Path(args.log)
    if not path.is_file():
        print(f"error: log not found: {path}", file=sys.stderr)
        return 1
    rows, fieldnames = load(path)
    try:
        summary = summarize(rows, fieldnames)
    except SourcingError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        _print_text(path, summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
