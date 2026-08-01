"""Exact, tiered project selection over the authorized view (ADR-0018).

Selection is an authorization and disclosure boundary, not a relevance problem. Only
``type=project`` notes inside the request-scoped authorized view participate. One normalized
selector is compared through four exact tiers — canonical ``source_id``, title, alias, and
(weaker, path-derived) filename stem — and the *first* tier with any match controls the
outcome. There is no fuzzy, prefix, substring, stemming, semantic, graph, or relevance
matching, and ambiguity at the controlling tier is never broken by a heuristic.
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass

from jarvis_core.identity import DuplicateIdentityError
from jarvis_core.models.base import NoteType
from jarvis_core.models.note import Note
from jarvis_core.policy.scope import AuthorizationScope
from jarvis_core.project_resume.contract import (
    TIER_ALIAS,
    TIER_CANONICAL_ID,
    TIER_FILENAME_STEM,
    TIER_TITLE,
)
from jarvis_core.project_resume.results import ProjectIdentity
from jarvis_core.query.authorized import AuthorizedView, build_authorized_view
from jarvis_core.query.tokenizer import normalize as _tok_normalize

# Internal selection statuses (mapped to result statuses by the assembler).
SELECTION_SELECTED = "selected"
SELECTION_AMBIGUOUS = "ambiguous"
SELECTION_NOT_FOUND = "not_found"
SELECTION_INVALID = "invalid"


@dataclass(frozen=True)
class IdentitySelection:
    """The outcome of exact tiered project selection."""

    status: str
    identity: ProjectIdentity | None = None
    candidates: tuple[ProjectIdentity, ...] = ()
    reason: str = ""


def normalize_selector(value: str) -> str:
    """Unicode-normalize (NFC), trim surrounding whitespace, and case-fold a selector.

    Mirrors normalization already accepted by the query tokenizer (whitespace + case),
    layered on Unicode NFC. It intentionally preserves internal punctuation such as the
    hyphens in canonical IDs, so ``project-alpha`` never collapses into ``projectalpha``.
    """
    return _tok_normalize(unicodedata.normalize("NFC", value))


def _project_identity(view: AuthorizedView, note: Note, tier: str) -> ProjectIdentity:
    ident = view.identities[note.relpath]
    return ProjectIdentity(
        source_id=ident.source_id,
        identity_kind=ident.kind,
        title=note.title or note.path.stem,
        relpath=note.relpath,
        tier=tier,
    )


def _sorted_candidates(cands: list[ProjectIdentity]) -> tuple[ProjectIdentity, ...]:
    # Sorted by stable canonical source identity then relative path (ADR-0018); no relevance.
    return tuple(sorted(cands, key=lambda c: (c.source_id, c.relpath)))


def select_project(view: AuthorizedView, selector: str) -> IdentitySelection:
    """Select exactly one authorized project, or report ambiguous/not_found (ADR-0018)."""
    sel = normalize_selector(selector)
    if not sel:
        return IdentitySelection(SELECTION_NOT_FOUND, reason="empty selector after normalization")

    projects = [n for n in view.notes if n.type is NoteType.PROJECT]

    # Each tier is (tier_name, predicate that yields True for a matching note).
    def canonical_match(n: Note) -> bool:
        return normalize_selector(view.identities[n.relpath].source_id) == sel

    def title_match(n: Note) -> bool:
        return bool(n.title) and normalize_selector(n.title or "") == sel

    def alias_match(n: Note) -> bool:
        return any(normalize_selector(a) == sel for a in n.aliases)

    def stem_match(n: Note) -> bool:
        return normalize_selector(n.path.stem) == sel

    tiers = (
        (TIER_CANONICAL_ID, canonical_match),
        (TIER_TITLE, title_match),
        (TIER_ALIAS, alias_match),
        (TIER_FILENAME_STEM, stem_match),
    )

    for tier_name, predicate in tiers:
        matches = [n for n in projects if predicate(n)]
        if not matches:
            continue  # weaker tiers only consulted when a stronger tier has no match
        if len(matches) == 1:
            return IdentitySelection(
                SELECTION_SELECTED,
                identity=_project_identity(view, matches[0], tier_name),
                reason=f"exact {tier_name} match",
            )
        candidates = _sorted_candidates(
            [_project_identity(view, n, tier_name) for n in matches]
        )
        return IdentitySelection(
            SELECTION_AMBIGUOUS,
            candidates=candidates,
            reason=f"{len(candidates)} projects matched at tier '{tier_name}'",
        )

    return IdentitySelection(SELECTION_NOT_FOUND, reason="no project matched at any tier")


def resolve_project(
    notes: list[Note], scope: AuthorizationScope, selector: str
) -> IdentitySelection:
    """Build the authorized view and select; duplicate/malformed identity fails closed."""
    try:
        view = build_authorized_view(notes, scope)
    except DuplicateIdentityError as exc:
        # Duplicate explicit canonical IDs (or malformed identity state) fail closed without
        # disclosing which sources collided (ADR-0015/0017/0018).
        return IdentitySelection(SELECTION_INVALID, reason=f"invalid identity state: {exc}")
    return select_project(view, selector)
