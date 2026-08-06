"""AE-05-01 remediation performance evidence (predeclared, recomputable).

Compares the accepted unchanged-query baseline commit against the correction candidate using
an identical harness and identical shared synthetic vaults at 100/500/1,000/5,000 notes.
Both trees are materialized via ``git archive`` (baseline) / a candidate source tree, and the
released Query Engine construction-plus-run is measured in isolated subprocesses (only
``jarvis_core`` differs). Candidate-first/baseline-first order alternates by size. Every raw
timing and per-run peak-memory sample is retained; p50/p95/p99, peak stats, the candidate/
baseline p95 ratio, and the ≤20% unchanged-query gate are recomputed independently. The three
absolute conversation gates are recomputed from the candidate conversation benchmark.

Protocol is fixed BEFORE results are seen: 3 warmups, 20 measured runs per size, the accepted
≤20% p95 rule at every reported size. No prompts, context, responses, credentials, private
paths, usernames, or raw errors are recorded.

    python scripts/benchmark_conversation_remediation.py [--baseline <sha>] \
        [--candidate-ref <sha>] [--sizes 100,500,1000,5000] [--runs 20] [--warmup 3] \
        [--json docs/evidence/v0.5/conversation-performance-remediation.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_MAIN_GIT_DIR = _ROOT.parent.parent / ".git"  # the shared object store (…/AI-Operating-System/.git)
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from benchmark_project_resume import build_resume_vault  # noqa: E402

BASELINE_DEFAULT = "e11703974219425b463a45a97e1d7d2a04de81dc"
_RUNNER = Path(__file__).resolve().parent / "_qe_bench_runner.py"
GATE_REGRESSION_MAX = 1.20  # candidate p95 may be at most 20% over baseline at every size


def _percentiles(samples: list[float]) -> dict[str, float]:
    s = sorted(samples)
    if not s:
        return {"p50": 0.0, "p95": 0.0, "p99": 0.0}

    def pct(q: float) -> float:
        return round(s[min(len(s) - 1, round(q * (len(s) - 1)))], 4)

    return {"p50": round(statistics.median(s), 4), "p95": pct(0.95), "p99": pct(0.99)}


def _materialize_baseline(ref: str, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    cmd = f'git --git-dir="{_MAIN_GIT_DIR}" archive {ref} src | tar -x -C "{dest}"'
    subprocess.run(cmd, shell=True, check=True)


def _materialize_candidate(ref: str | None, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    if ref:
        cmd = f'git --git-dir="{_MAIN_GIT_DIR}" archive {ref} src | tar -x -C "{dest}"'
        subprocess.run(cmd, shell=True, check=True)
    else:  # uncommitted correction candidate: use the current worktree source tree
        shutil.copytree(_ROOT / "src", dest / "src")


def _run_tree(src: Path, vault: Path, runs: int, warmup: int) -> dict[str, object]:
    proc = subprocess.run(
        [sys.executable, str(_RUNNER), str(vault), str(runs), str(warmup)],
        env={"PYTHONPATH": str(src), "PATH": "/usr/bin:/bin"},
        capture_output=True, text=True, check=True,
    )
    return json.loads(proc.stdout.strip())


def run(baseline: str, candidate_ref: str | None, sizes: list[int], runs: int, warmup: int) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        base_dir = Path(tmp) / "baseline"
        cand_dir = Path(tmp) / "candidate"
        _materialize_baseline(baseline, base_dir)
        _materialize_candidate(candidate_ref, cand_dir)
        base_src = base_dir / "src"
        cand_src = cand_dir / "src"

        per_size: dict[str, object] = {}
        gate_ok = True
        for idx, n in enumerate(sizes):
            vault = Path(tmp) / f"vault_{n}"
            build_resume_vault(vault, n)  # ONE shared fixture used by both trees
            # Alternate candidate-first / baseline-first by size.
            if idx % 2 == 0:
                cand = _run_tree(cand_src, vault, runs, warmup)
                base = _run_tree(base_src, vault, runs, warmup)
                order = "candidate_first"
            else:
                base = _run_tree(base_src, vault, runs, warmup)
                cand = _run_tree(cand_src, vault, runs, warmup)
                order = "baseline_first"
            b_ms = _percentiles(list(base["wall_ms"]))
            c_ms = _percentiles(list(cand["wall_ms"]))
            ratio = round(c_ms["p95"] / b_ms["p95"], 4) if b_ms["p95"] else 0.0
            within = ratio <= GATE_REGRESSION_MAX
            gate_ok = gate_ok and within
            per_size[str(n)] = {
                "order": order,
                "note_count": cand["note_count"],
                "baseline_wall_ms": b_ms,
                "candidate_wall_ms": c_ms,
                "baseline_raw_wall_ms": base["wall_ms"],
                "candidate_raw_wall_ms": cand["wall_ms"],
                "baseline_peak_mib": _percentiles(list(base["peak_mib"])),
                "candidate_peak_mib": _percentiles(list(cand["peak_mib"])),
                "baseline_raw_peak_mib": base["peak_mib"],
                "candidate_raw_peak_mib": cand["peak_mib"],
                "p95_ratio_candidate_over_baseline": ratio,
                "within_20pct": within,
            }

    # Absolute conversation gates recomputed from the candidate conversation benchmark.
    from benchmark_conversation import run as conv_run
    conv = conv_run(sizes, runs, warmup)
    conv_gates = conv["gate_results"]

    git_version = subprocess.run(
        ["git", "--version"], capture_output=True, text=True
    ).stdout.strip()
    return {
        "schema": "v0.5-conversation-performance-remediation/1",
        "protocol": {
            "baseline_commit": baseline,
            "candidate_ref": candidate_ref or "uncommitted-correction-candidate-worktree",
            "sizes": sizes,
            "warmups": warmup,
            "measured_runs": runs,
            "percentile_method": "median + nearest-rank p95/p99 (shared)",
            "regression_rule": "candidate query construction-plus-run p95 <= 1.20x baseline "
            "at every size (fixed before results)",
            "python": sys.version.split()[0],
            "git": git_version,
            "fixture": "build_resume_vault (shared per size; identical bytes for both trees)",
            "query": "summarize Bench",
        },
        "unchanged_query": per_size,
        "unchanged_query_gate_pass": gate_ok,
        "conversation_absolute_gates": conv_gates,
        "conversation_absolute_summary": {
            k: v["prepare_ms"] if isinstance(v, dict) and "prepare_ms" in v else None
            for k, v in conv["sizes"].items()
        },
        "all_gates_pass": bool(gate_ok and all(conv_gates.values())),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--baseline", default=BASELINE_DEFAULT)
    ap.add_argument("--candidate-ref", default=None)
    ap.add_argument("--sizes", default="100,500,1000,5000")
    ap.add_argument("--runs", type=int, default=20)
    ap.add_argument("--warmup", type=int, default=3)
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    sizes = [int(x) for x in args.sizes.split(",") if x.strip()]
    result = run(args.baseline, args.candidate_ref, sizes, args.runs, args.warmup)
    blob = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json:
        Path(args.json).write_text(blob, encoding="utf-8")
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    for n, v in result["unchanged_query"].items():
        ratio = v["p95_ratio_candidate_over_baseline"]
        print(
            f"n={n:>5} query p95 baseline={v['baseline_wall_ms']['p95']}ms "
            f"candidate={v['candidate_wall_ms']['p95']}ms ratio={ratio} "
            f"within20%={v['within_20pct']} ({v['order']})"
        )
    print("unchanged_query_gate_pass:", result["unchanged_query_gate_pass"])
    print("conversation_absolute_gates:", json.dumps(result["conversation_absolute_gates"]))
    print("all_gates_pass:", result["all_gates_pass"])
    print("artifact_sha256:", digest)
    return 0 if result["all_gates_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
