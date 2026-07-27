"""Paired, interleaved same-machine baseline/candidate performance protocol (QR-031-03).

Run-order and background load bias a single baseline-then-candidate comparison. This tool
runs multiple *paired attempts*; within each attempt it measures the v0.3.1 candidate and the
v0.3 baseline back-to-back and alternates which runs first, so order/scheduler bias averages
out. Each measurement uses the identical `benchmark_regression.py` harness (copied into the
baseline tree so only the jarvis_core version differs): same fixture, query, warm-ups,
measured runs, percentile estimator, and construction-plus-query boundary.

It retains raw per-attempt samples for both versions, reports per-pair and aggregate variance,
and exits non-zero if the aggregate (median) total-pipeline p95 regression exceeds the +20%
gate — an honest gate result, never a silent waiver.

Baseline source: pass ``--baseline-root`` (a checked-out/extracted v0.3 tree), or
``--baseline-ref`` to materialize one with ``git archive`` (best-effort).

Usage (from repo root):
    python scripts/benchmark_paired.py --baseline-root /path/to/v0.3 \
        --notes 1000 --runs 30 --attempts 5 [--out evidence.json]
"""
from __future__ import annotations

import argparse
import json
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_HARNESS = _ROOT / "scripts" / "benchmark_regression.py"
GATE_PERCENT = 20.0


def _materialize_baseline(ref: str) -> Path:
    dest = Path(tempfile.mkdtemp(prefix="v03_baseline_"))
    proc = subprocess.run(
        f"git archive {ref} | tar -x -C {dest}", shell=True, cwd=_ROOT,
        capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise SystemExit(f"could not git archive {ref}: {proc.stderr.strip()}")
    return dest


def _run(tree: Path, notes: int, runs: int, query: str, warmups: int) -> dict:
    """Run the regression harness in ``tree`` (no PYTHONPATH) and return its JSON summary."""
    env = {k: v for k, v in _clean_env().items()}
    cmd = [sys.executable, str(tree / "scripts" / "benchmark_regression.py"),
           "--notes", str(notes), "--runs", str(runs), "--query", query,
           "--warmups", str(warmups), "--json"]
    proc = subprocess.run(cmd, cwd=tree, env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"benchmark failed in {tree}:\n{proc.stderr}")
    return json.loads(proc.stdout)


def _clean_env() -> dict:
    import os
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)  # prove no import-path override is needed
    return env


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline-root", default=None, help="path to a v0.3 baseline tree")
    ap.add_argument("--baseline-ref", default="ce0dc35853008e6b83c3c6fdfd0b8650738bee3d")
    ap.add_argument("--notes", type=int, default=1000)
    ap.add_argument("--runs", type=int, default=30)
    ap.add_argument("--attempts", type=int, default=5)
    ap.add_argument("--query", default="links")
    ap.add_argument("--warmups", type=int, default=3)
    ap.add_argument("--out", default=None, help="write full raw evidence JSON here")
    args = ap.parse_args()

    baseline = Path(args.baseline_root) if args.baseline_root else _materialize_baseline(
        args.baseline_ref)
    # Use the identical harness for both versions (only jarvis_core differs).
    shutil.copy2(_HARNESS, baseline / "scripts" / "benchmark_regression.py")

    pairs = []
    for a in range(args.attempts):
        candidate_first = (a % 2 == 0)
        if candidate_first:
            cand = _run(_ROOT, args.notes, args.runs, args.query, args.warmups)
            base = _run(baseline, args.notes, args.runs, args.query, args.warmups)
        else:
            base = _run(baseline, args.notes, args.runs, args.query, args.warmups)
            cand = _run(_ROOT, args.notes, args.runs, args.query, args.warmups)
        c95 = cand["total_pipeline"]["p95"]
        b95 = base["total_pipeline"]["p95"]
        reg = round((c95 - b95) / b95 * 100, 2) if b95 else 0.0
        pairs.append({
            "attempt": a, "order": "candidate_first" if candidate_first else "baseline_first",
            "candidate_p95_ms": c95, "baseline_p95_ms": b95, "regression_pct": reg,
            "candidate_raw_ms": cand["total_pipeline"]["raw_ms"],
            "baseline_raw_ms": base["total_pipeline"]["raw_ms"],
        })

    regs = [p["regression_pct"] for p in pairs]
    c95s = [p["candidate_p95_ms"] for p in pairs]
    b95s = [p["baseline_p95_ms"] for p in pairs]
    agg = {
        "median_regression_pct": round(statistics.median(regs), 2),
        "max_regression_pct": max(regs),
        "min_regression_pct": min(regs),
        "median_candidate_p95_ms": round(statistics.median(c95s), 3),
        "median_baseline_p95_ms": round(statistics.median(b95s), 3),
        "gate_percent": GATE_PERCENT,
    }
    passed = agg["median_regression_pct"] <= GATE_PERCENT

    print(f"# Paired total-pipeline p95 — attempts={args.attempts} notes={args.notes} "
          f"runs={args.runs} query={args.query!r}\n")
    print("| attempt | order | candidate p95 | baseline p95 | regression % |")
    print("|---|---|---|---|---|")
    for p in pairs:
        print(f"| {p['attempt']} | {p['order']} | {p['candidate_p95_ms']} | "
              f"{p['baseline_p95_ms']} | {p['regression_pct']} |")
    print(f"\nAggregate: median regression {agg['median_regression_pct']}% "
          f"(min {agg['min_regression_pct']}%, max {agg['max_regression_pct']}%); "
          f"median candidate p95 {agg['median_candidate_p95_ms']}ms vs baseline "
          f"{agg['median_baseline_p95_ms']}ms")
    print(f"GATE (<= {GATE_PERCENT}% on median): {'PASS' if passed else 'FAIL'}")

    if args.out:
        Path(args.out).write_text(
            json.dumps({"pairs": pairs, "aggregate": agg, "passed": passed}, indent=2),
            encoding="utf-8")
        print(f"(raw evidence written to {args.out})")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
