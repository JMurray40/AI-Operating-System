from __future__ import annotations

import json
from pathlib import Path

import pytest

from jarvis_core.config import Config
from jarvis_core.identity import DuplicateIdentityError
from jarvis_core.policy import AuthorizationScope, local_allow_all
from jarvis_core.query import QueryEngine
from jarvis_core.repositories import FileSystemKnowledgeRepository
from tests.support.synthetic_vault import build_trust_vault, build_trust_vault_no_dupes

_UNIQUE = "zebrasecret"  # a term that appears ONLY in the restricted note


def _engine(path: Path, scope) -> QueryEngine:
    build_trust_vault_no_dupes(path)
    notes = FileSystemKnowledgeRepository(Config(vault_path=path)).discover()
    return QueryEngine(notes, scope=scope, source_root=path)


def _internal_scope() -> AuthorizationScope:
    return AuthorizationScope(workspace_id="local", max_sensitivity="internal")


def test_restricted_note_excluded_under_internal_ceiling(tmp_path: Path):
    eng = _engine(tmp_path, _internal_scope())
    assert eng.note_by_relpath("Secret.md") is None       # not in authorized view
    assert eng.excluded_count >= 1


def test_unknown_sensitivity_note_excluded(tmp_path: Path):
    eng = _engine(tmp_path, local_allow_all("local"))
    assert eng.note_by_relpath("Bare.md") is None          # no frontmatter -> fail closed


def test_excluded_term_yields_no_results(tmp_path: Path):
    eng = _engine(tmp_path, _internal_scope())
    ans = eng.search(_UNIQUE)
    assert ans.citations == ()                             # restricted content not retrievable


def test_excluded_identity_not_disclosed_in_answer_or_trace(tmp_path: Path):
    # Query an AUTHORIZED term. The restricted note (Secret, a graph neighbour of Alpha)
    # must not leak its identity or its unique content through answer or trace.
    eng = _engine(tmp_path, _internal_scope())
    ans, trace = eng.run("show notes related to Alpha", want_trace=True)
    blob = json.dumps(ans.to_dict()) + json.dumps(trace.to_dict())
    assert _UNIQUE not in blob                              # excluded content withheld
    assert "Secret.md" not in blob                         # excluded relpath withheld
    assert "note-secret" not in blob                       # excluded id withheld
    assert trace.excluded_count >= 1                        # only an aggregate count


def test_restricted_neighbor_not_expanded_into_graph(tmp_path: Path):
    # Alpha (public) links Secret (restricted). Under internal ceiling Secret must not appear
    # as a neighbour in related-to expansion.
    eng = _engine(tmp_path, _internal_scope())
    ans = eng.run("show notes related to Alpha")[0]
    assert all(c.relpath != "Secret.md" for c in ans.citations)


def test_allow_all_includes_restricted(tmp_path: Path):
    eng = _engine(tmp_path, local_allow_all("local", max_sensitivity="restricted"))
    assert eng.note_by_relpath("Secret.md") is not None
    assert any(c.relpath == "Secret.md" for c in eng.search(_UNIQUE).citations)


def test_duplicate_explicit_id_fails_closed(tmp_path: Path):
    build_trust_vault(tmp_path)  # includes Dup1/Dup2 sharing 'dup-id'
    notes = FileSystemKnowledgeRepository(Config(vault_path=tmp_path)).discover()
    with pytest.raises(DuplicateIdentityError):
        QueryEngine(notes, scope=local_allow_all("local"), source_root=tmp_path)


def test_authorization_is_deterministic(tmp_path: Path):
    a = _engine(tmp_path, _internal_scope()).run(_UNIQUE, want_trace=True)[1].to_dict()
    b = _engine(tmp_path, _internal_scope()).run(_UNIQUE, want_trace=True)[1].to_dict()
    a.pop("timings_ms")
    b.pop("timings_ms")
    a["request_id"] = b["request_id"] = "x"  # request id is per-scope
    a["authorization"]["request_id"] = b["authorization"]["request_id"] = "x"
    assert a == b
