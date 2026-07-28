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

