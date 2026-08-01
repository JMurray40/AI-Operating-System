# Roadmap

| Field | Value |
|---|---|
| Purpose | Sequence delivery into independently valuable milestones |
| Status | Draft |
| Version | 0.3.0 |
| Owner | Jason |
| Revised | 2026-08-01 |
| Related | [Product Vision](PRODUCT_VISION.md), [Version Roadmap v0.2–v2.0](product/VERSION_ROADMAP.md), [Implementation Plan](IMPLEMENTATION_PLAN.md) |

## Milestone-to-release crosswalk

This roadmap describes durable capability milestones. The
[Version Roadmap](product/VERSION_ROADMAP.md) controls current release numbering.

| Release | Capability milestone | Current state |
|---|---|---|
| v0.3 | Milestone 3 — read-only query foundation | Merged |
| v0.3.1 | Milestone 3 hardening — Query Trust Contracts | Released |
| v0.4 | Milestone 4 — Project Resume | Released as `v0.4.0`; A11 eight-week outcome pending |
| v0.5 | Conversation slice formerly included in Milestone 3 | Planning may begin after v0.4 closeout validation; implementation requires fresh authorization |

The crosswalk does not declare the broader milestone complete merely because one release
within it has merged.

## Milestone 0 — Foundation

**Goal:** Establish professional governance and a stable technical direction.

**Deliverables:** Core specifications, ADRs, templates, schema, contribution workflow, documentation validation, and initial repository.

**Dependencies:** The BRAIN v2 source specification.

**Completion criteria:** Documents cross-link correctly; GitHub repository is initialized; validation passes; no application code exists.

## Milestone 1 — Knowledge System

**Goal:** Make the vault useful and consistent in daily work.

**Deliverables:** Backup, inventory baseline, `VAULT-INDEX.md`, controlled vocabulary, two pilot project dashboards, Daily Notes, resource links, and migration log.

**Dependencies:** Milestone 0 and approved vault access.

**Completion criteria:** Two projects can be resumed from their dashboards for two weeks; no unapproved structural migration occurs.

## Milestone 2 — Cross-AI Memory

**Goal:** Produce consistent durable outcomes from multiple AI providers.

**Deliverables:** Provider-independent session workflow, pointer-only memory files, repository closeout instructions, decision extraction, and project updates.

**Dependencies:** Stable templates and pilot projects.

**Completion criteria:** Meaningful sessions from at least two AI providers produce valid, linked summaries without duplicate memory stores.

## Milestone 3 — Read-only Jarvis

**Goal:** Deliver a useful Daily Brain without write risk.

**Deliverables:** Local UI, API, vault parser, full-text search, project list, recent sessions, decisions, resource links, conversation history, and health checks.

**Dependencies:** Validated knowledge system and technical stack ADRs.

**Completion criteria:** Jarvis answers approved benchmark questions accurately and never modifies the vault.

## Milestone 4 — Project Resume

**Goal:** Eliminate project reorientation time.

**Deliverables:** Context builder, repository status adapter, “Resume Project” briefing, provenance display, and safe launch context for coding sessions.

**Dependencies:** Read-only Jarvis and approved GitHub/local-folder access.

**Completion criteria:** Each pilot project produces a useful briefing in under one minute with traceable sources.

## Milestone 5 — Relationship Engine

**Goal:** Surface useful overlap, duplicates, and contradictions.

**Deliverables:** Link graph, entity extraction, semantic index, similarity candidates, contradiction candidates, and review interface.

**Dependencies:** Sufficient real notes, benchmark set, and privacy policy.

**Completion criteria:** Findings meet an agreed precision threshold and remain advisory.

## Milestone 6 — Automation

**Goal:** Add controlled capture and repeatable workflows.

**Deliverables:** Tool registry, permissions, approval UI, atomic writes, audit log, session-save workflow, scheduled briefings, and connector framework.

**Dependencies:** Read-only reliability, backup/recovery, and security review.

**Completion criteria:** Approved workflows are idempotent, recoverable, and fully audited.

## Milestone 7 — Voice and additional interfaces

**Goal:** Provide natural access to capabilities already proven useful.

**Deliverables:** Desktop packaging, push-to-talk, speech-to-text, text-to-speech, notifications, mobile interface, and optional Home Assistant bridge.

**Dependencies:** Mature permissions and reliable core workflows.

**Completion criteria:** Voice and new interfaces invoke the same permissioned APIs without bypassing controls.

## Milestone governance

A milestone begins only when its dependencies are met. Completion requires evidence, not a percentage estimate. New ideas enter the backlog unless they are necessary to meet current completion criteria.

## Revision history

| Version | Date | Change |
|---|---|---|
| 0.3.0 | 2026-08-01 | Recorded the v0.4.0 release and the bounded v0.5 planning gate |
| 0.2.0 | 2026-07-27 | Added milestone-to-release crosswalk through v0.5 |
| 0.1.0 | 2026-07-27 | Initial milestone roadmap |
