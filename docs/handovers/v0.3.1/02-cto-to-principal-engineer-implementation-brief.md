# Handoff 02 — CTO to Principal Engineer

| Field | Value |
|---|---|
| Sender | Chief Architect / CTO |
| Receiver | Principal Engineer / Claude |
| Milestone | v0.3.1 — Query Trust Contracts |
| Date | 2026-07-27 |
| Status | Ready for Chief of Staff validation; engineering remains blocked until validated |
| Repository | `JMurray40/AI-Operating-System` |
| Code base branch | `main` |
| Exact code base commit | `ce0dc35853008e6b83c3c6fdfd0b8650738bee3d` |
| Implementation branch point | Clean governance commit containing this validated brief and accepted artifacts; exact SHA supplied in the Chief of Staff prompt package |
| Required implementation branch | `feature/v0.3.1-query-trust-contracts` |
| Required engineering output | `docs/handovers/v0.3.1/03-principal-engineer-to-cto-engineering-review.md` |

## 1. Objective and architecture disposition

Implement v0.3.1 Query Trust Contracts only. Close Architecture Review Board conditions
C1 through C5 by making query relevance, context budgeting, authorization, citations,
source identity, revisions, result versioning, and trace behavior explicit and testable.

The architecture is approved for implementation under the accepted requirements and
ADR-0014 through ADR-0017. The implementation remains offline, local, deterministic, and
strictly read-only.

This release is infrastructure for trustworthy retrieval. It is not a conversational or
generated-answer release.

## 2. Engineering base and workspace preconditions

The exact code baseline is `main` at:

```text
ce0dc35853008e6b83c3c6fdfd0b8650738bee3d
```

The implementation branch must start from the clean, documentation-only governance commit
that contains this validated brief and its accepted inputs. That commit is a descendant of
the exact code baseline above and introduces no implementation changes. Because a file
cannot contain the hash of the commit that contains itself, the Chief of Staff prompt
package supplies and requires verification of the governance commit SHA.

The current shared worktree was observed on `feature/v0.4-conversation` at
`4b09050b76fd9a448af3ce91b4aa66963d23dad2` with substantial staged, modified, deleted,
and untracked state. That branch is the parked v0.5 conversation candidate and is not an
acceptable implementation base.

Before engineering begins, the Chief of Staff must provide a clean worktree rooted at the
exact `main` commit and make this validated brief and its accepted governing artifacts
available there. The Principal Engineer must:

1. verify `git rev-parse HEAD` equals the governance commit SHA in the validated Chief of
   Staff prompt package, and verify that commit descends from the exact code base commit;
2. verify the implementation branch is `feature/v0.3.1-query-trust-contracts`;
3. verify the worktree is clean before implementation;
4. stop if the accepted artifacts are missing or differ from those linked below;
5. not switch, merge, rebase, stash, reset, stage, or modify the parked conversation
   worktree.

The implementation branch must not contain commits from `feature/v0.4-conversation`.

## 3. Authoritative inputs

Apply these artifacts in governance precedence order:

1. [Product Owner architecture approval](01-product-owner-to-cto-architecture-approval.md)
2. [Governance](../../GOVERNANCE.md)
3. Accepted ADRs:
   - [ADR-0007 — Read-only default](../../adr/ADR-0007-Read-Only-Is-The-Default-Operating-Mode.md)
   - [ADR-0012 — Layered deterministic query pipeline](../../adr/ADR-0012-Query-Engine-Is-A-Layered-Deterministic-Pipeline.md)
   - [ADR-0014 — Relevance versus answer confidence](../../adr/ADR-0014-Retrieval-Relevance-Is-Separate-From-Answer-Confidence.md)
   - [ADR-0015 — Authorization precedes retrieval](../../adr/ADR-0015-Authorization-Precedes-Retrieval-And-Graph-Expansion.md)
   - [ADR-0016 — Passage/revision citations](../../adr/ADR-0016-Citations-Bind-Passages-To-Source-Revisions.md)
   - [ADR-0017 — Stable source identity](../../adr/ADR-0017-Stable-Source-Identity-Is-Separate-From-Location.md)
