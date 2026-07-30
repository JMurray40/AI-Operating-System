# Handoff 02 — Principal Engineer to CTO: v0.4 Engineering Review (A10 bound)

**Date:** 2026-07-29
**From:** Principal Engineer
**To:** CTO; Chief of Staff (validation first)
**Disposition:** **A10 EXECUTED AND FROZEN — returned for Chief-of-Staff validation, then CTO architecture/evidence review**
**Authority:** Handoff 28 (A12 acceptance + A10 activation), Handoff 29 (A10 execution activation)

## 1. Bound identities

| Item | Identity |
|---|---|
| Executable | `ff402d7f82c061426a5e960f7177d916c355bbf2` |
| Executable tree | `a7ff2c023b0e59df1f8bbc2ad05a3af843a5e344` |
| Branch | `feature/v0.4-project-resume` |
| Wheel (A10 execution identity) | `jarvis_core-0.1.0-py3-none-any.whl`, SHA-256 `8dcc1378a1ac4c3b96dbfea94c0443e92ffaec54fafeb1db5aa73e449a768cd3` |
| PyYAML runtime dep | 6.0.3, SHA-256 `4a2e8cebe2ff6ab7d1050ecd59c25d4c8bd7e6f400f5f82b96557ac0abafd0ac` |

The bound executable independently resolves to the bound tree; the candidate wheel rehashes to the bound SHA-256. The superseded `014076c` wheel was neither reused nor cited as evidence for this candidate.

## 2. Committed evidence artifacts

| Path | Size (bytes) | SHA-256 (committed blob) |
|---|---:|---|
| `docs/evidence/v0.4/project-resume-performance-ff402d7.json` | 15,280 | `dc16254ab231560be851cce0714af2e4fd99a16f9d9370e484f672df73a7dad8` |
| `docs/evidence/v0.4/pilot-evaluation-ff402d7.json` | 8,474 | `d26a66a98b3e9dc40fdc86119d578f27191cacf2c8d93a7a95b3bfe7ec9aef1e` |

Identities are the exact committed blob bytes, computed binary-safe via `git cat-file blob <commit>:<path>`. Under Handoff 30 the pilot-evaluation artifact was corrected to remove per-mode policy metadata; the performance JSON is unchanged from parent `65264af`.

Private raw evidence, the redacted-field manifest, the measured runner, the artifact generator, per-mode representative briefings, and the synthetic capture live only under `data/v0.4-evidence/ff402d7/a10/` (gitignored). The manifest (`a10-manifest.json`) binds every private artifact by filename, size, and SHA-256, and contains no pilot or candidate copy.

## 3. Execution identity and method

A10 used one execution identity per reported mode: the installed candidate wheel (`8dcc…`) driven as the installed command for pilot timing/counts, and the same installed wheel's library API for in-process peak memory. Synthetic scale used the exact clean source checkout at `ff402d7` (worktree verified clean). No execution identities were mixed within a reported mode. The candidate, tests, tracked scripts, benchmark protocol, pilots, and classifications were not modified; measurement was performed by a private evidence runner and generator under the private evidence directory (the established A12 pattern).

## 4. Reference profile (A10-02, actual current-PC conditions; no equivalence claim)

Windows 11 (10.0.26200); Intel64 Family 6 Model 183 (16 logical CPUs); 31.74 GiB physical memory (4.12 GiB available, 87% load at run time); Python 3.14.4; Git 2.55.0.windows.1. Storage media type and power state were not instrumented and are recorded as such. The run was a dedicated evidence run.

## 5. Predeclared protocol (A10-03)

Declared before measured samples: three warm-ups then thirty measured attempts per warm mode; cold sample recorded separately; released nearest-index percentile estimator (`index = round(q·(n-1))`, `p50 = median`), identical to the frozen `scripts/benchmark_project_resume.py`; installed-CLI wall-clock total plus the candidate's native trace stage timings; complete raw arrays retained. Modes: Survivor Group Tracker denied and exact-grant; AI Prompt Suite explicit no-Git/unavailable.

## 6. Measured pilot results (warm, milliseconds)

| Mode | completed | p50 | p95 | p99 | max | <30 s | repo citations | peak heap (MiB) |
|---|---|---|---|---|---|---|---|---|
| Survivor — denied | 30/30 | 532.482 | 575.008 | 590.165 | 590.165 | yes | 0 | 0.567 |
| Survivor — exact grant | 30/30 | 655.480 | 788.337 | 793.643 | 793.643 | yes | 10 | 0.773 |
| AI Prompt Suite — no-Git | 30/30 | 307.189 | 337.360 | 357.402 | 357.402 | yes | 0 | 0.731 |

