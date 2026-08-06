"""Structured claim/evidence validation and coverage assembly (R6, C16-C20, AC-05-04).

The provider must return the structured answer contract — a JSON object with a ``claims``
list, each claim declaring a permitted ``type`` and its ``evidence`` IDs — never free-text
markers. Every claim's shape, taxonomy, IDs, current-source bytes, and deterministic support
are validated. A declared ``fact``/``inference`` whose evidence is missing, stale, unknown,
or not actually supported by the cited passage FAILS CLOSED (the whole answer is withheld
with a typed evidence failure). Unsupported content stays visibly ``model_knowledge`` /
``unknown`` / ``assumption`` and is never silently upgraded to supported. No live model or
semantic/embedding dependency is used — support is a deterministic lexical-overlap test over
the released tokenizer plus current-byte citation validation.
"""
from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from jarvis_core.conversation.contract import (
    RESPONSE_CONTRACT_VERSION,
    Coverage,
    EvidenceError,
    EvidenceType,
)
from jarvis_core.conversation.snapshot import ContextSnapshot
from jarvis_core.models.note import Note
from jarvis_core.query.evidence import CurrentSourceResolver
from jarvis_core.query.passages import Locator, validate
from jarvis_core.query.tokenizer import token_set

_SOURCE_BACKED = frozenset({EvidenceType.FACT, EvidenceType.INFERENCE})
_UNSUPPORTED = frozenset(
    {EvidenceType.MODEL_KNOWLEDGE, EvidenceType.UNKNOWN, EvidenceType.ASSUMPTION}
)


@dataclass(frozen=True)
class Claim:
    """One material claim with its taxonomy and validated evidence IDs."""

    text: str
    evidence_type: EvidenceType
    citations: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "text": self.text,
            "evidence_type": self.evidence_type.value,
            "citations": list(self.citations),
        }


@dataclass(frozen=True)
class AnswerEvidence:
    """The validated evidence view for one answer."""

    claims: tuple[Claim, ...]
    coverage: Coverage
    supported_count: int
    model_knowledge_count: int
    unknown_count: int
    assumptions: tuple[Mapping[str, object], ...]
    conflicts: tuple[Mapping[str, object], ...]
    limitations: tuple[str, ...]
    response_contract_version: str = RESPONSE_CONTRACT_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "response_contract_version": self.response_contract_version,
            "claims": [c.to_dict() for c in self.claims],
            "coverage": self.coverage.value,
            "supported_count": self.supported_count,
            "model_knowledge_count": self.model_knowledge_count,
            "unknown_count": self.unknown_count,
            "assumptions": [dict(a) for a in self.assumptions],
            "conflicts": [dict(c) for c in self.conflicts],
            "limitations": list(self.limitations),
        }


def _current_text(resolver: CurrentSourceResolver, note: Note) -> tuple[bytes, str]:
    current_bytes = resolver.current_bytes(note)
    return current_bytes, current_bytes.decode("utf-8", "replace")


def _validate_supported_premise(
    snapshot: ContextSnapshot,
    item_id: str,
    claim_text: str,
    resolver: CurrentSourceResolver,
    notes_by_relpath: dict[str, Note],
) -> None:
    """Validate one cited premise: known, current, and actually supporting (fails closed)."""
    item = snapshot.item(item_id)
    if item is None:
        raise EvidenceError(f"claim cites unknown evidence id {item_id!r}")
    if not item.excerpt.strip() or (item.line_start, item.line_end) == (0, 0):
        raise EvidenceError(f"evidence {item_id} has an empty excerpt or 0-0 locator")
    note = notes_by_relpath.get(item.relpath)
    if note is None:
        raise EvidenceError(f"evidence {item_id} source is no longer present")
    current_bytes, current_text = _current_text(resolver, note)
    locator = Locator(
        heading_path=item.heading_path,
        line_start=item.line_start,
        line_end=item.line_end,
    )
    result = validate(
        locator=locator,
        excerpt=item.excerpt,
        source_fingerprint=item.source_fingerprint,
        current_bytes=current_bytes,
        current_text=current_text,
    )
    if not result.ok:
        raise EvidenceError(f"evidence {item_id} failed current-byte validation")
    # Deterministic support: the claim must actually overlap the cited passage (relevance),
    # binding metadata claims to their metadata evidence and rejecting unrelated passages.
    if not (token_set(claim_text) & token_set(item.excerpt)):
        raise EvidenceError(f"claim is not supported by cited passage {item_id}")