4. [v0.3.1 Query Trust Contracts Requirements](../../software/V0.3.1_QUERY_TRUST_CONTRACTS_REQUIREMENTS.md)
5. [AI Behavior Standard](../../AI_BEHAVIOR_STANDARD.md)
6. [Search Engine PRD](../../prd/SEARCH_ENGINE.md)
7. [v0.3 Architecture Review](../../reviews/arb/2026-07-27-v0.3-architecture-review.md)
8. [Ways of Working](../../WAYS_OF_WORKING.md)

The Product Owner has accepted v0.3.1, ADR-0014 through ADR-0017, Project Resume as v0.4,
and conversation as v0.5. No release-name decision remains open.

## 4. Required architecture and affected contracts

Preserve the layered pipeline from ADR-0012. Small supporting modules may be introduced,
but `QueryEngine` remains orchestration rather than becoming the owner of policy,
identity, passage extraction, and serialization logic.

Expected affected surfaces include:

- `src/jarvis_core/models/note.py`
- repository/parser code needed to retain exact source revision and passage provenance;
- `src/jarvis_core/query/ranking.py`
- `src/jarvis_core/query/results.py`
- `src/jarvis_core/query/context_builder.py`
- `src/jarvis_core/query/index.py`
- `src/jarvis_core/query/engine.py`
- `src/jarvis_core/query/trace.py`
- `src/jarvis_core/relationships/resolver.py`
- CLI structured and text renderers;
- query, parser, repository, relationship, CLI, determinism, scale, and read-only tests;
- `scripts/benchmark_query.py`.

The Engineer may choose precise module names within `jarvis_core.query` or a small
policy/identity package, but may not change the trust semantics below.

### 4.1 Contract version

Use one explicit v0.3.1 structured-contract identifier across affected results, citations,
contexts, and traces:

```text
jarvis.query.v0.3.1
```

The identifier must serialize as `contract_version`. The index projection/version must
remain a separate field named `index_version`; do not conflate it with the result contract.

### 4.2 Retrieval relevance

- Rename `ScoredNote.confidence` and citation/trace serialization derived from it to
  `relative_relevance`.
- Text output uses `relevance` or `relative relevance`, never `confidence`, for ranking.
- The value remains deterministic normalization within one result set.
- Do not emit numeric answer confidence.
- Do not create an alias that allows new code to keep treating retrieval relevance as
  answer confidence.

### 4.3 Authorization scope

Introduce an immutable `AuthorizationScope` required by every v0.3.1 query entry point.
It contains:

- `workspace_id`;
- allowed source IDs and/or allowed relative-path prefixes;
- maximum sensitivity;
- optional allowed note types;
- `request_id`;
- a policy identifier/version suitable for safe tracing.

Provide an explicit local allow-all factory for existing CLI behavior. “Allow all” still
requires a non-empty workspace ID and a declared sensitivity ceiling; absence of scope
must not silently mean unrestricted access.

Sensitivity ordering and unknown-label behavior must be centralized and deterministic.
Unknown, invalid, or absent request scope fails closed with a typed policy error. Notes
with unknown sensitivity must not be treated as unrestricted.

Filter before request-visible index candidate generation and before graph expansion.
Constructing a request-scoped authorized index/view is acceptable. Post-retrieval
redaction alone is prohibited.

### 4.4 Source identity and revision

Use the validated frontmatter `id` as the explicit canonical identity when present.
Namespace every identity by `workspace_id`.

When `id` is absent, derive a deterministic fallback from normalized workspace ID and
normalized relative path. Mark the identity kind as `explicit` or `path_derived`; do not
pretend the fallback survives a rename.

Use SHA-256 of the exact source file bytes as `source_fingerprint`. Do not hash normalized
body text. Source identity and source fingerprint are separate fields.

Duplicate explicit IDs within one workspace are typed validation failures. They must not
be silently merged, overwritten, or resolved by path order.

### 4.5 Passage locator and citation

For v0.3.1, use a deterministic locator containing:

- heading path, empty only when the passage precedes the first heading;
- 1-based inclusive source `line_start`;
- 1-based inclusive source `line_end`.

The citation contains:

- `source_id`;
- `source_identity_kind`;
- `title`;
- `relpath`;
- `source_fingerprint`;
- locator;
- bounded excerpt;
- `relative_relevance` when retrieval-ranked;
- retrieval reason.

