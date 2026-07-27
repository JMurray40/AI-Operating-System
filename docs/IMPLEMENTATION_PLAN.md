# Implementation Plan

| Field | Value |
|---|---|
| Purpose | Translate the roadmap into the first executable work packages |
| Status | Draft |
| Version | 0.1.0 |
| Owner | Jason |
| Revised | 2026-07-27 |
| Related | [Roadmap](ROADMAP.md), [Architecture](SYSTEM_ARCHITECTURE.md), [Development Guide](DEVELOPMENT_GUIDE.md) |

## Phase 0: Repository foundation

1. Publish this repository privately.
2. Configure branch protection, labels, milestones, and a GitHub Project.
3. Enable the documentation validation workflow.
4. Review open questions in The BRAIN v2.
5. Accept or revise the initial ADRs.

## Phase 1: Knowledge pilot

1. Verify the vault backup.
2. Run a read-only inventory.
3. Install approved templates and `VAULT-INDEX.md`.
4. Select Jarvis and one active existing project.
5. Create dashboards and verified resource notes.
6. Use Daily Notes and session closeout for two weeks.
7. Record friction and revise the standard through reviewed changes.

## Phase 2: Read-only engineering discovery

Before application code, create focused research records for:

- Python/FastAPI and React/TypeScript baseline;
- local secrets and credential storage;
- Markdown/YAML parsing and safe path handling;
- full-text search options;
- model gateway options;
- GitHub and local-folder adapter boundaries; and
- desktop packaging assumptions.

Each material selection requires an ADR.

## Phase 3: Read-only Jarvis foundation

The first implementation issue should scaffold only:

- web interface;
- local API;
- health endpoint;
- SQLite conversation persistence;
- mock model provider;
- read-only sample-vault parser; and
- automated tests.

Do not add real providers, agents, MCP, voice, computer control, vault writes, or production connectors.

## Backlog entry criteria

An item enters an active milestone only when it has:

- clear user value;
- scope and non-goals;
- dependencies;
- acceptance criteria;
- risk and permission notes; and
- an identified validation approach.

## Initial risks

| Risk | Mitigation |
|---|---|
| Premature platform breadth | Enforce milestone non-goals |
| Vault damage | Read-only first, backups, approved roots |
| Knowledge duplication | Authority rules and resource pointers |
| Provider lock-in | Role aliases and adapters |
| Privacy leakage | Sensitivity labels and trust-boundary filtering |
| Low-quality similarity | Advisory findings and benchmark evaluation |

## Revision history

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-07-27 | Initial execution plan |
