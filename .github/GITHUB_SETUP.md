# GitHub Setup

| Field | Value |
|---|---|
| Purpose | Define repository settings not fully represented by tracked files |
| Status | Proposed |
| Version | 0.1.0 |
| Owner | Jason |
| Revised | 2026-07-27 |
| Related | [Roadmap](../docs/ROADMAP.md), [Contributing](../CONTRIBUTING.md) |

## Repository

- Visibility: private initially.
- Default branch: `main`.
- Enable issues, projects, vulnerability alerts, and secret scanning where available.
- Disable wiki until it has a distinct purpose; engineering documentation belongs in the repository.

## Branch protection

For `main`:

- require a pull request after the initial foundation commit;
- require the documentation validation check;
- require conversations to be resolved;
- prevent force pushes and deletion; and
- include administrators once the workflow is proven.

## Milestones

Create GitHub milestones matching [ROADMAP.md](../docs/ROADMAP.md):

1. Milestone 0 — Foundation
2. Milestone 1 — Knowledge System
3. Milestone 2 — Cross-AI Memory
4. Milestone 3 — Read-only Jarvis
5. Milestone 4 — Project Resume
6. Milestone 5 — Relationship Engine
7. Milestone 6 — Automation
8. Milestone 7 — Voice

Do not assign dates until dependencies and capacity are understood.

## Project suggestion

Create a private GitHub Project named **AI Operating System Roadmap** with:

- **Status:** Backlog, Ready, In progress, In review, Blocked, Done.
- **Milestone:** roadmap milestone.
- **Area:** Knowledge, Jarvis, Search, Providers, Integrations, Security, UX, Operations.
- **Risk:** Normal, Migration, Sensitive data, External write, Destructive.
- **Owner:** human accountable for acceptance.

Recommended views:

- Current milestone board.
- Roadmap table grouped by milestone.
- Security and migration risks.
- Architecture decisions.
- Research queue.

## Labels

Apply the label definitions in `labels.yml` after repository creation.

## Revision history

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-07-27 | Initial GitHub configuration proposal |
