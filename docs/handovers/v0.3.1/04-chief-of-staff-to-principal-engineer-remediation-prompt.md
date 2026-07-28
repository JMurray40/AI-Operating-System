# Chief of Staff Remediation Prompt — v0.3.1

| Field | Value |
|---|---|
| Role | Principal Engineer / Claude |
| Milestone | v0.3.1 — Query Trust Contracts |
| Trigger | CTO architecture disposition: Refactor first |
| Reviewed implementation | `62f2269245890b3f55925056c93e156c179d4b5b` |
| Required branch | `feature/v0.3.1-query-trust-contracts` |
| QA status | Blocked |
| Required output | Superseding Engineering Review at `docs/handovers/v0.3.1/03-principal-engineer-to-cto-engineering-review.md` |

## Objective

Correct only the blocking findings in the
[CTO architecture disposition](04-cto-to-quality-architecture-disposition.md), produce
equivalent performance evidence, and return the correction diff to the CTO for re-review.

Primary question:

> Can the accepted trust contracts be built correctly without expanding scope?

## Required corrections

### AC-01 — Explicit authorization scope

- Remove implicit `local_allow_all()` fallback from the v0.3.1 engine boundary.
- Require a non-null `AuthorizationScope`.
- Update every supported caller and test to construct scope explicitly.
- Add a regression test proving omitted/null scope is rejected.
- Keep `local_allow_all` only as an explicit factory.

### AC-02 — Path-boundary-safe authorization

- Canonicalize and validate allowed relative-path prefixes during scope construction.
- Reject empty/ambiguous, absolute, and parent-traversal prefixes.
- Match an exact path or descendant by complete path segments, never raw string prefix.
- Define case behavior consistently with repository identity rules.
- Test sibling-prefix collisions, near matches, slash variants, `..`, absolute paths, and
  empty prefixes.

### AC-03 — Claim-supporting citation binding

- Validate the complete heading hierarchy at the cited locator.
- Verify section bounds and that the locator remains inside the cited section.
- Select support corresponding to the actual retrieval signal, including metadata,
  frontmatter, title, alias, and filename matches.
- Decline to emit a material citation when no supporting passage exists.
- Reject empty supporting excerpts.
- Validate every constructed citation before emission.
- Add all negative and boundary cases required by AC-03.
- Preserve the additive parser approach; do not alter canonical Markdown parsing semantics.

If metadata evidence cannot be represented without changing an accepted citation or parser
contract, stop and escalate to the CTO before proceeding.

### AC-04 — Narrow compatibility reader

- Accept only documented legacy result/citation shapes.
- Reject conflicting old/new fields, or verify equality while always removing the old key.
- Validate legacy ranking value type and range.
- Never map retrieval ranking to `answer_confidence`.
- Add malformed, both-key, conflicting-key, wrong-type, and nested-shape tests.
- Preserve the one-release removal boundary.

### AE-01 — Equivalent benchmark evidence

- Measure v0.3 and candidate total-pipeline p95 using equivalent fixtures, queries,
  end-to-end boundaries, warm-up policy, environment, and percentile method.
- Use at least 10 measured runs; use more if practical so p95/p99 are meaningful.
- Report raw samples or a reproducible raw summary, p50/p95/p99, exact commands, and the
  regression calculation.
- Keep diagnostic stage timings separate from the release gate.
- Do not weaken authorization or citation validation to meet the performance gate.

## Required clarification

Document how duplicate explicit IDs are handled across:

- workspace-level validation; and
- request-scoped query disclosure.

Duplicate IDs must remain validation failures without allowing excluded sources to leak
through request-visible errors.

## Constraints

All original exclusions remain in force. Do not begin QA, merge, push, rewrite accepted
ADRs, touch the parked conversation worktree, or add unrelated refactors.

Preserve the existing four milestone commits. Add logical remediation commits on top of
the current handoff/review state.

## Evidence and handoff

Rerun and report:

- full tests;
- Ruff;
- mypy;
- `git diff --check`;
- unchanged-vault verification;
- corrected equivalent benchmark;
- targeted adversarial tests for every blocking finding.

Update the Engineering Review in place as a clearly marked superseding revision. Include:

- exact prior reviewed SHA;
- exact corrected HEAD and correction diff;
- AC-01 through AC-04 requirement-to-test mapping;
- AE-01 raw/reproducible benchmark evidence;
- duplicate-ID clarification;
- commands and complete results;
- deviations, debt, and unresolved defects;
- confirmation that excluded scope was not imported and the branch was not merged/pushed.

Stop after producing the revised Engineering Review. The CTO must re-review before QA.

## Exit statement

**Ready for bounded Principal Engineer remediation.** QA remains blocked.
