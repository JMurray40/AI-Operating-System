"""Prepare service: authorized retrieval into an immutable snapshot (ADR-0023, H07 §8).

``prepare`` validates the workspace/destination/scope/source-root, applies destination
sensitivity eligibility and source authorization *before* any retrieval, runs the released
deterministic query/evidence pipeline, and projects supported citations into an ordered,
budgeted, immutable :class:`ContextSnapshot`. No provider or network call occurs here
(C06). Excluded sources never influence the snapshot beyond a safe aggregate count (R2.5).
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from jarvis_core.conversation.contract import (
    RemoteEligibility,
    ValidationError,
    remote_eligibility,
)
from jarvis_core.conversation.prompt import context_capacity, item_block_tokens
from jarvis_core.conversation.references import ReferenceResolution, resolve_references
from jarvis_core.conversation.request import PrepareTurnRequest
from jarvis_core.conversation.snapshot import (
    ContextItem,
    ContextSnapshot,
    PromptConstructionVersions,
    ProviderPolicy,
)
from jarvis_core.identity import DuplicateIdentityError
from jarvis_core.models.note import Note
from jarvis_core.policy.scope import AuthorizationScope
from jarvis_core.policy.sensitivity import ceiling_rank
from jarvis_core.project_resume.identity import SELECTION_SELECTED, select_project
from jarvis_core.query.authorized import build_authorized_view
from jarvis_core.query.context_builder import estimate_tokens
from jarvis_core.query.engine import QueryEngine
from jarvis_core.query.results import Citation
from jarvis_core.relationships.resolver import RelationshipResolver

# For a remote destination only public/internal content is eligible (H07 §4.2). We cap the
# effective retrieval ceiling so private/restricted content is excluded *before* retrieval.
_REMOTE_CEILING = "internal"

# Bounded one-hop graph-neighbor expansion (Handoff 08a Decision B): at most 25 neighbors
# and 26 total notes (the selected project seed plus neighbors).
_MAX_NEIGHBORS = 25
_MAX_TOTAL_NOTES = 26


@dataclass(frozen=True)
class PreparedTurn:
    """The immutable result of prepare, plus session-only material for dispatch checks."""

    snapshot: ContextSnapshot
    source_root: Path
    notes_by_relpath: dict[str, Note]
    coverage_label: str
    focus_titles: tuple[str, ...]
    query_trace: dict[str, object] | None = None
    # Internal, session-only inspection aid (the authorized retrieval subset). Never
    # serialized into the snapshot or trace; used by tests and dispatch bookkeeping.
    in_scope_relpaths: tuple[str, ...] = ()


def _effective_ceiling(request_ceiling: str, is_remote: bool) -> str:
    if not is_remote:
        return request_ceiling
    # Cap at 'internal' for remote destinations without ever raising the request ceiling.
    if ceiling_rank(request_ceiling) <= ceiling_rank(_REMOTE_CEILING):
        return request_ceiling
    return _REMOTE_CEILING


def _effective_scope(scope: AuthorizationScope, ceiling: str) -> AuthorizationScope:
    if scope.max_sensitivity == ceiling:
        return scope
    return replace(scope, max_sensitivity=ceiling)


def _citation_to_item(index: int, cite: Citation, token_count: int) -> ContextItem:
    return ContextItem(
        item_id=f"C{index}",
        source_id=cite.source_id,
        source_identity_kind=cite.source_identity_kind,
        relpath=cite.relpath,
        title=cite.title,
        sensitivity=None,  # filled by caller from the note
        source_fingerprint=cite.source_fingerprint,
        heading_path=tuple(cite.locator.heading_path),
        line_start=cite.locator.line_start,
        line_end=cite.locator.line_end,
        excerpt=cite.excerpt,
        reason=cite.reason,
        token_count=token_count,
        relative_relevance=cite.relative_relevance,
    )


def prepare(
    request: PrepareTurnRequest,
    notes: list[Note],
    *,
    focus_titles: tuple[str, ...] = (),
    history_text: str = "",
) -> PreparedTurn:
    """Run the authorized prepare pipeline and return an immutable snapshot."""
    source_root = request.source_root.resolve()
    if not source_root.is_dir():
        raise ValidationError("source_root is not an existing directory")

    profile = request.provider_profile
    ceiling = _effective_ceiling(request.scope.max_sensitivity, profile.is_remote)
    scope = _effective_scope(request.scope, ceiling)

    # -------------------------------------------------- optional exact project selection
    authorization_summary: dict[str, object] = {
        "excluded_count": 0,
        "destination_is_remote": profile.is_remote,
        "effective_max_sensitivity": ceiling,
        "project_selection": None,
    }
    retrieval_notes = notes
    scope_excluded_count: int | None = None
    if request.project_selector is not None:
        # Build the immutable authorized view FIRST; adjacency is created only over
        # authorized notes, so traversal can never pass through an excluded source
        # (Handoff 08a Decision B; ADR-0015/0018).
        try:
            view = build_authorized_view(notes, scope)
        except DuplicateIdentityError as exc:
            # Duplicate/malformed identity fails closed without naming the colliding sources.
            raise ValidationError(
                "project selection failed (invalid): duplicate source identity"
            ) from exc
        selection = select_project(view, request.project_selector)
        if selection.status != SELECTION_SELECTED or selection.identity is None:
            # Fail closed: ambiguous / not_found / invalid never guesses a project.
            raise ValidationError(
                f"project selection failed ({selection.status}): {selection.reason}"
            )
        chosen = selection.identity
        # One-hop expansion: the selected project is the sole seed; include its resolved
        # inbound and outbound direct neighbors, ordered by (source_id, relpath), capped.
        report = RelationshipResolver(view.notes).resolve_all()
        seed = chosen.relpath
        authorized_relpaths = {n.relpath for n in view.notes}
        neighbor_relpaths = (set(report.outgoing(seed)) | set(report.incoming(seed))) - {seed}
        eligible = [rp for rp in neighbor_relpaths if rp in authorized_relpaths]
        ordered = sorted(eligible, key=lambda rp: (view.identities[rp].source_id, rp))
        limit = min(_MAX_NEIGHBORS, _MAX_TOTAL_NOTES - 1)
        included = ordered[:limit]
        neighbors_capped = len(ordered) - len(included)
        subset = {seed, *included}
        # Seed is preserved in the candidate set even if it yields no supporting passage.
        retrieval_notes = [n for n in view.notes if n.relpath in subset]
        scope_excluded_count = view.excluded_count
        authorization_summary["project_selection"] = {
            "status": selection.status,
            "tier": chosen.tier,
            "source_id": chosen.source_id,
            "title": chosen.title,
            "notes_in_scope": len(subset),
            "neighbor_candidates": len(ordered),
            "neighbors_included": len(included),
            # Capped neighbors are disclosed ONLY as a safe aggregate count + reason.
            "neighbors_capped": neighbors_capped,
            "cap_reason": "graph_neighbor_cap" if neighbors_capped else None,
        }

    # -------------------------------------------------- authorized retrieval (no network)
    engine = QueryEngine(retrieval_notes, scope=scope, source_root=source_root)
    answer, qtrace = engine.run(request.user_text, want_trace=request.want_trace)
    authorization_summary["excluded_count"] = (
        scope_excluded_count if scope_excluded_count is not None else engine.excluded_count
    )

    notes_by_relpath = {n.relpath: n for n in engine.all_notes()}

    # -------------------------------------------------- visible reference resolution
    resolution: ReferenceResolution = resolve_references(request.user_text, focus_titles)

    # -------------------------------------------------- project supported citations -> items
    # Budget by the FULL per-item prompt block cost (excerpt + delimiters), capped by the
    # prompt headroom, so the assembled prompt is guaranteed to fit its hard budget (C11).
    user_tokens = estimate_tokens(resolution.normalized_text)
    capacity = context_capacity(
        request.budgets.prompt_tokens, request.budgets.output_reserve_tokens, user_tokens
    )
    budget = min(request.budgets.context_tokens, capacity)
    excerpt_used = 0
    block_used = 0
    items: list[ContextItem] = []
    omissions: list[dict[str, object]] = []
    for cite in answer.supported_citations():
        excerpt_tokens = estimate_tokens(cite.excerpt)
        note = notes_by_relpath.get(cite.relpath)
        item = _citation_to_item(len(items) + 1, cite, excerpt_tokens)
        if note is not None:
            item = replace(item, sensitivity=note.sensitivity)
        block = item_block_tokens(item)
        if block_used + block > budget:
            omissions.append(
                {
                    "relpath": cite.relpath,
                    "title": cite.title,
                    "reason": "context_token_budget",
                }
            )
            continue
        items.append(item)
        excerpt_used += excerpt_tokens
        block_used += block

    # -------------------------------------------------- assemble the immutable snapshot
    provider_policy = ProviderPolicy(
        provider_id=profile.provider_id,
        model_id=profile.model_id,
        scheme=profile.scheme,
        host=profile.host,
        path=profile.path,
        operation=profile.operation,
        streaming=profile.streaming,
        thinking_level=profile.thinking_level,
        timeout_seconds=profile.timeout_seconds,
        automatic_retries=profile.automatic_retries,
        max_input_tokens=profile.max_input_tokens,
        max_output_tokens=profile.max_output_tokens,
        disabled_features=profile.disabled_features,
        is_remote=profile.is_remote,
    )
    prompt_versions = PromptConstructionVersions(
        output_reserve_value=request.budgets.output_reserve_tokens
    )
    budget_accounting: dict[str, object] = {
        "context_token_budget": budget,
        "context_tokens_used": excerpt_used,
        "prompt_context_tokens": block_used,
        "items_included": len(items),
        "items_omitted": len(omissions),
        "output_reserve_tokens": request.budgets.output_reserve_tokens,
        "prompt_token_budget": request.budgets.prompt_tokens,
    }
    snapshot = ContextSnapshot(
        request_id=request.request_id,
        session_id=request.session_id,
        workspace_id=request.workspace_id,
        normalized_user_input=resolution.normalized_text,
        assumptions=tuple(a.to_dict() for a in resolution.assumptions),
        items=tuple(items),
        provider_policy=provider_policy,
        prompt_versions=prompt_versions,
        policy_summary={
            # Exclude the scope's volatile random request_id: the snapshot already binds
            # the canonical request_id at top level, so including it here would make the
            # digest depend on a non-semantic value and break determinism (C08).
            k: v
            for k, v in scope.trace_summary().items()
            if k != "request_id"
        },
        authorization_summary=authorization_summary,
        budget_accounting=budget_accounting,
        safe_omissions=tuple(omissions),
        user_exclusions=(),
        price_table_version=profile.price_table_version,
        max_cost_usd_per_request=profile.max_cost_usd_per_request,
        evaluation_time=request.evaluation_time.isoformat(),
        history_serialization=history_text,
    )

    new_focus = tuple(dict.fromkeys([it.title for it in items] + list(focus_titles)))
    return PreparedTurn(
        snapshot=snapshot,
        source_root=source_root,
        notes_by_relpath={
            it.relpath: notes_by_relpath[it.relpath]
            for it in items
            if it.relpath in notes_by_relpath
        },
        coverage_label=str(answer.citation_coverage()["label"]),
        focus_titles=new_focus,
        query_trace=qtrace.to_dict() if qtrace is not None else None,
        in_scope_relpaths=tuple(sorted(n.relpath for n in retrieval_notes)),
    )


def destination_eligibility(sensitivity: str | None) -> RemoteEligibility:
    """Expose per-item remote eligibility for tests and the manifest."""
    return remote_eligibility(sensitivity)


__all__ = ["PreparedTurn", "destination_eligibility", "prepare"]
