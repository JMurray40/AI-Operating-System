# Handoff 36 — CTO Consolidated QA Remediation Authorization

**From:** Chief Architect / CTO  
**To:** Chief of Staff; Principal Engineer  
**Date:** 2026-07-30  
**Scope:** One bounded remediation cycle for QF-01, QF-02, and QF-03  
**Disposition:** **AUTHORIZED — ONE CONSOLIDATED FROZEN REMEDIATION**

## 1. Authoritative inputs

This authorization is based on:

- `04-quality-to-product-owner-release-review.md`;
- Handoff 34, `34-chief-of-staff-to-product-owner-and-cto-qa-remediation-proposal.md`;
- Handoff 35, `35-product-owner-a11-metric-and-qa-remediation-decision.md`; and
- the exact technical identities and limitations accepted in Handoff 32.

Quality disposition remains `Not ready` at commit:

`aa8d5a76404359f1f43108b2abde47d3d8527aac`

## 2. Frozen identities

The remediation must preserve:

| Item | Frozen identity |
|---|---|
| Executable commit | `ff402d7f82c061426a5e960f7177d916c355bbf2` |
| Executable tree | `a7ff2c023b0e59df1f8bbc2ad05a3af843a5e344` |
| Accepted wheel | `jarvis_core-0.1.0-py3-none-any.whl` |
| Accepted wheel SHA-256 | `8dcc1378a1ac4c3b96dbfea94c0443e92ffaec54fafeb1db5aa73e449a768cd3` |
| Accepted wheel size | 126,683 bytes |
| Runtime payload | 68 `jarvis_core` files |
| Existing A10 evidence commit | `61734825be2cf096608ade0fd6eefc2c731ede68` |
| Existing private A10 manifest SHA-256 | `7aa4402fd960198bed343969aa38ef0eb25b0dc7c4b70fa43e796c92ff218e1b` |
| Existing A12 public evidence SHA-256 | `42cf72981537a41cf84a38c381b321d58a78bc2c80770fc72d0150b0341e2fb9` |
| PyYAML wheel SHA-256 | `4a2e8cebe2ff6ab7d1050ecd59c25d4c8bd7e6f400f5f82b96557ac0abafd0ac` |

The returned remediation commit will be a documentation/evidence/evaluation-tool
descendant of `6173482`. It is not a new packaged-runtime identity. No change to `src/`,
packaging metadata, the accepted wheel, Project Resume runtime behavior, ADRs, pilots,
classifications, or local-Git architecture is authorized.

## 3. One-cycle rule

Engineering is authorized to perform QF-01, QF-02, and QF-03 together, run one complete
regression gate, create one exact remediation commit, and stop.

Engineering must not return findings piecemeal or begin a second correction. If any matrix
row cannot be satisfied without expanding scope, stop the entire cycle and return one
consolidated blocker report without committing a partial pass.

## 4. QF-01 — synthetic raw-evidence correction

### 4.1 Authorized execution

Rerun only the frozen synthetic Project Resume scale protocol against exact executable
`ff402d7`:

- note counts: 100, 500, 1,000, and 5,000;
- deterministic frozen linked-chain generator;
- repository activity disabled;
- explicit frozen evaluation time;
- one warm-up per size;
- 30 measured attempts per size;
- candidate-native `select_ms`, `discover_ms`, and `bind_ms`;
- full assemble `total_ms`;
- released nearest-index estimator, with p50 as median; and
- the frozen peak-memory procedure at 5,000 notes.

No pilot command, pilot benchmark, pilot briefing, pilot doctor, classification operation,
or pilot integrity window may run.

The tracked benchmark harness and executable must not change. A private ignored evidence
driver may invoke the frozen harness functions or faithfully expose their already produced
observations solely to retain evidence. It may not change generator semantics, request
scope, budgets, timing boundaries, warm-ups, run count, percentile estimator, or measured
runtime code.

### 4.2 Required retained observations

Private evidence must retain, without filtering or replacement:

- all 30 `select_ms` observations for each of four sizes;
- all 30 `discover_ms` observations for each size;
- all 30 `bind_ms` observations for each size;
- all 30 `total_ms` observations for each size;
- the exact launched/completed/failure accounting for each size;
- the frozen 5,000-note peak-memory observation and its unit/method;
- environment, interpreter, executable/tree, evaluation time, command/driver identity,
  warm-up, run count, generator identity, estimator, start/completion markers, and any
  failure; and
- SHA-256 and size for every private artifact.

This requires 120 measured attempts and 480 retained timing values, plus the exact
peak-memory observation produced by the frozen memory phase. A failed attempt remains in
the accounting and cannot be silently replaced. If any attempt fails, the evidence
correction does not pass.

