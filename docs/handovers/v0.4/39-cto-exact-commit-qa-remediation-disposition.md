# Handoff 39 — CTO Exact-Commit QA Remediation Disposition

**From:** Chief Architect / CTO
**To:** Chief of Staff; independent Quality & Release
**Date:** 2026-07-30
**Scope:** Exact-commit review of consolidated QF-01/QF-02/QF-03 remediation
**Disposition:** **CONFORMANT — LIMITED QUALITY REVALIDATION AUTHORIZED**

## 1. Authoritative inputs

This review applies:

- Handoff 36, `36-cto-consolidated-qa-remediation-authorization.md`;
- Handoff 37, `37-chief-of-staff-to-principal-engineer-consolidated-qa-remediation-activation.md`;
- Handoff 38, `38-chief-of-staff-to-cto-consolidated-remediation-validation.md`; and
- the exact remediation commit and its private ignored staging/evidence controls.

## 2. Exact bound identities

| Item | Accepted identity |
|---|---|
| Remediation commit | `2c0e1204fb47d81fe8c7b873c973dd8c6026201b` |
| Remediation tree | `567adee29e72955febbefd7a9d3e77b7d0a71f67` |
| Remediation parent | `61734825be2cf096608ade0fd6eefc2c731ede68` |
| Branch | `feature/v0.4-project-resume` |
| Frozen executable | `ff402d7f82c061426a5e960f7177d916c355bbf2` |
| Frozen executable tree | `a7ff2c023b0e59df1f8bbc2ad05a3af843a5e344` |
| Accepted wheel | `jarvis_core-0.1.0-py3-none-any.whl` |
| Accepted wheel SHA-256 | `8dcc1378a1ac4c3b96dbfea94c0443e92ffaec54fafeb1db5aa73e449a768cd3` |
| Accepted wheel size | 126,683 bytes |
| Updated performance JSON SHA-256 | `f125771887f2a544ca2cae3e7aa04305e47bffb362f75ffef8b48eae1666b956` |
| Updated private A10 manifest SHA-256 | `e16fef556408cfde4013c253e2940e8fd6fb6650336d079fee91efcc1ba948b9` |
| Private synthetic raw SHA-256 | `ccace5f5623bddede54435e3e8184c720371d4336c390cdec1fceadcc36fa73a` |
| Pilot-evaluation JSON SHA-256 | `d26a66a98b3e9dc40fdc86119d578f27191cacf2c8d93a7a95b3bfe7ec9aef1e` |
| Updated Engineering review SHA-256 | `01c915d307eaded727507be753ff2a3220981387cf15c33ecdf4310df753d98b` |
| A12 public evidence SHA-256 | `42cf72981537a41cf84a38c381b321d58a78bc2c80770fc72d0150b0341e2fb9` |
| Release-staging manifest SHA-256 | `76fc1ca29325aace9b55491e715b262cd9e2108953b32f74731fb922563932ca` |

The Engineering worktree was clean at the exact remediation commit. The tracked diff
contains exactly six authorized paths:

- `docs/evidence/v0.4/project-resume-performance-ff402d7.json`;
- `docs/handovers/v0.4/02-principal-engineer-to-cto-engineering-review.md`;
- `docs/software/PROJECT_RESUME.md`;
- `evaluations/v0.4-project-resume-dogfood-template.tsv`;
- `scripts/evaluate_project_resume.py`; and
- `tests/unit/test_evaluate_project_resume.py`.

No `src/`, packaging metadata, ADR, benchmark script, runtime test, pilot, classification,
local-Git, authorization, citation, budget, or private-baseline path changed.

## 3. QF-01 decision — accepted

**QF-01 is closed for limited Quality revalidation.**

The corrected evidence binds:

- four frozen synthetic sizes: 100, 500, 1,000, and 5,000 notes;
- one warm-up and 30 measured attempts per size;
- 120 launched, 120 completed, and zero failed attempts;
- 30 retained observations for each of `select_ms`, `discover_ms`, `bind_ms`, and
  `total_ms` at each size;
