"""Stable source identity and source revision — kept separate (ADR-0017).

- ``source_id``: logical identity, namespaced by workspace. Prefer the validated
  frontmatter ``id`` (kind ``explicit``); otherwise derive a workspace+path fallback (kind
  ``path_derived``) whose weaker stability is labelled honestly.
- ``source_fingerprint``: SHA-256 of the *exact source bytes* — a revision marker, never an
  identity. It changes on every byte change (including CRLF/LF) and is not a secret.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass


class DuplicateIdentityError(Exception):
    """Raised when two notes in one workspace share an explicit canonical id.

    Duplicate explicit IDs are validation failures; they must not be silently merged,
    overwritten, or resolved by path order (ADR-0017).
    """


@dataclass(frozen=True)
class SourceIdentity:
    """A source's logical identity and how it was determined."""

    source_id: str
    kind: str  # 'explicit' | 'path_derived'
    workspace_id: str

    def to_dict(self) -> dict[str, object]:
        return {"source_id": self.source_id, "kind": self.kind, "workspace_id": self.workspace_id}


def _normalize_relpath(relpath: str) -> str:
    return relpath.strip().replace("\\", "/").lstrip("/").lower()


def compute_identity(
    workspace_id: str, relpath: str, frontmatter_id: str | None
) -> SourceIdentity:
    """Return the workspace-namespaced identity for a source.

    Explicit id wins; otherwise a deterministic path-derived fallback is used and labelled.
    """
    ws = workspace_id.strip()
    fid = (frontmatter_id or "").strip()
    if fid:
        return SourceIdentity(source_id=f"{ws}:id:{fid}", kind="explicit", workspace_id=ws)
    return SourceIdentity(
        source_id=f"{ws}:path:{_normalize_relpath(relpath)}",
        kind="path_derived",
        workspace_id=ws,
    )


def fingerprint_bytes(data: bytes) -> str:
    """SHA-256 of exact source bytes, prefixed with the algorithm."""
    return "sha256:" + hashlib.sha256(data).hexdigest()
