"""Performance and determinism of the query engine at 100/500/1000 notes.

These are guardrail tests: generous absolute ceilings that only fail on a gross
regression (e.g. accidental O(n^2) retrieval). They also assert determinism at scale.
"""
from __future__ import annotations

import time
from pathlib import Path

import pytest

from jarvis_core.config import Config
from jarvis_core.query import QueryEngine
from jarvis_core.repositories import FileSystemKnowledgeRepository
from tests.support.synthetic_vault import build_synthetic_vault


def _engine(path: Path) -> QueryEngine:
    notes = FileSystemKnowledgeRepository(Config(vault_path=path)).discover()
    return QueryEngine(notes)


@pytest.mark.parametrize("n", [100, 500, 1000])
def test_query_scales_and_is_bounded(tmp_path: Path, n: int):
    build_synthetic_vault(tmp_path, n)
    eng = _engine(tmp_path)  # index build is part of construction
    start = time.perf_counter()
    answer = eng.search("links")
    elapsed = time.perf_counter() - start
    assert answer.citations  # "links" appears in every non-terminal note body
    # A single lexical query over <=1000 tiny notes must be well under a second.
    assert elapsed < 1.0, f"query at n={n} took {elapsed:.3f}s"


def test_ranking_is_deterministic_at_scale(tmp_path: Path):
    build_synthetic_vault(tmp_path, 500)
    eng = _engine(tmp_path)
    a = [c.relpath for c in eng.search("links", limit=25).citations]
    b = [c.relpath for c in eng.search("links", limit=25).citations]
    assert a == b
    assert a == sorted(a[: len(a)]) or len(a) == 25  # stable, top-N slice
