# ADR-0002: Markdown Is Canonical Storage

| Field | Value |
|---|---|
| Status | Proposed |
| Version | 0.1.0 |
| Owner | Jason |
| Date | 2026-07-27 |
| Related | [Vault Schema](../VAULT_SCHEMA.md), [Knowledge Standard](../KNOWLEDGE_STANDARD.md) |

## Context

The durable knowledge format must be portable, readable, versionable, supported by Obsidian, and independent of Jarvis or a specific database.

## Decision

UTF-8 Markdown files with YAML frontmatter and wikilinks are canonical for durable vault knowledge. Machine-readable indexes and embeddings are derived and rebuildable.

## Alternatives

### Relational database

Excellent for operational state but less convenient for direct human authoring and portability.

### Graph database

Powerful for traversal but introduces operational complexity and an additional authoritative representation.

### Proprietary document format

Rejected because it increases lock-in and reduces interoperability.

## Consequences

### Positive

- Human-readable and application-independent.
- Works naturally with Obsidian and versioning tools.
- Easy to back up, inspect, and migrate.

### Negative

- Schema enforcement is external.
- Cross-file transactions require special handling.
- Large-scale queries require derived indexes.
- Wikilink resolution has edge cases.

## Revision history

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-07-27 | Initial proposal |
