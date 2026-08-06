"""AC-05-03 — exact Google destination allowlisting; every negative proves zero transport."""
from __future__ import annotations

import json

import pytest

from jarvis_core.providers.conversation import (
    Credential,
    ProviderContent,
    ProviderRequest,
    TerminalState,
    TransportMetadata,
)
from jarvis_core.providers.google_gemini import (
    APPROVED_HOST,
    APPROVED_MODEL_ID,
    APPROVED_PATH,
    APPROVED_PROVIDER_ID,
    GoogleGeminiAdapter,
)
from jarvis_core.providers.transport import TransportResponse

CANARY = "CANARY-KEY"


class _CountingTransport:
    def __init__(self) -> None:
        self.calls = 0

    def send(self, request, cancel=None):  # type: ignore[no-untyped-def]
        self.calls += 1
        body = json.dumps(
            {"candidates": [{"content": {"parts": [{"text": "ok [C1]"}]},
                             "finishReason": "STOP"}]}
        ).encode()
        return TransportResponse(200, {}, body)


def _meta(**over: object) -> TransportMetadata:
    base = dict(
        provider_id=APPROVED_PROVIDER_ID, model_id=APPROVED_MODEL_ID, scheme="https",
        host=APPROVED_HOST, path=APPROVED_PATH, operation="generateContent",
        timeout_seconds=60.0, max_input_tokens=64000, streaming=False, automatic_retries=0,
    )
    base.update(over)
    return TransportMetadata(**base)  # type: ignore[arg-type]


def _req(meta: TransportMetadata) -> ProviderRequest:
    return ProviderRequest(
        request_id="r", attempt_id="a",
        content=ProviderContent("sys", "hi", 800), transport=meta,
        credential=Credential(CANARY),
    )


def test_approved_destination_dispatches() -> None:
    cap = _CountingTransport()
    res = GoogleGeminiAdapter(cap).dispatch(_req(_meta()))
    assert res.status is TerminalState.COMPLETED and cap.calls == 1


@pytest.mark.parametrize(
    "over",
    [
        {"host": "generativelanguage.googleapis.com:443"},   # alternate/explicit port
        {"host": "user@generativelanguage.googleapis.com"},  # user-info
        {"host": "Generativelanguage.Googleapis.Com"},       # case variant
        {"host": "evil.example.com"},                        # wrong host
        {"path": APPROVED_PATH + "/"},                        # trailing slash
        {"path": APPROVED_PATH + "?key=x"},                   # query
        {"path": APPROVED_PATH + "#frag"},                    # fragment
        {"path": "/v1beta//models/gemini-3.5-flash-lite:generateContent"},  # double slash
        {"path": "/v1beta/models/gemini-3.5-flash-lite%3AgenerateContent"},  # encoded
        {"path": "/V1BETA/models/gemini-3.5-flash-lite:generateContent"},   # case variant
        {"path": "/v1/models/gemini-3.5-flash-lite:generateContent"},       # alt api version
        {"path": "/v1beta/models/gemini-2.0-flash:generateContent"},        # alt model in path
        {"model_id": "gemini-2.0-flash"},                    # alt native model
        {"provider_id": "google-vertex"},                    # alt provider id
        {"scheme": "http"},                                  # non-https
        {"operation": "streamGenerateContent"},              # alt operation
        {"streaming": True},                                 # streaming
        {"automatic_retries": 1},                            # retry policy drift
        {"timeout_seconds": 120.0},                          # timeout drift
        {"max_input_tokens": 128000},                        # limit drift
    ],
)
def test_destination_drift_blocked_zero_transport(over: dict) -> None:
    cap = _CountingTransport()
    res = GoogleGeminiAdapter(cap).dispatch(_req(_meta(**over)))
    assert res.status is TerminalState.BLOCKED
    assert res.error_code == "endpoint_denied"
    assert cap.calls == 0
