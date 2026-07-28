# Handoff 05 — Quality & Release to Product Owner

| Field | Value |
|---|---|
| Sender | Independent Quality & Release Manager |
| Receiver | Product Owner — Jason Murray |
| Milestone | v0.3.1 — Query Trust Contracts |
| Review date | 2026-07-27 |
| Candidate branch | `feature/v0.3.1-query-trust-contracts` |
| Frozen QA HEAD | `09a4ca5a6e0d9b73a1e37a9e086abe788c894c72` |
| Governance base | `a6c89c5be8ce78a4d9d6359a62c94aa83a84d513` |
| QA worktree | `C:\Users\jmurr\Projects\AI-Operating-System\.worktrees\v0.3.1-qa` |
| Disposition | **Refactor first** |

## Latest effective state

**Effective revision:** Superseding limited A/G/H revalidation.

**Effective disposition:** **Ready** for frozen executable `956c2ed`; Product Owner
subsequently approved controlled merge.

**Supersession:** This effective state supersedes the initial `Refactor first` disposition
shown in the historical metadata and body below. Use the
[v0.3.1 Handoff Index](README.md) for current lifecycle routing.

## 1. Executive finding

The frozen candidate must not ship from this exact HEAD.

The trust-contract implementation passed the complete automated suite, static checks,
targeted authorization/citation/compatibility/context tests, direct CLI sampling, and
before/after vault-integrity comparison. The release nevertheless has two blocking
evidence defects:

1. Both documented benchmark entry points fail immediately when invoked using their
   documented commands. They cannot import `tests.support.synthetic_vault`.
2. The benchmark smoke tests do not exercise subprocess/script startup and therefore pass
   while both documented entry points are broken.

The independently repeated equivalent performance comparison also did not produce one
stable gate result. One same-machine comparison exceeded the permitted +20% regression
ceiling; a reverse-order repeat passed. This does not prove a deterministic performance
failure, but it does mean the release evidence cannot support an unconditional gate pass.

No defect was fixed during QA. The detached candidate worktree remained at the authorized
HEAD and clean after all checks.

## 2. Candidate and repository preconditions

| Check | Independent result |
|---|---|
| Detached QA HEAD | Exact match: `09a4ca5a6e0d9b73a1e37a9e086abe788c894c72` |
| Starting candidate status | Clean; detached HEAD |
| Local feature branch | Points exactly to the authorized HEAD |
| Commit belongs to feature branch | Confirmed by `git branch --contains` and worktree metadata |
| Governance-base ancestry | Confirmed |
| Local `main` contains candidate | No |
| `origin/main` contains candidate | No |
| Remote branch contains candidate | No |
| Remote feature branch exists | No |
| Candidate pushed | No evidence of any pushed ref containing the commit |
| Candidate merged | No, locally or on fetched `origin/main` |
| Ending candidate HEAD/status | Exact authorized HEAD; clean; detached |

Remote state was refreshed from `origin` before the remote containment checks. The remote
advertised only `main` and three earlier feature branches; none contained the candidate.

The complete release range contains 19 commits and 55 changed files, with 4,564 insertions
and 344 deletions. No conversation, streaming, real-provider, plugin, MCP, agent,
automation, persistence, or vault-write feature was found in the release diff.

The engineering worktree was already dirty with governance/coordination updates and the
Chief-of-Staff QA prompt. QA did not alter those inputs and added only this required
artifact.

## 3. QA environment

| Component | Value |
|---|---|
| OS | Windows 11, build `10.0.26200` |
| Python | 3.14.4 |
| pytest | 9.1.1 |
| Ruff | 0.16.0 |
| mypy | 2.3.0, compiled |
| Git | 2.55.0.windows.1 |
| Candidate worktree mode | Detached, clean, read-only during execution |
| Network use by product checks | None |

The interpreter came from the repository's existing root virtual environment:

```text
C:\Users\jmurr\Projects\AI-Operating-System\.venv\Scripts\python.exe
```

pytest obtains the candidate `src` path from `pyproject.toml`. Direct CLI diagnostic runs
used the candidate `src` directory explicitly because the shared virtual environment is
associated with the primary worktree.

## 4. Commands and primary results

### Candidate and remote state

```text
git rev-parse HEAD
git symbolic-ref -q HEAD
git status --porcelain=v2 --branch
git branch --contains 09a4ca5a6e0d9b73a1e37a9e086abe788c894c72
git worktree list --porcelain
git fetch origin --prune
git branch -r --contains 09a4ca5a6e0d9b73a1e37a9e086abe788c894c72
git merge-base --is-ancestor <candidate> main
git merge-base --is-ancestor <candidate> origin/main
git ls-remote --heads origin
```

