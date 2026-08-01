"""Reusable current-source resolution and citation construction (v0.3.1 behavior).

This module extracts the private current-source/citation logic that previously lived on
:class:`~jarvis_core.query.engine.QueryEngine` so it can be reused, unchanged, by other
authorized readers (for example v0.4 Project Resume) without copying path confinement,
fingerprint comparison, locator validation, or coverage rules (ADR-0016, ADR-0020).

The behavior is intentionally identical to the released v0.3.1 engine:

- a citation is emitted only after the stored fingerprint is validated against the CURRENT
  on-disk source bytes, re-read strictly within a resolved ``source_root`` (path/symlink
  escape, missing, and unreadable files fail closed);
- the full heading/line locator and a non-empty bounded excerpt are validated against the
  current text before a ``supported`` citation is emitted;
- a ranked ``material`` reference with no claim-supporting passage is declined (``None``);
- an unranked reference with no supporting passage becomes an explicit
  ``coverage="incomplete"`` citation (identity + revision only, never arbitrary content).
"""
from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from jarvis_core.identity import SourceIdentity, fingerprint_bytes
from jarvis_core.models.note import Note
from jarvis_core.query.passages import Locator, locate, validate_against_text
from jarvis_core.query.ranking import ScoredNote
from jarvis_core.query.results import Citation, citation_from_scored

__all__ = ["CitationFactory", "CurrentSourceResolver"]


class CurrentSourceResolver:
    """Re-reads exact CURRENT source bytes for a note, confined to a resolved root.

    A ``source_root`` is mandatory (ADR-0016): a discovery snapshot alone can never
    establish current-source validity, so there is no snapshot fallback. Path/symlink
    escape, a missing or unreadable file, and any read error fail closed by returning empty
    bytes, which then fail the fingerprint check and decline the citation (AC-03R3-01).
    """

    def __init__(self, source_root: Path) -> None:
        self._source_root = source_root.resolve()

    @property
    def source_root(self) -> Path:
        return self._source_root

    def current_bytes(self, note: Note) -> bytes:
        try:
            cand = (self._source_root / note.relpath).resolve()
            if cand.is_relative_to(self._source_root) and cand.is_file():
                return cand.read_bytes()
        except OSError:
            pass
        return b""  # missing / escaped / unreadable -> fail closed


class CitationFactory:
    """Builds validated passage-and-revision citations from authorized identities.

    ``identities`` maps ``relpath`` to the note's stable :class:`SourceIdentity` (as produced
    by the request-scoped authorized view). The factory never invents identity; it only
    binds an already-resolved identity to a validated current passage.
    """

    def __init__(
        self, identities: Mapping[str, SourceIdentity], resolver: CurrentSourceResolver
    ) -> None:
        self._identities = identities
        self._resolver = resolver

    @property
    def resolver(self) -> CurrentSourceResolver:
        return self._resolver

    def make(
        self,
        note: Note,
        evidence: frozenset[str],
        *,
        relevance: float | None,
        reason: str,
        material: bool,
        scored: ScoredNote | None = None,
    ) -> Citation | None:
        """Emit a validated citation, or ``None``.

        Validates the stored fingerprint against the CURRENT source bytes plus
        locator/hierarchy/excerpt before emission (AC-03R2). Returns ``None`` for a stale
        source, or for a ranked ``material`` reference with no claim-supporting passage.
        """
        ident = self._identities[note.relpath]
        current = self._resolver.current_bytes(note)
        if fingerprint_bytes(current) != note.source_fingerprint:
            return None  # stale: source changed since discovery -> never emitted as valid
        current_text = current.decode("utf-8", errors="replace")
        locator, excerpt = locate(note, evidence)
        if excerpt and validate_against_text(locator, excerpt, current_text).ok:
            if scored is not None:
                return citation_from_scored(
                    scored, source_id=ident.source_id, source_identity_kind=ident.kind,
                    source_fingerprint=note.source_fingerprint, locator=locator, excerpt=excerpt,
                )
            return Citation(
                source_id=ident.source_id, source_identity_kind=ident.kind,
                title=note.title or note.path.stem, relpath=note.relpath,
                source_fingerprint=note.source_fingerprint, locator=locator, excerpt=excerpt,
                reason=reason, relative_relevance=relevance, coverage="supported",
            )
        # No claim-specific supporting passage.
        if material:
            return None  # decline a ranked material citation with no supporting passage
        # Unranked reference: emit an explicit coverage-incomplete citation (never arbitrary
        # first content) — identity + revision only, no passage claim.
        return Citation(
            source_id=ident.source_id, source_identity_kind=ident.kind,
            title=note.title or note.path.stem, relpath=note.relpath,
            source_fingerprint=note.source_fingerprint, locator=Locator((), 0, 0), excerpt="",
            reason=reason, relative_relevance=relevance, coverage="incomplete",
        )