Every valid warm pilot total is far below the 30-second gate (max 793.643 ms). Independent percentile recomputation from the retained raw arrays equals the reported values. All three pilots produced valid `partial`-coverage briefings (produced sections and citations); none returned `not_found`. Denied mode yields no repository citations and no Git-derived claim; exact-grant yields ten snapshot/object-bound repository citations; the non-Git pilot degrades explicitly with zero repository citations.

Instrumented stages (native trace): selection, discovery (retrieval), citation binding, and repository, plus measured total. The exact-grant repository stage dominates (~150 ms) and is absent in the no-Git mode, as expected.

## 7. Synthetic scale (A10-19)

Deterministic synthetic vaults via the frozen harness at 100 / 500 / 1,000 / 5,000 notes (30 runs + warm-up each): total p50 46.5 / 62.7 / 85.3 / 269.5 ms; 5,000-note p99 316.9 ms; peak memory 34.554 MB at 5,000 notes. All sizes terminate well within budget with retained timing and counts. High fan-out and cycles are not generated by the frozen harness; see limitations.

## 8. Integrity (A10-21/22/23/24) — before/after, exact

Survivor Group Tracker (Git-enabled): canonical worktree manifest, HEAD, symbolic HEAD, refs, packed-refs, reflogs, index, local config, remotes (count and content digest), porcelain status, reachable-object manifest and count, count-objects, and ACL are all equal before and after; no new unreachable loose objects (`ambient_unreachable_object_drift: none`). AI Prompt Suite: worktree manifest and ACL equal; non-Git before and after. No canonical or reachable mutation occurred.

## 9. Boundary results

No provider, network, telemetry, remote-Git, or credential activity (A10-25). Public artifacts are redacted (A10-26/30): a self-scan confirms no absolute path, pilot passage, private note name, Git subject/author/remote, username, classification, or raw error. Every launched attempt has a recorded outcome; 30/30 completed per mode with no failures (A10-27). The candidate, wheel, tests, scripts, benchmark protocol, pilots, and classifications are unmodified (A10-29).

## 10. A10-01 through A10-30 disposition

Pass: A10-01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 13, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30. Explicit **unavailable** (raised for governance, not worked around): **A10-12** — the frozen candidate natively instruments selection/discovery/binding/repository + total, but authorization, identity, graph, authority-conflict, and rendering are not separately instrumented and cannot be measured without changing the frozen candidate; **A10-19** — scale points pass, but high fan-out and cycles are not produced by the frozen benchmark harness and cannot be added without modifying it. Per-row evidence is in `pilot-evaluation-ff402d7.json` (`a10_matrix`).

## 11. Reused prior evidence (Handoff 28 §10, cited by identity)

Architecture clearance and CS-01…CS-22 for `ff402d7` (Handoff 25); independent Windows-identity CS-21 (Handoff 24); exact-candidate A12 acceptance and evidence (Handoff 28 §§2–5; `docs/evidence/v0.4/a12-ff402d7-packaging-recovery.md`); Product Owner pilot substitution and classification approvals; accepted pre-edit/apply/post-classification evidence digests and the post-classification canonical/reachable baseline under the Handoff 06 boundary; documentation-only ancestry unchanged by `ff402d7`; the verified retained PyYAML wheel identity; and privacy/no-provider/no-telemetry policy evidence. A1–A9 technical evidence maps to `ff402d7` ancestry, with all local-Git-affected portions replaced by Handoffs 24/25/27 and this A10. The superseded `014076c` wheel/installed-candidate/local-Git/doctor/payload/A12 results and any pre-`ff402d7` A10 timings are not reused.

## 12. Consolidated limitations and blockers

1. **A10-12 extended per-stage instrumentation — unavailable.** Measuring authorization/identity/graph/authority-conflict/rendering as separate stages requires adding instrumentation to the frozen candidate, which is prohibited. Recommend the CTO either accept the instrumented-stage subset for v0.4 or authorize a separately reviewed instrumentation change in a later candidate.
2. **A10-19 high fan-out and cycles — unavailable.** The frozen benchmark harness generates a linked-chain synthetic vault only; fan-out/cycle topologies would require modifying the tracked harness. Recommend accepting the linear scale evidence for v0.4 or authorizing a harness extension separately.
3. **Reference vs current PC.** Per Handoff 28 §6 the current PC is the approved reference profile; actual conditions (including 87% memory load at run time) are disclosed with no equivalence claim. Latencies are hundreds of milliseconds with wide headroom under the 30 s gate, so the conclusion is robust to load.
4. **A11 eight-week dogfood outcome collection remains explicitly pending** and is out of A10 scope.
5. Storage media type and power state were not instrumented (recorded as such).

