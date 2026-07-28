"""Aggregate the v0.4 Project Resume dogfood scorecard (offline, no telemetry).

Reads a local UTF-8 tab-separated dogfood log (A11) and computes the release-readiness summary:
usefulness rate, median time-to-orientation and estimated time saved, citation-defect rate, and
outcome mix. It is a *release/evaluation* tool: it only reads a file the user points it at, sends
nothing anywhere, and never touches the vault. Rows whose id begins with ``EXAMPLE`` or ``#`` are
treated as template placeholders and skipped.

The A11 gate - at least 80% of rated briefings useful, 15-30 min saved per meaningful switch,
90-95% correctly sourced material claims - is validated on real dogfood data over the eight-week
window and remains PENDING; this tool computes the numbers from the given data and reports
whether that dataset clears the thresholds, without asserting the release gate itself.

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


def _skip(row_id: str) -> bool:
    return row_id.startswith("EXAMPLE") or row_id.startswith("#") or not row_id.strip()


def _to_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        return [r for r in reader if not _skip(r.get("id", ""))]


def summarize(rows: list[dict[str, str]]) -> dict[str, object]:
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
    return {
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
        "meets_useful_target": (
            useful_rate is not None and useful_rate >= _USEFUL_TARGET
        ),
        "meets_time_saved_target": (
            median_saved is not None and median_saved >= _TIME_SAVED_TARGET_MIN
        ),
    }


def _print_text(path: Path, s: dict[str, object]) -> None:
    print(f"# v0.4 Project Resume dogfood scorecard — {path.name}")
    print(
        "# NOTE: dataset summary only; the A11 release gate is validated on the eight-week "
        "dogfood window and remains PENDING.\n"
    )
    if s["rows"] == 0:
        print("No rated rows found (template placeholders are skipped). Collect dogfood data "
              "and re-run.")
        return
    print(f"Rows (excl. examples) : {s['rows']}")
    print(f"Rated (useful yes/no) : {s['rated']}")
    rate = s["useful_rate"]
    print(f"Useful rate           : {rate if rate is not None else 'n/a'} "
          f"(target >= {_USEFUL_TARGET})")
    print(f"Median time to orient : {s['median_time_to_orientation_min']} min")
    print(f"Median time saved     : {s['median_time_saved_min']} min "
          f"(target >= {_TIME_SAVED_TARGET_MIN})")
    print(f"Citation defects      : {s['total_citation_defects']}")
    print(f"Outcomes              : {s['outcomes']}")
    print(f"Meets useful target   : {s['meets_useful_target']}")
    print(f"Meets time-saved target: {s['meets_time_saved_target']}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("log", nargs="?", default=str(_DEFAULT_LOG),
                    help="Path to the dogfood TSV log (default: the template).")
    ap.add_argument("--json", action="store_true", help="Emit the summary as JSON.")
    args = ap.parse_args()
    path = Path(args.log)
    if not path.is_file():
        print(f"error: log not found: {path}", file=sys.stderr)
        return 1
    summary = summarize(load_rows(path))
    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        _print_text(path, summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
