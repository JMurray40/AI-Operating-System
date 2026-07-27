from __future__ import annotations

import json
from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.policy import local_allow_all
from jarvis_core.query import QueryEngine
from jarvis_core.query.contract import CONTRACT_VERSION
from jarvis_core.repositories import FileSystemKnowledgeRepository
from tests.support.synthetic_vault import build_trust_vault_no_dupes


def _engine(path: Path) -> QueryEngine:
    build_trust_vault_no_dupes(path)
    notes = FileSystemKnowledgeRepository(Config(vault_path=path)).discover()
    return QueryEngine(notes, scope=local_allow_all("local", max_sensitivity="restricted"),
                       source_root=path)


def test_answer_carries_contract_version_and_no_confidence(tmp_path: Path):
    ans = _engine(tmp_path).search("alpha")
    d = ans.to_dict()
    assert d["contract_version"] == CONTRACT_VERSION
    assert d["answer_confidence"] is None            # no numeric answer confidence (ADR-0014)
    blob = json.dumps(d)
    assert '"confidence"' not in blob                # ranking is never called confidence
    assert '"relative_relevance"' in blob


def test_trace_has_versioned_fields(tmp_path: Path):
    _, trace = _engine(tmp_path).run("alpha", want_trace=True)
    d = trace.to_dict()
    for key in ("contract_version", "index_version", "request_id",
                "workspace_fingerprint", "authorization", "excluded_count"):
        assert key in d
    assert '"confidence"' not in json.dumps(d)


def test_citation_shape(tmp_path: Path):
    c = _engine(tmp_path).search("alpha").citations[0].to_dict()
    for key in ("source_id", "source_identity_kind", "source_fingerprint",
                "locator", "excerpt", "relative_relevance", "reason", "contract_version"):
        assert key in c
    assert set(c["locator"]) == {"heading_path", "line_start", "line_end"}
