"""AC-05-04 — structured claim/evidence validation and deterministic support (fail-closed)."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from jarvis_core.config import Config
from jarvis_core.conversation import PrepareTurnRequest, mock_profile
from jarvis_core.conversation import context as ctx
from jarvis_core.conversation.contract import Coverage, EvidenceError, EvidenceType
from jarvis_core.conversation.evidence import validate_response
from jarvis_core.policy import local_allow_all
from jarvis_core.providers.conversation import structured_answer
from jarvis_core.query.tokenizer import token_set
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


# ------------------------------------------------------------------ happy path
def test_valid_fact_and_inference_and_model_knowledge(prepared) -> None:  # type: ignore[no-untyped-def]
    snap = prepared.snapshot
    i1, i2 = snap.items[0], snap.items[1]
    t1 = next(iter(token_set(i1.excerpt)))
    t2 = next(iter(token_set(i2.excerpt)))
    text = structured_answer([
        (f"A fact about {t1}.", "fact", [i1.item_id]),
        (f"An inference over {t1} and {t2}.", "inference", [i1.item_id, i2.item_id]),
        ("World knowledge.", "model_knowledge", []),
    ])
    ev = _check(prepared, text)
    assert ev.supported_count == 2 and ev.model_knowledge_count == 1
    assert ev.coverage is Coverage.PARTIAL
    types = {c.evidence_type for c in ev.claims}
    assert {EvidenceType.FACT, EvidenceType.INFERENCE, EvidenceType.MODEL_KNOWLEDGE} <= types


def test_model_knowledge_only_is_incomplete(prepared) -> None:  # type: ignore[no-untyped-def]
    ev = _check(prepared, structured_answer([("Just prose.", "model_knowledge", [])]))
    assert ev.coverage is Coverage.INCOMPLETE and ev.supported_count == 0


# ------------------------------------------------------------------ fail-closed
def test_non_json_response_fails_closed(prepared) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(EvidenceError):
        _check(prepared, "The system stores markdown. [C1]")   # legacy free-text markers


def test_missing_claims_list_fails_closed(prepared) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(EvidenceError):
        _check(prepared, '{"answer": "hi"}')


def test_empty_claims_fails_closed(prepared) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(EvidenceError):
        _check(prepared, structured_answer([]))


def test_unknown_claim_type_fails_closed(prepared) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(EvidenceError):
        _check(prepared, structured_answer([("x", "speculation", [])]))


def test_fabricated_evidence_id_fails_closed(prepared) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(EvidenceError):
        _check(prepared, structured_answer([("A fact.", "fact", ["C999"])]))


def test_fact_without_evidence_fails_closed(prepared) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(EvidenceError):
        _check(prepared, structured_answer([("A fact with no citation.", "fact", [])]))


def test_unrelated_current_passage_fails_closed(prepared) -> None:  # type: ignore[no-untyped-def]
    i1 = prepared.snapshot.items[0]
    # cites a real, current item but the claim shares no term with the passage (no support)
    with pytest.raises(EvidenceError):
        _check(prepared, structured_answer([("zzqqxx unrelated.", "fact", [i1.item_id])]))


def test_partial_inference_fails_closed(prepared) -> None:  # type: ignore[no-untyped-def]
    snap = prepared.snapshot
    i1, i2 = snap.items[0], snap.items[1]
    only_c1 = token_set(i1.excerpt) - token_set(i2.excerpt)
    if not only_c1:  # pragma: no cover - fixture always has a distinguishing token
        pytest.skip("fixture lacks a C1-only token")
    t1 = next(iter(only_c1))
    # declares inference over C1+C2 but only C1 is supported => every-premise rule fails
    claim = structured_answer([(f"{t1} zzqqxx", "inference", [i1.item_id, i2.item_id])])
    with pytest.raises(EvidenceError):
        _check(prepared, claim)


def test_model_knowledge_with_evidence_fails_closed(prepared) -> None:  # type: ignore[no-untyped-def]
    i1 = prepared.snapshot.items[0]
    with pytest.raises(EvidenceError):
        _check(prepared, structured_answer([("prose", "model_knowledge", [i1.item_id])]))


def test_adversarial_punctuation_fact_fails_closed(prepared) -> None:  # type: ignore[no-untyped-def]
    i1 = prepared.snapshot.items[0]
    with pytest.raises(EvidenceError):
        _check(prepared, structured_answer([("!!! ??? ...", "fact", [i1.item_id])]))


def test_duplicate_evidence_ids_deduplicated(prepared) -> None:  # type: ignore[no-untyped-def]
    i1 = prepared.snapshot.items[0]
    t1 = next(iter(token_set(i1.excerpt)))
    ev = _check(prepared, structured_answer([(f"About {t1}.", "fact", [i1.item_id, i1.item_id])]))
    assert ev.claims[0].citations == (i1.item_id,)   # de-duplicated, still supported
