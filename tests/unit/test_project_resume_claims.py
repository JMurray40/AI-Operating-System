"""C6: claim-to-current-citation binding + answer coverage (ADR-0020, brief §9).

Binding delegates to the reusable query-layer CitationFactory, so a claim is ``supported``
only when a passage validates against CURRENT bytes. Changed/deleted/unreadable/escaped
sources yield no supported citation and are marked ``incomplete``; a metadata-derived claim
cites the metadata-bearing frontmatter locator, not a body passage.
"""
from __future__ import annotations

from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.policy import local_allow_all
from jarvis_core.project_resume.contract import (
    COVERAGE_COMPLETE,
    COVERAGE_INCOMPLETE,
    COVERAGE_NONE,
    COVERAGE_PARTIAL,
    SUPPORT_INCOMPLETE,
    SUPPORT_SUPPORTED,
)
from jarvis_core.project_resume.evidence import (
    DiscoveredSource,
    bind_source_citation,
    evidence_id_for,
    summarize_coverage,
)
from jarvis_core.query.authorized import build_authorized_view
from jarvis_core.query.evidence import CitationFactory, CurrentSourceResolver
from jarvis_core.query.tokenizer import token_set
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
        "# Alpha\n\n## Current state\n\nThe widget pipeline is green and shipping weekly.\n",
    )
    _write(
        root, "Gamma.md",
        f"id: session-gamma\ntype: session-summary\ntitle: \"Gamma\"\nstatus: active\n"
        f"created: {_DATE}\nupdated: {_DATE}\nsensitivity: internal\n"
        f"session_date: {_DATE}\nprovider: mock\nobjective: \"o\"\nprojects: [Alpha]\n",
        "# Gamma\n\nSession about the Alpha project.\n",
    )


def _harness(root: Path):
    notes = FileSystemKnowledgeRepository(Config(vault_path=root)).discover()
    scope = local_allow_all("local")
    view = build_authorized_view(notes, scope)
    resolver = CurrentSourceResolver(root)
    factory = CitationFactory(view.identities, resolver)
    by_relpath = {n.relpath: n for n in view.notes}
    return view, factory, by_relpath


def _source(view, note, channel: str, reason: str) -> DiscoveredSource:
    ident = view.identities[note.relpath]
    return DiscoveredSource(
        relpath=note.relpath, source_id=ident.source_id,
        source_fingerprint=note.source_fingerprint, channel=channel,
        channel_reason=reason, note=note,
    )


def test_current_source_binds_supported_citation(tmp_path: Path) -> None:
    _vault(tmp_path)
    view, factory, by_relpath = _harness(tmp_path)
    note = by_relpath["Alpha.md"]
    src = _source(view, note, "canonical_project_passage", "canonical")
    terms = token_set("widget pipeline green shipping")
    binding = bind_source_citation(src, factory=factory, evidence_terms=terms)
    assert binding.is_supported
    assert binding.support_state == SUPPORT_SUPPORTED
    assert binding.citation is not None
    assert binding.citation.citation.coverage == "supported"
    assert binding.citation.citation.excerpt  # non-empty passage


def test_changed_source_is_not_supported(tmp_path: Path) -> None:
    _vault(tmp_path)
    view, factory, by_relpath = _harness(tmp_path)
    note = by_relpath["Alpha.md"]
    src = _source(view, note, "canonical_project_passage", "canonical")
    # Mutate the file AFTER discovery: fingerprint no longer matches current bytes.
    (tmp_path / "Alpha.md").write_text("---\nid: project-alpha\n---\n\n# Alpha\n\nrewritten\n",
                                       encoding="utf-8")
    terms = token_set("widget pipeline green shipping")
    binding = bind_source_citation(src, factory=factory, evidence_terms=terms)
    assert not binding.is_supported
    assert binding.support_state == SUPPORT_INCOMPLETE
    assert binding.citation is None  # stale -> no current-valid citation at all


def test_deleted_source_is_not_supported(tmp_path: Path) -> None:
    _vault(tmp_path)
    view, factory, by_relpath = _harness(tmp_path)
    note = by_relpath["Alpha.md"]
    src = _source(view, note, "canonical_project_passage", "canonical")
    (tmp_path / "Alpha.md").unlink()  # deleted after discovery
    binding = bind_source_citation(
        src, factory=factory, evidence_terms=token_set("widget pipeline")
    )
    assert binding.support_state == SUPPORT_INCOMPLETE
    assert binding.citation is None


def test_unreadable_under_resolved_root_is_not_supported(tmp_path: Path) -> None:
    _vault(tmp_path)
    view, _, by_relpath = _harness(tmp_path)
    note = by_relpath["Alpha.md"]
    src = _source(view, note, "canonical_project_passage", "canonical")
    # Bind through a resolver rooted at an EMPTY subdir: the source cannot be read within the
    # confined root (the same fail-closed path that catches escape/missing/unreadable sources).
    empty_root = tmp_path / "confined"
    empty_root.mkdir()
    mis_rooted = CitationFactory(view.identities, CurrentSourceResolver(empty_root))
    binding = bind_source_citation(
        src, factory=mis_rooted, evidence_terms=token_set("widget")
    )
    assert binding.support_state == SUPPORT_INCOMPLETE
    assert binding.citation is None


def test_metadata_claim_cites_frontmatter_locator(tmp_path: Path) -> None:
    _vault(tmp_path)
    view, factory, by_relpath = _harness(tmp_path)
    note = by_relpath["Gamma.md"]
    src = _source(view, note, "typed_project_metadata", "projects metadata references Alpha")
    # The metadata signal (the project name in the `projects:` frontmatter) is the evidence.
    terms = token_set("Alpha")
    binding = bind_source_citation(src, factory=factory, evidence_terms=terms)
    assert binding.is_supported
    # Frontmatter match -> empty heading path (the metadata block, not a body heading).
    assert binding.citation is not None
    assert binding.citation.citation.locator.heading_path == ()


def test_evidence_id_is_stable_and_revision_bound(tmp_path: Path) -> None:
    _vault(tmp_path)
    view, _, by_relpath = _harness(tmp_path)
    note = by_relpath["Alpha.md"]
    src = _source(view, note, "canonical_project_passage", "canonical")
    assert evidence_id_for(src) == evidence_id_for(src)
    assert note.source_fingerprint[:12] in evidence_id_for(src)


def test_incomplete_is_distinct_from_supported() -> None:
    complete = summarize_coverage(supported=3, incomplete=0, conflicting=0)
    partial = summarize_coverage(supported=2, incomplete=1, conflicting=0)
    only_incomplete = summarize_coverage(supported=0, incomplete=2, conflicting=0)
    conflicted = summarize_coverage(supported=2, incomplete=0, conflicting=1)
    empty = summarize_coverage(supported=0, incomplete=0, conflicting=0)
    assert complete.label == COVERAGE_COMPLETE and complete.note is None
    assert partial.label == COVERAGE_PARTIAL and partial.note is not None
    assert only_incomplete.label == COVERAGE_INCOMPLETE
    assert conflicted.label == COVERAGE_PARTIAL  # any conflict is never 'complete'
    assert empty.label == COVERAGE_NONE
