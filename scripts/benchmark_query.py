"""Benchmark the v0.3.1 authorized query pipeline (offline, read-only).

Reports p50/p95/p99 (ms) for authorized-view construction, candidate retrieval, ranking,
graph/context expansion, citation construction+validation, and total query, at increasing
vault sizes. Also reports peak memory at 1,000 notes and an authorization stress case where
half the notes are excluded. Deterministic content; timing only is nondeterministic.

Usage: python scripts/benchmark_query.py [--sizes 100,500,1000] [--runs 10]
"""
from __future__ import annotations

import argparse
import time
import tracemalloc
from pathlib import Path
from statistics import median
from tempfile import TemporaryDirectory

from tests.support.synthetic_vault import build_synthetic_vault

from jarvis_core.config import Config
from jarvis_core.policy import AuthorizationScope, local_allow_all
from jarvis_core.query.authorized import build_authorized_view
from jarvis_core.query.context_builder import QueryContextBuilder
from jarvis_core.query.engine import QueryEngine
from jarvis_core.query.index import LexicalIndex
from jarvis_core.query.passages import locate, validate
from jarvis_core.query.ranking import Ranker
from jarvis_core.relationships import RelationshipResolver
from jarvis_core.repositories import FileSystemKnowledgeRepository

_TERM = ["links"]


def _pct(samples: list[float], q: float) -> float:
    s = sorted(samples)
    if not s:
        return 0.0
    idx = min(len(s) - 1, round(q * (len(s) - 1)))
    return round(s[idx] * 1000, 3)


def _stats(samples: list[float]) -> dict[str, float]:
    return {
        "p50": round(median(samples) * 1000, 3),
        "p95": _pct(samples, 0.95),
        "p99": _pct(samples, 0.99),
    }


def bench(n: int, runs: int, scope: AuthorizationScope) -> dict[str, dict[str, float]]:
    with TemporaryDirectory() as d:
        root = Path(d)
        build_synthetic_vault(root, n)
        notes = FileSystemKnowledgeRepository(
            Config(vault_path=root, max_files=20000)
        ).discover()
        stages: dict[str, list[float]] = {
            k: [] for k in ("authorized_view", "retrieval", "ranking", "context",
                            "citation", "total")
        }
        QueryEngine(notes, scope=scope).search(" ".join(_TERM))  # warm-up (unmeasured)
        for _ in range(runs):
            t0 = time.perf_counter()
            view = build_authorized_view(notes, scope)
            t1 = time.perf_counter()
            index = LexicalIndex(view.notes)
            report = RelationshipResolver(view.notes).resolve_all()
            ranker = Ranker(index, report)
            builder = QueryContextBuilder(index, report)
            cands = index.candidates(_TERM)
            t2 = time.perf_counter()
            ranked = ranker.rank(_TERM, cands, phrase=" ".join(_TERM))
            t3 = time.perf_counter()
            builder.build([s.relpath for s in ranked[:10]])
            t4 = time.perf_counter()
            for s in ranked[:10]:
                loc, ex = locate(s.note, frozenset(_TERM))
                validate(locator=loc, excerpt=ex, source_fingerprint=s.note.source_fingerprint,
                         current_bytes=s.note.source_text.encode("utf-8"),
                         current_text=s.note.source_text)
            t5 = time.perf_counter()
            stages["authorized_view"].append(t1 - t0)
            stages["retrieval"].append(t2 - t1)
            stages["ranking"].append(t3 - t2)
            stages["context"].append(t4 - t3)
            stages["citation"].append(t5 - t4)
            stages["total"].append(t5 - t0)
        excluded = build_authorized_view(notes, scope).excluded_count
        return {k: _stats(v) for k, v in stages.items()}, excluded


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", default="100,500,1000")
    ap.add_argument("--runs", type=int, default=10)
    args = ap.parse_args()
    sizes = [int(s) for s in args.sizes.split(",")]
    scope = local_allow_all("local")
    print(f"# v0.3.1 query benchmark (runs={args.runs} + warm-up)\n")
    for n in sizes:
        res, _ = bench(n, args.runs, scope)
        print(f"## {n} notes")
        print("| stage | p50 | p95 | p99 |")
        print("|---|---|---|---|")
        for stage, st in res.items():
            print(f"| {stage} | {st['p50']} | {st['p95']} | {st['p99']} |")
        print()

    # Peak memory + auth-stress at 1000 notes.
    with TemporaryDirectory() as d:
        root = Path(d)
        build_synthetic_vault(root, 1000)
        notes = FileSystemKnowledgeRepository(
            Config(vault_path=root, max_files=20000)
        ).discover()
        tracemalloc.start()
        QueryEngine(notes, scope=scope).search(" ".join(_TERM))
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print(f"Peak memory @ 1000 notes: {round(peak / (1024 * 1024), 3)} MB")

    # Authorization stress: exclude ~half of 1000 notes via a source-id allowlist.
    allowed = frozenset(f"local:id:note-{i:04d}" for i in range(500))
    stress = AuthorizationScope(
        workspace_id="local", max_sensitivity="restricted", allowed_source_ids=allowed,
    )
    res, excl = bench(1000, args.runs, stress)
    print(f"\n## authorization stress @ 1000 notes ({excl} excluded)")
    print("| stage | p50 | p95 | p99 |")
    print("|---|---|---|---|")
    for stage, st in res.items():
        print(f"| {stage} | {st['p50']} | {st['p95']} | {st['p99']} |")


if __name__ == "__main__":
    main()
