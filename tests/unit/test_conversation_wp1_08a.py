"""Handoff 08a WP1 corrections — Decision A (credential preflight) and Decision B
(bounded one-hop authorized graph-neighbor expansion).

All tests are offline. The remote path uses an injected fake credential provider and a fake
adapter with canary values; nothing reads ``GEMINI_API_KEY`` or calls a network.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from jarvis_core.config import Config
from jarvis_core.conversation import (
    ConversationApplication,
    PrepareTurnRequest,
    ProviderProfile,
    mock_profile,
)
from jarvis_core.conversation import application as app_module
from jarvis_core.conversation import context as ctx
from jarvis_core.conversation.contract import (
    CredentialUnavailableError,
    ValidationError,
)
from jarvis_core.policy import local_allow_all
from jarvis_core.providers.conversation import (
    Credential,
    NormalizedResult,
    TerminalState,
)
from jarvis_core.repositories import FileSystemKnowledgeRepository

T = datetime(2026, 8, 1, tzinfo=timezone.utc)
CANARY = "CANARY-SECRET-KEY-do-not-log-abc123"


# ------------------------------------------------------------------ fakes
class FakeCredentials:
    """Injected availability provider with a canary secret (never a live key)."""

    def __init__(self, *, available: bool = True, secret: str = CANARY) -> None:
        self.available = available
        self.secret = secret
        self.avail_calls = 0
        self.get_calls = 0

    def is_available(self) -> bool:
        self.avail_calls += 1
        return self.available

    def get(self) -> Credential:
        self.get_calls += 1
        return Credential(self.secret)


class FakeRemoteProvider:
    """A fake Google-like adapter: records dispatch + credential, returns a completed result."""

    name = "google-gemini-developer-api"
    adapter_version = "test.google.v0.5.0"

    def __init__(self, reply: str = "answer [C1]") -> None:
        self.reply = reply
        self.calls = 0
        self.got_credential: Credential | None = None

    def dispatch(self, request, cancel=None):  # type: ignore[no-untyped-def]
        self.calls += 1
        self.got_credential = request.credential
        return NormalizedResult(
            status=TerminalState.COMPLETED,
            provider_id=request.transport.provider_id,
            model_id=request.transport.model_id,
            adapter_version=self.adapter_version,
            text=self.reply,
            finish_reason="stop",
        )


def remote_profile() -> ProviderProfile:
    return ProviderProfile(
        provider_id="google-gemini-developer-api",
        model_id="gemini-3.5-flash-lite",
        scheme="https",
        host="generativelanguage.googleapis.com",
        path="/v1beta/models/gemini-3.5-flash-lite:generateContent",
        operation="generateContent",
        max_input_tokens=64000,
        max_output_tokens=800,
        timeout_seconds=60.0,
        price_table_version="g-2026-08",
        is_remote=True,
        retention_disclosure="Google may retain per its published terms.",
    )


@pytest.fixture(scope="module")
def vault() -> tuple[list, Path]:
    repo = FileSystemKnowledgeRepository(Config())
    return repo.discover(), Path(repo.root)


def _req(
    session_id: str,
    root: Path,
    *,
    profile: ProviderProfile,
    text: str = "summarize the AI Operating System project",
    selector: str | None = None,
) -> PrepareTurnRequest:
    return PrepareTurnRequest(
        request_id="req-1",
        session_id=session_id,
        workspace_id="local",
        scope=local_allow_all(workspace_id="local", max_sensitivity="internal"),
        source_root=root,
        user_text=text,
        provider_profile=profile,
        project_selector=selector,
        evaluation_time=T,
        want_trace=True,
    )


# ================================================================ Decision A
def test_a1_mock_prepare_never_consults_credentials(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")
    creds = FakeCredentials()
    # Even if a provider is passed, the mock (non-remote) path must not consult it.
    app.prepare_turn(s, _req(s.session_id, root, profile=mock_profile()), notes, credentials=creds)
    assert creds.avail_calls == 0 and creds.get_calls == 0


def test_a2_google_prepare_unavailable_credential_before_retrieval(
    vault: tuple[list, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")
    called = {"prepare": False}

    def _spy(*args: object, **kwargs: object) -> None:
        called["prepare"] = True
        raise AssertionError("retrieval pipeline must not run when credential unavailable")

    monkeypatch.setattr(app_module.context_service, "prepare", _spy)
    with pytest.raises(CredentialUnavailableError):
        app.prepare_turn(
            s,
            _req(s.session_id, root, profile=remote_profile()),
            notes,
            credentials=FakeCredentials(available=False),
        )
    assert called["prepare"] is False
    assert s.pending_prepared is None


def test_a3_google_prepare_available_does_not_materialize_secret(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")
    creds = FakeCredentials(available=True)
    rp = remote_profile()
    snap = app.prepare_turn(s, _req(s.session_id, root, profile=rp), notes, credentials=creds)
    # Availability was checked but the secret was NOT materialized at prepare.
    assert creds.avail_calls >= 1 and creds.get_calls == 0
    blob = str(snap.to_dict()) + str(s.trace.to_dict())
    assert CANARY not in blob


def test_a4_credential_unavailable_after_approval_blocks_dispatch(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")
    creds = FakeCredentials(available=True)
    rp = remote_profile()
    app.prepare_turn(s, _req(s.session_id, root, profile=rp), notes, credentials=creds)
    app.approve(s, actor="jason", now=T)
    creds.available = False  # becomes unavailable after approval
    provider = FakeRemoteProvider()
    with pytest.raises(CredentialUnavailableError):
        app.dispatch_turn(s, provider, now=T)
    assert provider.calls == 0  # blocked before any transport/prompt assembly


def test_a5_no_secret_in_trace_or_result(vault: tuple[list, Path]) -> None:
    notes, root = vault
    app = ConversationApplication()
    s = app.create_session("local")
    creds = FakeCredentials(available=True)
    rp = remote_profile()
    app.prepare_turn(s, _req(s.session_id, root, profile=rp), notes, credentials=creds)
    app.approve(s, actor="jason", now=T)
    provider = FakeRemoteProvider(reply="stores markdown [C1]")
    res = app.dispatch_turn(s, provider, now=T)
    # The opaque credential materialized only at the adapter boundary.
    assert provider.got_credential is not None
    assert provider.got_credential.reveal() == CANARY
    surfaces = str(res.to_dict()) + str(s.trace.to_dict()) + repr(provider.got_credential)
    assert CANARY not in surfaces


# ================================================================ Decision B helpers
def _note(
    root: Path,
    folder: str,
    fname: str,
    *,
    nid: str,
    ntype: str,
    title: str,
    sensitivity: str = "internal",
    related: list[str] | None = None,
    body: str = "Body content.",
) -> None:
    fm = [
        "---",
        f"id: {nid}",
        f"type: {ntype}",
        f'title: "{title}"',
        f"sensitivity: {sensitivity}",
    ]
    if related:
        arr = ", ".join(f'"[[{t}]]"' for t in related)
        fm.append(f"related: [{arr}]")
    fm.append("---")
    text = "\n".join(fm) + f"\n\n# {title}\n\n{body}\n"
    d = root / folder
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{fname}.md").write_text(text, encoding="utf-8")


def _discover(root: Path) -> list:
    return FileSystemKnowledgeRepository(Config(vault_path=root)).discover()


def _breq(
    root: Path, selector: str | None = "Seed Project", text: str = "quokka"
) -> PrepareTurnRequest:
    return PrepareTurnRequest(
        request_id="r",
        session_id="s",
        workspace_id="local",
        scope=local_allow_all(workspace_id="local", max_sensitivity="internal"),
        source_root=root,
        user_text=text,
        provider_profile=mock_profile(),
        project_selector=selector,
        evaluation_time=T,
    )


def _in_scope(root: Path, notes: list, **kw: object) -> tuple[str, ...]:
    return ctx.prepare(_breq(root, **kw), notes).in_scope_relpaths  # type: ignore[arg-type]


# ================================================================ Decision B
def test_b1_b2_inbound_and_outbound_neighbors_in_scope(tmp_path: Path) -> None:
    _note(
        tmp_path,
        "projects",
        "Seed",
        nid="project-seed",
        ntype="project",
        title="Seed Project",
        related=["Out Neighbor"],
    )
    _note(
        tmp_path,
        "concepts",
        "Out",
        nid="concept-out",
        ntype="concept",
        title="Out Neighbor",
        body="The quokka topic lives here.",
    )
    _note(
        tmp_path,
        "decisions",
        "In",
        nid="decision-in",
        ntype="decision",
        title="In Neighbor",
        related=["Seed Project"],
    )
    notes = _discover(tmp_path)
    scope = _in_scope(tmp_path, notes)
    assert any("Out" in r for r in scope)  # outbound neighbor
    assert any("In" in r for r in scope)  # inbound neighbor
    # B1: the neighbor is retrievable and citable.
    snap = ctx.prepare(_breq(tmp_path, text="quokka"), notes).snapshot
    assert any("Out" in it.relpath for it in snap.items)


def test_b3_restricted_neighbor_cannot_affect(tmp_path: Path) -> None:
    _note(
        tmp_path,
        "projects",
        "Seed",
        nid="project-seed",
        ntype="project",
        title="Seed Project",
        related=["Secret Neighbor"],
    )
    _note(
        tmp_path,
        "concepts",
        "Secret",
        nid="concept-secret",
        ntype="concept",
        title="Secret Neighbor",
        sensitivity="restricted",
        body="quokka secret",
    )
    notes = _discover(tmp_path)
    scope = _in_scope(tmp_path, notes)
    assert not any("Secret" in r for r in scope)


def test_b4_traversal_cannot_cross_excluded_intermediary(tmp_path: Path) -> None:
    _note(
        tmp_path,
        "projects",
        "Seed",
        nid="project-seed",
        ntype="project",
        title="Seed Project",
        related=["Mid Excluded"],
    )
    _note(
        tmp_path,
        "concepts",
        "Mid",
        nid="concept-mid",
        ntype="concept",
        title="Mid Excluded",
        sensitivity="restricted",
        related=["Behind Mid"],
    )
    _note(
        tmp_path,
        "concepts",
        "Behind",
        nid="concept-behind",
        ntype="concept",
        title="Behind Mid",
        body="unreachable",
    )
    notes = _discover(tmp_path)
    scope = _in_scope(tmp_path, notes)
    assert not any("Mid" in r for r in scope)
    assert not any("Behind" in r for r in scope)


def test_b5_second_hop_only_note_excluded(tmp_path: Path) -> None:
    _note(
        tmp_path,
        "projects",
        "Seed",
        nid="project-seed",
        ntype="project",
        title="Seed Project",
        related=["In Neighbor"],
    )
    _note(
        tmp_path,
        "decisions",
        "In",
        nid="decision-in",
        ntype="decision",
        title="In Neighbor",
        related=["Second Hop"],
    )
    _note(
        tmp_path,
        "concepts",
        "Second",
        nid="concept-second",
        ntype="concept",
        title="Second Hop",
        body="two hops away",
    )
    notes = _discover(tmp_path)
    scope = _in_scope(tmp_path, notes)
    assert any("In" in r for r in scope)
    assert not any("Second" in r for r in scope)


def test_b6_cycles_and_duplicate_edges_do_not_duplicate(tmp_path: Path) -> None:
    _note(
        tmp_path,
        "projects",
        "Seed",
        nid="project-seed",
        ntype="project",
        title="Seed Project",
        related=["Out Neighbor", "Out Neighbor"],
    )
    _note(
        tmp_path,
        "concepts",
        "Out",
        nid="concept-out",
        ntype="concept",
        title="Out Neighbor",
        related=["Seed Project"],
    )  # cycle back
    notes = _discover(tmp_path)
    scope = _in_scope(tmp_path, notes)
    assert sorted(scope) == list(scope)  # deterministic
    assert len([r for r in scope if "Out" in r]) == 1  # neighbour once
    assert len(scope) == 2  # seed + one neighbor, cycle terminates


def _cap_vault(tmp_path: Path, n: int) -> list:
    titles = [f"Nbr{i:02d}" for i in range(n)]
    _note(
        tmp_path,
        "projects",
        "Seed",
        nid="project-seed",
        ntype="project",
        title="Seed Project",
        related=titles,
    )
    for i, t in enumerate(titles):
        _note(tmp_path, "concepts", f"N{i:02d}", nid=f"nbr-{i:02d}", ntype="concept", title=t)
    return _discover(tmp_path)


def test_b7_caps_hold_below_at_above(tmp_path: Path) -> None:
    # below the cap
    notes = _cap_vault(tmp_path / "a", 24)
    assert len(_in_scope(tmp_path / "a", notes)) == 25
    # at the cap
    notes = _cap_vault(tmp_path / "b", 25)
    assert len(_in_scope(tmp_path / "b", notes)) == 26
    # above the cap
    notes = _cap_vault(tmp_path / "c", 30)
    snap = ctx.prepare(_breq(tmp_path / "c"), notes).snapshot
    ps = snap.authorization_summary["project_selection"]
    assert ps["neighbors_included"] == 25
    assert ps["neighbors_capped"] == 5
    assert ps["cap_reason"] == "graph_neighbor_cap"
    assert ps["notes_in_scope"] == 26


def test_b8_cap_selection_deterministic_under_shuffle(tmp_path: Path) -> None:
    notes = _cap_vault(tmp_path, 30)
    a = _in_scope(tmp_path, notes)
    b = _in_scope(tmp_path, list(reversed(notes)))
    assert a == b


def test_b9_capped_omission_discloses_only_safe_aggregate(tmp_path: Path) -> None:
    notes = _cap_vault(tmp_path, 30)
    snap = ctx.prepare(_breq(tmp_path), notes).snapshot
    ps = snap.authorization_summary["project_selection"]
    assert isinstance(ps["neighbors_capped"], int) and ps["neighbors_capped"] == 5
    # the five capped neighbors' identities/titles are the highest-sorted ids nbr-25..29
    blob = str(snap.to_dict())
    for i in range(25, 30):
        assert f"nbr-{i:02d}" not in blob


def test_b10_duplicate_ids_fail_closed(tmp_path: Path) -> None:
    _note(tmp_path, "projects", "Seed", nid="project-seed", ntype="project", title="Seed Project")
    _note(tmp_path, "concepts", "A", nid="dup-id", ntype="concept", title="A")
    _note(tmp_path, "concepts", "B", nid="dup-id", ntype="concept", title="B")
    notes = _discover(tmp_path)
    with pytest.raises(ValidationError):
        ctx.prepare(_breq(tmp_path), notes)


def test_b11_no_selector_has_no_implicit_expansion(tmp_path: Path) -> None:
    notes = _cap_vault(tmp_path, 30)
    # With no selector, ordinary authorized query behavior retrieves over ALL authorized
    # notes (31 here), not a project-scoped subset.
    scope = _in_scope(tmp_path, notes, selector=None)
    assert len(scope) == 31
