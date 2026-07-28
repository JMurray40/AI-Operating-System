"""Build a request-authorized view of the vault BEFORE indexing/graph (ADR-0015).

Authorization and sensitivity filtering happen here, before any request-visible index
candidate generation or graph expansion. Excluded notes never enter the returned view, so
downstream retrieval, ranking, graph, context, citations, conflicts, and trace cannot see
them. Only an aggregate ``excluded_count`` is retained. Duplicate explicit identities within
the workspace fail closed (ADR-0017).
"""
from __future__ import annotations

from dataclasses import dataclass

from jarvis_core.identity import (
    DuplicateIdentityError,
    SourceIdentity,
    compute_identity,
)
from jarvis_core.models.note import Note
from jarvis_core.policy.scope import AuthorizationScope


@dataclass(frozen=True)
class AuthorizedView:
    """The authorized subset plus per-source identities and a safe excluded count."""

    notes: list[Note]
    identities: dict[str, SourceIdentity]   # relpath -> identity
    excluded_count: int


def build_authorized_view(notes: list[Note], scope: AuthorizationScope) -> AuthorizedView:
    authorized: list[Note] = []
    identities: dict[str, SourceIdentity] = {}
    seen_explicit: dict[str, str] = {}
    excluded = 0
    for note in notes:
        ident = compute_identity(scope.workspace_id, note.relpath, note.id)
        if not scope.permits(
            source_id=ident.source_id,
            relpath=note.relpath,
            sensitivity=note.sensitivity,
            note_type=note.raw_type,
        ):
            excluded += 1
            continue
        if ident.kind == "explicit":
            if ident.source_id in seen_explicit:
                raise DuplicateIdentityError(
                    f"duplicate explicit source id in workspace "
                    f"'{scope.workspace_id}': {note.id!r}"
                )
            seen_explicit[ident.source_id] = note.relpath
        authorized.append(note)
        identities[note.relpath] = ident
    return AuthorizedView(authorized, identities, excluded)
