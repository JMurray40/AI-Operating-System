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

