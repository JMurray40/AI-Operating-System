# v0.4 Quality & Release Review — exact executable `ff402d7`

**From:** Independent Quality & Release Manager  
**To:** Product Owner  
**Date:** 2026-07-30  
**Scope:** Handoff 32 Areas A–J and all stop conditions  
**Review posture:** adversarial, read-only except for this artifact

## 1. Bound identities and review views

| Item | Independently observed identity |
|---|---|
| Detached executable view | `C:\Users\jmurr\Projects\AI-Operating-System\.worktrees\v0.4-qa` |
| Executable commit | `ff402d7f82c061426a5e960f7177d916c355bbf2` |
| Executable tree | `a7ff2c023b0e59df1f8bbc2ad05a3af843a5e344` |
| Candidate wheel | `dist/ff402d7/jarvis_core-0.1.0-py3-none-any.whl` |
| Candidate wheel SHA-256 / size | `8dcc1378a1ac4c3b96dbfea94c0443e92ffaec54fafeb1db5aa73e449a768cd3` / 126,683 bytes |
| User-facing documentation commit | `79a4999a9d8d6f0ff4a6daf47e758e8dbffc85bb` |
| Read-only evidence view | `C:\Users\jmurr\Projects\AI-Operating-System\.worktrees\v0.4-engineering` |
| Evidence commit / parent | `61734825be2cf096608ade0fd6eefc2c731ede68` / `65264af50e375c0bd8e5d1618cfc89b70891df6d` |
| Private A10 manifest SHA-256 | `7aa4402fd960198bed343969aa38ef0eb25b0dc7c4b70fa43e796c92ff218e1b` |
| Performance JSON SHA-256 | `dc16254ab231560be851cce0714af2e4fd99a16f9d9370e484f672df73a7dad8` |
| Pilot-evaluation JSON SHA-256 | `d26a66a98b3e9dc40fdc86119d578f27191cacf2c8d93a7a95b3bfe7ec9aef1e` |
| Engineering review SHA-256 | `b90183051c22c46ef6ff9504c8e3138cfc37de362d5ba9faec2b923e358ee242` |
| A12 public evidence SHA-256 | `42cf72981537a41cf84a38c381b321d58a78bc2c80770fc72d0150b0341e2fb9` |
| PyYAML wheel SHA-256 | `4a2e8cebe2ff6ab7d1050ecd59c25d4c8bd7e6f400f5f82b96557ac0abafd0ac` |
| Coordination/output view starting commit | `420e7a563c208c2765dd61e2b2ed5c2ab9d55e5a` |
| CTO disposition commit | `391453adeda0b29bab83860ceef9e2107c840bd2` |
| Handoff 32 SHA-256 | `31e182dd1477afe2c33667e0071111d0d59d9daa249e15ed571df32179879dd1` |
| Handoff 33 SHA-256 | `a7021cfa397bcf8922b5fd7502ae0f09a72394ffd2ce1bb2204c7644f117b814` |
| QA artifact identity | This path, committed as the sole path delta by the Quality reviewer; the resulting commit is the external Git identity because a commit cannot contain its own hash |

The executable view started detached and clean. The evidence view started clean at the
exact evidence commit. The coordination view started clean. The released v0.3.1 baseline
is an ancestor of the executable. The evidence commit descends from the executable and
changes exactly the two declared public evidence JSON files and Engineering review. The
documentation commit is in the executable ancestry; user-facing documentation has no
later change through the executable or evidence commit.

Environment: Windows 11, PowerShell, CPython 3.14.4, Git 2.55.0. The full candidate gates
used the repository's established environment. Packaging was repeated in a new
reviewer-owned temporary virtual environment and removed after results were recorded.

## 2. Executive result

The executable behavior is technically strong: the complete suite, targeted adversarial
groups, static gates, installed-wheel checks, deterministic reinstall check, and an
independent bounded cyclic/high-fan-out fixture all passed. No candidate or evidence byte
was changed.

Release evidence is nevertheless incomplete against the activated QA contract:

1. retained synthetic benchmark artifacts do not contain the per-run arrays needed to
   recompute the reported 100/500/1,000/5,000-note percentiles; and
