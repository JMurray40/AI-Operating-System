# Jarvis Project Control and Handoff Index

| Field | Value |
|---|---|
| Purpose | Give every contributor one reliable starting point for current scope, ownership, handoffs, blockers, and decisions |
| Status | Active |
| Owner | Chief of Staff |
| Product Owner | Jason Murray |
| Updated | 2026-08-09 |
| Governing documents | [Governance](../GOVERNANCE.md), [Ways of Working](../WAYS_OF_WORKING.md), [Operating Handbook](../../Operating%20Handbook%20-%20AI%20Agent%20Roles.md) |

## Start here

Every role starts a new assignment by reading this file. Do not rely on conversation
history for project state.

1. Open the canonical [Current Handoff](CURRENT_HANDOFF.md).
2. Confirm the active worklist, task, assigned role, latest artifact, and required action there.
3. Open the linked incoming artifact and governing PRDs, ADRs, and requirements.
4. Verify the branch, base commit, scope, exclusions, and acceptance evidence before work.
5. Produce the required outgoing handoff file before declaring the stage complete.
6. Update the Current Handoff before stopping. Follow the
   [Agent Relay Process](AGENT_RELAY_PROCESS.md).

The Product Owner does not relay detailed agent reports. Ordinarily, the Product Owner tells
the next agent only: **“It is your turn. Read `docs/coordination/CURRENT_HANDOFF.md`.”**
Agents likewise return only the standard concise status defined in the
[Agent Relay Process](AGENT_RELAY_PROCESS.md); detailed output stays in the repository.

## Active machine-readable work queue

The current operational queue is
[v0.5 Full Certification](worklists/v0.5-certification.json). The predecessor
[v0.5 Visible-Context Conversation queue](worklists/v0.5.json) is closed and retained as
history. Every contributor must read the active queue and
run the offline validator before beginning or returning assigned work:

```text
python scripts/validate_worklist.py docs/coordination/worklists/v0.5-certification.json
```

Follow [the Version Worklist Process](WORKLIST_PROCESS.md). Start only a task assigned to your
role whose status is `authorized` or `in_progress`. The JSON queue does not grant authority:
open and verify the linked authorization artifact. An owner may mark its work in progress or
ready for review, but only the assigned reviewer may accept it, and only the Chief of Staff may
authorize the next task.

The narrative program-state sections below are retained historical context and may lag the
active worklist. Where they differ, use the worklist to locate the latest handoff, then apply the
project's normal artifact precedence. Never treat the worklist itself as higher authority.

If this index conflicts with an accepted Product Owner decision, ADR, PRD, roadmap, or
governance document, follow the order of precedence in
[Governance](../GOVERNANCE.md) and record the conflict for escalation.

## Current program state

### Active priority: v0.3.1 — Query Trust Contracts

| Item | Current state |
|---|---|
| Product Owner direction | Complete v0.3.1 before advancing the release sequence |
| Requirements | [v0.3.1 Query Trust Contracts Requirements](../software/V0.3.1_QUERY_TRUST_CONTRACTS_REQUIREMENTS.md) |
| Current incoming handoff | [Chief of Staff to CTO](../handovers/v0.3.1/00-chief-of-staff-to-cto-finalize-implementation-brief.md) |
| Requirements status | Accepted by Product Owner on 2026-07-27 |
| Trust-contract ADRs | [ADR-0014](../adr/ADR-0014-Retrieval-Relevance-Is-Separate-From-Answer-Confidence.md), [ADR-0015](../adr/ADR-0015-Authorization-Precedes-Retrieval-And-Graph-Expansion.md), [ADR-0016](../adr/ADR-0016-Citations-Bind-Passages-To-Source-Revisions.md), and [ADR-0017](../adr/ADR-0017-Stable-Source-Identity-Is-Separate-From-Location.md) — accepted |
| Product Owner decision | [Architecture approval](../handovers/v0.3.1/01-product-owner-to-cto-architecture-approval.md) |
| Implementation brief | [CTO implementation brief](../handovers/v0.3.1/02-cto-to-principal-engineer-implementation-brief.md) — content-complete; Chief of Staff validation blocked by base/artifact contradiction |
| Principal Engineer work | Not authorized to begin until an implementation-ready brief is accepted |
| QA review | Not started |
| Librarian pass | Not started |
| Primary gate | Close ARB conditions C1–C5 before conversational/generated-answer release |

**Next responsible role:** Chief Architect / CTO

**Required next actions:**

1. Establish a clean documentation commit containing the accepted governance, ADR,
   requirements, coordination, and handoff artifacts without disturbing the parked
   conversation worktree.
2. CTO repins the implementation brief to that documentation commit.
3. Chief of Staff completes validation and issues the Principal Engineer prompt package.

### Parked candidate: conversational implementation currently named v0.4

