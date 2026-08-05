"""The sole Google Gemini wire-format boundary (H07 §4.2/§7.4, ADR-0024, WP2).

Translates the normalized :class:`ProviderRequest` into exactly one approved
``generateContent`` HTTPS call through an injected :class:`Transport`, and normalizes the
response. It adds only the allowlisted method/path/host headers and the opaque API-key
header, rejects any endpoint/scheme/operation escape, follows no redirect, inherits no
proxy, emits no telemetry, performs no fallback or hidden retry, and never lets a raw
provider payload cross the boundary.

No live call occurs in this cycle — the adapter is exercised only against a fake transport
or a bounded loopback capture server. The request path, auth header, and field shapes are
implemented from the documented Google REST contract and MUST be reconfirmed at the
separately authorized WP4 preflight (H07 §4.2).
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from jarvis_core.providers.conversation import (
    ERROR_BLOCKED,
    ERROR_ENDPOINT_DENIED,
    ERROR_MALFORMED,
    ERROR_NETWORK,
    ERROR_TIMEOUT,
    ERROR_UNAVAILABLE_CREDENTIAL,
    CancellationToken,
    Cost,
    NormalizedResult,
    ProviderRequest,
    TerminalState,
    Usage,
    UsageProvenance,
)
from jarvis_core.providers.transport import (
    RedirectRejected,
    Transport,
    TransportCancelled,
    TransportError,
    TransportRequest,
    TransportResponse,
    TransportTimeout,
)

GOOGLE_ADAPTER_VERSION = "jarvis.provider.google-gemini.v0.5.0"

# Approved destination identity (Handoff 06 / H07 §4.2). Enforced independently of caller.
APPROVED_HOST = "generativelanguage.googleapis.com"
APPROVED_SCHEME = "https"
APPROVED_OPERATION = "generateContent"
_APPROVED_PATH_PREFIX = "/v1beta/models/"

# Documentation reference for the wire shape; reconfirm at the WP4 preflight.
GOOGLE_DOC_REFERENCE = "https://ai.google.dev/api/generate-content (v1beta models.generateContent)"
GOOGLE_DOC_VERIFIED = "2026-08-01 implementation reference; reconfirm at WP4 preflight"

# Versioned price table (USD per token). Placeholder rates recorded for the estimate/ceiling
# mechanism; exact pricing is reconfirmed at the WP4 preflight before any real spend.
GOOGLE_PRICE_TABLE_VERSION = "google-gemini-3.5-flash-lite-2026-08-est"
_USD_PER_INPUT_TOKEN = 0.10 / 1_000_000
_USD_PER_OUTPUT_TOKEN = 0.40 / 1_000_000

_MAX_RESPONSE_TEXT_CHARS = 100_000


@dataclass(frozen=True)
class _Parsed:
    text: str
    finish_reason: str
    input_tokens: int | None
    output_tokens: int | None


def _estimate_cost(input_tokens: int, output_tokens: int) -> float:
    return round(input_tokens * _USD_PER_INPUT_TOKEN + output_tokens * _USD_PER_OUTPUT_TOKEN, 6)


class GoogleGeminiAdapter:
    """Google Gemini Developer API complete-response adapter (non-streaming)."""

    name = "google-gemini-developer-api"
    adapter_version = GOOGLE_ADAPTER_VERSION

    def __init__(self, transport: Transport) -> None:
        self._transport = transport

    # ------------------------------------------------------------------ cost hook
    def estimate_cost_usd(self, snapshot: object) -> float:
        """Pre-dispatch cost estimate for the per-request ceiling check (application hook)."""
        budget = getattr(snapshot, "budget_accounting", {})
        used = 0
        reserve = 0
        if isinstance(budget, dict):
            used = int(budget.get("context_tokens_used", 0) or 0)
            reserve = int(budget.get("output_reserve_tokens", 0) or 0)
        # Conservative bound: assume the whole context plus a fixed instruction overhead as
        # input, and the full output reserve as output.
        return _estimate_cost(used + 256, reserve)

    # ------------------------------------------------------------------ dispatch
    def dispatch(
        self, request: ProviderRequest, cancel: CancellationToken | None = None
    ) -> NormalizedResult:
        t = request.transport
        # 1) Endpoint allowlist — enforced here regardless of what the caller supplied.
        if (
            t.scheme != APPROVED_SCHEME
            or t.host != APPROVED_HOST
            or t.operation != APPROVED_OPERATION
            or not t.path.startswith(_APPROVED_PATH_PREFIX)
            or not t.path.endswith(":" + APPROVED_OPERATION)
            or t.streaming
            or t.automatic_retries != 0
        ):
            return self._fail(request, TerminalState.BLOCKED, ERROR_ENDPOINT_DENIED)
        # 2) Credential must be present (materialized by the application for one attempt).
        if request.credential is None:
            return self._fail(request, TerminalState.FAILED, ERROR_UNAVAILABLE_CREDENTIAL)
        if cancel is not None and cancel.cancelled:
            return NormalizedResult(
                status=TerminalState.CANCELLED,
                provider_id=t.provider_id,
                model_id=t.model_id,
                adapter_version=self.adapter_version,
                finish_reason="cancelled",
            )

        body = self._project_body(request)
        headers = {
            "content-type": "application/json",
            "x-goog-api-key": request.credential.reveal(),
        }
        wire = TransportRequest(
            method="POST",
            scheme=t.scheme,
            host=t.host,
            path=t.path,
            headers=headers,
            body=body,
            timeout_seconds=t.timeout_seconds,
        )
        try:
            response = self._transport.send(wire, cancel)
        except TransportCancelled:
            return NormalizedResult(
                status=TerminalState.CANCELLED,
                provider_id=t.provider_id,
                model_id=t.model_id,
                adapter_version=self.adapter_version,
                finish_reason="cancelled",
            )
        except TransportTimeout:
            return self._fail(request, TerminalState.FAILED, ERROR_TIMEOUT)
        except (RedirectRejected, TransportError):
            return self._fail(request, TerminalState.FAILED, ERROR_NETWORK)

        return self._normalize(request, response)

    # ------------------------------------------------------------------ projection
    def _project_body(self, request: ProviderRequest) -> bytes:
        c = request.content
        # Text-only content; fixed system instruction; bounded generation config; minimal
        # thinking via the documented thinkingConfig shape. No tools/grounding/etc.
        payload = {
            "systemInstruction": {"parts": [{"text": c.system_instruction}]},
            "contents": [{"role": "user", "parts": [{"text": c.user_text}]}],
            "generationConfig": {
                "maxOutputTokens": c.max_output_tokens,
                "temperature": 0,
                "candidateCount": 1,
                "thinkingConfig": {"thinkingBudget": 0},
            },
        }
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

    # ------------------------------------------------------------------ normalization
    def _normalize(self, request: ProviderRequest, response: TransportResponse) -> NormalizedResult:
        t = request.transport
        if response.status_code != 200:
            # Redacted: never surface a raw provider error body.
            code = ERROR_BLOCKED if response.status_code in (400, 403, 429) else ERROR_NETWORK
            return self._fail(request, TerminalState.FAILED, code)
        try:
            parsed = self._parse(response.body)
        except (ValueError, KeyError, TypeError):
            return self._fail(request, TerminalState.FAILED, ERROR_MALFORMED)
        if parsed is None:
            # Safety block or no candidate.
            return self._fail(request, TerminalState.BLOCKED, ERROR_BLOCKED)
        if not parsed.text.strip() or len(parsed.text) > _MAX_RESPONSE_TEXT_CHARS:
            return self._fail(request, TerminalState.FAILED, ERROR_MALFORMED)

        if parsed.input_tokens is not None and parsed.output_tokens is not None:
            usage = Usage(parsed.input_tokens, parsed.output_tokens, UsageProvenance.REPORTED)
            cost = Cost(
                _estimate_cost(parsed.input_tokens, parsed.output_tokens),
                "USD",
                GOOGLE_PRICE_TABLE_VERSION,
                UsageProvenance.REPORTED,
            )
        else:
            usage = Usage(None, None, UsageProvenance.UNKNOWN)
            cost = Cost(None, "USD", GOOGLE_PRICE_TABLE_VERSION, UsageProvenance.UNKNOWN)

        return NormalizedResult(
            status=TerminalState.COMPLETED,
            provider_id=t.provider_id,
            model_id=t.model_id,
            adapter_version=self.adapter_version,
            text=parsed.text,
            finish_reason=parsed.finish_reason,
            usage=usage,
            cost=cost,
        )

    def _parse(self, body: bytes) -> _Parsed | None:
        data = json.loads(body.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("response is not an object")
        # Prompt-level safety block.
        feedback = data.get("promptFeedback")
        if isinstance(feedback, dict) and feedback.get("blockReason"):
            return None
        candidates = data.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            return None
        first = candidates[0]
        if not isinstance(first, dict):
            raise ValueError("candidate is not an object")
        finish = str(first.get("finishReason", "STOP"))
        content = first.get("content", {})
        parts = content.get("parts", []) if isinstance(content, dict) else []
        texts = [p["text"] for p in parts if isinstance(p, dict) and isinstance(p.get("text"), str)]
        text = "".join(texts)
        usage = data.get("usageMetadata")
        in_tok = out_tok = None
        if isinstance(usage, dict):
            in_tok = usage.get("promptTokenCount")
            out_tok = usage.get("candidatesTokenCount")
            in_tok = int(in_tok) if isinstance(in_tok, int) else None
            out_tok = int(out_tok) if isinstance(out_tok, int) else None
        return _Parsed(text=text, finish_reason=finish, input_tokens=in_tok, output_tokens=out_tok)

    def _fail(self, request: ProviderRequest, status: TerminalState, code: str) -> NormalizedResult:
        t = request.transport
        return NormalizedResult(
            status=status,
            provider_id=t.provider_id,
            model_id=t.model_id,
            adapter_version=self.adapter_version,
            finish_reason=code,
            error_code=code,
            usage=Usage(None, None, UsageProvenance.UNKNOWN),
            cost=Cost(None, "USD", GOOGLE_PRICE_TABLE_VERSION, UsageProvenance.UNKNOWN),
        )


def google_gemini_profile() -> object:
    """The approved Google profile (imported lazily to avoid a hard conversation dep)."""
    from jarvis_core.conversation.request import ProviderProfile

    return ProviderProfile(
        provider_id="google-gemini-developer-api",
        model_id="gemini-3.5-flash-lite",
        scheme=APPROVED_SCHEME,
        host=APPROVED_HOST,
        path="/v1beta/models/gemini-3.5-flash-lite:generateContent",
        operation=APPROVED_OPERATION,
        max_input_tokens=64000,
        max_output_tokens=8000,
        timeout_seconds=60.0,
        thinking_level="minimal",
        max_cost_usd_per_request=0.05,
        price_table_version=GOOGLE_PRICE_TABLE_VERSION,
        is_remote=True,
        retention_disclosure=(
            "Google may process and retain request data per its published API terms and "
            "abuse-monitoring policy; zero data retention is not claimed."
        ),
    )


__all__ = [
    "APPROVED_HOST",
    "APPROVED_OPERATION",
    "APPROVED_SCHEME",
    "GOOGLE_ADAPTER_VERSION",
    "GOOGLE_DOC_REFERENCE",
    "GOOGLE_DOC_VERIFIED",
    "GOOGLE_PRICE_TABLE_VERSION",
    "GoogleGeminiAdapter",
    "google_gemini_profile",
]
