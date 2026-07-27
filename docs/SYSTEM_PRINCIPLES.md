# System Principles

| Field | Value |
|---|---|
| Purpose | Define the enduring philosophy used to evaluate architecture, product, and workflow decisions |
| Status | Active |
| Version | 1.0.0 |
| Owner | Jason |
| Revised | 2026-07-27 |
| Related | [Product Vision](PRODUCT_VISION.md), [System Architecture](SYSTEM_ARCHITECTURE.md), [Architecture Decision Records](adr/) |

## Role of this document

These principles are the governance foundation for the AI Operating System. They are broader than individual Architecture Decision Records:

- A **principle** states an enduring value or decision criterion.
- An **ADR** records one consequential architectural decision made in a particular context.
- A **standard** translates principles and decisions into repeatable implementation rules.

Future proposals should identify which principles they support, where they create tension, and why any tradeoff is justified.

## Principle 1 — Human-owned knowledge is authoritative

Durable personal and project knowledge belongs to Jason, not to an AI provider, application, or opaque database.

The system may derive indexes, summaries, embeddings, and operational state, but those derived systems must not become the only place where important knowledge exists.

**Decision test:** Can Jason still access and understand the essential knowledge if Jarvis or an AI provider is unavailable?

## Principle 2 — Markdown is the canonical knowledge format

Durable knowledge should use portable, human-readable Markdown with structured metadata where appropriate.

Indexes and databases may improve performance, but they must be rebuildable from authoritative sources.

**Decision test:** Does the proposal preserve direct human readability and long-term portability?

## Principle 3 — AI proposes; humans approve

AI may classify, analyze, draft, compare, and recommend. Humans approve consequential, structural, sensitive, or destructive changes.

Approval must be informed: the user should understand the exact target, action, expected result, and recovery path.

**Decision test:** Does the user retain meaningful control over actions that could change knowledge, systems, costs, privacy, or other people?

## Principle 4 — Prefer references over duplication

Knowledge should describe and connect external assets without creating unnecessary editable copies.

GitHub remains authoritative for software. File and cloud systems remain authoritative for their assets. Calendars remain authoritative for events. The vault records meaning, context, relationships, and stable pointers.

**Decision test:** Does this create a second master copy that can drift?

## Principle 5 — Local-first whenever practical

Core knowledge and essential workflows should function locally when practical. Cloud services may add value, but they should be selected deliberately and should not create avoidable dependence.

Local-first does not mean local-only. It means the system retains useful capability, ownership, and recovery when external services are unavailable.

**Decision test:** What remains usable during an outage, provider change, or connectivity failure?

## Principle 6 — Every meaningful session should improve the system

AI and work sessions should leave behind durable value: a summary, decision, resolved problem, verified resource, clarified next action, or useful relationship.

Raw transcripts are evidence, not the default knowledge artifact.

**Decision test:** What useful, reusable outcome remains after the session ends?

## Principle 7 — Every active project has a dashboard

The Project Dashboard is the primary entry point for human and AI work. It assembles the project's purpose, current state, Resume section, priorities, decisions, sessions, resources, and relationships.

Folders, tags, backlinks, graphs, and search support navigation but do not replace the dashboard.

**Decision test:** Can a user resume this project accurately from one canonical page?

## Principle 8 — Every note has a clear primary purpose

A note may participate in many relationships, but it should have one understandable reason to exist.

Clear purpose improves classification, retrieval, metadata quality, maintenance, and AI context selection.

**Decision test:** Can the note's purpose be explained in one sentence?

## Principle 9 — Knowledge must outlive individual AI models

Claude, ChatGPT, Gemini, Ollama, and future models are interchangeable reasoning engines. Provider-specific memory must not become the long-term system of record.

Prompts and adapters may vary by provider; durable knowledge and decisions remain provider-independent.

**Decision test:** What would be lost if this model or provider were replaced tomorrow?

## Principle 10 — Components must be replaceable

The system should be separable into knowledge, orchestration, search, operational storage, provider adapters, tools, and interfaces.

Components communicate through explicit contracts so one may evolve without forcing a redesign of the whole system.

**Decision test:** Can this component be replaced without migrating unrelated responsibilities?

## Principle 11 — Inventory before modification

Before significant migration, restructuring, or metadata transformation, establish a read-only baseline of the current state.

The baseline should make scope, impact, validation, and rollback measurable.

**Decision test:** Do we know exactly what exists, what will change, and how to prove recovery?

## Principle 12 — Safety and provenance are product features

Permissions, approvals, attribution, source tracking, backups, and recovery are part of the system's value—not implementation details added later.

**Decision test:** Can a user understand why information or an action exists, where it came from, and how to reverse it?

## Applying the principles

Every material proposal should answer:

1. Which principles does it support?
2. Which principles are in tension?
3. What authority remains with the human?
4. What becomes authoritative, and where?
5. What is derived and rebuildable?
6. What is the failure and rollback behavior?
7. What evidence will demonstrate success?

If a proposal conflicts with a principle, it requires explicit rationale and, when architectural, an ADR.

## Relationship to current ADRs

| Principle | Supporting decision |
|---|---|
| Human-owned knowledge is authoritative | [ADR-0001](adr/ADR-0001-The-Brain-Is-The-Durable-Knowledge-Layer.md) |
| Markdown is canonical | [ADR-0002](adr/ADR-0002-Markdown-Is-The-Canonical-Storage.md) |
| External engineering assets retain authority | [ADR-0003](adr/ADR-0003-GitHub-Is-The-Source-Of-Truth-For-Code.md) |
| Project dashboards are primary navigation | [ADR-0004](adr/ADR-0004-Project-Dashboards-Are-The-Primary-Navigation-Layer.md) |
| Inventory before modification | [ADR-0005](adr/ADR-0005-Inventory-Before-Modification.md) |

## Revision history

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-07-27 | Initial system-governance principles |
