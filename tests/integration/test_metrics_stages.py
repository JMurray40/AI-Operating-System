from __future__ import annotations

from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.metrics import PerfReport, track_memory
from jarvis_core.repositories import FileSystemKnowledgeRepository
from tests.support.synthetic_vault import build_synthetic_vault


def test_timed_discovery_splits_stages(tmp_path: Path):
    build_synthetic_vault(tmp_path, 20)
    perf = PerfReport()
    repo = FileSystemKnowledgeRepository(Config(vault_path=tmp_path))
    notes = repo.discover(perf)
    perf.note_count = len(notes)
    assert {"disk_read", "metadata_parse", "markdown_parse"} <= set(perf.durations)
    assert repo.total_bytes > 0


def test_memory_tracking_optional(tmp_path: Path):
    build_synthetic_vault(tmp_path, 10)
    perf = PerfReport()
    with track_memory(perf, enabled=True):
        FileSystemKnowledgeRepository(Config(vault_path=tmp_path)).discover(perf)
    assert perf.peak_memory_bytes is not None and perf.peak_memory_bytes > 0

    perf2 = PerfReport()
    with track_memory(perf2, enabled=False):
        FileSystemKnowledgeRepository(Config(vault_path=tmp_path)).discover(perf2)
    assert perf2.peak_memory_bytes is None
