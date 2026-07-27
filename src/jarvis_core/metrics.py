"""Lightweight performance instrumentation.

Uses ``time.perf_counter`` for wall-clock stage timing and optional ``tracemalloc``
for memory. No global state; a :class:`PerfReport` is built explicitly and passed where
needed, preserving the read-only, side-effect-free design.
"""
from __future__ import annotations

import time
import tracemalloc
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field


@dataclass
class PerfReport:
    """Collected timings (seconds), counts, memory, and graph size for a run."""

    note_count: int = 0
    durations: dict[str, float] = field(default_factory=dict)
    # Optional resource metrics (populated when available).
    cache_bytes: int = 0
    graph_nodes: int = 0
    graph_edges: int = 0
    peak_memory_bytes: int | None = None
    current_memory_bytes: int | None = None

    def record(self, stage: str, seconds: float) -> None:
        self.durations[stage] = self.durations.get(stage, 0.0) + seconds

    @property
    def total_seconds(self) -> float:
        if "total" in self.durations:
            return self.durations["total"]
        return sum(v for k, v in self.durations.items() if k != "total")

    def notes_per_second(self) -> float:
        total = self.total_seconds
        return (self.note_count / total) if total > 0 else 0.0

    def to_dict(self) -> dict[str, object]:
        out: dict[str, object] = {
            "note_count": self.note_count,
            "durations_ms": {k: round(v * 1000, 3) for k, v in sorted(self.durations.items())},
            "total_ms": round(self.total_seconds * 1000, 3),
            "notes_per_second": round(self.notes_per_second(), 1),
            "cache_bytes": self.cache_bytes,
            "graph": {"nodes": self.graph_nodes, "edges": self.graph_edges},
        }
        if self.peak_memory_bytes is not None:
            out["memory"] = {
                "peak_bytes": self.peak_memory_bytes,
                "current_bytes": self.current_memory_bytes,
                "peak_mb": round(self.peak_memory_bytes / (1024 * 1024), 3),
            }
        return out


@contextmanager
def measure(report: PerfReport, stage: str) -> Iterator[None]:
    """Context manager that records elapsed wall-clock time into ``report``."""
    start = time.perf_counter()
    try:
        yield
    finally:
        report.record(stage, time.perf_counter() - start)


@contextmanager
def track_memory(report: PerfReport, enabled: bool = True) -> Iterator[None]:
    """Record peak/current memory (bytes) via tracemalloc when ``enabled``.

    tracemalloc adds overhead, so this is opt-in (the CLI enables it only for
    ``--memory``). When disabled it is a no-op and leaves memory fields as None.
    """
    if not enabled:
        yield
        return
    started_here = not tracemalloc.is_tracing()
    if started_here:
        tracemalloc.start()
    try:
        yield
    finally:
        current, peak = tracemalloc.get_traced_memory()
        report.current_memory_bytes = current
        report.peak_memory_bytes = peak
        if started_here:
            tracemalloc.stop()
