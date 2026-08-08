"""Structured claim/evidence validation and coverage assembly (R6, C16-C20, AC-05-04R).

The provider must return the structured answer contract — a JSON object with a ``claims``
list, each claim declaring a permitted ``type`` and its ``evidence`` IDs — never free-text
markers. Every claim's shape, taxonomy, IDs, current-source bytes, and deterministic support
are validated. A declared ``fact``/``inference`` whose evidence is missing, stale, unknown,
or not actually supported by the cited passage FAILS CLOSED (the whole answer is withheld
with a typed evidence failure). Unsupported content stays visibly ``model_knowledge`` /
``unknown`` / ``assumption`` and is never silently upgraded to supported.

AC-05-04R: support is CONSERVATIVE EXACT matching, not lexical overlap. The prior round's
support test was ``token_set(claim) & token_set(excerpt)`` — true whenever a claim shared even
one token (including a stopword like "the"/"a"/"is", since ``token_set`` does not filter
stopwords) with the cited excerpt, so an entirely fabricated or negated claim that merely
reused one common word from the source counted as "supported". A fact/inference claim may now
be ``supported`` only when its normalized text is bound to an exact current source
sentence/span, an exact whole excerpt, or an exact approved metadata value (title, relpath,
source id, heading path, or match reason) of the cited item, under a wholly deterministic
rule. A material transformation, added entity, changed number, changed polarity, negation, or
a partial/common-token-only match therefore fails closed as unsupported (the whole answer is
withheld). An inference additionally requires the claim to be exactly the deterministic
``" and "``-joined concatenation of one exact span per cited premise, in citation order — the
only entailment rule this milestone authorizes; anything else fails closed. No embeddings,
semantic models, live providers, or fuzzy thresholds are used.
"""
from __future__ import annotations

import itertools
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from jarvis_core.conversation.contract import (
    RESPONSE_CONTRACT_VERSION,
    Coverage,
    EvidenceError,
    EvidenceType,
)
from jarvis_core.conversation.snapshot import ContextItem, ContextSnapshot
from jarvis_core.models.note import Note
from jarvis_core.query.evidence import CurrentSourceResolver
from jarvis_core.query.passages import Locator, validate

_SOURCE_BACKED = frozenset({EvidenceType.FACT, EvidenceType.INFERENCE})
_UNSUPPORTED = frozenset(
    {EvidenceType.MODEL_KNOWLEDGE, EvidenceType.UNKNOWN, EvidenceType.ASSUMPTION}
)

# The sole authorized deterministic connector for reconstructing an inference conclusion from
# its premises' exact spans (AC-05-04R). Fixed and literal; never inferred or configurable.
_INFERENCE_CONNECTOR = " and "

_EDGE_STRIP = " \t\r\n.,;:!?\"'()[]{}\u2018\u2019\u201c\u201d"
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def _normalize_for_exact_match(text: str) -> str:
    """Deterministic normalization for exact support: collapse whitespace, strip only the
    outer edges of a value, casefold. No stemming, no reordering, no synonym/fuzzy matching —
    a claim differing anywhere in its interior fails to match, by design."""
    collapsed = " ".join(text.split())
    return collapsed.strip(_EDGE_STRIP).casefold()


def _exact_source_spans(excerpt: str) -> list[str]:
    """The deterministic candidate exact spans of one cited excerpt: each sentence, each
    non-blank line, and the whole excerpt. All are drawn only from the current, already
    byte-validated excerpt text — never synthesized or paraphrased."""
    spans: list[str] = [excerpt]
    spans.extend(s for s in _SENTENCE_SPLIT_RE.split(excerpt) if s.strip())
    spans.extend(line for line in excerpt.splitlines() if line.strip())
    return spans


def _exact_metadata_values(item: ContextItem) -> list[str]:
    """The deterministic candidate exact approved metadata values for one cited item."""
    values = [item.title, item.relpath, item.source_id, item.reason]
    if item.sensitivity:
        values.append(item.sensitivity)
    if item.heading_path:
        values.append(" ".join(item.heading_path))
    return [v for v in values if v]


