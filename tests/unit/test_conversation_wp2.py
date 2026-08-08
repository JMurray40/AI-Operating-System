"""WP2 — Google adapter through a fake transport and local capture (C13-C15 + degraded).

No live provider call, key, or network. The adapter is exercised with an in-process
capturing/fake transport and injected canary credentials.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from jarvis_core.config import Config
from jarvis_core.conversation import ConversationApplication, PrepareTurnRequest
from jarvis_core.conversation.contract import FailureClass
from jarvis_core.conversation.request import Budgets
from jarvis_core.policy import local_allow_all
from jarvis_core.providers.conversation import (
    CancellationToken,
    Credential,
    MockConversationProvider,
    NormalizedResult,
    ProviderContent,
    ProviderRequest,
    TerminalState,
    TransportMetadata,
    UsageProvenance,
)
from jarvis_core.providers.credentials import EnvCredentialProvider, StaticCredentialProvider
from jarvis_core.providers.google_gemini import (
    APPROVED_HOST,
    APPROVED_MAX_OUTPUT_TOKENS,
    APPROVED_THINKING_LEVEL,
    GoogleGeminiAdapter,
    google_gemini_profile,
)
from jarvis_core.providers.transport import (
    HttpsTransport,
    RedirectRejected,
    RequestTooLarge,
    TransportCancelled,
    TransportError,
    TransportRequest,
    TransportResponse,
    TransportTimeout,
)
from jarvis_core.repositories import FileSystemKnowledgeRepository

T = datetime(2026, 8, 1, tzinfo=timezone.utc)
CANARY = "CANARY-API-KEY-do-not-log-9z9z"

# AC-05-03R: the adapter now enforces exact content-policy equality (max_output_tokens,
# thinking_level), not just transport/destination. Fixtures below must supply the approved
# values to reach the behavior each test actually exercises (timeout/malformed/credential/
# secret-redaction/...), rather than being short-circuited by a (correct) BLOCKED result.
_GOOGLE_BUDGETS = Budgets(
    context_tokens=3000, prompt_tokens=20000, output_reserve_tokens=APPROVED_MAX_OUTPUT_TOKENS
)


class CapturingTransport:
    """In-process transport seam: records the exact wire request; optional raise/response."""

    def __init__(
        self, response: TransportResponse | None = None, raises: Exception | None = None
    ) -> None:
        self.response = response
        self.raises = raises
        self.calls = 0
        self.last: TransportRequest | None = None

    def send(self, request: TransportRequest, cancel: CancellationToken | None = None):  # type: ignore[no-untyped-def]
        self.calls += 1
        self.last = request
        if self.raises is not None:
            raise self.raises
        assert self.response is not None
        return self.response


def _ok_body(text: str | None = None, usage: bool = True) -> bytes:
    from jarvis_core.providers.conversation import structured_answer

    answer = (
        text
        if text is not None
        else structured_answer([("A deterministic offline reply.", "model_knowledge", [])])
    )
    doc: dict = {
        "candidates": [
            {"content": {"parts": [{"text": answer}], "role": "model"}, "finishReason": "STOP"}
        ]
    }
    if usage:
        doc["usageMetadata"] = {
            "promptTokenCount": 120,
            "candidatesTokenCount": 8,
            "totalTokenCount": 128,
        }
    return json.dumps(doc).encode("utf-8")


def _transport_meta() -> TransportMetadata:
    p = google_gemini_profile()
    return TransportMetadata(
        provider_id=p.provider_id,
        model_id=p.model_id,
        scheme=p.scheme,
        host=p.host,
        path=p.path,
        operation=p.operation,
        timeout_seconds=p.timeout_seconds,
        max_input_tokens=p.max_input_tokens,
    )


def _preq(
    *,
    host: str | None = None,
    scheme: str | None = None,
    operation: str | None = None,
    credential: Credential | None = Credential(CANARY),
) -> ProviderRequest:
    tm = _transport_meta()
    if host or scheme or operation:
        tm = TransportMetadata(
            provider_id=tm.provider_id,
            model_id=tm.model_id,
            scheme=scheme or tm.scheme,
            host=host or tm.host,
            path=tm.path,
            operation=operation or tm.operation,
            timeout_seconds=tm.timeout_seconds,
            max_input_tokens=tm.max_input_tokens,
        )
    return ProviderRequest(
        request_id="r",
        attempt_id="a",
        content=ProviderContent(
            "system safety instruction",
            "hello world",
            APPROVED_MAX_OUTPUT_TOKENS,
            APPROVED_THINKING_LEVEL,
        ),
        transport=tm,
        credential=credential,
    )


# ================================================================ C13
def test_c13_capture_exact_content_fields_and_header_allowlist() -> None:
    cap = CapturingTransport(TransportResponse(200, {}, _ok_body()))
    res = GoogleGeminiAdapter(cap).dispatch(_preq())
    assert res.status is TerminalState.COMPLETED
    wire = cap.last
    assert wire is not None
    assert wire.scheme == "https" and wire.host == APPROVED_HOST
    assert wire.path.endswith(":generateContent")
    assert sorted(wire.headers) == ["content-type", "x-goog-api-key"]
    body = json.loads(wire.body)
    assert sorted(body) == ["contents", "generationConfig", "systemInstruction"]
    # no tools/grounding/cache/telemetry fields
    for forbidden in ("tools", "toolConfig", "cachedContent", "safetySettings", "labels"):
        assert forbidden not in body


def test_c13_credential_in_header_only_not_body() -> None:
    cap = CapturingTransport(TransportResponse(200, {}, _ok_body()))
    GoogleGeminiAdapter(cap).dispatch(_preq())
    assert cap.last.headers["x-goog-api-key"] == CANARY
    assert CANARY not in cap.last.body.decode("utf-8")


def test_c13_endpoint_host_escape_denied_without_send() -> None:
    cap = CapturingTransport(TransportResponse(200, {}, _ok_body()))
    res = GoogleGeminiAdapter(cap).dispatch(_preq(host="evil.example.com"))
    assert res.status is TerminalState.BLOCKED
    assert cap.calls == 0  # never dispatched to a non-approved host


def test_c13_scheme_and_operation_escape_denied() -> None:
    cap = CapturingTransport(TransportResponse(200, {}, _ok_body()))
    assert GoogleGeminiAdapter(cap).dispatch(_preq(scheme="http")).status is TerminalState.BLOCKED
    assert (
        GoogleGeminiAdapter(cap).dispatch(_preq(operation="streamGenerateContent")).status
        is TerminalState.BLOCKED
    )
    assert cap.calls == 0


def test_c13_redirect_denied_single_attempt_no_fallback() -> None:
    cap = CapturingTransport(raises=RedirectRejected("no"))
    res = GoogleGeminiAdapter(cap).dispatch(_preq())
    assert res.status is TerminalState.FAILED
    assert res.error_code == "network_denied"
    assert cap.calls == 1  # exactly one attempt; no retry/fallback


# ================================================================ C14
def test_c14_mock_and_google_share_normalized_contract() -> None:
    cap = CapturingTransport(TransportResponse(200, {}, _ok_body()))
    google = GoogleGeminiAdapter(cap).dispatch(_preq())
    mock = MockConversationProvider().dispatch(_preq())
    for r in (google, mock):
        assert isinstance(r, NormalizedResult)
        assert r.status in set(TerminalState)
        d = r.to_dict()
        assert set(d) >= {
            "status",
            "provider_id",
            "model_id",
            "adapter_version",
            "text",
            "usage",
            "cost",
            "finish_reason",
        }


# ================================================================ C15
def test_c15_secret_absent_from_all_surfaces_end_to_end() -> None:
    repo = FileSystemKnowledgeRepository(Config())
    notes = repo.discover()
    root = Path(repo.root)
    cap = CapturingTransport(TransportResponse(200, {}, _ok_body()))
    app = ConversationApplication()
    s = app.create_session("local")
    req = PrepareTurnRequest(
        request_id="r1",
        session_id=s.session_id,
        workspace_id="local",
        scope=local_allow_all(workspace_id="local", max_sensitivity="internal"),
        source_root=root,
        user_text="summarize the AI Operating System project",
        provider_profile=google_gemini_profile(),
        budgets=_GOOGLE_BUDGETS,
        evaluation_time=T,
        want_trace=True,
    )
    snap = app.prepare_turn(s, req, notes, credentials=StaticCredentialProvider(CANARY))
    app.approve(s, actor="jason", now=T)
    res = app.dispatch_turn(s, GoogleGeminiAdapter(cap), now=T)
    assert res.attempt.status is TerminalState.COMPLETED
    blob = str(res.to_dict()) + str(s.trace.to_dict()) + str(snap.to_dict())
    assert CANARY not in blob


# ================================================================ degraded matrix
def test_provider_timeout_is_one_failed_attempt() -> None:
    cap = CapturingTransport(raises=TransportTimeout("t"))
    res = GoogleGeminiAdapter(cap).dispatch(_preq())
    assert res.status is TerminalState.FAILED and res.error_code == "provider_timeout"


def test_malformed_result_withheld() -> None:
    cap = CapturingTransport(TransportResponse(200, {}, b"not json at all"))
    res = GoogleGeminiAdapter(cap).dispatch(_preq())
    assert res.status is TerminalState.FAILED
    assert res.error_code == "malformed_response"
    assert res.text is None


def test_non_200_is_redacted_no_raw_body() -> None:
    cap = CapturingTransport(TransportResponse(500, {}, b"raw provider error SECRETLEAK"))
    res = GoogleGeminiAdapter(cap).dispatch(_preq())
    assert res.status is TerminalState.FAILED
    assert "SECRETLEAK" not in str(res.to_dict())


def test_safety_block_maps_to_blocked() -> None:
    body = json.dumps({"promptFeedback": {"blockReason": "SAFETY"}}).encode()
    cap = CapturingTransport(TransportResponse(200, {}, body))
    res = GoogleGeminiAdapter(cap).dispatch(_preq())
    assert res.status is TerminalState.BLOCKED


def test_usage_absent_is_unknown_not_zero() -> None:
    cap = CapturingTransport(TransportResponse(200, {}, _ok_body(usage=False)))
    res = GoogleGeminiAdapter(cap).dispatch(_preq())
    assert res.status is TerminalState.COMPLETED
    assert res.usage.provenance is UsageProvenance.UNKNOWN
    assert res.usage.input_tokens is None
    assert res.cost.amount_usd is None


def test_cancellation_before_send_no_dispatch() -> None:
    cap = CapturingTransport(TransportResponse(200, {}, _ok_body()))
    token = CancellationToken()
    token.cancel()
    res = GoogleGeminiAdapter(cap).dispatch(_preq(), token)
    assert res.status is TerminalState.CANCELLED
    assert cap.calls == 0


def test_missing_credential_is_typed_unavailable() -> None:
    cap = CapturingTransport(TransportResponse(200, {}, _ok_body()))
    res = GoogleGeminiAdapter(cap).dispatch(_preq(credential=None))
    assert res.status is TerminalState.FAILED
    assert res.error_code == "unavailable_credential"
    assert cap.calls == 0


def test_application_maps_failure_classes() -> None:
    repo = FileSystemKnowledgeRepository(Config())
    notes = repo.discover()
    root = Path(repo.root)
    app = ConversationApplication()
    s = app.create_session("local")
    req = PrepareTurnRequest(
        request_id="r1",
        session_id=s.session_id,
        workspace_id="local",
        scope=local_allow_all(workspace_id="local", max_sensitivity="internal"),
        source_root=root,
        user_text="summarize the AI Operating System project",
        provider_profile=google_gemini_profile(),
        budgets=_GOOGLE_BUDGETS,
        evaluation_time=T,
    )
    app.prepare_turn(s, req, notes, credentials=StaticCredentialProvider(CANARY))
    app.approve(s, actor="jason", now=T)
    adapter = GoogleGeminiAdapter(CapturingTransport(raises=TransportTimeout("t")))
    res = app.dispatch_turn(s, adapter, now=T)
    assert res.attempt.failure is FailureClass.PROVIDER_TIMEOUT
    assert s.turns == []  # failed attempt is not recorded as a completed turn


# ================================================================ transport guards
def test_https_transport_rejects_non_https() -> None:
    req = TransportRequest("POST", "http", "x", "/p", {}, b"{}", 5.0)
    with pytest.raises(TransportError):
        HttpsTransport().send(req)


def test_https_transport_rejects_oversized_request() -> None:
    req = TransportRequest("POST", "https", "x", "/p", {}, b"x" * 600_000, 5.0)
    with pytest.raises(RequestTooLarge):
        HttpsTransport().send(req)


def test_https_transport_honors_precancel() -> None:
    req = TransportRequest("POST", "https", "x", "/p", {}, b"{}", 5.0)
    token = CancellationToken()
    token.cancel()
    with pytest.raises(TransportCancelled):
        HttpsTransport().send(req, token)


# ================================================================ credentials
def test_env_credential_uses_injected_environment_only() -> None:
    present = EnvCredentialProvider(environ={"GEMINI_API_KEY": CANARY})
    assert present.is_available() is True
    assert present.get().reveal() == CANARY
    missing = EnvCredentialProvider(environ={})
    assert missing.is_available() is False
    with pytest.raises(LookupError):
        missing.get()
    blank = EnvCredentialProvider(environ={"GEMINI_API_KEY": "   "})
    assert blank.is_available() is False
