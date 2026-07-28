"""Real process-boundary smoke tests for the documented benchmark commands (QR-031-02).

These run the scripts as subprocesses from the repository root with NO PYTHONPATH override,
proving the documented commands import, parse args, warm up, run the measured query, memory,
authorization-stress, and regression paths to completion. A negative case proves the smoke
fails when the runtime dependency cannot be imported.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]


def _clean_env() -> dict:
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)  # prove the documented command needs no import-path override
    return env


def _run(args: list[str], cwd: Path):
    return subprocess.run(
        [sys.executable, *args], cwd=cwd, env=_clean_env(),
        capture_output=True, text=True, timeout=180,
    )


def test_benchmark_query_runs_from_repo_root():
    proc = _run(["scripts/benchmark_query.py", "--sizes", "5", "--runs", "1"], _ROOT)
    assert proc.returncode == 0, proc.stderr
    assert "Peak memory" in proc.stdout
    assert "authorization stress" in proc.stdout
    assert "total" in proc.stdout


def test_benchmark_project_resume_runs_from_repo_root():
    proc = _run(["scripts/benchmark_project_resume.py", "--sizes", "5", "--runs", "1"], _ROOT)
    assert proc.returncode == 0, proc.stderr
    assert "Peak memory" in proc.stdout
    assert "discover_ms" in proc.stdout  # the retrieval stage is recorded separately (A10)
    assert "total_ms" in proc.stdout
    assert "PENDING" in proc.stdout  # never asserts the reference-hardware gate is met


def test_benchmark_regression_runs_from_repo_root():
    proc = _run(["scripts/benchmark_regression.py", "--notes", "5", "--runs", "2"], _ROOT)
    assert proc.returncode == 0, proc.stderr
    assert "total_pipeline" in proc.stdout


def test_benchmark_regression_json_emits_raw_samples():
    proc = _run(["scripts/benchmark_regression.py", "--notes", "5", "--runs", "3", "--json"],
                _ROOT)
    assert proc.returncode == 0, proc.stderr
    import json
    data = json.loads(proc.stdout)
    assert len(data["total_pipeline"]["raw_ms"]) == 3


def test_smoke_fails_when_runtime_dependency_unavailable(tmp_path: Path):
    # Copy only the script (no sibling src/ or tests/) so its self-bootstrap cannot find
    # jarvis_core: direct execution must fail, proving the smoke detects a broken environment.
    (tmp_path / "scripts").mkdir()
    shutil.copy2(_ROOT / "scripts" / "benchmark_query.py", tmp_path / "scripts")
    proc = _run(["scripts/benchmark_query.py", "--sizes", "5", "--runs", "1"], tmp_path)
    assert proc.returncode != 0
    assert "ModuleNotFoundError" in proc.stderr or "Error" in proc.stderr


@pytest.mark.skipif(shutil.which("git") is None, reason="git not available")
def test_benchmark_paired_entrypoint_smoke(tmp_path: Path):
    # The paired tool runs end-to-end when given a baseline tree. Use the current tree as a
    # stand-in baseline (tiny workload) to exercise argument parsing and both subprocess runs.
    baseline = tmp_path / "baseline"
    shutil.copytree(_ROOT / "src", baseline / "src")
    shutil.copytree(_ROOT / "tests", baseline / "tests")
    (baseline / "scripts").mkdir()
    shutil.copy2(_ROOT / "scripts" / "benchmark_regression.py", baseline / "scripts")
    proc = _run(["scripts/benchmark_paired.py", "--baseline-root", str(baseline),
                 "--notes", "5", "--runs", "2", "--attempts", "2"], _ROOT)
    assert proc.returncode in (0, 1), proc.stderr  # PASS or honest FAIL, but it must complete
    assert "Aggregate:" in proc.stdout and "GATE" in proc.stdout
