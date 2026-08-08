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
    APPROVED_MAX_OUTPUT_TOKENS,
    APPROVED_MODEL_ID,
    APPROVED_PATH,
    APPROVED_PROVIDER_ID,
    APPROVED_THINKING_LEVEL,
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


def _content(**over: object) -> ProviderContent:
    base = dict(
        system_instruction="sys", user_text="hi",
        max_output_tokens=APPROVED_MAX_OUTPUT_TOKENS, thinking_level=APPROVED_THINKING_LEVEL,
    )
    base.update(over)
    return ProviderContent(**base)  # type: ignore[arg-type]


def _req(meta: TransportMetadata, content: ProviderContent | None = None) -> ProviderRequest:
    return ProviderRequest(
        request_id="r", attempt_id="a",
        content=content if content is not None else _content(), transport=meta,
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


# ------------------------------------------------------------------ AC-05-03R: content policy
# The prior round checked only ``TransportMetadata`` (destination/protocol/retry/streaming).
# ``max_output_tokens`` and ``thinking_level`` live on ``ProviderContent`` instead and were
# never checked at this boundary at all: the positive-path fixture above even asserted
# COMPLETED using an unapproved 800-token value, proving the field was fully unenforced. One
# negative case per bound content field, each proving zero transport calls.
@pytest.mark.parametrize(
    "over",
    [
        {"max_output_tokens": APPROVED_MAX_OUTPUT_TOKENS - 1},  # response-limit drift (under)
        {"max_output_tokens": APPROVED_MAX_OUTPUT_TOKENS + 1},  # response-limit drift (over)
        {"max_output_tokens": 800},                             # arbitrary caller value
        {"thinking_level": "high"},                             # thinking-level drift
        {"thinking_level": ""},                                 # empty thinking-level
    ],
)
def test_content_policy_drift_blocked_zero_transport(over: dict) -> None:
    cap = _CountingTransport()
    res = GoogleGeminiAdapter(cap).dispatch(_req(_meta(), _content(**over)))
    assert res.status is TerminalState.BLOCKED
    assert res.error_code == "endpoint_denied"
    assert cap.calls == 0


def test_content_policy_checked_before_credential_materialization() -> None:
    """A content-policy mismatch fails even when no credential/transport is reachable."""
    cap = _CountingTransport()
    req = ProviderRequest(
        request_id="r", attempt_id="a",
        content=_content(max_output_tokens=1), transport=_meta(), credential=None,
    )
    res = GoogleGeminiAdapter(cap).dispatch(req)
    assert res.status is TerminalState.BLOCKED
    assert res.error_code == "endpoint_denied"
    assert cap.calls == 0


# ------------------------------------------------------------------ AC-05-03R: cost estimation
# ``estimate_cost_usd`` must consume the frozen abstract Mapping contract (a real snapshot's
# ``budget_accounting`` is a ``MappingProxyType`` per AC-05-01R), not require a concrete
# ``dict``. Proves it uses the approved budgets rather than silently falling back to a fixed
# zero-usage/zero-reserve estimate when handed a mapping proxy.
def test_cost_estimation_uses_frozen_mapping_proxy_budgets() -> None:
    from types import MappingProxyType

    class _Snap:
        budget_accounting = MappingProxyType(
            {"context_tokens_used": 10_000, "output_reserve_tokens": 2_000}
        )
        max_cost_usd_per_request = 999.0

    adapter = GoogleGeminiAdapter(_CountingTransport())
    estimate = adapter.estimate_cost_usd(_Snap())
    fallback_estimate = adapter.estimate_cost_usd(
        type("S", (), {"budget_accounting": {}, "max_cost_usd_per_request": 999.0})()
    )
    assert estimate > fallback_estimate  # the real budgets must move the estimate
