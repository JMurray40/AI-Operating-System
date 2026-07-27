# Chief of Staff Remediation Prompt — Rev 2

| Field | Value |
|---|---|
| Role | Principal Engineer / Claude |
| Milestone | v0.3.1 — Query Trust Contracts |
| Trigger | Superseding CTO Revision 2: Refactor first |
| Returned implementation | `91636228e72f14c15fbc07c1733da00b8647f27f` |
| Required branch | `feature/v0.3.1-query-trust-contracts` |
| QA status | Blocked |
| Required output | Rev 3 in `03-principal-engineer-to-cto-engineering-review.md` |

## Objective

Correct only AC-03R2, AC-04R2, and AE-01R2 from the superseding CTO disposition.
AC-01, AC-02, and the duplicate-ID design are closed and must not be reopened.

## AC-03R2 — Current exact-byte validation

- Before citation emission, validate the stored fingerprint against current exact source
  bytes as well as locator, complete heading hierarchy, and excerpt.
- Keep reads confined to the configured source root and reject relative-path escape.
- Never emit a stale citation as valid.
- Test discovery followed by byte mutation before query/citation construction.
- Preserve exact CRLF/LF behavior and test a non-normalized byte change.

If the current repository abstraction cannot safely provide current bytes without changing
an accepted architecture contract, stop and escalate to the CTO.

## AC-03R2 — Claim-specific unranked citations

- Provide actual evidence for project summarization values and relationship explanations,
  including frontmatter fields and source link passages.
- When no supporting passage exists, omit the material claim or explicitly mark citation
  coverage incomplete; never attach arbitrary first content.
- Test unrelated first-body content with the actual status/link evidence later or only in
  frontmatter.
- Demonstrate that every emitted deterministic material citation supports its adjacent
  claim. Semantic entailment for future generated answers remains excluded.

## AC-04R2 — Exact legacy shapes

- Define exact allowed and required key sets for legacy v0.3 result and citation payloads.
- Reject unknown keys, missing required fields, and result/citation shape confusion.
- Reject new-only payloads at the legacy boundary or route them through an explicitly
  separate current reader.
- Validate every relevance value and every nested citation.
- Add all adversarial shape tests required by the CTO revision.
- Preserve the one-release removal target; do not build a broad compatibility framework.

## AE-01R2 — Accepted total-pipeline benchmark

- Use the same pre-parsed synthetic note set and equivalent fixture for both versions.
- For every sample, time engine construction plus one public query so authorization,
  index, and graph construction are included.
- Use identical query, runs, warm-up, percentile estimator, hardware, Python, and fixtures.
- Report p50/p95/p99, raw samples or reproducible summary, exact commands, and exact p95
  regression.
- Preserve the prebuilt-engine benchmark only as a steady-state diagnostic.
- Demonstrate candidate p95 is no more than 20% above equivalent v0.3 p95.

## Evidence and exit

Append a clearly marked **Rev 3** to the Engineering Review with:

- correction diff from `91636228e72f14c15fbc07c1733da00b8647f27f`;
- exact tests mapped to each remaining blocker;
- full tests, Ruff, mypy, `git diff --check`, unchanged-vault, and benchmark results;
- exact corrected HEAD;
- scope/exclusion confirmation and unresolved defects.

Do not modify closed findings, begin QA, merge, push, touch the parked conversation worktree,
or expand scope. Stop for another CTO conformance review.

## Exit statement

**Ready for narrowly bounded Rev 3 remediation.** QA remains blocked.
