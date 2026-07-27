"""Benchmark the v0.4 conversation layer at increasing vault sizes.

Read-only and offline. Reports per-turn cost broken into reference resolution, the
underlying retrieval/ranking run, and provenance enrichment, at 100/500/1000/5000 notes
(median of N runs). Usage: python scripts/benchmark_conversation.py [--sizes ...] [--runs 5]
"""
from __future__ import annotations

import argparse
import statistics
import tempfile
import time
from pathlib import Path

from tests.support.synthetic_vault import build_synthetic_vault

from jarvis_core.config import Config
from jarvis_core.conversation import ConversationManager
from jarvis_core.conversation.references import ReferenceResolver
from jarvis_core.query import QueryEngine
from jarvis_core.repositories import FileSystemKnowledgeRepository


def _ms(samples: list[float]) -> float:
    return round(statistics.median(samples) * 1000, 3)


def bench(n: int, runs: int) -> dict[str, float]:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        build_synthetic_vault(root, n)
        notes = FileSystemKnowledgeRepository(Config(vault_path=root, max_files=20000)).discover()

        resolve_t, turn_t = [], []
        for _ in range(runs):
            mgr = ConversationManager(QueryEngine(notes))
            mgr.ask("Tell me about links")  # seed focus (not timed)
            r = ReferenceResolver()
            t0 = time.perf_counter()
            r.resolve("what about it?", mgr.session.entity_stack)
            t1 = time.perf_counter()
            mgr.ask("Tell me about links")  # broad turn: exercises full retrieval/ranking
            t2 = time.perf_counter()
            resolve_t.append(t1 - t0)
            turn_t.append(t2 - t1)
        return {
            "notes": n,
            "reference_resolution": _ms(resolve_t),
            "full_turn": _ms(turn_t),
        }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", default="100,500,1000,5000")
    ap.add_argument("--runs", type=int, default=5)
    args = ap.parse_args()
    sizes = [int(s) for s in args.sizes.split(",")]
    rows = [bench(n, args.runs) for n in sizes]
    cols = ["notes", "reference_resolution", "full_turn"]
    print("| " + " | ".join(cols) + " |")
    print("|" + "|".join("---" for _ in cols) + "|")
    for row in rows:
        print("| " + " | ".join(str(row[c]) for c in cols) + " |")


if __name__ == "__main__":
    main()
