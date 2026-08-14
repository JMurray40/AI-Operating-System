# Agent Relay Process

| Field | Value |
|---|---|
| Purpose | Eliminate Product Owner copy-and-paste handoffs between agents |
| Canonical baton | `docs/coordination/CURRENT_HANDOFF.md` |
| Detailed evidence | Role-owned handoffs and evidence linked by the baton and active worklist |
| Authority | Routing aid only; never grants authority or overrides accepted artifacts |

## Core rule

Every agent reads the canonical baton before work and updates it before stopping. The baton is a
short pointer to repository evidence, not a duplicate narrative report. Conversation history and
Product Owner summaries are never required to resume work.

## Start protocol

1. Read `AGENTS.md`, `docs/coordination/README.md`, and `docs/coordination/CURRENT_HANDOFF.md`.
2. Open the active worklist named by the baton and run its validator.
3. Confirm the baton and worklist agree on task, status, owner, reviewer, and artifact paths.
4. Open the linked authority and incoming artifact. Neither the baton nor JSON grants authority.
5. Start only authorized or in-progress work assigned to your role.
6. If anything conflicts, stop and update the baton to `blocked` with the exact conflict.

## Return protocol

Before ending a work turn, the working agent:

1. writes the complete role-owned return or review artifact;
2. updates only the worklist transitions permitted to that role;
3. rewrites `CURRENT_HANDOFF.md` with the fixed fields in its template;
4. links evidence instead of copying it;
5. runs worklist, link, UTF-8, whitespace, and diff validation appropriate to the task; and
6. stops without authorizing dependent work unless the role has that authority.

The baton must stay under roughly 80 lines. Put tests, hashes, findings, and detailed reasoning in
the linked handoff, not in the baton.

## Standard agent return language

After the repository artifacts and baton are updated, the agent's entire user-facing return
should normally be:

```text
Task <TASK-ID>: <READY FOR REVIEW | BLOCKED | RETURNED FOR CORRECTION | ACCEPTED | SUPERSEDED | CANCELLED>.
Canonical baton updated: docs/coordination/CURRENT_HANDOFF.md
Detailed artifact: <repository-relative path>
Next role: <ROLE>. Product Owner action: <NONE | concise required action>.
```

Do not repeat test counts, hashes, findings, file inventories, implementation narratives, or
next-step instructions in chat. Those belong in the linked detailed artifact and baton. Add at
most one extra sentence only when immediate human action is required, such as approving UAC,
performing a private credential step, restarting the host, or deciding a material exception.

Use the disposition that describes the outcome accurately:

- `READY FOR REVIEW` means the task's acceptance criteria are claimed complete.
- `BLOCKED` means the attempt stopped and no reviewer should infer completion.
- `RETURNED FOR CORRECTION` means a reviewer found bounded defects.
- `ACCEPTED` may be used only by the assigned reviewer.
- `SUPERSEDED` means a preserved task was replaced by a separately authorized task.
- `CANCELLED` means controlling authority ended the task without replacement.

## Reviewer protocol

The reviewer independently verifies the linked return, produces a review artifact, updates the
reviewed task to `accepted` or `returned_for_correction`, and updates the baton. If the review is
accepted, the Chief of Staff may activate the next conditionally authorized task and make that
task the baton focus.

## Product Owner interaction

The normal Product Owner message is:

> It is your turn. Read `docs/coordination/CURRENT_HANDOFF.md` and follow the Agent Start Rule.

The Product Owner receives a substantive question only for a reserved human action, material
scope/cost/risk decision, exception, waiver, credential entry, or final disposition.

The Product Owner never needs to forward the prior agent's return. The next agent reads the baton
and repository artifacts directly.

## Required baton fields

- update timestamp and updating role;
- milestone and active worklist;
- current task ID, status, owner, and reviewer;
- latest completed or reviewed artifact;
- controlling authority;
- one-sentence current state;
- exact next role and required action;
- explicit prohibited work;
- validation command; and
- Product Owner action, normally `None`.

## Precedence and recovery

Accepted Product Owner decisions, ADRs, requirements, and handoffs outrank the baton and
worklist. If the baton is stale, the discovering agent must not infer permission. It records the
conflict, leaves executable work stopped, and routes correction to the Chief of Staff.
