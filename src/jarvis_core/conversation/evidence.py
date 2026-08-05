"""Claim evidence validation and coverage assembly (R6, C16-C20).

Maps provider prose to snapshot evidence IDs only, classifies each material claim, and
revalidates every cited passage against *current* source bytes immediately before emission.
It cannot fabricate a citation, silently retarget a stale passage, or present model prose as
a source fact. If a claim cites a source whose current bytes no longer support it, the whole
answer is withheld with a typed evidence failure (degraded-operation matrix).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from jarvis_core.conversation.contract import (
    Coverage,
    EvidenceError,
    EvidenceType,
)
from jarvis_core.conversation.snapshot import ContextSnapshot
from jarvis_core.models.note import Note
from jarvis_core.query.evidence import CurrentSourceResolver
from jarvis_core.query.passages import Locator, validate

_MARKER_RE = re.compile(r"\[(C\d+)\]")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


@dataclass(frozen=True)
class Claim:
    """One material claim with its taxonomy and (validated) citations."""

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
    assumptions: tuple[dict[str, object], ...]
    conflicts: tuple[dict[str, object], ...]
    limitations: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "claims": [c.to_dict() for c in self.claims],
            "coverage": self.coverage.value,
            "supported_count": self.supported_count,
            "model_knowledge_count": self.model_knowledge_count,
            "unknown_count": self.unknown_count,
            "assumptions": list(self.assumptions),
            "conflicts": list(self.conflicts),
            "limitations": list(self.limitations),
        }


def _split_claims(text: str) -> list[str]:
    fragments: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        for sentence in _SENTENCE_SPLIT.split(line):
            sentence = sentence.strip()
            if sentence:
                fragments.append(sentence)
    return fragments


def _validate_citation(
    snapshot: ContextSnapshot,
    item_id: str,
    resolver: CurrentSourceResolver,
    notes_by_relpath: dict[str, Note],
) -> None:
    item = snapshot.item(item_id)
    if item is None:
        raise EvidenceError(f"claim cites unknown snapshot item {item_id}")
    if not item.excerpt.strip() or (item.line_start, item.line_end) == (0, 0):
        raise EvidenceError(f"item {item_id} has an empty excerpt or 0-0 locator")
    note = notes_by_relpath.get(item.relpath)
    if note is None:
        raise EvidenceError(f"item {item_id} source is no longer present")
    current_bytes = resolver.current_bytes(note)
    current_text = current_bytes.decode("utf-8", "replace")
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
        raise EvidenceError(f"citation for {item_id} failed current-byte validation")


def validate_response(
    snapshot: ContextSnapshot,
    text: str,
    *,
    source_root: Path,
    notes_by_relpath: dict[str, Note],
) -> AnswerEvidence:
    """Validate provider prose into a typed, current-citation-backed evidence view."""
    resolver = CurrentSourceResolver(source_root)
    fragments = _split_claims(text)

    claims: list[Claim] = []
    supported = model_knowledge = 0
    for fragment in fragments:
        markers = tuple(dict.fromkeys(_MARKER_RE.findall(fragment)))
        if markers:
            for item_id in markers:
                _validate_citation(snapshot, item_id, resolver, notes_by_relpath)
            etype = EvidenceType.FACT if len(markers) == 1 else EvidenceType.INFERENCE
            claims.append(Claim(fragment, etype, markers))
            supported += 1
        else:
            claims.append(Claim(fragment, EvidenceType.MODEL_KNOWLEDGE, ()))
            model_knowledge += 1

    unknown = 1 if not fragments else 0
    if not fragments:
        claims.append(Claim("", EvidenceType.UNKNOWN, ()))

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
        limitations.append("answer contains model-knowledge statements not backed by vault sources")
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
