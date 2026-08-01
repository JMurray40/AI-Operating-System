"""C4: evidence discovery channels, dedup, cycle/bounds handling (ADR-0015/0016, §8)."""
from __future__ import annotations

from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.policy import local_allow_all
from jarvis_core.project_resume.contract import (
    CHANNEL_CANONICAL,
    CHANNEL_METADATA,
    CHANNEL_RELATIONSHIP,
)
from jarvis_core.project_resume.evidence import DiscoveryBounds, discover_evidence
from jarvis_core.project_resume.identity import resolve_project
from jarvis_core.query.authorized import build_authorized_view
from jarvis_core.query.index import LexicalIndex
from jarvis_core.query.ranking import Ranker
from jarvis_core.relationships.resolver import RelationshipResolver
from jarvis_core.repositories import FileSystemKnowledgeRepository

_DATE = "2026-07-27"


def _write(root: Path, fname: str, front: str, body: str) -> None:
    (root / fname).write_text(f"---\n{front}---\n\n{body}\n", encoding="utf-8")


def _vault(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    _write(
        root, "Alpha.md",
        f"id: project-alpha\ntype: project\ntitle: \"Alpha\"\nstatus: active\n"
        f"created: {_DATE}\nupdated: {_DATE}\ngoal: \"g\"\npriority: high\nsensitivity: internal\n",
        "# Alpha\n\n## Links\n\nWork with [[Beta]].\n",
    )
    _write(
        root, "Beta.md",
        f"id: concept-beta\ntype: concept\ntitle: \"Beta\"\nstatus: active\n"
        f"created: {_DATE}\nupdated: {_DATE}\nsensitivity: internal\n",
        "# Beta\n\nBeta links back to [[Alpha]].\n",  # mutual link -> cycle guard
    )
    _write(
        root, "Gamma.md",
        f"id: session-gamma\ntype: session-summary\ntitle: \"Gamma\"\nstatus: active\n"
        f"created: {_DATE}\nupdated: {_DATE}\nsensitivity: internal\n"
        f"session_date: {_DATE}\nprovider: mock\nobjective: \"o\"\nprojects: [Alpha]\n",
        "# Gamma\n\nSession about the Alpha project.\n",
    )
    _write(
        root, "Delta.md",
        f"id: concept-delta\ntype: concept\ntitle: \"Delta\"\nstatus: active\n"
        f"created: {_DATE}\nupdated: {_DATE}\nsensitivity: internal\n",
        "# Delta\n\nUnrelated content about widgets.\n",
    )


def _harness(root: Path, bounds: DiscoveryBounds | None = None):
    notes = FileSystemKnowledgeRepository(Config(vault_path=root)).discover()
    scope = local_allow_all("local")
    view = build_authorized_view(notes, scope)
    report = RelationshipResolver(view.notes).resolve_all()
    index = LexicalIndex(view.notes)
    ranker = Ranker(index, report)
    sel = resolve_project(notes, scope, "Alpha")
    project_note = next(n for n in view.notes if n.relpath == sel.identity.relpath)
    return discover_evidence(
        view=view, report=report, index=index, ranker=ranker,
        project_note=project_note, project_identity=sel.identity, bounds=bounds,
    )


def test_canonical_channel_is_the_project_note(tmp_path: Path):
    _vault(tmp_path)
    res = _harness(tmp_path)
    canonical = [s for s in res.sources if s.channel == CHANNEL_CANONICAL]
    assert [s.relpath for s in canonical] == ["Alpha.md"]


def test_metadata_channel_resolves_projects_field(tmp_path: Path):
    _vault(tmp_path)
    res = _harness(tmp_path)
    meta = {s.relpath for s in res.sources if s.channel == CHANNEL_METADATA}
    assert "Gamma.md" in meta


def test_relationship_channel_includes_linked_note(tmp_path: Path):
    _vault(tmp_path)
    res = _harness(tmp_path)
    rel = {s.relpath for s in res.sources if s.channel == CHANNEL_RELATIONSHIP}
    assert "Beta.md" in rel


def test_sources_are_deduplicated_by_identity(tmp_path: Path):
    _vault(tmp_path)
    res = _harness(tmp_path)
    relpaths = [s.relpath for s in res.sources]
    assert len(relpaths) == len(set(relpaths))  # no note appears twice
    # Each dedup key (source_id, fingerprint) is unique.
    keys = [(s.source_id, s.source_fingerprint) for s in res.sources]
    assert len(keys) == len(set(keys))


def test_cycle_between_project_and_neighbour_terminates(tmp_path: Path):
    _vault(tmp_path)
    # Alpha <-> Beta are mutually linked; discovery must terminate and not duplicate.
    res = _harness(tmp_path)
    assert [s.relpath for s in res.sources].count("Beta.md") == 1


def test_channel_cap_reports_omission(tmp_path: Path):
    _vault(tmp_path)
    # Force a channel to overflow a tiny cap and record an omission.
    bounds = DiscoveryBounds(max_sources_per_channel=1, max_total_candidates=100)
    res = _harness(tmp_path, bounds=bounds)
    assert any(o.reason == "channel source cap reached" for o in res.omissions)
