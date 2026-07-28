# v0.4 Project Resume — Planning Index

| Field | Value |
|---|---|
| Milestone | v0.4 — Read-only Project Resume CLI Pilot |
| Status | Planning validated; implementation blocked |
| Prerequisite | v0.3.1 accepted, released, and closed |
| Next decision | Repository activity scope |
| Implementation branch | Not authorized |
| Implementation base | Not pinned |

## Current effective state

Architecture planning is complete. No engineering work may begin.

| Item | Current artifact/state |
|---|---|
| Accepted release tests | [v0.4 Project Resume Acceptance Tests](../../product/V0.4_PROJECT_RESUME_ACCEPTANCE_TESTS.md) |
| CTO planning brief | [Project Resume Planning Brief](00-cto-to-principal-engineer-project-resume-planning-brief.md) |
| Chief of Staff validation | [Planning Validation](00-chief-of-staff-project-resume-planning-validation.md) |
| Principal Engineer authorization | Does not exist |
| Required future authorization | `01-chief-of-staff-to-principal-engineer-implementation-authorization.md` |
| Conversation candidate | Parked and excluded; planned separately as v0.5 |

## Open decision

The Product Owner must choose the v0.4 repository-activity boundary:

1. fixture plus local read-only Git only; or
2. separately authorize live GitHub reads with connector, credential, egress, timeout,
   rate-limit, permission, and security gates.

Chief of Staff recommendation: **fixture plus local read-only Git only**. Defer live GitHub
to a separately authorized connector milestone.

## Authorization gate

The future implementation authorization may be created only when:

1. v0.3.1 has a Product Owner release decision and Librarian closeout;
2. the selected v0.4 base contains the released trust contracts;
3. the repository-activity decision is recorded;
4. the brief is reconciled against the merged base;
5. required new ADRs are accepted;
6. the Product Owner explicitly authorizes implementation;
7. a clean branch and exact base SHA are pinned.
