# Governance Simplification Pilot

| Field | Value |
|---|---|
| Purpose | Reduce process weight on low-risk work without removing any existing safety control |
| Owner | Chief of Staff |
| Reviewer | Product Owner |
| Applies to | Jarvis and reusable future projects |
| Authority | Process aid; never a substitute for [Governance](../../GOVERNANCE.md), [Ways of Working](../../WAYS_OF_WORKING.md), [Worklist Process](../WORKLIST_PROCESS.md), or [Agent Relay Process](../AGENT_RELAY_PROCESS.md) |
| Originating task | `V05-PT-59` |
| Originating review | [Consolidated Chief-of-Staff Review](../reviews/CLAUDE-PLANNING-CONSOLIDATED-CHIEF-OF-STAFF-REVIEW.md), package 7 |
| Authorization | [Product Owner Authorization](../reviews/CLAUDE-PLANNING-CONSOLIDATION-PRODUCT-OWNER-AUTHORIZATION.md) |
| Incorporates | The external-input closure gate required by `docs/coordination/CURRENT_HANDOFF.md`, exposed by PT58 Handoff 220 |
| Status | Piloting — not yet adopted as the default process |

## Why this exists

`WORKLIST_PROCESS.md` and `AGENT_RELAY_PROCESS.md` were built to keep unreviewed, expensive, or
irreversible work honest. `V05-PT-58` shows what that costs on real high-risk work: multiple
preflight round-trips, restart cycles, and gated-credential decisions, each correctly routed
through the Chief of Staff and Product Owner one at a time. That weight is doing its job on PT58
and this pilot does not touch it.

Most tasks are not PT58. A documentation refresh or an offline test rebase does not carry
credential, network, destructive, live-provider, or release risk, and paying PT58-grade process
tax on it produces handoffs without producing safety. This pilot defines a lighter path for that
majority of work, keeps every existing hard control in place, and measures whether the lighter
path actually saves handoffs and time before it becomes the default.

## Scope and boundary

- This document defines a process. It does not authorize, start, or reclassify any task.
- It never applies to `V05-PT-58` or any task in the `v05-prototype` concurrency group while PT58
  is active. PT58 continues under the unmodified `WORKLIST_PROCESS.md` and `AGENT_RELAY_PROCESS.md`.
- It changes no code, schema, candidate, or safety gate. Risk tiers are recorded as ordinary text
  in a task's `scope` or `required_evidence` entries, not as a new worklist schema field.
- Adoption beyond the pilot task(s) the Product Owner selects at review time requires a separate
  Product Owner decision, recorded the same way any other worklist change is recorded.

## External-input closure gate (applies at every tier)

`V05-PT-58` stalled after execution had already begun: Phase 1 reached the fixture requirement
before anyone had confirmed that a licensed public source existed for the five exact required
phrases, and the task had to stop and route a Product Owner decision (Handoff 220) mid-flight.
That is a closure gap, not a tiering problem, so it is added here as a strengthening that applies
to every tier, including Tier 3, and is never itself simplified away.

Before any task moves from `proposed`/`blocked` to `authorized`, and again before the owner moves
it from `authorized` to `in_progress`, the Chief of Staff confirms that every external input the
task's `scope` or `inputs` depends on — a data set, fixture, recording, credential, model,
dependency, or third-party artifact not already in the repository — has all of the following
closed, or the task stays `blocked` with the missing item named:

1. **Source or construction method** — an identified place the input comes from, or an exact
   method to construct it (for example: record it, generate it, derive it).
2. **Permission** — the license or authorization that allows this project to acquire, hold, and
   use it for the task's stated purpose.
3. **Identity** — the exact version, revision, hash, or equivalent that will be acquired, so the
   task cannot silently substitute a different input.
4. **Access path** — the concrete mechanism to obtain it (URL, repository, device, recording
   session) that the owner can actually execute.
5. **Validation method** — how the owner will confirm, after acquisition, that the input matches
   its declared identity and is fit for use.
6. **Fallback** — what happens if acquisition fails: an alternate source, an alternate
   construction method, or an explicit stop-and-escalate route, decided before execution rather
   than discovered during it.

