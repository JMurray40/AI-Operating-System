# Handoff 00 — Chief of Staff to CTO: v0.5 Conversation Planning Authorization

**From:** Chief of Staff
**To:** Chief Architect / CTO
**Date:** 2026-08-01
**Milestone:** v0.5 — visible-context conversation
**Base:** `main` at `0fda11812144e758f7fc11462a8bdf70ccdff9ec`
**Disposition:** **AUTHORIZED — ARCHITECTURE AND PRODUCT-SCOPE PLANNING ONLY**

## 1. Closeout validation

The v0.4 Librarian closeout commit is accepted.

Independent Chief-of-Staff validation confirmed:

- exactly 12 changed Markdown paths and no executable, test, script, evidence, packaging,
  ADR-substance, wheel, pilot, or classification change;
- 216 Markdown files and 514 repository-local links checked with zero broken targets;
- `git diff --check` passed;
- annotated tag `v0.4.0` remains unchanged and peels to
  `6cf9b72355d65768d3ea549a5af34006e2b6d3b6`;
- executable `ff402d7`, evidence remediation `2c0e120`, and final Quality `cc43b0e`
  remain ancestors of `main`;
- the documented release sequence is v0.3, v0.3.1, v0.4, then v0.5; and
- A11's eight-week outcome remains pending and unproven.

The closeout disposition `Ready for v0.5 planning` is accepted. It does not authorize
v0.5 implementation.

## 2. Planning objective

Produce the architecture and Product Owner decision package for a trustworthy
visible-context conversation release built on the released Query Trust Contracts and
Project Resume foundations.

The primary question is:

> What is the smallest coherent v0.5 conversation scope that exposes authorized context
> and evidence truthfully, preserves read-only and privacy boundaries, and can be tested
> without silently inheriting obsolete v0.4 candidate assumptions?

## 3. Authoritative inputs

Read in this order:

1. [Project Control](../../coordination/README.md);
2. [Operating Handbook](../../../Operating%20Handbook%20-%20AI%20Agent%20Roles.md);
3. this planning authorization;
4. [Chat Interface PRD](../../prd/CHAT_INTERFACE.md), treating its status, target, and
   scope as draft inputs requiring reconciliation;
5. [Historical conversation Quality review](../../reviews/QUALITY_RELEASE_REVIEW_V0.4_CONVERSATION_2026-07-27.md);
6. [Historical implementation report](../../software/V0.4_IMPLEMENTATION_REPORT.md);
7. accepted ADR-0014 through ADR-0017 and released v0.3.1 trust-contract requirements;
8. ADR-0018 through ADR-0021 and released Project Resume contracts where conversation
   context selection or repository evidence depends on them; and
9. current roadmap, limitations, architecture, CLI, testing, privacy, and governance
   documentation on released `main`.

Conversation history is not authoritative.

## 4. Historical candidate boundary

Historical branch `feature/v0.4-conversation` remains at:

`4b09050b76fd9a448af3ce91b4aa66963d23dad2`

The CTO may inspect that commit and compare it read-only with released `main`. Planning
must explicitly classify each reusable concept, obsolete assumption, architectural
conflict, security gap, and test/evidence gap.

Do not:

- create a v0.5 implementation branch or worktree;
- modify, merge, cherry-pick, rebase, rename, tag, or push the historical branch;
- change code, tests, scripts, packaging, evidence, pilots, or classifications;
- treat the historical implementation or its old passing tests as accepted v0.5 evidence;
  or
- assume that the prior v0.4 name, PRD target, streaming promise, provider behavior, or
  conversation-store design remains approved.

## 5. Required planning decisions

The CTO package must make recommendations and identify Product Owner approvals required
for at least:

1. exact v0.5 user-visible scope and non-goals;
2. whether the first release includes real provider-response streaming or explicitly
   defers it;
3. whether v0.5 is CLI-only, adds an application API, or includes a UI surface;
4. provider strategy, including mock/local versus real adapters and network evidence;
5. operational conversation persistence, retention, encryption, export, archive, and
   deletion boundaries;
6. context inspection/removal, immutable context snapshots, and retry semantics;
7. authorization and egress-policy ordering before retrieval, graph expansion, prompt
   assembly, or provider dispatch;
8. retrieval relevance versus answer-confidence semantics;
9. passage/revision citation and generated-claim support requirements;
10. prompt-injection and untrusted-content treatment;
11. trace numbering, trace privacy, cost/usage, failure, cancellation, and degradation
    contracts;
12. read-only vault guarantees and any permitted operational-store writes;
13. performance, accessibility, packaging, recovery, privacy, and adversarial acceptance
    gates; and
14. migration treatment for historical conversation contracts and data, if any.

Do not silently select a materially broader scope where Product Owner choice is required.

## 6. Required deliverables

Produce documentation only:

1. a reconciled v0.5 conversation planning brief or requirements document;
2. proposed ADRs or explicit amendments only where an architectural decision is genuinely
   required;
3. a requirement-to-evidence and adversarial security matrix;
4. a historical-candidate disposition with reusable and rejected portions;
5. a Product Owner decision list with recommendations and consequences; and
6. outgoing handoff:
   `docs/handovers/v0.5/01-cto-to-product-owner-conversation-planning-disposition.md`.

Every artifact must remain proposed until Product Owner approval. Do not prepare an
engineering implementation prompt or claim implementation readiness.

## 7. Stop conditions

Stop and escalate on:

- any need to change an accepted ADR rather than propose an explicit amendment;
- inability to preserve ADR-0015 authorization-before-retrieval/dispatch;
- ambiguity over whether private or unclassified content may leave the local trust
  boundary;
- any proposed vault write;
- any hidden provider/network/telemetry behavior;
- any attempt to reuse historical evidence without exact applicability proof; or
- any requirement to begin implementation to answer a planning question.

## 8. Exit condition

Planning is complete only when the CTO provides a coherent recommended scope, proposed
architecture, explicit Product Owner decisions, evidence matrix, candidate disposition,
and the required outgoing handoff.

The next gate is Product Owner approval followed by separate Chief-of-Staff validation.
No Principal Engineer work begins from this authorization.
