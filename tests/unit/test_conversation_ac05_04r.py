"""AC-05-04R — residual: conservative EXACT claim support, not lexical overlap (Handoff 14 §5).

The prior AC-05-04 round's support test was ``token_set(claim) & token_set(excerpt)`` — TRUE
whenever a claim shared even one token with the cited excerpt, INCLUDING an ordinary stopword
("the"/"a"/"is"/"and"/...), since ``token_set`` does not filter them. A negated, numerically
altered, entity-substituted, or wholly fabricated claim that happened to reuse one common word
from the source counted as fully "supported". This file proves the replacement conservative
rule — exact current source sentence/span, exact metadata value, or (for inference) the exact
deterministic ``" and "``-joined conjunction of one exact span per cited premise — rejects
every one of those adversarial shapes, and still accepts a genuinely exact claim.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from jarvis_core.config import Config
from jarvis_core.conversation import PrepareTurnRequest, mock_profile
from jarvis_core.conversation import context as ctx
from jarvis_core.conversation.contract import EvidenceError
from jarvis_core.conversation.evidence import exact_source_spans, validate_response
from jarvis_core.policy import local_allow_all
from jarvis_core.providers.conversation import structured_answer
from jarvis_core.repositories import FileSystemKnowledgeRepository

T = datetime(2026, 8, 1, tzinfo=timezone.utc)


@pytest.fixture(scope="module")
def prepared():  # type: ignore[no-untyped-def]
    repo = FileSystemKnowledgeRepository(Config())
    notes = repo.discover()
    req = PrepareTurnRequest(
        request_id="r", session_id="s", workspace_id="local",
        scope=local_allow_all(workspace_id="local", max_sensitivity="internal"),
        source_root=Path(repo.root), user_text="summarize the AI Operating System project",
        provider_profile=mock_profile(), evaluation_time=T,
    )
    return ctx.prepare(req, notes)


def _check(prepared, text: str):  # type: ignore[no-untyped-def]
    return validate_response(
        prepared.snapshot, text,
        source_root=prepared.source_root, notes_by_relpath=prepared.notes_by_relpath,
    )


def _real_sentence(prepared, index: int = 0) -> tuple[str, str]:  # type: ignore[no-untyped-def]
    """A real exact-source sentence/span from item ``index`` and that item's id."""
    item = prepared.snapshot.items[index]
    spans = [s for s in exact_source_spans(item.excerpt) if s != item.excerpt and s.strip()]
    assert spans, "fixture item has no splittable sentence/line span"
    # Prefer a span with at least a few words so mutation tests below are meaningful.
    sentence = max(spans, key=len)
    return sentence, item.item_id


# ------------------------------------------------------------------ positive control
def test_exact_whole_excerpt_is_supported(prepared) -> None:  # type: ignore[no-untyped-def]
    item = prepared.snapshot.items[0]
    ev = _check(prepared, structured_answer([(item.excerpt, "fact", [item.item_id])]))
    assert ev.supported_count == 1


def test_exact_sentence_span_is_supported(prepared) -> None:  # type: ignore[no-untyped-def]
    sentence, item_id = _real_sentence(prepared)
    ev = _check(prepared, structured_answer([(sentence, "fact", [item_id])]))
    assert ev.supported_count == 1


def test_exact_metadata_value_is_supported(prepared) -> None:  # type: ignore[no-untyped-def]
    item = prepared.snapshot.items[0]
    ev = _check(prepared, structured_answer([(item.title, "fact", [item.item_id])]))
    assert ev.supported_count == 1


# ------------------------------------------------------------------ common-token-only (core fix)
def test_common_token_only_no_longer_counts_as_support(prepared) -> None:  # type: ignore[no-untyped-def]
    """The exact bug this round fixes: sharing ONE word with the excerpt is not support."""
    item = prepared.snapshot.items[0]
    # Guaranteed to share the word "the" (a stopword) with virtually any English excerpt,
    # and nothing else — the prior token-overlap rule would have accepted this.
    claim = "The completely fabricated unrelated statement nobody wrote."
    with pytest.raises(EvidenceError):
        _check(prepared, structured_answer([(claim, "fact", [item.item_id])]))


# ------------------------------------------------------------------ negation
def test_negation_fails_closed(prepared) -> None:  # type: ignore[no-untyped-def]
    sentence, item_id = _real_sentence(prepared)
    negated = sentence.replace(" is ", " is not ", 1) if " is " in sentence else "not " + sentence
    assert negated != sentence
    with pytest.raises(EvidenceError):
        _check(prepared, structured_answer([(negated, "fact", [item_id])]))


# ------------------------------------------------------------------ numeric substitution
def test_numeric_substitution_fails_closed(prepared) -> None:  # type: ignore[no-untyped-def]
    item = prepared.snapshot.items[0]
    # A source-shaped claim asserting a number that is guaranteed not to appear verbatim.
    claim = f"{item.title} has exactly 999999 recorded items."
    with pytest.raises(EvidenceError):
        _check(prepared, structured_answer([(claim, "fact", [item.item_id])]))


