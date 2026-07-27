"""Benchmark the v0.3 query engine at increasing vault sizes.

Read-only and offline. Prints a Markdown table of per-stage timings (median of N runs).
Usage: python scripts/benchmark_query.py [--sizes 100,500,1000] [--runs 5]
"""
from __future__ import annotations

import argparse
import statistics
import tempfile
import time
from pathlib import Path

from tests.support.synthetic_vault import build_synthetic_vault

from jarvis_core.config import Config
from jarvis_core.query import QueryEngine
from jarvis_core.query.context_builder import QueryContextBuilder
from jarvis_core.query.index import LexicalIndex
from jarvis_core.query.ranking import Ranker
from jarvis_core.relationships import RelationshipResolver
from jarvis_core.repositories import FileSystemKnowledgeRepository


def _median_ms(samples: list[float]) -> float:
    return round(statistics.median(samples) * 1000, 3)


def bench(n: int, runs: int) -> dict[str, float]:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        build_synthetic_vault(root, n)
        notes = FileSystemKnowledgeRepository(Config(vault_path=root)).discover()

        index_t, retrieval_t, ranking_t, context_t, total_t = [], [], [], [], []
        for _ in range(runs):
            t0 = time.perf_counter()
            index = LexicalIndex(notes)
            report = RelationshipResolver(notes).resolve_all()
            t1 = time.perf_counter()
            ranker = Ranker(index, report)
            builder = QueryContextBuilder(index, report)
            cands = index.candidates(["links"])
            t2 = time.perf_counter()
            ranked = ranker.rank(["links"], cands, phrase="links")
            t3 = time.perf_counter()
            builder.build([s.relpath for s in ranked[:10]])
            t4 = time.perf_counter()
            index_t.append(t1 - t0)
            retrieval_t.append(t2 - t1)
            ranking_t.append(t3 - t2)
            context_t.append(t4 - t3)
            total_t.append(t4 - t0)

        # provider stage (summarize path) measured separately via full engine
        eng = QueryEngine(notes)
        prov = []
        for _ in range(runs):
            p0 = time.perf_counter()
            eng.summarize("Note 0000")
            prov.append(time.perf_counter() - p0)

        return {
            "notes": n,
            "index_build": _median_ms(index_t),
            "retrieval": _median_ms(retrieval_t),
            "ranking": _median_ms(ranking_t),
            "context": _median_ms(context_t),
            "provider(mock)": _median_ms(prov),
            "total(query)": _median_ms(total_t),
        }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", default="100,500,1000")
    ap.add_argument("--runs", type=int, default=5)
    args = ap.parse_args()
    sizes = [int(s) for s in args.sizes.split(",")]
    rows = [bench(n, args.runs) for n in sizes]
    cols = ["notes", "index_build", "retrieval", "ranking", "context",
            "provider(mock)", "total(query)"]
    print("| " + " | ".join(cols) + " |")
    print("|" + "|".join("---" for _ in cols) + "|")
    for r in rows:
        print("| " + " | ".join(str(r[c]) for c in cols) + " |")


if __name__ == "__main__":
    main()