The parser/repository must preserve enough exact-source provenance to resolve this
locator against the fingerprint. Citation validation must prove:

1. the current bytes match `source_fingerprint`;
2. the locator is within the cited source;
3. the excerpt is derived from the located passage;
4. the passage supports the selected retrieval evidence.

Excerpt bounding must be deterministic and documented. Truncation must not invent,
reorder, or normalize words in a way that prevents validation.

### 4.6 Context budget

Reject negative token budgets at construction/config validation. A zero budget returns no
included chunks.

For positive budgets:

- `0 <= total_tokens <= token_budget` is invariant;
- every serialized excerpt and deterministic separator/wrapper charged by the context
  contract counts toward the total;
- an oversized first or later source is deterministically truncated to the remaining
  allowance when a valid non-empty passage can be produced, otherwise omitted;
- included chunks must never be assigned a fictional minimum of one token when no token
  can be emitted;
- every truncation/omission has a typed reason;
- trace reports only authorized included/excluded source identities.

Use the existing deterministic model-independent estimator for selection unless changing
it is necessary to enforce the invariant. Provider-specific tokenization is out of scope.

### 4.7 Trace

Trace must include:

- `contract_version`;
- `request_id`;
- workspace/vault fingerprint;
- `index_version`;
- safe authorization decision summary and policy version;
- provider and prompt version when applicable, otherwise explicit `none`;
- context budget, used tokens, truncations, omissions, and reasons;
- rankings labeled `relative_relevance`.

Excluded sources must not be identified, quoted, counted by sensitive category, or exposed
through candidate lists, graph channels, conflicts, errors, or trace. A single aggregate
excluded count is permitted.

Timing data may remain nondeterministic, but deterministic structured fields must remain
byte-identical for identical source snapshot, scope, request, and configuration.

## 5. Compatibility and migration plan

This is an intentional pre-1.0 contract correction:

| Old surface | v0.3.1 surface | Rule |
|---|---|---|
| `confidence` on ranked results/citations | `relative_relevance` | New writers emit only the new name |
| `confidence` in trace JSON/text | `relative_relevance` / `relevance` | Never reinterpret as answer confidence |
| unversioned query payload | `contract_version: jarvis.query.v0.3.1` | Version all affected outputs |
| note-level citation | passage-and-revision citation | No generated/material claim uses legacy citation |
| implicit unrestricted query | explicit local allow-all scope | Missing scope fails closed |

If an existing deserialization boundary accepts stored v0.3 payloads, it may accept legacy
`confidence` for one release and map it only to `relative_relevance`. Do not invent durable
storage or a broad compatibility framework solely for this release. Document the removal
target as no earlier than the next minor release.

Existing supported v0.1–v0.3 CLI commands must continue to work by constructing an explicit
local scope. JSON snapshots may change only as required by the accepted v0.3.1 contract.

No vault migration and no source write are permitted. Explicit IDs missing from notes
continue through the path-derived fallback.

## 6. Requirement-to-acceptance evidence matrix

| Req. | Acceptance criteria | Minimum automated evidence |
|---|---|---|
| R1 | No affected public, JSON, trace, or text output calls ranking “confidence”; no numeric answer confidence | Unit contract tests, JSON snapshots, CLI text tests, repository-wide semantic search reviewed in handoff |
| R2 | For all tested budgets, `0 <= total_tokens <= token_budget`; zero is empty; negative fails; oversized first/later chunks truncate or omit deterministically | Boundary tests at `-1, 0, 1`, exact fit, one under/over, oversized first and later; property-style range loop; deterministic snapshots |
| R3 | Citation resolves to exact source bytes, heading path, inclusive lines, and excerpt; changed bytes make it stale | Parser/locator unit tests; heading/nested-heading/no-heading cases; CRLF/LF fixture; stale fingerprint, bad range, excerpt mismatch, empty source |
| R4 | Unauthorized sources cannot influence index candidates, rank, graph, context, citations, conflicts, trace, or errors | Positive/negative scope tests; sensitivity boundary; unknown label; missing workspace/scope; restricted seed and one-hop neighbor; term unique to excluded note; non-disclosure snapshots |
| R5 | Explicit IDs survive path/title changes logically; fallback is workspace/path-scoped; fingerprint tracks bytes; duplicates fail | Identity unit tests; workspace collision tests; rename fixtures; byte-change/unchanged tests; duplicate-ID integration test |
| R6 | All affected structured outputs carry the contract version and new field names; supported legacy reader maps only to relevance | New-writer snapshots; legacy-reader fixture if reader exists; deterministic serialization; old-key absence assertions |
| R7 | Release docs say Query Engine v0.3, trust contracts v0.3.1, Project Resume v0.4, conversation v0.5 | Documentation assertions/review checklist; no chat code or conversation commit in branch diff |
| Cross-cutting | Vault remains byte-, file-set-, and metadata-identical; existing behavior regresses only where contract intentionally changed | Full regression suite; before/after SHA-256 and path inventory; stat metadata comparison; `git diff --check` |

