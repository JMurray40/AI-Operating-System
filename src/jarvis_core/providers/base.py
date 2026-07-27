"""Provider-neutral interface. Providers are interchangeable reasoning engines
(SYSTEM_PRINCIPLES.md Principle 9); durable knowledge stays provider-independent.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from jarvis_core.models.context import ContextPackage


@dataclass(frozen=True)
class ProviderResponse:
    """A provider's structured response to a context package."""

    provider: str
    model_role: str
    summary: str
    received: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "provider": self.provider,
            "model_role": self.model_role,
            "summary": self.summary,
            "received": self.received,
        }


@runtime_checkable
class Provider(Protocol):
    """The minimal contract every provider adapter implements."""

    name: str

    def summarize(self, package: ContextPackage, model_role: str = "fast") -> ProviderResponse:
        """Accept a context package and return a structured response."""
