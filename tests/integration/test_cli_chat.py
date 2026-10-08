"""WP3 — `jarvis chat` CLI surface and CLI/API parity (C01, C02; accessibility, exit codes).

Offline; mock adapter only. The Google surface is preparable but not dispatchable in this
build.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from jarvis_core.cli import main
from jarvis_core.config import Config
from jarvis_core.conversation import ConversationApplication, PrepareTurnRequest, mock_profile
from jarvis_core.conversation.contract import ExitCode
from jarvis_core.policy import local_allow_all
from jarvis_core.repositories import FileSystemKnowledgeRepository

_MSG = "summarize the AI Operating System project"
_AS_OF = "2026-08-01T00:00:00+00:00"
_SID = "test-session"


def _chat(capsys: pytest.CaptureFixture[str], *extra: str) -> tuple[int, str]:
    rc = main(["chat", _MSG, "--session-id", _SID, "--as-of", _AS_OF, *extra])
    return rc, capsys.readouterr().out


def test_manifest_prepare_only_exit_success(capsys: pytest.CaptureFixture[str]) -> None:
    rc, out = _chat(capsys, "--format", "json")
    assert rc == int(ExitCode.SUCCESS)
    payload = json.loads(out)
    assert payload["digest"].startswith("sha256:")
    assert "items" in payload


def test_approve_dispatch_mock_completes(capsys: pytest.CaptureFixture[str]) -> None:
    _, out = _chat(capsys, "--format", "json")
    digest = json.loads(out)["digest"]
    rc, out2 = _chat(capsys, "--approve", digest, "--format", "json")
    assert rc == int(ExitCode.SUCCESS)
    result = json.loads(out2)
    assert result["attempt"]["status"] == "completed"
    assert result["turn_number"] == 1


def test_wrong_approve_digest_is_validation_failure(capsys: pytest.CaptureFixture[str]) -> None:
    rc, _ = _chat(capsys, "--approve", "sha256:deadbeef")
    assert rc == int(ExitCode.VALIDATION_FAILED)


def test_google_is_preparable_but_not_dispatchable(capsys: pytest.CaptureFixture[str]) -> None:
    # No credential is wired in the CLI, so a remote destination fails closed at prepare.
    rc = main(["chat", "hi", "--provider", "google", "--session-id", _SID, "--as-of", _AS_OF])
    assert rc == int(ExitCode.PROVIDER_UNAVAILABLE)


def test_text_and_json_have_equivalent_status(capsys: pytest.CaptureFixture[str]) -> None:
    _, out = _chat(capsys, "--format", "json")
    digest = json.loads(out)["digest"]
    _, txt = _chat(capsys, "--approve", digest)  # text
    _, js = _chat(capsys, "--approve", digest, "--format", "json")  # json
    result = json.loads(js)
    assert result["attempt"]["status"] in txt  # 'completed' appears in the text render
    assert result["coverage"] in txt


def test_cli_api_digest_parity(capsys: pytest.CaptureFixture[str]) -> None:
    # C02: the CLI and the in-process API produce the same snapshot for the same inputs.
    repo = FileSystemKnowledgeRepository(Config())
    notes = repo.discover()
    app = ConversationApplication()
    session = app.create_session("local", session_id=_SID)
    req = PrepareTurnRequest(
        request_id="cli-1",
        session_id=_SID,
        workspace_id="local",
        scope=local_allow_all(workspace_id="local", max_sensitivity="internal"),
        source_root=Path(repo.root),
        user_text=_MSG,
        provider_profile=mock_profile(),
        evaluation_time=datetime(2026, 8, 1, tzinfo=timezone.utc),
    )
    api_digest = app.prepare_turn(session, req, notes).digest
    _, out = _chat(capsys, "--format", "json")
    assert json.loads(out)["digest"] == api_digest


def test_message_required_in_scripted_mode(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["chat", "--session-id", _SID])
    assert rc == int(ExitCode.VALIDATION_FAILED)


def test_existing_ask_command_unaffected(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["ask", "what is markdown storage"])
    assert rc == 0
    assert capsys.readouterr().out.strip() != ""
