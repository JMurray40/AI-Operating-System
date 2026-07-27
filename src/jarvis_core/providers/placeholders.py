"""Documentation-only placeholder adapters for future real providers.

These intentionally raise :class:`NotImplementedError`. No API keys, no network, no
SDK imports. They exist to show exactly where Anthropic/OpenAI/Gemini/Ollama adapters
will plug into the same :class:`Provider` contract (see docs/software/EXTENDING.md).
"""
from __future__ import annotations

from jarvis_core.models.context import ContextPackage
from jarvis_core.providers.base import ProviderResponse

_MESSAGE = (
    "{name} adapter is not implemented in the read-only prototype. "
    "Real providers require a separate design and explicit approval "
    "(no API keys or network access in this build)."
)


class _UnimplementedProvider:
    name = "unimplemented"

    def summarize(self, package: ContextPackage, model_role: str = "fast") -> ProviderResponse:
        raise NotImplementedError(_MESSAGE.format(name=self.name))


class AnthropicProvider(_UnimplementedProvider):
    name = "anthropic"


class OpenAIProvider(_UnimplementedProvider):
    name = "openai"


class GeminiProvider(_UnimplementedProvider):
    name = "gemini"


class OllamaProvider(_UnimplementedProvider):
    name = "ollama"