### 4.3 Recompute and update boundary

An independently implemented recomputation must derive p50, p95, and p99 for every stage
and size directly from the retained arrays and must reproduce every published aggregate.
It must also confirm sample completeness and the retained 5,000-note memory result.

QF-01 may update only:

- private ignored A10 synthetic raw evidence;
- the private A10 manifest;
- `docs/evidence/v0.4/project-resume-performance-ff402d7.json`; and
- `docs/handovers/v0.4/02-principal-engineer-to-cto-engineering-review.md`.

`pilot-evaluation-ff402d7.json`, pilot raw arrays, pilot aggregates, pilot integrity
evidence, and all A12 evidence remain byte-identical.

The public performance artifact may add the raw synthetic arrays or may bind them through
private-artifact digests while retaining recomputable published derivations. It must remain
privacy-safe and contain no private path, pilot content, or machine credential.

## 5. QF-02 — frozen A11 sourcing metric

### 5.1 Product Owner metric

Engineering must implement exactly:

- `material_claims_reviewed`: non-negative integer count of material claims manually
  reviewed;
- `material_claims_correctly_sourced`: non-negative integer count of reviewed claims whose
  citation supports the claim and binds to the correct current source or repository
  revision;
- `correctly_sourced_rate`:
  `material_claims_correctly_sourced / material_claims_reviewed`;
- zero total reviewed claims produces JSON `null` for the rate and JSON `null` for the
  sourcing-threshold result;
- example and template rows remain excluded;
- `citation_defects` remains a separate diagnostic and never supplies either numerator or
  denominator;
- weekly records identify a claim-sampling procedure and sample size without claim text,
  citation text, private paths, note names, or source content;
- the 90–95% target is reported only after a non-zero reviewed-claim denominator exists;
  the minimum technical threshold is 0.90, and a rate above 0.95 is not treated as a
  failure; and
- the eight-week outcome remains pending until valid Product Owner-approved collection is
  complete.

Dataset/weekly aggregation must use:

```text
sum(material_claims_correctly_sourced)
------------------------------------------------
sum(material_claims_reviewed)
```

It must not average per-row percentages.

### 5.2 Validation rules

For every non-example collected row:

- reviewed and correctly sourced values are required non-negative integers;
- correctly sourced cannot exceed reviewed;
- the sampling-procedure field is required and non-empty;
- the declared sampling size is required, non-negative, and must reconcile with
  `material_claims_reviewed`;
- malformed, negative, inconsistent, or over-numerator rows produce a clear offline
  evaluation error and no threshold claim; and
- zero reviewed claims remain valid evidence of no review, but never a threshold result.

The evaluator must distinguish:

- no collected rows;
- collected rows with a zero reviewed-claim denominator;
- a valid non-zero denominator below 0.90;
- a valid rate from 0.90 through 0.95; and
- a valid rate above 0.95.

### 5.3 Authorized files

QF-02 may change only:

- `evaluations/v0.4-project-resume-dogfood-template.tsv`;
- `scripts/evaluate_project_resume.py`;
- directly required evaluator/smoke tests under `tests/`; and
- documentation sections directly describing A11 collection, sampling, evaluation,
  privacy, thresholds, or pending status.

No `src/`, packaging metadata, ADR, benchmark script, Project Resume runtime test,
acceptance-test meaning, pilot, classification, private baseline, or existing A11 record
may change. No A11 event may be collected.

## 6. QF-03 — release staging and quarantine

### 6.1 Clean candidate-specific staging

Create one candidate-specific release staging directory:

```text
dist/release/ff402d7/
```

It must contain exactly:

1. `jarvis_core-0.1.0-py3-none-any.whl`; and
2. `artifact-identity.json`.

The staged wheel must be copied from the already accepted bound artifact, not rebuilt. It
must have:

- SHA-256 `8dcc1378a1ac4c3b96dbfea94c0443e92ffaec54fafeb1db5aa73e449a768cd3`;
- size 126,683 bytes;
- executable commit `ff402d7f82c061426a5e960f7177d916c355bbf2`; and
- executable tree `a7ff2c023b0e59df1f8bbc2ad05a3af843a5e344`.

`artifact-identity.json` must record schema/version, candidate commit/tree, filename,
size, SHA-256, wheel package/version/tag, source-wheel digest, staging purpose, and an
explicit statement that filename alone is not identity. It must contain no private path,
username, credential, remote, or pilot data.

The staging directory is an out-of-band ignored release-control artifact. It is not
committed.

### 6.2 Quarantine

Every known same-named wheel with SHA-256 other than the accepted digest must be moved
outside `dist/release/ff402d7/` into a clearly labeled non-release quarantine directory.
Quarantined artifacts must retain their bytes and be recorded by prior location category,
filename, size, SHA-256, and quarantine destination category without publishing a private
absolute path.

