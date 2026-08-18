"""V05-PT-37: end-to-end application-layer behavior for the local profile -- completed-turn
round trip, presentation surface, raw-payload/hostile-content non-leakage across every public
surface (trace, session history, attempt details), zero-provider-request-on-rejection proofs,
and (Handoff 150 sec 3, PT37-CTO-02 correction) the exact non-streaming Ollama request/response
envelope contract -- exact model identity, ``stream=false``, ``num_ctx``, class-specific
``num_predict`` sent; returned model/``prompt_eval_count``/``eval_count``/``done_reason``
verified before any content is trusted (Handoff 148 sec 4 required verification). Fakes/
synthetic fixtures only; the ``LocalOllamaAdapter`` here is always constructed with a
``FakeTransport`` -- no real loopback endpoint, no live Ollama, no network (Handoff 148 sec 3).
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


class FakeTransport:
    """Records every request it receives; never touches a socket.

    Handoff 150 sec 3 (PT37-CTO-02): the adapter now sends a full Ollama
    non-streaming request envelope (exact model, ``stream=false``, ``num_ctx``,
    class-specific ``num_predict``) and expects a full completion envelope back
    (returned model, ``prompt_eval_count``, ``eval_count``, ``done_reason``,
    ``response``). By default this fake ECHOES a well-formed envelope derived
    from the EXACT incoming request (model and the real synthetic-counted prompt
    tokens), wrapping ``response_payload`` (the local closed-schema
    answer/limitations/citations dict) as the ``response`` string -- so a normal
    test describes only its INTENT, not a hand-computed token count. Any
    ``*_override`` keyword replaces exactly one envelope field, which is how the
    adversarial envelope-mismatch tests below target one exact violation at a
    time. ``raw_envelope_bytes`` bypasses all of this and returns the given bytes
    verbatim (for malformed/non-JSON/wrong-shape envelope tests).
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
            else {"answer": "", "limitations": [], "citations": []}
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
    cited_id = snap.items[0].item_id
    payload = {"answer": f"Backed by {cited_id}.", "limitations": [], "citations": [cited_id]}
    transport = FakeTransport(payload)
    adapter = LocalOllamaAdapter(gateway=gw, transport=transport, enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "completed"
    assert turn.attempt.failure is None
    assert turn.attempt.text == f"Backed by {cited_id}."
    assert turn.attempt.local_citations == (cited_id,)
    assert turn.attempt.local_limitations == ()
    # Handoff 150 §4 (PT37-CTO-03): a valid, current citation no longer manufactures
    # COMPLETE coverage — the closed local schema cannot express real per-claim support,
    # so every completed local turn is unconditionally NONE until a contract amendment.
    assert turn.coverage.value == "none"
    assert len(transport.calls) == 1


def test_presentation_surfaces_the_local_answer_directly_with_no_claims(vault) -> None:
    app = ConversationApplication()
    session, snap, gw = _prepared_and_approved(app, vault)
    cited_id = snap.items[0].item_id
    payload = {
        "answer": f"See {cited_id}.",
        "limitations": ["partial coverage"],
        "citations": [cited_id],
    }
    adapter = LocalOllamaAdapter(gateway=gw, transport=FakeTransport(payload), enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)
    pres = present(turn)

    assert pres.answer == f"See {cited_id}."
    assert pres.claims == ()  # the remote/mock claims taxonomy never applies to local
    assert pres.citations == (cited_id,)
    assert pres.limitations == ("partial coverage",)
    assert pres.status == "completed"
    # Handoff 150 §4 (PT37-CTO-03): citations/limitations no longer drive coverage at all.
    assert pres.coverage == "none"

    rendered = pres.to_dict()
    assert rendered["attempt"]["answer"] == f"See {cited_id}."
    assert rendered["attempt"]["claims"] == []
    text = pres.to_text()
    assert f"See {cited_id}." in text


@pytest.mark.parametrize(
    ("citations", "limitations"),
    [
        (("C1",), ()),
        (("C1",), ("gap",)),
        ((), ("gap",)),
        ((), ()),
    ],
)
def test_local_coverage_is_unconditionally_none(vault, citations, limitations) -> None:
    """Handoff 150 §4 (PT37-CTO-03) correction: the prior mapping inferred COMPLETE/
    PARTIAL/INCOMPLETE from citation-ID presence and model-declared limitations alone —
    exactly the inference the CTO review prohibits ("do not infer support or coverage
    from citation-ID presence or model-declared limitations"). No combination of
    citations/limitations can produce anything but NONE now; the closed local schema
    cannot express real per-claim support, so coverage stays NONE pending a contract
    amendment (see ``_local_coverage``'s docstring)."""
    app = ConversationApplication()
    session, snap, gw = _prepared_and_approved(app, vault)
    # Use only ids that are actually in the current snapshot when non-empty.
    real_citations = tuple(snap.items[0].item_id for _ in citations)
    payload = {
        "answer": "some answer text",
        "limitations": list(limitations),
        "citations": list(real_citations),
    }
    adapter = LocalOllamaAdapter(gateway=gw, transport=FakeTransport(payload), enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "completed"
    assert turn.coverage.value == "none"


# ------------------------------------------------------------------ PT37-CTO-03: citation
# binding -- Handoff 150 sec 4 requires local citations to enter the same current-byte
# validation semantics as the remote/mock contract and prohibits inferring support or
# coverage from citation-ID presence or model-declared limitations. Per-claim decomposition
# and typed support (fact/inference exact-match) are inapplicable -- the closed local schema
# has no per-claim structure at all (see ``_local_coverage``'s docstring); the tests below
# cover every adversarial category Handoff 150 sec 4 names that the closed schema CAN
# express: unrelated valid IDs, current-byte drift, removed items, and mixed valid/drifted
# citations. "conflicts" is structurally inapplicable to local (``AnswerEvidence.conflicts``
# only exists on the remote/mock evidence path; a completed local attempt's ``evidence`` is
# always ``None``) and is proven empty below rather than silently unaddressed.


def test_a_valid_but_content_unrelated_citation_still_yields_none_coverage(vault) -> None:
    """The exact PT37-CTO-03 hostile scenario: a citation that is genuinely current and
    genuinely in the snapshot, but has nothing to do with the answer's content, must not
    manufacture elevated coverage. Coverage is unconditionally NONE for every completed
    local turn now, so this citation cannot reach COMPLETE regardless of relatedness."""
    app = ConversationApplication()
    session, snap, gw = _prepared_and_approved(app, vault)
    unrelated_id = snap.items[-1].item_id
    payload = {
        "answer": "The sky is blue and bourbon pairs well with barbecue.",
        "limitations": [],
        "citations": [unrelated_id],
    }
    adapter = LocalOllamaAdapter(gateway=gw, transport=FakeTransport(payload), enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "completed"
    assert turn.coverage.value == "none"


class _DriftMidFlightTransport:
    """Wraps a ``FakeTransport`` and runs ``mutate()`` exactly once, the first time
    ``send()`` is called -- i.e. AFTER step 8's pre-dispatch ``_revalidate_current_bytes``
    has already passed (it runs before ``provider.dispatch()``/the transport call) but
    BEFORE the local model's (simulated) reply is interpreted. This is the precise mid-
    flight race window ``_revalidate_local_citations`` exists to close: pre-dispatch
    revalidation cannot see a mutation that happens while the model is generating."""

    def __init__(self, inner: FakeTransport, mutate) -> None:
        self._inner = inner
        self._mutate = mutate
        self.calls = inner.calls

    def send(self, request, cancel=None):
        self._mutate()
        return self._inner.send(request, cancel)


def test_current_byte_drift_on_a_cited_source_fails_the_attempt_closed(tmp_path: Path) -> None:
    """Handoff 150 sec 4 (PT37-CTO-03): a cited source edited AFTER pre-dispatch
    revalidation passed -- while the (potentially slow) local model call is in flight --
    must not reach COMPLETED. Pre-dispatch revalidation (step 8 /
    ``_revalidate_current_bytes``) cannot see a drift that happens WHILE the model is
    generating; ``_revalidate_local_citations`` (added this correction) closes that exact
    window at interpretation time."""
    app = ConversationApplication()
    notes, root = _tmp_vault(tmp_path)
    session = app.create_session("local")
    gw = _ready_gateway()
    snap = app.prepare_turn(session, _request(session.session_id, root), notes, local_gateway=gw)
    app.approve(session, actor="jason", now=T)
    cited_id = snap.items[0].item_id
    target = root / snap.items[0].relpath

    def _drift() -> None:
        target.write_bytes(target.read_bytes() + b"\n\ndrift after snapshot, before local reply\n")

    payload = {"answer": f"Backed by {cited_id}.", "limitations": [], "citations": [cited_id]}
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
    """Handoff 150 sec 4 (PT37-CTO-03): a cited source deleted from disk while the local
    model call is in flight (e.g. a concurrent vault edit) must fail the attempt closed,
    the same as a byte-level drift -- ``CurrentSourceResolver`` returns empty bytes for a
    missing file (fail-closed by design), which then fails locator/fingerprint validation
    exactly like a drifted file."""
    app = ConversationApplication()
    notes, root = _tmp_vault(tmp_path)
    session = app.create_session("local")
    gw = _ready_gateway()
    snap = app.prepare_turn(session, _request(session.session_id, root), notes, local_gateway=gw)
    app.approve(session, actor="jason", now=T)
    cited_id = snap.items[0].item_id
    target = root / snap.items[0].relpath

    payload = {"answer": f"Backed by {cited_id}.", "limitations": [], "citations": [cited_id]}
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
    """Handoff 150 sec 4 (PT37-CTO-03) "mixed supported/unsupported" analog for the closed
    local schema: the closed schema has no per-claim decomposition, so there is no per-claim
    partial-credit outcome to test (see ``_local_coverage``'s docstring) -- but a citation
    LIST mixing a still-current item with a mid-flight-drifted one is expressible, and must
    fail the entire attempt closed rather than silently accepting the still-current one."""
    app = ConversationApplication()
    notes, root = _tmp_vault(tmp_path)
    session = app.create_session("local")
    gw = _ready_gateway()
    snap = app.prepare_turn(session, _request(session.session_id, root), notes, local_gateway=gw)
    app.approve(session, actor="jason", now=T)
    assert len(snap.items) >= 2, "fixture vault must have at least 2 distinct items"
    still_current_id = snap.items[0].item_id
    drifted_id = snap.items[1].item_id
    target = root / snap.items[1].relpath

    def _drift() -> None:
        target.write_bytes(target.read_bytes() + b"\n\ndrift after snapshot\n")

    payload = {
        "answer": f"Backed by {still_current_id} and {drifted_id}.",
        "limitations": [],
        "citations": [still_current_id, drifted_id],
    }
    transport = _DriftMidFlightTransport(FakeTransport(payload), _drift)
    adapter = LocalOllamaAdapter(gateway=gw, transport=transport, enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "failed"
    assert turn.attempt.failure.value == "evidence_failed"
    assert len(session.turns) == 0


def test_local_completion_never_carries_conflicts(vault) -> None:
    """Handoff 150 sec 4 names "conflicts" in its required adversarial coverage. It is
    structurally inapplicable to local: ``AnswerEvidence.conflicts`` only exists on the
    remote/mock evidence path, and a completed local attempt's ``evidence`` is always
    ``None`` (see the ``_interpret`` local branch). Proven empty here rather than left
    silently unaddressed."""
    app = ConversationApplication()
    session, snap, gw = _prepared_and_approved(app, vault)
    cited_id = snap.items[0].item_id
    payload = {"answer": f"Backed by {cited_id}.", "limitations": [], "citations": [cited_id]}
    adapter = LocalOllamaAdapter(gateway=gw, transport=FakeTransport(payload), enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "completed"
    assert turn.attempt.evidence is None
    pres = present(turn)
    assert pres.to_dict()["attempt"].get("claims") == []


def test_session_history_records_the_local_answer_text(vault) -> None:
    app = ConversationApplication()
    session, snap, gw = _prepared_and_approved(app, vault)
    cited_id = snap.items[0].item_id
    payload = {"answer": "recorded answer", "limitations": [], "citations": [cited_id]}
    adapter = LocalOllamaAdapter(gateway=gw, transport=FakeTransport(payload), enabled=True)

    app.dispatch_turn(session, adapter, now=T)

    assert len(session.turns) == 1
    assert session.turns[0].answer_text == "recorded answer"


# ------------------------------------------------------------------ diagnostics wiring
def test_allowed_citation_ids_are_wired_from_the_current_snapshot_items(vault) -> None:
    app = ConversationApplication()
    session, snap, gw = _prepared_and_approved(app, vault)
    real_ids = {item.item_id for item in snap.items}
    transport = FakeTransport({"answer": "x", "limitations": [], "citations": []})
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
    transport = FakeTransport({"answer": "x", "limitations": [], "citations": []})
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
    payload = {"answer": "x [ZZZ]", "limitations": [], "citations": ["ZZZ-not-real"]}
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
    payload = {"answer": "at the boundary", "limitations": [], "citations": []}
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
    payload = {"answer": "over the boundary", "limitations": [], "citations": []}
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
    payload = {"answer": "wrong model", "limitations": [], "citations": []}
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
    payload = {"answer": "truncated", "limitations": [], "citations": []}
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
    payload = {"answer": "provider miscounted", "limitations": [], "citations": []}
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
    payload = {"answer": "still streaming?", "limitations": [], "citations": []}
    transport = FakeTransport(payload, done_override=False)
    adapter = LocalOllamaAdapter(gateway=gw, transport=transport, enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "blocked"
    assert turn.attempt.failure.value == "blocked_local_output_contract"
    assert gw.state is LocalReadinessState.NOT_READY


def test_envelope_known_extra_field_is_accepted(vault) -> None:
    app = ConversationApplication()
    session, _snap, gw = _prepared_and_approved(app, vault)
    payload = {"answer": "extra field smuggled in", "limitations": [], "citations": []}
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
    payload = {"answer": "extra field smuggled in", "limitations": [], "citations": []}
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
    payload = {"answer": f"click {hostile_marker}", "limitations": [], "citations": []}
    adapter = LocalOllamaAdapter(gateway=gw, transport=FakeTransport(payload), enabled=True)

    turn = app.dispatch_turn(session, adapter, now=T)

    assert turn.attempt.status.value == "blocked"
    assert turn.attempt.failure.value == "blocked_local_unsafe_output"
    assert turn.attempt.text is None
    # No turn is ever recorded into session history for a non-completed attempt.
    assert session.turns == []
    # details only ever carries the fixed safe fields (reason/field) -- never the hostile
    # substring or any other raw provider text.
    assert hostile_marker not in json.dumps(turn.attempt.details)
    # "javascript:" matches the script/markup pattern before the separate uri_scheme
    # pattern is even reached (_HOSTILE_PATTERNS is checked in a fixed order).
    assert turn.attempt.details.get("reason") == "script_or_markup"
    assert turn.attempt.details.get("field") == "answer"
    # And the redacted, allowlisted trace never carries it either.
    trace_dump = json.dumps(session.trace.to_dict())
    assert hostile_marker not in trace_dump


def test_raw_wire_response_bytes_never_appear_verbatim_in_the_presentation(vault) -> None:
    app = ConversationApplication()
    session, snap, gw = _prepared_and_approved(app, vault)
    cited_id = snap.items[0].item_id
    # The raw wire *inner* payload has different key order/whitespace than the canonical
    # decode; assert the PresentationResult never contains that literal raw string, only
    # the parsed+validated answer text. It must still be wrapped in a well-formed envelope
    # (Handoff 150 sec 3) -- the envelope's ``response`` field carries the raw wire string
    # itself so we control its exact bytes independent of ``FakeTransport``'s canonical
    # echo.
    raw_wire_inner = (
        f'{{"citations": ["{cited_id}"], "limitations": [], "answer": "final answer text"}}'
    )
    transport = FakeTransport(
        {"answer": "final answer text", "limitations": [], "citations": [cited_id]}
    )

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
    assert "final answer text" in rendered  # the validated content itself is legitimately present


def test_trace_events_carry_only_allowlisted_fields_for_local_lifecycle(vault) -> None:
    app = ConversationApplication()
    session, _snap, gw = _prepared_and_approved(app, vault)
    payload = {"answer": "ok", "limitations": [], "citations": []}
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
