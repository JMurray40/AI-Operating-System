# Chief of Staff to Principal Engineer — Performance Evidence Correction

| Field | Value |
|---|---|
| Role | Principal Engineer / Claude |
| Milestone | v0.3.1 — Query Trust Contracts |
| Trigger | CTO disposition: Evidence correction required |
| Executable candidate | `956c2ed1dd1144e836014b049a89c47e971818a0` |
| Exact baseline | `ce0dc35853008e6b83c3c6fdfd0b8650738bee3d` |
| Scope | Documentation and retained evidence only |
| QA status | Blocked |

## Objective

Close only QR-031-03 by retaining independently recomputable raw performance evidence.
QR-031-01 and QR-031-02 are closed. Do not change executable files, tests, benchmark
protocol, configuration, contracts, or product documentation unrelated to the evidence.

## Required evidence run

Run the accepted paired/interleaved command against the exact executable candidate and
baseline with `--out` enabled. Use the already accepted protocol:

- 1,000 notes;
- 30 measured runs per version per attempt;
- five attempts;
- identical query, warm-ups, fixture, percentile estimator, Python, and machine;
- alternating candidate-first/baseline-first order;
- construction plus one public query boundary.

Preserve the complete generated JSON at:

```text
docs/evidence/v0.3.1/paired-performance-956c2ed-vs-ce0dc35.json
```

The evidence must contain every raw candidate and baseline sample for every attempt.

## Required metadata and validation

Record alongside the samples:

- full candidate and baseline commit identifiers;
- exact command;
- Python version;
- OS/machine/environment identity;
- note count, query, warm-ups, runs, attempts, and percentile method;
- attempt order;
- generated timestamp;
- per-attempt candidate and baseline p50/p95/p99;
- per-attempt regression;
- aggregate minimum, maximum, and median regression;
- pass/fail against the 20% ceiling.

Independently recompute the summaries from the retained arrays and verify the stored
derived values. Compute the artifact SHA-256 after final serialization.

## Engineering Review update

Append an **Evidence Addendum to Rev 6** to
`03-principal-engineer-to-cto-engineering-review.md` containing:

- stable evidence path;
- SHA-256;
- exact execution identities and conditions;
- exact command;
- recomputed result table and aggregate;
- confirmation of sample counts;
- confirmation that no executable/test/protocol file changed;
- exact evidence commit and diff from executable candidate `956c2ed…`.

Only the evidence JSON, Engineering Review addendum, and directly required coordination
metadata may change.

## Exit and review sequence

Stop for a CTO evidence-integrity review limited to:

- the retained artifact;
- arithmetic recomputation;
- digest;
- candidate/baseline binding;
- confirmation that no executable file changed.

Do not begin QA, merge, push, or modify the parked conversation worktree.

## Exit statement

**Ready for documentation/evidence-only correction.** QA remains blocked.