| Item | Current state |
|---|---|
| Branch | `feature/v0.4-conversation` |
| Workspace HEAD observed by Chief of Staff | `4b09050b76fd9a448af3ce91b4aa66963d23dad2` |
| Engineering | Principal Engineer reports implementation complete |
| Engineering report | [v0.4 Implementation Report](../software/V0.4_IMPLEMENTATION_REPORT.md) |
| Existing QA review | [Quality & Release Review](../reviews/QUALITY_RELEASE_REVIEW_V0.4_CONVERSATION_2026-07-27.md) — **Not ready** |
| Release status | Parked; do not merge or release |
| Sequencing decision | v0.3.1 is completed first |
| Known blockers | Trust-contract C1/C3, trace numbering, streaming scope/evidence, complete re-review package, release-name reconciliation |

The existing QA review says the implementation report was absent at review time; the report
now exists. This does not invalidate the other findings. QA must perform a fresh review only
after v0.3.1 is complete and the conversation candidate has been reconciled with the approved
release sequence and trust contracts.

## Role queue

| Order | Role | Assignment | Incoming artifact | Required outgoing artifact |
|---:|---|---|---|---|
| 1 | Chief Architect / CTO | Finalize architecture and implementation gates for v0.3.1 | Requirements and accepted ADRs | Accepted implementation brief and architect-to-engineer handoff |
| 2 | Chief of Staff | Check brief completeness, contradictions, dependencies, and prompt clarity | CTO brief | Validated Principal Engineer prompt package |
| 3 | Principal Engineer / Claude | Implement only the accepted v0.3.1 scope | Validated brief and prompt package | Engineering review and engineer-to-architect handoff |
| 4 | Chief Architect / CTO | Conduct architecture fitness/conformance review | Engineering evidence | Architecture disposition and architect-to-QA handoff |
| 5 | Quality & Release | Adversarially assess release evidence | Architecture disposition and engineering evidence | One formal release disposition and QA-to-Product-Owner handoff |
| 6 | Product Owner | Approve, return, stop, or re-scope | QA disposition | Recorded Product Owner decision |
| 7 | Historian / Librarian | Reconcile documentation after approval/merge | Product Owner decision and merged scope | Repository health/drift report and release-to-Librarian handoff |

No downstream role should start from a verbal summary when the required incoming artifact is
missing.

## Handoff storage convention

New milestone handoffs belong under:

```text
docs/handovers/<milestone>/
```

Use this filename:

```text
<sequence>-<sender-role>-to-<receiver-role>-<short-purpose>.md
```

Examples:

```text
docs/handovers/v0.3.1/01-product-owner-to-cto-architecture-approval.md
docs/handovers/v0.3.1/02-cto-to-principal-engineer-implementation-brief.md
docs/handovers/v0.3.1/03-principal-engineer-to-cto-engineering-review.md
docs/handovers/v0.3.1/04-cto-to-quality-architecture-disposition.md
docs/handovers/v0.3.1/05-quality-to-product-owner-release-review.md
docs/handovers/v0.3.1/06-product-owner-to-librarian-release-decision.md
docs/handovers/v0.3.1/07-librarian-to-product-owner-repository-closeout.md
```

Use lowercase milestone and role names, two-digit sequence numbers, and Markdown. Do not
overwrite an accepted handoff; add a revision history or a new superseding artifact.

## Required handoff contract

Every handoff must contain:

1. **Sender, receiver, milestone, date, and status.**
2. **Objective and completed scope.**
3. **Repository, branch, base commit, and reviewed/produced commit.**
4. **Authoritative inputs** — linked PRDs, ADRs, requirements, and decisions.
5. **Artifacts produced** — exact repository paths.
6. **Acceptance evidence** — tests, checks, benchmarks, and review results.
7. **Known risks, defects, technical debt, and deviations.**
8. **Explicit exclusions and forbidden next work.**
9. **Unresolved decisions** — owner and blocking impact.
10. **Required next actions** — assigned to the receiving role.
11. **Exit statement** — ready, ready with conditions, blocked, or returned.

The receiver verifies the artifact against the repository rather than trusting its claims.

## Prompt-package contract

When the Chief of Staff prepares a role prompt, it must:

- name the role and its primary question;
- link this control page and the incoming handoff;
- state the exact objective, branch, commit, scope, and exclusions;
- identify the authoritative artifacts in precedence order;
- specify required evidence and the outgoing handoff path;
- prohibit silent scope changes and require written escalation;
- remind the role that conversation history is not authoritative.

Prompts coordinate work; they do not override governance or grant authority.

## Decisions awaiting Product Owner

| Decision | Needed by | Current recommendation |
|---|---|---|
| v0.3.1 requirements and implementation authorization | Approved 2026-07-27 | Recorded |
| ADR-0014 through ADR-0017 | Approved 2026-07-27 | Recorded |
| Release identity | Approved 2026-07-27 | Project Resume is v0.4; visible-context conversation moves to v0.5 |
| Streaming in the first conversation release | Before conversation rework | Defer provider-response streaming unless it is necessary to validate the core workflow |

## Chief of Staff maintenance rules

The Chief of Staff updates this page when:

- the Product Owner changes priority or scope;
- a handoff is accepted, rejected, or superseded;
- responsibility moves to the next role;
- a blocker or required decision appears;
- a release is merged or closed by the Librarian.

This page records coordination state only. It does not accept architecture, approve a
release, or replace the artifacts owned by the other roles.
