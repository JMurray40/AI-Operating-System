"""Typed views over notes for the entities the context loader assembles.

These wrap a :class:`Note` and expose type-specific conveniences. They never copy the
underlying content authority; a note remains the single source of its own data.
"""
from __future__ import annotations

from dataclasses import dataclass

from jarvis_core.models.note import Note


@dataclass(frozen=True)
class Project:
    """A project note (also the project dashboard per ADR-0004)."""

    note: Note

    @property
    def name(self) -> str:
        return self.note.title or self.note.path.stem

    @property
    def goal(self) -> str | None:
        return _s(self.note.frontmatter.get("goal"))

    @property
    def priority(self) -> str | None:
        return _s(self.note.frontmatter.get("priority"))

    @property
    def current_milestone(self) -> str | None:
        return _s(self.note.frontmatter.get("current_milestone"))

    @property
    def purpose(self) -> str | None:
        return self.note.section("Purpose")

    @property
    def resume(self) -> str | None:
        return self.note.section("Resume here")

    @property
    def current_state(self) -> str | None:
        return self.note.section("Current state")

    def open_questions(self) -> tuple[str, ...]:
        return _bullets(self.note.section("Open questions and blockers"))


@dataclass(frozen=True)
class ProjectDashboard:
    """The dashboard reading of a project note: the primary navigation layer."""

    project: Project

    @property
    def note(self) -> Note:
        return self.project.note


@dataclass(frozen=True)
class Decision:
    """A decision note."""

    note: Note

    @property
    def title(self) -> str:
        return self.note.title or self.note.path.stem

    @property
    def decision_date(self) -> str | None:
        return _s(self.note.frontmatter.get("decision_date"))

    @property
    def status(self) -> str | None:
        return self.note.status


@dataclass(frozen=True)
class Session:
    """A session-summary note."""

    note: Note

    @property
    def title(self) -> str:
        return self.note.title or self.note.path.stem

    @property
    def session_date(self) -> str | None:
        return _s(self.note.frontmatter.get("session_date"))

    @property
    def provider(self) -> str | None:
        return _s(self.note.frontmatter.get("provider"))

    @property
    def objective(self) -> str | None:
        return _s(self.note.frontmatter.get("objective")) or self.note.section("Objective")


@dataclass(frozen=True)
class Resource:
    """A resource note referencing an external authority."""

    note: Note

    @property
    def title(self) -> str:
        return self.note.title or self.note.path.stem

    @property
    def resource_type(self) -> str | None:
        return _s(self.note.frontmatter.get("resource_type"))

    @property
    def source_of_truth(self) -> str | None:
        return _s(self.note.frontmatter.get("source_of_truth"))

    @property
    def uri(self) -> str | None:
        return _s(self.note.frontmatter.get("uri")) or _s(self.note.frontmatter.get("local_path"))


@dataclass(frozen=True)
class Concept:
    """A concept note."""

    note: Note

    @property
    def title(self) -> str:
        return self.note.title or self.note.path.stem

    @property
    def definition(self) -> str | None:
        return self.note.section("Definition")


def _s(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _bullets(section: str | None) -> tuple[str, ...]:
    if not section:
        return ()
    out: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        for marker in ("- ", "* ", "+ "):
            if stripped.startswith(marker):
                item = stripped[2:].strip()
                if item and not item.startswith("{{"):
                    out.append(item)
                break
    return tuple(out)
