"""Deep immutability helpers for snapshot/approval semantic values (AC-05-01R).

``deep_freeze`` returns a deeply read-only view of nested mappings/sequences/set-like values:
mappings become ``MappingProxyType`` (mutation raises ``TypeError``), lists/tuples become
tuples, and sets/frozensets become frozensets. It copies as it goes, so a caller that retains
the original object cannot mutate a frozen value through that reference.

AC-05-01R requires runtime validation to REJECT unsupported value types rather than silently
retaining a mutable object whose later mutation is merely detected by
``ContextSnapshot.verify_integrity()`` after the fact. Only known-immutable scalars (``str``,
``int``, ``float``, ``bool``, ``bytes``, ``None``, ``Enum`` members) and the recognized
container shapes above are accepted; anything else (a plain object, a ``bytearray``, a custom
mutable type, ...) raises ``TypeError`` at the freeze boundary, before it can ever be retained.
Digest recomputation via ``verify_integrity()`` remains required as defense in depth, not as
the primary control.

``json_default`` lets the canonical serializer emit frozen mappings/frozensets, and
``deep_thaw`` produces plain dict/list copies for public output.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence, Set
from enum import Enum
from types import MappingProxyType

# Scalar types accepted as-is: already immutable, safe to retain by reference.
_SAFE_SCALARS = (str, int, float, bool, bytes, type(None))


def deep_freeze(value: object) -> object:
    """Return a deeply immutable copy-view of ``value``; reject unsupported types.

    Mappings -> ``MappingProxyType``. Lists/tuples -> ``tuple``. Sets/frozensets ->
    ``frozenset``. Known-immutable scalars and enum members pass through unchanged. Anything
    else raises ``TypeError`` rather than being silently retained as a mutable alias.
    """
    if isinstance(value, MappingProxyType):
        return value
    if isinstance(value, Mapping):
        return MappingProxyType({k: deep_freeze(v) for k, v in value.items()})
    if isinstance(value, (str, bytes)):
        return value
    if isinstance(value, (list, tuple)):
        return tuple(deep_freeze(v) for v in value)
    if isinstance(value, (set, frozenset)) or (
        isinstance(value, Set) and not isinstance(value, (Mapping, Sequence))
    ):
        return frozenset(deep_freeze(v) for v in value)
    if isinstance(value, Enum):
        return value
    if isinstance(value, _SAFE_SCALARS):
        return value
    raise TypeError(
        f"unsupported value type for digest-bearing deep_freeze: {type(value).__name__!r}"
    )


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
    """``json.dumps`` default: serialize a frozen mapping/frozenset as a plain dict/list."""
    if isinstance(obj, MappingProxyType):
        return dict(obj)
    if isinstance(obj, frozenset):
        return sorted(obj, key=repr)
    raise TypeError(f"not serializable: {type(obj).__name__}")


def deep_thaw(value: object) -> object:
    """Return a plain (mutable) dict/list copy for public output surfaces."""
    if isinstance(value, (MappingProxyType, Mapping)):
        return {k: deep_thaw(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [deep_thaw(v) for v in value]
    if isinstance(value, (set, frozenset)):
        return sorted((deep_thaw(v) for v in value), key=repr)
    return value


__all__ = [
    "deep_freeze",
    "deep_thaw",
    "freeze_mapping",
    "freeze_tuple_of_mappings",
    "json_default",
]
