"""Deep immutability helpers for snapshot/approval semantic values (AC-05-01).

``deep_freeze`` returns a deeply read-only view of nested mappings/sequences: mappings become
``MappingProxyType`` (mutation raises ``TypeError``) and lists/tuples become tuples. It copies
as it goes, so a caller that retains the original object cannot mutate a frozen value through
that reference. ``json_default`` lets the canonical serializer emit frozen mappings, and
``deep_thaw`` produces plain dict/list copies for public output.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from types import MappingProxyType


def deep_freeze(value: object) -> object:
    """Return a deeply immutable copy-view of ``value`` (mappings/sequences frozen)."""
    if isinstance(value, MappingProxyType):
        return value
    if isinstance(value, Mapping):
        return MappingProxyType({k: deep_freeze(v) for k, v in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(deep_freeze(v) for v in value)
    return value


def freeze_mapping(value: Mapping[str, object]) -> Mapping[str, object]:
    """Deep-freeze a mapping and return it typed as an immutable mapping."""
    frozen = deep_freeze(dict(value))
    assert isinstance(frozen, MappingProxyType)
    return frozen


def freeze_tuple_of_mappings(
    values: Sequence[Mapping[str, object]],
) -> tuple[Mapping[str, object], ...]:
    """Deep-freeze a sequence of mappings into a tuple of immutable mappings."""
    return tuple(freeze_mapping(v) for v in values)


def json_default(obj: object) -> object:
    """``json.dumps`` default: serialize a frozen mapping as a plain dict."""
    if isinstance(obj, MappingProxyType):
        return dict(obj)
    raise TypeError(f"not serializable: {type(obj).__name__}")


def deep_thaw(value: object) -> object:
    """Return a plain (mutable) dict/list copy for public output surfaces."""
    if isinstance(value, (MappingProxyType, Mapping)):
        return {k: deep_thaw(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [deep_thaw(v) for v in value]
    return value


__all__ = [
    "deep_freeze",
    "deep_thaw",
    "freeze_mapping",
    "freeze_tuple_of_mappings",
    "json_default",
]
