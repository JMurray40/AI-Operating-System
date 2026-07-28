# Version Roadmap: v0.2–v2.0

| Field | Value |
|---|---|
| Purpose | Sequence product releases with implementable acceptance gates |
| Status | Active planning record; near-term sequence approved |
| Version | 0.3.0 |
| Owner | Chief Product Officer |
| Revised | 2026-07-27 |
| Related | [Product Strategy](PRODUCT_STRATEGY.md), [Roadmap](../ROADMAP.md), [Architecture Review](../reviews/ENTERPRISE_ARCHITECTURE_REVIEW.md) |

## Estimation model

Effort is expressed as focused engineer-weeks, excluding external security audits and store approvals. Estimates assume one experienced engineer assisted by AI, reviewed by a human maintainer. Release gates are evidence-based; dates should not override failed acceptance criteria.

## Current approved near-term sequence

This sequence supersedes the original v0.3–v0.5 numbering while preserving its historical
product intent:

| Release | Current identity | State |
|---|---|---|
| v0.3 | Query Engine foundation | Merged |
| v0.3.1 | Query Trust Contracts | Released |
| v0.4 | Read-only Project Resume CLI Pilot | Planning validated; implementation blocked |
| v0.5 | Visible-Context Conversation | Parked candidate requires reconciliation and fresh authorization |

The originally planned v0.3 chat/provider scope moved to v0.5. Proposed Memory moved
beyond v0.5; its exact release number requires a future Product Owner decision.

## v0.2 — Indexed Retrieval Foundation

**Objectives:** Make larger vaults fast and queryable while preserving the read-only guarantee.

**Major features:** Published context-package schema; SQLite FTS index; incremental hash-based indexing; lexical search CLI; block/heading locators; benchmark corpus; strict JSON Schema option.

**Dependencies:** v0.1 parser contracts; ADRs for context schema, index projection, Python floor.

**Risks:** Index drift, SQLite limits, accidental canonical-state leakage, schema churn.

**Effort:** 4–6 engineer-weeks.

**Acceptance criteria:**

- 100,000-note synthetic corpus indexes deterministically and incrementally.
- Search p95 under 500 ms on reference hardware.
- Deleting the index and rebuilding produces equivalent logical results.
- Source files remain byte-identical.
- Benchmark precision@10 and recall targets are documented and pass.

## v0.3 — Query Engine Foundation

**Objectives:** Provide deterministic, explainable, read-only retrieval and provenance.

**Delivered features:** Layered lexical query pipeline; deterministic ranking; source-note
citations; token-budgeted context; trace mode; `ask`, `search`, `summarize`, and `explain`.

**Deferred from the original milestone:** Local/streaming chat, conversation storage,
cloud/Ollama adapters, cost/latency capture, and provider egress controls moved to v0.5.

**Historical note:** The original title was “Read-only Chat and Provenance.” The merged
release completed the Query Engine/provenance foundation, not that entire original scope.

## v0.3.1 — Query Trust Contracts

**Objectives:** Harden the merged query engine before Project Resume or generated answers
expand its trust boundary.

**Delivered features:** Explicit authorization scope before retrieval/graph expansion;
relative relevance separated from answer confidence; passage-and-revision citations;
stable source identity; strict context budgets; versioned result/context/trace contracts.

**State:** Released as `v0.3.1` from merge `00f1813`. Product Owner approved, QA issued
`Ready`, and the Librarian issued `Ready for final release`.

## v0.4 — Read-only Project Resume CLI Pilot

**Objectives:** Make project resumption the first daily-use workflow.

**Planned features:** Deterministic sourced Resume briefing; project status, decisions,
sessions, resources, and missing-context warnings; fixtures plus local read-only Git only.

**Dependencies:** Released v0.3.1 trust contracts; accepted Project Resume tests;
repository-activity scope decision; explicit implementation authorization.

**Risks:** Stale summaries, overly broad context, weak project identity matching.

**Effort:** 5–7 weeks.

**Acceptance criteria:** Pilot projects generate sourced briefings in under 30 seconds; user rates ≥80% as useful; missing/ambiguous project matches are surfaced rather than guessed.

## v0.5 — Visible-Context Conversation

**Objectives:** Add inspectable conversation only after the trust contracts and Project
Resume path are proven.

**Planned features:** Visible context, evidence-backed responses, local API, provider/egress
controls, retained/deletable conversation state, cost/latency capture, and streaming only
if separately accepted.

**Dependencies:** Released trust contracts; fresh architecture/QA review; reconciliation of
the parked `feature/v0.4-conversation` candidate; [Chat PRD](../prd/CHAT_INTERFACE.md).

**Risks:** Context leakage, citation mismatch, provider lock-in, uncontrolled cost, and
confusion between temporary conversation state and durable memory.

**Acceptance criteria:** Requires a future accepted brief. No v0.5 implementation is
authorized by this roadmap reconciliation.

## v0.6 — Semantic Search and Relationship Intelligence

**Objectives:** Find meaningful overlap beyond exact terms.

**Major features:** Hybrid ranking; local embeddings; entity extraction; relationship candidates; contradiction candidates; relevance feedback.

**Dependencies:** v0.2 index abstraction; benchmark and privacy policy.

**Risks:** False connections, embedding exposure, opaque ranking, high compute.

**Effort:** 7–10 weeks.

**Acceptance criteria:** Hybrid retrieval materially outperforms lexical baseline; findings show evidence and confidence; embeddings are rebuildable and sensitivity-scoped.

## v0.7 — Plugin and MCP Foundations

**Objectives:** Add integrations without coupling them to core.

