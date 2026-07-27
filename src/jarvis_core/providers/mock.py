"""Deterministic mock provider. No network, no API keys, no randomness."""
from __future__ import annotations

from collections.abc import Iterator

from jarvis_core.models.context import ContextPackage
from jarvis_core.providers.base import ProviderResponse


class MockProvider:
    """Echoes a deterministic description of the context it received.

    This exists to prove the end-to-end flow without any external dependency. Given
    the same package it always returns the same response. It also supports optional
    streaming (:meth:`stream_summarize`) by chunking that deterministic summary.
    """

    name = "mock"

    def _summary(self, package: ContextPackage, model_role: str) -> str:
        counts = {
            "decisions": len(package.decisions),
            "sessions": len(package.sessions),
            "resources": len(package.resources),
            "concepts": len(package.concepts),
            "outstanding_questions": len(package.outstanding_questions),
            "sources": len(package.sources),
            "unresolved_references": len(package.unresolved_references),
        }
        latest_session = package.sessions[0].title if package.sessions else "none"
        return (
            f"[mock:{model_role}] Project '{package.project_title}' "
            f"(status={package.status or 'unknown'}, priority={package.priority or 'n/a'}). "
            f"Assembled {counts['decisions']} decision(s), {counts['sessions']} session(s), "
            f"{counts['resources']} resource(s), {counts['concepts']} concept(s); "
            f"{counts['outstanding_questions']} open question(s); "
            f"latest session: {latest_session}. "
            f"Resume: {(package.resume or 'no resume section').strip()[:160]}"
        )

    def summarize(self, package: ContextPackage, model_role: str = "fast") -> ProviderResponse:
        summary = self._summary(package, model_role)
        counts = {
            "decisions": len(package.decisions),
            "sessions": len(package.sessions),
            "resources": len(package.resources),
            "concepts": len(package.concepts),
            "outstanding_questions": len(package.outstanding_questions),
            "sources": len(package.sources),
            "unresolved_references": len(package.unresolved_references),
        }
        return ProviderResponse(
            provider=self.name,
            model_role=model_role,
            summary=summary,
            received={
                "schema_version": package.schema_version,
                "project_title": package.project_title,
                "counts": counts,
            },
        )

    def stream_summarize(
        self, package: ContextPackage, model_role: str = "fast"
    ) -> Iterator[str]:
        """Yield the deterministic summary in word-sized deltas."""
        words = self._summary(package, model_role).split(" ")
        for i, word in enumerate(words):
            yield word if i == 0 else " " + word