Result: exact detached HEAD, clean candidate, correct feature-branch membership, and no
local or remote merge/push.

### Automated and static checks

```text
python -m pytest -q
python -m ruff check src tests scripts
python -m mypy src
git diff --check a6c89c5be8ce78a4d9d6359a62c94aa83a84d513..09a4ca5a6e0d9b73a1e37a9e086abe788c894c72
```

Results:

- pytest: 198 passed, 1 skipped in 27.53 seconds;
- Ruff: passed;
- mypy: passed for 52 source files;
- release-diff whitespace check: passed.

The skipped test was
`tests/integration/test_citation_currentness.py::test_symlink_escape_declines_citation`.
Windows denied creation of the test symlink in this environment. This is an environment
limitation on one path-confinement probe, not a waiver of the contract.

### Targeted adversarial suite

```text
python -m pytest -q -vv \
  tests/unit/test_policy.py \
  tests/integration/test_authorization.py \
  tests/integration/test_citation_currentness.py \
  tests/integration/test_citation_claims.py \
  tests/unit/test_passages.py \
  tests/unit/test_passages_ac03.py \
  tests/integration/test_cli_coverage_visibility.py \
  tests/unit/test_context_budget.py \
  tests/unit/test_compat.py \
  tests/integration/test_versioned_contract.py \
  tests/integration/test_readonly_v031.py \
  tests/integration/test_determinism.py
```

Result: 67 passed, 1 symlink test skipped.

### Documented benchmark commands

```text
python scripts\benchmark_query.py --sizes 100,500,1000 --runs 10
python scripts\benchmark_regression.py --runs 20
```

Both commands failed before argument parsing or measurement:

```text
ModuleNotFoundError: No module named 'tests'
```

Both scripts import `tests.support.synthetic_vault`, but direct script execution places
the `scripts` directory—not the repository root—at the front of `sys.path`.

The mandated smoke test still passed:

```text
python -m pytest -q tests\integration\test_benchmark_smoke.py
3 passed
```

The smoke test loads each script with `importlib.util.spec_from_file_location()` inside
pytest. pytest has already added the repository root, so this test does not reproduce the
documented process-start boundary and cannot detect the observed import failure.

### Diagnostic benchmark workaround

QA added the repository root and candidate source directory to `PYTHONPATH` only for
diagnosis; no candidate file was changed.

The documented query workload then completed:

| Size | Total p50 | Total p95 | Total p99 |
|---:|---:|---:|---:|
| 100 | 3.030 ms | 4.104 ms | 4.104 ms |
| 500 | 15.026 ms | 20.814 ms | 20.814 ms |
| 1,000 | 30.387 ms | 33.990 ms | 33.990 ms |

- Peak memory at 1,000 notes: 5.453 MB.
- Authorization stress excluded 500 of 1,000 notes.
- Authorization-stress total p95: 17.083 ms.

Equivalent 50-run total-pipeline comparisons on the same machine and interpreter:

| Attempt | Baseline p95 | Candidate p95 | Regression | Gate |
|---|---:|---:|---:|---|
| Initial | 32.927 ms | 41.411 ms | +25.8% | Exceeds ceiling |
| Reverse-order repeat | 32.858 ms | 36.816 ms | +12.0% | Within ceiling |

The first result exceeds the accepted +20% ceiling; the repeat does not. No performance
waiver exists. The gate therefore needs a reproducible paired protocol and stable evidence
after the entry-point defect is corrected.

## 5. Exact-HEAD matrix results A–I

### A — Candidate identity and evidence integrity

Candidate identity, ancestry, complete release diff, starting cleanliness, remote state,
and ending cleanliness were verified. Full tests, Ruff, mypy, and release-diff checks were
rerun. A sorted inventory containing relative path, SHA-256, size, and UTC last-write
timestamp was captured before and after representative commands; it was unchanged.

Environment-specific findings:

- one symlink test could not execute;
- the shared interpreter is not installed against the detached worktree;
- both direct benchmark commands fail without an extra repository-root import path.

### B — Authorization and non-disclosure

Targeted policy and authorization checks passed for sensitivity ceilings, unknown
sensitivity, empty/restricted dimensions, source/path/type restrictions, excluded-only
terms, trace non-disclosure, restricted graph neighbors, explicit local scope, duplicate
IDs, deterministic policy behavior, sibling-prefix collision, slash/case normalization,
absolute prefixes, and parent traversal.

