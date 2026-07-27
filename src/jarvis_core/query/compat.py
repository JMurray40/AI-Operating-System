"""Narrowly bounded single-release compatibility reader for legacy v0.3 payloads (AC-04R2).

Accepts ONLY the exact documented legacy v0.3 result and citation shapes. It is not a generic
dictionary normalizer: unknown keys, missing required keys, result/citation shape confusion,
and non-legacy (new-only) payloads are all rejected. A legacy ranking ``confidence`` is mapped
to ``relative_relevance`` (never to answer confidence, ADR-0014); when both keys are present
they must be equal and the ambiguous old key is always removed. Every ranking value and every
nested citation is validated.

Removal target: no earlier than v0.4. Do not broaden this into a compatibility framework.
"""
from __future__ import annotations

from typing import Any

# Exact v0.3 citation shape: {"id"?, "title", "relpath", "confidence", "reason"}.
_CITATION_REQUIRED = frozenset({"title", "relpath", "reason"})
_CITATION_ALLOWED = _CITATION_REQUIRED | {"id", "confidence", "relative_relevance"}
# Exact v0.3 result shape: {"intent", "question", "answer", "citations"}.
_RESULT_REQUIRED = frozenset({"intent", "question", "answer", "citations"})
_RESULT_ALLOWED = _RESULT_REQUIRED


class LegacyContractError(ValueError):
    """Raised when a payload does not match the exact documented legacy shape."""


def _validate_ranking_value(value: Any, field: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise LegacyContractError(f"{field} must be a number, got {type(value).__name__}")
    v = float(value)
    if not (0.0 <= v <= 1.0):
        raise LegacyContractError(f"{field} out of range [0,1]: {v}")
    return v


def read_legacy_citation(data: dict[str, Any]) -> dict[str, Any]:
    """Map an EXACT legacy v0.3 citation to the v0.3.1 field names, strictly validated."""
    if not isinstance(data, dict):
        raise LegacyContractError(f"citation must be a mapping, got {type(data).__name__}")
    if "citations" in data or "intent" in data:
        raise LegacyContractError("result shape supplied where a citation was expected")
    unknown = set(data) - _CITATION_ALLOWED
    if unknown:
        raise LegacyContractError(f"unknown citation key(s): {sorted(unknown)}")
    missing = _CITATION_REQUIRED - set(data)
    if missing:
        raise LegacyContractError(f"missing required citation key(s): {sorted(missing)}")
    if "confidence" not in data:
        raise LegacyContractError(
            "not a legacy citation (no 'confidence'); use the current reader"
        )
    legacy = _validate_ranking_value(data["confidence"], "confidence")
    out = {k: v for k, v in data.items() if k != "confidence"}
    if "relative_relevance" in out:
        new = _validate_ranking_value(out["relative_relevance"], "relative_relevance")
        if new != legacy:
            raise LegacyContractError("conflicting 'confidence' and 'relative_relevance'")
    out["relative_relevance"] = legacy  # never mapped to answer_confidence
    return out


def read_legacy_result(data: dict[str, Any]) -> dict[str, Any]:
    """Map an EXACT legacy v0.3 result (with nested citations), strictly validated."""
    if not isinstance(data, dict):
        raise LegacyContractError(f"result must be a mapping, got {type(data).__name__}")
    if {"relpath", "confidence", "reason"} & set(data):
        raise LegacyContractError("citation shape supplied where a result was expected")
    unknown = set(data) - _RESULT_ALLOWED
    if unknown:
        raise LegacyContractError(f"unknown result key(s): {sorted(unknown)}")
    missing = _RESULT_REQUIRED - set(data)
    if missing:
        raise LegacyContractError(f"missing required result key(s): {sorted(missing)}")
    cits = data["citations"]
    if not isinstance(cits, list):
        raise LegacyContractError("'citations' must be a list")
    out = dict(data)
    out["citations"] = [read_legacy_citation(c) for c in cits]
    return out
