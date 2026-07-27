from __future__ import annotations

from pathlib import Path

import pytest

from jarvis_core.config import Config
from jarvis_core.query.context_builder import QueryContextBuilder
from jarvis_core.query.index import LexicalIndex
from jarvis_core.relationships import RelationshipResolver
from jarvis_core.repositories import FileSystemKnowledgeRepository
from tests.support.synthetic_vault import build_feature_vault


def _builder(path: Path, budget: int) -> QueryContextBuilder:
    build_feature_vault(path)
    notes = FileSystemKnowledgeRepository(Config(vault_path=path)).discover()
    idx = LexicalIndex(notes)
    rep = RelationshipResolver(notes).resolve_all()
    return QueryContextBuilder(idx, rep, token_budget=budget)


def test_negative_budget_fails_at_construction(tmp_path: Path):
    build_feature_vault(tmp_path)
    notes = FileSystemKnowledgeRepository(Config(vault_path=tmp_path)).discover()
    idx = LexicalIndex(notes)
    rep = RelationshipResolver(notes).resolve_all()
    with pytest.raises(ValueError):
        QueryContextBuilder(idx, rep, token_budget=-1)


def test_zero_budget_is_empty(tmp_path: Path):
    ctx = _builder(tmp_path, 0).build(["Invoicing.md", "Ledger.md"])
    assert ctx.included == ()
    assert ctx.total_tokens == 0


def test_budget_invariant_property_loop(tmp_path: Path):
    # rebuild builders at many budgets and assert the invariant every time
    build_feature_vault(tmp_path)
    notes = FileSystemKnowledgeRepository(Config(vault_path=tmp_path)).discover()
    idx = LexicalIndex(notes)
    rep = RelationshipResolver(notes).resolve_all()
    seeds = ["Invoicing.md", "Ledger.md", "Storefront.md", "Payments.md"]
    for budget in range(0, 40):
        ctx = QueryContextBuilder(idx, rep, token_budget=budget).build(seeds)
        assert 0 <= ctx.total_tokens <= budget


def test_oversized_first_note_truncated(tmp_path: Path):
    ctx = _builder(tmp_path, 3).build(["Invoicing.md", "Ledger.md"])
    assert ctx.total_tokens <= 3
    if ctx.included:
        assert ctx.included[0].truncated is True
        assert ctx.included[0].tokens <= 3


def test_context_is_deterministic(tmp_path: Path):
    b = _builder(tmp_path, 50)
    assert b.build(["Invoicing.md"]).to_dict() == b.build(["Invoicing.md"]).to_dict()
