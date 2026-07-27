"""Resolve relationships among notes using wikilinks and frontmatter fields.

Read-only: unresolved references are reported, never repaired. Resolution is by a
stable name index (id, title, aliases, filename stem), case-insensitive.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from jarvis_core.models.base import LinkKind
from jarvis_core.models.note import Note

# Frontmatter fields treated as relationship arrays (KNOWLEDGE_STANDARD.md).
RELATIONSHIP_FIELDS: tuple[str, ...] = (
    "projects",
    "areas",
    "topics",
    "people",
    "organizations",
    "related",
    "decisions",
    "sources",
    "supersedes",
    "superseded_by",
)


@dataclass(frozen=True)
class Edge:
    """A resolved relationship from one note to another."""

    source: str          # source relpath
    target_relpath: str  # resolved target relpath
    origin: str          # 'wikilink' | 'frontmatter:<field>'


@dataclass(frozen=True)
class Unresolved:
    """A reference that did not resolve to any known note."""

    source: str      # source relpath
    reference: str   # raw reference text
    origin: str


@dataclass
class ResolutionReport:
    """The outcome of resolving all relationships across a note set."""

    edges: list[Edge] = field(default_factory=list)
    unresolved: list[Unresolved] = field(default_factory=list)

    def outgoing(self, relpath: str) -> list[str]:
        return sorted({e.target_relpath for e in self.edges if e.source == relpath})

    def incoming(self, relpath: str) -> list[str]:
        return sorted({e.source for e in self.edges if e.target_relpath == relpath})


def _clean_name(value: str) -> str:
    """Strip wikilink decoration/anchors and lowercase for indexing."""
    v = value.strip()
    if v.startswith("[[") and v.endswith("]]"):
        v = v[2:-2]
    v = v.split("|", 1)[0]
    v = v.split("#", 1)[0]
    return v.strip().lower()


class RelationshipResolver:
    """Builds a name index and resolves links/frontmatter relationships."""

    def __init__(self, notes: list[Note]) -> None:
        self._notes = notes
        self._index: dict[str, str] = {}  # name (lower) -> relpath
        for note in notes:
            for name in note.names():
                key = _clean_name(name)
                # First writer wins for determinism; notes are pre-sorted by relpath.
                self._index.setdefault(key, note.relpath)

    def resolve_target(self, reference: str) -> str | None:
        """Return the relpath a reference points to, or None if unresolved."""
        return self._index.get(_clean_name(reference))

    def resolve_all(self) -> ResolutionReport:
        """Resolve every wikilink and frontmatter relationship into a report."""
        report = ResolutionReport()
        for note in self._notes:
            seen: set[tuple[str, str]] = set()

            for link in note.links:
                if link.kind not in (LinkKind.WIKILINK, LinkKind.EMBED):
                    continue  # external markdown/urls are not vault entities
                target = self.resolve_target(link.target)
                pair = ("wikilink", link.target)
                if target:
                    key = (target, "wikilink")
                    if key not in seen:
                        seen.add(key)
                        report.edges.append(
                            Edge(source=note.relpath, target_relpath=target, origin="wikilink")
                        )
                elif pair not in seen:
                    seen.add(pair)
                    report.unresolved.append(
                        Unresolved(source=note.relpath, reference=link.target, origin="wikilink")
                    )

            for field_name in RELATIONSHIP_FIELDS:
                for ref in note.frontmatter_list(field_name):
                    origin = f"frontmatter:{field_name}"
                    target = self.resolve_target(ref)
                    if target:
                        key = (target, origin)
                        if key not in seen:
                            seen.add(key)
                            report.edges.append(
                                Edge(source=note.relpath, target_relpath=target, origin=origin)
                            )
                    else:
                        pair = (origin, ref)
                        if pair not in seen:
                            seen.add(pair)
                            report.unresolved.append(
                                Unresolved(source=note.relpath, reference=ref, origin=origin)
                            )

        report.edges.sort(key=lambda e: (e.source, e.target_relpath, e.origin))
        report.unresolved.sort(key=lambda u: (u.source, u.origin, u.reference))
        return report