Tests must include positive, negative, boundary, compatibility, security, and regression
cases. Every matrix row must map to named test files and test cases in the engineering
handoff.

## 7. Performance and scale gates

Use synthetic vaults of 100, 500, and 1,000 notes. Execute at least 10 measured query runs
per size after one unmeasured warm-up and report p50, p95, and p99 for:

- authorized index/view construction;
- candidate retrieval;
- ranking;
- graph/context expansion;
- citation construction and validation;
- total query pipeline.

Compare the 1,000-note p95 total query time against the v0.3 baseline measured by running
the benchmark at the exact base commit on the same machine and Python environment.
v0.3.1 must not regress by more than 20%.

Also report:

- peak memory at 1,000 notes;
- an authorization stress case where at least half the notes are excluded;
- a graph case with restricted one-hop neighbors;
- benchmark hardware, OS, Python version, run count, and raw command.

Do not weaken security filtering to meet the performance target. Escalate a measured
regression rather than silently changing the gate.

## 8. Read-only and security invariants

The implementation must prove:

1. no write-capable repository or vault handle is introduced;
2. no query, validation, citation, benchmark, or failure path changes vault files;
3. authorization is applied before candidates and graph traversal;
4. excluded identity/content cannot leak through results, traces, conflicts, counts beyond
   the permitted aggregate, exception text, or timing-specific debug detail;
5. raw file paths are normalized and cannot escape the configured vault;
6. citation excerpts inherit the source authorization/sensitivity decision;
7. fingerprints and request IDs contain no source content or secrets;
8. duplicate IDs and unknown policy data fail closed;
9. all processing remains local and network-free.

For unchanged-vault evidence, capture before and after:

- sorted relative-path inventory;
- SHA-256 for every source file;
- file size;
- last-write timestamp.

Run the complete query/CLI/benchmark acceptance path between snapshots and assert exact
equality. Temporary benchmark data must be outside the source fixture/vault or automatically
isolated and removed.

## 9. Testing and required checks

At minimum, report the exact commands and results for:

```powershell
python -m pytest
python -m ruff check src tests scripts
python -m mypy src
python scripts/benchmark_query.py --sizes 100,500,1000 --runs 10
git diff --check
```

If the project environment exposes the tools through a different interpreter, report the
equivalent exact commands. Do not omit failures or rerun only selected passing tests in the
final evidence.

Required test coverage includes:

- every row of the evidence matrix;
- CLI `ask`, `search`, `summarize`, and `explain` in text and JSON where applicable;
- deterministic repeated queries;
- authorization across direct retrieval and graph expansion;
- citation validation failure behavior;
- context-budget boundaries;
- legacy compatibility boundary, if one exists;
- unchanged-vault integration;
- 100/500/1,000-note scale.

No arbitrary line-coverage percentage is imposed. Behavioral coverage of every trust
boundary is mandatory.

## 10. Documentation requirements

Engineering must update or create only documentation needed to describe implemented
behavior:

- query architecture and public contract reference;
- CLI usage affected by scope, trace, citations, and relevance terminology;
- JSON/compatibility migration notes;
- benchmark usage/output definition;
- changelog entry for v0.3.1;
- ADR index entries for accepted ADR-0014 through ADR-0017 if not already present on the
  implementation branch;
- the required engineering handoff.

