"""Deterministic mock provider. No network, no API keys, no randomness."""
from __future__ import annotations

from jarvis_core.models.context import ContextPackage
from jarvis_core.providers.base import ProviderResponse


class MockProvider:
    """Echoes a deterministic description of the context it received.

    This exists to prove the end-to-end flow without any external dependency. Given
    the same package it always returns the same response.
    """

    name = "mock"

    def summarize(self, package: ContextPackage, model_role: str = "fast") -> ProviderResponse:
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
        summary = (
            f"[mock:{model_role}] Project '{package.project_title}' "
            f"(status={package.status or 'unknown'}, priority={package.priority or 'n/a'}). "
            f"Assembled {counts['decisions']} decision(s), {counts['sessions']} session(s), "
            f"{counts['resources']} resource(s), {counts['concepts']} concept(s); "
            f"{counts['outstanding_questions']} open question(s); "
            f"latest session: {latest_session}. "
            f"Resume: {(package.resume or 'no resume section').strip()[:160]}"
        )
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
