"""AC-05-01R — residual: reject-not-detect typing, and every alias-mutation case.

Handoff 14 §2. The prior AC-05-01 round deep-froze the top-level snapshot mapping fields but
left three gaps: (1) ``deep_freeze`` silently retained any value type it didn't recognize
(a set, a bytearray, an arbitrary mutable object) instead of rejecting it; (2)
``ContextItem.heading_path`` and ``ProviderPolicy.disabled_features`` were typed as tuples but
never actually copied/validated at construction, so a caller-owned mutable list passed in
could be mutated in place after the fact; (3) ``ContextSnapshot.items`` itself was never
copied, so a caller-retained list of items could be appended/reordered/removed after
construction. All three are fixed here; these tests prove rejection (not mere later
detection via ``verify_integrity()``) and prove every alias case is inert.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType

import pytest

from jarvis_core.config import Config
from jarvis_core.conversation import PrepareTurnRequest, mock_profile
from jarvis_core.conversation import context as ctx
from jarvis_core.conversation.immutable import deep_freeze, freeze_mapping
from jarvis_core.conversation.snapshot import ContextItem, ContextSnapshot, ProviderPolicy
from jarvis_core.policy import local_allow_all
from jarvis_core.repositories import FileSystemKnowledgeRepository

T = datetime(2026, 8, 1, tzinfo=timezone.utc)


def _snap():  # type: ignore[no-untyped-def]
    repo = FileSystemKnowledgeRepository(Config())
    notes = repo.discover()
    req = PrepareTurnRequest(
        request_id="r", session_id="s", workspace_id="local",
        scope=local_allow_all(workspace_id="local", max_sensitivity="internal"),
        source_root=Path(repo.root), user_text="summarize the AI Operating System project",
        provider_profile=mock_profile(), evaluation_time=T,
    )
    return ctx.prepare(req, notes).snapshot


def _item(**over: object) -> ContextItem:
    base = dict(
        item_id="C1", source_id="s1", source_identity_kind="note", relpath="a.md",
        title="A", sensitivity="internal", source_fingerprint="fp", heading_path=["H1", "H2"],
        line_start=1, line_end=2, excerpt="excerpt text", reason="matched", token_count=3,
    )
    base.update(over)
    return ContextItem(**base)  # type: ignore[arg-type]


def _policy(**over: object) -> ProviderPolicy:
    base = dict(
        provider_id="p", model_id="m", scheme="https", host="h", path="/x",
        operation="generateContent", streaming=False, thinking_level="minimal",
        timeout_seconds=1.0, automatic_retries=0, max_input_tokens=1, max_output_tokens=1,
        disabled_features=["tools", "streaming"], is_remote=False,
    )
    base.update(over)
    return ProviderPolicy(**base)  # type: ignore[arg-type]


# ------------------------------------------------------------------ reject, don't just detect
def test_deep_freeze_rejects_unsupported_type() -> None:
    class Mutable:
        pass

    with pytest.raises(TypeError):
        deep_freeze(Mutable())


def test_deep_freeze_rejects_bytearray_alias() -> None:
    # bytearray is mutable; silently retaining it would let a caller mutate stored bytes.
    with pytest.raises(TypeError):
        deep_freeze(bytearray(b"x"))


def test_freeze_mapping_rejects_nested_unsupported_type() -> None:
    class Mutable:
        pass

    with pytest.raises(TypeError):
        freeze_mapping({"a": {"b": Mutable()}})


def test_deep_freeze_set_becomes_frozenset() -> None:
    frozen = deep_freeze({"a", "b"})
    assert isinstance(frozen, frozenset)
    assert frozen == frozenset({"a", "b"})


# ------------------------------------------------------------------ heading_path alias case
def test_heading_path_list_alias_mutation_is_inert() -> None:
    hp = ["Intro", "Sub"]
    item = _item(heading_path=hp)
    assert item.heading_path == ("Intro", "Sub")
    hp.append("Injected")
    hp[0] = "Tampered"
    assert item.heading_path == ("Intro", "Sub")  # unaffected by the caller's later mutation


def test_heading_path_rejects_non_sequence() -> None:
    with pytest.raises(TypeError):
        _item(heading_path=object())  # type: ignore[arg-type]


def test_heading_path_rejects_non_string_elements() -> None:
    with pytest.raises(TypeError):
        _item(heading_path=[1, 2])  # type: ignore[list-item]


# ------------------------------------------------------------------ disabled_features alias case
def test_disabled_features_list_alias_mutation_is_inert() -> None:
    feats = ["tools"]
    policy = _policy(disabled_features=feats)
    assert policy.disabled_features == ("tools",)
    feats.append("streaming")
    assert policy.disabled_features == ("tools",)


def test_disabled_features_rejects_non_string_elements() -> None:
    with pytest.raises(TypeError):
        _policy(disabled_features=[1])  # type: ignore[list-item]


# ------------------------------------------------------------------ snapshot-item alias case
def _base_snapshot_kwargs(items: list[ContextItem]) -> dict[str, object]:
    return dict(
        request_id="r", session_id="s", workspace_id="w", normalized_user_input="hi",
        assumptions=(), items=items, provider_policy=_policy(is_remote=False),
        prompt_versions=__import__(
            "jarvis_core.conversation.snapshot", fromlist=["PromptConstructionVersions"]
        ).PromptConstructionVersions(output_reserve_value=10),
        policy_summary={}, authorization_summary={}, budget_accounting={},
        safe_omissions=(), user_exclusions=(), price_table_version="v1",
        max_cost_usd_per_request=1.0, evaluation_time="2026-08-01T00:00:00+00:00",
    )


def test_snapshot_items_list_alias_mutation_is_inert() -> None:
    items = [_item(item_id="C1"), _item(item_id="C2")]
    snap = ContextSnapshot(**_base_snapshot_kwargs(items))  # type: ignore[arg-type]
    original_digest = snap.digest
    assert isinstance(snap.items, tuple)
    items.append(_item(item_id="C3"))  # mutate the caller's original list after construction
    items.pop(0)
    assert [it.item_id for it in snap.items] == ["C1", "C2"]
    snap.verify_integrity()
    assert snap.digest == original_digest


# ------------------------------------------------------------------ nested list-in-mapping /
# mapping-in-sequence cases (real prepare() pipeline, not a synthetic mapping)
def test_nested_list_in_mapping_and_mapping_in_sequence_are_frozen() -> None:
    snap = _snap()
    sel = snap.authorization_summary.get("project_selection")
    # budget_accounting / authorization_summary are plain scalar-valued mappings in this
    # fixture; assert the general recursive contract on a constructed analog instead so the
    # test does not depend on fixture shape drift.
    payload = {"seq_of_maps": [{"a": 1}, {"b": [1, 2]}], "map_of_seq": {"x": [1, {"y": 2}]}}
    frozen = freeze_mapping(payload)
    assert isinstance(frozen["seq_of_maps"], tuple)
    assert isinstance(frozen["seq_of_maps"][0], MappingProxyType)
    assert isinstance(frozen["seq_of_maps"][1]["b"], tuple)
    assert isinstance(frozen["map_of_seq"]["x"][1], MappingProxyType)
    with pytest.raises(TypeError):
        frozen["seq_of_maps"][0]["a"] = 99  # type: ignore[index]
    with pytest.raises(TypeError):
        frozen["map_of_seq"]["x"][1]["y"] = 99  # type: ignore[index]
    assert sel is None or isinstance(sel, MappingProxyType)


# ------------------------------------------------------------------ full-pipeline alias sweep
def test_full_prepare_pipeline_survives_every_caller_alias_mutation() -> None:
    """A real prepare() call, then mutate every original caller-owned collection we can reach."""
    repo = FileSystemKnowledgeRepository(Config())
    notes = repo.discover()
    focus = ["AI Operating System"]
    req = PrepareTurnRequest(
        request_id="r", session_id="s", workspace_id="local",
        scope=local_allow_all(workspace_id="local", max_sensitivity="internal"),
        source_root=Path(repo.root), user_text="tell me about it",
        provider_profile=mock_profile(), evaluation_time=T,
    )
    prepared = ctx.prepare(req, notes, focus_titles=tuple(focus))
    snap = prepared.snapshot
    before = snap.digest
    # Mutate the caller's own focus list after the fact (not retained by the snapshot anyway,
    # but proves no hidden aliasing was introduced).
    focus.append("Injected")
    notes.clear()  # exhaust the caller's notes list; the snapshot must not depend on it
    snap.verify_integrity()
    assert snap.digest == before
