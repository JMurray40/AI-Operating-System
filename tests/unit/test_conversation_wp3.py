"""WP3 supplemental acceptance coverage — C17 (metadata evidence) and C21 (retry/drift)."""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

from jarvis_core.config import Config
from jarvis_core.conversation import ConversationApplication, PrepareTurnRequest, mock_profile
from jarvis_core.conversation.contract import DriftError, EvidenceType
from jarvis_core.policy import local_allow_all
from jarvis_core.providers.conversation import MockConversationProvider, TerminalState
from jarvis_core.repositories import FileSystemKnowledgeRepository

T = datetime(2026, 8, 1, tzinfo=timezone.utc)
_MSG = "summarize the AI Operating System project"


def _req(session_id: str, root: Path) -> PrepareTurnRequest:
    return PrepareTurnRequest(
        request_id="r1",
        session_id=session_id,
        workspace_id="local",
        scope=local_allow_all(workspace_id="local", max_sensitivity="internal"),
        source_root=root,
        user_text=_MSG,
        provider_profile=mock_profile(),
        evaluation_time=T,
    )


def _vault(tmp_path: Path) -> tuple[list, Path]:
    src = Path(FileSystemKnowledgeRepository(Config()).root)
    dst = tmp_path / "vault"
    shutil.copytree(src, dst)
    return FileSystemKnowledgeRepository(Config(vault_path=dst)).discover(), dst


def test_c17_metadata_claim_binds_current_metadata_evidence(tmp_path: Path) -> None:
    notes, root = _vault(tmp_path)
    app = ConversationApplication()
    s = app.create_session("local")
    snap = app.prepare_turn(s, _req(s.session_id, root), notes)
    # A frontmatter-derived excerpt is a valid, current-byte-validated citation target.
    fm_item = next((it for it in snap.items if "---" in it.excerpt or ":" in it.excerpt), None)
    assert fm_item is not None
    app.approve(s, actor="jason", now=T)
    res = app.dispatch_turn(
        s, MockConversationProvider(reply=f"Metadata says so. [{fm_item.item_id}]"), now=T
    )
    assert res.attempt.status is TerminalState.COMPLETED
    facts = [c for c in res.attempt.evidence.claims if c.evidence_type is EvidenceType.FACT]
    assert any(fm_item.item_id in c.citations for c in facts)


def test_c21_exact_retry_reuses_snapshot_new_attempt(tmp_path: Path) -> None:
    notes, root = _vault(tmp_path)
    app = ConversationApplication()
    s = app.create_session("local")
    snap = app.prepare_turn(s, _req(s.session_id, root), notes)
    app.approve(s, actor="jason", now=T)
    first = app.dispatch_turn(s, MockConversationProvider(reply="a [C1]"), now=T)
    retry = app.retry_attempt(s, MockConversationProvider(reply="a [C1]"), now=T)
    assert retry.snapshot_digest == snap.digest == first.snapshot_digest
    assert retry.attempt.attempt_id != first.attempt.attempt_id


def test_c21_drift_blocks_retry(tmp_path: Path) -> None:
    notes, root = _vault(tmp_path)
    app = ConversationApplication()
    s = app.create_session("local")
    snap = app.prepare_turn(s, _req(s.session_id, root), notes)
    app.approve(s, actor="jason", now=T)
    app.dispatch_turn(s, MockConversationProvider(reply="a [C1]"), now=T)
    target = root / snap.items[0].relpath
    target.write_bytes(target.read_bytes() + b"\n\ndrift after first attempt\n")
    with pytest.raises(DriftError):
        app.retry_attempt(s, MockConversationProvider(reply="a [C1]"), now=T)
