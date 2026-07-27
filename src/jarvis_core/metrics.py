"""Lightweight performance instrumentation.

Uses ``time.perf_counter`` for wall-clock stage timing. No global state; a
:class:`PerfReport` is built explicitly and passed where needed, preserving the
read-only, side-effect-free design.
"""
from __future__ import annotations

import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field


@dataclass
class PerfReport:
    """Collected timings (seconds) and counts for a pipeline run."""

    note_count: int = 0
    durations: dict[str, float] = field(default_factory=dict)

    def record(self, stage: str, seconds: float) -> None:
        self.durations[stage] = self.durations.get(stage, 0.0) + seconds

    @property
    def total_seconds(self) -> float:
        # 'total' is recorded explicitly by the caller when it wraps the whole run;
        # fall back to the sum of stages if not present.
        if "total" in self.durations:
            return self.durations["total"]
        return sum(v for k, v in self.durations.items() if k != "total")

    def notes_per_second(self) -> float:
        total = self.total_seconds
        return (self.note_count / total) if total > 0 else 0.0

    def to_dict(self) -> dict[str, object]:
        return {
            "note_count": self.note_count,
            "durations_ms": {k: round(v * 1000, 3) for k, v in sorted(self.durations.items())},
            "total_ms": round(self.total_seconds * 1000, 3),
            "notes_per_second": round(self.notes_per_second(), 1),
        }


@contextmanager
def measure(report: PerfReport, stage: str) -> Iterator[None]:
    """Context manager that records elapsed wall-clock time into ``report``."""
    start = time.perf_counter()
    try:
        yield
    finally:
        report.record(stage, time.perf_counter() - start)
