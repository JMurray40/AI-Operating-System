# Jarvis Project Control and Handoff Index

| Field | Value |
|---|---|
| Purpose | Give every contributor one reliable starting point for current scope, ownership, handoffs, blockers, and decisions |
| Status | Active |
| Owner | Chief of Staff |
| Product Owner | Jason Murray |
| Updated | 2026-08-01 |
| Governing documents | [Governance](../GOVERNANCE.md), [Ways of Working](../WAYS_OF_WORKING.md), [Operating Handbook](../../Operating%20Handbook%20-%20AI%20Agent%20Roles.md) |
| Handoff router | [Global handoff router](../handovers/README.md) |

## Start here

Every role starts a new assignment by reading this file. Do not rely on conversation
history for project state.

1. Confirm the active milestone and assigned role below.
2. Open the linked incoming artifact.
3. Read the governing PRDs, ADRs, and requirements named by that artifact.
4. Verify the branch, base commit, scope, exclusions, and acceptance evidence before work.
5. Produce the required outgoing handoff file before declaring the stage complete.
6. Tell the Chief of Staff where the handoff was written so this index can be updated.

If this index conflicts with an accepted Product Owner decision, ADR, PRD, roadmap, or
governance document, follow the order of precedence in
[Governance](../GOVERNANCE.md) and record the conflict for escalation.

## Current program state

### Active priority: v0.4 — released; repository closeout awaiting validation

**Latest effective handoff state:** [v0.4 Handoff Index](../handovers/v0.4/README.md)

| Item | Current state |
|---|---|
| Current incoming handoff | [Librarian Repository Closeout](../handovers/v0.4/43-librarian-to-product-owner-v0.4-repository-closeout.md) |
| Acceptance tests | [Accepted v0.4 Project Resume tests](../product/V0.4_PROJECT_RESUME_ACCEPTANCE_TESTS.md) |
| Planning brief | [CTO Project Resume planning brief](../handovers/v0.4/00-cto-to-principal-engineer-project-resume-planning-brief.md) |
| Planning validation | [Chief of Staff validation](../handovers/v0.4/00-chief-of-staff-project-resume-planning-validation.md) |
| v0.3.1 release | Complete as `v0.3.1` |
| v0.4 release | Published as annotated tag `v0.4.0` from integrated release commit `6cf9b72355d65768d3ea549a5af34006e2b6d3b6` |
| Frozen executable | `ff402d7f82c061426a5e960f7177d916c355bbf2` (tree `a7ff2c023b0e59df1f8bbc2ad05a3af843a5e344`) |
| Evidence / final QA | `2c0e1204fb47d81fe8c7b873c973dd8c6026201b` / `cc43b0e918bc0164089b7d7120c92095058cc618` (`Ready`) |
| Repository activity | [Fixtures plus local read-only Git](../handovers/v0.4/00-product-owner-repository-activity-scope-decision.md); live GitHub excluded |
| Current gate | Chief of Staff validation of the Librarian closeout commit |
| A11 strategic outcome | Eight-week dogfood outcome remains pending and unproven |
| v0.5 conversation | Planning may begin after closeout validation; implementation remains unauthorized |

**Next responsible role:** Chief of Staff — validate the documentation-only closeout commit

**Required next actions:**

1. Verify the Librarian commit changes documentation only and preserves the released identities.
2. Validate repository navigation, latest-effective handoff routing, links, and whitespace.
3. Accept or return the closeout explicitly.
4. If accepted, authorize v0.5 planning separately; do not infer implementation authority.

### Parked candidate: conversation branch with historical v0.4 identity

| Item | Current state |
|---|---|
| Branch | `feature/v0.4-conversation` |
| Workspace HEAD observed by Chief of Staff | `4b09050b76fd9a448af3ce91b4aa66963d23dad2` |
| Engineering | Principal Engineer reports implementation complete |
| Engineering report | [v0.4 Implementation Report](../software/V0.4_IMPLEMENTATION_REPORT.md) |
| Existing QA review | [Quality & Release Review](../reviews/QUALITY_RELEASE_REVIEW_V0.4_CONVERSATION_2026-07-27.md) — **Not ready** |
| Release status | Parked; do not merge or release |
| Sequencing decision | Project Resume is v0.4; conversation is planned for v0.5 |
| Known blockers | Trust-contract C1/C3, trace numbering, streaming scope/evidence, complete re-review package, release-name reconciliation |

The existing QA review says the implementation report was absent at review time; the
historical report now exists. This does not invalidate the other findings. QA must perform
a fresh review only after the candidate has been reconciled as v0.5 with the approved
sequence and released trust contracts.

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
