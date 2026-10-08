"""AC-05-01R-2 — residual: copy and recursively freeze mapping proxies, not alias them.

Chief-of-Staff Handoff 17 §2. ``deep_freeze`` special-cased an incoming ``MappingProxyType``
as "already frozen" and returned it unchanged. A ``MappingProxyType`` is a read-only VIEW,
not a copy: the proxy object itself rejects writes, but its backing mapping may still be
owned and mutated by the caller, and any such mutation is immediately visible through the
retained proxy. Every mapping input is now treated as an untrusted view — including one that
already presents as a ``MappingProxyType``, at any nesting depth or through multiple layers
of proxy-wrapping-proxy — and is copied into a newly owned mapping with every key AND value
deep-frozen before being retained. These tests prove no alias to any caller-owned backing
mapping survives, in every shape Handoff 17 §2 requires.
"""

from __future__ import annotations

from types import MappingProxyType

import pytest

from jarvis_core.conversation.immutable import deep_freeze, freeze_mapping
from jarvis_core.conversation.snapshot import ContextItem, ContextSnapshot, ProviderPolicy

# ------------------------------------------------------------------ shared snapshot fixture


def _item(**over: object) -> ContextItem:
    base = dict(
        item_id="C1",
        source_id="s1",
        source_identity_kind="note",
        relpath="a.md",
        title="A",
        sensitivity="internal",
        source_fingerprint="fp",
        heading_path=["H1", "H2"],
        line_start=1,
        line_end=2,
        excerpt="excerpt text",
        reason="matched",
        token_count=3,
    )
    base.update(over)
    return ContextItem(**base)  # type: ignore[arg-type]


def _policy(**over: object) -> ProviderPolicy:
    base = dict(
        provider_id="p",
        model_id="m",
        scheme="https",
        host="h",
        path="/x",
        operation="generateContent",
        streaming=False,
        thinking_level="minimal",
        timeout_seconds=1.0,
        automatic_retries=0,
        max_input_tokens=1,
        max_output_tokens=1,
        disabled_features=["tools", "streaming"],
        is_remote=False,
    )
    base.update(over)
    return ProviderPolicy(**base)  # type: ignore[arg-type]


def _base_snapshot_kwargs(budget_accounting: object) -> dict[str, object]:
    from jarvis_core.conversation.snapshot import PromptConstructionVersions

    return dict(
        request_id="r",
        session_id="s",
        workspace_id="w",
        normalized_user_input="hi",
        assumptions=(),
        items=[_item()],
        provider_policy=_policy(),
        prompt_versions=PromptConstructionVersions(output_reserve_value=10),
        policy_summary={},
        authorization_summary={},
        budget_accounting=budget_accounting,
        safe_omissions=(),
        user_exclusions=(),
        price_table_version="v1",
        max_cost_usd_per_request=1.0,
        evaluation_time="2026-08-01T00:00:00+00:00",
    )


# ------------------------------------------------------------------ direct proxy over a
# mutable backing dictionary
def test_direct_proxy_over_mutable_backing_dict_no_alias() -> None:
    backing = {"a": 1}
    proxy = MappingProxyType(backing)
    frozen = deep_freeze(proxy)
    assert isinstance(frozen, MappingProxyType)
    assert frozen is not proxy  # AC-05-01R-2: never the same proxy object
    backing["a"] = 999
    backing["b"] = "injected"
    assert dict(frozen) == {"a": 1}  # unaffected by mutating the backing dict afterward


def test_direct_proxy_is_itself_immutable() -> None:
    frozen = deep_freeze(MappingProxyType({"a": 1}))
    with pytest.raises(TypeError):
        frozen["a"] = 2  # type: ignore[index]


# ------------------------------------------------------------------ proxy nested inside a
# mapping, a sequence, and a snapshot digest-bearing field
def test_proxy_nested_inside_mapping_value_no_alias() -> None:
    inner_backing = {"x": 1}
    outer = {"inner": MappingProxyType(inner_backing)}
    frozen = deep_freeze(outer)
    inner_backing["x"] = 999
    assert dict(frozen["inner"]) == {"x": 1}


def test_proxy_nested_inside_sequence_element_no_alias() -> None:
    inner_backing = {"y": 2}
    outer = [MappingProxyType(inner_backing), "other"]
    frozen = deep_freeze(outer)
    inner_backing["y"] = 999
    assert isinstance(frozen, tuple)
    assert dict(frozen[0]) == {"y": 2}