No superseded wheel may remain in a generic or candidate release-selection directory.
No quarantine directory may be searched as a release input. Quarantine is recoverable;
no wheel is deleted.

After staging/quarantine:

- recursive enumeration across the designated local v0.4 worktrees must find exactly one
  non-quarantined release-eligible wheel with the accepted filename;
- that wheel must be the staged `8dcc…cd3` artifact;
- any additional same-named wheel must be under an explicitly named quarantine path; and
- installation/publication instructions must select by staging path, size, and SHA-256,
  never filename alone.

## 7. Packaged-runtime and A12 preservation proof

Because QF-02 is outside packaged runtime paths, Engineering must prove:

1. the accepted wheel still rehashes to `8dcc…cd3`;
2. its inventory remains exactly 74 entries: 68 `jarvis_core` runtime payloads and six
   distribution metadata entries;
3. all 68 runtime payload files remain byte-identical to
   `ff402d7:src/jarvis_core/*`;
4. all six distribution metadata entries remain byte-identical to the previously accepted
   wheel;
5. package/version, Python requirement, sole `PyYAML>=6.0` dependency, console entry point,
   and wheel tags are unchanged;
6. the remediation diff contains no `src/`, build configuration, packaging metadata,
   console-entry, dependency, or candidate-wheel change; and
7. the A12 public artifact and its bound private evidence remain byte-identical.

Engineering may state that the existing wheel and A12 evidence appear applicable, but only
the next exact-commit CTO review may accept that conclusion.

## 8. Complete Engineering regression gate

Run once after all three remediations are complete:

| Gate | Required result |
|---|---|
| Exact identities | Executable/tree/wheel match Section 2; remediation HEAD descends from `6173482` |
| Scope diff | Only QF-01 evidence/handoff, QF-02 template/evaluator/tests/docs, and ignored QF-03 staging/quarantine controls changed |
| Full tests | Zero failures; every skip named and unchanged or newly justified |
| Evaluator tests | Example exclusion; valid weighted aggregation; zero denominator; below target; 0.90/0.95 boundaries; above 0.95; malformed/negative/inconsistent rejection; citation-defect separation |
| Benchmark evidence | 120/120 attempts complete; 480 timing observations retained; peak-memory observation retained; independent aggregates exact |
| Ruff | `ruff check` and `ruff format --check` pass |
| mypy | `mypy src` passes; evaluator typing check passes under the repository’s configured scope |
| Whitespace | `git diff --check` passes |
| Markdown links | All repository-relative Markdown links resolve |
| Wheel digest/size | Exact `8dcc…cd3`, 126,683 bytes |
| Wheel payload | 68/68 runtime files byte-identical |
| Wheel metadata | 6/6 metadata entries byte-identical |
| Staging | Exactly two allowed files; manifest and staged wheel identities reconcile |
| Quarantine | No non-quarantined stale same-named release candidate remains |
| A10 pilots | No rerun; existing pilot evidence and aggregates byte-identical |
| A12 | Public/private identities and evidence byte-identical |
| Runtime/architecture | No `src/`, ADR, local-Git, authorization, citation, budget, CLI runtime, pilot, classification, or private-baseline change |
| Privacy | Public diffs and manifests contain no prohibited private data |
| Worktree | Clean after the exact remediation commit |

The full test total may increase only through directly required QF-02 tests. Existing
failures or skips may not be hidden, deleted, weakened, or reclassified to obtain a pass.

## 9. Required Engineering return

Engineering must create one exact commit and append a clearly marked remediation revision
to:

```text
docs/handovers/v0.4/02-principal-engineer-to-cto-engineering-review.md
```

The return must provide:

- exact branch, parent `6173482`, remediation commit, and diff;
- exact changed-file list separated by QF-01 and QF-02;
- QF-03 staging and quarantine inventory without private absolute paths;
- old and new private-manifest/public-evidence SHA-256 values;
- raw synthetic sample counts and independent recomputation result;
- exact A11 schema, formulas, validation behavior, and test mapping;
- complete regression commands/results/skips;
- wheel inventory and 68/68 plus 6/6 byte-comparison proof;
- proof pilot evidence, A12 evidence, runtime, packaging metadata, ADRs, local-Git,
  classifications, and private baselines are unchanged;
- `git diff --check` and link-validation results;
- residual limitations; and
- one proposed applicability statement for the accepted wheel and A12.

Engineering must freeze the commit and stop. It may not route directly to Quality.

## 10. Required exact-commit CTO review

The remediation returns through Chief-of-Staff validation and one CTO review pinned to the
exact remediation commit.