def _parse_claim(raw: object) -> tuple[str, EvidenceType, tuple[str, ...]]:
    if not isinstance(raw, dict):
        raise EvidenceError("claim is not an object")
    text = raw.get("text")
    ctype = raw.get("type")
    evidence = raw.get("evidence", [])
    if not isinstance(text, str) or not isinstance(ctype, str) or not isinstance(evidence, list):
        raise EvidenceError("malformed claim shape")
    try:
        etype = EvidenceType(ctype)
    except ValueError as exc:
        raise EvidenceError(f"unknown claim type {ctype!r}") from exc
    if not all(isinstance(i, str) for i in evidence):
        raise EvidenceError("evidence id is not a string")
    ids = tuple(dict.fromkeys(i for i in evidence if isinstance(i, str)))
    return text, etype, ids


def validate_response(
    snapshot: ContextSnapshot,
    text: str,
    *,
    source_root: Path,
    notes_by_relpath: dict[str, Note],
) -> AnswerEvidence:
    """Validate the structured provider answer into a typed, supported evidence view."""
    resolver = CurrentSourceResolver(source_root)
    try:
        data = json.loads(text)
    except (ValueError, TypeError) as exc:
        raise EvidenceError("provider response is not the structured answer contract") from exc
    if not isinstance(data, dict) or not isinstance(data.get("claims"), list):
        raise EvidenceError("structured answer is missing a 'claims' list")
    raw_claims = data["claims"]
    if not raw_claims:
        raise EvidenceError("structured answer contains no claims")

    claims: list[Claim] = []
    supported = model_knowledge = unknown = 0
    for raw in raw_claims:
        ctext, etype, ids = _parse_claim(raw)
        if etype in _SOURCE_BACKED:
            if not ids:
                raise EvidenceError(f"{etype.value} claim declares no evidence")
            # Inference validates EVERY material premise; fact validates its citation(s).
            for item_id in ids:
                _validate_supported_premise(
                    snapshot, item_id, ctext, resolver, notes_by_relpath
                )
            supported += 1
        else:
            if ids:
                raise EvidenceError(
                    f"{etype.value} claim must not cite evidence (found {list(ids)})"
                )
            if etype is EvidenceType.MODEL_KNOWLEDGE:
                model_knowledge += 1
            elif etype is EvidenceType.UNKNOWN:
                unknown += 1
        claims.append(Claim(ctext, etype, ids))

    if supported and not model_knowledge and not unknown:
        coverage = Coverage.COMPLETE
    elif supported:
        coverage = Coverage.PARTIAL
    elif model_knowledge:
        coverage = Coverage.INCOMPLETE
    else:
        coverage = Coverage.NONE

    limitations: list[str] = []
    if model_knowledge:
        limitations.append(
            "answer contains model-knowledge statements not backed by vault sources"
        )
    if coverage in (Coverage.INCOMPLETE, Coverage.NONE):
        limitations.append("answer is not fully supported by cited sources")

    return AnswerEvidence(
        claims=tuple(claims),
        coverage=coverage,
        supported_count=supported,
        model_knowledge_count=model_knowledge,
        unknown_count=unknown,
        assumptions=snapshot.assumptions,
        conflicts=(),
        limitations=tuple(limitations),
    )


__all__ = ["AnswerEvidence", "Claim", "validate_response"]
