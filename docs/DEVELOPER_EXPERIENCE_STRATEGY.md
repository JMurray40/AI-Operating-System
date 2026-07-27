# Developer Experience Strategy

| Field | Value |
|---|---|
| Purpose | Define the ideal human-and-AI engineering workflow through v2.0 |
| Status | Draft |
| Version | 1.0.0 |
| Owner | Engineering |
| Revised | 2026-07-27 |
| Related | [Development Guide](DEVELOPMENT_GUIDE.md), [Contributing](../CONTRIBUTING.md), [Architecture Review](reviews/ENTERPRISE_ARCHITECTURE_REVIEW.md) |

## Experience goals

A contributor should clone, understand, validate, test, and make a small safe change within 30 minutes. Architecture rules should be executable where possible. AI contributors follow the same branch, test, review, provenance, and approval requirements as humans.

## Repository organization

Near-term monorepo:

```text
src/jarvis_core/          Domain and application contracts
apps/                     Future desktop/web/mobile clients
packages/                 Public SDKs and schema packages
plugins/                  First-party reference plugins
schemas/                  Versioned public data contracts
tests/                    Unit, contract, integration, security, performance
docs/product/             Strategy and release roadmap
docs/prd/                 Capability requirements
docs/agents/              Agent manifests/specifications
docs/sdk/                 Extension contracts
docs/reviews/             Architecture and security audits
docs/software/            Current implementation documentation
```

Keep one repository until independent release cadence, access control, or build cost justifies a split. Avoid microrepositories per agent/plugin.

## Branch strategy

Use trunk-based development:

- protected `main`, always releasable;
- short-lived `feat/`, `fix/`, `docs/`, `chore/`, `security/` branches;
- draft PR early; squash merge by default;
- release tags from `main`;
- no long-lived `develop` branch;
- emergency fix branch from affected tag, then merge forward.

Large architectural work uses feature flags and contract-first slices, not months-long branches.

## Issue and PR readiness

An implementation issue must state problem, user outcome, non-goals, acceptance criteria, security/privacy impact, dependencies, relevant PRD/ADR, test/evaluation plan, migration, and rollback.

A PR must be reviewable:

- one coherent outcome;
- linked issue/decision;
- changed contracts and compatibility called out;
- tests and docs updated;
- generated/AI-assisted content disclosed;
- no unrelated formatting churn;
- evidence pasted or attached, not merely “tests pass.”

## Testing strategy

| Layer | Purpose |
|---|---|
| Unit | Pure parser, model, policy, ranking, and transformation behavior |
| Contract | Provider, repository, plugin, MCP, schema, and tool adapters |
| Integration | Real component boundaries using disposable stores/fixtures |
| End-to-end | User workflows with mock external effects |
| Golden/snapshot | Deterministic context, search, audit, and rendering contracts |
| Property/fuzz | YAML/Markdown/path/schema/IPC robustness |
| Security | Permissions, injection, isolation, secrets, cross-workspace |
| Performance | Corpus indexing/search/context and concurrency budgets |
| Migration | Upgrade, rollback, and old-schema compatibility |
| Evaluation | Retrieval relevance and agent outcome rubrics |

Tests involving personal vault content are prohibited in CI. Use synthetic, licensed, or explicitly sanitized fixtures.

## AI-assisted development

AI must read repository instructions, relevant PRD/ADR, and current code before changes. It proposes a plan for multi-file work, stays within task scope, does not invent passing test results, and produces a session summary. Human review is mandatory for merge, dependencies, permissions, security controls, schemas, migrations, and releases.

Prompt/version changes to agents are code: review, test on fixed evaluations, and record behavioral deltas.

## Documentation strategy

- Product strategy explains why/outcomes.
- PRDs define user-visible requirements.
- Architecture defines boundaries and qualities.
- ADRs record one accepted decision and alternatives.
- Software docs describe current implementation truth.
- Runbooks describe operations and recovery.
- Schemas define machine contracts.

Every document has status, version, owner, revision date, related documents, and history. CI validates relative links, Mermaid syntax where possible, duplicate headings, metadata, and stale generated indexes. Avoid repeating canonical requirements; link instead.

## Release strategy

Before 1.0 use semantic pre-releases with explicit schema compatibility. Every release includes:

- changelog and release notes;
- package/artifact hashes, SBOM, provenance, and signatures;
- schema/database migration and rollback;
- compatibility matrix;
- security review and known limitations;
- installation/upgrade validation;
- backup/restore instructions where state is affected.

Use canary/dogfood rings before broad update. Never auto-update across a permission expansion without review.

## CI/CD improvements

Immediate:

- test on supported Python versions and Windows/Linux/macOS;
- lint, type check, unit/integration tests, coverage trend;
- docs/link/schema validation;
- dependency, license, secret, and code scanning;
- immutable action references and least-privilege tokens.

Before v0.7:

- plugin/MCP contract conformance;
- adversarial injection corpus;
- package SBOM/provenance/signing;
- performance regression budgets;
- compatibility fixtures and migration tests.

Before v1.0:

- signed installers;
- staged update/rollback testing;
- reproducible or independently verifiable builds;
- disaster recovery and security release workflow.

## Coding standards

- Typed public interfaces; explicit errors; immutable domain values where practical.
- Pure domain logic separated from I/O and frameworks.
- No ambient filesystem/network/secrets.
- Structured logs with correlation and redaction.
- Time, randomness, and external services injected for tests.
- Backward-compatible schema evolution or explicit migration.
- Dependency additions require rationale, maintenance/security assessment, and removal plan.

## Contribution and governance

- CODEOWNERS for security, schemas, SDK, and release workflows.
- Two reviewers for security/permission/cryptography/release changes when team size permits.
- ADR approval required for new canonical store, public protocol, trust boundary, major dependency, or irreversible migration.
- Good-first issues are bounded and fixture-driven.
- Publish a support/deprecation policy before external plugin developers depend on contracts.

## Local developer workflow

1. Create an isolated environment.
2. Install locked development dependencies.
3. Run one `check` command that formats/checks/lints/types/tests/docs.
4. Run targeted tests while iterating.
5. Run security/performance suites when affected.
6. Update documentation and changelog.
7. Open draft PR with evidence and risk.

The repository should provide task-runner commands so contributors do not memorize tool-specific invocations.

## Developer success metrics

- Time to first passing change.
- CI median and p95 duration/flakiness.
- Review cycle time and escaped defect rate.
- Breaking contract changes per release.
- Documentation freshness and broken links.
- Security findings age.
- Plugin conformance pass rate.
- Reproducible bug rate from diagnostics.

## Revision history

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-07-27 | Initial decade-scale developer experience design |
