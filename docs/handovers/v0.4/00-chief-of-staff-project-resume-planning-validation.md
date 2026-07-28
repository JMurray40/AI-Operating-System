# Chief of Staff Validation — v0.4 Project Resume Planning

| Field | Value |
|---|---|
| Role | Chief of Staff |
| Milestone | v0.4 — Read-only Project Resume CLI Pilot |
| Reviewed artifact | `00-cto-to-principal-engineer-project-resume-planning-brief.md` |
| Validation date | 2026-07-27 |
| Disposition | Planning validated; implementation not authorized |

## Validation result

The CTO planning brief is consistent with the accepted v0.4 Project Resume acceptance
tests and the accepted v0.3.1 trust-contract architecture.

It adequately defines:

- layered application architecture over the v0.3.1 query and trust pipeline;
- exact project identity and ambiguity behavior;
- mandatory authorization and current-source validation;
- claim, citation, authority, temporal, conflict, coverage, and degradation semantics;
- hard evidence and output budgets;
- deterministic trace behavior and non-disclosure;
- A1–A12 requirement-to-evidence mapping;
- adversarial fixtures and security tests;
- performance, packaging, recovery, and dogfood gates;
- explicit exclusions and forbidden work;
- future engineering and review handoff contracts.

The absence of an implementation branch, base commit, and exact SHA is intentional and
correct at this stage. This is a planning brief, not the final Implementation Brief
Contract.

## Required refinements at authorization time

Before creating the implementation authorization:

1. pin the exact post-v0.3.1 base branch and commit;
2. reconcile proposed contracts with the merged v0.3.1 implementation;
3. identify and accept any required Project Resume ADRs;
4. convert proposed package names into an affected-file forecast, without constraining the
   Principal Engineer's implementation ownership;
5. define exact performance reference hardware and dogfood evidence destination;
6. record the repository-activity decision;
7. confirm that any local Git subprocess boundary is already approved or separately
   review its command, path, timeout, output, and injection controls.

## Product Owner decision

The Product Owner approved fixture data plus local read-only Git for v0.4. Live GitHub
reads are deferred. See
[Repository Activity Scope Decision](00-product-owner-repository-activity-scope-decision.md).

## Constraints

This validation does not authorize:

- a v0.4 branch;
- implementation;
- live GitHub access;
- reuse of the parked conversation candidate;
- changes to v0.3.1;
- writes, providers, conversation, agents, MCP, plugins, or automation.

## Exit statement

**Planning validated and parked behind the v0.3.1 release gate.**
