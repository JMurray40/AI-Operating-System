"""C10: assembler orchestration + render + trace (brief §5/§9/§14).

The assembler wires the C5-C9 modules into a frozen, versioned ``ProjectResumeResult`` with a
deterministic status. These tests exercise the happy path, determinism, the ambiguous /
not-found / invalid-identity terminals, authority ordering (accepted outranks draft), retained
conflicts, valid supersession, current-source binding failure, both hard budgets, grant-gated
repository activity, and the text/JSON rendering + trace-safety rules.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.policy import local_allow_all
from jarvis_core.project_resume import (
    assemble,
    build_request,
    exit_code_for,
    render_json,
    render_text,
)
from jarvis_core.project_resume.contract import (
    COVERAGE_INCOMPLETE,
    SECTION_DECISIONS,
    SECTION_REPOSITORY,
    STATUS_AMBIGUOUS,
    STATUS_BUDGET_ERROR,
    STATUS_COMPLETE,
    STATUS_INVALID_IDENTITY,
    STATUS_NOT_FOUND,
    STATUS_PARTIAL,
    SUPPORT_CONFLICTING,
    SUPPORT_SUPPORTED,
)
from jarvis_core.project_resume.repository_activity import (
    CODE_UNAVAILABLE_NO_GIT,
    FixtureRepositoryActivityAdapter,
    RepositoryActivityFixture,
    RepositoryActivityGrant,
    RepositoryActivityUnavailable,
    RepositoryCommitRecord,
)
from jarvis_core.repositories import FileSystemKnowledgeRepository

_DATE = "2026-07-27"
_EVAL = "2026-07-28T00:00:00Z"


def _write(root: Path, fname: str, front: str, body: str) -> None:
    (root / fname).write_text(f"---\n{front}---\n\n{body}\n", encoding="utf-8")


def _notes(root: Path):
    return FileSystemKnowledgeRepository(Config(vault_path=root)).discover()


def _request(root: Path, selector: str = "Alpha", **kw):
    return build_request(
        workspace_id="local",
        project_selector=selector,
        authorization_scope=local_allow_all("local"),
        source_root=root,
        evaluation_time=_EVAL,
        **kw,
    )


def _base_vault(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    _write(
        root, "Alpha.md",
        f'id: project-alpha\ntype: project\ntitle: "Alpha"\nstatus: active\n'
        f"created: {_DATE}\nupdated: {_DATE}\ngoal: g\npriority: high\nsensitivity: internal\n",
        "# Alpha\n\n## Current state\n\nThe Alpha widget pipeline is green and shipping weekly.\n",
    )
    _write(
        root, "Decision.md",
        f'id: decision-one\ntype: decision\ntitle: "Adopt widgets"\nstatus: accepted\n'
        f"created: {_DATE}\nupdated: {_DATE}\nsensitivity: internal\ndecision_date: {_DATE}\n"
        "projects: [Alpha]\n",
        "# Adopt widgets\n\nWe will adopt the Alpha widget pipeline for shipping.\n",
    )
    _write(
        root, "Gamma.md",
        f'id: session-gamma\ntype: session-summary\ntitle: "Gamma"\nstatus: active\n'
        f"created: {_DATE}\nupdated: {_DATE}\nsensitivity: internal\nsession_date: {_DATE}\n"
        "provider: mock\nobjective: o\nprojects: [Alpha]\n",
        "# Gamma\n\nSession about the Alpha widget pipeline.\n",
    )


# ---------------------------------------------------------------- happy path


def test_complete_selection_with_sections_and_citations(tmp_path: Path) -> None:
    _base_vault(tmp_path)
    result = assemble(_notes(tmp_path), _request(tmp_path))
    assert result.status == STATUS_COMPLETE
    assert result.project_identity is not None
    assert result.project_identity.title == "Alpha"
    assert len(result.sections) == 10  # exactly the ten fixed sections, in order
    assert result.coverage.supported >= 1
    assert result.citations  # at least one validated passage-and-revision citation
    # Every non-repository citation is a validated vault passage.
    assert all(c.citation.coverage in ("supported", "incomplete") for c in result.citations)


def test_structured_result_is_deterministic_excluding_trace_timings(tmp_path: Path) -> None:
    _base_vault(tmp_path)
    req = _request(tmp_path, trace_requested=True)
    notes = _notes(tmp_path)
    a = json.loads(render_json(assemble(notes, req)))
    b = json.loads(render_json(assemble(notes, req)))
    a.pop("trace")
    b.pop("trace")
    assert a == b  # selection + citations are byte-identical for identical inputs (A8)


def test_trace_carries_required_provenance_and_hides_candidates(tmp_path: Path) -> None:
    _base_vault(tmp_path)
    result = assemble(_notes(tmp_path), _request(tmp_path, trace_requested=True))
    trace = result.trace
    assert trace is not None
    assert trace["request_id"] == result.request_id
    assert str(trace["workspace_fingerprint"]).startswith("sha256:")
    assert trace["contract_version"] and trace["index_version"]
    assert "candidates" not in trace  # rejected ambiguity candidates are never traced
    assert "timings_ms" in trace  # timing is isolated in its own field


# ---------------------------------------------------------------- terminals


def test_not_found_does_not_substitute(tmp_path: Path) -> None:
    _base_vault(tmp_path)
    result = assemble(_notes(tmp_path), _request(tmp_path, selector="Nonexistent"))
    assert result.status == STATUS_NOT_FOUND
    assert result.project_identity is None
    assert exit_code_for(result.status) == 4


def test_ambiguous_presents_candidates_without_choosing(tmp_path: Path) -> None:
    tmp_path.mkdir(parents=True, exist_ok=True)
    _write(
        tmp_path, "A1.md",
        f'id: project-a1\ntype: project\ntitle: "Alpha"\nstatus: active\n'
        f"created: {_DATE}\nupdated: {_DATE}\ngoal: g\npriority: high\nsensitivity: internal\n",
        "# Alpha one\n",
    )
    _write(
        tmp_path, "A2.md",
        f'id: project-a2\ntype: project\ntitle: "Alpha"\nstatus: active\n'
        f"created: {_DATE}\nupdated: {_DATE}\ngoal: g\npriority: high\nsensitivity: internal\n",
        "# Alpha two\n",
    )
    result = assemble(_notes(tmp_path), _request(tmp_path, selector="Alpha"))
    assert result.status == STATUS_AMBIGUOUS
    assert len(result.candidates) == 2
    assert result.project_identity is None
    assert exit_code_for(result.status) == 3


def test_duplicate_identity_fails_closed(tmp_path: Path) -> None:
    tmp_path.mkdir(parents=True, exist_ok=True)
    for fname in ("D1.md", "D2.md"):
        _write(
            tmp_path, fname,
            f'id: project-alpha\ntype: project\ntitle: "Alpha {fname}"\nstatus: active\n'
            f"created: {_DATE}\nupdated: {_DATE}\ngoal: g\npriority: high\nsensitivity: internal\n",
            "# dup\n",
        )
    result = assemble(_notes(tmp_path), _request(tmp_path, selector="project-alpha"))
    assert result.status == STATUS_INVALID_IDENTITY
    assert result.project_identity is None


# ---------------------------------------------------------------- authority + conflict


def test_accepted_decision_outranks_draft_without_conflict(tmp_path: Path) -> None:
    _base_vault(tmp_path)
    _write(
        tmp_path, "Draft.md",
        f'id: decision-draft\ntype: decision\ntitle: "Draft widget idea"\nstatus: draft\n'
        f"created: {_DATE}\nupdated: {_DATE}\nsensitivity: internal\nprojects: [Alpha]\n",
        "# Draft widget idea\n\nMaybe change the Alpha widget pipeline later.\n",
    )
    result = assemble(_notes(tmp_path), _request(tmp_path))
    decisions = next(s for s in result.sections if s.key == SECTION_DECISIONS)
    classes = [c.authority_class for c in decisions.claims]
    assert "accepted_decision" in classes and "draft" in classes
    # Accepted is ordered strictly before the draft, and nothing is marked conflicting.
    assert classes.index("accepted_decision") < classes.index("draft")
    assert not result.conflicts


def test_two_accepted_decisions_conflict_and_degrade_status(tmp_path: Path) -> None:
    _base_vault(tmp_path)
    _write(
        tmp_path, "Decision2.md",
        f'id: decision-two\ntype: decision\ntitle: "Adopt gadgets"\nstatus: accepted\n'
        f"created: {_DATE}\nupdated: {_DATE}\nsensitivity: internal\ndecision_date: {_DATE}\n"
        "projects: [Alpha]\n",
        "# Adopt gadgets\n\nWe will adopt the Alpha widget pipeline differently.\n",
    )
    result = assemble(_notes(tmp_path), _request(tmp_path))
    assert result.conflicts, "two same-class supported decisions must be retained as a conflict"
    assert result.status == STATUS_PARTIAL
    conflicting = [
        c for s in result.sections for c in s.claims if c.support_state == SUPPORT_CONFLICTING
    ]
    assert len(conflicting) >= 2


def test_valid_supersession_resolves_conflict(tmp_path: Path) -> None:
    _base_vault(tmp_path)
    _write(
        tmp_path, "Decision2.md",
        f'id: decision-two\ntype: decision\ntitle: "Adopt gadgets"\nstatus: accepted\n'
        f"created: {_DATE}\nupdated: {_DATE}\nsensitivity: internal\ndecision_date: {_DATE}\n"
        "projects: [Alpha]\nsupersedes: [decision-one]\n",
        "# Adopt gadgets\n\nWe will adopt the Alpha widget pipeline differently.\n",
    )
    result = assemble(_notes(tmp_path), _request(tmp_path))
    assert not result.conflicts  # explicit supersession removes the older decision from contention


def test_binding_failure_marks_claims_incomplete(tmp_path: Path) -> None:
    _base_vault(tmp_path)
    empty_root = tmp_path / "confined"
    empty_root.mkdir()
    # source_root points at an empty dir: no source validates against current bytes, so every
    # claim falls back to incomplete and nothing is presented as supported.
    result = assemble(_notes(tmp_path), _request(empty_root, selector="Alpha"))
    # Selection still succeeds (identity is not a current-bytes claim); briefing is unsupported.
    assert result.status == STATUS_PARTIAL
    assert result.coverage.label == COVERAGE_INCOMPLETE
    supported = [
        c for s in result.sections for c in s.claims if c.support_state == SUPPORT_SUPPORTED
    ]
    assert not supported
    assert not result.citations


# ---------------------------------------------------------------- budgets


def test_output_budget_too_small_fails_closed(tmp_path: Path) -> None:
    _base_vault(tmp_path)
    result = assemble(
        _notes(tmp_path),
        _request(tmp_path, evidence_token_budget=256, output_token_budget=256),
    )
    assert result.status == STATUS_BUDGET_ERROR
    assert exit_code_for(result.status) == 7
    assert all(not s.claims for s in result.sections)  # no claim severed mid-citation


def test_mid_output_budget_sheds_claims_to_partial(tmp_path: Path) -> None:
    _base_vault(tmp_path)
    notes = _notes(tmp_path)
    full = assemble(notes, _request(tmp_path))
    full_claims = sum(len(s.claims) for s in full.sections)
    # A budget just under the full serialization (measured in the same word-count the estimator
    # uses) must shed the lowest-priority claim(s) rather than emit an over-budget result.
    full_tokens = len(render_json(full).split())
    budget = max(256, full_tokens - 40)
    tight = assemble(notes, _request(tmp_path, output_token_budget=budget))
    tight_claims = sum(len(s.claims) for s in tight.sections)
    assert tight_claims < full_claims
    assert tight.status == STATUS_PARTIAL
    assert any(o.reason == "output budget reached" for o in tight.omissions)


# ---------------------------------------------------------------- repository activity


def _grant(project_id: str, repo_root: Path) -> RepositoryActivityGrant:
    return RepositoryActivityGrant(
        workspace_id="local", project_id=project_id, repository_root=repo_root, max_records=10
    )


def _adapter(repo_root: Path, records, *, forced=None) -> FixtureRepositoryActivityAdapter:
    fixture = RepositoryActivityFixture(
        repository_id="repo-alpha", head_object_id="a" * 40,
        records=tuple(records), forced_outcome=forced,
    )
    return FixtureRepositoryActivityAdapter({str(repo_root): fixture})


def test_granted_repository_activity_emits_revision_citations(tmp_path: Path) -> None:
    _base_vault(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    ident = assemble(_notes(tmp_path), _request(tmp_path)).project_identity
    assert ident is not None
    records = [
        RepositoryCommitRecord("c" * 40, "2026-07-27T10:00:00+00:00", "Dev", "Ship widget"),
        RepositoryCommitRecord("d" * 40, "2026-07-26T10:00:00+00:00", "Dev", "Fix pipeline"),
    ]
    req = _request(tmp_path, repository_activity_grant=_grant(ident.source_id, repo_root))
    result = assemble(_notes(tmp_path), req, repository_port=_adapter(repo_root, records))
    assert result.repository_citations
    assert all(rc.head_object_id == "a" * 40 for rc in result.repository_citations)
    repo_section = next(s for s in result.sections if s.key == SECTION_REPOSITORY)
    assert repo_section.claims  # activity surfaced as supported, revision-bound claims


def test_repository_denied_without_grant_leaves_section_empty(tmp_path: Path) -> None:
    _base_vault(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    records = [RepositoryCommitRecord("c" * 40, "2026-07-27T10:00:00+00:00", "Dev", "Ship")]
    # No grant on the request -> the port is never consulted; no repository evidence appears.
    result = assemble(
        _notes(tmp_path), _request(tmp_path), repository_port=_adapter(repo_root, records)
    )
    assert not result.repository_citations
    repo_section = next(s for s in result.sections if s.key == SECTION_REPOSITORY)
    assert not repo_section.claims


def test_repository_degradation_becomes_a_limitation(tmp_path: Path) -> None:
    _base_vault(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    ident = assemble(_notes(tmp_path), _request(tmp_path)).project_identity
    assert ident is not None
    forced = RepositoryActivityUnavailable(CODE_UNAVAILABLE_NO_GIT, "no git")
    req = _request(tmp_path, repository_activity_grant=_grant(ident.source_id, repo_root))
    result = assemble(_notes(tmp_path), req, repository_port=_adapter(repo_root, [], forced=forced))
    assert not result.repository_citations
    assert any(limit.code == CODE_UNAVAILABLE_NO_GIT for limit in result.limitations)


# ---------------------------------------------------------------- rendering


def test_text_render_distinguishes_supported_and_never_shows_zero_locator(tmp_path: Path) -> None:
    _base_vault(tmp_path)
    result = assemble(_notes(tmp_path), _request(tmp_path))
    text = render_text(result)
    assert "== PROJECT RESUME ==" in text
    assert "[supported]" in text
    assert "L0-L0" not in text  # an incomplete reference is never rendered as a passage locator
    # Empty content sections state the neutral note rather than asserting none exist.
    assert "no supported evidence available" in text


def test_render_incomplete_reference_is_visibly_distinct(tmp_path: Path) -> None:
    _base_vault(tmp_path)
    empty_root = tmp_path / "confined"
    empty_root.mkdir()
    result = assemble(_notes(tmp_path), _request(empty_root, selector="Alpha"))
    text = render_text(result)
    assert "unverified" in text  # incomplete references are labelled distinctly from supported
    assert "[supported]" not in text
    assert "L0-L0" not in text


def test_utc_evaluation_time_is_explicit_not_wall_clock(tmp_path: Path) -> None:
    _base_vault(tmp_path)
    req = _request(tmp_path, trace_requested=True)
    # The evaluation time echoed in the trace is exactly the explicit request input.
    result = assemble(_notes(tmp_path), req)
    assert result.trace is not None
    expected = datetime(2026, 7, 28, tzinfo=timezone.utc).isoformat()
    assert result.trace["evaluation_time"] == expected
