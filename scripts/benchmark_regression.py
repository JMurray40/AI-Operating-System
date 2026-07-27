"""Equivalent p95-to-p95 regression benchmark for the public QueryEngine (AE-01).

Measures the *complete public* ``QueryEngine.run(query)`` call end-to-end on a prebuilt
engine, using the same fixture, query, warm-up policy, run count, and percentile method for
both the v0.3 baseline and the v0.3.1 candidate. Construction is adaptive so the same script
runs against either version (the candidate requires an explicit scope; the baseline does not).

Run against each version by pointing PYTHONPATH at that version's ``src`` (and the repo root
for ``tests.support``). Report is Markdown with raw min/median/max plus p50/p95/p99.

Usage: python scripts/benchmark_regression.py [--notes 1000] [--runs 50] [--query links]
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path
from tempfile import TemporaryDirectory

from tests.support.synthetic_vault import build_synthetic_vault

from jarvis_core.config import Config
from jarvis_core.query.engine import QueryEngine
from jarvis_core.repositories import FileSystemKnowledgeRepository

try:  # candidate requires an explicit scope; baseline does not accept one
    from jarvis_core.policy import local_allow_all
    _SCOPE = local_allow_all("local")
except Exception:  # pragma: no cover - baseline path
    _SCOPE = None


def _make_engine(notes: list) -> QueryEngine:
    if _SCOPE is not None:
        try:
            return QueryEngine(notes, scope=_SCOPE)  # type: ignore[call-arg]
        except TypeError:
            pass
    return QueryEngine(notes)  # type: ignore[call-arg]


def _pct(sorted_s: list[float], q: float) -> float:
    if not sorted_s:
        return 0.0
    idx = min(len(sorted_s) - 1, round(q * (len(sorted_s) - 1)))
    return round(sorted_s[idx] * 1000, 3)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--notes", type=int, default=1000)
    ap.add_argument("--runs", type=int, default=50)
    ap.add_argument("--query", default="links")
    ap.add_argument("--warmups", type=int, default=3)
    args = ap.parse_args()

    with TemporaryDirectory() as d:
        root = Path(d)
        build_synthetic_vault(root, args.notes)
        notes = FileSystemKnowledgeRepository(
            Config(vault_path=root, max_files=20000)
        ).discover()
        engine = _make_engine(notes)  # construction excluded from the per-query gate
        for _ in range(args.warmups):
            engine.run(args.query)
        samples: list[float] = []
        for _ in range(args.runs):
            t0 = time.perf_counter()
            engine.run(args.query)
            samples.append(time.perf_counter() - t0)

    s = sorted(samples)
    print(f"# QueryEngine.run() end-to-end — notes={args.notes} runs={args.runs} "
          f"query={args.query!r}")
    print(f"min={round(s[0]*1000,3)}ms  median={_pct(s,0.5)}ms  max={round(s[-1]*1000,3)}ms")
    print(f"p50={_pct(s,0.5)}ms  p95={_pct(s,0.95)}ms  p99={_pct(s,0.99)}ms")


if __name__ == "__main__":
    main()
