# Contributing

| Field | Value |
|---|---|
| Purpose | Define the contribution and review workflow |
| Status | Active |
| Version | 0.3.0 |
| Owner | Jason |
| Revised | 2026-08-01 |
| Related | [System Principles](docs/SYSTEM_PRINCIPLES.md), [Development Guide](docs/DEVELOPMENT_GUIDE.md), [AI Behavior Standard](docs/AI_BEHAVIOR_STANDARD.md) |

## Principles

- Keep every change scoped to one clear outcome.
- Treat documentation and Architecture Decision Records as product artifacts.
- Never commit secrets, private vault content, credentials, or personal data.
- Prefer portable interfaces and reversible changes.
- Preserve the distinction between knowledge, engineering artifacts, operational data, and indexes.

## Workflow

1. Read [Project Control](docs/coordination/README.md) and the active milestone's
   [handoff index](docs/handovers/README.md); do not rely on conversation history.
2. Start from the exact incoming artifact, issue, or documented milestone outcome.
   For released milestones, use the milestone index's latest-effective chain rather than
   the highest filename or an older cumulative disposition.
3. Verify the named branch, base commit, scope, exclusions, and governing decisions.
4. Create a focused branch named `feature/...`, `fix/...`, `docs/...`, or `chore/...`.
5. Review relevant specifications and ADRs.
6. Check the proposal against the System Principles.
7. Make the smallest coherent change.
8. Update related documentation and the changelog when behavior or architecture changes.
9. Run available validation.
10. Open a pull request using the repository template.
11. Obtain human approval for architecture, security, schema, migration, or external-write changes.

## Documentation changes

Every primary document must include purpose, status, version, owner, related documents, revised date, and revision history. Use relative links. Mermaid diagrams should be readable in GitHub and must not be the only description of a system.

## Architecture decisions

Create an ADR when a change:

- establishes or alters a system boundary;
- selects a durable technology or storage model;
- changes security or permission behavior;
- affects data portability or migration; or
- constrains multiple future components.

Accepted ADRs are immutable. Supersede them with a new ADR instead of rewriting history.

## AI-generated contributions

AI-generated work is held to the same standards as human work.

- The AI must identify the context it read.
- Claims must be traceable to project documents or cited sources.
- Generated changes require human review.
- Bulk, destructive, security-sensitive, or external write operations require explicit approval.
- The pull request must disclose material AI assistance.

## Commit guidance

Use imperative, concise commit messages:

```text
docs: establish system architecture
chore: add documentation validation
feat: add read-only vault scanner
```

## Revision history

| Version | Date | Change |
|---|---|---|
| 0.3.0 | 2026-08-01 | Clarified contributor routing through latest-effective milestone state |
| 0.2.0 | 2026-07-27 | Added project-control and handoff startup requirements |
| 0.1.0 | 2026-07-27 | Initial contribution policy |
