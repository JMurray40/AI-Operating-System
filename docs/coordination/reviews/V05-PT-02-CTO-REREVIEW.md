# V05-PT-02 CTO Superseding Re-review

| Field | Value |
|---|---|
| Task | `V05-PT-02` |
| Reviewer | Chief Architect / CTO |
| Date | 2026-08-13 |
| Incoming artifact | [Handoff 102 Revision 2](../../../.worktrees/v0.3.1-release/docs/handovers/v0.5/102-principal-engineer-to-cto-personal-prototype-return.md) |
| Prior review | [V05-PT-02 CTO Review](V05-PT-02-CTO-REVIEW.md) |
| Correction authority | [V05-PT-02 Correction Authorization](V05-PT-02-CORRECTION-AUTHORIZATION.md) |
| Voice base | `b02c95da40f0f1b47b6a983c75ce5bd8e5e44c35` / `104e33bcd075def264219746e36e1be86c9e4f69` |
| Core executable | `d7105e4f6793f1317ba15f98c7e9c9f03c9f8910` / `f221c7451726437956acf61ecad2fc701bbbbefe` |
| Disposition | **BLOCKED — REVISION 2 DOES NOT CLOSE THE CTO FINDINGS** |

## 1. Outcome

Revision 2 improves the mock-provider restriction, Core approval retention, supported-claim
count, trace binding, and focused adversarial tests. Those changes are directionally correct.
The candidate cannot proceed to Quality because lifecycle atomicity, usable cancellation,
trust projection, and current-PC reproducibility remain nonconformant. The one authorized
bounded retry has been consumed, so this review does not authorize another Engineering cycle.

## 2. Remaining blocking findings

### PT02-R2-01 — publication is still not one atomic generation-bound commit

`prepare_turn`, `remove_context`, and `approve_turn` call `_is_current`, release that lock,
then acquire another lock or mutate `_Binding` fields outside the lock. A reset or replacement
can win between the check and `_set_request`, `binding.snapshot = ...`, or
`binding.approval = ...`. A stale operation can therefore repopulate `_by_request` or publish
state through a binding that is no longer current. This is the exact check-then-act race the
prior review required the correction to close.

The entire admissibility check and all adapter-owned publication writes must occur in one lock
acquisition. The returned public view must be constructed from that committed state or be
withheld. Tests must pause after the current-binding check but before each publish operation;
the present reset-versus-dispatch test does not cover these gaps.

`_dispatch` is closer, but its losing path still returns a public `CoreTurnView` containing a
real attempt reference and turn number plus the invented `trace-discarded` value while claiming
that no public attempt, turn, or trace exists. A stale completion must produce the contract's
typed silent lifecycle rejection/cancellation surface without publishing an attempt/turn/trace
identity that the adapter says was discarded.

### PT02-R2-02 — cancellation remains unusable through the accepted shell contract

Revision 2 registers the in-flight token under `cancellation_ref`, but
`VoiceShellController.cancel()` calls `cancel_attempt()` only when `self.attempt_ref` exists.
That value is assigned only after synchronous `dispatch_turn()` returns. The user-facing shell
therefore still cannot cancel an in-flight dispatch. The new test invokes the bridge directly
with a value the controller never retains or submits; it proves an internal seam, not the
accepted `VoiceShellController -> VoiceCoreBridgeProtocol` workflow.

This is blocking under the task acceptance criterion that Jason can use cancellation, Handoff
101's bridge/controller race matrix, and the Correction Authorization's explicit operational
cancellation requirement and stop line. It is not safely deferrable as an unrelated follow-up.
If the frozen controller/protocol cannot expose a pre-attempt cancellation handle without a
Core change, that exact contract gap must remain stopped for architecture decision.

### PT02-R2-03 — approval and trust projections are still incomplete or misleading

The retained Core `EgressApproval` is correct, but `_approval_ref` hashes only a subset of its
semantic envelope. It omits actor, host, operation, model role, policy version, prompt versions,
output reserve, permitted-request count, and approval contract version. The safe opaque
reference must bind the canonical complete `EgressApproval.to_dict()` representation, not a
selected subset.

The authorization omission still uses `OmissionView(count=1)`. A fixed `1` avoids leaking the
true cardinality but falsely represents one excluded item and does not satisfy the prior
instruction to use a categorical marker without a count. Either add a non-count categorical
surface or omit this projection.

Both distinct Core limitations are still mapped to repeated instances of the same
`INCOMPLETE_EVIDENCE` code. Preserving tuple length is not preserving categorical meaning.
The Voice contract needs exact safe categories for model knowledge versus not-fully-supported
coverage, or it must fail closed. The default model-knowledge answer also remains directly
speech-eligible without the fixed spoken limitation phrase required by Handoff 101.

### PT02-R2-04 — cleanup is not exception-safe

The live-cancellation registration is removed only after Core returns and `present(turn)`
succeeds. If provider construction, Core dispatch with a non-`ConversationError`, presentation,
or DTO projection fails, `_live` retains a stale cancellation entry. Cleanup must occur through
an exception-safe `finally` path while preserving the terminal commit decision. Add fault
injection at provider construction, Core return, presentation, limitation mapping, trace
projection, and view construction.

### PT02-R2-05 — the Windows worktree repair is invalid and the required evidence is absent

Direct independent Windows Git still reports `Not a git repository` in the returned worktree.
The worktree `.git` file now points to itself:

```text
gitdir: C:/Users/jmurr/Projects/J.A.R.V.I.S/.worktrees/v0.5-personal-prototype/.git
```

It must point to the corresponding administrative directory under the main repository's
`.git/worktrees/`; the reverse `gitdir` file points back to the worktree `.git` file. Revision 2
made both sides point at the worktree pointer file, creating a loop rather than a valid repair.
The reported `prunable` state is further evidence that Git does not recognize a healthy linked
worktree.

Accordingly, direct `git status`, `git rev-parse`, and `git diff --check` fail from the exact
worktree on the current Windows host. The required fresh Windows environment, unrestricted
changed-file Ruff check, full Voice tests, direct prototype command, two-run determinism, and
non-vacuous repository-integrity test were not executed. Revision 2 explicitly discloses this,
so PT02-CTO-05 and PT02-CTO-06 cannot be considered closed.

The inert `.bak` administrative artifacts and any future repair must be handled only under a
new Chief-of-Staff-approved repository-safe procedure. This review does not authorize further
Git metadata edits.

## 3. Evidence status

The reported Linux test results may remain supporting evidence for the corrected source, but
they do not establish the current-PC personal prototype. The repository-integrity test is
explicitly vacuous in that environment, and the direct Windows commands fail before test or
demo startup. Quality cannot independently bind a candidate or reproduce the operator path.

Previously accepted frozen-Core behavior remains reusable because Core was not modified.
The Voice implementation has no exact commit/tree candidate; it remains an uncommitted diff
against `b02c95d` and is not approved for merge, packaging, or pilot use.

## 4. Governance routing

**V05-PT-02 is BLOCKED.** Chief of Staff must decide whether to authorize a new, narrowly
scoped recovery/correction task or return the unresolved controller-cancellation/API issue for
architecture re-planning. The consumed retry must not be silently reset in the existing task.

`V05-PT-03` remains blocked. No Quality work, Product Owner pilot, provider, credential,
network, audio, legacy, vault, certification, merge, push, publication, or release activity is
authorized.