Source inspection confirmed `build_authorized_view()` executes before construction of the
relationship resolver, lexical index, ranker, and context builder. Excluded notes are not
provided to those collaborators. Only the aggregate excluded count is retained.

No excluded identity/content leakage was observed in answers, citations, traces, graph
expansion, or errors sampled by the targeted suite.

### C — Current-source and citation trust boundary

The supported engine and CLI constructions require explicit scope and `source_root`;
omission and explicit null fail closed. Tests passed for current-byte mutation, missing
sources, exact fingerprints, LF/CRLF distinction, invalid ranges, excerpt mismatch,
heading hierarchy, renamed parents, moved locators, empty excerpts/sources, metadata
support, claim-specific summarization, relationship passages, and evidence-absent decline.

Source inspection confirmed current paths are resolved, required to remain beneath the
resolved source root, required to be files, and reread immediately before supported
citation emission. Fingerprint equality and passage validation are checked against those
current bytes.

The symlink-escape test was not executable on this host. No waiver was requested or
granted.

### D — Evidence coverage and consumer semantics

Supported, mixed, incomplete-only, and no-citation structures were exercised through the
suite and CLI sampling. Text separates supporting passages from incomplete references.
JSON includes answer-level coverage plus per-citation coverage. Incomplete references do
not render `0-0` as a supporting locator. Incomplete-only answers are treated as warnings
and explicitly not fully evidence-backed.

The activated matrix names `query`, `context`, and `brief`, but the accepted implementation
brief and actual v0.3.1 CLI expose `ask`, `search`, `summarize`, and `explain`. QA exercised
the accepted implemented surfaces in text and JSON. No Product Owner authorization exists
to add the three matrix-only command names during QA.

### E — Retrieval, ranking, graph, and context

Deterministic candidate/ranking behavior, graph restriction, missing links, duplicate
titles, direct relationships, scale behavior, and context selection passed. New structured
outputs use `relative_relevance`; `answer_confidence` remains null. No new writer emits the
ambiguous ranking field.

Budget checks passed for negative, zero, property-loop boundaries, oversized-first-source
truncation, deterministic output, and the invariant
`0 <= total_tokens <= token_budget`. The accepted context contract charges excerpt tokens
and a deterministic inter-chunk separator; title/path/role fields are audit metadata rather
than provider-prompt content.

### F — Versioning and compatibility

Current answers, citations, context, and traces use `jarvis.query.v0.3.1`; index versioning
is separate. The narrow legacy reader accepted exact valid legacy shapes and rejected
missing/unknown keys, wrong types/ranges, mixed shapes, result/citation confusion, invalid
nested citations, and conflicting old/new relevance values. It removes legacy
`confidence` and never maps ranking into answer confidence.

Source inspection found the compatibility path to be reader-only and unused to bypass
current authorization or citation validation.

### G — CLI, exit behavior, and operational safety

Direct samples covered `ask`, `search`, `summarize`, and `explain` across text and JSON,
including trace output. Observed exit behavior:

| Scenario | Exit | stdout | stderr |
|---|---:|---|---|
| Successful query commands | 0 | Product output | Empty |
| No-match warning | 2 | Structured answer | Empty |
| Missing required argument | 2 | Empty | argparse diagnostic |
| Missing vault/internal setup failure | 1 | Empty | Error diagnostic |

The before/after vault inventory was identical after these commands. No network,
subprocess, rename, delete, permission, timestamp, or vault-content mutation was observed
from the query paths. Repository and candidate status remained unchanged.

Existing suites additionally exercised empty results, malformed vault data, Unicode
fixtures, 100/500/1,000-note scale, deterministic JSON, and read-only repository behavior.

### H — Benchmark and release gate

The benchmark smoke module passed, but both exact documented benchmark commands failed at
startup. The smoke design does not test the failing subprocess boundary. This directly
contradicts Revision 5's claim that the documented entry points are enforced.

With an import-path workaround, functional benchmark phases completed and the baseline
adapter selected the full candidate constructor when candidate source was active. Source
inspection confirmed the fallback branches are confined to the benchmark adapter.

Performance comparisons were not stable enough for one independent gate conclusion: one
equivalent attempt was +25.8%, and a reverse-order repeat was +12.0%. The release may not
claim the ceiling is independently demonstrated until the supported harness runs directly
and a recorded reproducible protocol resolves that variance.

### I — QA disposition and handoff

This document is the only QA artifact. No candidate change, defect fix, merge, push,
rebase, amend, staging action, parked-conversation action, or Librarian activity was
performed.

## 6. Blocking findings

