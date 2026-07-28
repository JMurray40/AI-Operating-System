# Product Owner to Historian / Librarian — v0.3.1 Release Decision

| Field | Value |
|---|---|
| Product Owner | Jason Murray |
| Recorded by | Chief of Staff |
| Receiver | Historian / Librarian |
| Milestone | v0.3.1 — Query Trust Contracts |
| Decision date | 2026-07-27 |
| Decision | **Approved** |
| Executable candidate | `956c2ed1dd1144e836014b049a89c47e971818a0` |
| Evidence commit | `8fa5f18c09de1a0c9a79f33e0ba987f9de0e1083` |
| Evidence SHA-256 | `f8a67162b74125454f2a5199e6b46a33952763fff18821b7c81497819ffa18d6` |
| QA disposition | `Ready` |

## Decision

The Product Owner approves v0.3.1 Query Trust Contracts for controlled merge and release
execution, following the accepted lifecycle:

1. merge the reviewed feature lineage into `main`;
2. perform the required post-merge Historian / Librarian reconciliation;
3. verify the merged release state and close documentation drift; and
4. complete push, tagging, or public release only after that closeout is accepted.

This decision accepts the exact executable candidate and evidence identities above. It
does not authorize substitution of a different executable implementation.

## Accepted evidence

- The final CTO disposition is **Ready for limited Quality & Release revalidation**.
- Quality & Release independently revalidated Areas A, G, and H and issued **Ready**.
- The retained paired benchmark has a predeclared median-of-five p95 rule with a 20%
  ceiling. Its median is 11.56%.
- The independent Windows rerun also passes with a 14.52% median.
- All retained and fresh individual attempts remain disclosed, including results above
  20%.
- No waiver was requested or granted.

## Accepted residual risks

The Product Owner accepts the following for v0.3.1:

1. material attempt-level benchmark variability, including retained 23.64% and fresh
   Windows 40.94% individual results, because the predeclared aggregate gate passes;
2. no proven causal attribution for the observed timing variability;
3. the previously documented Windows symlink-test environmental limitation; and
4. the accepted aggregate-timing side-channel and operational-measurement debt.

These risks remain part of the durable release record and must not be erased or rewritten
as individual-attempt compliance.

## Merge and release controls

- Merge only the reviewed `feature/v0.3.1-query-trust-contracts` lineage descended from
  executable candidate `956c2ed`.
- Preserve the engineering, architecture, QA, evidence, and Product Owner decision
  artifacts in the merged history.
- Do not touch or merge the parked conversation candidate.
- Do not begin v0.4 implementation as part of the v0.3.1 merge.
- Do not push, tag, publish, or announce the release before post-merge verification and
  Librarian closeout.
- Any merge conflict affecting executable, accepted requirements, ADRs, evidence, or
  release semantics invalidates automatic execution and must be escalated.

## Required Librarian closeout

After the controlled merge, the Historian / Librarian must:

1. verify the exact merged executable and decision ancestry;
2. reconcile the changelog, roadmap, README, ADR index, handbook, release naming, and
   coordination pages against the approved sequence;
3. address or explicitly track the findings in the
   [Repository Health and Documentation Drift Report](../librarian/2026-07-27-repository-health-and-drift-report.md);
4. ensure the latest effective handoff revision is visible at the top-level routing entry;
5. produce `07-librarian-to-product-owner-repository-closeout.md`; and
6. recommend whether the repository is ready for final push/tag/release.

The Librarian does not change product scope, architecture, or executable behavior.

## Exit statement

**APPROVED FOR CONTROLLED MERGE.** Final push, tag, and release remain gated by post-merge
verification and the required Librarian closeout.
