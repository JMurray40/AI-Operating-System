"""Injected HTTP transport seam for the conversation provider gateway (H07 §10, WP2).

The adapter never talks to a socket directly — it calls an injected :class:`Transport`.
Tests substitute a fake or a bounded loopback capture server; the production
:class:`HttpsTransport` uses only the standard library and is hardened: HTTPS-only,
environment proxy inheritance disabled, redirect following OFF, strict TLS verification,
bounded request/response bodies, connect/read timeouts, and cooperative cancellation.

No live provider call occurs in this cycle; the production transport is exercised only
against a loopback capture server in tests.
"""

from __future__ import annotations

import http.client
import ssl
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from jarvis_core.providers.conversation import CancellationToken

MAX_REQUEST_BYTES = 512_000
MAX_RESPONSE_BYTES = 1_000_000
_REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})


class TransportError(Exception):
    """Base transport failure (redacted; no raw provider error text escapes)."""


class TransportTimeout(TransportError):
    pass


class TransportCancelled(TransportError):
    pass


class RedirectRejected(TransportError):
    pass


class ResponseTooLarge(TransportError):
    pass


class RequestTooLarge(TransportError):
    pass


@dataclass(frozen=True)
class TransportRequest:
    """A fully-formed HTTP request. The adapter builds exactly one of these."""

    method: str
    scheme: str
    host: str
    path: str
    headers: Mapping[str, str]
    body: bytes
    timeout_seconds: float


@dataclass(frozen=True)
class TransportResponse:
    status_code: int
    headers: Mapping[str, str]
    body: bytes


@runtime_checkable
class Transport(Protocol):
    """The injected request runner contract."""

    def send(
        self, request: TransportRequest, cancel: CancellationToken | None = None
    ) -> TransportResponse:
        """Perform exactly one request; never follow redirects or read env proxies."""
        ...


class HttpsTransport:
    """Hardened stdlib HTTPS transport. HTTPS-only; no proxy inheritance; no redirects."""

    def __init__(
        self,
        *,
        max_response_bytes: int = MAX_RESPONSE_BYTES,
        max_request_bytes: int = MAX_REQUEST_BYTES,
        verify_tls: bool = True,
    ) -> None:
        self._max_response = max_response_bytes
        self._max_request = max_request_bytes
        self._verify_tls = verify_tls

    def send(
        self, request: TransportRequest, cancel: CancellationToken | None = None
    ) -> TransportResponse:
        if request.scheme != "https":
            raise TransportError("only https is permitted")
        if len(request.body) > self._max_request:
            raise RequestTooLarge("request body exceeds the bounded limit")
        if cancel is not None and cancel.cancelled:
            raise TransportCancelled("cancelled before dispatch")

        context = ssl.create_default_context()
        if not self._verify_tls:  # only ever used for loopback capture tests
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        # http.client does not read HTTP(S)_PROXY env vars, so proxy inheritance is off.
        conn = http.client.HTTPSConnection(
            request.host, timeout=request.timeout_seconds, context=context
        )
        try:
            conn.request(
                request.method,
                request.path,
                body=request.body,
                headers=dict(request.headers),
            )
            resp = conn.getresponse()
            if resp.status in _REDIRECT_STATUSES:
                raise RedirectRejected("redirects are not followed")
            body = resp.read(self._max_response + 1)
            if len(body) > self._max_response:
                raise ResponseTooLarge("response body exceeds the bounded limit")
            headers = {k.lower(): v for k, v in resp.getheaders()}
            if cancel is not None and cancel.cancelled:
                raise TransportCancelled("cancelled during dispatch")
            return TransportResponse(resp.status, headers, body)
        except TimeoutError as exc:
            raise TransportTimeout("request timed out") from exc
        finally:
            conn.close()


__all__ = [
    "MAX_REQUEST_BYTES",
    "MAX_RESPONSE_BYTES",
    "HttpsTransport",
    "RedirectRejected",
    "RequestTooLarge",
    "ResponseTooLarge",
    "Transport",
    "TransportCancelled",
    "TransportError",
    "TransportRequest",
    "TransportResponse",
    "TransportTimeout",
]