## 13. Requested routing

Chief of Staff to validate exact candidate, tree, wheel, documentation, evidence digests, protocol completeness, privacy, and worktree scope; then CTO to conduct the final v0.4 architecture/A1–A10/A12 evidence review, resolve the two unavailable rows, and issue an exact-candidate disposition. Quality & Release remains unauthorized until that disposition. A10 evidence is frozen; no QA, merge, push, tag, release, publication, or v0.5 work was performed.

---

## Remediation revision — QF-01 / QF-02 / QF-03 (Handoff 36 / 37)

One consolidated documentation/evidence/evaluation-tool remediation, parent `61734825be2cf096608ade0fd6eefc2c731ede68`, branch `feature/v0.4-project-resume`. No `src/`, packaging metadata, accepted-wheel, ADR, pilot, classification, local-Git, authorization, citation, budget, or private-baseline change.

### Changed files by QF

- **QF-01** (synthetic evidence): `docs/evidence/v0.4/project-resume-performance-ff402d7.json` (only `synthetic_scale`); this handoff revision.
- **QF-02** (A11 metric): `evaluations/v0.4-project-resume-dogfood-template.tsv`, `scripts/evaluate_project_resume.py`, `tests/unit/test_evaluate_project_resume.py`, `docs/software/PROJECT_RESUME.md`.
- **QF-03** (staging/quarantine): out-of-band under ignored `dist/release/ff402d7/` and `dist/quarantine/`; not committed.

### Binary-safe committed identities (`git cat-file blob <commit>:<path>`)

| Path | Size | Old SHA-256 | New SHA-256 |
|---|---:|---|---|
| `project-resume-performance-ff402d7.json` | 26,188 | `dc16254ab231560be851cce0714af2e4fd99a16f9d9370e484f672df73a7dad8` | `f125771887f2a544ca2cae3e7aa04305e47bffb362f75ffef8b48eae1666b956` |
| `pilot-evaluation-ff402d7.json` | 8,474 | `d26a66a98b3e9dc40fdc86119d578f27191cacf2c8d93a7a95b3bfe7ec9aef1e` | unchanged |
| `evaluate_project_resume.py` | 10,455 | — | `ac3e4e2dfedcef4eae7b7bfe2a440ba330a3f27b67b29cc59508858c09b10839` |
| `v0.4-project-resume-dogfood-template.tsv` | 720 | — | `13b0e5a6cf9c4ae383bbb3143aa373714551e32fa254897b8729ca5a594e46b1` |
| `test_evaluate_project_resume.py` | 6,436 | — | `1df2649cb59f186c1ea11f0068be4a6cb7a37ba9f00899192dda141247405eec` |
| `PROJECT_RESUME.md` | 13,185 | — | `49a05fe0a096c2d2a2ff1f7bf5a5365829a8511be84604f94ec7ae62138e96a8` |

Private A10 manifest: old `7aa4402fd960198bed343969aa38ef0eb25b0dc7c4b70fa43e796c92ff218e1b`; new digest bound in the return. A12 public evidence unchanged: `42cf72981537a41cf84a38c381b321d58a78bc2c80770fc72d0150b0341e2fb9`.

### QF-01 synthetic evidence (supersedes Section 7 numbers)

A private ignored driver invoked the frozen harness's own functions (no protocol change) and retained every observation: **120 launched, 120 completed, 0 failed, 480 timing values** (30 × select/discover/bind/total × four sizes), plus the frozen 5,000-note peak memory **34.554 MB** (`tracemalloc`). Independent recomputation of p50/p95/p99 from the retained arrays reproduces every published aggregate (`independent_recompute_ok = true`). New total_ms p50: 100 → 54.246, 500 → 61.711, 1,000 → 87.740, 5,000 → 269.607 ms. The public artifact embeds the raw arrays and binds the private raw file `a10-synthetic-raw.json` (`ccace5f5623bddede54435e3e8184c720371d4336c390cdec1fceadcc36fa73a`, 15,739 bytes). Pilots were not rerun.

### QF-02 A11 sourcing metric