def _exact_candidates(item: ContextItem) -> list[str]:
    return _exact_source_spans(item.excerpt) + _exact_metadata_values(item)


def _claim_exactly_supported(claim_text: str, item: ContextItem) -> bool:
    """AC-05-04R fact rule: exact current source sentence/span OR exact metadata value."""
    normalized_claim = _normalize_for_exact_match(claim_text)
    if not normalized_claim:
        return False
    return any(
        _normalize_for_exact_match(candidate) == normalized_claim
        for candidate in _exact_candidates(item)
    )


def _inference_exactly_supported(claim_text: str, premises: list[ContextItem]) -> bool:
    """AC-05-04R inference rule: the claim is exactly the deterministic ``" and "``-joined
    concatenation of one exact span/metadata value per premise, in citation order. This is
    the only authorized entailment rule; anything else — including a claim that merely
    restates one premise, or a synthesized/paraphrased conclusion — fails closed."""
    normalized_claim = _normalize_for_exact_match(claim_text)
    if not normalized_claim or not premises:
        return False
    per_premise_candidates = [_exact_candidates(p) for p in premises]
    # Bounded: excerpts are budget-limited to a handful of sentences/lines each, so the
    # product of candidate spans across premises stays small (never unbounded/live).
    for combo in itertools.product(*per_premise_candidates):
        candidate = _INFERENCE_CONNECTOR.join(combo)
        if _normalize_for_exact_match(candidate) == normalized_claim:
            return True
    return False


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


def _validate_current_premise(
    snapshot: ContextSnapshot,
    item_id: str,
    resolver: CurrentSourceResolver,
    notes_by_relpath: dict[str, Note],
) -> ContextItem:
    """Validate one cited premise is known, current, and byte-valid (fails closed).

    This is deliberately separate from the exact-support test below: an item can be a
    perfectly valid, current, unmodified citation while still not exactly supporting a
    particular claim's text.
    """
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
    return item


def _validate_fact(
    snapshot: ContextSnapshot,
    ids: tuple[str, ...],
    claim_text: str,
    resolver: CurrentSourceResolver,
    notes_by_relpath: dict[str, Note],
) -> None:
    """AC-05-04R: every cited item must independently be current AND exactly support the
    claim (a fact citing several sources means the same exact statement appears in each)."""
    for item_id in ids:
        item = _validate_current_premise(snapshot, item_id, resolver, notes_by_relpath)
        if not _claim_exactly_supported(claim_text, item):
            raise EvidenceError(
                f"claim is not exactly supported by cited passage/metadata {item_id}"
            )


def _validate_inference(
    snapshot: ContextSnapshot,
    ids: tuple[str, ...],
    claim_text: str,
    resolver: CurrentSourceResolver,
    notes_by_relpath: dict[str, Note],
) -> None:
    """AC-05-04R: every premise must independently be current; the conclusion must be exactly
    the deterministic conjunction of one exact span per premise (the sole authorized
    entailment rule). No authorized rule -> fail closed as incomplete."""
    premises = [
        _validate_current_premise(snapshot, item_id, resolver, notes_by_relpath)
        for item_id in ids
    ]
    if not _inference_exactly_supported(claim_text, premises):
        raise EvidenceError(
            "inference conclusion is not the exact deterministic conjunction of its "
            f"cited premises {list(ids)}"
        )


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
            # AC-05-04R: fact requires each citation to independently exactly support the
            # claim; inference requires the exact deterministic conjunction of every premise.
            if etype is EvidenceType.FACT:
                _validate_fact(snapshot, ids, ctext, resolver, notes_by_relpath)
            else:
                _validate_inference(snapshot, ids, ctext, resolver, notes_by_relpath)
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


__all__ = [
    "AnswerEvidence",
    "Claim",
    "exact_source_spans",
    "validate_response",
]


def exact_source_spans(excerpt: str) -> list[str]:
    """Public accessor for the AC-05-04R deterministic exact-span candidates of an excerpt.

    Exposed so callers/tests can construct a genuinely exactly-supported claim from a real
    excerpt without duplicating (or drifting from) the production sentence/line-splitting
    rule.
    """
    return _exact_source_spans(excerpt)
