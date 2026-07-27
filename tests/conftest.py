"""Shared test paths."""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES


@pytest.fixture
def aios_dir() -> Path:
    return FIXTURES / "ai-operating-system"


@pytest.fixture
def fileorbit_dir() -> Path:
    return FIXTURES / "fileorbit"


@pytest.fixture
def edge_dir() -> Path:
    return FIXTURES / "edge-cases"