2. the A11 mechanism lacks a reviewed-material-claim denominator and therefore cannot
   compute the required 90–95% correctly sourced claim rate.

A same-named stale wheel also exists outside the exact bound artifact directory. It is not
the release input, but it creates an avoidable artifact-selection hazard.

## 3. Area A — identity, ancestry, dependencies, and scope

**Result:** A01–A07 pass, with release finding QF-03.

- `git rev-parse HEAD`, `git rev-parse HEAD^{tree}`, `git symbolic-ref -q HEAD`, and
  `git status --porcelain=v1` confirmed exact detached/clean executable identity and tree.
- `git merge-base --is-ancestor` confirmed released-baseline ancestry, documentation
  ancestry, evidence descent, and CTO-disposition ancestry.
- `git diff --name-status ff402d7..6173482` returned only the two public evidence JSON
  files and Engineering review.
- SHA-256 and size checks matched every bound identity in Section 1.
- ZIP enumeration found 74 entries: 68 runtime payloads and six distribution metadata
  entries. All 68 runtime files were byte-identical to `ff402d7:src/jarvis_core`.
- Metadata independently reported `jarvis-core` 0.1.0, Python `>=3.10`, sole runtime
  dependency `PyYAML>=6.0`, and sole console entry point
  `jarvis = jarvis_core.cli:main`. No provider or build-backend payload was present.
- Static scope review found no Project Resume conversation, provider, network, agent,
  plugin, MCP, automation, live-GitHub, or canonical-write path. The legacy
  `vault-report` write option is outside Project Resume scope.

## 4. Area B — exact selection and safe identity failure

**Result:** B01–B07 pass.

`python -m pytest -q` over the identity and CLI-resume selections produced **20 passed**.
The cases cover canonical ID/title/alias/stem tiers, same-tier ambiguity, tier precedence,
duplicate IDs, not-found behavior, hostile/Unicode/path-like selectors, approved candidate
fields, text/JSON structure, and exit statuses. No fuzzy or related-project substitution
was observed.

## 5. Area C — authorization, sensitivity, and graph confinement

**Result:** C01–C08 pass; one environment-specific symlink case is justified below.

The combined assembler, claims, discovery, authorization, citation-currentness, and
citation-claims selection produced **47 passed, 1 skipped**. Tests exercised deny-before-
identity, sensitivity and source scope, excluded-source non-disclosure, traversal and
canonical-root confinement, graph-bridge denial, inert prompt-injection content, and
default-denied repository activation. The independent Area F fixture also showed bounded
graph behavior without reading or modifying pilots.

## 6. Area D — authority, temporal state, conflict, and staleness

**Result:** D01–D07 pass.

The authority group produced **21 passed**. Accepted/current precedence, explicit valid
supersession, equal/future/invalid/timezone timestamps, visible accepted conflicts,
staleness labels, confidence reduction, and incomplete sparse-context coverage matched
the frozen contract.

## 7. Area E — claims, citations, coverage, and rendering

**Result:** E01–E09 pass; the Area C symlink skip applies.

The 47-test C/E group verified current-byte fingerprints, metadata signals, post-discovery
mutation/deletion/unreadability failure, locator/excerpt validity, root confinement,
repository snapshot/object identity, incomplete-reference separation, partial coverage,
confidence, and text/JSON semantic equivalence. Public pilot rows show no prohibited Git
subject, author, or remote content.

## 8. Area F — budgets, determinism, trace, and bounded topology

**Result:** F01–F09 pass.

The budget/contracts/determinism group produced **37 passed**. It covered byte and
serialized-output boundaries, multibyte and wrapper accounting, overflow redaction,
semantic determinism, timing isolation, trace content, and malformed inputs.

Quality also created an ephemeral fixture under the operating-system temporary directory,
outside all canonical pilot/evidence roots. Forty linked nodes formed a cycle and
high-fan-out backlinks. With depth 10, fan-out 5, channel 7, and total-candidate 10 caps:

- two executions terminated successfully;
- each selected 10 unique sources with byte-identical semantic results;
- omissions reported one fan-out-cap event, 16 channel-cap events, and one total-cap
  event; and
