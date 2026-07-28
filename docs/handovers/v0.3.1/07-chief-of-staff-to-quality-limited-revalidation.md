# Chief of Staff to Quality & Release — Limited Revalidation Prompt

| Field | Value |
|---|---|
| Sender | Chief of Staff |
| Receiver | Quality & Release |
| Milestone | v0.3.1 — Query Trust Contracts |
| Date | 2026-07-27 |
| Status | Authorized for limited execution |
| Review worktree | `C:\Users\jmurr\Projects\AI-Operating-System\.worktrees\v0.3.1-qa-revalidation` |
| Executable candidate | `956c2ed1dd1144e836014b049a89c47e971818a0` |
| Evidence commit | `8fa5f18c09de1a0c9a79f33e0ba987f9de0e1083` |
| Baseline | `ce0dc35853008e6b83c3c6fdfd0b8650738bee3d` |

## Role and primary question

Act as Quality & Release. Determine whether the narrowly remediated v0.3.1 candidate and
its retained performance evidence satisfy affected review Areas A, G, and H and can be
returned to the Product Owner with a release disposition.

Conversation history and verbal summaries are not authoritative. Verify repository state,
artifacts, arithmetic, and execution results directly.

## Startup and source locations

1. Work only from the detached review worktree named above for executable testing.
2. Verify that it is detached at exactly
   `956c2ed1dd1144e836014b049a89c47e971818a0` and initially clean.
3. Read [Project Control](../../coordination/README.md) and the
   [v0.3.1 Handoff Index](README.md) from the engineering worktree.
4. Read the latest superseding revision of the
   [CTO Architecture Disposition](04-cto-to-quality-architecture-disposition.md).
5. Read the Rev 6 Evidence Addendum in the
   [Engineering Review](03-principal-engineer-to-cto-engineering-review.md).
6. Read the existing
   [Quality & Release Review](05-quality-to-product-owner-release-review.md), including
   its prepared A/G/H checklist.
7. Inspect `docs/evidence/v0.3.1/paired-performance-956c2ed-vs-ce0dc35.json` in the
   engineering worktree at evidence commit `8fa5f18c09de1a0c9a79f33e0ba987f9de0e1083`.

The detached review worktree intentionally contains the executable candidate, not later
documentation-only evidence and disposition commits. Do not copy those files into it or
alter its reviewed state.

## Authorized scope

Revalidate only Area A (candidate and evidence integrity), Area G (operational entry points
and safety affected by remediation), Area H (performance evidence and gate), and evidence
directly affected by the benchmark and evidence corrections.

Follow the complete adversarial matrix in the latest CTO disposition. In particular:

- verify the executable/evidence identity split and prove that no executable, test, or
  benchmark-protocol files changed after `956c2ed`;
- independently verify artifact SHA-256
  `f8a67162b74125454f2a5199e6b46a33952763fff18821b7c81497819ffa18d6`;
- count all five pairs of 30 candidate and 30 baseline samples and independently recompute
  every p50, p95, p99, per-attempt regression, and aggregate;
- run both documented benchmark entry points from repository root without a `PYTHONPATH`
  override and run the real subprocess smoke coverage;
- verify import isolation, completion and failure behavior, temporary-directory
  confinement, and unchanged canonical sources;
- validate or rerun the paired/interleaved protocol against the exact candidate and
  baseline using equivalent conditions; and
- apply the predeclared median-of-five paired-p95 rule with a 20% ceiling.

The retained result reports 8.74%–23.64%, median 11.56%. Preserve the 23.64% attempt in
the QA record. Treat scheduler or background-load causation as inference unless
independently instrumented evidence proves it.

## Exclusions and controls

Do not reopen unaffected QA areas without a concrete regression signal; implement fixes;
modify source, tests, protocol, evidence, or gate rules; change reviewed identities; use
an after-the-fact rule or waiver; merge, push, release; touch parked conversation work;
or begin v0.4 implementation.

If a blocking defect appears, record exact reproducible evidence and return one
`Refactor first` disposition. Do not repair it in the QA role.

## Required output

Append a clearly marked superseding limited-revalidation revision to the existing
[Quality & Release Review](05-quality-to-product-owner-release-review.md) in the engineering
worktree. Do not create a competing QA artifact.

The revision must pin all identities and the digest; report Areas A, G, and H separately;
document integrity, arithmetic, and execution checks; state the predeclared rule; disclose
the full range, median, and over-20% attempt; separate observations from inference; explain
any concrete signal that justified broader review; issue exactly one Product Owner
disposition; and stop without fixes, merge, push, release, or closeout.

Valid dispositions are `Ready`, `Ready with conditions`, `Refactor first`, or `Stop`.

## Exit statement

**READY FOR LIMITED QUALITY & RELEASE REVALIDATION.** Authority is limited to the exact
identities and Areas A, G, and H stated above.
