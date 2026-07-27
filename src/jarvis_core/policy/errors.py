"""Typed policy errors. Unknown or incomplete policy must fail closed (ADR-0015)."""
from __future__ import annotations


class PolicyError(Exception):
    """Raised when authorization/sensitivity policy is missing, invalid, or fails closed.

    Message text is safe for tracing: it must never contain excluded source identities,
    content, secrets, or file paths beyond what the caller already supplied.
    """
