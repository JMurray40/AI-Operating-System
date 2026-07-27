from __future__ import annotations

from jarvis_core.query.compat import read_legacy_citation, read_legacy_result


def test_legacy_citation_maps_confidence_to_relevance():
    out = read_legacy_citation({"title": "X", "confidence": 0.5})
    assert out["relative_relevance"] == 0.5
    assert "confidence" not in out


def test_legacy_result_maps_nested_citations():
    legacy = {"confidence": 0.9, "citations": [{"confidence": 0.4}, {"confidence": 0.1}]}
    out = read_legacy_result(legacy)
    assert out["relative_relevance"] == 0.9
    assert [c["relative_relevance"] for c in out["citations"]] == [0.4, 0.1]
    assert all("confidence" not in c for c in out["citations"])


def test_legacy_reader_never_synthesizes_answer_confidence():
    out = read_legacy_result({"confidence": 0.7})
    assert "answer_confidence" not in out