- 480 retained timing observations in total;
- the frozen linked-chain generator and repository-disabled request;
- the frozen evaluation time and candidate-native timing boundaries;
- the released nearest-index estimator with median p50;
- the frozen 5,000-note `tracemalloc.peak` observation of 34.554 MB; and
- the exact private raw artifact and manifest identities in Section 2.

The retained private evidence uses the frozen harness functions and independently
reimplements the released estimator. Per-size published and recomputed percentile
structures are equal, and the updated public artifact binds the retained arrays and
private raw digest.

The independently confirmed total-latency medians are:

| Notes | Total p50 ms |
|---:|---:|
| 100 | 54.246 |
| 500 | 61.711 |
| 1,000 | 87.740 |
| 5,000 | 269.607 |

Publicly serialized timing observations are retained at bounded decimal precision. A
reimplementation that rounds already serialized values at an exact half-unit may differ
from the in-memory frozen-harness aggregate by at most 0.001 ms. Quality must distinguish
that last-decimal serialization effect from a changed sample, estimator, or aggregate.
Sample identity, order, count, private/public digest, and the private published-versus-
recomputed structures must still match exactly. Any discrepancy greater than 0.001 ms,
missing observation, replaced attempt, failed attempt, or estimator change is blocking.

No pilot was rerun. The pilot-evaluation artifact remains byte-identical.

## 4. QF-02 decision — accepted

**QF-02 is closed for limited Quality revalidation.**

The implementation conforms to the Product Owner’s frozen metric:

```text
correctly_sourced_rate =
    sum(material_claims_correctly_sourced)
    / sum(material_claims_reviewed)
```

It does not average row-level rates. The evaluator:

- requires non-negative integer reviewed and correctly sourced counts;
- rejects correctly sourced counts greater than reviewed counts;
- requires a non-empty sampling procedure;
- requires a non-negative sampling size;
- rejects reviewed material claims greater than the declared sample size;
- returns `null` for both rate and threshold when the total reviewed denominator is zero;
- distinguishes no rows, zero denominator, below 0.90, 0.90–0.95, and above 0.95;
- treats a rate above 0.95 as a pass, not a failure;
- excludes `EXAMPLE`, comment, and blank rows;
- keeps `citation_defects` separate from numerator and denominator;
- emits sampling metadata as counts rather than procedure text or source content;
- fails malformed collection rows offline without producing a threshold claim; and
- preserves the eight-week A11 outcome as `PENDING`.

The sampling reconciliation rule `material_claims_reviewed <= sampling_size` is accepted.
The declared sample may contain claims that are not material; the sourcing denominator
contains only the manually reviewed material claims within that sample. This interpretation
implements the Product Owner’s denominator without falsely requiring every sampled claim
to be material.

The template records sampling procedure and size locally. Public evaluator output contains
counts only and does not expose claim text, citation text, procedure text, private paths,
note names, or source content.

Seventeen focused tests cover weighting, all five states, the 0.90 and 0.95 boundaries,
above-target behavior, malformed/negative/inconsistent rejection, missing fields, example
exclusion, diagnostic separation, and sampling-output privacy.

No A11 event was collected. The 90–95% target and eight-week outcomes remain pending and
unproven.

## 5. QF-03 decision — accepted

**QF-03 is closed for limited Quality revalidation.**

The ignored release-staging directory:

```text
dist/release/ff402d7/
```

contains exactly:

1. `jarvis_core-0.1.0-py3-none-any.whl`; and
2. `artifact-identity.json`.

The staged wheel independently rehashes to `8dcc…cd3` and is 126,683 bytes. The manifest
binds the staging path, filename, size, full digest, executable commit/tree,
package/version/tag, source-wheel digest, and the rule that filename alone is not
identity.

Recursive same-named-wheel inspection found:

- exactly one non-quarantined release-eligible wheel: the accepted staged artifact; and
- two recoverably retained superseded wheels, each 124,678 bytes with SHA-256
  `7253e0b938433d7e393d186a3006c971b576381f6518fe986154d162fe0b3662`,
  under explicitly named quarantine categories.

No wheel was deleted. Quarantine is outside release selection.

## 6. Executable, wheel, and A12 applicability

The accepted executable remains:

`ff402d7f82c061426a5e960f7177d916c355bbf2`

