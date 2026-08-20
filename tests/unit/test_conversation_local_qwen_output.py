"""V05-PT-37: end-to-end application-layer behavior for the local profile -- completed-turn
round trip, presentation surface, raw-payload/hostile-content non-leakage across every public
surface (trace, session history, attempt details), zero-provider-request-on-rejection proofs,
and (Handoff 150 sec 3, PT37-CTO-02 correction) the exact non-streaming Ollama request/response
envelope contract -- exact model identity, ``stream=false``, ``num_ctx``, class-specific
``num_predict`` sent; returned model/``prompt_eval_count``/``eval_count``/``done_reason``
verified before any content is trusted (Handoff 148 sec 4 required verification). Fakes/
synthetic fixtures only; the ``LocalOllamaAdapter`` here is always constructed with a
``FakeTransport`` -- no real loopback endpoint, no live Ollama, no network (Handoff 148 sec 3).

V05-PT-37 / Handoff 151, 151a (PT37-CTO-03 closure): the closed local response shape is
amended from the flat ``{"answer","limitations","citations"}`` (147/150) to
``{"claims": [{"text","type","evidence"}, ...], "limitations": [...]}``, routed unchanged
into the SAME ``evidence.validate_response``/``AnswerEvidence`` pipeline the remote/mock
profile already uses (see ``application.py``'s ``_interpret`` local branch). A completed
local turn now carries real per-claim, current-byte-bound support and real coverage
(COMPLETE/PARTIAL/INCOMPLETE/NONE derived from ``evidence.coverage``) instead of the interim
correction round's unconditional ``Coverage.NONE`` fail-safe, which is removed. Tests below
that previously proved "every combination of citations/limitations still yields NONE" are
replaced with tests proving the real per-claim coverage derivation, and the previous "a
valid-but-unrelated citation still yields NONE coverage" hostile-scenario test is replaced
with a strictly stronger outcome: such a claim now fails the whole attempt CLOSED
(``EVIDENCE_FAILED``) via AC-05-04R's exact-match rule, rather than merely staying inert at
NONE.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

from jarvis_core.config import Config
from jarvis_core.conversation import ConversationApplication, PrepareTurnRequest, local_qwen_profile
from jarvis_core.conversation.contract import LocalContextLimitError, LocalNotReadyError
from jarvis_core.conversation.presentation import present
from jarvis_core.conversation.request import Budgets
from jarvis_core.policy import local_allow_all
from jarvis_core.providers.local_ollama import (
    LOCAL_LIMITS,
    LocalOllamaAdapter,
    LocalReadinessGateway,
    LocalReadinessState,
    MemoryObservation,
    SyntheticCapacityProbe,
    SyntheticClock,
    SyntheticTokenCounter,
    canonical_json,
)
from jarvis_core.providers.transport import TransportResponse
from jarvis_core.repositories import FileSystemKnowledgeRepository

T = datetime(2026, 8, 1, tzinfo=timezone.utc)
_OK = MemoryObservation(avail_phys_bytes=16 * 1024**3, memory_load_percent=10)


def _claims_payload(
    claims: list[tuple[str, str, list[str]]], *, limitations: list[str] | None = None
) -> dict:
    """Build a ``FakeTransport`` ``response_payload`` in the closed local schema (Handoff
    151/151a): ``claims`` is a list of ``(text, type, evidence_ids)`` tuples, mirroring
    ``providers.conversation.structured_answer``'s remote/mock convention. ``limitations``
    is the model's own closed-schema field -- validated for shape/hostile content by the
    LOCAL boundary but never merged into the trusted, system-computed
    ``AnswerEvidence.limitations`` (see
    ``test_model_declared_limitations_are_validated_but_not_blindly_trusted_into_output``).
    """
    return {
        "claims": [{"text": t, "type": ty, "evidence": list(ev)} for t, ty, ev in claims],
        "limitations": list(limitations) if limitations is not None else [],
    }


def _fact_claim(item) -> tuple[str, str, list[str]]:
    """A genuinely exactly-supported ``fact`` claim built from a real snapshot item's
    excerpt (AC-05-04R exact-match rule) -- the item's whole excerpt is always one of
    ``evidence.exact_source_spans``'s candidate spans, so this never needs a hand-written
    approximation that could silently drift from the production matching rule."""
    return (item.excerpt, "fact", [item.item_id])


class FakeTransport:
    """Records every request it receives; never touches a socket.

    Handoff 150 sec 3 (PT37-CTO-02): the adapter now sends a full Ollama
    non-streaming request envelope (exact model, ``stream=false``, ``num_ctx``,
    class-specific ``num_predict``) and expects a full completion envelope back
    (returned model, ``prompt_eval_count``, ``eval_count``, ``done_reason``,
    ``response``). By default this fake ECHOES a well-formed envelope derived
    from the EXACT incoming request (model and the real synthetic-counted prompt
    tokens), wrapping ``response_payload`` (the local closed-schema
    claims/limitations dict -- Handoff 151/151a) as the ``response`` string --
    so a normal test describes only its INTENT, not a hand-computed token count.
    Any ``*_override`` keyword replaces exactly one envelope field, which is how
    the adversarial envelope-mismatch tests below target one exact violation at
    a time. ``raw_envelope_bytes`` bypasses all of this and returns the given
    bytes verbatim (for malformed/non-JSON/wrong-shape envelope tests).
    """

    def __init__(
        self,
        response_payload: dict | None = None,
        *,
        raw_envelope_bytes: bytes | None = None,
        model_override: str | None = None,
        prompt_eval_count_override: int | None = None,
        eval_count_override: int | None = None,
        done_reason_override: str | None = None,
        done_override: bool | None = None,
        extra_envelope_fields: dict | None = None,
    ) -> None:
        self._response_payload = (
            response_payload
            if response_payload is not None
            else _claims_payload([("", "unknown", [])])
        )
        self._raw_envelope_bytes = raw_envelope_bytes
        self._model_override = model_override
        self._prompt_eval_count_override = prompt_eval_count_override
        self._eval_count_override = eval_count_override
        self._done_reason_override = done_reason_override
        self._done_override = done_override
        self._extra_envelope_fields = extra_envelope_fields or {}
        self.calls: list = []

    def send(self, request, cancel=None):
        self.calls.append(request)
        if self._raw_envelope_bytes is not None:
            return TransportResponse(
                200, {"content-type": "application/json"}, self._raw_envelope_bytes
            )
        sent = json.loads(request.body.decode("utf-8"))
        real_prompt_tokens = SyntheticTokenCounter().count(sent["prompt"])
        envelope: dict = {
            "model": self._model_override if self._model_override is not None else sent["model"],
            "response": canonical_json(self._response_payload),
            "done": self._done_override if self._done_override is not None else True,
            "done_reason": (
                self._done_reason_override if self._done_reason_override is not None else "stop"
            ),
            "prompt_eval_count": (
                self._prompt_eval_count_override
                if self._prompt_eval_count_override is not None
                else real_prompt_tokens
            ),
            "eval_count": self._eval_count_override if self._eval_count_override is not None else 1,
        }
        envelope.update(self._extra_envelope_fields)
        body = canonical_json(envelope).encode("utf-8")
        return TransportResponse(200, {"content-type": "application/json"}, body)


class ExplodingTransport:
    """Fails the test if ever called -- proves a rejection made zero provider requests."""

    def send(self, request, cancel=None):  # pragma: no cover - must never run
        raise AssertionError("transport must not be called for a pre-provider rejection")


@pytest.fixture(scope="module")
def vault() -> tuple[list, Path]:
    repo = FileSystemKnowledgeRepository(Config())
    return repo.discover(), Path(repo.root)


def _request(
    session_id: str, root: Path, *, text: str = "summarize the AI Operating System project"
) -> PrepareTurnRequest:
    return PrepareTurnRequest(
        request_id="req-out-1",
        session_id=session_id,
        workspace_id="local",
        scope=local_allow_all(workspace_id="local", max_sensitivity="internal"),
        source_root=root,
        user_text=text,
        provider_profile=local_qwen_profile(),
        budgets=Budgets(),
        evaluation_time=T,
        want_trace=True,
    )


def _ready_gateway(*, admission_samples: int = 6) -> LocalReadinessGateway:
    gw = LocalReadinessGateway(capacity_probe=SyntheticCapacityProbe(), clock=SyntheticClock())
    gw.begin_warming()
    gw.complete_warm_up(
        min_probe_ok=True,
        min_probe_elapsed_seconds=1.0,
        max_probe_ok=True,
        max_probe_elapsed_seconds=1.0,
    )
    for _ in range(admission_samples):
        gw._capacity_probe.push(_OK)
    return gw


def _tmp_vault(tmp_path: Path) -> tuple[list, Path]:
    """A disposable, mutable copy of the real fixture vault (mirrors
    ``test_conversation_wp3.py``'s ``_vault`` helper) -- used only by the PT37-CTO-03
    current-byte-drift/removed-item adversarial tests below, which must mutate/delete a
    source file on disk. The shared module-scoped ``vault`` fixture points at the real
    repository fixtures and must never be mutated."""
    src = Path(FileSystemKnowledgeRepository(Config()).root)
    dst = tmp_path / "vault"
    shutil.copytree(src, dst)
    return FileSystemKnowledgeRepository(Config(vault_path=dst)).discover(), dst


def _prepared_and_approved(app: ConversationApplication, vault, *, text: str | None = None):
    notes, root = vault
    session = app.create_session("local")
    gw = _ready_gateway()
    kwargs = {"text": text} if text is not None else {}
    snap = app.prepare_turn(
        session, _request(session.session_id, root, **kwargs), notes, local_gateway=gw
    )
    app.approve(session, actor="jason", now=T)
    return session, snap, gw


# ------------------------------------------------------------------ completed happy path
def test_completed_local_turn_end_to_end(vault) -> None:
    app = ConversationApplication()
    session, snap, gw = _prepared_and_approved(app, vault)
    cited_item = snap.items[0]
    payload = _claims_payload([_fact_claim(cited_item)])
    transport = FakeTransport(payload)
    adapter = LocalOllamaAdapter(gateway=gw, transport=transport, enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "completed"
    assert turn.attempt.failure is None
    assert turn.attempt.evidence is not None
    assert turn.attempt.evidence.supported_count == 1
    assert cited_item.item_id in (turn.attempt.text or "")
    # Handoff 151/151a (PT37-CTO-03 closure): a genuinely exactly-supported fact claim now
    # reaches real COMPLETE coverage via the SAME evidence.validate_response pipeline the
    # remote/mock profile already uses -- replacing the interim unconditional Coverage.NONE.
    assert turn.coverage.value == "complete"
    assert len(transport.calls) == 1


def test_presentation_surfaces_local_claims_the_same_way_as_remote(vault) -> None:
    app = ConversationApplication()
    session, snap, gw = _prepared_and_approved(app, vault)
    cited_item = snap.items[0]
    payload = _claims_payload([_fact_claim(cited_item)])
    adapter = LocalOllamaAdapter(gateway=gw, transport=FakeTransport(payload), enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)
    pres = present(turn)

    assert pres.status == "completed"
    assert pres.coverage == "complete"
    # Handoff 151/151a: local now shares the SAME claims/evidence public surface remote
    # already has -- no longer inert/empty for a completed local turn.
    assert len(pres.claims) == 1
    assert pres.claims[0]["evidence_type"] == "fact"
    assert tuple(pres.claims[0]["citations"]) == (cited_item.item_id,)
    assert pres.citations == (cited_item.item_id,)
    assert cited_item.item_id in (pres.answer or "")

    rendered = pres.to_dict()
    assert len(rendered["attempt"]["claims"]) == 1
    assert rendered["attempt"]["claims"][0]["evidence_type"] == "fact"
    text = pres.to_text()
    assert cited_item.item_id in text


@pytest.mark.parametrize(
    ("claim_types", "expected_coverage"),
    [
        (("fact",), "complete"),
        (("fact", "model_knowledge"), "partial"),
        (("model_knowledge",), "incomplete"),
        (("unknown",), "none"),
        (("assumption",), "none"),
    ],
)
def test_local_coverage_reflects_real_per_claim_support(
    vault, claim_types, expected_coverage
) -> None:
    """Handoff 151/151a (PT37-CTO-03 closure) replaces the interim correction's
    unconditional NONE (which the CTO review found indistinguishable regardless of what
    was actually supported) with the SAME per-claim-typed coverage derivation the
    remote/mock profile already uses -- COMPLETE only when every claim is either
    source-backed or absent-of-gaps, PARTIAL/INCOMPLETE/NONE otherwise."""
    app = ConversationApplication()
    session, snap, gw = _prepared_and_approved(app, vault)
    cited_item = snap.items[0]
    claims: list[tuple[str, str, list[str]]] = []
    for ctype in claim_types:
        if ctype == "fact":
            claims.append(_fact_claim(cited_item))
        else:
            claims.append((f"a {ctype} statement", ctype, []))
    payload = _claims_payload(claims)
    adapter = LocalOllamaAdapter(gateway=gw, transport=FakeTransport(payload), enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "completed"
    assert turn.coverage.value == expected_coverage


# ------------------------------------------------------------------ PT37-CTO-03: real per-claim
# evidence binding (Handoff 151/151a closure) -- local citations now enter the EXACT SAME
# claim/evidence pipeline (evidence.validate_response) the remote/mock contract already uses:
# real current-byte revalidation, real AC-05-04R exact-match support, real coverage. The tests
# below cover every adversarial category Handoff 150/151 sec 4 name: unrelated valid IDs
# (now fails closed, strictly stronger than the interim NONE), current-byte drift, removed
# items, mixed valid/drifted citations, a source-backed claim with no evidence, and an
# unsupported-type claim that improperly cites evidence.


def test_a_valid_but_content_unrelated_citation_now_fails_closed(vault) -> None:
    """The exact PT37-CTO-03 hostile scenario: a citation that is genuinely current and
    genuinely in the snapshot, but whose claim text does not exactly match it. Routed
    through the real evidence pipeline, AC-05-04R's exact-match rule now fails the WHOLE
    attempt closed (EVIDENCE_FAILED) -- a strictly stronger outcome than the interim
    correction round's unconditional-but-still-COMPLETED NONE coverage."""
    app = ConversationApplication()
    session, snap, gw = _prepared_and_approved(app, vault)
    unrelated_item = snap.items[-1]
    unrelated_text = "The sky is blue and bourbon pairs well with barbecue."
    payload = _claims_payload([(unrelated_text, "fact", [unrelated_item.item_id])])
    adapter = LocalOllamaAdapter(gateway=gw, transport=FakeTransport(payload), enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "failed"
    assert turn.attempt.failure.value == "evidence_failed"
    assert turn.coverage.value == "none"
    assert len(session.turns) == 0


class _DriftMidFlightTransport:
    """Wraps a ``FakeTransport`` and runs ``mutate()`` exactly once, the first time
    ``send()`` is called -- i.e. AFTER step 8's pre-dispatch ``_revalidate_current_bytes``
    has already passed (it runs before ``provider.dispatch()``/the transport call) but
    BEFORE the local model's (simulated) reply is interpreted. This is the precise mid-
    flight race window ``evidence.validate_response``'s per-citation current-byte check
    (``_validate_current_premise``) exists to close: pre-dispatch revalidation cannot see
    a mutation that happens while the model is generating."""

    def __init__(self, inner: FakeTransport, mutate) -> None:
        self._inner = inner
        self._mutate = mutate
        self.calls = inner.calls

    def send(self, request, cancel=None):
        self._mutate()
        return self._inner.send(request, cancel)


def test_current_byte_drift_on_a_cited_source_fails_the_attempt_closed(tmp_path: Path) -> None:
    """Handoff 150/151 sec 4 (PT37-CTO-03): a cited source edited AFTER pre-dispatch
    revalidation passed -- while the (potentially slow) local model call is in flight --
    must not reach COMPLETED. ``evidence.validate_response``'s per-citation current-byte
    check runs BEFORE its exact-match check for every fact/inference claim, so this closes
    the exact window pre-dispatch revalidation (step 8) cannot see, regardless of whether
    the claim text would otherwise have matched."""
    app = ConversationApplication()
    notes, root = _tmp_vault(tmp_path)
    session = app.create_session("local")
    gw = _ready_gateway()
    snap = app.prepare_turn(session, _request(session.session_id, root), notes, local_gateway=gw)
    app.approve(session, actor="jason", now=T)
    cited_item = snap.items[0]
    target = root / cited_item.relpath

    def _drift() -> None:
        target.write_bytes(target.read_bytes() + b"\n\ndrift after snapshot, before local reply\n")

    payload = _claims_payload([_fact_claim(cited_item)])
    transport = _DriftMidFlightTransport(FakeTransport(payload), _drift)
    adapter = LocalOllamaAdapter(gateway=gw, transport=transport, enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "failed"
    assert turn.attempt.failure.value == "evidence_failed"
    assert turn.coverage.value == "none"
    assert turn.attempt.text is None
    assert len(session.turns) == 0  # a failed attempt is never recorded as a public turn
    assert "drift after snapshot" not in json.dumps(turn.attempt.to_dict())


def test_a_cited_source_removed_from_the_vault_fails_the_attempt_closed(tmp_path: Path) -> None:
    """Handoff 150/151 sec 4 (PT37-CTO-03): a cited source deleted from disk while the local
    model call is in flight (e.g. a concurrent vault edit) must fail the attempt closed --
    ``CurrentSourceResolver`` returns empty bytes for a missing file (fail-closed by design),
    which then fails locator/fingerprint validation exactly like a drifted file."""
    app = ConversationApplication()
    notes, root = _tmp_vault(tmp_path)
    session = app.create_session("local")
    gw = _ready_gateway()
    snap = app.prepare_turn(session, _request(session.session_id, root), notes, local_gateway=gw)
    app.approve(session, actor="jason", now=T)
    cited_item = snap.items[0]
    target = root / cited_item.relpath

    payload = _claims_payload([_fact_claim(cited_item)])
    transport = _DriftMidFlightTransport(FakeTransport(payload), target.unlink)
    adapter = LocalOllamaAdapter(gateway=gw, transport=transport, enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "failed"
    assert turn.attempt.failure.value == "evidence_failed"
    assert turn.coverage.value == "none"
    assert len(session.turns) == 0


def test_one_drifted_citation_among_several_valid_ones_fails_the_whole_attempt(
    tmp_path: Path,
) -> None:
    """A response mixing a still-current, genuinely-supported fact claim with a second
    fact claim whose citation drifted mid-flight must fail the ENTIRE attempt closed --
    the same "no partial credit" semantics ``evidence.validate_response`` already applies
    to the remote/mock profile, now proven for local too."""
    app = ConversationApplication()
    notes, root = _tmp_vault(tmp_path)
    session = app.create_session("local")
    gw = _ready_gateway()
    snap = app.prepare_turn(session, _request(session.session_id, root), notes, local_gateway=gw)
    app.approve(session, actor="jason", now=T)
    assert len(snap.items) >= 2, "fixture vault must have at least 2 distinct items"
    still_current_item = snap.items[0]
    drifted_item = snap.items[1]
    target = root / drifted_item.relpath

    def _drift() -> None:
        target.write_bytes(target.read_bytes() + b"\n\ndrift after snapshot\n")

    payload = _claims_payload([_fact_claim(still_current_item), _fact_claim(drifted_item)])
    transport = _DriftMidFlightTransport(FakeTransport(payload), _drift)
    adapter = LocalOllamaAdapter(gateway=gw, transport=transport, enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "failed"
    assert turn.attempt.failure.value == "evidence_failed"
    assert len(session.turns) == 0


def test_fact_claim_with_no_evidence_fails_closed_at_the_real_evidence_pipeline(vault) -> None:
    """The LOCAL closed-schema boundary (``validate_local_response``) deliberately does
    NOT itself enforce fact/inference-requires-evidence coherence -- that taxonomy/support
    semantics is exclusively ``evidence.validate_response``'s job (Handoff 151a §3 item 2),
    proven here end-to-end rather than only at the schema-boundary unit-test level."""
    app = ConversationApplication()
    session, _snap, gw = _prepared_and_approved(app, vault)
    payload = _claims_payload([("an unsupported fact claim", "fact", [])])
    adapter = LocalOllamaAdapter(gateway=gw, transport=FakeTransport(payload), enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "failed"
    assert turn.attempt.failure.value == "evidence_failed"
    assert len(session.turns) == 0


def test_model_knowledge_claim_citing_evidence_fails_closed(vault) -> None:
    """A model_knowledge/unknown/assumption claim must never cite evidence -- proven
    end-to-end for local the same way it already holds for remote/mock."""
    app = ConversationApplication()
    session, snap, gw = _prepared_and_approved(app, vault)
    cited_item = snap.items[0]
    payload = _claims_payload([("an unsupported claim", "model_knowledge", [cited_item.item_id])])
    adapter = LocalOllamaAdapter(gateway=gw, transport=FakeTransport(payload), enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "failed"
    assert turn.attempt.failure.value == "evidence_failed"
    assert len(session.turns) == 0


def test_inference_claim_exact_premise_conjunction_is_supported(vault) -> None:
    """AC-05-04R's inference rule: the claim text must be exactly the ``" and "``-joined
    conjunction of one exact span per cited premise, in citation order -- proven for local
    via the same pipeline remote/mock already uses."""
    app = ConversationApplication()
    session, snap, gw = _prepared_and_approved(app, vault)
    assert len(snap.items) >= 2, "fixture vault must have at least 2 distinct items"
    premises = snap.items[:2]
    inference_text = " and ".join(item.excerpt for item in premises)
    payload = _claims_payload(
        [(inference_text, "inference", [item.item_id for item in premises])]
    )
    adapter = LocalOllamaAdapter(gateway=gw, transport=FakeTransport(payload), enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "completed"
    assert turn.attempt.evidence.supported_count == 1
    assert turn.coverage.value == "complete"


def test_all_five_claim_types_in_one_turn(vault) -> None:
    """Handoff 151a §3 item 5: all 5 claim types, mixed support, in one completed local
    turn -- 2 source-backed (fact + inference), 1 model_knowledge, 1 unknown,
    1 assumption -- yields real PARTIAL coverage (never COMPLETE while any gap claim is
    present, never NONE while at least one claim is genuinely supported)."""
    app = ConversationApplication()
    session, snap, gw = _prepared_and_approved(app, vault)
    assert len(snap.items) >= 2, "fixture vault must have at least 2 distinct items"
    fact_item = snap.items[0]
    premises = snap.items[:2]
    inference_text = " and ".join(item.excerpt for item in premises)
    claims = [
        _fact_claim(fact_item),
        (inference_text, "inference", [item.item_id for item in premises]),
        ("something the model knows but the sources don't state", "model_knowledge", []),
        ("cannot answer this part of the question", "unknown", []),
        ("assuming you meant the AI Operating System project", "assumption", []),
    ]
    payload = _claims_payload(claims, limitations=["not fully covered"])
    adapter = LocalOllamaAdapter(gateway=gw, transport=FakeTransport(payload), enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "completed"
    ev = turn.attempt.evidence
    assert ev is not None
    assert ev.supported_count == 2
    assert ev.model_knowledge_count == 1
    assert ev.unknown_count == 1
    assert turn.coverage.value == "partial"
    assert ev.conflicts == ()
    pres = present(turn)
    assert len(pres.claims) == 5
    assert {c["evidence_type"] for c in pres.claims} == {
        "fact", "inference", "model_knowledge", "unknown", "assumption",
    }


def test_model_declared_limitations_are_validated_but_not_blindly_trusted_into_output(
    vault,
) -> None:
    """Handoff 151 §3 item 4 ("retain existing limitation/coverage semantics"): the closed
    schema's own top-level ``limitations`` field is validated for shape/hostile content by
    the LOCAL boundary (``validate_local_response``) but is never merged into the rendered,
    trusted ``AnswerEvidence.limitations`` -- that stays exclusively
    ``evidence.validate_response``'s own deterministic, system-computed limitations, the
    same as remote/mock. A model asserting an arbitrary free-text "limitation" cannot use
    this field to inject untrusted content into the trusted output surface."""
    app = ConversationApplication()
    session, _snap, gw = _prepared_and_approved(app, vault)
    payload = _claims_payload(
        [("something the model knows", "model_knowledge", [])],
        limitations=["the model's own untrusted claim about its limitations"],
    )
    adapter = LocalOllamaAdapter(gateway=gw, transport=FakeTransport(payload), enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "completed"
    ev = turn.attempt.evidence
    assert ev is not None
    assert "the model's own untrusted claim about its limitations" not in ev.limitations
    assert turn.coverage.value == "incomplete"


def test_local_completion_never_carries_conflicts(vault) -> None:
    """``AnswerEvidence.conflicts`` is never populated by ``evidence.validate_response``
    (Handoff R6/C19's conflict taxonomy is not yet implemented for any profile) -- proven
    empty for local too now that a completed local attempt carries real ``evidence``."""
    app = ConversationApplication()
    session, snap, gw = _prepared_and_approved(app, vault)
    cited_item = snap.items[0]
    payload = _claims_payload([_fact_claim(cited_item)])
    adapter = LocalOllamaAdapter(gateway=gw, transport=FakeTransport(payload), enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "completed"
    assert turn.attempt.evidence is not None
    assert turn.attempt.evidence.conflicts == ()
    pres = present(turn)
    assert pres.to_dict()["attempt"]["claims"]  # claims are populated for local now, not []


def test_session_history_records_the_local_answer_text(vault) -> None:
    app = ConversationApplication()
    session, snap, gw = _prepared_and_approved(app, vault)
    cited_item = snap.items[0]
    payload = _claims_payload([_fact_claim(cited_item)])
    adapter = LocalOllamaAdapter(gateway=gw, transport=FakeTransport(payload), enabled=True)

    app.dispatch_turn(session, adapter, now=T)

    assert len(session.turns) == 1
    assert cited_item.item_id in session.turns[0].answer_text


# ------------------------------------------------------------------ diagnostics wiring
def test_allowed_citation_ids_are_wired_from_the_current_snapshot_items(vault) -> None:
    app = ConversationApplication()
    session, snap, gw = _prepared_and_approved(app, vault)
    real_ids = {item.item_id for item in snap.items}
    transport = FakeTransport(_claims_payload([("x", "unknown", [])]))
    adapter = LocalOllamaAdapter(gateway=gw, transport=transport, enabled=True)

    app.dispatch_turn(session, adapter, now=T)

    assert len(transport.calls) == 1
    # The adapter never puts diagnostics on the wire; assert indirectly via a citation
    # from every real item id being accepted (proven by a separate completed-turn test)
    # and a fake id being rejected (below) -- this test checks the transport body itself
    # never carries the id allowlist (it must not leak onto the wire).
    sent_body = json.loads(transport.calls[0].body.decode("utf-8"))
    assert "allowed_citation_ids" not in sent_body
    assert "allowed_citation_ids" not in sent_body.get("options", {})
    assert real_ids  # sanity: the fixture vault actually produced items


def test_request_envelope_carries_exact_model_stream_num_ctx_and_num_predict(vault) -> None:
    """Handoff 150 sec 3 (PT37-CTO-02): the outgoing request is the exact non-streaming
    Ollama envelope -- not the bare ``{"prompt", "num_predict"}`` body the prior
    implementation sent, which never proved the provider was running the pinned
    model or context window."""
    app = ConversationApplication()
    session, _snap, gw = _prepared_and_approved(app, vault)
    transport = FakeTransport(_claims_payload([("x", "unknown", [])]))
    adapter = LocalOllamaAdapter(gateway=gw, transport=transport, enabled=True)

    app.dispatch_turn(session, adapter, now=T)

    sent = json.loads(transport.calls[0].body.decode("utf-8"))
    assert set(sent.keys()) == {"model", "prompt", "stream", "options"}
    assert sent["model"] == "qwen2.5:7b"
    assert sent["stream"] is False
    assert set(sent["options"].keys()) == {"num_ctx", "num_predict"}
    assert sent["options"]["num_ctx"] == LOCAL_LIMITS.provider_num_ctx == 4352
    # num_predict is the class Core actually selected for this exact prompt size
    # (``select_warm_class``) -- LOCAL-S (128) for this short fixture prompt.
    assert sent["options"]["num_predict"] in (128, 256)


def test_a_citation_id_outside_the_current_snapshot_is_rejected_as_fake(vault) -> None:
    app = ConversationApplication()
    session, _snap, gw = _prepared_and_approved(app, vault)
    payload = _claims_payload([("x [ZZZ]", "fact", ["ZZZ-not-real"])])
    adapter = LocalOllamaAdapter(gateway=gw, transport=FakeTransport(payload), enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "blocked"
    assert turn.attempt.failure.value == "blocked_local_unsafe_output"


# ------------------------------------------------------------------ Handoff 150 sec 3
# (PT37-CTO-02): exact Ollama envelope contract -- model/stream/num_ctx/num_predict sent, returned
# model/prompt_eval_count/eval_count/done_reason verified before any content is trusted.
def test_envelope_eval_count_exactly_at_num_predict_limit_is_accepted(vault) -> None:
    app = ConversationApplication()
    session, _snap, gw = _prepared_and_approved(app, vault)
    payload = _claims_payload([("at the boundary", "unknown", [])])
    # LOCAL-S's num_predict is 128 for this short fixture prompt (see the envelope test
    # above); pin the boundary value directly rather than re-deriving the warm class here.
    transport = FakeTransport(payload, eval_count_override=128)
    adapter = LocalOllamaAdapter(gateway=gw, transport=transport, enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "completed"
    assert gw.state is LocalReadinessState.READY


def test_envelope_eval_count_one_above_num_predict_limit_is_blocked_and_not_ready(vault) -> None:
    app = ConversationApplication()
    session, _snap, gw = _prepared_and_approved(app, vault)
    payload = _claims_payload([("over the boundary", "unknown", [])])
    transport = FakeTransport(payload, eval_count_override=129)
    adapter = LocalOllamaAdapter(gateway=gw, transport=transport, enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "blocked"
    assert turn.attempt.failure.value == "blocked_local_output_contract"
    assert turn.attempt.text is None
    # Handoff 150 sec 3: any envelope mismatch discards raw content and falls the
    # gateway back to not_ready.
    assert gw.state is LocalReadinessState.NOT_READY


def test_envelope_wrong_model_identity_is_blocked_and_not_ready(vault) -> None:
    app = ConversationApplication()
    session, _snap, gw = _prepared_and_approved(app, vault)
    payload = _claims_payload([("wrong model", "unknown", [])])
    transport = FakeTransport(payload, model_override="llama3:8b")
    adapter = LocalOllamaAdapter(gateway=gw, transport=transport, enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "blocked"
    assert turn.attempt.failure.value == "blocked_local_output_contract"
    assert turn.attempt.text is None
    assert gw.state is LocalReadinessState.NOT_READY
    # the wrong model identity is never carried in the safe details surface
    assert "llama3" not in json.dumps(turn.attempt.details)


def test_envelope_wrong_done_reason_is_blocked_and_not_ready(vault) -> None:
    app = ConversationApplication()
    session, _snap, gw = _prepared_and_approved(app, vault)
    payload = _claims_payload([("truncated", "unknown", [])])
    transport = FakeTransport(payload, done_reason_override="length")
    adapter = LocalOllamaAdapter(gateway=gw, transport=transport, enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "blocked"
    assert turn.attempt.failure.value == "blocked_local_output_contract"
    assert turn.attempt.text is None
    assert gw.state is LocalReadinessState.NOT_READY


def test_envelope_prompt_eval_count_mismatch_is_blocked_and_not_ready(vault) -> None:
    app = ConversationApplication()
    session, _snap, gw = _prepared_and_approved(app, vault)
    payload = _claims_payload([("provider miscounted", "unknown", [])])
    transport = FakeTransport(payload, prompt_eval_count_override=1)
    adapter = LocalOllamaAdapter(gateway=gw, transport=transport, enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "blocked"
    assert turn.attempt.failure.value == "blocked_local_output_contract"
    assert turn.attempt.text is None
    assert gw.state is LocalReadinessState.NOT_READY


def test_envelope_not_done_is_blocked_and_not_ready(vault) -> None:
    app = ConversationApplication()
    session, _snap, gw = _prepared_and_approved(app, vault)
    payload = _claims_payload([("still streaming?", "unknown", [])])
    transport = FakeTransport(payload, done_override=False)
    adapter = LocalOllamaAdapter(gateway=gw, transport=transport, enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "blocked"
    assert turn.attempt.failure.value == "blocked_local_output_contract"
    assert gw.state is LocalReadinessState.NOT_READY


def test_envelope_known_extra_field_is_accepted(vault) -> None:
    app = ConversationApplication()
    session, _snap, gw = _prepared_and_approved(app, vault)
    payload = _claims_payload([("extra field smuggled in", "unknown", [])])
    transport = FakeTransport(
        payload, extra_envelope_fields={"total_duration": 12345}
    )
    adapter = LocalOllamaAdapter(gateway=gw, transport=transport, enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    # total_duration is an ALLOWED envelope key (it is a real Ollama field) -- this
    # confirms the allowlist accepts it rather than rejecting every unexpected key.
    assert turn.attempt.status.value == "completed"


def test_envelope_truly_unknown_field_is_blocked_and_not_ready(vault) -> None:
    app = ConversationApplication()
    session, _snap, gw = _prepared_and_approved(app, vault)
    payload = _claims_payload([("extra field smuggled in", "unknown", [])])
    transport = FakeTransport(
        payload, extra_envelope_fields={"debug_raw_model_stderr": "should never be accepted"}
    )
    adapter = LocalOllamaAdapter(gateway=gw, transport=transport, enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "blocked"
    assert turn.attempt.failure.value == "blocked_local_output_contract"
    assert gw.state is LocalReadinessState.NOT_READY
    assert "debug_raw_model_stderr" not in json.dumps(turn.attempt.details)
    assert turn.attempt.details == {"reason": "envelope_unknown_fields", "count": 1}


def test_envelope_non_json_body_is_blocked_and_not_ready(vault) -> None:
    app = ConversationApplication()
    session, _snap, gw = _prepared_and_approved(app, vault)
    transport = FakeTransport(raw_envelope_bytes=b"not json at all")
    adapter = LocalOllamaAdapter(gateway=gw, transport=transport, enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "blocked"
    assert turn.attempt.failure.value == "blocked_local_output_contract"
    assert gw.state is LocalReadinessState.NOT_READY


# ------------------------------------------------------------ zero-provider-request-on-rejection
def test_zero_provider_calls_when_gateway_is_cold(vault) -> None:
    notes, root = vault
    app = ConversationApplication()
    session = app.create_session("local")
    cold_gateway = LocalReadinessGateway(
        capacity_probe=SyntheticCapacityProbe(), clock=SyntheticClock()
    )
    with pytest.raises(LocalNotReadyError):
        app.prepare_turn(
            session, _request(session.session_id, root), notes, local_gateway=cold_gateway
        )
    # prepare_turn raised before any adapter/transport was ever constructed or reachable --
    # there is nothing to assert on a transport because dispatch_turn was never reached.
    assert session.pending_prepared is None


def test_zero_transport_calls_on_prompt_assembly_context_limit_rejection(vault) -> None:
    huge_text = "word " * 5000  # far over both the local byte and token ceilings
    app = ConversationApplication()
    session, _snap, gw = _prepared_and_approved(app, vault, text=huge_text)
    adapter = LocalOllamaAdapter(gateway=gw, transport=ExplodingTransport(), enabled=True)

    with pytest.raises(LocalContextLimitError):
        app.dispatch_turn(session, adapter, now=T)  # ExplodingTransport asserts if reached


def test_zero_transport_calls_when_adapter_disabled(vault) -> None:
    app = ConversationApplication()
    session, _snap, gw = _prepared_and_approved(app, vault)
    adapter = LocalOllamaAdapter(gateway=gw, transport=ExplodingTransport(), enabled=False)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "blocked"
    assert turn.attempt.failure.value == "blocked_local_unavailable"
    assert turn.attempt.details.get("reason") == "adapter_disabled"


def test_zero_transport_calls_when_in_flight(vault) -> None:
    app = ConversationApplication()
    session, _snap, gw = _prepared_and_approved(app, vault)
    gw.begin_attempt()  # simulate another attempt already occupying the single in-flight slot
    adapter = LocalOllamaAdapter(gateway=gw, transport=ExplodingTransport(), enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "blocked"
    assert turn.attempt.failure.value == "blocked_local_not_ready"
    assert turn.attempt.details.get("reason") == "in_flight"


def test_zero_transport_calls_when_capacity_insufficient_at_dispatch(vault) -> None:
    app = ConversationApplication()
    session, _snap, gw = _prepared_and_approved(app, vault)
    # The 6 pushed OK samples were already consumed by prepare_turn's own admission check
    # (3) -- exactly 3 remain for the adapter's immediate pre-dispatch re-check (147b sec
    # 3.1). Replace the queue with an insufficient sample so THAT re-check blocks.
    low_mem = MemoryObservation(avail_phys_bytes=1024, memory_load_percent=10)
    gw._capacity_probe._queue.clear()
    gw._capacity_probe.push(low_mem)
    adapter = LocalOllamaAdapter(gateway=gw, transport=ExplodingTransport(), enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "blocked"
    assert turn.attempt.failure.value == "blocked_local_capacity"


# -------------------------------------------------------- hostile-content / raw-payload non-leakage
def test_hostile_output_blocks_without_recording_a_turn_or_leaking_raw_text(vault) -> None:
    app = ConversationApplication()
    session, _snap, gw = _prepared_and_approved(app, vault)
    hostile_marker = "javascript:alert(document.cookie)"
    payload = _claims_payload([(f"click {hostile_marker}", "unknown", [])])
    adapter = LocalOllamaAdapter(gateway=gw, transport=FakeTransport(payload), enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "blocked"
    assert turn.attempt.failure.value == "blocked_local_unsafe_output"
    assert turn.attempt.text is None
    # No turn is ever recorded into session history for a non-completed attempt.
    assert session.turns == []
    # details only ever carries the fixed safe fields (reason/field/index) -- never the
    # hostile substring or any other raw provider text.
    assert hostile_marker not in json.dumps(turn.attempt.details)
    # "javascript:" matches the script/markup pattern before the separate uri_scheme
    # pattern is even reached (_HOSTILE_PATTERNS is checked in a fixed order).
    assert turn.attempt.details.get("reason") == "script_or_markup"
    assert turn.attempt.details.get("field") == "claims[0].text"
    # And the redacted, allowlisted trace never carries it either.
    trace_dump = json.dumps(session.trace.to_dict())
    assert hostile_marker not in trace_dump


def test_hostile_unknown_top_level_key_name_never_leaks_across_any_public_surface(vault) -> None:
    """PT37-CTO-05 canary: an adversarial/malformed local response smuggling a hostile
    string AS a JSON key name (not a value) must never appear in AttemptResult.to_dict(),
    the trace, or the presentation surface -- only a safe count crosses the boundary."""
    app = ConversationApplication()
    session, _snap, gw = _prepared_and_approved(app, vault)
    hostile_key = "AKIAABCDEFGHIJKLMNOP-<script>evil()</script>-../../etc/passwd"
    payload = {
        "claims": [{"text": "x", "type": "unknown", "evidence": []}],
        "limitations": [],
        hostile_key: "nope",
    }
    adapter = LocalOllamaAdapter(gateway=gw, transport=FakeTransport(payload), enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "blocked"
    assert turn.attempt.failure.value == "blocked_local_output_contract"
    assert turn.attempt.details.get("reason") == "unknown_fields"
    assert turn.attempt.details.get("count") == 1
    assert "fields" not in turn.attempt.details
    assert hostile_key not in json.dumps(turn.attempt.to_dict())
    assert hostile_key not in json.dumps(present(turn).to_dict())
    trace_dump = json.dumps(session.trace.to_dict())
    assert hostile_key not in trace_dump
    assert session.turns == []


def test_hostile_per_claim_unknown_key_name_never_leaks_across_any_public_surface(vault) -> None:
    """PT37-CTO-05 canary: same as above at the per-claim boundary -- only a count and the
    Core-computed numeric claim index may cross the boundary, never the untrusted key name."""
    app = ConversationApplication()
    session, _snap, gw = _prepared_and_approved(app, vault)
    hostile_key = "sk-abcdefghijklmnopqrstuvwx-<script>evil()</script>"
    claim = {"text": "x", "type": "unknown", "evidence": [], hostile_key: "nope"}
    payload = {"claims": [claim], "limitations": []}
    adapter = LocalOllamaAdapter(gateway=gw, transport=FakeTransport(payload), enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "blocked"
    assert turn.attempt.failure.value == "blocked_local_output_contract"
    assert turn.attempt.details.get("reason") == "claim_unknown_fields"
    assert turn.attempt.details.get("index") == 0
    assert turn.attempt.details.get("count") == 1
    assert "fields" not in turn.attempt.details
    assert hostile_key not in json.dumps(turn.attempt.to_dict())
    assert hostile_key not in json.dumps(present(turn).to_dict())
    trace_dump = json.dumps(session.trace.to_dict())
    assert hostile_key not in trace_dump
    assert session.turns == []


def test_raw_wire_response_bytes_never_appear_verbatim_in_the_presentation(vault) -> None:
    app = ConversationApplication()
    session, snap, gw = _prepared_and_approved(app, vault)
    cited_item = snap.items[0]
    # The raw wire *inner* payload has different key order/whitespace than the canonical
    # decode; assert the PresentationResult never contains that literal raw string, only
    # the parsed+validated+re-canonicalized claims. It must still be wrapped in a
    # well-formed envelope (Handoff 150 sec 3) -- the envelope's ``response`` field
    # carries the raw wire string itself so we control its exact bytes independent of
    # ``FakeTransport``'s canonical echo.
    raw_wire_inner = (
        '{"limitations": [], "claims": [{"evidence": ["'
        + cited_item.item_id
        + '"], "type": "fact", "text": '
        + json.dumps(cited_item.excerpt)
        + "}]}"
    )
    transport = FakeTransport(_claims_payload([_fact_claim(cited_item)]))

    def _sniff(request, cancel=None):
        transport.calls.append(request)
        sent = json.loads(request.body.decode("utf-8"))
        real_prompt_tokens = SyntheticTokenCounter().count(sent["prompt"])
        envelope = {
            "model": sent["model"],
            "response": raw_wire_inner,
            "done": True,
            "done_reason": "stop",
            "prompt_eval_count": real_prompt_tokens,
            "eval_count": 1,
        }
        return TransportResponse(
            200, {"content-type": "application/json"}, canonical_json(envelope).encode("utf-8")
        )

    transport.send = _sniff  # type: ignore[method-assign]
    adapter = LocalOllamaAdapter(gateway=gw, transport=transport, enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)
    pres = present(turn)

    assert turn.attempt.status.value == "completed"
    rendered = json.dumps(pres.to_dict())
    assert raw_wire_inner not in rendered
    assert cited_item.item_id in rendered  # the validated content itself is legitimately present


def test_trace_events_carry_only_allowlisted_fields_for_local_lifecycle(vault) -> None:
    app = ConversationApplication()
    session, _snap, gw = _prepared_and_approved(app, vault)
    payload = _claims_payload([("ok", "unknown", [])])
    adapter = LocalOllamaAdapter(gateway=gw, transport=FakeTransport(payload), enabled=True)
    app.dispatch_turn(session, adapter, now=T)

    names = [e.name for e in session.trace.events]
    assert "local_admission_checked" in names
    assert "prompt_assembled" in names
    assert "dispatch_started" in names
    assert "dispatch_completed" in names
    assert "evidence_validated" in names
    admission_event = next(e for e in session.trace.events if e.name == "local_admission_checked")
    assert set(admission_event.fields.keys()) <= {
        "session_id", "request_id", "destination_profile_id", "local_state",
    }


# ------------------------------------------------------------------ cancellation
def test_cancelled_before_transport_call_makes_zero_provider_requests(vault) -> None:
    from jarvis_core.providers.conversation import CancellationToken

    app = ConversationApplication()
    session, _snap, gw = _prepared_and_approved(app, vault)
    cancel = CancellationToken()
    cancel.cancel()
    adapter = LocalOllamaAdapter(gateway=gw, transport=ExplodingTransport(), enabled=True)

    turn = app.dispatch_turn(session, adapter, cancel=cancel, now=T)

    assert turn.attempt.status.value == "cancelled"