That review must decide separately:

1. QF-01 evidence completeness and arithmetic;
2. QF-02 conformance to the Product Owner metric and privacy boundary;
3. QF-03 staging/quarantine integrity;
4. complete regression and scope conformance;
5. whether the existing `8dcc…cd3` wheel remains the exact valid runtime artifact;
6. whether existing A12 evidence remains applicable without rerun;
7. whether A10 pilot evidence, local-Git architecture, classification evidence, and
   unaffected QA results remain reusable; and
8. the exact limited Quality revalidation scope.

Quality remains unauthorized until that CTO disposition explicitly activates it.

## 11. Frozen limited Quality revalidation scope

If and only if the exact-commit CTO review accepts the remediation, it may authorize
Quality to revalidate only:

- QF-01, QF-02, and QF-03;
- Area A identity, ancestry, artifact, diff, and scope rows affected by the remediation;
- Area H full regression, evaluator, documentation links, whitespace, wheel identity, and
  staging rows affected by the remediation;
- Area I synthetic raw arithmetic, private-manifest/public-evidence binding, privacy, and
  unchanged pilot evidence;
- Area J metric schema, weighted arithmetic, zero-denominator null behavior, sampling
  metadata, example exclusion, citation-defect separation, privacy, and honest
  strategic-pending status;
- final candidate/tree/wheel/documentation/evidence/remediation/CTO-disposition identities;
- final worktree and canonical/reachable integrity; and
- confirmation that no previously passing unaffected QA area changed.

Quality must not rerun pilots, reopen local-Git architecture, repeat unaffected Areas B–G,
reclassify notes, collect A11 data, or expand into unrelated QA.

Quality must append a clearly marked superseding revision to:

```text
docs/handovers/v0.4/04-quality-to-product-owner-release-review.md
```

That superseding revision must also correct the four existing Markdown whitespace defects
identified in Handoff 34. The entire resulting Markdown diff must pass `git diff --check`.
Quality must end with exactly one disposition: `Ready`, `Ready with conditions`,
`Refactor first`, `Not ready`, or `Re-scope`.

## 12. Closure matrix

| ID | Closed only when |
|---|---|
| QF-01 | Exact frozen synthetic rerun retains all 480 timing values, attempt accounting, and memory observation; independent recomputation matches the updated public artifact; pilots were not rerun |
| QF-02 | Template/evaluator/tests/docs implement the exact approved numerator, denominator, weighted rate, zero-denominator null, validation, sampling metadata, privacy, example exclusion, separate defects, and strategic-pending rules |
| QF-03 | Clean candidate staging contains only the accepted wheel and identity manifest; all stale same-named wheels are recoverably quarantined; release selection is path+size+digest bound |
| Regression | Full tests/static/typing/links/whitespace pass with no runtime, packaging, ADR, pilot, classification, local-Git, or private-baseline change |
| Runtime identity | Accepted wheel rehashes exactly and all 68 runtime plus six metadata entries are byte-identical |
| Governance | Chief of Staff validates; exact-commit CTO accepts; limited Quality revalidation returns a superseding disposition |

Satisfying this matrix closes QF-01, QF-02, and QF-03 without reopening:

- local-Git architecture or CS-01 through CS-22;
- A10 pilot timing, briefing, privacy, or integrity evidence;
- A12 packaging/recovery execution;
- Product Owner pilot selection or sensitivity classifications;
- A1–A9 runtime architecture;
- accepted A10-12/A10-19 limitations; or
- unaffected QA Areas B–G.

## 13. Explicit exclusions and stop conditions

Stop and return a blocker on:

- any need to change `src/`, packaging metadata, the accepted wheel, ADRs, benchmark
  scripts, pilots, classifications, local-Git, authorization, citations, budgets, or
  private baselines;
- any pilot or A12 rerun;
- synthetic protocol drift, missing/replaced observation, failed attempt, or
  non-recomputable result;
- A11 formula, validation, sampling, privacy, or pending-status deviation;
- staged-wheel mismatch, extra release-staging file, deletion of a superseded wheel, or
  ambiguous release-eligible duplicate;
- payload or metadata mismatch;
- private-data disclosure;
- regression failure, unjustified skip, broken link, or whitespace failure; or
- worktree/evidence/candidate identity mismatch.

This authorization does not permit QA, merge, push, tag, release, publication, A11
collection, Product Owner decision changes, pilot/classification changes, unrelated work,
or v0.5.

**Final CTO disposition:** **Authorize exactly one consolidated QF-01/QF-02/QF-03
Engineering remediation cycle under this frozen matrix, followed by Chief-of-Staff
validation and one exact-commit CTO review.**
