"""Credential retrieval boundary implementations (Handoff 08a Decision A, WP2).

``EnvCredentialProvider`` is the production environment-backed provider. Its environment
is *injectable*: the default binds to ``os.environ`` at construction, but tests pass their
own mapping with a canary so they never read the live ``GEMINI_API_KEY``. ``is_available``
answers presence only (no network, no remote validation); ``get`` returns the opaque
:class:`Credential` for a single dispatch. ``StaticCredentialProvider`` is a small helper
for scripted/local wiring and tests.

No live key is read in this cycle. WP4 (separately authorized) is the only place a real key
is ever used.
"""

from __future__ import annotations

import os
from collections.abc import Mapping

from jarvis_core.providers.conversation import Credential

DEFAULT_ENV_VAR = "GEMINI_API_KEY"


class EnvCredentialProvider:
    """Reads an API key from an injected environment mapping (defaults to ``os.environ``)."""

    def __init__(
        self,
        *,
        var: str = DEFAULT_ENV_VAR,
        environ: Mapping[str, str] | None = None,
    ) -> None:
        self._var = var
        # Bind to os.environ only when no explicit mapping is injected. Tests always inject.
        self._environ: Mapping[str, str] = environ if environ is not None else os.environ

    def is_available(self) -> bool:
        value = self._environ.get(self._var)
        return bool(value and value.strip())

    def get(self) -> Credential:
        value = self._environ.get(self._var)
        if not value or not value.strip():
            raise LookupError("credential is unavailable")
        return Credential(value)


class StaticCredentialProvider:
    """A fixed in-memory credential provider (scripted wiring / tests)."""

    def __init__(self, secret: str | None) -> None:
        self._secret = secret

    def is_available(self) -> bool:
        return bool(self._secret and self._secret.strip())

    def get(self) -> Credential:
        if not self._secret or not self._secret.strip():
            raise LookupError("credential is unavailable")
        return Credential(self._secret)


__all__ = ["DEFAULT_ENV_VAR", "EnvCredentialProvider", "StaticCredentialProvider"]
