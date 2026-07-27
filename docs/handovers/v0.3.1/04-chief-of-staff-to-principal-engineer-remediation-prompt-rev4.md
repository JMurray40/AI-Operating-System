# Chief of Staff Benchmark Entry-Point Correction — Rev 4

| Field | Value |
|---|---|
| Role | Principal Engineer / Claude |
| Milestone | v0.3.1 — Query Trust Contracts |
| Trigger | Final Superseding CTO Revision 4: Refactor first |
| Returned implementation | `649e5a2ecfc98b2c4c9f23b5456716bb5f05f7f9` |
| Required branch | `feature/v0.3.1-query-trust-contracts` |
| QA status | Blocked |
| Required output | Rev 5 in `03-principal-engineer-to-cto-engineering-review.md` |

## Objective

Correct only the unmigrated `scripts/benchmark_query.py` entry point. All implementation
contracts, other findings, and the performance gate are closed.

## Required correction

1. Pass the synthetic vault root to every current-version `QueryEngine` construction in
   `scripts/benchmark_query.py`, including warm-up and memory measurement paths.
2. Add an automated smoke test or equivalent enforced check that executes the documented
   benchmark entry point far enough to detect constructor-contract drift.
3. Search all non-baseline current-version call sites and prove none omit either explicit
   authorization scope or mandatory `source_root`.
4. Rerun:
   - full tests;
   - Ruff;
   - mypy;
   - `git diff --check`;
   - unchanged-vault verification;
   - the documented query benchmark;
   - the regression benchmark.
5. Append **Rev 5** to the Engineering Review with the exact correction diff from
   `649e5a2ecfc98b2c4c9f23b5456716bb5f05f7f9`, corrected HEAD, test mapping, commands,
   results, and branch/merge/push status.

Do not modify citation semantics, compatibility, authorization, performance gates, or any
other closed finding. Do not begin QA, merge, push, or touch the parked conversation
worktree.

## Exit statement

**Ready for the final benchmark entry-point correction.** QA remains blocked pending exact
HEAD clearance by the CTO.