# ------------------------------------------------------------------ entity substitution
def test_entity_substitution_fails_closed(prepared) -> None:  # type: ignore[no-untyped-def]
    sentence, item_id = _real_sentence(prepared)
    words = sentence.split()
    if len(words) < 2:  # pragma: no cover - fixture spans are always multi-word
        pytest.skip("fixture sentence too short to substitute a word")
    words[0] = "Zzqqxx-Entity"
    substituted = " ".join(words)
    with pytest.raises(EvidenceError):
        _check(prepared, structured_answer([(substituted, "fact", [item_id])]))


# ------------------------------------------------------------------ partial sentence
def test_partial_sentence_fragment_fails_closed(prepared) -> None:  # type: ignore[no-untyped-def]
    sentence, item_id = _real_sentence(prepared)
    words = sentence.split()
    if len(words) < 4:  # pragma: no cover
        pytest.skip("fixture sentence too short to fragment meaningfully")
    fragment = " ".join(words[: len(words) // 2])  # a real but truncated/partial quote
    assert fragment != sentence
    with pytest.raises(EvidenceError):
        _check(prepared, structured_answer([(fragment, "fact", [item_id])]))


# ------------------------------------------------------------------ reordered punctuation
def test_reordered_punctuation_fails_closed(prepared) -> None:  # type: ignore[no-untyped-def]
    sentence, item_id = _real_sentence(prepared)
    stripped = sentence.rstrip(".!?")
    if stripped == sentence:  # pragma: no cover - no terminal punctuation to move
        pytest.skip("fixture sentence has no trailing punctuation to reorder")
    reordered = "!" + stripped  # move/insert punctuation elsewhere rather than at the tail
    assert reordered != sentence
    with pytest.raises(EvidenceError):
        _check(prepared, structured_answer([(reordered, "fact", [item_id])]))


# ------------------------------------------------------------------ metadata/body mismatch
def test_metadata_body_cross_item_mismatch_fails_closed(prepared) -> None:  # type: ignore[no-untyped-def]
    items = prepared.snapshot.items
    if len(items) < 2:  # pragma: no cover
        pytest.skip("fixture needs at least two items")
    i1, i2 = items[0], items[1]
    if i1.title == i2.title:  # pragma: no cover
        pytest.skip("fixture items have identical titles")
    # i2's exact title cited against i1: a real exact value, but bound to the WRONG item.
    with pytest.raises(EvidenceError):
        _check(prepared, structured_answer([(i2.title, "fact", [i1.item_id])]))


# ------------------------------------------------------------------ multi-premise inference
def test_multi_premise_inference_exact_conjunction_supported(prepared) -> None:  # type: ignore[no-untyped-def]
    i1, i2 = prepared.snapshot.items[0], prepared.snapshot.items[1]
    conclusion = f"{i1.excerpt} and {i2.excerpt}"
    ev = _check(prepared, structured_answer([(conclusion, "inference", [i1.item_id, i2.item_id])]))
    assert ev.supported_count == 1


def test_multi_premise_inference_synthesized_conclusion_fails_closed(prepared) -> None:  # type: ignore[no-untyped-def]
    i1, i2 = prepared.snapshot.items[0], prepared.snapshot.items[1]
    # A plausible-sounding SYNTHESIZED conclusion (not the exact deterministic conjunction of
    # the two premises' exact spans) must fail closed: no broad entailment is authorized.
    conclusion = f"Because {i1.title} and {i2.title} are related, this follows."
    with pytest.raises(EvidenceError):
        _check(
            prepared, structured_answer([(conclusion, "inference", [i1.item_id, i2.item_id])])
        )


def test_multi_premise_inference_wrong_order_fails_closed(prepared) -> None:  # type: ignore[no-untyped-def]
    i1, i2 = prepared.snapshot.items[0], prepared.snapshot.items[1]
    # The exact spans exist, but joined in the WRONG order relative to the citation order —
    # not an exact match of any authorized combination for this citation order.
    conclusion = f"{i2.excerpt} and {i1.excerpt}"
    if conclusion == f"{i1.excerpt} and {i2.excerpt}":  # pragma: no cover
        pytest.skip("fixture excerpts happen to be order-symmetric")
    with pytest.raises(EvidenceError):
        _check(
            prepared, structured_answer([(conclusion, "inference", [i1.item_id, i2.item_id])])
        )


def test_multi_premise_inference_missing_one_premise_link_fails_closed(prepared) -> None:  # type: ignore[no-untyped-def]
    i1, i2 = prepared.snapshot.items[0], prepared.snapshot.items[1]
    # Only i1's exact span, with unrelated filler standing in for the second premise.
    conclusion = f"{i1.excerpt} and something else entirely"
    with pytest.raises(EvidenceError):
        _check(
            prepared, structured_answer([(conclusion, "inference", [i1.item_id, i2.item_id])])
        )
