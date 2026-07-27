"""Assemble a deterministic project context package from the knowledge repository."""
from __future__ import annotations

from jarvis_core.models.base import NoteType
from jarvis_core.models.context import (
    ConceptItem,
    ContextPackage,
    DecisionItem,
    ResourceItem,
    SessionItem,
    SourceRef,
)
from jarvis_core.models.entities import (
    Concept,
    Decision,
    Project,
    Resource,
    Session,
)
from jarvis_core.models.note import Note
from jarvis_core.relationships.resolver import RelationshipResolver, ResolutionReport

CONTEXT_SCHEMA_VERSION = "context-package/0.1.0"


class ProjectNotFoundError(LookupError):
    """Raised when no project note matches the requested name."""


class ProjectContextLoader:
    """Builds a :class:`ContextPackage` for a named project.

    Determinism: every collection is sorted by a stable key so identical inputs
    always produce identical output.
    """

    def __init__(self, notes: list[Note]) -> None:
        self._notes = notes
        self._resolver = RelationshipResolver(notes)
        self._report: ResolutionReport = self._resolver.resolve_all()
        self._by_relpath = {n.relpath: n for n in notes}

    def _find_project(self, name: str) -> Note:
        target = name.strip().lower()
        candidates = [
            n for n in self._notes if n.type is NoteType.PROJECT
        ]
        # Match by id, title, alias, or filename stem (deterministic by relpath order).
        for note in sorted(candidates, key=lambda n: n.relpath):
            names = {c.strip().lower() for c in note.names()}
            if target in names:
                return note
        raise ProjectNotFoundError(
            f"No project note found matching '{name}'. "
            f"Known projects: {', '.join(self._known_project_names()) or '(none)'}"
        )

    def _known_project_names(self) -> list[str]:
        return sorted(
            {(n.title or n.path.stem) for n in self._notes if n.type is NoteType.PROJECT}
        )

    def _related_notes(self, project: Note) -> list[Note]:
        """Notes related to the project via frontmatter projects[] or dashboard links."""
        related: dict[str, Note] = {}
        project_names = {c.strip().lower() for c in project.names()}

        # 1. Notes that name this project in their `projects` frontmatter.
        for note in self._notes:
            for ref in note.frontmatter_list("projects"):
                cleaned = ref.strip().strip("[]").split("|", 1)[0].split("#", 1)[0].strip().lower()
                if cleaned in project_names:
                    related[note.relpath] = note

        # 2. Notes the dashboard links out to (wikilinks + relationship fields).
        for target_relpath in self._report.outgoing(project.relpath):
            linked = self._by_relpath.get(target_relpath)
            if linked is not None:
                related[linked.relpath] = linked

        related.pop(project.relpath, None)
        return sorted(related.values(), key=lambda n: n.relpath)

    def load(self, name: str) -> ContextPackage:
        """Assemble the context package for the named project."""
        project_note = self._find_project(name)
        project = Project(project_note)
        related = self._related_notes(project_note)

        decisions = sorted(
            (Decision(n) for n in related if n.type is NoteType.DECISION),
            key=lambda d: (d.decision_date or "", d.note.id or "", d.title),
        )
        sessions = sorted(
            (Session(n) for n in related if n.type is NoteType.SESSION_SUMMARY),
            key=lambda s: (s.session_date or "", s.note.id or "", s.title),
            reverse=True,
        )
        resources = sorted(
            (Resource(n) for n in related if n.type is NoteType.RESOURCE),
            key=lambda r: (r.title.lower(), r.note.id or ""),
        )
        concepts = sorted(
            (Concept(n) for n in related if n.type is NoteType.CONCEPT),
            key=lambda c: (c.title.lower(), c.note.id or ""),
        )

        sources = tuple(
            SourceRef(id=n.id, title=(n.title or n.path.stem), relpath=n.relpath)
            for n in sorted([project_note, *related], key=lambda n: n.relpath)
        )

        warnings: list[str] = []
        for n in [project_note, *related]:
            for err in n.parse_errors:
                warnings.append(f"{n.relpath}: {err}")
        if not project.resume:
            warnings.append(f"{project_note.relpath}: no 'Resume here' section found.")

        unresolved = tuple(
            f"{u.reference} (in {u.source}, {u.origin})"
            for u in self._report.unresolved
            if u.source == project_note.relpath or u.source in {n.relpath for n in related}
        )

        return ContextPackage(
            schema_version=CONTEXT_SCHEMA_VERSION,
            project_id=project.note.id,
            project_title=project.name,
            goal=project.goal,
            priority=project.priority,
            current_milestone=project.current_milestone,
            status=project.note.status,
            summary=project.purpose,
            current_status=project.current_state,
            resume=project.resume,
            decisions=tuple(
                DecisionItem(
                    id=d.note.id, title=d.title, decision_date=d.decision_date,
                    status=d.status, relpath=d.note.relpath,
                )
                for d in decisions
            ),
            sessions=tuple(
                SessionItem(
                    id=s.note.id, title=s.title, session_date=s.session_date,
                    provider=s.provider, objective=s.objective, relpath=s.note.relpath,
                )
                for s in sessions
            ),
            resources=tuple(
                ResourceItem(
                    id=r.note.id, title=r.title, resource_type=r.resource_type,
                    source_of_truth=r.source_of_truth, uri=r.uri, relpath=r.note.relpath,
                )
                for r in resources
            ),
            concepts=tuple(
                ConceptItem(id=c.note.id, title=c.title, relpath=c.note.relpath)
                for c in concepts
            ),
            outstanding_questions=project.open_questions(),
            sources=sources,
            warnings=tuple(sorted(set(warnings))),
            unresolved_references=tuple(sorted(set(unresolved))),
        )
