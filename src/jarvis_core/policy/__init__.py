"""Authorization policy: scope, sensitivity, and typed fail-closed errors (ADR-0015)."""
from __future__ import annotations

from jarvis_core.policy.errors import PolicyError
from jarvis_core.policy.scope import AuthorizationScope, local_allow_all
from jarvis_core.policy.sensitivity import KNOWN_SENSITIVITIES, within_ceiling

__all__ = [
    "KNOWN_SENSITIVITIES",
    "AuthorizationScope",
    "PolicyError",
    "local_allow_all",
    "within_ceiling",
]
