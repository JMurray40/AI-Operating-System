"""The deterministic project context package handed to a provider."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceRef:
    """A stable reference back to a source note."""

    id: str | None
    title: str
    relpath: str

    def to_dict(self) -> dict[str, object]:
        return {"id": self.id, "title": self.title, "relpath": self.relpath}


@dataclass(frozen=True)
class DecisionItem:
    id: str | None
    title: str
    decision_date: str | None
    status: str | None
    relpath: str

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "title": self.title,
            "decision_date": self.decision_date,
            "status": self.status,
            "relpath": self.relpath,
        }


@dataclass(frozen=True)
class SessionItem:
    id: str | None
    title: str
    session_date: str | None
    provider: str | None
    objective: str | None
    relpath: str

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "title": self.title,
            "session_date": self.session_date,
            "provider": self.provider,
            "objective": self.objective,
            "relpath": self.relpath,
        }


@dataclass(frozen=True)
class ResourceItem:
    id: str | None
    title: str
    resource_type: str | None
    source_of_truth: str | None
    uri: str | None
    relpath: str

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "title": self.title,
            "resource_type": self.resource_type,
            "source_of_truth": self.source_of_truth,
            "uri": self.uri,
            "relpath": self.relpath,
        }


@dataclass(frozen=True)
class ConceptItem:
    id: str | None
    title: str
    relpath: str

    def to_dict(self) -> dict[str, object]:
        return {"id": self.id, "title": self.title, "relpath": self.relpath}


@dataclass(frozen=True)
class ContextPackage:
    """A deterministic, structured package describing a project's resumable state.

    Field order and all internal collections are stable so identical inputs produce
    byte-identical serialized output.
    """

    schema_version: str
    project_id: str | None
    project_title: str
    goal: str | None
    priority: str | None
    current_milestone: str | None
    status: str | None
    summary: str | None
    current_status: str | None
    resume: str | None
    decisions: tuple[DecisionItem, ...] = ()
    sessions: tuple[SessionItem, ...] = ()
    resources: tuple[ResourceItem, ...] = ()
    concepts: tuple[ConceptItem, ...] = ()
    outstanding_questions: tuple[str, ...] = ()
    sources: tuple[SourceRef, ...] = ()
    warnings: tuple[str, ...] = ()
    unresolved_references: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        """Serialize to an ordered, JSON-ready dict (no timestamps, no randomness)."""
        return {
            "contract_version": "jarvis.query.v0.3.1",
            "schema_version": self.schema_version,
            "project": {
                "id": self.project_id,
                "title": self.project_title,
                "goal": self.goal,
                "priority": self.priority,
                "current_milestone": self.current_milestone,
                "status": self.status,
            },
            "summary": self.summary,
            "current_status": self.current_status,
            "resume": self.resume,
            "decisions": [d.to_dict() for d in self.decisions],
            "sessions": [s.to_dict() for s in self.sessions],
            "resources": [r.to_dict() for r in self.resources],
            "concepts": [c.to_dict() for c in self.concepts],
            "outstanding_questions": list(self.outstanding_questions),
            "sources": [s.to_dict() for s in self.sources],
            "warnings": list(self.warnings),
            "unresolved_references": list(self.unresolved_references),
        }