- the executable view remained clean.

The fixture was deleted after review. This is a QA safety execution only. It is not
retained A10 timing evidence and is not represented as satisfying A10-19.

## 9. Area G — ADR-0021 local-Git boundary

**Result:** G01–G13 pass; one deliberate CS-21 placeholder skip is justified below.

The local-Git and repository-activity selection produced **78 passed, 1 skipped**. Source
and tests independently confirm the three accepted command arrays, placement of
`i18n.logOutputEncoding=UTF-8` before `-C` and `log`, fail-before-activity gates, Git 2.38
floor, one command-scoped `safe.directory` triplet, disabled system/global configuration,
ambient-variable exclusion, no shell/retry/remote/credential route, malformed/timeout/
overflow degradation, linked-worktree/bare/submodule confinement, redaction, and no
persistent Jarvis configuration namespace.

Handoff 24 independently demonstrated the Windows separate-logon case: ordinary Git was
denied while the exact granted adapter succeeded, followed by 68 local-Git passes under
that identity. Handoff 25 binds that evidence to this executable. Candidate and retained
pilot integrity records show stable canonical files, HEAD, index, refs, reflogs, config,
remotes, ownership, reachable objects, and loose-object boundary.

## 10. Area H — CLI, compatibility, packaging, diagnostics, and recovery

**Result:** H01–H10 pass, subject to QF-03 and the two justified suite skips.

Full and static gates:

| Command | Result |
|---|---|
| `python -m pytest -q` | 404 passed, 2 skipped, 45.27 s |
| `python -m ruff check .` | pass |
| `python -m ruff format --check .` | pass |
| `python -m mypy src` | success, 67 source files |
| `git diff --check <released-v0.3.1>..ff402d7` | pass |
| reviewer relative-Markdown link validator over `rg --files -g '*.md'` | 157 files, 488 relative links, 0 missing |

`lychee` was unavailable in the frozen environment, so no result is claimed for that
binary. The independent read-only validator covered repository-relative Markdown
targets; external-network URL validation was intentionally not attempted.

In a new CPython 3.14.4 virtual environment, Quality installed the retained PyYAML wheel
and the exact candidate wheel with `pip install --no-index --no-deps`. Candidate install,
`jarvis --help`, `jarvis resume --help`, and `jarvis resume-doctor --help` all exited 0.
Two fixed-time FileOrbit JSON runs exited 0 and shared SHA-256
`bb9e9376b05096112d086a4fd97895b83c9e0b292bff79a14006aa8dd50f8f93`.
Doctor exited 0. Uninstall exited 0 and removed the command; reinstall of the same verified
wheel exited 0 and reproduced the exact JSON digest. Fixture bytes were unchanged.

The bound A12 artifact supplies the independent explicit outbound-network denial
(Windows error 10051), pilot/doctor executions, missing/corrupt derived-state recovery,
and full before/after canonical and Git integrity. Quality rehashed that artifact and
independently repeated the non-networked installation, help, doctor, deterministic,
uninstall, and reinstall subset. No private pilot was rerun.

## 11. Area I — performance, pilots, privacy, and evidence arithmetic

**Result:** I01–I04 and I06–I12 pass; I05 fails under QF-01.

For each pilot mode, retained raw data declares three warm-ups, 30 measured attempts, 30
completed attempts, a separate cold sample, and no removed sample. Quality recomputed
totals from the retained arrays:

| Mode | p50 / p95 / p99 / max ms | Under 30 s |
|---|---|---|
| survivor denied | 532.482 / 575.008 / 590.165 / 590.165 | 30/30 |
| survivor exact grant | 655.480 / 788.337 / 793.643 / 793.643 | 30/30 |
| AI no-Git | 307.189 / 337.360 / 357.402 / 357.402 | 30/30 |

Quality also recomputed instrumented selection, discovery, binding, and repository
percentiles from their arrays. Values match the reported Python estimator; three exact
halfway p50 values differ by 0.001 ms if PowerShell banker-rounding is used, which is a
rounding implementation difference rather than an evidence mismatch. Authorization,
identity, graph, authority-conflict, and rendering are explicitly uninstrumented and are
not assigned zero.

