# Prepared Prompt — v0.4 Pilot-Readiness Audit

**May run read-only while engineering is active. Do not inspect or modify unfinished
implementation unless the Chief of Staff explicitly supplies a frozen candidate.**

Act as an operational readiness auditor. Determine whether the two approved pilots—AI
Operating System and Cloud Organizer Pro—can produce valid, private, repeatable Project
Resume evidence when the candidate is ready.

Read the v0.4 acceptance tests, final CTO brief Sections 18–21, ADR-0021, and current
privacy/exclusion rules. Inventory without mutation:

- confirmed pilot locations and ownership;
- whether each has an identifiable canonical project note and permitted local repository;
- whether access can be granted request-by-request without broadening scope;
- Git availability/version and ability to use temporary fixture repositories;
- reference-hardware facts and which required facts remain unknown;
- approved ignored private destinations and whether they are outside canonical vaults;
- redacted committed-manifest fields versus prohibited private fields;
- benchmark modes, warm-ups, attempts, cold/warm labeling, and raw-sample retention;
- non-author installation environment availability;
- corrupt/missing derived-state recovery test feasibility; and
- blockers requiring Jason rather than assumptions.

Do not read private note contents beyond what is necessary to verify availability. Do not
run Project Resume, Git activity collection, benchmarks, or dogfood collection. Do not
write to either pilot, create credentials, or access GitHub/network services.

Produce a readiness report at:

```text
docs/handovers/v0.4/pilot-readiness-audit.md
```

Classify every requirement as `Ready`, `Missing`, `Needs Product Owner input`, or
`Candidate-dependent`, with no invented paths or hardware facts.

## Execution context

```text
repository: C:\Users\jmurr\Projects\AI-Operating-System
coordination_source: main
released_v0.3.1: v0.3.1
v0.4_immutable_base: 3253b052a3986e7d2c94124fbac86c03980e0765
engineering_worktree: C:\Users\jmurr\Projects\AI-Operating-System\.worktrees\v0.4-engineering
output: docs/handovers/v0.4/pilot-readiness-audit.md
```

The engineering worktree path is identity context only. Do not enter it or inspect
uncommitted work during this audit.

## Questions requiring explicit answers

For each pilot, record:

1. user-confirmed vault root or `Unknown`;
2. user-confirmed repository root or `None/Unknown`;
3. canonical project selector readiness without reading private contents;
4. availability of an authorization scope and request-scoped Git grant;
5. whether private evidence destinations exist, are ignored, and are outside the vault;
6. whether a clean non-author environment is available;
7. whether Python/Git/reference-hardware facts can be recorded;
8. whether cold/warm and denied/unavailable/authorized modes are operationally feasible;
9. whether before/after integrity inventories can be taken without changing timestamps;
10. exact Product Owner decisions still needed.

Also inspect `.gitignore`, documented pilot names, accepted privacy fields, benchmark
protocol, and recovery requirements. Checking path existence is allowed only for paths
already provided by the user or repository; do not search broadly outside scope.

## Evidence and handoff

The report must include an evidence table, blockers, owners, safe next actions, and a
statement that no pilot content, Git activity, benchmark, collection, or mutation was
performed. Do not stage or commit the report until the Chief of Staff validates that it
contains no private path or content disclosure.
