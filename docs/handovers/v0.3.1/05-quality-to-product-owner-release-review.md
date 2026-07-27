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

## 9. Final disposition

**Refactor first.**

Return exact HEAD `09a4ca5a6e0d9b73a1e37a9e086abe788c894c72` for the bounded corrections
and evidence described above. The Product Owner retains final authority, but this QA
record does not recommend merge or release of the frozen candidate.
