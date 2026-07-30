# Handoff 38 — Chief of Staff to CTO: Consolidated QA Remediation Validation

**From:** Chief of Staff
**To:** Chief Architect / CTO
**Date:** 2026-07-30
**Scope:** Independent validation of QF-01, QF-02, and QF-03 remediation
**Disposition:** **READY FOR EXACT-COMMIT CTO REVIEW — ONE GOVERNANCE MATRIX CORRECTION REQUIRED**

## 1. Exact identities and scope

The validated Engineering return is:

| Item | Identity |
|---|---|
| Remediation commit | `2c0e1204fb47d81fe8c7b873c973dd8c6026201b` |
| Parent | `61734825be2cf096608ade0fd6eefc2c731ede68` |
| Branch | `feature/v0.4-project-resume` |
| Frozen executable | `ff402d7f82c061426a5e960f7177d916c355bbf2` |
| Frozen executable tree | `a7ff2c023b0e59df1f8bbc2ad05a3af843a5e344` |
| Accepted wheel SHA-256 | `8dcc1378a1ac4c3b96dbfea94c0443e92ffaec54fafeb1db5aa73e449a768cd3` |
| Accepted wheel size | 126,683 bytes |

The Engineering worktree was clean at the exact remediation commit. The tracked diff
contains exactly six authorized files:

- `docs/evidence/v0.4/project-resume-performance-ff402d7.json`;
- `docs/handovers/v0.4/02-principal-engineer-to-cto-engineering-review.md`;
- `evaluations/v0.4-project-resume-dogfood-template.tsv`;
- `scripts/evaluate_project_resume.py`;
- `tests/unit/test_evaluate_project_resume.py`; and
- `docs/software/PROJECT_RESUME.md`.

No `src/`, packaging, ADR, benchmark-protocol, pilot, classification, local-Git, or
accepted-wheel file changed. `git diff --check` passes.

## 2. QF-01 — independently validated

The corrected private and public evidence retains:

- 120 launched and 120 completed synthetic attempts with zero failures;
- all 480 timing observations: 30 values for each of `select_ms`, `discover_ms`,
  `bind_ms`, and `total_ms` at 100, 500, 1,000, and 5,000 notes;
- the frozen 5,000-note peak-memory result of 34.554 MiB; and
- the frozen generator, run count, warm-up, estimator, environment, and execution
  identities.

Independent parsing and recomputation confirmed the raw-array counts and every published
aggregate. The recomputed `total_ms` medians are 54.246, 61.711, 87.740, and 269.607 ms
for 100, 500, 1,000, and 5,000 notes respectively.

The updated public performance artifact is 26,188 bytes with SHA-256:

`f125771887f2a544ca2cae3e7aa04305e47bffb362f75ffef8b48eae1666b956`

The updated private A10 manifest is 3,200 bytes with SHA-256:

`e16fef556408cfde4013c253e2940e8fd6fb6650336d079fee91efcc1ba948b9`

All eleven private artifacts bound by that manifest were independently rehashed
successfully. The pilot evidence was not rerun and remains byte-identical at:

`d26a66a98b3e9dc40fdc86119d578f27191cacf2c8d93a7a95b3bfe7ec9aef1e`

**Chief-of-Staff finding:** QF-01 is complete and suitable for CTO acceptance.

## 3. QF-02 — independently validated

The evaluator implements the Product Owner's required weighted metric:

```text
sum(material_claims_correctly_sourced)
------------------------------------------------
sum(material_claims_reviewed)
```

It does not average per-row percentages. It enforces non-negative integer values,
`correctly sourced <= reviewed`, required sampling procedure and sample size, and
`reviewed <= sample size`. This last relationship is the correct reconciliation rule:
the declared sample may contain claims that are not material, while the denominator
contains only reviewed material claims.

The evaluator:

- returns JSON `null` for both the sourcing rate and threshold result when the total
  reviewed-claim denominator is zero;
- distinguishes no rows, zero denominator, below target, 0.90–0.95 target band, and
  above-target states;
- keeps citation defects separate from the numerator and denominator;
- excludes example/template rows;
- emits only counts for sampling metadata; and
- preserves the honest `PENDING` eight-week A11 outcome.

All 17 focused evaluator tests passed independently. Running the evaluator against the
template produced zero collected rows, a null sourcing rate, and a null threshold result.

**Chief-of-Staff finding:** QF-02 is complete and suitable for CTO acceptance.

## 4. QF-03 — independently validated