This gate is a precondition check, not new work: it asks the Chief of Staff to confirm these six
facts are already knowable, not to go acquire the input. A task whose external inputs cannot be
closed on all six points stays `blocked`, with the specific unclosed point recorded, exactly as
PT58 was correctly routed to `blocked` once the fixture-source gap was found. The gate applies
identically at Tiers 0-3; a Tier 0-2 task's bundled preflight (below) simply runs this check as
one of its bundled, non-destructive items instead of a separate round-trip.

## Risk tiers

The Chief of Staff assigns a tier when creating or activating a task and states it as the first
`scope` entry, for example `Risk tier: 1 (local, reversible, no credentials/network/destructive
action)`. Tier assignment is a Chief-of-Staff judgment, not engineering's; the owning role may
not lower its own tier.

| Tier | Definition | Example from this project |
|---|---|---|
| 3 — Full process | Any credential use, live network or provider call, destructive operation (delete, move, merge, push), model/dependency acquisition, or release/certification/publication step | `V05-PT-58` |
| 2 — Standard, bundled preflight | Local execution that installs, runs, or configures something in an isolated worktree or sandbox, with no credentials, no external network, and full rollback | Isolated-worktree adversarial test execution |
| 1 — Light | Local, reversible, read/write-only work in a single worktree; no installs, no credentials, no network | Offline test/fixture rebasing (`V05-PT-61`-shaped work) |
| 0 — Documentation-only | Read-only research plus Markdown/JSON coordination artifacts; no source code change | Documentation refresh (`V05-PT-60`-shaped work), this pilot itself |

A task is Tier 3 if it meets the Tier 3 definition on any single criterion, regardless of how
small the rest of the task is. Tier is not negotiable downward mid-task: if new information shows
a Tier 0–2 task actually touches credentials, network, a destructive action, or release, the owner
stops and the Chief of Staff re-tiers it to 3 before work continues (see Escalation).

## What is simplified, and what stays exactly as strict

The External-input closure gate above is not in this table: it is a strengthening added at every
tier, not a simplification, and it is never lightened by the items below.

| Simplification (Tiers 0–2 only) | What it changes | What stays unchanged |
|---|---|---|
| Bundled preflight | Non-destructive, non-elevated preflight checks are run and reported as one pass instead of one round-trip per check | Any preflight step needing elevation, network, or credentials is never bundled; it stays a separate gated step, same as today |
| Graded review outcomes | The reviewer may note non-blocking observations inline in the `accepted` disposition instead of forcing a correction round for cosmetic issues | The four governing outcomes remain exactly `accepted`, `returned_for_correction`, `blocked`, `superseded` from the existing worklist schema; no new terminal status is introduced and nothing is auto-accepted |
| Consolidated correction list | A `returned_for_correction` disposition must list every defect found in one pass | The reviewer still finds and lists every defect; consolidation changes delivery cadence, not review rigor or coverage |
| Same-task correction allowance | One bounded correction round happens inside the same task by default, without a new task ID | Still exactly one round by default, matching the existing `retry_policy` pattern already used on PT58 and PT61; a second round still requires Chief of Staff escalation |
| Measured process churn | Handoff count, elapsed time, and correction rounds are recorded on the task so future tiering decisions are evidence-based | Recording measurements never substitutes for reviewer acceptance and never changes a task's tier retroactively |

Nothing above removes the Product Owner as reviewer for governance work, removes the Chief of
Staff's exclusive authority to move a task from `blocked` to `authorized`, or changes who may set
`accepted`. Credential handling, network/provider access, destructive operations, and
release/certification/publication controls in `WORKLIST_PROCESS.md` and `AGENT_RELAY_PROCESS.md`
are unmodified for every tier.

## Bundled preflight (Tiers 0–2)

1. The owner lists every applicable preflight check from the task's `execution.preflight_checks`,
   plus the External-input closure gate above for every external input the task depends on.
2. The owner runs every non-destructive, non-elevated check in one pass and records pass/fail for
   each in the outgoing handoff, instead of stopping after each individual check.
3. Any check that would require credentials, network access, elevation, or an irreversible action
   is excluded from the bundle and run as its own gated step under the unmodified process.
4. A single bundled failure still stops the task; the owner reports the exact failing check and
   does not substitute or skip it.

## Graded review outcomes (Tiers 0–2)