### QR-031-01 — Documented benchmark entry points cannot run

**Affected gate:** Area H; implementation brief sections 7, 9, and Definition of Done.

The exact required commands fail with `ModuleNotFoundError` before executing any benchmark
phase. A release benchmark that requires an undocumented `PYTHONPATH` workaround is not a
reproducible supported entry point.

Required correction:

- make both documented script commands run from the repository root in the supported
  environment without an undocumented import-path override;
- preserve candidate/baseline isolation in the regression harness; and
- rerun the complete benchmark evidence from those exact entry points.

### QR-031-02 — Benchmark smoke test does not enforce process startup

**Affected gate:** Revision 5 correction claim and Area H.2.

The smoke tests import scripts inside pytest, masking the missing repository-root import
path. They pass while direct execution fails.

Required correction:

- add an automated subprocess or equivalent process-boundary smoke test that runs the
  documented commands from the repository root;
- assert successful startup and required completion markers; and
- ensure the test fails if either benchmark cannot import its runtime dependencies.

### QR-031-03 — Performance-ceiling evidence is not independently stable

**Affected gate:** Area H.3–H.5.

One equivalent 50-run comparison exceeded the ceiling by approximately 5.8 percentage
points; a reverse-order repeat passed. This is not a proven permanent implementation
regression, but it is an unresolved release-evidence conflict and has no approved waiver.

Required correction/evidence:

- define and run a paired or interleaved same-machine baseline/candidate protocol;
- retain raw samples for both versions;
- use identical warm-ups, run counts, fixtures, queries, percentile calculation, Python,
  and construction-plus-query boundary;
- report repeatability or variance across multiple paired attempts; and
- demonstrate that the accepted result is no more than +20%.

## 7. Waivers, residual risks, and exclusions

No waivers were requested or granted.

Residual risks after the blocking corrections:

- Windows symlink/junction confinement still needs execution in an environment that can
  create the relevant link type.
- Aggregate timing remains a coarse side channel, as already recorded by architecture.
- Direct filesystem current-source resolution remains bounded technical debt before a
  second repository implementation.
- Performance measurements on a developer workstation remain sensitive to scheduler and
  background-load variance; the gate protocol should make that variance visible.

Out of scope and untouched: chat, streaming, real providers, Project Resume, memory,
plugins, MCP, tools, agents, automation, writes, and the parked conversation candidate.

## 8. Required return package

Return a superseding exact-HEAD package containing:

1. the two benchmark entry-point corrections;
2. a real process-boundary benchmark smoke test;
3. full pytest, Ruff, mypy, and release-diff results;
4. unchanged-vault evidence covering the corrected benchmark paths;
5. reproducible paired baseline/candidate raw performance evidence;
6. exact new HEAD and bounded correction diff; and
7. renewed architecture clearance for the changed benchmark/test scope.

Quality & Release must then rerun the affected Area A, G, and H evidence and any area
impacted by the correction before issuing a superseding release disposition.

## 9. Prepared narrowed A/G/H rerun checklist

**Status:** Prepared only; not executed.

This checklist becomes active only after the CTO issues evidence clearance for a new exact
HEAD and identifies the bounded correction diff. Preparation of this checklist does not
authorize QA execution, change the disposition below, or accept engineering or
architecture claims as proof.

### Entry gate — required before any QA rerun

- [ ] Receive a superseding CTO evidence-clearance artifact naming the exact branch, exact
  HEAD, prior QA HEAD, correction range, reviewed files, and authorized QA scope.
- [ ] Confirm the clearance explicitly authorizes the narrowed A/G/H rerun.
- [ ] Confirm the correction scope is limited to benchmark entry points, process-boundary
  smoke coverage, performance evidence, and directly necessary documentation.
- [ ] Stop and require broader architecture review if production query, policy,
  authorization, identity, citation, context, compatibility, CLI contract, dependency, or
  packaging behavior changed.
- [ ] Use a clean detached QA worktree at the cleared exact HEAD.
- [ ] Record the toolchain, operating system, CPU/power context, and environment variables.
- [ ] Preserve the candidate as read-only; write only a superseding QA handoff after the
  rerun is complete.

### Area A — exact candidate and evidence integrity

- [ ] Verify `git rev-parse HEAD` equals the CTO-cleared SHA.
- [ ] Verify `git symbolic-ref -q HEAD` confirms detached HEAD.
- [ ] Verify the starting worktree is clean with
  `git status --porcelain=v2 --branch`.
- [ ] Verify the cleared commit belongs to
  `feature/v0.3.1-query-trust-contracts`.
