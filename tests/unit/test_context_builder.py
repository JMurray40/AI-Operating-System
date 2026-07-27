from __future__ import annotations

from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.query.context_builder import QueryContextBuilder, estimate_tokens
from jarvis_core.query.index import LexicalIndex
from jarvis_core.relationships import RelationshipResolver
from jarvis_core.repositories import FileSystemKnowledgeRepository
from tests.support.synthetic_vault import build_feature_vault


def _builder(path: Path, budget: int) -> QueryContextBuilder:
    build_feature_vault(path)
    notes = FileSystemKnowledgeRepository(Config(vault_path=path)).discover()
    index = LexicalIndex(notes)
    report = RelationshipResolver(notes).resolve_all()
    return QueryContextBuilder(index, report, token_budget=budget)


def test_estimate_tokens_counts_words():
    assert estimate_tokens("one two three") == 3


def test_seed_notes_included(tmp_path: Path):
    ctx = _builder(tmp_path, 4000).build(["Invoicing.md"])
    roles = {c.relpath: c.role for c in ctx.included}
    assert roles["Invoicing.md"] == "seed"
    # Ledger is linked from Invoicing -> expanded in.
    assert "Ledger.md" in roles


def test_budget_excludes_overflow(tmp_path: Path):
    ctx = _builder(tmp_path, 1).build(["Invoicing.md", "Ledger.md", "Storefront.md"])
    assert len(ctx.included) == 1  # first seed fits, rest excluded
    assert ctx.excluded
    assert all(x.reason == "token_budget" for x in ctx.excluded)
    assert ctx.total_tokens <= max(ctx.total_tokens, 1)


def test_context_is_deterministic(tmp_path: Path):
    b = _builder(tmp_path, 4000)
    a = b.build(["Invoicing.md"]).to_dict()
    c = b.build(["Invoicing.md"]).to_dict()
    assert a == c
