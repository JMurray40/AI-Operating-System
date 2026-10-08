"""AC-05-01 — deep semantic immutability (mutation/alias/integrity)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from jarvis_core.config import Config
from jarvis_core.conversation import ConversationApplication, PrepareTurnRequest, mock_profile
from jarvis_core.conversation import context as ctx
from jarvis_core.conversation.immutable import deep_freeze, freeze_mapping
from jarvis_core.policy import local_allow_all
from jarvis_core.repositories import FileSystemKnowledgeRepository

T = datetime(2026, 8, 1, tzinfo=timezone.utc)


def _snap(selector: str | None = None):  # type: ignore[no-untyped-def]
    repo = FileSystemKnowledgeRepository(Config())
    notes = repo.discover()
    req = PrepareTurnRequest(
        request_id="r",
        session_id="s",
        workspace_id="local",
        scope=local_allow_all(workspace_id="local", max_sensitivity="internal"),
        source_root=Path(repo.root),
        user_text="tell me about it",
        provider_profile=mock_profile(),
        project_selector=selector,
        evaluation_time=T,
    )
    return ctx.prepare(req, notes, focus_titles=("AI Operating System",)).snapshot


# ------------------------------------------------------------------ primitive
def test_deep_freeze_copies_and_blocks_mutation() -> None:
    src = {"a": 1, "n": {"b": 2}, "lst": [1, 2]}
    frozen = freeze_mapping(src)
    with pytest.raises(TypeError):
        frozen["a"] = 9  # type: ignore[index]
    with pytest.raises(TypeError):
        frozen["n"]["b"] = 9  # type: ignore[index]
    assert isinstance(frozen["lst"], tuple)  # sequences become tuples
    src["a"] = 99  # mutate the original: the frozen copy is unaffected
    src["n"]["b"] = 99
    assert frozen["a"] == 1 and frozen["n"]["b"] == 2


def test_deep_freeze_idempotent() -> None:
    # AC-05-01R-2: re-freezing an already-frozen value is idempotent in VALUE (the content is
    # unchanged and still fully immutable) but is deliberately NOT identity-preserving anymore
    # — a MappingProxyType is a read-only VIEW, not a copy, so returning the SAME proxy object
    # here would retain whatever mutable mapping backs it. deep_freeze now always copies, even
    # when the input already presents as a MappingProxyType, so the backing mapping can never
    # be aliased through a "no-op" re-freeze.
    once = deep_freeze({"x": {"y": 1}})
    twice = deep_freeze(once)
    assert twice is not once
    assert twice == once
    assert isinstance(twice, type(once))
    with pytest.raises(TypeError):
        twice["x"]["y"] = 9  # type: ignore[index]


# ------------------------------------------------------------------ snapshot fields
@pytest.mark.parametrize("field", ["budget_accounting", "policy_summary", "authorization_summary"])
def test_snapshot_mapping_fields_are_frozen(field: str) -> None:
    snap = _snap()
    mapping = getattr(snap, field)
    with pytest.raises(TypeError):
        mapping["injected"] = "x"


def test_snapshot_tuple_fields_are_tuples() -> None:
    snap = _snap()
    assert isinstance(snap.assumptions, tuple)
    assert isinstance(snap.safe_omissions, tuple)
    assert isinstance(snap.user_exclusions, tuple)


def test_snapshot_nested_frozen_mapping() -> None:
    snap = _snap(selector="AI Operating System")
    sel = snap.authorization_summary["project_selection"]
    with pytest.raises(TypeError):
        sel["status"] = "tampered"  # type: ignore[index]


def test_snapshot_assumption_records_frozen() -> None:
    snap = _snap()
    # "tell me about it" + a single focus resolves the pronoun to an assumption.
    assert snap.assumptions, "expected a visible reference assumption"
    with pytest.raises(TypeError):
        snap.assumptions[0]["status"] = "x"  # type: ignore[index]


def test_snapshot_verify_integrity_passes_on_clean_snapshot() -> None:
    _snap().verify_integrity()  # does not raise


# ------------------------------------------------------------------ approval
def test_approval_prompt_versions_frozen() -> None:
    app = ConversationApplication()
    s = app.create_session("local", session_id="s")
    repo = FileSystemKnowledgeRepository(Config())
    req = PrepareTurnRequest(
        request_id="r",
        session_id="s",
        workspace_id="local",
        scope=local_allow_all(workspace_id="local", max_sensitivity="internal"),
        source_root=Path(repo.root),
        user_text="summarize the AI Operating System project",
        provider_profile=mock_profile(),
        evaluation_time=T,
    )
    app.prepare_turn(s, req, repo.discover())
    approval = app.approve(s, actor="jason", now=T)
    with pytest.raises(TypeError):
        approval.prompt_versions["prompt_template_version"] = "x"  # type: ignore[index]