- [ ] Verify the prior QA HEAD is an ancestor of the cleared HEAD.
- [ ] Verify the correction range matches the files and commits named by CTO clearance.
- [ ] Inspect the complete correction diff and `git diff --check`.
- [ ] Refresh `origin`, then verify no remote branch contains the cleared commit and
  neither local nor remote `main` contains it.
- [ ] Identify untracked, generated, cached, environment-specific, or unreviewed release
  inputs.
- [ ] Rerun the full test suite, Ruff, and mypy because the benchmark smoke test is part of
  the integrated release suite.
- [ ] Record every pass, failure, skip, warning, and environment limitation without
  substituting Engineering or CTO summaries.
- [ ] Reconfirm exact HEAD and clean candidate status after all A/G/H work.

Prepared command set:

```powershell
git rev-parse HEAD
git symbolic-ref -q HEAD
git status --porcelain=v2 --branch
git branch --contains <CLEARED_HEAD>
git log --oneline --reverse 09a4ca5a6e0d9b73a1e37a9e086abe788c894c72..<CLEARED_HEAD>
git diff --name-status 09a4ca5a6e0d9b73a1e37a9e086abe788c894c72..<CLEARED_HEAD>
git diff --check 09a4ca5a6e0d9b73a1e37a9e086abe788c894c72..<CLEARED_HEAD>
git fetch origin --prune
git branch -r --contains <CLEARED_HEAD>
git merge-base --is-ancestor <CLEARED_HEAD> main
git merge-base --is-ancestor <CLEARED_HEAD> origin/main
python -m pytest -q
python -m ruff check src tests scripts
python -m mypy src
```

### Area G — operational and read-only safety of corrected entry points

- [ ] Capture a sorted before-snapshot of every designated fixture/vault source containing
  relative path, SHA-256, size, and UTC last-write timestamp.
- [ ] Run both corrected benchmark commands exactly as documented from the repository root,
  with no undocumented `PYTHONPATH`, working-directory, import, or installation workaround.
- [ ] Capture stdout, stderr, and exit code separately for each command.
- [ ] Verify successful output is on stdout and diagnostics are on stderr.
- [ ] Exercise invalid benchmark arguments and verify deterministic nonzero exit behavior
  without traceback leakage or filesystem mutation.
- [ ] Verify benchmark temporary data is isolated outside source fixtures and is not left
  behind as a release input.
- [ ] Verify no product network, subprocess escape, vault write, deletion, rename,
  permission, or timestamp mutation occurs.
- [ ] Capture the after-snapshot and require exact equality with the before-snapshot.
- [ ] Verify no candidate or repository file changed and no untracked benchmark output was
  created.
- [ ] If the correction changes shared CLI/bootstrap/import behavior, rerun representative
  `ask`, `search`, `summarize`, and `explain` text/JSON exit-code scenarios; otherwise
  record why those previously passed scenarios are outside the bounded correction.

Prepared exact supported commands:

```powershell
python scripts\benchmark_query.py --sizes 100,500,1000 --runs 10
python scripts\benchmark_regression.py --runs 50
```

No environment-path override is permitted when evaluating whether these documented entry
points are corrected.

### Area H — benchmark entry point, smoke enforcement, and performance gate

- [ ] Run `scripts/benchmark_query.py` through warm-up, 100/500/1,000 measured sizes,
  1,000-note memory measurement, and authorization-stress completion.
- [ ] Require the exact documented command to start and finish without import-path help.
- [ ] Run the benchmark smoke module directly.
- [ ] Inspect the corrected smoke test and prove it crosses a real process boundary from
  the repository root rather than importing the script inside pytest.
- [ ] Perform a negative mutation review: demonstrate that removing the benchmark import
  correction, `scope`, or `source_root` at either corrected site would make the enforced
  smoke test fail.
- [ ] Verify the baseline adapter cannot instantiate current candidate code without both
  explicit scope and `source_root`.
- [ ] Run the exact v0.3 baseline and cleared candidate with identical fixture, query,
  warm-ups, run count, percentile calculation, interpreter, machine, and
  construction-plus-query boundary.
- [ ] Use a predeclared paired or interleaved order to reduce scheduler/order bias.
- [ ] Retain or reference raw samples for every baseline and candidate attempt.
- [ ] Report p50, p95, p99, peak memory, authorization-stress behavior, and the exact
  percentage calculation.
- [ ] Require every accepted paired result—or a predeclared aggregate rule approved in the
  CTO clearance—to remain no more than +20% above baseline p95.
