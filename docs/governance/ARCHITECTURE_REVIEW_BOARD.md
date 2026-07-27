# Standing Architecture Review Board

| Field | Value |
|---|---|
| Purpose | Create a recurring architecture-alignment review after every material implementation |
| Status | Active process |
| Version | 1.0.0 |
| Owner | Jason |
| Revised | 2026-07-27 |
| Related | [Jarvis Bible](../JARVIS_BIBLE.md), [Engineering Checklists](../ENGINEERING_QUALITY_CHECKLISTS.md), [Decision Matrix](../ARCHITECTURE_DECISION_MATRIX.md) |

## Operating model

Claude or another implementation engineer builds the approved release scope. GPT/Codex serves as a standing Architecture Review Board (ARB), reviewing the implementation report and evidence for alignment—not replacing code review or CI.

This separation is intentional:

- the implementation engineer optimizes for correct delivery;
- the ARB optimizes for long-term coherence, simplicity, trust, and readiness;
- Jason accepts decisions and authorizes the next phase.

## Mandatory review trigger

Run an ARB review after:

- every version or milestone implementation;
- a new trust boundary, canonical store, public schema, provider, plugin, MCP server, agent, or write path;
- a major dependency or deployment change;
- a migration or material performance redesign;
- a security incident or significant regression.

## Required review packet

The implementation engineer provides:

1. objective, scope, and acceptance criteria;
2. implementation summary and architecture/data-flow changes;
3. files, schemas, migrations, dependencies, and ADRs affected;
4. tests/evaluations, results, performance, and known limitations;
5. security/privacy/permission analysis;
6. operational impact, observability, rollback, and compatibility;
7. technical debt introduced or retired;
8. deviations from PRD/architecture and reasons;
9. decisions requested;
10. recommended next phase.

## ARB questions

The review MUST answer:

- Does the implementation align with mission, product strategy, PRD, principles, ADRs, and behavior standard?
- Did it add unnecessary abstraction, services, dependencies, or duplicated responsibility?
- Did a prototype seam accidentally become a public platform contract?
- Is canonical ownership still unambiguous?
- Are read-only, sensitivity, permission, provenance, and rollback guarantees preserved?
- Did it introduce hidden coupling or provider/plugin/framework lock-in?
- Are schemas versioned and compatibility behavior explicit?
- Are performance and scale claims supported by representative evidence?
- Is technical debt documented with owner and trigger?
- Is the feature supportable and diagnosable?
- What should be simplified or refactored before the next phase?
- Is the release ready, conditionally ready, or not ready?

## Decision outcomes

| Outcome | Meaning |
|---|---|
| Ready | Meets gates; next phase may begin after human acceptance |
| Ready with conditions | Safe to proceed only after named follow-ups with owners/dates |
| Refactor first | Current implementation works but compounds architectural risk |
| Not ready | Acceptance, safety, recovery, or evidence is materially incomplete |
| Re-scope | Product value does not justify complexity or current sequencing |

## Review output

Save `docs/reviews/arb/YYYY-MM-DD-vX.Y-architecture-review.md` containing:

- executive decision;
- alignment findings;
- strengths;
- complexity and debt;
- security/privacy;
- performance/operability;
- ADR conformance and new decisions;
- required changes, owners, and gates;
- readiness outcome;
- reminder for the next ARB trigger.

## Standing prompt

```text
Act as the standing Architecture Review Board for AI Operating System.

Read the Jarvis Bible, Product Strategy, relevant PRDs, System Principles,
Architecture Decision Matrix, ADRs, AI Behavior Standard, Security Threat Model,
and the attached implementation report.

Evaluate alignment, unnecessary complexity, technical debt, duplicated
responsibilities, trust-boundary changes, canonical ownership, permissions,
read-only guarantees, schema compatibility, performance evidence, operability,
and readiness for the next phase.

Do not perform a general code review. Cite concrete implementation evidence.
Classify the outcome as Ready, Ready with conditions, Refactor first,
Not ready, or Re-scope. List blocking actions, owners, and required ADRs.
```

## Reminder rule

At the completion of every future Claude implementation, remind Jason to provide the implementation report and run this ARB review before authorizing the next version.

## Revision history

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-07-27 | Established the standing implementation/architecture feedback loop |
