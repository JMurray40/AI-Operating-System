# v0.4 Project Resume — Planning Index

| Field | Value |
|---|---|
| Milestone | v0.4 — Read-only Project Resume CLI Pilot |
| Status | Product Owner authorized implementation; CTO finalization in progress |
| Prerequisite | v0.3.1 accepted, released, and closed |
| Repository activity | Accepted: fixtures plus local read-only Git only |
| Implementation branch | Reserved: `feature/v0.4-project-resume`; create only after CTO package validation |
| Released architecture baseline | `main@2022c2dffeda8341011b45ceaedd550dd53bf742` |
| Implementation base | Pending exact commit containing accepted ADRs and final CTO brief |

## Current effective state

Architecture planning is complete and Product Owner implementation direction is recorded.
Engineering code remains blocked until the required ADRs and final CTO implementation
brief are complete and validated.

| Item | Current artifact/state |
|---|---|
| Accepted release tests | [v0.4 Project Resume Acceptance Tests](../../product/V0.4_PROJECT_RESUME_ACCEPTANCE_TESTS.md) |
| CTO planning brief | [Project Resume Planning Brief](00-cto-to-principal-engineer-project-resume-planning-brief.md) |
| Chief of Staff validation | [Planning Validation](00-chief-of-staff-project-resume-planning-validation.md) |
| Current incoming artifact | [Chief of Staff to CTO implementation finalization](01-chief-of-staff-to-cto-implementation-finalization.md) |
| Next responsible role | Chief Architect / CTO |
| Principal Engineer authorization | Pending CTO finalization |
| Required future authorization | `02-chief-of-staff-to-principal-engineer-implementation-authorization.md` |
| Conversation candidate | Parked and excluded; planned separately as v0.5 |

## Product Owner decision

[Repository Activity Scope Decision](00-product-owner-repository-activity-scope-decision.md):
v0.4 uses deterministic fixtures plus local read-only Git only. Live GitHub is deferred
to a separately authorized connector milestone.

## Remaining authorization gate

The future implementation authorization may be created only when:

1. CTO reconciles the brief against released baseline `main@2022c2d`;
2. required Project Resume ADRs are accepted;
3. the final CTO implementation brief closes all authorization-time refinements;
4. Chief of Staff validates and commits that package, then pins that exact `main` commit;
5. a clean `feature/v0.4-project-resume` worktree is created at that pinned base; and
6. the Principal Engineer receives the validated authorization prompt.
