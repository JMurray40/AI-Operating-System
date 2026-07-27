# Contributing

| Field | Value |
|---|---|
| Purpose | Define the contribution and review workflow |
| Status | Active |
| Version | 0.1.0 |
| Owner | Jason |
| Revised | 2026-07-27 |
| Related | [Development Guide](docs/DEVELOPMENT_GUIDE.md), [AI Behavior Standard](docs/AI_BEHAVIOR_STANDARD.md) |

## Principles

- Keep every change scoped to one clear outcome.
- Treat documentation and Architecture Decision Records as product artifacts.
- Never commit secrets, private vault content, credentials, or personal data.
- Prefer portable interfaces and reversible changes.
- Preserve the distinction between knowledge, engineering artifacts, operational data, and indexes.

## Workflow

1. Start from an issue or a documented milestone outcome.
2. Create a focused branch named `feature/...`, `fix/...`, `docs/...`, or `chore/...`.
3. Review relevant specifications and ADRs.
4. Make the smallest coherent change.
5. Update related documentation and the changelog when behavior or architecture changes.
6. Run available validation.
7. Open a pull request using the repository template.
8. Obtain human approval for architecture, security, schema, migration, or external-write changes.

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
| 0.1.0 | 2026-07-27 | Initial contribution policy |
