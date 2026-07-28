# Prepared Prompt — v0.4 Deferred-Risk Register

**May run read-only. Do not convert a risk into a blocker without evidence and the correct
decision owner.**

Act as Chief of Staff risk-register coordinator. Consolidate durable risks from v0.3.1
release evidence, the v0.4 final CTO brief, ADR-0018 through ADR-0021, engineering
handoffs, CTO/QA dispositions, and pilot-readiness evidence.

Track at minimum:

- benchmark attempt-level variability and lack of proven causal attribution;
- Windows symlink/junction test coverage and environmental skips;
- exact identity fallback behavior on project rename;
- sparse authority/supersession evidence and visible unknown/conflict outcomes;
- dual-budget serializer/accounting risk;
- local Git environment/config/path/process isolation;
- private pilot evidence leakage and redaction;
- packaging/non-author/recovery reproducibility;
- A11 eight-week strategic validation remaining pending;
- ADR-0001–0003/0006 decision-hygiene debt;
- future release numbering; and
- parked conversation reconciliation as v0.5.

For each risk record evidence, likelihood/impact without invented precision, owner,
mitigation, trigger, blocking milestone, status, and next review date. Distinguish accepted
residual risk, active blocker, technical debt, documentation debt, and future-scope gate.

Do not edit accepted evidence or reopen closed v0.3.1 findings without a concrete
regression signal. Do not assign product/architecture decisions to engineering.

Produce or update:

```text
docs/handovers/v0.4/v0.4-risk-register.md
```

## Source and update rules

Begin with current Project Control, v0.3.1 final QA/decision/Librarian records, v0.4
acceptance tests, ADR-0018 through ADR-0021, the final CTO brief, pilot-readiness report,
and only committed engineering evidence. Every entry must cite a repository artifact,
commit, test, or decision; unsupported concerns are labeled `Hypothesis`.

## Required fields

```text
risk_id:
category:
statement:
evidence:
status:
accepted_by:
owner:
likelihood: low | medium | high | unknown
impact: low | medium | high | unknown
affected_gate:
mitigation:
trigger:
next_review:
closure_evidence:
```

Use status `Open blocker`, `Accepted residual`, `Mitigating`, `Deferred debt`,
`Future-scope gate`, or `Closed`. Do not use numeric probability without measured data.

## Governance and reporting

Only the Product Owner accepts product/release risk; only the CTO accepts architecture
interpretations; QA owns release evidence; engineering owns implementation mitigation;
the Librarian owns record coherence. The register records those decisions but does not
make them.

Append changes with a dated history. Never delete an accepted risk or unfavorable
benchmark attempt. Summarize blockers first, then accepted residuals, then deferred/future
items. Stop after producing a documentation-only register update.