Pilot counts reconcile: denied and no-Git modes have zero repository citations; the exact
grant has ten; all three report partial coverage with visible conflict/incomplete state;
the no-Git limitation is explicit. Eight private manifest entries independently matched
filename, size, and SHA-256. Both public artifacts matched their committed identities.
The public privacy scan found no absolute path, pilot passage, unapproved note name,
classification value, Git subject/author/remote value, username, credential, or raw
error. Pilot and A12 private evidence remained read-only and is not reproduced here.

### Accepted disclosed limitations

- **A10-12:** only selection, discovery, binding, repository, and total timing are
  available. Quality accepts the disclosure; no value is imputed to unavailable stages.
- **A10-19:** the retained benchmark harness does not generate high-fan-out/cyclic
  topologies. Quality accepts the disclosure and separately tested safety consequences
  under Area F without calling that execution retained A10 timing evidence.

## 12. Area J — A11 consent and strategic-pending boundary

**Result:** J01–J06, J08, and J09 pass; J07 fails under QF-02.

The TSV template contains outcome, usefulness, orientation time, estimated time saved,
incorrect/missing context, citation defects, correction time, requested features, and
notes. Template/example rows are excluded. `python scripts/evaluate_project_resume.py
--json` returned zero rows, null rates/medians, and both threshold booleans false; it did
not declare the gate passed. Static and executable review found no automatic event append,
vault write, telemetry, or opt-out collection path.

The eight-week A11 strategic outcomes are **pending and unproven**. The ≥80% usefulness
threshold, 15–30 minutes-saved target, and 90–95% correctly sourced material-claim target
are not passed, failed, or waived. The executable can satisfy its technical behavior
contract while strategic validation remains pending, but no strategic-success claim may
be made.

## 13. Skips

1. `tests/integration/test_citation_currentness.py:77` skipped because the current Windows
   execution identity cannot create symlinks. Non-symlink traversal/confinement cases and
   other citation-mutation cases passed. This is an environment limitation, not a product
   pass claim.
2. `tests/unit/test_project_resume_local_git.py:578` is the deliberate CS-21
   separate-Windows-logon placeholder. Handoffs 24/25 supply the real process-boundary
   execution and 68-pass follow-up bound to this executable.

No other test or review step was skipped. External URL checking was outside the offline
boundary and is reported as a link-tool limitation, not as a pass.

## 14. Findings and required closure

### QF-01 — High — retained synthetic percentiles are not independently recomputable

- **Reproduction:** enumerate all eight files in the private A10 manifest; inspect
  `a10-raw.json` top-level/mode schemas and `a10-synthetic.txt`; compare them with the
  synthetic section of the public performance JSON.
- **Expected contract:** QA-I05 requires independent recomputation of 100/500/1,000/5,000
  synthetic percentiles and 5,000-note peak memory from retained underlying measurements.
- **Observed result:** `a10-raw.json` retains per-attempt arrays only for the three pilot
  modes. `a10-synthetic.txt` and the public JSON retain synthetic aggregates, not the 30
  per-run arrays or raw peak-memory observations. Hashes prove integrity of the aggregates
  but cannot prove their arithmetic, sample completeness, or non-selection.
- **Affected scope:** A10 synthetic scale evidence and QA-I05. This does not invalidate
  the independently recomputed three-pilot under-30-second result or the separate cyclic/
  fan-out safety execution.
- **Release impact:** the activated evidence contract is materially incomplete and cannot
  be independently reproduced. Release must not proceed on this package.
- **Owner / closure evidence:** Engineering Evidence owner, independently reviewed by CTO
  and Quality. Retain per-run synthetic arrays and memory observations, bind them in the
  manifest/public derivation, and provide an independently recomputable exact-candidate
  evidence package without changing the candidate.

### QF-02 — Medium — A11 sourcing percentage has no reviewed-claim denominator

- **Reproduction:** inspect the dogfood TSV header, `evaluate_project_resume.py`, A11
  acceptance text, and search the executable documentation for a weekly claim-review
  denominator.
