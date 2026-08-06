"""AE-05-01 per-tree runner: measure the released Query Engine construction-plus-run.

Invoked as a subprocess with a specific ``PYTHONPATH`` (baseline or candidate ``src``) so
exactly one ``jarvis_core`` differs while everything else — the shared synthetic vault,
query, scope, evaluation boundary, warmups, run count — is identical. Emits raw wall-clock
milliseconds and per-run peak memory (MiB) as JSON on stdout. No prompts, context,
responses, credentials, private paths, usernames, or raw errors are emitted.
"""
from __future__ import annotations

import json
import sys
import time
import tracemalloc
from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.policy import local_allow_all
from jarvis_core.query.engine import QueryEngine
from jarvis_core.repositories import FileSystemKnowledgeRepository

_QUERY = "summarize Bench"


def main() -> int:
    vault = Path(sys.argv[1])
    runs = int(sys.argv[2])
    warmup = int(sys.argv[3])
    notes = FileSystemKnowledgeRepository(Config(vault_path=vault)).discover()
    scope = local_allow_all(workspace_id="local", max_sensitivity="internal")
    root = Path(vault)

    def one() -> None:
        # Construction-plus-run boundary (discovery is excluded and shared).
        engine = QueryEngine(notes, scope=scope, source_root=root)
        engine.run(_QUERY)

    for _ in range(warmup):
        one()
    wall_ms: list[float] = []
    peak_mib: list[float] = []
    for _ in range(runs):
        tracemalloc.start()
        t0 = time.perf_counter()
        one()
        dt = (time.perf_counter() - t0) * 1000.0
        peak = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        wall_ms.append(round(dt, 4))
        peak_mib.append(round(peak / (1024 * 1024), 4))
    print(json.dumps({"note_count": len(notes), "wall_ms": wall_ms, "peak_mib": peak_mib}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