Do not rewrite accepted ADR decisions. Record implementation tradeoffs and deviations in
the engineering handoff. Flag broader roadmap drift for the Historian/Librarian.

## 11. Explicit exclusions and forbidden work

Do not implement, import, cherry-pick, merge, or expose:

- chat or multi-turn conversation;
- streaming or progressive-rendering features;
- any code from the parked conversation branch;
- real AI providers or network access;
- embeddings, vector databases, persisted indexes, or background watchers;
- durable conversation state or proposed memory;
- vault writes or migrations;
- plugins, MCP, tools, agents, automation, or background services;
- Project Resume feature work;
- v0.5 conversation rework;
- unrelated refactors or public frameworks.

The parked conversation candidate remains untouched. After v0.3.1 is approved and merged,
it will be separately rebased/reconciled as v0.5, and must adopt the new trust contracts
before a fresh architecture and Quality review. That future reconciliation is not part of
this implementation.

## 12. Known risks and mandatory escalation points

| Risk | Required handling |
|---|---|
| Exact line provenance may require parser contract changes | Keep the change minimal and provider-neutral; escalate if canonical parsing semantics would change |
| Authorization filtering may duplicate indexes per request | Accept for v0.3.1 scale unless the performance gate fails; do not add persistence |
| Timing can become a side channel | Avoid source-identifying trace detail; record residual aggregate-timing risk |
| CRLF/LF and encoding affect fingerprints/lines | Fingerprint exact bytes and test both newline styles; do not normalize before hashing |
| Explicit ID collisions exist in real vaults | Fail closed and report validation; do not auto-repair |
| CLI compatibility conflicts with mandatory scope | Use an explicit local allow-all scope, never an implicit bypass |
| Legacy query consumers depend on `confidence` | Apply the accepted breaking-change plan; do not preserve ambiguous writer output |
| Context wrapper accounting is underspecified by existing code | Document the selected deterministic accounting rule and test it; escalate if provider prompt accounting is required |

Stop and escalate in writing if implementation requires changing an accepted ADR, weakens
fail-closed behavior, introduces a new trust boundary, cannot meet the performance gate,
or reveals a product decision not fixed by this brief. Continue only with separable,
uncontested work.

## 13. Definition of Done

v0.3.1 is engineering-complete only when:

- all R1–R7 requirements and matrix cases pass;
- all previous supported tests pass;
- Ruff and mypy pass;
- the benchmark meets the 1,000-note p95 regression gate;
- unchanged-vault evidence passes;
- outputs are versioned and compatibility behavior is documented;
- security/non-disclosure tests pass;
- required documentation is updated;
- changes are organized into logical commits on
  `feature/v0.3.1-query-trust-contracts`;
- work is not merged and not pushed by the Principal Engineer;
- every escalation is resolved and recorded;
- the engineering handoff is complete at the required path.

## 14. Required engineering handoff

Produce:

```text
docs/handovers/v0.3.1/03-principal-engineer-to-cto-engineering-review.md
```

It must include:

- repository, branch, exact base SHA, final implementation SHA, and commit list;
- implemented and deferred scope;
- requirement-to-test mapping with exact test names;
- changed contracts and old-to-new compatibility table;
- commands and complete results;
- benchmark environment, baseline, raw summary, p50/p95/p99, regression percentage, and
  peak memory;
- unchanged-vault method and result;
- security/non-disclosure analysis;
- tradeoffs, technical debt, deviations, and unresolved defects;
- documentation changes;
- confirmation that the branch was neither merged nor pushed;
- recommended next step.

## 15. Unresolved decisions

No Product Owner decision currently blocks the defined v0.3.1 scope. Engineering remains
procedurally blocked until the Chief of Staff validates this brief, provides a clean
worktree at the pinned base, and issues the Principal Engineer prompt package.

Any newly discovered architectural ambiguity belongs to the CTO; any material scope,
release, or risk-acceptance decision belongs to Jason.

## Exit statement

**Ready for Chief of Staff validation.** Once validated and provided on a clean
documentation-only governance commit descended from the exact `main` code baseline
`ce0dc35853008e6b83c3c6fdfd0b8650738bee3d`, this brief is implementation-ready for the
Principal Engineer. The parked conversation candidate remains unmerged, unreleased, and
out of scope.
