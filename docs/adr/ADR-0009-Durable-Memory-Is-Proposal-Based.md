# ADR-0009: Durable Memory Is Proposal-Based

| Field | Value |
|---|---|
| Status | Proposed |
| Date | 2026-07-27 |
| Deciders | Pending product, knowledge, and security review |
| Related | [Memory PRD](../prd/MEMORY_SYSTEM.md), [The BRAIN v2](../THE_BRAIN_V2_SPEC.md), [ADR-0001](ADR-0001-The-Brain-Is-The-Durable-Knowledge-Layer.md) |

## Context

AI sessions frequently produce decisions, summaries, preferences, and relationships worth preserving. Saving entire transcripts creates noise and privacy risk; allowing a model to edit the vault silently can create false facts, duplicates, contradictions, and irreversible structural drift.

Conversation history, task working state, durable knowledge, preferences, and search projections have different owners and lifecycles.

## Decision

AI-generated durable memory begins as a typed `MemoryCandidate`, not a committed fact or direct vault edit.

Candidates:

- identify create, update, link, supersede, or skip intent;
- include source evidence, provenance, confidence, and sensitivity;
- validate against schemas and controlled vocabulary;
- check identity, duplicates, and conflicts;
- present an exact before/after diff and target revision;
- require the applicable human approval;
- commit atomically with audit, validation, and rollback.

Conversation and provider-native memories never become durable knowledge merely because they exist.

## Alternatives considered

### Save every transcript

Rejected as the primary memory because it is verbose, difficult to retrieve, privacy-heavy, and preserves discussion rather than accepted knowledge.

### Let the model update notes automatically

Rejected because model confidence is not authority and later corrections are costly.

### Never allow AI-generated memory

Rejected because structured session outcomes are a primary source of long-term value.

### Store durable memory only in a database

Rejected because it would compete with the human-owned portable vault.

## Tradeoffs

- Review introduces friction and possible approval fatigue.
- Candidate extraction and conflict detection add complexity.
- Some useful knowledge may remain unaccepted.

## Consequences

- The first vault-write feature is a proposal/approval workflow, not general file mutation.
- Candidate quality and later correction rates become product metrics.
- Approved memories retain provenance and supersession history.
- Operational transcript retention can be shortened independently.
- Agents and automations cannot bypass memory approval through a different write path.

## Approval conditions

Accept after identity, sensitivity, candidate schema, atomic write transaction, backup/rollback, and approval-token designs are approved.
