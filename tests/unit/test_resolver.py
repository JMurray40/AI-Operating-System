from __future__ import annotations

from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.relationships import RelationshipResolver
from jarvis_core.repositories import FileSystemKnowledgeRepository


def _notes(path: Path):
    return FileSystemKnowledgeRepository(Config(vault_path=path)).discover()


def test_resolves_wikilinks_and_reports_unresolved(edge_dir: Path):
    report = RelationshipResolver(_notes(edge_dir)).resolve_all()
    unresolved_refs = {u.reference for u in report.unresolved}
    assert "A Note That Does Not Exist" in unresolved_refs
    assert "Nonexistent Session" in unresolved_refs
    # embed of an existing note resolves
    assert any(e.target_relpath == "Edge Project.md" for e in report.edges)


def test_conflicting_alias_first_by_path_wins(edge_dir: Path):
    resolver = RelationshipResolver(_notes(edge_dir))
    # Conflict A.md sorts before Conflict B.md, so the shared alias resolves to A.
    assert resolver.resolve_target("Shared Alias") == "Conflict A.md"


def test_frontmatter_relationships_resolve(aios_dir: Path):
    report = RelationshipResolver(_notes(aios_dir)).resolve_all()
    dash = "projects/AI Operating System.md"
    incoming = report.incoming(dash)
    # decisions/sessions/resource/concept reference the project in frontmatter
    assert any("decisions/" in s for s in incoming)
    assert any("sessions/" in s for s in incoming)
