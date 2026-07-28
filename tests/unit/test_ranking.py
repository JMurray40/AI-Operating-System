from __future__ import annotations

from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.query.index import LexicalIndex
from jarvis_core.query.ranking import Ranker, RankingWeights
from jarvis_core.relationships import RelationshipResolver
from jarvis_core.repositories import FileSystemKnowledgeRepository
from tests.support.synthetic_vault import build_feature_vault


def _ranker(path: Path) -> Ranker:
    build_feature_vault(path)
    notes = FileSystemKnowledgeRepository(Config(vault_path=path)).discover()
    index = LexicalIndex(notes)
    report = RelationshipResolver(notes).resolve_all()
    return Ranker(index, report)


def test_title_match_outranks_body_match(tmp_path: Path):
    r = _ranker(tmp_path)
    ranked = r.rank(["invoicing"], {"Invoicing.md", "Ledger.md"})
    assert ranked[0].relpath == "Invoicing.md"
    assert ranked[0].score > 0


def test_exact_title_bonus_applies(tmp_path: Path):
    r = _ranker(tmp_path)
    ranked = r.rank(["ledger"], {"Ledger.md"}, phrase="ledger")
    names = {s.name for s in ranked[0].explanation.signals}
    assert "exact_title" in names


def test_alias_is_a_ranking_signal(tmp_path: Path):
    r = _ranker(tmp_path)
    ranked = r.rank(["billing"], {"Invoicing.md"})
    assert ranked and ranked[0].relpath == "Invoicing.md"
    assert any(s.name == "alias_match" for s in ranked[0].explanation.signals)


def test_tag_is_a_ranking_signal(tmp_path: Path):
    r = _ranker(tmp_path)
    ranked = r.rank(["accounting"], {"Ledger.md"})
    assert any(s.name == "tag_match" for s in ranked[0].explanation.signals)


def test_duplicate_titles_break_ties_by_relpath(tmp_path: Path):
    r = _ranker(tmp_path)
    ranked = r.rank(["report"], {"Report A.md", "Report B.md"}, phrase="report")
    assert [s.relpath for s in ranked] == ["Report A.md", "Report B.md"]
    assert ranked[0].score == ranked[1].score  # identical content -> equal score


def test_ranking_is_deterministic(tmp_path: Path):
    r = _ranker(tmp_path)
    cands = {"Invoicing.md", "Ledger.md", "Scratch.md"}
    a = [(s.relpath, s.score) for s in r.rank(["quickbooks"], cands)]
    b = [(s.relpath, s.score) for s in r.rank(["quickbooks"], cands)]
    assert a == b


def test_relative_relevance_is_relative_to_top(tmp_path: Path):
    r = _ranker(tmp_path)
    ranked = r.rank(["quickbooks"], {"Invoicing.md", "Scratch.md"})
    assert ranked[0].relative_relevance == 1.0
    assert all(0.0 <= s.relative_relevance <= 1.0 for s in ranked)


def test_custom_weights_change_order(tmp_path: Path):
    r = _ranker(tmp_path)
    # Zeroing every weight yields no positive scores -> no results.
    from jarvis_core.query.fields import Field
    zero = RankingWeights(
        field_weights={f: 0.0 for f in Field},
        exact_title=0.0, exact_alias=0.0, graph_proximity=0.0, backlink=0.0,
    )
    zeroed = Ranker(r._index, r._report, zero).rank(["quickbooks"], {"Invoicing.md"})
    assert zeroed == []
