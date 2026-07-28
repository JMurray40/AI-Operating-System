# v0.4 Project Resume — Planning Index

| Field | Value |
|---|---|
| Milestone | v0.4 — Read-only Project Resume CLI Pilot |
| Status | Principal Engineer implementation authorized |
| Prerequisite | v0.3.1 accepted, released, and closed |
| Repository activity | Accepted: fixtures plus local read-only Git only |
| Implementation branch | `feature/v0.4-project-resume` |
| Released architecture baseline | `main@2022c2dffeda8341011b45ceaedd550dd53bf742` |
| Implementation base | `3253b052a3986e7d2c94124fbac86c03980e0765` |

## Current effective state

Architecture planning and finalization are complete. ADR-0018 through ADR-0021 and the
final CTO implementation brief are accepted and committed. Principal Engineer
implementation is authorized on the exact branch and base above.

| Item | Current artifact/state |
|---|---|
| Accepted release tests | [v0.4 Project Resume Acceptance Tests](../../product/V0.4_PROJECT_RESUME_ACCEPTANCE_TESTS.md) |
| CTO planning brief | [Project Resume Planning Brief](00-cto-to-principal-engineer-project-resume-planning-brief.md) |
| Chief of Staff validation | [Planning Validation](00-chief-of-staff-project-resume-planning-validation.md) |
| Current incoming artifact | [Chief of Staff Principal Engineer authorization](02-chief-of-staff-to-principal-engineer-implementation-authorization.md) |
| Next responsible role | Principal Engineer |
| Final CTO brief | [Implementation brief](01-cto-to-principal-engineer-implementation-brief.md) |
| Principal Engineer authorization | Active |
| Required engineering output | `02-principal-engineer-to-cto-engineering-review.md` |
| Conversation candidate | Parked and excluded; planned separately as v0.5 |

## Product Owner decision

[Repository Activity Scope Decision](00-product-owner-repository-activity-scope-decision.md):
v0.4 uses deterministic fixtures plus local read-only Git only. Live GitHub is deferred
to a separately authorized connector milestone.

## Engineering gate

The future implementation authorization may be created only when:

1. Principal Engineer verifies the exact branch, worktree, immutable base, and authorized
   documentation-only starting delta.
2. Principal Engineer presents the required implementation plan.
3. Engineering implements only the final brief and accepted ADRs.
4. Engineering produces the required exact-HEAD handoff to CTO.
5. CTO and QA remain blocked until that handoff is complete.