The reviewer still chooses one of the four existing worklist statuses. "Grading" means the
reviewer's return artifact states which of the following applies, so routine notes stop consuming
a full correction round:

| Grade | Worklist status | Meaning |
|---|---|---|
| Clean accept | `accepted` | No defects found |
| Accept with notes | `accepted` | No defect blocks acceptance; non-blocking observations are logged in the review artifact for the next task in the same area, not corrected now |
| Bounded correction | `returned_for_correction` | One or more defects block acceptance; every defect is listed in one consolidated list per the section below |
| Structural block | `blocked` | The task cannot proceed as scoped; routed to the Chief of Staff, not corrected by the current owner |

Grading applies only within Tiers 0–2. Tier 3 review keeps the binary
accept/return-for-correction discipline already used on PT58, without notes-only acceptance.

## Consolidated correction list

When a Tier 0–2 task is returned for correction, the review artifact contains one list with, for
every defect: what is wrong, where, and what acceptance requires. The owner addresses every listed
item in the same correction round. A defect discovered by the reviewer after that list is sent is
still in scope for the same round; the reviewer does not open a second round to add one more
finding once correction work has started, unless the newly found defect is itself Tier 3 (see
Escalation).

## Same-task correction allowance

Tiers 0–2 default to the `retry_policy` value "one consolidated correction round within the same
task," matching the pattern already recorded on `V05-PT-59` itself. A second round requires the
Chief of Staff to record why the first round was insufficient and either extend the same task with
a second bounded round or supersede it with a new task ID, exactly as `WORKLIST_PROCESS.md`
already requires for corrections in general.

## Escalation

Escalate to Tier 3 immediately, mid-task, whenever any of the following becomes true, regardless
of the task's original tier:

- a credential, secret, or token is needed or discovered in scope;
- any live network call to an external provider becomes necessary;
- a destructive, irreversible, merge, push, or release action becomes necessary;
- the task would modify `V05-PT-58`, its candidate, or an active safety gate;
- the owner or reviewer is unsure which tier applies.

Escalation means: stop, do not perform the newly discovered action, and route the task to the
Chief of Staff under the unmodified full process. This mirrors the stop-and-route behavior already
demonstrated on PT58 (Handoffs 215, 216, 218) and is not weakened by this pilot.

## Pilot measurement template

The Chief of Staff records these fields on each Tier 0–2 task piloted under this process, starting
with the first task the Product Owner selects at review of this document. This is descriptive
only; it does not gate acceptance.

| Field | How to record |
|---|---|
| Task ID | Worklist task ID |
| Assigned tier | 0, 1, or 2 |
| Handoff count | Number of handoff/review artifacts produced from `authorized` to terminal status |
| Elapsed time | Wall-clock time from `authorized` to `accepted`, `returned_for_correction`, or `blocked` |
| Correction rounds | Count of `returned_for_correction` cycles |
| Bundled preflight used | Yes/No, and whether any check had to be excluded from the bundle |
| Escalations triggered | Count, and which criterion in Escalation fired each time |
| Reviewer grade | Clean accept / accept with notes / bounded correction / structural block |
| External-input closure gate result | Closed on all six points / blocked on point N, named |
| Comparable full-process estimate | Chief of Staff's estimate of handoff count and elapsed time the same task would have taken under the unmodified process, for comparison |

After 3–5 piloted tasks, the Chief of Staff summarizes these fields for the Product Owner and
recommends: adopt as default for the piloted tier(s), narrow the tier definitions, or discontinue
the pilot and revert to the unmodified process for that tier.

## Pilot activation

This document defines and readies the process; it does not itself activate a pilot task. Per its
authorizing task, the Product Owner reviews this artifact and selects the first Tier 0–2 task to
run under it. `V05-PT-60` and `V05-PT-61` are documentation- and test-shaped candidates already in
the worklist as `proposed`; either remains subject to its own separate activation conditions and
Product Owner authorization independent of this pilot's adoption.

## Stop condition check

Per `V05-PT-59`'s stop condition, this document is void wherever it would remove an existing
safety control or conflict with an active task. Nothing above removes a credential, network,
destructive-action, live-provider, or release control, and nothing above modifies PT58, its code,
or its candidates. If a future edit to this document would do either, that edit requires the same
Product Owner authorization this document itself required, and the edit must restate this check.
