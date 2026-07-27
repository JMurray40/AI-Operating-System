"""Enforced smoke test for the documented benchmark entry points (AC-03R3-01 follow-up).

Executes scripts/benchmark_query.py far enough to detect QueryEngine constructor-contract
drift (e.g. a construction that omits the now-mandatory source_root would raise here).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"_bench_{name}", _SCRIPTS / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_benchmark_query_bench_constructs_engine():
    from jarvis_core.policy import local_allow_all
    mod = _load("benchmark_query")
    res, excluded = mod.bench(5, 1, local_allow_all("local"))  # warm-up path builds an engine
    assert "total" in res and isinstance(excluded, int)


def test_benchmark_query_entrypoint_runs(monkeypatch, capsys):
    mod = _load("benchmark_query")
    monkeypatch.setattr(sys, "argv", ["benchmark_query.py", "--sizes", "5", "--runs", "1"])
    mod.main()  # covers warm-up AND the 1,000-note memory-measurement construction
    out = capsys.readouterr().out
    assert "Peak memory" in out
    assert "authorization stress" in out


def test_benchmark_regression_entrypoint_runs(monkeypatch, capsys):
    mod = _load("benchmark_regression")
    monkeypatch.setattr(sys, "argv", ["benchmark_regression.py", "--notes", "5", "--runs", "1"])
    mod.main()
    out = capsys.readouterr().out
    assert "total_pipeline" in out
