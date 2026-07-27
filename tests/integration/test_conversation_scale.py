"""Conversation retrieval stays bounded and deterministic at scale (100..5000 notes)."""
from __future__ import annotations

import time
from pathlib import Path

import pytest

from jarvis_core.config import Config
from jarvis_core.conversation import ConversationManager
from jarvis_core.query import QueryEngine
from jarvis_core.repositories import FileSystemKnowledgeRepository
from tests.support.synthetic_vault import build_synthetic_vault


def _manager(path: Path) -> ConversationManager:
    notes = FileSystemKnowledgeRepository(Config(vault_path=path)).discover()
    return ConversationManager(QueryEngine(notes))


@pytest.mark.parametrize("n", [100, 500, 1000, 5000])
def test_followup_turn_is_bounded(tmp_path: Path, n: int):
    build_synthetic_vault(tmp_path, n)
    mgr = _manager(tmp_path)
    mgr.ask("Tell me about links")  # seeds focus
    start = time.perf_counter()
    ans, _ = mgr.ask("what about it?")  # pronoun-resolved follow-up
    elapsed = time.perf_counter() - start
    assert ans.effective_query != "what about it?"  # a focus was appended
    assert elapsed < 1.5, f"follow-up turn at n={n} took {elapsed:.3f}s"


def test_scale_conversation_deterministic(tmp_path: Path):
    build_synthetic_vault(tmp_path, 500)
    a = _manager(tmp_path)
    b = _manager(tmp_path)
    for m in (a, b):
        m.ask("Tell me about links")
    r1, _ = a.ask("what about it?")
    r2, _ = b.ask("what about it?")
    assert r1.to_dict() == r2.to_dict()
