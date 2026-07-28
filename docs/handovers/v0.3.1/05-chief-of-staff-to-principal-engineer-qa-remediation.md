# Chief of Staff to Principal Engineer — QA Remediation

| Field | Value |
|---|---|
| Role | Principal Engineer / Claude |
| Milestone | v0.3.1 — Query Trust Contracts |
| Trigger | Quality & Release disposition: Refactor first |
| QA-reviewed candidate | `09a4ca5a6e0d9b73a1e37a9e086abe788c894c72` |
| Required branch | `feature/v0.3.1-query-trust-contracts` |
| Release status | Blocked |
| Required engineering output | Rev 6 in `03-principal-engineer-to-cto-engineering-review.md` |

## Objective

Correct only QR-031-01 through QR-031-03 from the independent
[QA review](05-quality-to-product-owner-release-review.md). Do not modify the accepted
trust-contract implementation.

## QR-031-01 — Direct benchmark entry points

- Make both documented commands run from the repository root without an undocumented
  `PYTHONPATH` override:

```text
python scripts/benchmark_query.py --sizes 100,500,1000 --runs 10
python scripts/benchmark_regression.py --runs 20
```

- Preserve candidate/baseline isolation.
- Do not create a broad packaging/import framework for this correction.
- Rerun and record every benchmark phase from the exact supported commands.

## QR-031-02 — Process-boundary smoke test

- Replace or extend the import-based smoke test with a subprocess or equivalent true
  process-start boundary from the repository root.
- Execute the documented scripts far enough to prove imports, argument parsing, warm-up,
  measured query, memory, authorization stress, and regression paths start and complete.
- Assert successful exit and stable required completion markers.
- Prove the test fails when the runtime dependency import is unavailable.

Keep the smoke workload small enough for the normal suite.

## QR-031-03 — Stable performance evidence

- Define a paired or interleaved same-machine baseline/candidate protocol that reduces
  run-order and background-load bias.
- Use identical fixtures, queries, Python, warm-ups, measured runs, percentile estimator,
  and construction-plus-query boundary.
- Retain raw samples for both versions in a reproducible evidence location or output.
- Run multiple paired attempts and report per-pair and aggregate variance.
- Demonstrate the accepted p95 result is no more than 20% above baseline, or stop and
  report a failed gate without seeking a silent waiver.

Do not tune away authorization, current-byte citation validation, or other release work to
meet the performance gate.

## Required verification

Report:

- full pytest;
- Ruff;
- mypy;
- `git diff --check`;
- unchanged-vault evidence covering both benchmark entry points;
- direct documented benchmark results;
- process-boundary smoke results;
- paired raw performance results;
- exact corrected HEAD and diff from the QA-reviewed candidate.

Append **Rev 6** to the Engineering Review. Confirm that no trust-contract code, closed
finding, parked conversation work, or out-of-scope capability changed.

## Review sequence

1. Stop for CTO architecture clearance of the changed benchmark/test scope.
2. After clearance, Quality & Release reruns affected matrix areas A, G, and H plus any
   impacted evidence.
3. Do not merge, push, or begin either review role yourself.

## Exit statement

**Ready for benchmark-only QA remediation.** Release remains blocked.
