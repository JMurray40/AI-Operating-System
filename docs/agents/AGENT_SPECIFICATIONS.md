# Reference Agent Specifications

| Field | Value |
|---|---|
| Purpose | Define bounded specialist agent profiles without creating separate runtimes |
| Status | Draft |
| Version | 0.1.0 |
| Owner | Product/AI Platform |
| Revised | 2026-07-27 |
| Related | [Agent Framework PRD](../prd/AGENT_FRAMEWORK.md), [AI Behavior Standard](../AI_BEHAVIOR_STANDARD.md) |

## Shared contract

An agent is a versioned manifest plus instructions, task/input schema, output schema, context policy, capabilities, budgets, and evaluation suite. It is not a persistent persona, source of truth, or unrestricted process.

Every run receives:

- immutable task ID and user objective;
- workspace/project scope and sensitivity ceiling;
- context snapshot with provenance;
- least-privilege capability grant;
- time, cost, token, tool, and delegation budgets;
- explicit output contract and human checkpoints.

Every run returns typed artifacts, sources, unresolved questions, actions proposed/taken, costs, and terminal status. Agents exchange artifacts through the runtime; they do not share mutable hidden memory.

## Permission classes

| Class | Meaning |
|---|---|
| R0 | Read task-supplied content only |
| R1 | Read approved workspace sources |
| R2 | Query approved external systems |
| W1 | Draft/propose a canonical or external change |
| W2 | Execute a reversible approved change |
| X | High-risk action requiring explicit per-action approval |

No reference agent receives unrestricted shell, filesystem, secrets, financial transfer, message-send, or device-control capability.

## Research Agent

**Responsibilities:** Frame questions, plan searches, collect primary evidence, compare claims, assess source quality, synthesize findings, and identify uncertainty.

**Inputs:** Research question, scope, deadline, source constraints, project context, citation style.

**Outputs:** Research brief, evidence table, citations, conflicting findings, confidence, open questions, recommended follow-up.

**Permissions:** R0–R2; W1 for research-note proposal. Network/domain access is explicit. No publishing or contacting people.

**Memory requirements:** Project decisions, prior research, controlled concepts, source history. Temporary browsing state expires; accepted brief enters vault only after review.

**Failure modes:** Citation fabrication, secondary-source echo, stale evidence, confirmation bias, paywall omission, prompt injection in sources. Mitigate with URL/source capture, claim-evidence checks, source diversity, and explicit “not found.”

**Interactions:** Supplies evidence to Planning, Writing, Coding, Finance, and Bookkeeping. Requests domain review for regulated conclusions.

## Coding Agent

**Responsibilities:** Analyze repositories, propose designs, implement scoped code, test, document, and prepare reviewable changes.

**Inputs:** Issue/task, repository/branch, acceptance criteria, architecture/ADRs, test commands, file and tool scope.

**Outputs:** Plan, patch/commit proposal, tests and results, changed-file summary, risks, migration/rollback notes, session summary.

**Permissions:** R1 repository; W1 patch; W2 branch writes only when approved; X for dependency installation, secrets, deployment, destructive Git, or production changes.

**Memory requirements:** Repository instructions, current architecture, relevant ADRs, open issue, recent project sessions. Never uses model memory as authoritative code context.

**Failure modes:** Scope creep, destructive Git, insecure code, tests that do not exercise behavior, architecture drift, secret exposure. Enforce branch isolation, diff limits, CI, dependency review, and mandatory human merge.

**Interactions:** Research for technical evidence, Planning for work breakdown, Writing for user documentation. Cannot delegate approval.

## Finance Agent

**Responsibilities:** Analyze personal/business financial data, model scenarios, reconcile assumptions, explain trends, and draft forecasts.

**Inputs:** Approved financial statements/data, period, currency, scenario assumptions, accounting basis, risk tolerance.

**Outputs:** Analysis workbook/report, formulas/assumptions, variance explanation, scenarios, data-quality exceptions, non-advisory disclaimer where applicable.

**Permissions:** R0–R2 to scoped financial sources; W1 drafts. No transfers, trades, filings, account changes, or external communication.

**Memory requirements:** Approved financial preferences, entity/currency/fiscal-period definitions, prior accepted models. Highly restricted; exclude from general context.

**Failure modes:** Wrong period/entity, unit errors, hallucinated figures, stale market/tax data, treating estimates as facts. Require source-to-cell lineage, arithmetic checks, freshness, and human professional review.

**Interactions:** Bookkeeping provides reconciled data; Research verifies current authoritative rules; Planning turns accepted analysis into tasks.

## Bookkeeping Agent

**Responsibilities:** Classify transactions, identify reconciliation exceptions, assemble month-end checklists, draft journal-entry suggestions, and organize supporting evidence.

**Inputs:** Scoped ledger export, chart of accounts, bank/processor records, receipts, period, entity policy.

**Outputs:** Proposed classifications, reconciliation report, exception queue, missing-document list, draft entries with explanation, close checklist.

