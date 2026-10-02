from __future__ import annotations

import hashlib
import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from jarvis_core.personal_recall import (
    PERSONAL_RECALL_CONTRACT_VERSION,
    PersonalRecallApplication,
    RecallRequest,
    RecallStatus,
    RecallWorkspaceBinding,
)

ROOTS = ("00 Inbox", "01 Daily Notes", "02 Projects", "03 Areas", "04 Wiki (Resources)")


class Token:
    def __init__(self, value: bool = False) -> None:
        self.value = value

    def is_requested(self) -> bool:
        return self.value


def binding(tmp_path: Path) -> RecallWorkspaceBinding:
    root = tmp_path / "vault"
    root.mkdir()
    for name in ROOTS:
        (root / name).mkdir()
    (root / "02 Projects" / "Aurora.md").write_text(
        "---\nid: recall-demo-aurora\ntitle: Aurora\ntype: project\n---\n"
        " Launch\nAurora launch review is Thursday.\n",
        encoding="utf-8",
    )
    (root / "03 Areas" / "decoy.md").write_text("# Decoy\nforbidden-orchid", encoding="utf-8")
    rules = [
        {
            "pattern": f"{name}/**/*.md",
            "sensitivity": "restricted" if name == "03 Areas" else "private",
        }
        for name in ROOTS
    ]
    policy = tmp_path / "policy.json"
    policy.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "policy_id": "test",
                "policy_version": "1",
                "workspace_id": "workspace",
                "vault_root": str(root),
                "max_sensitivity": "private",
                "rules": rules,
            }
        ),
        encoding="utf-8",
    )
    return RecallWorkspaceBinding(
        "synthetic",
        root,
        policy,
        hashlib.sha256(policy.read_bytes()).hexdigest(),
        "test",
        "1",
        "workspace",
        hashlib.sha256(str(root.resolve()).encode()).hexdigest(),
    )


def test_search_is_retrieve_only_and_scope_bound(tmp_path: Path) -> None:
    app = PersonalRecallApplication(binding(tmp_path))
    session = app.open_session()
    request_1812 = RecallRequest(PERSONAL_RECALL_CONTRACT_VERSION, "r1", "Aurora launch")
    result = app.recall(session, request_1812, Token())
    assert result.status is RecallStatus.COMPLETED
    assert result.resolution == "unresolved" and result.answer_claim == "none"
    assert [item.source_id for item in result.candidates] == ["workspace:id:recall-demo-aurora"]
    assert all(item.sensitivity == "private" for item in result.candidates)


def test_restricted_decoy_is_non_disclosing(tmp_path: Path) -> None:
    app = PersonalRecallApplication(binding(tmp_path))
    request_2355 = RecallRequest(PERSONAL_RECALL_CONTRACT_VERSION, "r1", "forbidden-orchid")
    result = app.recall(app.open_session(), request_2355, Token())
    assert result.status is RecallStatus.COMPLETED
    assert result.candidates == ()


def test_invalid_and_cancelled_requests_fail_closed(tmp_path: Path) -> None:
    app = PersonalRecallApplication(binding(tmp_path))
    session = app.open_session()
    invalid_request = RecallRequest(PERSONAL_RECALL_CONTRACT_VERSION, "bad id", "x")
    invalid = app.recall(session, invalid_request, Token())
    assert invalid.error_code is not None and invalid.candidates == ()
    cancelled_request = RecallRequest(PERSONAL_RECALL_CONTRACT_VERSION, "r2", "Aurora")
    cancelled = app.recall(session, cancelled_request, Token(True))
    assert cancelled.status is RecallStatus.CANCELLED and cancelled.candidates == ()


def test_nested_contract_is_frozen(tmp_path: Path) -> None:
    app = PersonalRecallApplication(binding(tmp_path))
    request_3230 = RecallRequest(PERSONAL_RECALL_CONTRACT_VERSION, "r1", "Aurora")
    result = app.recall(app.open_session(), request_3230, Token())
    with pytest.raises(FrozenInstanceError):
        result.status = RecallStatus.FAILED  # type: ignore[misc]