- [ ] Treat any unapproved result above +20%, missing raw evidence, entry-point failure, or
  mismatch in benchmark boundaries as release-blocking.
- [ ] Do not weaken authorization, current-source validation, citation construction, or
  measured scope to improve performance.

Prepared regression calculation:

```text
regression_percent = ((candidate_p95 - baseline_p95) / baseline_p95) * 100
pass only when the CTO-approved reproducibility rule is satisfied and
regression_percent <= 20.0
```

### Narrowed rerun stop conditions

Stop without issuing a superseding QA disposition if:

- the CTO clearance is absent, ambiguous, or refers to a different HEAD;
- the candidate is not detached and clean at the cleared HEAD;
- the correction diff exceeds the authorized benchmark/test/documentation scope;
- the commit has been merged or pushed before QA;
- a documented entry point still needs an undocumented environment workaround;
- the process-boundary smoke test does not detect startup/import failure;
- fixture/vault metadata or content changes;
- the equivalent performance gate breaches the approved ceiling or remains unresolved;
- any trust-contract or production source changed without renewed full-matrix clearance.

### Prepared rerun output contract

After authorized execution, append a superseding QA revision to this handoff or create the
exact successor artifact directed by the CTO/Chief of Staff. Record:

1. cleared branch, exact HEAD, prior HEAD, and correction range;
2. environment and exact commands;
3. A/G/H results, failures, skips, waivers, and evidence locations;
4. vault before/after result;
5. benchmark raw-evidence location and performance calculation;
6. residual risks;
7. one new formal disposition to the Product Owner.

Until that authorized rerun occurs, the disposition below remains controlling.

## 10. Final disposition

**Refactor first.**

Return exact HEAD `09a4ca5a6e0d9b73a1e37a9e086abe788c894c72` for the bounded corrections
and evidence described above. The Product Owner retains final authority, but this QA
record does not recommend merge or release of the frozen candidate.

---

# Superseding Limited Revalidation — Areas A, G, and H

| Field | Value |
|---|---|
| Role | Independent Quality & Release Manager |
| Revalidation date | 2026-07-27 |
| Authorized scope | Areas A, G, and H only |
| Executable candidate | `956c2ed1dd1144e836014b049a89c47e971818a0` |
| Evidence commit | `8fa5f18c09de1a0c9a79f33e0ba987f9de0e1083` |
| CTO/routing commit | `6692c5e3b1cf4564f3f2be5c7f412739a4d3686a` |
| Exact baseline | `ce0dc35853008e6b83c3c6fdfd0b8650738bee3d` |
| QA worktree | `C:\Users\jmurr\Projects\AI-Operating-System\.worktrees\v0.3.1-qa-revalidation` |
| Evidence artifact | `docs/evidence/v0.3.1/paired-performance-956c2ed-vs-ce0dc35.json` |
| Evidence SHA-256 | `f8a67162b74125454f2a5199e6b46a33952763fff18821b7c81497819ffa18d6` |

## S1. Superseding effect and scope

This revision supersedes the earlier Quality & Release disposition for the bounded
benchmark-entry-point, process-smoke, and performance-evidence findings QR-031-01 through
QR-031-03. The earlier full review remains the historical record for unaffected Areas
B–F and I.

Execution was limited to the latest CTO-authorized Areas A, G, and H. No concrete
regression signal required reopening an unaffected trust-contract area.

No source, test, script, protocol, evidence, gate rule, dependency, or candidate file was
changed during revalidation. QA did not implement a fix, merge, push, release, perform
Librarian work, or touch the parked conversation candidate.

## S2. Environment

| Component | Revalidation value |
|---|---|
| OS | Windows 11 `10.0.26200` |
| Python | 3.14.4 |
| pytest | 9.1.1 |
| Ruff | 0.16.0 |
| mypy | 2.3.0 |
| Git | 2.55.0.windows.1 |
| Candidate state | Clean detached HEAD |
| Product benchmark network use | None |
| Benchmark import override | None; `PYTHONPATH` removed |

The retained evidence was generated separately on Python 3.10.12 and Linux
6.8.0-124-generic x86_64. QA treated the retained arithmetic and the fresh Windows
execution as separate evidence and did not equate their absolute timings.

## S3. Area A — candidate and evidence integrity

### Identity and repository state

- The revalidation worktree began clean and detached at exact executable candidate
  `956c2ed1dd1144e836014b049a89c47e971818a0`.
