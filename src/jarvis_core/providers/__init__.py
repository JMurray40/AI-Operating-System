"""Provider adapters (mock implemented; others are documented placeholders)."""
from __future__ import annotations

from jarvis_core.providers.base import Provider, ProviderResponse
from jarvis_core.providers.mock import MockProvider
from jarvis_core.providers.placeholders import (
    AnthropicProvider,
    GeminiProvider,
    OllamaProvider,
    OpenAIProvider,
)

#: Only providers safe to run in this prototype.
AVAILABLE_PROVIDERS = {"mock": MockProvider}


def get_provider(name: str) -> Provider:
    """Return an instantiated provider by name, or raise ValueError."""
    factory = AVAILABLE_PROVIDERS.get(name)
    if factory is None:
        raise ValueError(
            f"Unknown or unavailable provider '{name}'. Available: "
            f"{', '.join(sorted(AVAILABLE_PROVIDERS))}"
        )
    return factory()


__all__ = [
    "AVAILABLE_PROVIDERS",
    "AnthropicProvider",
    "GeminiProvider",
    "MockProvider",
    "OllamaProvider",
    "OpenAIProvider",
    "Provider",
    "ProviderResponse",
    "get_provider",
]
