"""Single-release compatibility reader for legacy v0.3 query payloads (R6).

This reader accepts stored v0.3 JSON that used ``confidence`` for ranking and maps it to
``relative_relevance`` only. It never reinterprets the value as answer confidence. Writers
emit only the v0.3.1 names; this reader exists solely so previously-stored snapshots remain
loadable for one release.

Removal target: no earlier than the next minor release (v0.4).
"""
from __future__ import annotations

from typing import Any


def read_legacy_citation(data: dict[str, Any]) -> dict[str, Any]:
    """Return a citation dict with legacy ``confidence`` mapped to ``relative_relevance``."""
    out = dict(data)
    if "confidence" in out and "relative_relevance" not in out:
        out["relative_relevance"] = out.pop("confidence")
    return out


def read_legacy_result(data: dict[str, Any]) -> dict[str, Any]:
    """Map a legacy result payload's ranking ``confidence`` to ``relative_relevance``.

    Answer confidence is never synthesized from a ranking value (ADR-0014).
    """
    out = dict(data)
    if "confidence" in out and "relative_relevance" not in out:
        out["relative_relevance"] = out.pop("confidence")
    if isinstance(out.get("citations"), list):
        out["citations"] = [
            read_legacy_citation(c) if isinstance(c, dict) else c for c in out["citations"]
        ]
    return out