**Permissions:** Read-only accounting integration by default; W1 drafts. Posting, deleting, closing periods, filing, paying, or contacting clients is X and outside initial release.

**Memory requirements:** Entity-specific chart, vendor mappings, prior approved treatments, close procedures, retention policy. Strict tenant/client separation.

**Failure modes:** Cross-client leakage, duplicate transactions, incorrect tax treatment, unbalanced entries, unsupported assumptions. Enforce entity boundary, control totals, confidence thresholds, and accountant approval.

**Interactions:** Finance consumes reconciled outputs; Personal Assistant may schedule missing-item follow-ups but cannot send without approval.

## Writing Agent

**Responsibilities:** Draft, revise, adapt tone, structure long-form content, preserve claims/citations, and produce publication-ready proposals.

**Inputs:** Brief, audience, purpose, voice guide, source pack, channel constraints, approval status.

**Outputs:** Draft, alternatives where useful, claim/source map, editorial notes, unresolved facts, publication checklist.

**Permissions:** R0–R2 approved sources; W1 drafts. Publishing, emailing, posting, or replacing canonical content requires separate approval.

**Memory requirements:** Approved style guide, organization profile, audience, prior accepted terminology. Raw private conversations excluded unless supplied.

**Failure modes:** Invented claims, plagiarism, voice drift, accidental private detail, SEO degrading quality. Use claim verification, provenance, similarity checks, and redaction review.

**Interactions:** Research supplies evidence; Planning supplies brief/timeline; Personal Assistant may coordinate review.

## Planning Agent

**Responsibilities:** Convert objectives into milestones, dependencies, decisions, risks, estimates, and next actions; maintain alignment with product/architecture.

**Inputs:** Objective, constraints, deadline, resources, current state, roadmap, relevant decisions.

**Outputs:** Plan, critical path, assumptions, decision requests, risk register, acceptance criteria, checkpoints.

**Permissions:** R1–R2 for status; W1 plan/task proposals. Cannot assign external people, change deadlines, or commit budgets without approval.

**Memory requirements:** Project dashboard, accepted roadmap, decisions, outstanding work, capacity assumptions.

**Failure modes:** False precision, hidden assumptions, overplanning, stale status, optimizing local tasks against strategy. Require ranges, evidence, explicit assumptions, and periodic replan triggers.

**Interactions:** Coordinates all specialists but does not override their domain safeguards or the user.

## Home Automation Agent

**Responsibilities:** Monitor approved home systems, explain state, propose routines, diagnose anomalies, and execute narrowly pre-approved reversible controls.

**Inputs:** Device registry, current states, household policy, presence/time context, routine objective.

**Outputs:** Status, proposed control plan, executed action receipts, anomaly alerts, rollback/restore steps.

**Permissions:** R2 device state; W2 only allowlisted low-risk actions; X for locks, alarms, garage, cameras, HVAC extremes, power-critical devices, or occupancy-affecting actions.

**Memory requirements:** Device identities, rooms, safe ranges, household preferences, recent actions. Sensitive occupancy/camera data strictly isolated and short-retained.

**Failure modes:** Wrong device, stale state, unsafe automation, presence inference, network partition, repeated toggling. Require device IDs, state preconditions, rate limits, safe defaults, and physical override.

**Interactions:** Personal Assistant schedules/routs notifications; Planning may design routines. Finance may receive energy summaries, never raw occupancy data.

## Personal Assistant Agent

**Responsibilities:** Produce daily briefs, coordinate calendar/tasks, capture inbox items, prepare communications, and route work to specialists.

**Inputs:** User request, calendar/task/project context, communication draft, preferences, availability.

**Outputs:** Briefing, proposed schedule, task/capture proposals, drafted messages, delegation plan, approval queue.

**Permissions:** R1–R2 scoped personal systems; W1 by default. Sending, booking, cancelling, purchasing, sharing, or changing commitments requires explicit approval.

**Memory requirements:** User preferences, active projects, commitments, people/organization context, communication style. Sensitivity-aware and user-editable.

**Failure modes:** Overstepping authority, leaking private context, double booking, wrong recipient, notification overload, treating suggestion as commitment. Require recipient/target confirmation, calendar conflict checks, and explicit external-effect approval.

**Interactions:** Routes research, writing, planning, finance, bookkeeping, coding, and home tasks; returns consolidated results without expanding their permissions.

## Cross-agent conflict policy

When agents disagree, preserve both recommendations, evidence, assumptions, and confidence. The runtime or Planning Agent may compare them but cannot manufacture consensus. Domain safety policy wins over convenience; the human resolves material ambiguity.

## Evaluation requirements

Each agent ships with:

- happy-path, ambiguity, refusal, prompt-injection, stale-context, and budget tests;
- domain-specific factual and structural rubrics;
- permission-denial and cancellation scenarios;
- at least one adversarial fixture;
- version-to-version regression report.

## Revision history

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-07-27 | Initial eight reference agent specifications |
