"""Single-release compatibility reader for legacy v0.3 query payloads (R6, AC-04).

Accepts only the documented legacy result/citation shapes (a mapping). It maps a legacy
ranking ``confidence`` to ``relative_relevance`` and never to answer confidence (ADR-0014).
It is strict: a value that is not a number in [0, 1] (or ``None``) is rejected, and a payload
supplying BOTH ``confidence`` and ``relative_relevance`` is accepted only when they are equal
(the ambiguous ``confidence`` key is then always removed); conflicting values are rejected.

Removal target: no earlier than v0.4.
"""
from __future__ import annotations

from typing import Any


class LegacyContractError(ValueError):
    """Raised when a legacy payload does not match the documented compatibility shape."""


def _validate_ranking_value(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise LegacyContractError(
            f"legacy ranking value must be a number, got {type(value).__name__}"
        )
    v = float(value)
    if not (0.0 <= v <= 1.0):
        raise LegacyContractError(f"legacy ranking value out of range [0,1]: {v}")
    return v


def _reconcile(data: dict[str, Any]) -> dict[str, Any]:
    """Map legacy ``confidence`` -> ``relative_relevance`` on one mapping, strictly."""
    if not isinstance(data, dict):
        raise LegacyContractError(f"legacy payload must be a mapping, got {type(data).__name__}")
    out = dict(data)
    if "confidence" not in out:
        return out
    legacy = _validate_ranking_value(out["confidence"])
    if "relative_relevance" in out:
        if out["relative_relevance"] != legacy:
            raise LegacyContractError(
                "conflicting 'confidence' and 'relative_relevance' values"
            )
        out.pop("confidence")            # equal -> always drop the ambiguous old key
        return out
    out.pop("confidence")
    out["relative_relevance"] = legacy   # never mapped to answer_confidence
    return out


def read_legacy_citation(data: dict[str, Any]) -> dict[str, Any]:
    """Return a citation dict with legacy ``confidence`` mapped to ``relative_relevance``."""
    return _reconcile(data)


def read_legacy_result(data: dict[str, Any]) -> dict[str, Any]:
    """Map a legacy result payload's ranking ``confidence`` and its nested citations."""
    out = _reconcile(data)
    cits = out.get("citations")
    if cits is not None:
        if not isinstance(cits, list):
            raise LegacyContractError("legacy 'citations' must be a list")
        out["citations"] = [read_legacy_citation(c) for c in cits]
    return out
