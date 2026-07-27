from __future__ import annotations

from pathlib import Path

import pytest

from jarvis_core.config import Config
from jarvis_core.context.loader import ProjectContextLoader, ProjectNotFoundError
from jarvis_core.repositories import FileSystemKnowledgeRepository


def _loader(path: Path) -> ProjectContextLoader:
    return ProjectContextLoader(FileSystemKnowledgeRepository(Config(vault_path=path)).discover())


def test_load_aios_project(aios_dir: Path):
    pkg = _loader(aios_dir).load("AI Operating System")
    assert pkg.project_id == "project-ai-operating-system"
    assert pkg.priority == "high"
    assert len(pkg.decisions) == 2
    assert len(pkg.sessions) == 1
    assert len(pkg.resources) == 1
    assert len(pkg.concepts) == 1
    assert pkg.resume and "context assembly" in pkg.resume
    assert len(pkg.outstanding_questions) == 2


def test_load_by_alias(aios_dir: Path):
    pkg = _loader(aios_dir).load("AIOS")
    assert pkg.project_title == "AI Operating System"


def test_load_fileorbit_project(fileorbit_dir: Path):
    pkg = _loader(fileorbit_dir).load("FileOrbit")
    assert pkg.project_id == "project-fileorbit"
    assert len(pkg.decisions) == 1
    assert len(pkg.sessions) == 1
    assert any("cloud" in (pkg.summary or "").lower() for _ in [0])


def test_unknown_project_raises(aios_dir: Path):
    with pytest.raises(ProjectNotFoundError):
        _loader(aios_dir).load("Does Not Exist")


def test_decisions_sorted_by_date_then_id(aios_dir: Path):
    pkg = _loader(aios_dir).load("AI Operating System")
    dates = [d.decision_date for d in pkg.decisions]
    assert dates == sorted(dates)
