# Development Guide

| Field | Value |
|---|---|
| Purpose | Define professional engineering practices for humans and AI |
| Status | Draft |
| Version | 0.1.0 |
| Owner | Jason |
| Revised | 2026-07-27 |
| Related | [Contributing](../CONTRIBUTING.md), [AI Behavior](AI_BEHAVIOR_STANDARD.md), [Architecture](SYSTEM_ARCHITECTURE.md) |

## Working model

Development is specification-first, milestone-scoped, test-driven where behavior warrants it, and human-approved for consequential changes.

## Before implementation

1. Identify the active roadmap milestone.
2. Confirm acceptance criteria and non-goals.
3. Read governing ADRs and specifications.
4. Open an issue for a coherent outcome.
5. Create an ADR if the work introduces a durable architectural choice.
6. Identify security, privacy, migration, and rollback implications.

## Human contributors

- Keep changes focused and reviewable.
- Separate refactoring from new behavior when practical.
- Document public interfaces and operational assumptions.
- Include tests proportional to risk.
- Do not commit local data, secrets, or real vault fixtures.

## Claude Code

Claude Code should read repository instructions, the active milestone, governing ADRs, and relevant documents before planning. It must propose a plan before broad changes, preserve user work, run validation, and produce a session closeout. It may not access or modify the live vault unless explicitly authorized for that task.

## ChatGPT and other conversational AI

Conversational models should produce specifications, reviews, research, or bounded artifacts. Their output enters the repository only after validation and human review. They must not be treated as an implicit source of truth.

## Coding standards

Technology-specific rules will be added when the implementation stack is approved. Until then:

- favor explicit interfaces and typed data contracts;
- isolate provider and connector behavior behind adapters;
- keep domain logic independent of frameworks;
- validate input at trust boundaries;
- use structured logs without sensitive content;
- make consequential operations idempotent where possible;
- support dry-run behavior for migrations and automation; and
- write tests for routing, permissions, parsing, and persistence.

## Documentation standards

- Markdown is canonical.
- Use relative links.
- Include document metadata and revision history.
- Explain diagrams in prose.
- Keep examples non-sensitive.
- Update documentation in the same change as behavior.
- Record durable choices as ADRs.

## Approval workflow

| Change | Minimum approval |
|---|---|
| Typographical documentation change | Standard review |
| Feature implementation | Owner review |
| Architecture or schema change | Owner approval and ADR |
| Security or permission change | Owner approval and security review |
| Vault migration or destructive action | Explicit per-scope approval and backup |
| External message or system write | Permission defined by tool policy |

## Definition of done

- Acceptance criteria are met.
- Relevant tests and validation pass.
- Security and privacy implications are addressed.
- Documentation and changelog are current.
- Migration and rollback paths exist when applicable.
- No secrets or private fixtures are present.
- Human review is complete.

## Revision history

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-07-27 | Initial development practices |
