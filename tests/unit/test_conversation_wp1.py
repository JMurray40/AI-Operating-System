"""WP1 offline conversation core — C01-C12, C16-C30 (offline subset).

Deterministic tests over the released fixture vault, mapping each acceptance-test ID to
executable evidence. No network, no provider key, no real adapter. Every remote turn uses
the deterministic mock adapter or an injected spy/fake.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from jarvis_core.config import Config
from jarvis_core.conversation import (
    ConversationApplication,
    PrepareTurnRequest,
    ProviderProfile,
    mock_profile,
)
from jarvis_core.conversation import context as ctx
from jarvis_core.conversation.contract import (
    ApprovalError,
    BudgetError,
    Coverage,
    DriftError,
    EvidenceType,
    RemoteEligibility,
    ValidationError,
    remote_eligibility,
)
from jarvis_core.conversation.prompt import FIXED_SAFETY_INSTRUCTION, assemble_prompt
from jarvis_core.conversation.render import sanitize_markdown
from jarvis_core.conversation.request import Budgets
from jarvis_core.policy import local_allow_all
from jarvis_core.providers.conversation import (
    CancellationToken,
    MockConversationProvider,
    NormalizedResult,
    ProviderRequest,
    TerminalState,
    UsageProvenance,
)
from jarvis_core.repositories import FileSystemKnowledgeRepository

T = datetime(2026, 8, 1, tzinfo=timezone.utc)
_QUERY = "summarize the AI Operating System project"


@pytest.fixture(scope="module")
def vault() -> tuple[list, Path]:
    repo = FileSystemKnowledgeRepository(Config())
    return repo.discover(), Path(repo.root)


def _request(
    session_id: str,
    root: Path,
    *,
    text: str = _QUERY,
    profile: ProviderProfile | None = None,
    selector: str | None = None,
    budgets: Budgets | None = None,
    workspace_id: str = "local",
) -> PrepareTurnRequest:
    return PrepareTurnRequest(
        request_id="req-1",
        session_id=session_id,
        workspace_id=workspace_id,
        scope=local_allow_all(workspace_id=workspace_id, max_sensitivity="internal"),
        source_root=root,
        user_text=text,
        provider_profile=profile or mock_profile(),
        project_selector=selector,
        budgets=budgets or Budgets(),
        evaluation_time=T,
        want_trace=True,
    )


class ExplodingProvider:
    """A provider that fails if dispatched — proves prepare/inspect never call it (C06)."""

    name = "exploding"
    adapter_version = "test.exploding"

    def dispatch(
        self, request: ProviderRequest, cancel: CancellationToken | None = None
    ) -> NormalizedResult:
        raise AssertionError("provider must not be called during prepare/inspect")


# ------------------------------------------------------------------ C01 session
def test_c01_session_numbering_and_reset(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")
    assert s.peek_turn_number() == 1
    app.prepare_turn(s, _request(s.session_id, root), notes)
    app.approve(s, actor="jason", now=T)
    r1 = app.dispatch_turn(s, MockConversationProvider(reply="ok [C1]"), now=T)
    assert r1.turn_number == 1
    app.reset_session(s)
    assert s.peek_turn_number() == 1 and s.turns == []


def test_c01_no_durable_state(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")
    app.prepare_turn(s, _request(s.session_id, root), notes)
    # Nothing is written anywhere; a fresh application shares no state.
    assert ConversationApplication()._sessions == {}


# ------------------------------------------------------------------ C05 selection
def test_c05_project_selection_exact(vault: tuple[list, Path]) -> None:
    notes, root = vault
    prepared = ctx.prepare(_request("s", root, selector="AI Operating System"), notes)
    sel = prepared.snapshot.authorization_summary["project_selection"]
    assert isinstance(sel, Mapping) and sel["status"] == "selected"


def test_c05_project_selection_not_found_fails_closed(vault: tuple[list, Path]) -> None:
    notes, root = vault
    with pytest.raises(ValidationError):
        ctx.prepare(_request("s", root, selector="no-such-project-xyz"), notes)


# ------------------------------------------------------------------ C06 no network in prepare
def test_c06_no_provider_call_during_prepare(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")
    snap = app.prepare_turn(s, _request(s.session_id, root), notes)  # must not raise
    app.remove_context(s, snap.items[0].item_id)  # inspect/remove also offline
    # Dispatch with an exploding provider only fails at dispatch, never before.
    app.approve(s, actor="jason", now=T)
    with pytest.raises(AssertionError):
        app.dispatch_turn(s, ExplodingProvider(), now=T)


# ------------------------------------------------------------------ C07/C08 snapshot
def test_c07_removal_is_immutable_new_digest(vault: tuple[list, Path]) -> None:
    notes, root = vault
    snap = ctx.prepare(_request("s", root), notes).snapshot
    first = snap.items[0].item_id
    d0 = snap.digest
    smaller = snap.without_item(first)
    assert snap.digest == d0  # original unchanged
    assert smaller.digest != d0  # new digest
    assert first not in [i.item_id for i in smaller.items]
    assert first in smaller.user_exclusions


def test_c08_canonical_serialization_deterministic(vault: tuple[list, Path]) -> None:
    notes, root = vault
    req = _request("s", root)
    d1 = ctx.prepare(req, notes).snapshot.digest
    shuffled = list(reversed(notes))
    d2 = ctx.prepare(req, shuffled).snapshot.digest
    assert d1 == d2


# ------------------------------------------------------------------ C09 approval binding
def test_c09_approval_replay_after_removal_blocked(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")
    snap = app.prepare_turn(s, _request(s.session_id, root), notes)
    app.approve(s, actor="jason", now=T)
    app.remove_context(s, snap.items[0].item_id)  # invalidates the approval
    with pytest.raises(ApprovalError):
        app.dispatch_turn(s, MockConversationProvider(), now=T)


def test_c09_expired_approval_blocked(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")
    app.prepare_turn(s, _request(s.session_id, root), notes)
    app.approve(s, actor="jason", now=T, ttl_seconds=10)
    with pytest.raises(ApprovalError):
        app.dispatch_turn(s, MockConversationProvider(), now=T + timedelta(seconds=60))


def test_c09_prompt_version_change_after_approval_blocked(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")
    snap = app.prepare_turn(s, _request(s.session_id, root), notes)
    approval = app.approve(s, actor="jason", now=T)
    # Mutate a bound prompt-construction version and prove the approval no longer matches.
    tampered = dict(approval.prompt_versions)
    tampered["safety_instruction_version"] = "tampered"
    object.__setattr__(approval, "prompt_versions", tampered)
    with pytest.raises(ApprovalError):
        approval.check(snap, policy_version="1", now=T)


# ------------------------------------------------------------------ C10 drift
def test_c10_current_byte_drift_blocks_dispatch(vault: tuple[list, Path], tmp_path: Path) -> None:
    # Copy the vault so we can mutate a source without touching the real fixture.
    import shutil

    _notes, root = vault
    dst = tmp_path / "vault"
    shutil.copytree(root, dst)
    repo_notes = FileSystemKnowledgeRepository(Config(vault_path=dst)).discover()
    app = ConversationApplication()
    s = app.create_session("local")
    snap = app.prepare_turn(s, _request(s.session_id, dst), repo_notes)
    app.approve(s, actor="jason", now=T)
    target = dst / snap.items[0].relpath
    target.write_bytes(target.read_bytes() + b"\n\ndrift\n")
    with pytest.raises(DriftError):
        app.dispatch_turn(s, MockConversationProvider(), now=T)


# ------------------------------------------------------------------ C11 budget
def test_c11_prompt_budget_hard_boundary(vault: tuple[list, Path]) -> None:
    notes, root = vault
    tiny = Budgets(context_tokens=3000, prompt_tokens=10, output_reserve_tokens=5)
    snap = ctx.prepare(_request("s", root, budgets=tiny), notes).snapshot
    with pytest.raises(BudgetError):
        assemble_prompt(snap)


# ------------------------------------------------------------------ C12 injection
def test_c12_source_text_cannot_change_instructions(vault: tuple[list, Path]) -> None:
    notes, root = vault
    snap = ctx.prepare(_request("s", root), notes).snapshot
    projection = assemble_prompt(snap)
    # Fixed trusted safety instruction is always present and separate from source blocks.
    assert FIXED_SAFETY_INSTRUCTION in projection.content.system_instruction
    assert "[SOURCE C1" in projection.content.system_instruction  # sources are delimited


# ------------------------------------------------------------------ C16/C18 taxonomy
def test_c16_c18_taxonomy_distinct(vault: tuple[list, Path]) -> None:
    # AC-05-04R: support is exact (a current source sentence/span or exact metadata value),
    # never shared-token overlap — bind claims to real exact excerpt text.
    from jarvis_core.conversation.evidence import exact_source_spans
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")
    snap = app.prepare_turn(s, _request(s.session_id, root), notes)
    app.approve(s, actor="jason", now=T)
    i1, i2 = snap.items[0], snap.items[1]
    fact1 = exact_source_spans(i1.excerpt)[0]
    fact2 = exact_source_spans(i2.excerpt)[0]
    claims = [
        (fact1, "fact", [i1.item_id]),
        (f"{fact1} and {fact2}", "inference", [i1.item_id, i2.item_id]),
        ("General world knowledge, not from the vault.", "model_knowledge", []),
    ]
    res = app.dispatch_turn(s, MockConversationProvider(claims=claims), now=T)
    types = {c.evidence_type for c in res.attempt.evidence.claims}
    assert EvidenceType.FACT in types
    assert EvidenceType.INFERENCE in types       # explicit multi-premise inference
    assert EvidenceType.MODEL_KNOWLEDGE in types  # uncited, visibly not source-backed


def test_c16_stale_citation_withholds_answer(vault: tuple[list, Path], tmp_path: Path) -> None:
    import shutil

    _notes, root = vault
    dst = tmp_path / "vault"
    shutil.copytree(root, dst)
    repo_notes = FileSystemKnowledgeRepository(Config(vault_path=dst)).discover()
    app = ConversationApplication()
    s = app.create_session("local")
    snap = app.prepare_turn(s, _request(s.session_id, dst), repo_notes)
    app.approve(s, actor="jason", now=T)
    # Change bytes AFTER approval; drift is caught at step 8, so dispatch fails
    # closed rather than answering from a stale citation.
    (dst / snap.items[0].relpath).write_bytes(b"totally different content\n")
    res_or_error = None
    try:
        claims = [("A fact.", "fact", [snap.items[0].item_id])]
        res = app.dispatch_turn(s, MockConversationProvider(claims=claims), now=T)
        res_or_error = res.attempt.status
    except DriftError:
        res_or_error = "drift"
    assert res_or_error in (TerminalState.FAILED, "drift")


# ------------------------------------------------------------------ C19 coverage
def test_c19_coverage_labels(vault: tuple[list, Path]) -> None:
    # AC-05-04R: bind the claim to the item's real exact excerpt, not a shared-token wrapper.
    from jarvis_core.conversation.evidence import exact_source_spans
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")
    snap = app.prepare_turn(s, _request(s.session_id, root), notes)
    app.approve(s, actor="jason", now=T)
    fact_text = exact_source_spans(snap.items[0].excerpt)[0]
    fact = [(fact_text, "fact", [snap.items[0].item_id])]
    complete = app.dispatch_turn(s, MockConversationProvider(claims=fact), now=T)
    assert complete.coverage is Coverage.COMPLETE

    app.prepare_turn(s, _request(s.session_id, root), notes)
    app.approve(s, actor="jason", now=T)
    modelonly = app.dispatch_turn(
        s, MockConversationProvider(reply="no citation here"), now=T
    )
    assert modelonly.coverage is Coverage.INCOMPLETE


# ------------------------------------------------------------------ C20 no numeric confidence
def test_c20_no_numeric_answer_confidence(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")
    app.prepare_turn(s, _request(s.session_id, root), notes)
    app.approve(s, actor="jason", now=T)
    res = app.dispatch_turn(s, MockConversationProvider(reply="a [C1]"), now=T)
    blob = str(res.to_dict())
    assert "answer_confidence" not in blob
    assert "confidence" not in blob


# ------------------------------------------------------------------ C24 usage provenance
def test_c24_usage_provenance_never_silent_zero() -> None:
    prov = MockConversationProvider()
    from jarvis_core.providers.conversation import ProviderContent, TransportMetadata

    req = ProviderRequest(
        request_id="r",
        attempt_id="a",
        content=ProviderContent("sys", "hello world", 10),
        transport=TransportMetadata("mock", "mock", "none", "local", "/m", "complete", 60.0, 64000),
    )
    result = prov.dispatch(req)
    assert result.usage.provenance is UsageProvenance.ESTIMATED
    # An unknown-usage result reports UNKNOWN, not zero.
    unknown = NormalizedResult(TerminalState.COMPLETED, "mock", "mock", "v")
    assert unknown.usage.provenance is UsageProvenance.UNKNOWN
    assert unknown.usage.input_tokens is None


# ------------------------------------------------------------------ C22 cancellation
def test_c22_cancellation_is_terminal_once(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")
    app.prepare_turn(s, _request(s.session_id, root), notes)
    app.approve(s, actor="jason", now=T)
    token = CancellationToken()
    token.cancel()
    res = app.dispatch_turn(s, MockConversationProvider(), now=T, cancel=token)
    assert res.attempt.status is TerminalState.CANCELLED
    assert s.turns == []  # no completed message recorded


# ------------------------------------------------------------------ C25 rendering
def test_c25_sanitizer_neutralizes_active_content() -> None:
    hostile = "<script>evil()</script> ![x](http://e/i.png) [t](javascript:alert(1)) <http://e>"
    safe = sanitize_markdown(hostile)
    assert "<script>" not in safe
    assert "http://e/i.png" not in safe  # remote image defanged
    assert "javascript:" not in safe
    assert "[blocked-link" in safe


# ------------------------------------------------------------------ C26 trace
def test_c26_trace_has_no_content(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")
    app.prepare_turn(s, _request(s.session_id, root), notes)
    app.approve(s, actor="jason", now=T)
    app.dispatch_turn(s, MockConversationProvider(reply="secret answer body [C1]"), now=T)
    blob = str(s.trace.to_dict())
    assert "secret answer body" not in blob
    assert _QUERY not in blob


# ------------------------------------------------------------------ C27 isolation
def test_c27_cross_workspace_sessions_isolated(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    a = app.create_session("wsA")
    b = app.create_session("wsB")
    assert a.session_id != b.session_id
    app.prepare_turn(a, _request(a.session_id, root, workspace_id="wsA"), notes)
    assert b.pending_prepared is None  # A's prepare does not leak into B


# ------------------------------------------------------------------ C28/C29 read-only
def test_c28_c29_no_vault_mutation_or_store(vault: tuple[list, Path]) -> None:
    import hashlib

    notes, root = vault

    def tree_hash(p: Path) -> str:
        h = hashlib.sha256()
        for f in sorted(p.rglob("*.md")):
            h.update(f.read_bytes())
        return h.hexdigest()

    before = tree_hash(root)
    app = ConversationApplication()
    s = app.create_session("local")
    app.prepare_turn(s, _request(s.session_id, root), notes)
    app.approve(s, actor="jason", now=T)
    app.dispatch_turn(s, MockConversationProvider(reply="a [C1]"), now=T)
    assert tree_hash(root) == before  # vault unchanged


# ------------------------------------------------------------------ eligibility helper
def test_remote_eligibility_fails_closed() -> None:
    assert remote_eligibility("public") is RemoteEligibility.ELIGIBLE
    assert remote_eligibility("internal") is RemoteEligibility.ELIGIBLE
    assert remote_eligibility("private") is RemoteEligibility.DENIED
    assert remote_eligibility("restricted") is RemoteEligibility.DENIED
    assert remote_eligibility(None) is RemoteEligibility.DENIED
