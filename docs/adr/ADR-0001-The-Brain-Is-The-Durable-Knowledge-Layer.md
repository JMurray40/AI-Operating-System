# ADR-0001: The BRAIN Is the Durable Knowledge Layer

| Field | Value |
|---|---|
| Status | Proposed |
| Version | 0.1.0 |
| Owner | Jason |
| Date | 2026-07-27 |
| Related | [The BRAIN v2](../THE_BRAIN_V2_SPEC.md), [Architecture](../SYSTEM_ARCHITECTURE.md) |

## Context

Useful knowledge currently spans AI conversations, project files, repositories, and applications. Provider-specific memory is inaccessible to other tools and creates lock-in. Jarvis also needs an authoritative, human-editable source from which indexes and context can be rebuilt.

## Decision

The Obsidian vault known as The BRAIN is the durable knowledge layer for personal and project knowledge. Jarvis, AI providers, and search services consume or propose changes to it through permissioned interfaces. Operational state and external assets remain in their appropriate systems.

## Alternatives

### Provider memory

Rejected because it fragments knowledge by vendor and is not a stable human-owned store.

### Jarvis relational database

Rejected as the sole knowledge source because it reduces direct human editability and couples knowledge to the application.

### Dedicated graph database

Deferred. It may become a derived index but not the only durable store.

## Consequences

### Positive

- Human ownership and portability.
- Direct use when Jarvis is unavailable.
- Shared memory across AI providers.
- Rebuildable search and relationship indexes.

### Negative

- File concurrency and safe writes require care.
- Markdown relationships need conventions and validation.
- Some operational queries belong in a separate database.

## Revision history

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-07-27 | Initial proposal |
