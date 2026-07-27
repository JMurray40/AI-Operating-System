from __future__ import annotations

from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.query.fields import Field
from jarvis_core.query.index import LexicalIndex
from jarvis_core.repositories import FileSystemKnowledgeRepository
from tests.support.synthetic_vault import build_feature_vault


def _index(path: Path) -> LexicalIndex:
    build_feature_vault(path)
    notes = FileSystemKnowledgeRepository(Config(vault_path=path)).discover()
    return LexicalIndex(notes)


def test_candidates_union(tmp_path: Path):
    idx = _index(tmp_path)
    hits = idx.candidates(["quickbooks"])
    assert "Invoicing.md" in hits
    assert "Scratch.md" in hits  # missing-frontmatter note still indexed


def test_field_counts(tmp_path: Path):
    idx = _index(tmp_path)
    ni = idx.get("Invoicing.md")
    assert ni.count(Field.TITLE, "invoicing") == 1
    assert ni.count(Field.ALIAS, "billing") == 1
    assert ni.count(Field.TAG, "finance") == 1


def test_wikilink_field_indexed(tmp_path: Path):
    idx = _index(tmp_path)
    assert idx.get("Ledger.md").count(Field.WIKILINK, "invoicing") == 1


def test_missing_term_has_no_postings(tmp_path: Path):
    idx = _index(tmp_path)
    assert idx.candidates(["nonexistentzzz"]) == set()
    assert idx.vocabulary_size > 0