**Major features:** Out-of-process plugin host; signed manifest; capability grants; event contracts; MCP client gateway; connector health; compatibility tests.

**Dependencies:** Plugin SDK approval; permission engine; secrets broker.

**Risks:** Supply chain compromise, protocol confusion, unbounded capability.

**Effort:** 10–14 weeks plus penetration testing.

**Acceptance criteria:** A malicious reference plugin cannot read undeclared paths or secrets; plugin failure cannot crash core; MCP tools are normalized and policy checked.

## v0.8 — Agent Framework

**Objectives:** Support bounded specialist reasoning with observable plans.

**Major features:** Agent manifests; task budgets; shared artifact protocol; delegation limits; checkpoints; cancellation; evaluation harness; eight reference agent profiles.

**Dependencies:** v0.7 capabilities; [Agent Framework PRD](../prd/AGENT_FRAMEWORK.md).

**Risks:** Recursive delegation, cost explosions, responsibility ambiguity, unsafe tool composition.

**Effort:** 10–14 weeks.

**Acceptance criteria:** Every action traces to one user task and capability grant; depth, cost, time, and tool budgets are enforced; cancellation reaches all children.

## v0.9 — Automation Preview

**Objectives:** Run narrow repeatable workflows safely.

**Major features:** Durable workflow definitions; scheduler; triggers; idempotency; approval nodes; retry/dead-letter queues; execution dashboard.

**Dependencies:** v0.7 plugin host; v0.8 agents; operational database migrations.

**Risks:** Duplicate effects, stale approvals, missed triggers, background privacy violations.

**Effort:** 10–13 weeks.

**Acceptance criteria:** Reference workflows survive restart, never duplicate external effects, and produce complete audit records; schedules do not bypass approvals.

## v1.0 — Trusted Personal AI Operating System

**Objectives:** Deliver a stable, supportable personal platform.

**Major features:** Installer/updater; chat, search, dashboard, memory approval, plugins/MCP, bounded agents, automation; backup/restore; observability; migration compatibility.

**Dependencies:** All v0.x gates; external security assessment; documentation and support runbooks.

**Risks:** Scope accumulation, upgrade failures, nontechnical operational burden.

**Effort:** 12–18 stabilization weeks.

**Acceptance criteria:** 90-day dogfood period; zero unresolved critical vulnerabilities; tested upgrade/rollback across two prior versions; recovery time objective under one hour; core workflows meet published SLOs.

## v1.1 — Desktop Productization

**Objectives:** Make installation and daily operation approachable.

**Features:** Desktop shell, system tray, notifications, guided setup, diagnostics, background-service control.

**Dependencies:** v1.0 stable API and updater.

**Risks:** OS-specific packaging and security.

**Effort:** 8–12 weeks.

**Acceptance:** Signed installers; clean install/uninstall; no orphaned secrets or services; diagnostics export redacts private content.

## v1.2 — Mobile Companion

**Objectives:** Capture, approve, and resume from mobile without duplicating the system.

**Features:** Secure pairing; inbox capture; dashboard; approval queue; notifications; offline draft queue.

**Dependencies:** Identity, remote access gateway, sync protocol.

**Risks:** Lost-device exposure, notification leakage, conflict handling.

**Effort:** 12–18 weeks.

**Acceptance:** Device revocation; encrypted transport/storage; offline actions reconcile without duplication; no direct vault exposure to the public internet.

## v1.3 — Voice and Ambient Input

**Objectives:** Add hands-free access to proven workflows.

**Features:** Push-to-talk, transcription, TTS, confirmation prompts, speaker/privacy controls.

**Dependencies:** v1.1 desktop, stable permissions.

**Risks:** Accidental activation, sensitive audio, ambiguous confirmation.

**Effort:** 8–12 weeks.

**Acceptance:** Consequential actions require explicit non-ambiguous confirmation; recordings follow retention policy; voice never bypasses authorization.

## v1.5 — Team Workspaces

**Objectives:** Support small teams with explicit shared ownership.

**Features:** Workspace membership; roles; shared dashboards; review queues; audit exports; conflict-safe collaborative knowledge.

**Dependencies:** New identity/tenant architecture; enterprise threat model.

**Risks:** Personal/team data leakage, permission inheritance, ownership disputes.

**Effort:** 20–30 weeks.

**Acceptance:** Tenant isolation tests; role revocation within defined SLO; complete subject-access and audit export; clear personal/shared boundary.

## v2.0 — Governed Platform

**Objectives:** Become a platform for third-party agents, plugins, and organizational deployments.

**Features:** Stable public SDK/API; plugin marketplace governance; federated identity; policy administration; remote execution pools; multi-region metadata plane; enterprise compliance controls.

**Dependencies:** v1.5; platform governance; compatibility program; security certification.

**Risks:** Ecosystem abuse, backwards-compatibility burden, regulatory exposure, platform complexity.

**Effort:** 40–60 weeks across a multidisciplinary team.

**Acceptance:** Versioned public contracts; independent plugin certification; tenant isolation and policy conformance audits; published deprecation policy; million-note and thousand-plugin scale tests; disaster recovery exercise passes.

## Release governance

No release advances because a feature list is complete. It advances when its acceptance evidence, migration path, rollback plan, security review, documentation, and operational ownership are complete.

## Revision history

| Version | Date | Change |
|---|---|---|
| 0.3.0 | 2026-07-27 | Reconciled v0.3 Query Engine, v0.3.1 Trust Contracts, v0.4 Project Resume, and v0.5 conversation sequence |
| 0.2.0 | 2026-07-27 | Initial product release sequence through v2.0 |
