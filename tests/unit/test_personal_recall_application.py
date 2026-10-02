from __future__ import annotations

import hashlib
import json
import os
import subprocess
import threading
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from jarvis_core.personal_recall import (
    PERSONAL_RECALL_CONTRACT_VERSION,
    PersonalRecallApplication,
    RecallCandidate,
    RecallErrorCode,
    RecallLocator,
    RecallRequest,
    RecallStatus,
    RecallWorkspaceBinding,
)
from jarvis_core.personal_recall.corpus import inventory_sources
from jarvis_core.personal_recall.policy import load_policy
from jarvis_core.policy.errors import PolicyError

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
        "# Launch\nAurora launch review is Thursday.\n",
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
    result = app.recall(
        session, RecallRequest(PERSONAL_RECALL_CONTRACT_VERSION, "r1", "Aurora launch"), Token()
    )
    assert result.status is RecallStatus.COMPLETED
    assert result.resolution == "unresolved" and result.answer_claim == "none"
    assert [item.source_id for item in result.candidates] == ["workspace:id:recall-demo-aurora"]
    assert all(item.sensitivity == "private" for item in result.candidates)


def test_restricted_decoy_is_non_disclosing(tmp_path: Path) -> None:
    app = PersonalRecallApplication(binding(tmp_path))
    result = app.recall(
        app.open_session(),
        RecallRequest(PERSONAL_RECALL_CONTRACT_VERSION, "r1", "forbidden-orchid"),
        Token(),
    )
    assert result.status is RecallStatus.COMPLETED
    assert result.candidates == ()


def test_invalid_and_cancelled_requests_fail_closed(tmp_path: Path) -> None:
    app = PersonalRecallApplication(binding(tmp_path))
    session = app.open_session()
    invalid = app.recall(
        session, RecallRequest(PERSONAL_RECALL_CONTRACT_VERSION, "bad id", "x"), Token()
    )
    assert invalid.error_code is RecallErrorCode.INVALID_REQUEST and invalid.candidates == ()
    cancelled = app.recall(
        session, RecallRequest(PERSONAL_RECALL_CONTRACT_VERSION, "r2", "Aurora"), Token(True)
    )
    assert cancelled.status is RecallStatus.CANCELLED and cancelled.candidates == ()


def test_nested_contract_is_frozen(tmp_path: Path) -> None:
    app = PersonalRecallApplication(binding(tmp_path))
    result = app.recall(
        app.open_session(), RecallRequest(PERSONAL_RECALL_CONTRACT_VERSION, "r1", "Aurora"), Token()
    )
    with pytest.raises(FrozenInstanceError):
        result.status = RecallStatus.FAILED  # type: ignore[misc]


def test_closed_candidate_rejects_probe_values() -> None:
    with pytest.raises(ValueError):
        RecallCandidate(
            1,
            "",
            "forged",
            "title",
            "C:secret.md",
            "private",
            "not-a-fingerprint",
            RecallLocator(["Launch"], 1, 1),
            "excerpt",
            1,
            "reason",
            "bogus",
        )


def test_heading_path_is_immutable() -> None:
    locator = RecallLocator(("Launch",), 1, 1)
    with pytest.raises(TypeError):
        locator.heading_path[0] = "changed"  # type: ignore[index]


def test_session_ceiling_is_eight(tmp_path: Path) -> None:
    app = PersonalRecallApplication(binding(tmp_path))
    for _ in range(8):
        app.open_session()
    with pytest.raises(RuntimeError):
        app.open_session()


def test_cancel_publication_has_one_winner(tmp_path: Path) -> None:
    app = PersonalRecallApplication(binding(tmp_path))
    session = app.open_session()
    entered = threading.Event()
    release = threading.Event()
    original = inventory_sources

    def blocked(*args: object, **kwargs: object):
        entered.set()
        assert release.wait(2)
        return original(*args, **kwargs)  # type: ignore[arg-type]

    request = RecallRequest(PERSONAL_RECALL_CONTRACT_VERSION, "race", "Aurora")
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr("jarvis_core.personal_recall.application.inventory_sources", blocked)
        worker = threading.Thread(target=app.recall, args=(session, request, Token()))
        worker.start()
        assert entered.wait(2)
        requested = app.cancel(session, "race")
        release.set()
        worker.join(2)
    assert requested.status.value == "requested"
    assert app.cancel(session, "race").status.value == "already_terminal"


def test_walk_entry_budget_fails_closed(tmp_path: Path) -> None:
    bound = binding(tmp_path)
    policy = load_policy(bound.policy_path)
    with pytest.raises(PolicyError, match="resource_limit"):
        inventory_sources(policy, max_files=1)
    for index in range(3):
        (bound.fixture_root / "00 Inbox" / f"n{index}.md").write_text("# n\n", encoding="utf-8")
    with pytest.raises(PolicyError, match="resource_limit"):
        inventory_sources(policy, max_files=1)


def test_growing_file_read_stops_at_cap(tmp_path: Path) -> None:
    bound = binding(tmp_path)
    target = bound.fixture_root / "02 Projects" / "Aurora.md"
    target.write_bytes(b"x" * 100)
    policy = load_policy(bound.policy_path)
    with pytest.raises(PolicyError, match="resource_limit"):
        inventory_sources(policy, max_file_bytes=10)


def test_windows_junction_is_rejected(tmp_path: Path) -> None:
    if os.name != "nt":
        pytest.skip("native Windows junction coverage")
    bound = binding(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "escaped.md").write_text("# Escaped\nsecret-canary\n", encoding="utf-8")
    link = bound.fixture_root / "00 Inbox" / "linked"
    completed = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link), str(outside)],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        pytest.fail(completed.stderr or completed.stdout)
    policy = load_policy(bound.policy_path)
    with pytest.raises(PolicyError, match="reparse"):
        inventory_sources(policy)
