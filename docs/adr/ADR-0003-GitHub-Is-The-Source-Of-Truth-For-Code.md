# ADR-0003: GitHub Is the Source of Truth for Software

| Field | Value |
|---|---|
| Status | Proposed |
| Version | 0.1.0 |
| Owner | Jason |
| Date | 2026-07-27 |
| Related | [Repository README](../../README.md), [Development Guide](../DEVELOPMENT_GUIDE.md) |

## Context

The vault must describe software projects without becoming a second editable copy of source code, repository documentation, issues, or releases.

## Decision

Git repositories hosted on GitHub are authoritative for source code and repository-scoped engineering artifacts. The vault stores project context, durable knowledge, decisions, session summaries, and pointers to GitHub objects.

## Alternatives

### Store code and repository documents in Obsidian

Rejected because it creates duplicate editable copies and weakens standard engineering workflows.

### Local repositories without a remote

Permitted for experiments but unsuitable as the long-term authority because collaboration, recovery, and automation are weaker.

### Store all project knowledge only in GitHub

Rejected because cross-project personal knowledge and AI session context need a human-owned knowledge layer.

## Consequences

### Positive

- Standard branches, reviews, issues, CI, and releases.
- Clear source-of-truth boundary.
- Vault remains focused on knowledge rather than code replication.

### Negative

- Project context must maintain durable links to repository objects.
- Offline availability depends on local clones.
- Private repository access and credentials require secure configuration.

## Revision history

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-07-27 | Initial proposal |
