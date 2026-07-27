from __future__ import annotations

import pytest

from jarvis_core.query.compat import (
    LegacyContractError,
    read_legacy_citation,
    read_legacy_result,
)


def test_maps_confidence_to_relevance():
    out = read_legacy_citation({"title": "X", "confidence": 0.5})
    assert out["relative_relevance"] == 0.5
    assert "confidence" not in out


def test_both_keys_equal_drops_old():
    out = read_legacy_citation({"confidence": 0.4, "relative_relevance": 0.4})
    assert out == {"relative_relevance": 0.4}


def test_both_keys_conflict_rejected():
    with pytest.raises(LegacyContractError):
        read_legacy_citation({"confidence": 0.4, "relative_relevance": 0.9})


def test_wrong_type_rejected():
    with pytest.raises(LegacyContractError):
        read_legacy_citation({"confidence": "high"})
    with pytest.raises(LegacyContractError):
        read_legacy_citation({"confidence": True})  # bool is not a ranking number


def test_out_of_range_rejected():
    with pytest.raises(LegacyContractError):
        read_legacy_citation({"confidence": 1.5})


def test_non_mapping_rejected():
    with pytest.raises(LegacyContractError):
        read_legacy_citation(["not", "a", "dict"])  # type: ignore[arg-type]


def test_nested_citations_mapped_and_bad_shape_rejected():
    ok = read_legacy_result({"confidence": 0.9, "citations": [{"confidence": 0.1}]})
    assert ok["relative_relevance"] == 0.9
    assert ok["citations"][0] == {"relative_relevance": 0.1}
    with pytest.raises(LegacyContractError):
        read_legacy_result({"citations": "notalist"})


def test_never_synthesizes_answer_confidence():
    out = read_legacy_result({"confidence": 0.7})
    assert "answer_confidence" not in out


def test_none_value_allowed():
    out = read_legacy_citation({"confidence": None})
    assert out["relative_relevance"] is None
