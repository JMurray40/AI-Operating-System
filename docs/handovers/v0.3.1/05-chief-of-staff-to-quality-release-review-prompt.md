# Chief of Staff to Quality & Release — Review Prompt

| Field | Value |
|---|---|
| Role | Quality & Release Manager |
| Milestone | v0.3.1 — Query Trust Contracts |
| Architecture disposition | Ready for Quality & Release |
| Authorized candidate | `feature/v0.3.1-query-trust-contracts@09a4ca5a6e0d9b73a1e37a9e086abe788c894c72` |
| Review posture | Adversarial and independent |
| Required output | `05-quality-to-product-owner-release-review.md` |

## Objective

Determine what evidence says this exact candidate should **not** ship. Review the
implementation and engineering evidence independently. Do not defer to the CTO clearance
or regenerate the implementation.

## Required inputs

1. [Project Control](../../coordination/README.md)
2. [CTO Implementation Brief](02-cto-to-principal-engineer-implementation-brief.md)
3. [Engineering Review, including Rev 1–5](03-principal-engineer-to-cto-engineering-review.md)
4. [CTO Disposition, Exact-HEAD Clearance Revision 5](04-cto-to-quality-architecture-disposition.md)
5. ADR-0012 and ADR-0014 through ADR-0017.
6. The complete candidate diff from governance base
   `a6c89c5be8ce78a4d9d6359a62c94aa83a84d513` through the authorized HEAD.

## Preconditions

Before QA:

- verify the exact branch and authorized HEAD;
- verify the starting worktree is clean;
- verify no remote branch contains the candidate and it is not merged into `main`;
- record the environment and available toolchain;
- stop if the candidate changes after verification.

## Review contract

Execute every area A–I in the activated adversarial QA matrix in Exact-HEAD CTO Clearance
Revision 5. At minimum, independently rerun:

- the full test suite;
- Ruff;
- mypy;
- `git diff --check`;
- unchanged-vault/read-only checks;
- documented query benchmark;
- benchmark smoke test;
- equivalent total-pipeline regression benchmark;
- targeted adversarial checks for authorization, non-disclosure, current-source
  validation, path/symlink confinement, citation support, evidence coverage, compatibility,
  context budget, CLI/JSON behavior, and exit codes.

Sample claims rather than accepting green summaries. Record any environment limitation,
failure, waiver request, or evidence gap.

## Independence and constraints

- Remain read-only except for the required QA artifact.
- Do not fix defects or modify the candidate.
- Do not merge, push, rebase, amend, or touch the parked conversation worktree.
- Treat chat, streaming, providers, Project Resume, memory, plugins, MCP, agents,
  automation, and writes as out of scope.
- Any trust-boundary, read-only, contract, or performance-gate failure is blocking unless
  governance explicitly supersedes it.

## Required output

Produce:

```text
docs/handovers/v0.3.1/05-quality-to-product-owner-release-review.md
```

The artifact must include exact branch, HEAD, environment, commands, results, failures,
waivers, residual risks, evidence locations, and one explicit disposition:

- Ready
- Ready with conditions
- Refactor first
- Not ready
- Re-scope

Stop after the QA disposition. The Product Owner retains final go/no-go authority.

## Exit statement

**Quality & Release is authorized only for the exact candidate identified above.**