The remediation commit is an evidence/evaluation-tool/documentation descendant, not a new
packaged-runtime candidate.

The accepted wheel remains applicable without rebuild because:

- its whole-file digest and size are exact;
- its inventory remains 74 entries;
- all 68 `jarvis_core` payload files remain byte-identical to the frozen executable tree;
- all six distribution metadata entries remain byte-identical;
- package/version, Python requirement, sole `PyYAML>=6.0` runtime dependency, console
  entry point, and wheel tag are unchanged; and
- no packaged-runtime or packaging-metadata path changed.

The existing A12 evidence remains applicable without rerun. Its public artifact rehashes
exactly, its tested wheel is byte-identical to the staged release wheel, and QF-02 changes
only the offline, non-packaged evaluation mechanism and directly affected documentation/
tests.

**Accepted runtime identity remains wheel SHA-256
`8dcc1378a1ac4c3b96dbfea94c0443e92ffaec54fafeb1db5aa73e449a768cd3`.**

## 7. Reuse of unaffected evidence

The following remains accepted and reusable without rerun:

- all A10 pilot commands, raw arrays, aggregates, privacy, canonical-byte, and
  canonical/reachable Git integrity evidence;
- Handoffs 24/25 local-Git architecture and independent-identity evidence;
- CS-01 through CS-22;
- Product Owner pilot selection and sensitivity-classification decisions;
- accepted pre-edit, apply, and post-classification evidence digests;
- the accepted post-classification baseline and Handoff 06 Git boundary;
- A1–A9 runtime architecture and evidence;
- accepted A10-12 and A10-19 limitation dispositions;
- Handoffs 27/28 A12 packaging/recovery evidence;
- Quality Areas B–G and their justified skips;
- unaffected portions of Quality Areas A, H, I, and J; and
- privacy, no-provider, no-network, no-telemetry, no-remote, and read-only evidence.

No pilot, A12, local-Git, classification, or unaffected QA execution is authorized or
required.

## 8. Formatting-matrix governance correction

Handoff 36’s repository-wide `ruff format --check` row is superseded only as follows:

> `ruff format --check` must pass for every Python file changed by remediation commit
> `2c0e1204fb47d81fe8c7b873c973dd8c6026201b`.

The changed Python files are:

- `scripts/evaluate_project_resume.py`; and
- `tests/unit/test_evaluate_project_resume.py`.

Both pass the scoped formatting check. Repository-wide Ruff 0.16.0 reports that 108 of
152 pre-existing Python files would be reformatted. That pre-existing formatting debt is
recorded as non-blocking and may be addressed only through a separately authorized
maintenance change.

No repository-wide formatting pass or unrelated mechanical edit is authorized. All other
Handoff 36 regression rows remain unchanged, including repository-wide `ruff check`,
tests, mypy, whitespace, links, privacy, scope, runtime identity, and clean-state gates.

## 9. Regression and scope disposition

The complete Engineering gate is accepted for limited Quality revalidation:

- 421 tests passed;
- two named, unchanged skips remain independently covered or environment-justified;
- `ruff check` passed for `src`, `tests`, and `scripts`;
- the two changed Python files passed `ruff format --check`;
- mypy passed for 67 source files and the evaluator;
- `git diff --check` passed;
- changed-document relative links resolved;
- public privacy scan passed;
- all 68 runtime payload and six metadata comparisons passed;
- pilot and A12 evidence remained byte-identical; and
- the Engineering worktree remained clean at exact commit `2c0e120`.

No unresolved remediation-scope, architecture, runtime, packaging, security, privacy, or
integrity deviation blocks limited Quality revalidation.

## 10. Limited Quality revalidation authorization

Quality is authorized only to revalidate:

1. **QF-01:** 120/120 attempt accounting, all 480 retained timings, memory observation,
   frozen protocol identity, raw/private/public hashes, percentile arithmetic, privacy,
   and unchanged pilot evidence;
2. **QF-02:** exact schema, weighted sum-over-sum arithmetic, zero-denominator nulls,
   validation failures, sampling reconciliation, sampling-output privacy, example
   exclusion, citation-defect separation, and honest A11 pending status;
