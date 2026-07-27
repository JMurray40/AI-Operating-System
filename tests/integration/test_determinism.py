from __future__ import annotations

import json
from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.context.loader import ProjectContextLoader
from jarvis_core.providers import get_provider
from jarvis_core.repositories import FileSystemKnowledgeRepository


def _pkg_dict(path: Path, name: str):
    notes = FileSystemKnowledgeRepository(Config(vault_path=path)).discover()
    return ProjectContextLoader(notes).load(name).to_dict()


def test_identical_inputs_produce_identical_json(aios_dir: Path):
    a = json.dumps(_pkg_dict(aios_dir, "AI Operating System"), sort_keys=False)
    b = json.dumps(_pkg_dict(aios_dir, "AI Operating System"), sort_keys=False)
    assert a == b


def test_mock_provider_is_deterministic(fileorbit_dir: Path):
    notes = FileSystemKnowledgeRepository(Config(vault_path=fileorbit_dir)).discover()
    pkg = ProjectContextLoader(notes).load("FileOrbit")
    p = get_provider("mock")
    r1 = p.summarize(pkg)
    r2 = p.summarize(pkg)
    assert r1.to_dict() == r2.to_dict()


def test_collection_ordering_stable(aios_dir: Path):
    pkg = _pkg_dict(aios_dir, "AI Operating System")
    src = [s["relpath"] for s in pkg["sources"]]
    assert src == sorted(src)