- `09a4ca5` and baseline `ce0dc35` are ancestors of the executable candidate.
- The executable candidate is an ancestor of evidence commit `8fa5f18`.
- The local feature branch contains the executable candidate.
- Refreshed remote refs contain neither the candidate nor a feature branch for it.
- Neither local `main` nor fetched `origin/main` contains the candidate.
- The candidate therefore remains unmerged and unpushed.
- The ending candidate state remained clean, detached, and byte-identical at `956c2ed`.

The executable correction from prior QA HEAD `09a4ca5` through `956c2ed` changed only
benchmark scripts, benchmark smoke tests, the new paired protocol, and lifecycle
documentation. The range from executable candidate `956c2ed` through evidence commit
`8fa5f18` contains no change under `src/`, `tests/`, `scripts/`, or `pyproject.toml`.
The evidence commit itself adds the retained JSON and Engineering Review addendum only.

### Evidence digest and independent arithmetic

QA independently computed the artifact digest:

```text
f8a67162b74125454f2a5199e6b46a33952763fff18821b7c81497819ffa18d6
```

It exactly matches the authorized digest.

QA parsed every raw array and independently applied the committed estimator:

```text
idx = min(n - 1, round(q * (n - 1)))
```

Every stored count, p50, p95, p99, and regression matched:

| Attempt | Order | Candidate p50/p95/p99 (ms) | Baseline p50/p95/p99 (ms) | Regression |
|---:|---|---:|---:|---:|
| 0 | candidate first | 31.924 / 37.280 / 38.150 | 29.578 / 33.417 / 34.510 | 11.56% |
| 1 | baseline first | 32.168 / 37.329 / 37.918 | 29.166 / 33.578 / 35.819 | 11.17% |
| 2 | candidate first | 33.401 / 41.925 / 58.252 | 29.866 / 33.910 / 34.436 | **23.64%** |
| 3 | baseline first | 32.297 / 38.679 / 39.017 | 30.658 / 35.570 / 35.789 | 8.74% |
| 4 | candidate first | 33.666 / 41.379 / 43.289 | 29.796 / 35.433 / 35.795 | 16.78% |

Counts are exactly 30 candidate plus 30 baseline observations in each of five attempts:
150 candidate and 150 baseline samples.

Sorted retained regressions are 8.74%, 11.17%, 11.56%, 16.78%, and 23.64%. The
predeclared median is 11.56%. The 23.64% attempt is retained and not removed, discounted,
or waived.

### Integrated checks

```text
python -m pytest -q
python -m ruff check src tests scripts
python -m mypy src
git diff --check 09a4ca5..956c2ed
```

Results:

- pytest: 200 passed, 1 skipped in 27.42 seconds;
- Ruff: passed;
- mypy: passed for 52 source files;
- correction-diff check: passed.

The one skip remains the previously recorded Windows inability to create the symlink used
by `test_symlink_escape_declines_citation`. The limited correction did not touch that
test or path-confinement implementation, so it is retained as an environmental residual
risk rather than a new regression signal.

**Area A result: pass.**

## S4. Area G — operational entry points and safety

QA removed `PYTHONPATH` and executed the documented commands directly from the frozen
candidate repository root:

```text
python scripts\benchmark_query.py --sizes 100,500,1000 --runs 10
python scripts\benchmark_regression.py --runs 50
```

Both started and completed with exit code 0 and no import-path workaround.

The query benchmark reached all required completion phases:

| Workload | Total p50 | Total p95 | Total p99 |
|---:|---:|---:|---:|
| 100 notes | 3.264 ms | 5.525 ms | 5.525 ms |
| 500 notes | 14.845 ms | 16.202 ms | 16.202 ms |
| 1,000 notes | 31.383 ms | 33.462 ms | 33.462 ms |

- Peak memory at 1,000 notes: 5.453 MB.
- Authorization stress excluded 500 of 1,000 notes.
- Authorization-stress total p95: 16.925 ms.

The standalone current-candidate regression diagnostic completed with total-pipeline p95
36.260 ms over 50 runs.

An invalid `--runs not-an-integer` invocation returned exit 2 with an argparse diagnostic
and no candidate or canonical-source mutation.

Before and after the documented commands, QA compared every canonical fixture source by
relative path, SHA-256, byte size, and UTC last-write timestamp. The snapshots were
identical. No repository output or untracked benchmark artifact was produced. Benchmark
fixtures and the independently materialized baseline were confined to temporary
directories; the QA-created exact-baseline directory was verified beneath the system temp
root and removed after use.

The corrected benchmark bootstrap inserts only each script's own repository root and
`src` directory. Candidate and baseline runs execute from separate trees. The paired
protocol removes inherited `PYTHONPATH` and runs one subprocess per version per attempt.

