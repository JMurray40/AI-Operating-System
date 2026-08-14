# Version Worklist Process

| Field | Value |
|---|---|
| Purpose | Give humans and AI agents one validated operational queue for a milestone |
| Owner | Chief of Staff |
| Applies to | Jarvis and reusable future projects |
| Authority | Coordination aid; never a substitute for governance, decisions, ADRs, briefs, or handoffs |

## Why this exists

Handoffs explain decisions and preserve evidence, but a long handoff chain is inefficient as a
daily task queue. A version worklist answers five immediate questions:

1. What is the next authorized task?
2. Who owns it?
3. What must already be accepted?
4. What evidence and output are required?
5. Where must the agent stop?

The worklist is deliberately machine-readable so it can be validated before an agent starts.
It is deliberately not authoritative so editing JSON cannot grant permission or accept work.

For environment-heavy or multi-stage work, pair the worklist with the
[End-to-End Readiness Process](END_TO_END_READINESS_PROCESS.md). New projects should use schema
1.1 and complete readiness before activating execution.

## Files

```text
docs/coordination/worklists/
  README.md                    # quick start
  schema.json                  # structural contract
  templates/worklist.json      # reusable starting template
  v0.5.json                    # active Jarvis queue
scripts/validate_worklist.py   # offline structural and lifecycle checks
```

For another repository, copy `schema.json`, the template, validator, and this document. Change
the project, repository, milestone, roles, and paths; keep the lifecycle and authority rules.

## Source-of-truth boundary

The order of precedence remains:

1. recorded Product Owner decision;
2. accepted ADR;
3. accepted PRD or requirements;
4. roadmap;
5. Ways of Working;
6. implementation brief or handoff;
7. version worklist.

The worklist mirrors the current result of those artifacts. When it conflicts with one, the
higher artifact wins and the Chief of Staff corrects the worklist. An agent must never use a
JSON status as proof of authority without opening `authorization.artifact`.

## Status lifecycle

| Status | Meaning | Who may set it |
|---|---|---|
| `proposed` | Candidate work; not authorized | Chief of Staff |
| `blocked` | Known work whose dependencies or decision are incomplete | Chief of Staff or reviewer |
| `authorized` | A recorded artifact permits the owner to begin | Chief of Staff after verifying authority |
| `in_progress` | The authorized owner has begun | Assigned owner |
| `ready_for_review` | Owner stopped and produced the required return | Assigned owner |
| `returned_for_correction` | Reviewer found bounded defects | Assigned reviewer |
| `accepted` | Reviewer accepted the evidence under recorded authority | Assigned reviewer |
| `superseded` | A newer task or decision replaces this item | Chief of Staff |
| `cancelled` | Product Owner or controlling authority ended the work | Chief of Staff after recording the decision |

Engineering may move its own item only from `authorized` to `in_progress` to
`ready_for_review`. Engineering cannot mark its work `accepted`, authorize a blocked item,
change dependencies, or expand scope. Reviewers cannot silently add implementation work; they
return a task or create a new bounded remediation item through the Chief of Staff.

## Task contract

Every task contains:

- stable ID, title, workstream, priority, owner, reviewer, and status;
- an authorization state, decision identifier, and artifact path;
- dependency task IDs and explicit blockers;
- exact incoming and outgoing handoffs;
- scope and exclusions;
- acceptance criteria, evidence, and stop conditions;
- relevant repository identity when code or artifacts are candidate-bound; and
- append-only history showing who changed state, when, why, and from which artifact.

IDs remain stable even when a title changes. Use `<MILESTONE>-<STREAM>-<NN>`, for example
`V05-PKG-03`. Never reuse an ID from a superseded or cancelled task.

## Operating procedure

### Complete readiness before execution

1. Define the complete end-to-end outcome, not only the next task.
2. Inventory every environment, tool/version, privilege, network control, human action, evidence,
   fallback, retry, rollback, and cleanup requirement in a readiness packet.
3. Run one consolidated read-only preflight covering the entire route.
4. Resolve every unknown or record an explicit Product Owner waiver.
5. Group work into execution waves and obtain one conditional authorization envelope.
6. Mark readiness `ready` only when `unresolved` is empty.
7. Activate only the first covered task.

The validator rejects an active schema-1.1 execution task while readiness is not `ready`.

### Chief of Staff creates or updates the queue

1. Read the latest accepted handoff and Product Owner decision.
2. Decompose work into independently reviewable tasks.
3. Add dependencies before authorizing downstream work.
4. Mark only the current executable task `authorized` or `in_progress`.
5. Link every authority and required return.
6. Run the validator.
7. Update `current_focus_ids` and the coordination-page pointer.

### An assigned agent starts

1. Read `docs/coordination/README.md` and the active worklist.
2. Find tasks whose `owner_role` matches the assigned role.
3. Start only a task with status `authorized` or resume one marked `in_progress`.
4. Open and verify the authorization artifact, dependencies, repository identity, scope,
   exclusions, evidence, output handoff, and stop conditions.
5. If any fact conflicts or is missing, stop and report it; do not repair the worklist silently.
6. Change the task to `in_progress`, append a history entry, and run validation.

### An assigned agent returns work

1. Produce the exact outgoing handoff and evidence.
2. Stop at the named review gate.
3. Change only its task to `ready_for_review` and append a history entry.
4. Update `docs/coordination/CURRENT_HANDOFF.md` with the return path, next role, and required
   review action, following `docs/coordination/AGENT_RELAY_PROCESS.md`.
5. Do not unlock or start the dependent task.
6. Run validation.
7. Return only the standard four-line relay message from `AGENT_RELAY_PROCESS.md`. The Product
   Owner need not copy the return text between agents.

### Reviewer and Chief of Staff route the next task

1. Independently verify the return.
2. Set the reviewed task to `accepted` or `returned_for_correction` with the review artifact.
3. Re-evaluate dependencies.
4. Only the Chief of Staff changes the next task from `blocked` to `authorized`, after confirming
   a real authorization artifact exists.
5. Update focus and `docs/coordination/CURRENT_HANDOFF.md`, then validate again.

## Concurrency

More than one item may be active only when their scopes, worktrees, evidence paths, and decision
boundaries are independent. `concurrency_group` identifies tasks that must not overlap. Within a
group, at most one task may be `authorized`, `in_progress`, or `ready_for_review` unless the
worklist explicitly sets `allow_parallel_in_group` to true and cites the authorizing artifact.

## Corrections and supersession

Do not rewrite history to make an earlier task look successful. Preserve it and either:

- move it to `returned_for_correction`, then back through the lifecycle; or
- mark it `superseded` and create a new task with `supersedes` pointing to the old ID.

The validator rejects missing dependencies, duplicate IDs, impossible accepted states, circular
dependencies, unauthorized active work, and broken repository-relative artifact paths.

## Pull-request and commit practice

Ordinary task progress should update the worklist in the same logical commit as its handoff when
that is safe. A candidate executable commit should not be polluted merely to update coordination;
use the coordination worktree or an evidence-only descendant as the governing handoff requires.

## Minimal adoption checklist for another project

1. Copy the process, worklists directory, and validator.
2. Define role names and artifact precedence.
3. Create a schema-1.1 milestone file and readiness packet from the templates.
4. Enter already-completed work as `accepted` with real evidence links.
5. Enter future work as `proposed` or `blocked`.
6. Complete the consolidated readiness audit and conditional authorization envelope.
7. Authorize only the first executable task after readiness is `ready`.
8. Add “read and validate the active worklist” to the project's agent-start rules.
9. Run the validator in local checks or CI.
