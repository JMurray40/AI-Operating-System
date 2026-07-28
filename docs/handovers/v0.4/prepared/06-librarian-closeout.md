# Prepared Prompt — v0.4 Librarian Closeout

**Inactive until:** Product Owner approves the QA-reviewed candidate and it is merged
locally into `main`.

Act as Historian / Librarian. Determine whether the merged v0.4 repository record remains
coherent and ready for final release action.

Verify exact candidate, evidence, Product Owner decision, merge ancestry, unchanged
executable after QA, and clean starting state. Reconcile:

- README, changelog, roadmap, PRD/software/ADR indexes, handbook, and coordination pages;
- Project Resume as v0.4 and visible-context conversation as v0.5;
- latest-effective engineering, CTO, QA, and Product Owner handoffs;
- result/trace/Git-capability/CLI/packaging/recovery/dogfood documentation;
- retained versus private evidence boundaries;
- all Markdown local links and release-state language; and
- deferred A11 strategic validation without representing it as complete.

Preserve historical revisions. Make documentation-only changes. Do not alter source,
tests, scripts, evidence JSON, accepted ADR substance, product scope, or the parked branch.
Do not push, tag, or release.

Produce:

```text
docs/handovers/v0.4/06-librarian-to-product-owner-repository-closeout.md
```

End with `Ready for final release`, `Ready with conditions`, or `Not ready`, and identify
all remaining debt and owners.

## Activation block

```text
local_main_worktree: <ABSOLUTE_PATH>
pre_merge_main: <FULL_SHA>
approved_candidate: <FULL_SHA>
product_owner_decision: <FULL_SHA_OR_ARTIFACT>
merge_commit: <FULL_SHA>
qa_disposition: <FULL_SHA_OR_ARTIFACT>
required_output: docs/handovers/v0.4/06-librarian-to-product-owner-repository-closeout.md
```

Do not start unless the merge is local, clean, exact, and unpushed.

## Required reconciliation ledger

For every changed document record:

- prior claim;
- merged implementation/evidence truth;
- required correction;
- owner/authority;
- changed path;
- link-validation result; and
- closed, deferred, or escalated status.

Check all local Markdown targets and important heading anchors; external links are
separately labeled if not network-validated. Ensure changelog and roadmaps distinguish
technical release from A11 strategic validation. Preserve exact evidence digests and
private-data exclusions.

## Required closeout evidence

The closeout must list merge parents and ancestry, executable/evidence/QA/Product Owner
identities, documentation-only diff, files reconciled, link counts, broken targets,
whitespace result, deferred debt, and confirmation that the parked conversation branch
and v0.5 remained untouched.

Commit only the documentation reconciliation and closeout locally. Do not push, tag,
publish, or begin the next milestone. Return final authority to the Product Owner.
