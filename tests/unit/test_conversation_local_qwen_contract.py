"""V05-PT-37: frozen numeric contract, canonical-text rules, prompt template, and the
hostile-output/closed-schema validation boundary for the inactive
``local-sensitive-conversation/qwen25-7b-constrained-v1`` local profile (Handoff 147
sec 3-4, corrected by 147b sec 2.2-2.3). Every boundary is proven at/just-below/one-above
using fakes/synthetic fixtures only (Handoff 148 sec 3-4); no live Ollama, no network, no
model.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from jarvis_core.config import Config
from jarvis_core.conversation import context as ctx
from jarvis_core.conversation.contract import LocalContextLimitError, LocalPolicyDriftError
from jarvis_core.conversation.prompt import assemble_local_prompt
from jarvis_core.conversation.request import Budgets, LOCAL_LIMITS, LocalLimits, LocalWarmClass, local_qwen_profile
from jarvis_core.policy import local_allow_all
from jarvis_core.providers.local_ollama import (
    LOCAL_WARM_CLASS_SPECS,
    LocalClaim,
    LocalGatewayBlocked,
    LocalResponse,
    build_qwen_prompt,
    canonical_json,
    select_warm_class,
    validate_canonical_text,
    validate_local_response,
)
from jarvis_core.repositories import FileSystemKnowledgeRepository
from jarvis_core.conversation.request import PrepareTurnRequest

T = datetime(2026, 8, 1, tzinfo=timezone.utc)


@pytest.fixture(scope="module")
def vault() -> tuple[list, Path]:
    repo = FileSystemKnowledgeRepository(Config())
    return repo.discover(), Path(repo.root)


def _local_request(root: Path, *, text: str = "summarize the AI Operating System project") -> PrepareTurnRequest:
    return PrepareTurnRequest(
        request_id="req-contract-1",
        session_id="s-contract",
        workspace_id="local",
        scope=local_allow_all(workspace_id="local", max_sensitivity="internal"),
        source_root=root,
        user_text=text,
        provider_profile=local_qwen_profile(),
        budgets=Budgets(),
        evaluation_time=T,
        want_trace=False,
    )


@pytest.fixture(scope="module")
def base_snapshot(vault: tuple[list, Path]):
    notes, root = vault
    return ctx.prepare(_local_request(root), notes).snapshot


def _words(n: int) -> str:
    """``n`` single space-separated word tokens -> SyntheticTokenCounter.count == n."""
    return " ".join(f"w{i}" for i in range(n))


# ------------------------------------------------------------------ LocalLimits (147 sec 3, 147b sec 2.3)
def test_frozen_local_limits_match_the_spec() -> None:
    assert LOCAL_LIMITS == LocalLimits(
        prompt_tokens_max=4096,
        context_tokens_max=3072,
        user_text_tokens_max=512,
        user_text_bytes_max=4096,
        history_tokens_max=256,
        context_items_max=12,
        provider_num_ctx=4352,
        raw_response_bytes_max=16384,
        answer_bytes_max=8192,
        citations_max=12,
        in_flight_max_per_process=1,
        automatic_retry_max=0,
    )


def test_warm_class_specs_match_the_spec_corrected_by_147b() -> None:
    s = LOCAL_WARM_CLASS_SPECS[LocalWarmClass.LOCAL_S]
    m = LOCAL_WARM_CLASS_SPECS[LocalWarmClass.LOCAL_MAX]
    assert (s.prompt_tokens_max, s.num_predict, s.per_attempt_deadline_seconds) == (1024, 128, 35.0)
    assert (m.prompt_tokens_max, m.num_predict, m.per_attempt_deadline_seconds) == (4096, 256, 60.0)
    assert (s.warm_p50_seconds, s.warm_p95_seconds) == (10.0, 25.0)
    assert (m.warm_p50_seconds, m.warm_p95_seconds) == (20.0, 45.0)


@pytest.mark.parametrize(
    ("prompt_tokens", "expected"),
    [
        (1, LocalWarmClass.LOCAL_S),
        (1023, LocalWarmClass.LOCAL_S),
        (1024, LocalWarmClass.LOCAL_S),  # at the LOCAL-S boundary -> still LOCAL-S
        (1025, LocalWarmClass.LOCAL_MAX),  # one above -> LOCAL-MAX
        (4096, LocalWarmClass.LOCAL_MAX),  # at the LOCAL-MAX ceiling
    ],
)
def test_select_warm_class_boundary(prompt_tokens: int, expected: LocalWarmClass) -> None:
    assert select_warm_class(prompt_tokens) is expected


# ------------------------------------------------------------------ canonical text (147b sec 2.2)
def test_canonical_text_accepts_plain_nfc_lf_text() -> None:
    validate_canonical_text("hello\nworld", field_name="x")  # must not raise


def test_canonical_text_rejects_nul() -> None:
    with pytest.raises(LocalGatewayBlocked) as ei:
        validate_canonical_text("a\x00b", field_name="x")
    assert ei.value.code == "blocked_policy_drift"
    assert ei.value.details["reason"] == "nul_byte"


def test_canonical_text_rejects_cr() -> None:
    with pytest.raises(LocalGatewayBlocked) as ei:
        validate_canonical_text("a\r\nb", field_name="x")
    assert ei.value.details["reason"] == "cr_present"


def test_canonical_text_rejects_non_nfc() -> None:
    # "e" + combining acute (NFD) is not the NFC-composed form.
    nfd = "e\u0301"
    assert nfd != "\u00e9"
    with pytest.raises(LocalGatewayBlocked) as ei:
        validate_canonical_text(nfd, field_name="x")
    assert ei.value.details["reason"] == "non_nfc"


@pytest.mark.parametrize("token", ["<|im_start|>", "<|im_end|>"])
def test_canonical_text_rejects_reserved_role_tokens(token: str) -> None:
    with pytest.raises(LocalGatewayBlocked) as ei:
        validate_canonical_text(f"hello {token} world", field_name="x")
    assert ei.value.details["reason"] == "reserved_token"


# ------------------------------------------------------------------ prompt template (147b sec 2.2)
def test_build_qwen_prompt_is_the_exact_frozen_template() -> None:
    prompt = build_qwen_prompt(system_instruction="SYS", user_text="USR")
    assert prompt == (
        "<|im_start|>system\nSYS<|im_end|>\n"
        "<|im_start|>user\nUSR<|im_end|>\n"
        "<|im_start|>assistant\n"
    )


def test_canonical_json_is_sorted_compact_and_direct_unicode() -> None:
    out = canonical_json({"b": 1, "a": "caf\u00e9"})
    assert out == '{"a":"caf\u00e9","b":1}'
    assert "\\u00e9" not in out  # non-ASCII encoded directly, not \uXXXX-escaped
    assert " " not in out  # compact ","/":" separators


# ------------------------------------------------------------------ assemble_local_prompt boundaries
def test_user_text_bytes_boundary() -> None:
    # 4096 ASCII bytes (1 byte/char) is exactly at the limit and must pass; 4097 must not.
    limits = replace(LOCAL_LIMITS, user_text_tokens_max=10_000, prompt_tokens_max=100_000)
    ok_text = "a" * 4096
    over_text = "a" * 4097
    ok_snap = _snapshot_with_user_text(ok_text)
    over_snap = _snapshot_with_user_text(over_text)
    assemble_local_prompt(ok_snap, limits=limits)  # must not raise
    with pytest.raises(LocalContextLimitError) as ei:
        assemble_local_prompt(over_snap, limits=limits)
    assert ei.value.details["limit_name"] == "user_text_bytes"
    assert ei.value.details["actual"] == 4097


def test_user_text_tokens_boundary() -> None:
    limits = replace(LOCAL_LIMITS, user_text_bytes_max=1_000_000, prompt_tokens_max=100_000, user_text_tokens_max=5)
    ok_snap = _snapshot_with_user_text(_words(5))
    over_snap = _snapshot_with_user_text(_words(6))
    assemble_local_prompt(ok_snap, limits=limits)  # 5 tokens, at the limit -> passes
    with pytest.raises(LocalContextLimitError) as ei:
        assemble_local_prompt(over_snap, limits=limits)
    assert ei.value.details["limit_name"] == "user_text_tokens"
    assert ei.value.details["actual"] == 6


def test_context_items_boundary(base_snapshot) -> None:
    n = len(base_snapshot.items)
    assert n > 0, "the released fixture vault must produce at least one context item"
    limits_ok = replace(LOCAL_LIMITS, context_items_max=n, prompt_tokens_max=100_000, context_tokens_max=100_000)
    limits_over = replace(LOCAL_LIMITS, context_items_max=n - 1, prompt_tokens_max=100_000, context_tokens_max=100_000)
    assemble_local_prompt(base_snapshot, limits=limits_ok)  # must not raise
    with pytest.raises(LocalContextLimitError) as ei:
        assemble_local_prompt(base_snapshot, limits=limits_over)
    assert ei.value.details["limit_name"] == "context_items"
    assert ei.value.details["actual"] == n


def test_context_tokens_boundary(base_snapshot) -> None:
    # Measure the real counted context/prompt tokens once with a permissive ceiling, then
    # pin the boundary exactly at/one-below that measured value.
    permissive = replace(LOCAL_LIMITS, context_tokens_max=1_000_000, prompt_tokens_max=1_000_000)
    measured = assemble_local_prompt(base_snapshot, limits=permissive).budget_report
    actual = int(measured["context_tokens"])
    limits_ok = replace(LOCAL_LIMITS, context_tokens_max=actual, prompt_tokens_max=1_000_000)
    limits_over = replace(LOCAL_LIMITS, context_tokens_max=max(actual - 1, 0), prompt_tokens_max=1_000_000)
    assemble_local_prompt(base_snapshot, limits=limits_ok)  # must not raise
    with pytest.raises(LocalContextLimitError) as ei:
        assemble_local_prompt(base_snapshot, limits=limits_over)
    assert ei.value.details["limit_name"] == "context_tokens"


def test_prompt_tokens_boundary(base_snapshot) -> None:
    permissive = replace(LOCAL_LIMITS, context_tokens_max=1_000_000, prompt_tokens_max=1_000_000)
    measured = assemble_local_prompt(base_snapshot, limits=permissive).budget_report
    actual = int(measured["prompt_tokens"])
    limits_ok = replace(LOCAL_LIMITS, prompt_tokens_max=actual, context_tokens_max=1_000_000)
    limits_over = replace(LOCAL_LIMITS, prompt_tokens_max=actual - 1, context_tokens_max=1_000_000)
    assemble_local_prompt(base_snapshot, limits=limits_ok)  # must not raise
    with pytest.raises(LocalContextLimitError) as ei:
        assemble_local_prompt(base_snapshot, limits=limits_over)
    assert ei.value.details["limit_name"] == "prompt_tokens"


def test_history_tokens_boundary(vault: tuple[list, Path]) -> None:
    notes, root = vault
    request = replace(_local_request(root), history_limits=_local_request(root).history_limits)
    prepared = ctx.prepare(request, notes, history_text=_words(10))
    snap = prepared.snapshot
    permissive = replace(LOCAL_LIMITS, history_tokens_max=1_000_000, prompt_tokens_max=1_000_000, context_tokens_max=1_000_000)
    measured = assemble_local_prompt(snap, limits=permissive).budget_report
    actual = int(measured["history_tokens"])
    assert actual > 0, "expected the injected history text to be counted"
    limits_ok = replace(LOCAL_LIMITS, history_tokens_max=actual, prompt_tokens_max=1_000_000, context_tokens_max=1_000_000)
    limits_over = replace(LOCAL_LIMITS, history_tokens_max=actual - 1, prompt_tokens_max=1_000_000, context_tokens_max=1_000_000)
    assemble_local_prompt(snap, limits=limits_ok)  # must not raise
    with pytest.raises(LocalContextLimitError) as ei:
        assemble_local_prompt(snap, limits=limits_over)
    assert ei.value.details["limit_name"] == "history_tokens"


def test_assemble_local_prompt_rejects_non_canonical_user_text() -> None:
    limits = replace(LOCAL_LIMITS, user_text_bytes_max=1_000_000, user_text_tokens_max=1_000_000, prompt_tokens_max=1_000_000, context_tokens_max=1_000_000)
    snap = _snapshot_with_user_text("hello\x00world")
    with pytest.raises(LocalPolicyDriftError):
        assemble_local_prompt(snap, limits=limits)


def test_assemble_local_prompt_selects_warm_class_and_output_reserve(base_snapshot) -> None:
    permissive = replace(LOCAL_LIMITS, context_tokens_max=1_000_000, prompt_tokens_max=1_000_000)
    projection = assemble_local_prompt(base_snapshot, limits=permissive)
    warm_class = projection.budget_report["warm_class"]
    assert warm_class in (LocalWarmClass.LOCAL_S.value, LocalWarmClass.LOCAL_MAX.value)
    expected_reserve = LOCAL_WARM_CLASS_SPECS[LocalWarmClass(warm_class)].num_predict
    assert projection.content.max_output_tokens == expected_reserve
    assert projection.budget_report["output_reserve_tokens"] == expected_reserve
    # The shared prompt_assembled trace call (application._execute_attempt) reads these two
    # keys unconditionally regardless of profile; assemble_local_prompt must always supply them.
    assert projection.budget_report["input_tokens"] == projection.budget_report["prompt_tokens"]
    assert projection.budget_report["total_tokens"] == (
        projection.budget_report["prompt_tokens"] + expected_reserve
    )


def _snapshot_with_user_text(text: str):
    repo = FileSystemKnowledgeRepository(Config())
    notes = repo.discover()
    root = Path(repo.root)
    return ctx.prepare(_local_request(root, text=text), notes).snapshot


# ------------------------------------------------------------------ validate_local_response
# (147 sec 4, amended by Handoff 151/151a -- V05-PT-37 PT37-CTO-03 closure: the closed local
# response shape is now ``{"claims": [{"text","type","evidence"}, ...], "limitations": [...]}``,
# mirroring the remote/mock claims taxonomy's field names. ``validate_local_response`` proves
# only the LOCAL closed-schema/hostile-content boundary (shape, per-claim taxonomy-string
# allowlist, hostile-content/canonical-text on claim text, citation-id-exists-in-allowlist);
# it deliberately does NOT enforce fact/inference-requires-evidence or
# model_knowledge/unknown/assumption-forbids-evidence coherence -- that taxonomy/support
# semantics is exclusively ``evidence.validate_response``'s job once ``application.py`` routes
# the validated shape into it unchanged (Handoff 151a §3 item 2), so it is proven once, not
# duplicated here.
_ALLOWED = frozenset({"C1", "C2"})


def _body(obj: object) -> bytes:
    return canonical_json(obj).encode("utf-8")


def _claim(text: str = "x", type_: str = "model_knowledge", evidence: list | None = None) -> dict:
    return {"text": text, "type": type_, "evidence": evidence if evidence is not None else []}


def test_validate_local_response_accepts_a_minimal_valid_claim() -> None:
    out = validate_local_response(
        _body({"claims": [_claim("hello")], "limitations": []}),
        allowed_citation_ids=_ALLOWED,
    )
    assert out == LocalResponse(
        claims=(LocalClaim(text="hello", type="model_knowledge", evidence=()),),
        limitations=(),
    )


def test_validate_local_response_accepts_a_real_citation() -> None:
    out = validate_local_response(
        _body({"claims": [_claim("hello", "fact", ["C1"])], "limitations": []}),
        allowed_citation_ids=_ALLOWED,
    )
    assert out.claims[0].evidence == ("C1",)


def test_validate_local_response_accepts_several_claims_and_limitations() -> None:
    out = validate_local_response(
        _body(
            {
                "claims": [
                    _claim("first fact", "fact", ["C1"]),
                    _claim("second inference", "inference", ["C1", "C2"]),
                    _claim("unsupported knowledge", "model_knowledge"),
                    _claim("cannot answer", "unknown"),
                    _claim("assumed reference", "assumption"),
                ],
                "limitations": ["not fully covered"],
            }
        ),
        allowed_citation_ids=_ALLOWED,
    )
    assert [c.type for c in out.claims] == [
        "fact",
        "inference",
        "model_knowledge",
        "unknown",
        "assumption",
    ]
    assert out.limitations == ("not fully covered",)


def test_same_citation_id_across_different_claims_is_allowed() -> None:
    # A single closed-schema validation pass does not know whether two claims citing the
    # same source are each independently exactly supported by it -- that per-claim support
    # test is evidence.validate_response's job. Re-citing the same real id from a different
    # claim is legitimate shape and must not be rejected as a "duplicate" here.
    out = validate_local_response(
        _body(
            {
                "claims": [_claim("first", "fact", ["C1"]), _claim("second", "fact", ["C1"])],
                "limitations": [],
            }
        ),
        allowed_citation_ids=_ALLOWED,
    )
    assert out.claims[0].evidence == out.claims[1].evidence == ("C1",)


@pytest.mark.parametrize(
    ("raw_bytes_len", "should_raise"),
    [(16384, False), (16385, True)],
)
def test_raw_response_bytes_boundary(raw_bytes_len: int, should_raise: bool) -> None:
    # Pad via a *limitations* entry (not a claim's text) so the whole canonical JSON body
    # lands exactly at/one-over the raw-bytes limit without separately tripping the much
    # smaller per-claim-text-bytes limit (8192).
    scaffold = canonical_json({"claims": [_claim("x")], "limitations": [""]}).encode("utf-8")
    pad = raw_bytes_len - len(scaffold)
    assert pad > 0
    body = canonical_json({"claims": [_claim("x")], "limitations": ["a" * pad]}).encode("utf-8")
    assert len(body) == raw_bytes_len
    if should_raise:
        with pytest.raises(LocalGatewayBlocked) as ei:
            validate_local_response(body, allowed_citation_ids=_ALLOWED)
        assert ei.value.details["reason"] == "raw_bytes_exceeded"
    else:
        validate_local_response(body, allowed_citation_ids=_ALLOWED)  # must not raise


def test_invalid_utf8_rejected() -> None:
    with pytest.raises(LocalGatewayBlocked) as ei:
        validate_local_response(b"\xff\xfe\x00bad", allowed_citation_ids=_ALLOWED)
    assert ei.value.details["reason"] == "invalid_utf8"


def test_invalid_json_rejected() -> None:
    with pytest.raises(LocalGatewayBlocked) as ei:
        validate_local_response(b"not json{", allowed_citation_ids=_ALLOWED)
    assert ei.value.details["reason"] == "invalid_json"


def test_non_object_json_rejected() -> None:
    with pytest.raises(LocalGatewayBlocked) as ei:
        validate_local_response(b"[1,2,3]", allowed_citation_ids=_ALLOWED)
    assert ei.value.details["reason"] == "not_an_object"


def test_unknown_top_level_field_rejected() -> None:
    body = _body({"claims": [_claim("x")], "limitations": [], "extra": "nope"})
    with pytest.raises(LocalGatewayBlocked) as ei:
        validate_local_response(body, allowed_citation_ids=_ALLOWED)
    assert ei.value.details["reason"] == "unknown_fields"
    assert ei.value.details["fields"] == ["extra"]


def test_claims_missing_or_wrong_typed_rejected() -> None:
    with pytest.raises(LocalGatewayBlocked) as ei:
        validate_local_response(_body({"limitations": []}), allowed_citation_ids=_ALLOWED)
    assert ei.value.details["reason"] == "claims_wrong_type"
    with pytest.raises(LocalGatewayBlocked) as ei2:
        validate_local_response(
            _body({"claims": "nope", "limitations": []}), allowed_citation_ids=_ALLOWED
        )
    assert ei2.value.details["reason"] == "claims_wrong_type"


def test_empty_claims_rejected() -> None:
    with pytest.raises(LocalGatewayBlocked) as ei:
        validate_local_response(
            _body({"claims": [], "limitations": []}), allowed_citation_ids=_ALLOWED
        )
    assert ei.value.details["reason"] == "claims_empty"


def test_limitations_wrong_typed_rejected() -> None:
    with pytest.raises(LocalGatewayBlocked) as ei:
        validate_local_response(
            _body({"claims": [_claim("x")], "limitations": "not-a-list"}),
            allowed_citation_ids=_ALLOWED,
        )
    assert ei.value.details["reason"] == "limitations_wrong_type"
    with pytest.raises(LocalGatewayBlocked):
        validate_local_response(
            _body({"claims": [_claim("x")], "limitations": [1]}), allowed_citation_ids=_ALLOWED
        )


def test_claim_not_an_object_rejected() -> None:
    body = _body({"claims": ["not-an-object"], "limitations": []})
    with pytest.raises(LocalGatewayBlocked) as ei:
        validate_local_response(body, allowed_citation_ids=_ALLOWED)
    assert ei.value.details["reason"] == "claim_not_an_object"
    assert ei.value.details["index"] == 0


def test_claim_unknown_field_rejected() -> None:
    claim = {"text": "x", "type": "unknown", "evidence": [], "extra": "nope"}
    body = _body({"claims": [claim], "limitations": []})
    with pytest.raises(LocalGatewayBlocked) as ei:
        validate_local_response(body, allowed_citation_ids=_ALLOWED)
    assert ei.value.details["reason"] == "claim_unknown_fields"
    assert ei.value.details["fields"] == ["extra"]


def test_claim_with_evidence_key_omitted_defaults_to_no_evidence() -> None:
    # "evidence" is optional-with-default in the raw per-claim lookup (mirroring the old
    # flat schema's "citations" default) -- a claim object with only text/type still
    # parses, defaulting evidence to an empty tuple rather than being rejected.
    out = validate_local_response(
        _body({"claims": [{"text": "x", "type": "unknown"}], "limitations": []}),
        allowed_citation_ids=_ALLOWED,
    )
    assert out.claims[0].evidence == ()


def test_claim_missing_text_rejected() -> None:
    body = _body({"claims": [{"type": "unknown", "evidence": []}], "limitations": []})
    with pytest.raises(LocalGatewayBlocked) as ei:
        validate_local_response(body, allowed_citation_ids=_ALLOWED)
    assert ei.value.details["reason"] == "claim_text_wrong_type"


def test_claim_text_missing_or_wrong_typed_rejected() -> None:
    with pytest.raises(LocalGatewayBlocked) as ei:
        validate_local_response(
            _body({"claims": [{"type": "unknown", "evidence": []}], "limitations": []}),
            allowed_citation_ids=_ALLOWED,
        )
    assert ei.value.details["reason"] == "claim_text_wrong_type"
    with pytest.raises(LocalGatewayBlocked):
        validate_local_response(
            _body({"claims": [_claim(5, "unknown")]}), allowed_citation_ids=_ALLOWED  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "claim_type", ["fact", "inference", "model_knowledge", "unknown", "assumption"]
)
def test_every_recognized_claim_type_is_accepted(claim_type: str) -> None:
    evidence = ["C1"] if claim_type in ("fact", "inference") else []
    validate_local_response(
        _body({"claims": [_claim("x", claim_type, evidence)], "limitations": []}),
        allowed_citation_ids=_ALLOWED,
    )  # must not raise


def test_claim_type_missing_or_wrong_typed_or_unrecognized_rejected() -> None:
    bad_claims = [
        {"text": "x", "evidence": []},
        _claim("x", 5),  # type: ignore[arg-type]
        _claim("x", "opinion"),
    ]
    for bad in bad_claims:
        body = _body({"claims": [bad], "limitations": []})
        with pytest.raises(LocalGatewayBlocked) as ei:
            validate_local_response(body, allowed_citation_ids=_ALLOWED)
        assert ei.value.details["reason"] == "claim_type_invalid"


def test_claim_evidence_wrong_typed_rejected() -> None:
    with pytest.raises(LocalGatewayBlocked) as ei:
        validate_local_response(
            _body({"claims": [{"text": "x", "type": "fact", "evidence": "C1"}], "limitations": []}),
            allowed_citation_ids=_ALLOWED,
        )
    assert ei.value.details["reason"] == "claim_evidence_wrong_type"
    with pytest.raises(LocalGatewayBlocked):
        validate_local_response(
            _body({"claims": [{"text": "x", "type": "fact", "evidence": [1]}], "limitations": []}),
            allowed_citation_ids=_ALLOWED,
        )


def test_duplicate_evidence_within_one_claim_rejected() -> None:
    body = _body({"claims": [_claim("x", "fact", ["C1", "C1"])], "limitations": []})
    with pytest.raises(LocalGatewayBlocked) as ei:
        validate_local_response(body, allowed_citation_ids=_ALLOWED)
    assert ei.value.details["reason"] == "duplicate_claim_evidence"
    assert ei.value.details["index"] == 0


@pytest.mark.parametrize(("count", "should_raise"), [(12, False), (13, True)])
def test_total_citations_count_boundary(count: int, should_raise: bool) -> None:
    allowed = frozenset(f"C{i}" for i in range(1, 14))
    # Spread the citations across several claims (one per citation) so the boundary is on
    # the aggregate, not any single claim's evidence list.
    claims = [_claim(f"c{i}", "fact", [f"C{i}"]) for i in range(1, count + 1)]
    body = _body({"claims": claims, "limitations": []})
    if should_raise:
        with pytest.raises(LocalGatewayBlocked) as ei:
            validate_local_response(body, allowed_citation_ids=allowed)
        assert ei.value.details["reason"] == "citations_exceeded"
    else:
        validate_local_response(body, allowed_citation_ids=allowed)  # must not raise


@pytest.mark.parametrize(("n", "should_raise"), [(8192, False), (8193, True)])
def test_claim_text_bytes_boundary(n: int, should_raise: bool) -> None:
    body = _body({"claims": [_claim("a" * n)], "limitations": []})
    if should_raise:
        with pytest.raises(LocalGatewayBlocked) as ei:
            validate_local_response(body, allowed_citation_ids=_ALLOWED)
        assert ei.value.details["reason"] == "claim_text_bytes_exceeded"
    else:
        validate_local_response(body, allowed_citation_ids=_ALLOWED)  # must not raise


def test_fake_citation_id_rejected() -> None:
    body = _body({"claims": [_claim("x [Z9]", "fact", ["Z9"])], "limitations": []})
    with pytest.raises(LocalGatewayBlocked) as ei:
        validate_local_response(body, allowed_citation_ids=_ALLOWED)
    assert ei.value.code == "blocked_local_unsafe_output"
    assert ei.value.details["reason"] == "fake_citation"
    assert ei.value.details["citation_id"] == "Z9"


def test_non_canonical_claim_text_rejected() -> None:
    body = _body({"claims": [_claim("bad\rline")], "limitations": []})
    with pytest.raises(LocalGatewayBlocked) as ei:
        validate_local_response(body, allowed_citation_ids=_ALLOWED)
    assert ei.value.details["reason"] == "cr_present"


# ------------------------------------------------------------------ hostile-output corpus
# (147 sec 4)
_HOSTILE_ANSWERS = [
    ("control_char", "hello\x01world"),
    ("bidi_override", "hello\u202eworld"),
    ("script_or_markup", "click <script>evil()</script>"),
    ("script_or_markup_onattr", 'a<div onclick="x()">b</div>'),
    ("uri_scheme", "see file://etc/passwd"),
    ("path_like", "open /etc/passwd now"),
    ("path_like_windows", "open C:\\Windows\\System32\\config now"),
    ("path_like_traversal", "go ../../etc/passwd"),
    ("secret_like_aws", "key AKIAABCDEFGHIJKLMNOP leaked"),
    ("secret_like_openai", "key sk-abcdefghijklmnopqrstuvwx leaked"),
    ("secret_like_pem", "-----BEGIN RSA PRIVATE KEY-----leak"),
    ("provider_error_syntax", "Traceback (most recent call last): boom"),
]


_HOSTILE_IDS = [label for label, _ in _HOSTILE_ANSWERS]


@pytest.mark.parametrize(("label", "hostile_text"), _HOSTILE_ANSWERS, ids=_HOSTILE_IDS)
def test_hostile_output_corpus_rejected_in_claim_text(label: str, hostile_text: str) -> None:
    body = _body({"claims": [_claim(hostile_text)], "limitations": []})
    with pytest.raises(LocalGatewayBlocked) as ei:
        validate_local_response(body, allowed_citation_ids=_ALLOWED)
    assert ei.value.code == "blocked_local_unsafe_output"
    assert ei.value.details["field"] == "claims[0].text"


def test_hostile_output_corpus_rejected_in_limitations() -> None:
    body = _body({"claims": [_claim("fine")], "limitations": ["<script>evil()</script>"]})
    with pytest.raises(LocalGatewayBlocked) as ei:
        validate_local_response(body, allowed_citation_ids=_ALLOWED)
    assert ei.value.code == "blocked_local_unsafe_output"
    assert ei.value.details["field"] == "limitations"


def test_benign_urls_and_words_are_not_falsely_flagged() -> None:
    # Sanity check the corpus isn't so broad it rejects ordinary safe text.
    benign = _claim("The file is small and the pathway is clear.")
    validate_local_response(
        _body({"claims": [benign], "limitations": []}), allowed_citation_ids=_ALLOWED
    )  # must not raise
