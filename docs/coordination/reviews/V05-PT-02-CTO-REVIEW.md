# V05-PT-02 CTO Conformance Review

| Field | Value |
|---|---|
| Task | `V05-PT-02` |
| Reviewer | Chief Architect / CTO |
| Date | 2026-08-12 |
| Incoming artifact | [Handoff 102](../../../.worktrees/v0.3.1-release/docs/handovers/v0.5/102-principal-engineer-to-cto-personal-prototype-return.md) |
| Controlling brief | [Handoff 101](../../../.worktrees/v0.3.1-release/docs/handovers/v0.5/101-cto-to-principal-engineer-personal-prototype-integration-brief.md) |
| Voice base | `b02c95da40f0f1b47b6a983c75ce5bd8e5e44c35` / `104e33bcd075def264219746e36e1be86c9e4f69` |
| Core executable | `d7105e4f6793f1317ba15f98c7e9c9f03c9f8910` / `f221c7451726437956acf61ecad2fc701bbbbefe` |
| Disposition | **RETURNED FOR BOUNDED CORRECTION** |

## 1. Review boundary

The review inspected the uncommitted Voice worktree at
`C:\Users\jmurr\Projects\J.A.R.V.I.S\.worktrees\v0.5-personal-prototype`, the exact
Handoff 102 return, the bridge, DTO additions, prototype harness, and focused tests. The
frozen Core identity resolves correctly and remains outside the implementation diff.

Quality task `V05-PT-03` remains blocked. This review authorizes no live capability,
certification activity, merge, push, publication, or release.

## 2. Blocking findings

### PT02-CTO-01 — bridge lifecycle commits are not generation-bound

Handoff 101 requires each post-Core result to revalidate the exact session instance,
generation, request, digest, approval, and attempt in the same critical section that
publishes the shell view and speech eligibility. The implementation does not do that.

`prepare_turn`, `remove_context`, `approve_turn`, and `_dispatch` resolve a mutable `_Binding`,
release the bridge lock, call Core, then mutate or publish through that old object without
proving it is still the alias's current binding. `_dispatch` may therefore return and record a
completion from a binding concurrently replaced by reset/decline. That stale result can reach
`VoiceShellController._handle_turn` and become speech. `_replace_binding` also holds the bridge
lock while calling Core reset and Core session creation, contrary to the frozen rule that the
adapter lock is not held across Core work.

The reported same-alias concurrent-prepare test is not evidence for reset/removal/decline/
cancellation versus terminal publication. Reliance on Core's internal race tests cannot prove
the adapter's additional lookup, projection, publication, and speech boundary. Handoff 101
matrix rows 11–13 and 16 remain open at the bridge boundary.

Required correction: implement an adapter-owned admission/commit protocol with an immutable
captured lifecycle identity, no bridge lock held across Core calls, and exact current-binding
revalidation before every mutation, returned public view, attempt record, or speech-eligible
result. Add real barrier-controlled bridge/controller tests for every required race. A losing
completion must return a typed silent stale/cancelled result and create no public attempt,
turn, trace, approval, or speech state.

### PT02-CTO-02 — approval and cancellation identities are not the authoritative Core bindings

`approve_turn` discards the `EgressApproval` returned by Core, creates a new `appr-*` reference,
and stores only that bridge value. This contradicts Handoff 101's exact mapping to Core's
approval identity and retention of the Core approval object. The bridge value can prove only
that the adapter minted a token, not that the token is the approval Core consumed.

Cancellation is likewise not operational for an admitted synchronous attempt. The token is
stored under `cancellation_ref`, but public cancellation accepts only `attempt_ref`; the attempt
record and attempt reference do not exist until after dispatch has completed. `cancel_attempt`
therefore only reports an already-terminal result and never addresses an in-flight token.

Required correction: project the exact safe Core approval identity and retain/revalidate the
exact Core approval object. Define an atomic, bounded cancellation admission mapping that lets
the controller cancel the currently admitted operation without inventing an attempt identity
before Core allocates one. Prove cancellation before admission, during Core work, racing
completion, after terminal state, and after reset. If the released synchronous API cannot
support this without a Core change, stop and return that contract gap rather than simulating
cancellation.

### PT02-CTO-03 — trust projections alter Core semantics and disclose excluded-source counts

The bridge emits an `AUTHORIZATION` omission containing Core's `excluded_count`. Handoff 101
explicitly prohibits excluded-source disclosure through counts. The public view must state a
fixed categorical authorization omission, if needed, without a count or identity-derived
cardinality.