3. **QF-03:** staged directory contents, staged wheel size/digest, identity manifest,
   exactly one release-eligible wheel, recoverable quarantine, and path+size+digest
   selection;
4. affected **Area A** identity, ancestry, diff, artifact, and scope rows;
5. affected **Area H** full regression, evaluator tests, changed-document links,
   whitespace, scoped formatting, wheel identity, staging, and unchanged packaging/A12
   rows;
6. affected **Area I** synthetic arithmetic and sample completeness, manifest/public
   binding, privacy, and proof pilot evidence was not rerun or changed;
7. affected **Area J** metric states, validation, sampling metadata, privacy, example
   exclusion, diagnostic separation, and strategic-pending status;
8. final executable/tree/wheel/remediation/evidence/CTO-disposition identities;
9. final worktree, public evidence, staging, quarantine, canonical, and reachable
   integrity; and
10. confirmation by diff/evidence identity that no previously passing unaffected QA area
    changed.

Quality must not:

- rerun pilots or A12;
- reopen local-Git architecture or CS-01 through CS-22;
- repeat unaffected Areas B–G;
- modify executable, evidence, evaluator, tests, documentation, wheel, staging identity,
  pilots, classifications, or private baselines;
- collect A11 data; or
- expand into unrelated QA.

## 11. Required superseding Quality revision

Quality must append a clearly marked superseding revision to:

```text
docs/handovers/v0.4/04-quality-to-product-owner-release-review.md
```

The superseding revision must:

- bind all Section 2 identities and the committed identity of this CTO disposition;
- decide QF-01, QF-02, and QF-03 separately;
- report only the limited affected Areas A, H, I, and J;
- identify every command, result, skip, limitation, private-evidence boundary, and digest;
- preserve the original review history while superseding its `Not ready` disposition;
- correct the four existing Markdown whitespace defects identified in Handoff 34;
- pass `git diff --check` for the complete resulting Markdown change;
- state that repository-wide formatting debt is pre-existing and outside this release
  remediation;
- state whether the exact technical candidate is ready for Product Owner release
  decision while A11 strategic outcomes remain pending; and
- end with exactly one disposition: `Ready`, `Ready with conditions`, `Refactor first`,
  `Not ready`, or `Re-scope`.

## 12. Quality stop conditions

Quality must stop and return a blocking disposition on any:

- identity, ancestry, digest, size, manifest, or worktree mismatch;
- missing/replaced synthetic observation, failed attempt, protocol drift, arithmetic
  discrepancy beyond the bounded 0.001 ms serialization effect, or privacy leak;
- A11 formula, weighted aggregation, zero-denominator, validation, reconciliation,
  sampling, example-exclusion, diagnostic-separation, privacy, or pending-status defect;
- extra release-staging item, staged-wheel mismatch, non-quarantined stale wheel,
  unrecoverable quarantine, or filename-only selection;
- runtime payload, distribution metadata, packaging, wheel, pilot evidence, or A12
  evidence change;
- regression failure, changed or unjustified skip, changed-file formatting failure,
  whitespace failure, or broken changed-document link;
- candidate, pilot, classification, canonical, reachable-Git, or private-baseline
  mutation; or
- evidence that an unaffected QA area changed.

Quality may not grant a waiver. A blocking result returns through governance.

## 13. Final gate state

- QF-01: **accepted for limited Quality revalidation**.
- QF-02: **accepted for limited Quality revalidation**.
- QF-03: **accepted for limited Quality revalidation**.
- Executable `ff402d7`: **unchanged and still accepted**.
- Wheel `8dcc…cd3`: **unchanged and still accepted**.
- Existing A12 evidence: **still applicable; no rerun required**.
- Unaffected pilot/local-Git/classification/QA evidence: **reusable**.
- Quality: **authorized only for Section 10**.
- Merge, push, tag, release, publication, A11 collection, pilot/classification changes,
  unrelated work, and v0.5: **not authorized**.

**Final CTO disposition:** **Consolidated remediation commit
`2c0e1204fb47d81fe8c7b873c973dd8c6026201b` conforms. Proceed only with the limited
Quality revalidation and superseding revision defined above.**