Schema adds `material_claims_reviewed`, `material_claims_correctly_sourced`, `sampling_procedure`, `sampling_size`. Weighted rate (never an average of per-row rates):
`correctly_sourced_rate = sum(material_claims_correctly_sourced) / sum(material_claims_reviewed)`. A zero reviewed-claim denominator yields JSON `null` for the rate and threshold; five states are distinguished (no rows, zero-denominator, below 0.90, 0.90-0.95 band, above 0.95 — not a failure); minimum technical threshold 0.90. `citation_defects` stays a separate diagnostic (never numerator/denominator). Per-row validation rejects malformed, negative, over-numerator, missing-procedure, and reviewed>sampling-size rows with a clear offline error and no threshold claim. Sampling metadata is emitted as counts only (no claim/citation/procedure text). Eight-week outcome remains PENDING. Tests (`test_evaluate_project_resume.py`, 17 cases) map: weighting (`test_weighted_rate_is_sum_over_sum_not_average_of_rates`), five states (`test_no_rows_state`/`test_zero_denominator_state`/`test_below_target_state`/`test_090_boundary_in_band_and_meets`/`test_095_boundary_in_band_and_meets`/`test_above_095_not_a_failure`), rejection (`test_invalid_rows_raise_sourcing_error` ×5, `test_missing_required_field_raises`), defect separation (`test_citation_defects_do_not_affect_sourcing`), privacy (`test_sampling_metadata_is_counts_only_no_text`), example exclusion (`test_examples_and_comments_skipped`), absent-columns (`test_sourcing_absent_columns_is_zero_denominator`).

### QF-03 staging and quarantine (categories only, no private absolute paths)

Staging `dist/release/ff402d7/` contains exactly `jarvis_core-0.1.0-py3-none-any.whl` (SHA-256 `8dcc1378a1ac4c3b96dbfea94c0443e92ffaec54fafeb1db5aa73e449a768cd3`, 126,683 bytes) and `artifact-identity.json` (`76fc1ca29325aace9b55491e715b262cd9e2108953b32f74731fb922563932ca`). Two stale same-named wheels (SHA-256 `7253e0b938433d7e393d186a3006c971b576381f6518fe986154d162fe0b3662`, 124,678 bytes) were recoverably quarantined by prior-location category `engineering-dist-root` and `a12-worktree-root` into `dist/quarantine/from-<category>/`; no wheel was deleted. Recursive enumeration across the v0.4 worktrees finds exactly one non-quarantined release-eligible wheel — the staged accepted artifact. Release selection binds staging path + size + SHA-256, never filename alone.

### Preservation proof (Section 7)

Accepted wheel rehashes to `8dcc…cd3` (126,683 bytes); 74 entries (68 runtime payload + 6 metadata); all 68 payload files byte-identical to `ff402d7:src/jarvis_core/*`; the 6 metadata entries are byte-identical to the accepted wheel (identical wheel bytes). Package `jarvis-core` 0.1.0, `Requires-Python >=3.10`, sole runtime dependency `PyYAML>=6.0`, console entry `jarvis = jarvis_core.cli:main`, tag `py3-none-any` — unchanged. The remediation diff contains no `src/`, build-config, packaging-metadata, entry-point, dependency, or candidate-wheel change. A12 public and pilot A10 evidence are byte-identical.

### Regression gate

Full tests: **421 passed, 2 skipped** — the two skips are the pre-existing symlink integration test (unsupported filesystem) and the CS-21 in-suite placeholder (independent Windows-identity, satisfied by Handoff 24); both named and unchanged. `ruff check src tests scripts`: clean. `mypy` (67 source files) and the evaluator: clean. `git diff --check`: clean. Repository-relative Markdown links in the changed docs resolve.

### Residual limitations

1. **`ruff format --check` (repo-wide) is a pre-existing failure.** This repository has never been ruff-*formatted*: 108 of 152 Python files (all of `src/` and prior CTO-accepted test files) would be reformatted; the repository's active style gate is `ruff check`, which passes. Making `ruff format --check` pass repo-wide requires reformatting `src/`, a Handoff 36 §13 stop condition and out of scope. The remediation's two changed Python files pass `ruff format --check`.
2. The accepted **A10-12** (extended per-stage instrumentation) and **A10-19** (fan-out/cycles) unavailabilities are carried unchanged.

### Proposed applicability statement (for the exact-commit CTO review)

The accepted wheel `8dcc…cd3` and the existing A12 evidence `42cf7298…` appear applicable to executable `ff402d7` (this remediation touches no packaged-runtime path; the wheel rehashes exactly and its 68 payload files are byte-identical to `ff402d7:src`). This is proposed only; per Handoff 36 §7 and §10, only the next exact-commit CTO review may accept it. Freeze; stop for Chief-of-Staff validation. No QA, merge, push, tag, release, publication, A11 collection, or v0.5 work was performed.
