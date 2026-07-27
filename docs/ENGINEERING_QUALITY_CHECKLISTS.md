# Engineering Quality Checklists

| Field | Value |
|---|---|
| Purpose | Provide objective, reusable review gates for Jarvis engineering work |
| Status | Active |
| Version | 1.0.0 |
| Owner | Engineering and Architecture Review Board |
| Revised | 2026-07-27 |
| Related | [Jarvis Bible](JARVIS_BIBLE.md), [Development Guide](DEVELOPMENT_GUIDE.md), [Security Threat Model](reviews/SECURITY_THREAT_MODEL.md) |

Use **Yes / No / Not applicable**, attach evidence, and treat any unexplained “No” as blocking. Checklists support judgment; they do not replace it.

## New feature

- [ ] Problem, target user, and measurable outcome are documented.
- [ ] Scope and non-goals are explicit.
- [ ] Acceptance criteria include success, no-result, degraded, and failure paths.
- [ ] Canonical data ownership and migration impact are identified.
- [ ] Permission, privacy, and audit requirements are defined.
- [ ] Interfaces are provider- and UI-neutral where appropriate.
- [ ] Observability and support diagnostics are specified.
- [ ] Automated tests and human evaluation are included.
- [ ] Documentation and changelog impact are addressed.
- [ ] Rollout, rollback, and compatibility plans exist.

## Pull request review

- [ ] The change matches the issue/PR scope and accepted architecture.
- [ ] Unrelated refactors are absent or separately justified.
- [ ] Inputs, outputs, and failure behavior are explicit.
- [ ] Security boundaries and secrets handling are preserved.
- [ ] Tests would fail without the intended change.
- [ ] Error messages are actionable and do not leak sensitive data.
- [ ] Public contracts remain compatible or include migration/versioning.
- [ ] Derived state can be rebuilt without losing canonical data.
- [ ] Documentation and ADRs are updated when needed.
- [ ] Reviewer can explain the change and its risks.

## Architecture review

- [ ] The design aligns with mission, principles, and current ADRs.
- [ ] The simplest viable architecture was considered.
- [ ] Canonical, derived, and operational data are separated.
- [ ] Trust boundaries and permissions are enforceable outside prompts.
- [ ] Scale assumptions have evidence and measurable budgets.
- [ ] Component failure and degraded operation are designed.
- [ ] Provider, plugin, and storage lock-in are assessed.
- [ ] Migration, compatibility, and rollback are feasible.
- [ ] New technical debt has an owner and exit condition.
- [ ] A new or updated ADR captures consequential decisions.

## Security review

- [ ] Assets, actors, entry points, and trust boundaries are identified.
- [ ] Least privilege and deny-by-default behavior are enforced.
- [ ] Prompt injection cannot grant tools, access, or durable memory.
- [ ] Paths, URLs, Markdown, and structured inputs are validated.
- [ ] Secrets use approved storage and never enter logs or prompts.
- [ ] Network egress and third-party destinations are controlled.
- [ ] Plugin/dependency provenance and update risks are assessed.
- [ ] Sensitive data is minimized, encrypted where appropriate, and auditable.
- [ ] Abuse cases include confused deputy, exfiltration, and privilege escalation.
- [ ] Security tests and incident/rollback procedures exist.

## Performance review

- [ ] User-facing latency and throughput budgets are stated.
- [ ] p50, p95, and p99 are measured by pipeline stage.
- [ ] Tests use representative vault sizes and relationship density.
- [ ] Indexing is incremental and cancellation-safe where required.
- [ ] Memory, CPU, disk, network, model, and cost impacts are measured.
- [ ] Cache correctness, invalidation, and privacy are validated.
- [ ] Timeouts, retries, backpressure, and provider limits are bounded.
- [ ] Slow-path diagnostics identify bottlenecks without leaking data.
- [ ] Degraded performance produces a usable partial response.
- [ ] Claimed optimization has before/after evidence.

## Documentation review

- [ ] Purpose, status, version, owner, related documents, and revision history exist.
- [ ] Audience and prerequisite knowledge are clear.
- [ ] Terms follow the project glossary.
- [ ] Statements distinguish current behavior from proposals.
- [ ] Examples are synthetic, safe, and consistent with schemas.
- [ ] Diagrams match the prose and render on GitHub.
- [ ] Relative links resolve and do not duplicate authoritative content.
- [ ] Decisions explain rationale and consequences.
- [ ] Operational instructions include validation and rollback.
- [ ] A new contributor can act without relying on private conversation history.

## Release readiness

- [ ] Release scope and version are frozen and documented.
- [ ] All acceptance criteria and required checks pass.
- [ ] Query regression, security, migration, and performance suites pass.
- [ ] Known issues and deferred risks are documented.
- [ ] Upgrade and rollback were tested from the supported prior version.
- [ ] Index rebuild and backup restore were validated.
- [ ] Documentation, examples, changelog, and release notes are complete.
- [ ] Dependency, license, and secret scans pass.
- [ ] Monitoring, support ownership, and incident response are ready.
- [ ] Architecture Review Board disposition is “Ready” or has accepted conditions.

## Evidence record

For consequential reviews, record:

| Field | Required content |
|---|---|
| Artifact | PR, design, release, or document reviewed |
| Reviewers | Human and AI reviewers with roles |
| Date | Review completion date |
| Checklist version | Version of this document |
| Exceptions | Failed or waived items and rationale |
| Evidence | Tests, traces, benchmarks, or links |
| Disposition | Approved, approved with conditions, revise, or stop |
| Follow-up owner/date | Accountable owner and due date |

## Revision history

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-07-27 | Initial reusable quality gates |