def test_proxy_nested_inside_snapshot_digest_bearing_field_no_alias() -> None:
    backing = {"context_tokens_used": 10, "items_included": 1}
    proxy = MappingProxyType(backing)
    snap = ContextSnapshot(**_base_snapshot_kwargs(proxy))  # type: ignore[arg-type]
    original_digest = snap.digest
    assert isinstance(snap.budget_accounting, MappingProxyType)
    assert snap.budget_accounting is not proxy
    # Mutate the caller-owned backing dict AFTER construction: the retained field, its
    # canonical serialization, and the already-computed digest must all be unaffected.
    backing["context_tokens_used"] = 999999
    backing["injected"] = "tampered"
    assert dict(snap.budget_accounting) == {"context_tokens_used": 10, "items_included": 1}
    snap.verify_integrity()
    assert snap.digest == original_digest


# ------------------------------------------------------------------ proxy whose backing
# mapping contains nested mutable mappings/sequences
def test_proxy_with_nested_mutable_mapping_and_sequence_no_alias() -> None:
    inner_dict = {"b": 2}
    inner_list = [1, 2]
    backing = {"n": inner_dict, "lst": inner_list}
    proxy = MappingProxyType(backing)
    frozen = deep_freeze(proxy)
    inner_dict["b"] = 999
    inner_list.append(3)
    backing["n"] = {"replaced": True}  # also swap the backing's own top-level reference
    assert dict(frozen["n"]) == {"b": 2}
    assert frozen["lst"] == (1, 2)
    with pytest.raises(TypeError):
        frozen["n"]["b"] = 9  # type: ignore[index]


# ------------------------------------------------------------------ multiple proxy layers
def test_multiple_proxy_layers_no_alias() -> None:
    backing = {"z": 5}
    layer1 = MappingProxyType(backing)
    layer2 = MappingProxyType(layer1)  # a proxy wrapping a proxy: supported by the runtime
    frozen = deep_freeze(layer2)
    assert isinstance(frozen, MappingProxyType)
    backing["z"] = 999
    assert dict(frozen) == {"z": 5}


# ------------------------------------------------------------------ caller mutation after
# freezing cannot change retained semantics, canonical bytes, or digest
def test_caller_mutation_after_freezing_does_not_change_canonical_bytes() -> None:
    from jarvis_core.conversation.snapshot import _canonical_bytes

    backing = {"a": 1, "nested": {"b": 2}}
    proxy = MappingProxyType(backing)
    frozen = deep_freeze({"budget_accounting": proxy})
    payload = {"budget_accounting": frozen["budget_accounting"]}
    before = _canonical_bytes(payload)
    backing["a"] = 999
    backing["nested"]["b"] = 999
    backing["extra"] = "injected"
    after = _canonical_bytes(payload)
    assert before == after


def test_caller_mutation_after_freezing_does_not_change_snapshot_digest() -> None:
    backing: dict[str, object] = {"context_tokens_used": 1}
    snap = ContextSnapshot(**_base_snapshot_kwargs(MappingProxyType(backing)))  # type: ignore[arg-type]
    digest_before = snap.digest
    backing["context_tokens_used"] = 12345
    backing["new_key"] = "tampered"
    snap.verify_integrity()  # recomputes the digest from the retained (unaliased) state
    assert snap.digest == digest_before


# ------------------------------------------------------------------ unsupported keys/values
# still fail closed rather than being stringified or retained
def test_unsupported_value_type_inside_proxy_fails_closed() -> None:
    class Mutable:
        pass

    backing = {"a": Mutable()}
    with pytest.raises(TypeError):
        deep_freeze(MappingProxyType(backing))


def test_unsupported_key_type_fails_closed() -> None:
    class WeirdKey:
        def __hash__(self) -> int:
            return 1

        def __eq__(self, other: object) -> bool:
            return self is other

    with pytest.raises(TypeError):
        deep_freeze({WeirdKey(): "value"})


def test_unsupported_key_type_inside_proxy_fails_closed() -> None:
    class WeirdKey:
        def __hash__(self) -> int:
            return 2

        def __eq__(self, other: object) -> bool:
            return self is other

    backing = {WeirdKey(): "value"}
    with pytest.raises(TypeError):
        deep_freeze(MappingProxyType(backing))


def test_unsupported_key_is_not_silently_stringified() -> None:
    # A prior "stringify unknown keys" fallback would make this pass with a str-keyed result
    # instead of failing; assert the rejection, not a coerced/retained value.
    class WeirdKey:
        def __hash__(self) -> int:
            return 3

        def __eq__(self, other: object) -> bool:
            return self is other

    try:
        result = deep_freeze({WeirdKey(): "value"})
    except TypeError:
        return
    pytest.fail(f"unsupported key type was silently retained/stringified as {result!r}")


def test_freeze_mapping_with_proxy_input_still_type_validates_values() -> None:
    class Mutable:
        pass

    with pytest.raises(TypeError):
        freeze_mapping(MappingProxyType({"a": Mutable()}))