`CoverageView.supported_claims` is computed from the number of presentation citations rather
than Core's `AnswerEvidence.supported_count`; those are not equivalent. The bridge also maps
every non-empty Core limitation tuple to one generic incomplete-evidence limitation, losing
categorical meaning, and constructs a trace reference from request/attempt strings rather than
binding a released safe Core trace identity. These violate the required exact semantic
projection and fail-closed handling of unmapped fields.

Required correction: project exact Core counts and categories only where the Voice contract
has an exact mapping; otherwise add a safe explicit category or fail closed. Do not expose
excluded cardinality. Do not invent trace provenance. Add separate tests where claim count,
citation count, limitation count/type, and excluded count differ.

### PT02-CTO-04 — the mock-only provider boundary is advisory, not enforced

The constructor accepts an arbitrary `provider_factory` callable and `_dispatch` accepts its
result without an exact runtime type check. A type annotation and AST scan do not prevent a
caller from supplying a different implementation of the provider protocol, including a
network-capable adapter. This weakens the structural mock-only boundary.

Required correction: remove the injection seam or enforce that the constructed object is the
exact released `MockConversationProvider` class (not merely protocol-compatible or a
subclass). Preserve deterministic claims through bounded mock configuration, not arbitrary
provider construction. Add a hostile-factory test proving rejection before any provider call.

### PT02-CTO-05 — the required current-PC run is not reproducible from the returned worktree

The worktree's `.git` file points to a transient Linux session path, so ordinary Windows Git
reports that the directory is not a repository. Its `.venv` has only Linux `bin/` executables,
while Handoff 102 documents Windows `.venv\Scripts\...` commands. The CTO could verify the base
only by addressing the repository's administrative worktree directory explicitly; the claimed
direct Windows test and demo commands cannot execute from the returned environment.

This is not a request to alter Git metadata casually. Engineering must recreate or repair the
authorized worktree through a Chief-of-Staff-approved, repository-safe mechanism, preserve the
exact base and diff, then run the complete gates under the current Windows host using a fresh
Windows virtual environment and the same exact Core source identity. The direct repository-root
prototype command, Git status/diff checks, two-run determinism, and all focused tests must be
independently reproducible there. Record exact Windows Python/tool identities. Do not treat the
Linux-only run as current-PC acceptance evidence.

### PT02-CTO-06 — mandatory safety and formatting evidence is incomplete

Handoff 101 requires item 10's hostile-output cases and all applicable lifecycle cases as
executable prototype evidence. Handoff 102 expressly reports that unsafe/empty/oversized
speech was not independently re-tested and that rows 11–13/16 were not exercised at the
bridge boundary. Those are mandatory, not optional defense-in-depth.

The changed Python package also does not pass the frozen Ruff gate because the new files add
new `EXE002` findings. Pre-existing debt does not make new changed-file findings acceptable.
Correct the authorized files or freeze a changed-file-only command that passes without hiding
new debt. Do not perform an unrelated repository-wide formatting or file-mode rewrite.

## 3. Accepted elements retained

The following direction remains accepted and need not be redesigned unless required by the
corrections above:

- one-way Voice Shell to shell-owned adapter to frozen Core architecture;
- exact Voice and Core base identities;
- local `mock_profile()` with no credential/provider network authority;
- synthetic classified fixtures outside both repositories;
- additive instance/generation DTO fields;
- context removal through Core item IDs;
- no legacy, real-audio, tool, vault-write, provider, or certification scope; and
- a direct explicit `--core-mock --fixture synthetic` operator flow.

Prior Core evidence may be cited for unchanged Core behavior, but it cannot replace tests of
the adapter's own authority, race, projection, cancellation, or speech boundaries.

## 4. Required bounded return

Engineering may correct only the existing `V05-PT-02` implementation and directly required
tests/docs. Return a superseding revision of Handoff 102 with:

1. the valid Windows worktree identity and complete changed-file list;
2. exact lifecycle and trust-projection corrections for PT02-CTO-01 through PT02-CTO-04;
3. real barrier-controlled adapter/controller evidence and hostile-output tests;
4. a directly runnable current-PC mock command and two-run semantic digest;
5. complete Voice, applicable frozen-Core, Ruff, typing, privacy, structural, whitespace, and
   repository-integrity results; and
6. no new scope, dependency, live capability, Core modification, commit, merge, push, or
   release action.

Stop if correction requires a released-Core API change, live capability, destructive Git
repair, or broader architecture decision. The one bounded retry permitted by the worklist is
now in use.

## 5. Disposition

**V05-PT-02 IS RETURNED FOR BOUNDED CORRECTION.** Quality remains blocked. Chief of Staff must
route the correction attempt; this CTO review does not itself authorize or activate it.
