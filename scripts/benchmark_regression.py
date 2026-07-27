"""Total-pipeline p95 regression benchmark for the query engine (AE-01R2).

The accepted total query pipeline includes authorized-view/index/graph construction, which
happen in ``QueryEngine.__init__``. So the release gate times, per sample, engine
CONSTRUCTION plus one public query over the same pre-parsed note set. The prebuilt-engine
``run()`` latency is reported separately as a steady-state diagnostic only.

Runs directly from a version's repository root with no PYTHONPATH override: the script adds
its own root and ``src`` to ``sys.path``. Against the current tree it measures the v0.3.1
candidate; run from a checked-out v0.3 baseline tree it measures the baseline (which accepts
neither an explicit scope nor a source root). Notes are parsed once and reused for every
sample, so only engine construction + query are measured. Candidate/baseline isolation is
preserved by running each version from its own tree.

Usage: python scripts/benchmark_regression.py [--notes 1000] [--runs 50] [--query links]
       [--json]   # emit a machine-readable JSON summary incl. raw samples
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory

# Runnable directly from the repository root (QR-031-01): add repo root + src to sys.path.
_ROOT = Path(__file__).resolve().parents[1]
for _p in (str(_ROOT), str(_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tests.support.synthetic_vault import build_synthetic_vault  # noqa: E402

from jarvis_core.config import Config  # noqa: E402
from jarvis_core.query.engine import QueryEngine  # noqa: E402
from jarvis_core.repositories import FileSystemKnowledgeRepository  # noqa: E402

try:  # candidate requires an explicit scope; baseline accepts neither scope nor source root
    from jarvis_core.policy import local_allow_all
    _SCOPE = local_allow_all("local")
except Exception:  # pragma: no cover - baseline path
    _SCOPE = None


def _make_engine(notes: list, root: Path) -> QueryEngine:
    if _SCOPE is not None:
        try:
            return QueryEngine(notes, scope=_SCOPE, source_root=root)  # type: ignore[call-arg]
        except TypeError:
            try:
                return QueryEngine(notes, scope=_SCOPE)  # type: ignore[call-arg]
            except TypeError:
                pass
    return QueryEngine(notes)  # type: ignore[call-arg]


def _pct(samples: list[float], q: float) -> float:
    s = sorted(samples)
    if not s:
        return 0.0
    return round(s[min(len(s) - 1, round(q * (len(s) - 1)))] * 1000, 3)


def _summary(name: str, samples: list[float]) -> None:
    s = sorted(samples)
    print(f"## {name}")
    print(f"min={round(s[0]*1000,3)}ms  max={round(s[-1]*1000,3)}ms  "
          f"p50={_pct(s,0.5)}ms  p95={_pct(s,0.95)}ms  p99={_pct(s,0.99)}ms")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--notes", type=int, default=1000)
    ap.add_argument("--runs", type=int, default=50)
    ap.add_argument("--query", default="links")
    ap.add_argument("--warmups", type=int, default=3)
    ap.add_argument("--json", action="store_true", help="emit a JSON summary incl. raw samples")
    args = ap.parse_args()

    with TemporaryDirectory() as d:
        root = Path(d)
        build_synthetic_vault(root, args.notes)
        notes = FileSystemKnowledgeRepository(
            Config(vault_path=root, max_files=20000)
        ).discover()

        for _ in range(args.warmups):
            _make_engine(notes, root).run(args.query)

        total: list[float] = []          # construction + one query (RELEASE GATE)
        for _ in range(args.runs):
            t0 = time.perf_counter()
            engine = _make_engine(notes, root)
            engine.run(args.query)
            total.append(time.perf_counter() - t0)

        engine = _make_engine(notes, root)  # steady-state diagnostic (prebuilt engine)
        for _ in range(args.warmups):
            engine.run(args.query)
        steady: list[float] = []
        for _ in range(args.runs):
            t0 = time.perf_counter()
            engine.run(args.query)
            steady.append(time.perf_counter() - t0)

    if args.json:
        print(json.dumps({
            "notes": args.notes, "runs": args.runs, "query": args.query,
            "warmups": args.warmups,
            "total_pipeline": {
                "raw_ms": [round(x * 1000, 4) for x in total],
                "p50": _pct(total, 0.5), "p95": _pct(total, 0.95), "p99": _pct(total, 0.99),
            },
            "steady_state": {
                "raw_ms": [round(x * 1000, 4) for x in steady],
                "p50": _pct(steady, 0.5), "p95": _pct(steady, 0.95), "p99": _pct(steady, 0.99),
            },
        }))
        return
    print(f"# QueryEngine total pipeline — notes={args.notes} runs={args.runs} "
          f"query={args.query!r} warmups={args.warmups}\n")
    _summary("total_pipeline (construction + query) — RELEASE GATE", total)
    print()
    _summary("steady_state (prebuilt engine, query only) — diagnostic", steady)


if __name__ == "__main__":
    main()
