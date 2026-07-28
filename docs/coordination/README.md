# Jarvis Project Control and Handoff Index

| Field | Value |
|---|---|
| Purpose | Give every contributor one reliable starting point for current scope, ownership, handoffs, blockers, and decisions |
| Status | Active |
| Owner | Chief of Staff |
| Product Owner | Jason Murray |
| Updated | 2026-07-27 |
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

### Active priority: v0.3.1 — Query Trust Contracts

**Latest effective handoff state:** [v0.3.1 Handoff Index](../handovers/v0.3.1/README.md)

| Item | Current state |
|---|---|
| Product Owner direction | Complete v0.3.1 before advancing the release sequence |
| Requirements | [v0.3.1 Query Trust Contracts Requirements](../software/V0.3.1_QUERY_TRUST_CONTRACTS_REQUIREMENTS.md) |
| Current incoming handoff | [Superseding Quality & Release Review](../handovers/v0.3.1/05-quality-to-product-owner-release-review.md) |
| Requirements status | Accepted by Product Owner on 2026-07-27 |
| Trust-contract ADRs | [ADR-0014](../adr/ADR-0014-Retrieval-Relevance-Is-Separate-From-Answer-Confidence.md), [ADR-0015](../adr/ADR-0015-Authorization-Precedes-Retrieval-And-Graph-Expansion.md), [ADR-0016](../adr/ADR-0016-Citations-Bind-Passages-To-Source-Revisions.md), and [ADR-0017](../adr/ADR-0017-Stable-Source-Identity-Is-Separate-From-Location.md) — accepted |
| Product Owner decision | [Architecture approval](../handovers/v0.3.1/01-product-owner-to-cto-architecture-approval.md) |
| Implementation brief | [CTO implementation brief](../handovers/v0.3.1/02-cto-to-principal-engineer-implementation-brief.md) — validated |
| Engineer prompt package | [Chief of Staff validation and prompt](../handovers/v0.3.1/02-chief-of-staff-to-principal-engineer-validated-prompt.md) |
| Principal Engineer work | Executable candidate complete at `956c2ed`; evidence retained at `8fa5f18` |
| CTO disposition | Ready for limited revalidation; QR-031-01 through QR-031-03 closed |
| QA review | [Ready; superseding Areas A/G/H revalidation complete](../handovers/v0.3.1/05-quality-to-product-owner-release-review.md) |
| QA prompt | [Chief of Staff limited revalidation](../handovers/v0.3.1/07-chief-of-staff-to-quality-limited-revalidation.md) — completed |
| Librarian pass | Not started |
| Primary gate | Close ARB conditions C1–C5 before conversational/generated-answer release |

**Next responsible role:** Product Owner — release go/no-go decision

**Required next actions:**

1. Review the superseding QA disposition and its disclosed residual risks.
2. Decide whether to approve, return, stop, or re-scope exact executable `956c2ed` with
   evidence commit `8fa5f18`.
3. If approved, record the Product Owner decision before any merge, push, or release.
4. Route approved release execution and subsequent Librarian closeout as separate gates.

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