The ignored candidate-specific staging directory contains exactly:

1. `jarvis_core-0.1.0-py3-none-any.whl`; and
2. `artifact-identity.json`.

The staged wheel rehashes to the accepted SHA-256 and size. The identity manifest is 876
bytes with SHA-256:

`76fc1ca29325aace9b55491e715b262cd9e2108953b32f74731fb922563932ca`

It binds release selection to the staging path, executable commit/tree, byte size, and
digest, and states that filename alone is not identity.

Recursive same-named-wheel enumeration found:

- exactly one non-quarantined release-eligible wheel: the accepted staged artifact; and
- two superseded 124,678-byte wheels, each with SHA-256
  `7253e0b938433d7e393d186a3006c971b576381f6518fe986154d162fe0b3662`,
  retained recoverably under explicitly named quarantine categories.

No stale wheel remains eligible for release selection and no wheel was deleted.

**Chief-of-Staff finding:** QF-03 is complete and suitable for CTO acceptance.

## 5. Packaged-runtime and prior-evidence applicability

The accepted wheel remains 74 entries: 68 `jarvis_core` runtime payloads and six
distribution metadata entries. All 68 runtime payload files are byte-identical to the
frozen executable tree. Because the staged wheel is byte-identical to the already accepted
wheel by whole-file digest, its six metadata entries are necessarily byte-identical as
well.

Package name/version, Python requirement, sole runtime dependency, console entry point,
and wheel tag are unchanged. The remediation changed no packaged-runtime path.

The accepted A12 public evidence remains byte-identical with SHA-256:

`42cf72981537a41cf84a38c381b321d58a78bc2c80770fc72d0150b0341e2fb9`

**Chief-of-Staff recommendation:** accept the existing wheel, A12 evidence, pilot A10
evidence, local-Git architecture findings, and unaffected QA results as applicable without
rerun.

## 6. Regression results and the sole governance correction

Engineering reports:

- 421 tests passed and two named, unchanged skips;
- `ruff check` clean for `src`, `tests`, and `scripts`;
- `mypy` clean for 67 source files and the evaluator;
- changed documentation links valid;
- public privacy scan clean; and
- clean worktree and whitespace validation.

Focused Chief-of-Staff reruns confirmed the 17 evaluator tests and formatting compliance
for the two changed Python files.

Handoff 36 contains one internally contradictory matrix row: it requires repository-wide
`ruff format --check` to pass while also prohibiting the mass formatting needed to make
that pre-existing repository state pass. Independent execution with Ruff 0.16.0 confirms
that 108 of 152 existing files would be reformatted, including previously accepted source
and test files. This is pre-existing formatting debt, not a regression introduced by
`2c0e1204`.

Engineering correctly disclosed the conflict and demonstrated that both changed Python
files pass `ruff format --check`. Returning this work for repository-wide mechanical
formatting would violate the authorized scope, alter unrelated files, and create avoidable
release risk.

**Required CTO governance correction:** supersede only the Handoff 36 repository-wide
format row with:

> `ruff format --check` must pass for Python files changed by the remediation. Existing
> repository-wide formatting debt is recorded as non-blocking and may be addressed in a
> separately authorized maintenance change.

This correction changes no product requirement, security boundary, executable, evidence,
or Quality finding. It resolves an impossible gate without waiving any remediation defect.

## 7. CTO decisions requested

The exact-commit CTO review should decide:

1. accept QF-01 raw synthetic evidence and arithmetic;
2. accept QF-02 metric, validation, sampling reconciliation, privacy, and pending status;
3. accept QF-03 staging and recoverable quarantine;
4. adopt the single formatting-matrix correction in Section 6;
5. accept the frozen wheel and existing A12 evidence without rerun;
6. accept unaffected pilot, local-Git, classification, and QA evidence as reusable; and
7. authorize only the limited Quality revalidation defined in Handoff 36 Section 11.

Quality must append a superseding revision to
`docs/handovers/v0.4/04-quality-to-product-owner-release-review.md` and repair its four
existing Markdown whitespace defects. No pilot, A12, architecture, or unaffected QA area
should be rerun.

## 8. Chief-of-Staff disposition

**The substantive QF-01, QF-02, and QF-03 remediation is validated and ready for the
exact-commit CTO review. The only unresolved item is an internally contradictory formatting
gate, for which the narrowly bounded correction above is recommended.**

No Quality review, merge, push, tag, release, publication, A11 collection, pilot or
classification change, unrelated work, or v0.5 work is authorized by this handoff.
