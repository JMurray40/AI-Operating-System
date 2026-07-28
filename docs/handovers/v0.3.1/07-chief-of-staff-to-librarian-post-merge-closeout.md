# Chief of Staff to Historian / Librarian — Post-Merge Closeout Prompt

| Field | Value |
|---|---|
| Sender | Chief of Staff |
| Receiver | Historian / Librarian |
| Milestone | v0.3.1 — Query Trust Contracts |
| Date | 2026-07-27 |
| Status | Authorized for post-merge documentation closeout |
| Worktree | `C:\Users\jmurr\Projects\AI-Operating-System\.worktrees\v0.3.1-release` |
| Branch | `main` |
| Merge commit | `00f181312b92cc59f20407fec6db1d1a3da09ec0` |
| Executable candidate | `956c2ed1dd1144e836014b049a89c47e971818a0` |
| Evidence commit | `8fa5f18c09de1a0c9a79f33e0ba987f9de0e1083` |
| Product Owner decision | `e54bcd9b99bf6baf09bb91e5e0bb97337934357e` |

## Role and primary question

Act as Historian / Librarian. Determine whether the merged repository record is coherent,
current, navigable, and ready for final push, tag, and release.

Do not rely on conversation history. Begin with [Project Control](../../coordination/README.md),
the [v0.3.1 Handoff Index](README.md), and the
[Product Owner Release Decision](06-product-owner-to-librarian-release-decision.md).

## Startup verification

1. Verify the worktree is on `main`, initially clean, and at or descended only by
   documentation-closeout commits from merge `00f1813`.
2. Verify `00f1813` has parents `ce0dc35` and `e54bcd9`.
3. Verify executable `956c2ed`, evidence `8fa5f18`, and Product Owner decision `e54bcd9`
   are ancestors.
4. Verify no executable, test, benchmark-protocol, evidence, or accepted gate-rule changes
   occurred after `956c2ed`.
5. Verify the retained evidence SHA-256 remains
   `f8a67162b74125454f2a5199e6b46a33952763fff18821b7c81497819ffa18d6`.
6. Confirm the parked conversation worktree was not merged or modified.

## Required reconciliation

Use the
[Repository Health and Documentation Drift Report](../librarian/2026-07-27-repository-health-and-drift-report.md)
as the findings backlog. Reconcile, at minimum:

- top-level README and contributor reading order;
- changelog and v0.3.1 release status;
- roadmap sequence: v0.3 Query Engine, v0.3.1 Trust Contracts, v0.4 Project Resume, and
  v0.5 visible-context conversation;
- ADR index coverage for accepted ADR-0014 through ADR-0017;
- Operating Handbook and current coordination pointers;
- release naming across product, software, review, and handoff documentation;
- latest-effective-revision visibility for cumulative CTO and QA handoffs;
- broken or stale local links in the merged repository; and
- the state of the validated, still-blocked v0.4 Project Resume planning package.

Make only documentation, index, changelog, roadmap, and cross-reference corrections.
Preserve historical evidence and superseded revisions; mark history rather than deleting
it.

## Controls and exclusions

Do not change source, tests, scripts, evidence JSON, requirements, accepted ADR substance,
product scope, architecture, or benchmark rules. Do not touch the parked conversation
worktree. Do not begin v0.4 implementation. Do not push, tag, publish, or announce a
release.

If reconciliation would require changing product scope, accepted architecture, or release
semantics, stop and return the conflict to the Product Owner and CTO.

## Verification and required output

Validate all changed Markdown links and run `git diff --check`. Confirm that the final diff
contains documentation-only changes.

Create:

```text
docs/handovers/v0.3.1/07-librarian-to-product-owner-repository-closeout.md
```

The closeout must contain:

1. exact merged and closeout commit identities;
2. files reconciled and drift findings closed, deferred, or escalated;
3. link-validation and documentation-diff evidence;
4. confirmation that executable/evidence identities remain unchanged;
5. remaining documentation debt with owners;
6. an explicit recommendation of `Ready for final release`, `Ready with conditions`, or
   `Not ready`; and
7. a statement that no push, tag, or release occurred.

Stop after committing the documentation-only closeout package on local `main`. Final push,
tag, and release remain Product Owner-controlled.

## Exit statement

**READY FOR HISTORIAN / LIBRARIAN POST-MERGE CLOSEOUT.**