Real process-boundary smoke command:

```text
python -m pytest -q -vv tests\integration\test_benchmark_smoke.py
```

Result: 5 passed in 9.09 seconds. The cases cover:

- direct query benchmark completion from repository root;
- direct regression benchmark completion;
- JSON raw-sample output;
- nonzero missing-runtime-dependency failure; and
- paired-protocol entry-point completion.

Source inspection confirmed these tests invoke new Python processes rather than importing
the benchmark modules inside pytest. The missing-dependency case proves the smoke fails
when the script cannot reach required runtime modules. Existing fail-closed engine tests
continue to enforce explicit scope and `source_root`.

**Area G result: pass.**

## S5. Area H — performance evidence and gate

### Predeclared rule

The committed `scripts/benchmark_paired.py` defines, before retained evidence collection:

- five paired attempts by default;
- 30 measured runs per version per attempt;
- three warm-ups;
- alternating candidate-first and baseline-first order;
- the same `benchmark_regression.py` harness in both trees;
- 1,000 synthetic notes and query `links`;
- construction plus one public `QueryEngine.run()` as the measured boundary;
- the recorded nearest-rank percentile estimator; and
- pass when median paired p95 regression is no more than 20%.

QA did not change or select this rule after observing results.

### Retained evidence result

```text
range: 8.74%–23.64%
median: 11.56%
gate: 11.56% <= 20.00%
```

The retained performance gate passes under the predeclared median-of-five rule. Attempt 2
at 23.64% is explicitly disclosed. The evidence proves that the attempt occurred; it does
not instrument or prove scheduler activity, background load, CPU frequency, thermal
behavior, or another cause. Any attribution to those causes remains inference.

### Independent fresh paired rerun

QA materialized exact baseline `ce0dc35` from `git archive`, used the identical harness,
removed `PYTHONPATH`, and ran:

```text
python scripts\benchmark_paired.py --baseline-root <temporary-ce0dc35-tree> \
  --notes 1000 --runs 30 --attempts 5
```

Observed results:

| Attempt | Order | Candidate p95 | Baseline p95 | Regression |
|---:|---|---:|---:|---:|
| 0 | candidate first | 39.886 ms | 36.880 ms | 8.15% |
| 1 | baseline first | 40.216 ms | 36.358 ms | 10.61% |
| 2 | candidate first | 44.749 ms | 31.750 ms | **40.94%** |
| 3 | baseline first | 40.880 ms | 32.707 ms | **24.99%** |
| 4 | candidate first | 38.190 ms | 33.349 ms | 14.52% |

```text
range: 8.15%–40.94%
median: 14.52%
gate: 14.52% <= 20.00%
exit code: 0
```

The fresh equivalent rerun independently confirms that the committed rule executes and
passes on this Windows/Python environment. It also shows substantial attempt-level timing
variance, including two attempts above 20%. Those attempts are not removed or waived.
The rerun did not instrument a cause, so QA records the variance as observation only.

Absolute retained Linux timings and fresh Windows timings are not combined. Each
candidate/baseline pair used equivalent conditions within its own attempt.

The baseline compatibility adapter remains confined to the isolated historical baseline
tree. Current candidate construction uses explicit authorization scope and
`source_root`; existing contract tests fail closed when either is absent.

**Area H result: pass under the predeclared median-of-five rule.**

## S6. Failures, waivers, and residual risks

No A/G/H release-blocking failure remains, and no waiver was requested or granted.

Residual risks disclosed to the Product Owner:

1. Attempt-level timing variance is material. The retained range reaches 23.64%; the fresh
   Windows range reaches 40.94%, with two individual attempts above 20%. The predeclared
   median gate passes in both datasets, but future releases should continue paired raw
   evidence rather than rely on one comparison.
2. The evidence does not prove that scheduler or background load caused any high attempt.
3. The previously recorded Windows symlink-execution limitation remains outside the
   bounded correction and was not reopened without a regression signal.
4. Aggregate timing remains the previously accepted coarse side-channel and operational
   measurement debt.

## S7. Product Owner disposition

**Ready.**

Quality & Release recommends the exact executable candidate
`956c2ed1dd1144e836014b049a89c47e971818a0`, with evidence commit
`8fa5f18c09de1a0c9a79f33e0ba987f9de0e1083` and the digest pinned above, for Product
Owner go/no-go consideration. The earlier QR-031-01, QR-031-02, and QR-031-03 blockers are
closed by independent limited revalidation.

This recommendation does not merge, push, release, or authorize v0.4 work. The Product
Owner retains final authority.
