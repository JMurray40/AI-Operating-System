# Chief of Staff to CTO — v0.4 Implementation Finalization

| Field | Value |
|---|---|
| Sender | Chief of Staff |
| Receiver | Chief Architect / CTO |
| Milestone | v0.4 — Read-only Project Resume CLI Pilot |
| Date | 2026-07-27 |
| Status | **Authorized architecture-finalization gate** |
| Repository | `AI-Operating-System` |
| Architecture reconciliation branch | `main` |
| Released architecture baseline | `2022c2dffeda8341011b45ceaedd550dd53bf742` |
| Future engineering base | Exact clean `main` commit containing the accepted ADRs and final CTO brief; Chief of Staff pins it after validation |
| Released prerequisite | `v0.3.1` |
| Product Owner implementation direction | **Begin v0.4 implementation** |

## Role and primary question

Act as Chief Architect / CTO. Determine whether the validated Project Resume planning
architecture can be implemented safely on released v0.3.1, then produce the missing
accepted decisions and a final implementation brief.

Conversation history is not authoritative. Begin with [Project Control](../../coordination/README.md)
and the [v0.4 Planning Index](README.md).

## Gate status

The following prerequisites are closed:

- v0.3.1 is released as tag `v0.3.1`;
- released v0.3.1 code is pinned at
  `2022c2dffeda8341011b45ceaedd550dd53bf742`;
- the v0.3.1 executable, evidence, QA, Product Owner, and Librarian lifecycle is closed;
- the Product Owner chose deterministic fixtures plus local read-only Git only;
- live GitHub, credentials, network access, and provider egress are excluded; and
- the Product Owner explicitly directed the project to begin v0.4 implementation.

Engineering remains blocked only until this architecture-finalization package is complete
and validated.

## Authoritative inputs

Read in precedence order:

1. [v0.4 Acceptance Tests](../../product/V0.4_PROJECT_RESUME_ACCEPTANCE_TESTS.md)
2. [Product Owner repository-activity decision](00-product-owner-repository-activity-scope-decision.md)
3. [v0.3.1 final release acceptance](../v0.3.1/08-product-owner-final-release-acceptance.md)
4. [Project Resume planning brief](00-cto-to-principal-engineer-project-resume-planning-brief.md)
5. [Chief of Staff planning validation](00-chief-of-staff-project-resume-planning-validation.md)
6. ADR-0012 and accepted ADR-0014 through ADR-0017
7. the merged v0.3.1 implementation and current documentation at the pinned base

The accepted tests and Product Owner decisions control scope. The planning brief remains
proposed where this final review changes or sharpens it.

## Required architecture work

### 1. Reconcile against released code

Inspect the actual v0.3.1 query engine, authorization scope, source-root/current-byte
validation, identity, citation, context budget, result, trace, CLI, filesystem repository,
and benchmark boundaries. Identify every reusable contract and every required additive
extension. Do not assume proposed package names already match the implementation.

### 2. Accept the missing durable decisions

Create and accept separate ADRs, using the next available ADR numbers, for:

1. Project Resume exact identity and ambiguity semantics;
2. authority, temporal ordering, supersession, and conflict semantics;
3. claim support, coverage, evidence budget, and output budget contracts; and
4. the fixture/local-read-only-Git repository-activity port and request-scoped capability
   boundary.

The fourth ADR must define permitted Git commands/arguments, repository-root confinement,
environment handling, timeout, bounded output, deterministic parsing, error redaction,
non-mutation proof, unavailable/denied/malformed/stale outcomes, and test seams that do
not require installed Git.

Update the ADR index. Do not accept live GitHub or a generic connector framework.

### 3. Close authorization-time refinements

The final brief must define:

- branch `feature/v0.4-project-resume`;
- released architecture baseline
  `main@2022c2dffeda8341011b45ceaedd550dd53bf742`;
- the rule that the implementation base is the exact clean `main` commit containing the
  accepted Project Resume ADRs and final brief, to be recorded by the Chief of Staff after
  validating and committing the CTO package;
- affected-file/package forecast;
- exact local-Git subprocess and security boundaries;
- reference hardware and required benchmark protocol;
- raw benchmark evidence destination;
- pilot-vault evidence destination and privacy controls;
- dogfood record destination and consent boundary, or a manual external scorecard;
- packaging and non-author recovery evidence;
- requirement-to-test mapping for A1–A12; and
- the precise engineering-to-CTO handoff path.

If the eight-week A11 gate is post-candidate evidence, distinguish technical candidate
completion from strategic validation and prohibit claims that v0.5 is unlocked early.

## Required output

Produce:

```text
docs/handovers/v0.4/01-cto-to-principal-engineer-implementation-brief.md
```

The brief must satisfy the complete Implementation Brief Contract in Ways of Working and
end with one disposition:

- `Ready for Chief of Staff validation and engineering branch creation`; or
- `Blocked`, with the exact unresolved owner and decision.

Also create the required accepted ADRs and update `docs/adr/README.md`.

Do not create the engineering branch, write implementation code, run Principal Engineer
work, touch the parked conversation worktree, merge, tag, or release.

## Scope exclusions

Exclude visible-context/multi-turn chat, the parked conversation branch, providers,
streaming, durable conversation state, memory, vault writes, schema migration, embeddings,
vectors, plugins, MCP, agents, tools/actions, automation, watchers, dashboard UI, live
GitHub, remote APIs, credentials, and unrelated refactoring.

## Exit statement

**READY FOR CTO IMPLEMENTATION FINALIZATION.** Principal Engineer implementation remains
blocked until the CTO package is complete and Chief of Staff validates it against the
released base.
