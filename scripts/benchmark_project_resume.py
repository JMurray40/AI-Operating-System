"""Benchmark the v0.4 Project Resume pipeline (offline, read-only).

Reports p50/p95/p99 (ms) for the instrumented resume stages — exact project selection, evidence
discovery (the retrieval stage), and claim-to-current-citation binding — plus total assemble
latency, at increasing vault sizes, and peak memory at the largest size. Per-stage timings are
read from the assembler's own trace instrumentation; total latency is measured around the call.

IMPORTANT (release status): this harness measures latency on *the current machine only*. The
A10 acceptance gate — "under 30 seconds for each pilot vault on documented reference hardware" —
is validated separately on the §18 reference profile and remains PENDING. This script therefore
records and prints measurements but never asserts the reference-hardware gate is met.

Runs directly from the repository root with no PYTHONPATH override:
    python scripts/benchmark_project_resume.py [--sizes 100,500,1000] [--runs 20]
"""
from __future__ import annotations

import argparse
import sys
import time
import tracemalloc
from pathlib import Path
from statistics import median
from tempfile import TemporaryDirectory

# Runnable directly from the repository root: add the repo root and src/ to sys.path so no
# PYTHONPATH override is required (matches scripts/benchmark_query.py).
_ROOT = Path(__file__).resolve().parents[1]
for _p in (str(_ROOT), str(_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from jarvis_core.config import Config  # noqa: E402
from jarvis_core.policy import local_allow_all  # noqa: E402
from jarvis_core.project_resume import assemble, build_request  # noqa: E402
from jarvis_core.repositories import FileSystemKnowledgeRepository  # noqa: E402

_DATE = "2026-07-27"
_EVAL = "2026-07-28T00:00:00Z"
_SELECTOR = "Bench"
_STAGES = ("select_ms", "discover_ms", "bind_ms", "total_ms")


def _fm(note_id: str, note_type: str, title: str, extra: str = "") -> str:
    return (
        f"---\nid: {note_id}\ntype: {note_type}\ntitle: \"{title}\"\nstatus: active\n"
        f"created: {_DATE}\nupdated: {_DATE}\nsensitivity: internal\n{extra}---\n\n"
    )


def build_resume_vault(root: Path, n_notes: int) -> None:
    """Create a selectable project plus ``n_notes-1`` supporting notes that reference it.

    Deterministic content across a mix of decisions, sessions, references, and concepts, each
    bound to the project by typed ``projects`` metadata and a wikilink, so evidence discovery
    and citation binding do realistic (bounded) work. Only timing is nondeterministic.
    """
    root.mkdir(parents=True, exist_ok=True)
    (root / "Bench.md").write_text(
        _fm("project-bench", "project", _SELECTOR,
            "goal: g\npriority: high\nnext_action: \"Ship the bench pipeline\"\n")
        + "# Bench\n\n## Current state\n\nThe Bench pipeline is green and shipping weekly.\n",
        encoding="utf-8",
    )
    kinds = (
        ("decision", "accepted", "decision_date"),
        ("session-summary", "active", "session_date"),
        ("reference", "active", None),
        ("concept", "active", None),
    )
    width = max(4, len(str(n_notes)))
    for i in range(n_notes - 1):
        note_type, status, date_field = kinds[i % len(kinds)]
        name = f"Support {i:0{width}d}"
        link = f"[[Support {i + 1:0{width}d}]]" if i < n_notes - 2 else "[[Bench]]"
        extra = "projects: [Bench]\nstatus: " + status + "\n"
        if date_field:
            extra += f"{date_field}: {_DATE}\n"
        (root / f"{name}.md").write_text(
            _fm(f"support-{i:0{width}d}", note_type, name, extra)
            + f"# {name}\n\nAbout the Bench pipeline. Links {link}.\n",
            encoding="utf-8",
        )


def _stats_ms(samples: list[float]) -> dict[str, float]:
    """p50/p95/p99 for samples already expressed in milliseconds."""
    s = sorted(samples)
    if not s:
        return {"p50": 0.0, "p95": 0.0, "p99": 0.0}

    def pct(q: float) -> float:
        return round(s[min(len(s) - 1, round(q * (len(s) - 1)))], 3)

    return {"p50": round(median(s), 3), "p95": pct(0.95), "p99": pct(0.99)}


def bench(n: int, runs: int) -> dict[str, dict[str, float]]:
    scope = local_allow_all("local")
    with TemporaryDirectory() as d:
        root = Path(d)
        build_resume_vault(root, n)
        notes = FileSystemKnowledgeRepository(
            Config(vault_path=root, max_files=40000)
        ).discover()
        request = build_request(
            workspace_id="local", project_selector=_SELECTOR,
            authorization_scope=scope, source_root=root,
            evaluation_time=_EVAL, trace_requested=True,
        )
        assemble(notes, request)  # warm-up (parsing/imports/caches)
        samples: dict[str, list[float]] = {stage: [] for stage in _STAGES}
        for _ in range(runs):
            t0 = time.perf_counter()
            result = assemble(notes, request)
            total_ms = (time.perf_counter() - t0) * 1000.0
            timings = dict(result.trace["timings_ms"]) if result.trace else {}
            samples["select_ms"].append(float(timings.get("select_ms", 0.0)))
            samples["discover_ms"].append(float(timings.get("discover_ms", 0.0)))
            samples["bind_ms"].append(float(timings.get("bind_ms", 0.0)))
            samples["total_ms"].append(total_ms)
        return {stage: _stats_ms(values) for stage, values in samples.items()}


def _print_table(title: str, res: dict[str, dict[str, float]]) -> None:
    print(f"## {title}")
    print("| stage | p50 | p95 | p99 |")
    print("|---|---|---|---|")
    for stage, st in res.items():
        print(f"| {stage} | {st['p50']} | {st['p95']} | {st['p99']} |")
    print()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sizes", default="100,500,1000")
    ap.add_argument("--runs", type=int, default=20)
    args = ap.parse_args()
    sizes = [int(s) for s in args.sizes.split(",")]

    print(f"# v0.4 Project Resume benchmark (runs={args.runs} + warm-up)")
    print(
        "# NOTE: current-machine measurements only; the A10 30s reference-hardware gate is "
        "validated on the reference profile and remains PENDING.\n"
    )
    largest = max(sizes)
    for n in sizes:
        _print_table(f"{n} notes", bench(n, args.runs))

    # Peak memory at the largest size (single instrumented assemble).
    scope = local_allow_all("local")
    with TemporaryDirectory() as d:
        root = Path(d)
        build_resume_vault(root, largest)
        notes = FileSystemKnowledgeRepository(
            Config(vault_path=root, max_files=40000)
        ).discover()
        request = build_request(
            workspace_id="local", project_selector=_SELECTOR,
            authorization_scope=scope, source_root=root, evaluation_time=_EVAL,
        )
        assemble(notes, request)  # warm-up
        tracemalloc.start()
        assemble(notes, request)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print(f"Peak memory @ {largest} notes: {round(peak / (1024 * 1024), 3)} MB")


if __name__ == "__main__":
    main()
