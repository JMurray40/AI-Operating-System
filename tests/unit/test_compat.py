from __future__ import annotations

import pytest

from jarvis_core.query.compat import (
    LegacyContractError,
    read_legacy_citation,
    read_legacy_result,
)


def _legacy_cit(**over):
    base = {"id": "x", "title": "T", "relpath": "t.md", "confidence": 0.5, "reason": "r"}
    base.update(over)
    return base


def test_exact_legacy_citation_maps_and_drops_old():
    out = read_legacy_citation(_legacy_cit(confidence=0.4))
    assert out["relative_relevance"] == 0.4
    assert "confidence" not in out


def test_both_keys_equal_ok_conflict_rejected():
    assert read_legacy_citation(_legacy_cit(confidence=0.4, relative_relevance=0.4))
    with pytest.raises(LegacyContractError):
        read_legacy_citation(_legacy_cit(confidence=0.4, relative_relevance=0.9))


def test_unknown_key_rejected():
    with pytest.raises(LegacyContractError):
        read_legacy_citation(_legacy_cit(bogus=1))


def test_missing_required_rejected():
    d = _legacy_cit()
    del d["relpath"]
    with pytest.raises(LegacyContractError):
        read_legacy_citation(d)


def test_new_only_citation_rejected_at_legacy_boundary():
    with pytest.raises(LegacyContractError):
        read_legacy_citation({"title": "T", "relpath": "t.md", "reason": "r",
                              "relative_relevance": 0.5})


def test_wrong_type_and_out_of_range_rejected():
    with pytest.raises(LegacyContractError):
        read_legacy_citation(_legacy_cit(confidence="high"))
    with pytest.raises(LegacyContractError):
        read_legacy_citation(_legacy_cit(confidence=True))
    with pytest.raises(LegacyContractError):
        read_legacy_citation(_legacy_cit(confidence=1.5))


def test_result_shape_as_citation_rejected():
    with pytest.raises(LegacyContractError):
        read_legacy_citation({"intent": "search", "question": "q", "answer": "a",
                              "citations": []})


def test_exact_legacy_result_maps_nested_citations():
    result = {"intent": "search", "question": "q", "answer": "a",
              "citations": [_legacy_cit(confidence=0.1), _legacy_cit(confidence=0.9)]}
    out = read_legacy_result(result)
    assert [c["relative_relevance"] for c in out["citations"]] == [0.1, 0.9]
    assert all("confidence" not in c for c in out["citations"])


def test_result_unknown_key_and_missing_rejected():
    with pytest.raises(LegacyContractError):
        read_legacy_result({"intent": "s", "question": "q", "answer": "a",
                            "citations": [], "bogus": 1})
    with pytest.raises(LegacyContractError):
        read_legacy_result({"intent": "s", "question": "q", "answer": "a"})


def test_citation_shape_as_result_rejected():
    with pytest.raises(LegacyContractError):
        read_legacy_result(_legacy_cit())


def test_result_citations_must_be_list_and_validated():
    with pytest.raises(LegacyContractError):
        read_legacy_result({"intent": "s", "question": "q", "answer": "a",
                            "citations": "notalist"})
    with pytest.raises(LegacyContractError):
        read_legacy_result({"intent": "s", "question": "q", "answer": "a",
                            "citations": [{"title": "T"}]})  # bad nested citation


def test_none_confidence_allowed():
    out = read_legacy_citation(_legacy_cit(confidence=None))
    assert out["relative_relevance"] is None
