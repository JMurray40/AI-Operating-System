# Chief of Staff Validation and Principal Engineer Prompt

| Field | Value |
|---|---|
| Role | Principal Engineer / Claude |
| Milestone | v0.3.1 — Query Trust Contracts |
| Status | Validated for implementation |
| Validated | 2026-07-27 |
| Code baseline | `main` at `ce0dc35853008e6b83c3c6fdfd0b8650738bee3d` |
| Clean branch point | The documentation-only governance commit containing this file; exact SHA is supplied when the Claude session is launched |
| Required branch | `feature/v0.3.1-query-trust-contracts` |
| Engineering output | `docs/handovers/v0.3.1/03-principal-engineer-to-cto-engineering-review.md` |

## Chief of Staff validation

The CTO brief was checked against the accepted requirements, ADR-0014 through ADR-0017,
Governance, Ways of Working, and the Implementation Brief Contract.

Validation result: **Approved for Principal Engineer implementation.**

The brief contains the required objective, repository and branch controls, exact code
baseline, authoritative inputs, architecture constraints, acceptance criteria, exclusions,
Definition of Done, performance gates, testing expectations, documentation expectations,
known risks, escalation rules, and outgoing evidence contract.

The clean implementation branch point contains only accepted documentation and coordination
artifacts on top of the exact code baseline. It contains no conversation implementation.

## Principal Engineer instruction

Read, in order:

1. [Project Control and Handoff Index](../../coordination/README.md)
2. [Product Owner Approval](01-product-owner-to-cto-architecture-approval.md)
3. [CTO Implementation Brief](02-cto-to-principal-engineer-implementation-brief.md)
4. Every authoritative artifact named by the CTO brief.

Primary question:

> Can this be built well?

Implement only v0.3.1 Query Trust Contracts. Do not import, merge, cherry-pick, or otherwise
use the parked conversation candidate.

Before changing code:

1. verify the current branch is `feature/v0.3.1-query-trust-contracts`;
2. verify `HEAD` equals the governance commit SHA supplied at session launch;
3. verify that `HEAD` descends from code baseline
   `ce0dc35853008e6b83c3c6fdfd0b8650738bee3d`;
4. verify the worktree is clean;
5. confirm the accepted artifacts and this prompt are present;
6. present the implementation plan, affected contracts, test plan, security implications,
   and migration approach before implementation.

Stop and escalate if any precondition fails or if an accepted decision must change.
Conversation history is not authoritative.

When implementation is complete, produce the full Engineering Review required by the CTO
brief at:

```text
docs/handovers/v0.3.1/03-principal-engineer-to-cto-engineering-review.md
```

Do not merge or push the implementation branch.

## Exit statement

**Validated and ready for Principal Engineer implementation** once launched from the exact
clean governance commit identified by the Chief of Staff.