- **Expected contract:** QA-J07 requires a defined count of reviewed material claims before
  reporting the 90–95% correctly sourced percentage.
- **Observed result:** the template records `citation_defects`; the evaluator sums defects.
  Neither records `material_claims_reviewed` (or an equivalent denominator), computes a
  sourcing rate, or defines a weekly denominator procedure.
- **Affected scope:** future A11 collection and the 90–95% sourcing outcome only; no A11
  data was collected during QA.
- **Release impact:** the current mechanism cannot prove the strategic sourcing target.
  Any percentage would be undefined. A11 remains pending and unproven.
- **Owner / closure evidence:** Product Owner defines the denominator and consented weekly
  procedure; Engineering versions the template/evaluator; Quality verifies example-row
  exclusion and correct rate arithmetic before real percentage reporting.

### QF-03 — Medium — same-named stale wheels create an artifact-selection hazard

- **Reproduction:** recursively enumerate
  `jarvis_core-0.1.0-py3-none-any.whl` under the designated worktrees and hash each file.
- **Expected contract:** release installation and publication select only the bound
  126,683-byte wheel with SHA-256 `8dcc1378...a768cd3`.
- **Observed result:** the exact wheel exists under `dist/ff402d7`. Same-named ignored/
  out-of-band copies exist under the generic Engineering `dist` directory and A12
  worktree; both are 124,678 bytes with SHA-256
  `7253e0b938433d7e393d186a3006c971b576381f6518fe986154d162fe0b3662`.
  Quality did not install or modify those copies.
- **Affected scope:** human artifact selection and release staging, not executable source
  behavior or the exact bound wheel.
- **Release impact:** selecting by filename rather than path, size, and digest can publish
  or install the wrong payload.
- **Owner / closure evidence:** Release owner stages only the exact `dist/ff402d7` wheel,
  records size and SHA-256 at the publication boundary, and proves the staged artifact
  matches the bound identity. Stale out-of-band copies must not be release inputs.

## 15. Command ledger

The review used the following command families; results are recorded in the applicable
Areas above:

- Git identity, tree, detached-state, status, ancestry, worktree-list, diff-name, and
  `diff --check` commands in each designated view.
- SHA-256/size enumeration for every Section 1 artifact, all private manifest entries,
  and all same-named wheel copies.
- ZIP metadata/inventory enumeration and byte comparison of all 68 runtime payload files.
- `python -m pytest -q`; targeted `pytest` selections for Areas B, C/E, D, F, G, and H/J;
  `python -m ruff check .`; `python -m ruff format --check .`; and
  `python -m mypy src`.
- Read-only source/document searches for scope, command arrays, privacy terms, A11 fields,
  denominator procedure, and excluded capabilities.
- Independent raw-array percentile/max/accounting recomputation and manifest verification.
- Offline temporary-environment `venv`, `pip install --no-index --no-deps`, installed
  help/fixture/doctor, uninstall, exact-wheel reinstall, and deterministic rerun commands.
- Reviewer relative-Markdown target validation over all tracked Markdown paths.
- `python scripts/evaluate_project_resume.py --json` against the unchanged template.
- Ephemeral cyclic/high-fan-out fixture execution in an operating-system temporary
  directory, followed by verified cleanup.

One initial packaging attempt referenced a nonexistent QA-local `.venv` and exited before
creating an environment; Quality corrected the interpreter path to system CPython 3.14.4.
An initial private-evidence lookup used the repository root rather than the evidence
worktree and returned path-not-found; the exact read-only evidence path was then used.
Neither operator correction touched a designated view.

## 16. Final integrity and stop conditions

After executable work, the QA view remained detached at `ff402d7`, tree `a7ff2c0`, and
clean. The evidence view remained at `6173482` and clean. No pilot, classification,
private baseline, candidate, wheel, evidence, or documentation file changed. Reviewer
fixtures and installation outputs remained outside canonical data and were removed.

QF-01 triggers Handoff 32's materially incomplete/unreproducible-evidence stop condition.
QF-02 prevents the required future sourcing metric. Quality performed no repair, merge,
push, tag, release, publication, A11 collection, pilot/classification change, unrelated
work, or v0.5 work.

Not ready
