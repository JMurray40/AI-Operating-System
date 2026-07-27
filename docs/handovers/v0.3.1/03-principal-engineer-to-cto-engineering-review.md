# Handoff 03 — Principal Engineer to CTO (Engineering Review)

| Field | Value |
|---|---|
| Sender | Principal Engineer / Claude |
| Receiver | Chief Architect / CTO |
| Milestone | v0.3.1 — Query Trust Contracts |
| Date | 2026-07-27 |
| Status | Ready for architecture fitness/conformance review |
| Repository | `JMurray40/AI-Operating-System` |
| Branch | `feature/v0.3.1-query-trust-contracts` |
| Exact code baseline | `main` @ `ce0dc35853008e6b83c3c6fdfd0b8650738bee3d` |
| Governance base (branch point) | `a6c89c5be8ce78a4d9d6359a62c94aa83a84d513` (docs-only; verified descends from baseline) |
| Commits (this milestone) | `b512a1a` feat · `38d944c` test · `6ff478c` docs · this handoff commit (see `git log`) |
| Merged / pushed | **No** (branch left for review) |

## 1. Preconditions verified before implementation

Branch `feature/v0.3.1-query-trust-contracts`; `HEAD` = supplied governance SHA `a6c89c5`;
`a6c89c5` descends from baseline `ce0dc35`; worktree clean; accepted artifacts + validated
prompt present; the governance commit is documentation-only and contains no conversation
implementation. Baseline was green (124 tests) before any change.

## 2. Implemented scope (R1–R7)

- **R1 Relevance vs answer confidence (ADR-0014):** `ScoredNote.confidence` →
  `relative_relevance` across ranking, citations, trace, CLI, and JSON. No ranking output is
  called "confidence". No numeric answer confidence is emitted; `QueryAnswer.answer_confidence`
  is reserved and always `null`. Text uses "relative relevance".
- **R2 Context budget:** `QueryContextBuilder` enforces `0 <= total_tokens <= token_budget`;
  negative budget raises at construction; zero budget is empty; deterministic per-chunk
  separator counted; oversized chunks truncated to remaining allowance or omitted with a
  typed reason; no fictional one-token minimum. Runtime `assert` guards the invariant.
- **R3 Passage citations (ADR-0016):** `jarvis_core.query.passages` produces a deterministic
  locator (heading path + 1-based inclusive line range) and bounded excerpt, and validates
  (fingerprint match, in-range locator, excerpt-in-passage, heading resolves). Parser retains
  exact-source provenance additively (see §11 design decision 1).
- **R4 Authorization before candidates/graph (ADR-0015):** immutable `AuthorizationScope`
  (`jarvis_core.policy`); `build_authorized_view` filters before the index/graph are built;
  fail-closed on unknown/missing workspace or sensitivity; excluded identities/content never
  reach candidates, ranking, graph, context, citations, conflicts, errors, or trace — only an
  aggregate `excluded_count`.
- **R5 Identity and revision (ADR-0017):** `jarvis_core.identity` — workspace-namespaced
  `source_id` (`explicit` vs `path_derived`), `source_fingerprint` = SHA-256 of exact bytes;
  identity separate from revision; duplicate explicit IDs raise `DuplicateIdentityError`.
- **R6 Versioned results/trace:** `contract_version: jarvis.query.v0.3.1` on results,
  citations, context, and trace; distinct `index_version`. Trace adds request id, workspace
  fingerprint, safe authorization summary, and aggregate excluded count. Single-release legacy
  `confidence` compatibility reader in `jarvis_core.query.compat`.
- **R7 Roadmap/milestone docs:** Query Trust Contracts reference states v0.3 = query engine,
  v0.3.1 = trust hardening, Project Resume = v0.4, conversation = v0.5. No chat/conversation
  code or commit is in the branch diff.

## 3. Deferred / excluded (as required by the brief)

No chat, streaming, real providers, embeddings, vector DBs, persisted indexes, watchers,
durable/proposed memory, vault writes/migrations, plugins, MCP, agents, Project Resume, or
v0.5 conversation work. The parked conversation worktree was not switched, merged, rebased,
stashed, reset, staged, or modified.

## 4. Requirement → test mapping (exact names)

| Req | Test file :: test |
|---|---|
| R1 | `tests/unit/test_ranking.py::test_relative_relevance_is_relative_to_top`; `tests/integration/test_versioned_contract.py::test_answer_carries_contract_version_and_no_confidence`, `::test_trace_has_versioned_fields` |
| R2 | `tests/unit/test_context_budget.py::{test_negative_budget_fails_at_construction,test_zero_budget_is_empty,test_budget_invariant_property_loop,test_oversized_first_note_truncated,test_context_is_deterministic}` |
| R3 | `tests/unit/test_passages.py::{test_nested_heading_path,test_single_heading_note_path,test_validate_ok_and_stale,test_validate_bad_range_and_excerpt_mismatch,test_crlf_and_lf_fingerprints_differ_but_locate}`; `tests/integration/test_citations_resolve.py::{test_ranked_citation_resolves_to_exact_source,test_changed_bytes_make_citation_stale}` |
| R4 | `tests/integration/test_authorization.py::{test_restricted_note_excluded_under_internal_ceiling,test_unknown_sensitivity_note_excluded,test_excluded_term_yields_no_results,test_excluded_identity_not_disclosed_in_answer_or_trace,test_restricted_neighbor_not_expanded_into_graph,test_allow_all_includes_restricted,test_authorization_is_deterministic}`; `tests/unit/test_policy.py::*` |
| R5 | `tests/unit/test_identity.py::*`; `tests/integration/test_authorization.py::test_duplicate_explicit_id_fails_closed` |
| R6 | `tests/integration/test_versioned_contract.py::{test_answer_carries_contract_version_and_no_confidence,test_trace_has_versioned_fields,test_citation_shape}`; `tests/unit/test_compat.py::*` |
| R7 | `docs/software/QUERY_TRUST_CONTRACTS.md`; branch diff contains no conversation code |
| Read-only | `tests/integration/test_readonly_v031.py::test_full_query_path_does_not_modify_vault`; `tests/integration/test_readonly_safety.py` |
| Determinism | `tests/integration/test_authorization.py::test_authorization_is_deterministic`; `tests/unit/test_context_budget.py::test_context_is_deterministic` |

## 5. Changed contracts (old → new)

| Old (v0.3) | v0.3.1 | Rule |
|---|---|---|
| `confidence` (ranked results/citations) | `relative_relevance` | new writers emit only the new name |
| `confidence` (trace) | `relative_relevance` | never reinterpreted as answer confidence |
| unversioned payloads | `contract_version: jarvis.query.v0.3.1` (+ distinct `index_version`) | all affected outputs versioned |
| note-level citation | passage+revision citation (locator, fingerprint, excerpt) | material claims need a passage |
| implicit unrestricted query | explicit `AuthorizationScope` / `local_allow_all` | missing scope fails closed |

Compatibility: `jarvis_core.query.compat.read_legacy_result/read_legacy_citation` map legacy
`confidence` → `relative_relevance` only (one release; removal target v0.4). Writers emit new
names only.

## 6. Commands and results (worktree, Python 3.10.12)

- `python -m pytest -q` → **163 passed** (124 prior + 39 new).
- `ruff check src tests scripts` → **All checks passed**.
- `mypy` (config `pyproject.toml`) → **Success: no issues found in 52 source files**
  (run with cache on local disk; the FUSE-mounted `.mypy_cache` triggers a sqlite `disk I/O
  error` — environmental, not a code issue).
- `git diff --check` → clean (exit 0).

## 7. Benchmark

Environment: Linux sandbox (x86-64), Python 3.10.12, single process; synthetic chained
vaults; `python scripts/benchmark_query.py --sizes 100,500,1000 --runs 10` (10 measured runs
+ 1 warm-up). Timing is nondeterministic; the shared sandbox shows run-to-run variance.

Total query (ms):

| notes | p50 | p95 | p99 |
|---|---|---|---|
| 100 | 3.4 | 4.0 | 4.0 |
| 500 | 19.3 | 31.1 | 31.1 |
| 1000 | 30.7 | 35.7 | 35.7 |

Per-stage @1000 (p50): authorized_view 1.6 · retrieval (incl. index+graph build) 23.7 ·
ranking 10.0 · context 0.5 · citation build+validate 0.2. Peak memory @1000: **6.1 MB**.
Authorization stress @1000 (500 excluded): total p50 16.5 / p95 22.2 ms.

Baseline (v0.3 at `ce0dc35`, same machine/env, extracted via `git archive`,
`benchmark_query.py --sizes 1000 --runs 10`): `total(query)` median **35.7 ms**.

Regression gate: v0.3.1 1,000-note total **p95 35.7 ms** vs v0.3 baseline **35.7 ms** →
**≈0% (within the ≤20% gate)**. Authorization + citation validation add negligible cost
(authorized_view ≈1.6 ms, citation ≈0.2 ms). Security filtering was not weakened to meet the
gate.

## 8. Unchanged-vault (read-only) evidence

`tests/integration/test_readonly_v031.py` snapshots the fixture vault (per-file SHA-256, size,
mtime), runs the full CLI + engine + citation-validation path (which re-reads source bytes),
re-snapshots, and asserts byte-, file-set-, and metadata-identical. The repository opens files
read-only; no write handle exists; benchmark data is created only in isolated temp dirs.

## 9. Security / non-disclosure analysis

Authorization is structural (pre-index/pre-graph), not post-retrieval redaction. A restricted
note that is a one-hop neighbour of an authorized note is proven absent from candidates,
ranking, graph expansion, context, citations, and trace; a term unique to an excluded note
returns nothing and its identity/content never appear in serialized answer or trace (only an
aggregate `excluded_count`). Unknown/missing sensitivity and duplicate explicit IDs fail
closed. Fingerprints are SHA-256 integrity markers (no content/secrets); request ids are
opaque. Excerpts inherit source authorization (only authorized notes are cited). All processing
is local and network-free. Residual: aggregate timing is not constant-time; no source-identifying
timing detail is emitted (recorded risk).

## 10. Documentation changes

`docs/software/QUERY_TRUST_CONTRACTS.md` (new); `CHANGELOG.md`; `docs/adr/README.md`
(ADR-0014..0017 rows); `docs/software/CLI_USAGE.md`, `QUERYING.md`, `TESTING.md` notes.
Accepted ADRs were not rewritten.

## 11. Design decisions recorded (per Chief-of-Staff disposition)

1. **Parser line/heading provenance is additive.** The repository reads exact bytes (for the
   fingerprint), decodes text for parsing, and computes `body_start_line` from the text/body
   offset; `passages.py` derives headings/line ranges from the stored source text. No change
   was made to `split_frontmatter` or inline parsing semantics. Stop condition (escalate if
   exact provenance requires changing canonical parsing) was **not** triggered. Tests:
   `test_passages.py`, `test_citations_resolve.py`, CRLF fixture in `build_trust_vault`.
2. **Deterministic context accounting.** Each serialized excerpt is charged its word-count
   token estimate; a fixed `SEPARATOR_TOKENS=1` is charged between chunks; truncation uses the
   remaining allowance. The hard invariant `0 <= total_tokens <= token_budget` holds for every
   budget (property loop 0–39) with no fictional minimum. Stop condition (escalate if
   accounting cannot satisfy the invariant) was **not** triggered. Tests: `test_context_budget.py`.

## 12. Tradeoffs, technical debt, deviations, unresolved defects

- **Authorization builds a per-request authorized view** (re-indexes the authorized subset).
  Accepted for v0.3.1 scale (gate passes, 6.1 MB @1000); a shared projection with a scoped
  view is a future optimization (no persistence added, per the risk table).
- **Excerpt/passage selection** cites the section containing the first evidence term with a
  bounded window; deterministic and validated, but heuristic in which passage it chooses.
  Documented in `QUERY_TRUST_CONTRACTS.md`.
- **`ContextPackage` versioning** was added via a literal `contract_version` string in
  `to_dict()`; acceptable but could import the constant once the module graph allows.
- No unresolved defects. No accepted ADR was changed. No new trust boundary beyond the
  ADR-mandated `AuthorizationScope`.

## 13. Definition of Done

All R1–R7 + matrix cases pass; all prior supported tests pass; ruff + mypy pass; benchmark
meets the 1,000-note p95 gate; unchanged-vault evidence passes; outputs versioned and
compatibility documented; security/non-disclosure tests pass; documentation updated; logical
commits on `feature/v0.3.1-query-trust-contracts`; **not merged, not pushed**; escalations:
none required (both surfaced design decisions were pre-dispositioned by the Chief of Staff and
recorded here).

## Exit statement

**Ready for CTO architecture fitness/conformance review.** Recommended next step: CTO reviews
this evidence against ADR-0012/0014–0017 and issues the architecture disposition and
architect-to-QA handoff (`04-cto-to-quality-architecture-disposition.md`). The parked
conversation candidate remains untouched and out of scope.

---

# SUPERSEDING REVISION — Rev 2 (remediation of CTO "Refactor first")

| Field | Value |
|---|---|
| Revision | 2 (supersedes Rev 1 above; Rev 1 retained for history) |
| Prior reviewed SHA | `62f2269245890b3f55925056c93e156c179d4b5b` |
| CTO disposition addressed | [04-cto-to-quality-architecture-disposition.md](04-cto-to-quality-architecture-disposition.md) — Refactor first |
| Correction base | `4285e28` (CTO return commit) |
| Remediation commits | `871a7cf` fix · `dea0733` test · this docs commit (see `git log`) |
| Correction diff range | `62f2269..HEAD` |
| Scope | AC-01, AC-02, AC-03, AC-04, AE-01 + duplicate-ID clarification only |
| Merged / pushed | **No** |

Only the five returned findings were addressed. All original exclusions remain in force; the
parked conversation worktree was not touched; no accepted ADR was rewritten; no chat,
streaming, provider, embedding, persistence, plugin, MCP, agent, automation, or write code was
added.

## Corrections and requirement → test mapping

**AC-01 — Explicit scope, fail closed.** `QueryEngine.__init__` now takes a required
keyword-only `scope` (no default, no `local_allow_all()` fallback); omitted scope raises
`TypeError`, explicit `None` raises `PolicyError`. All library callers/tests pass an explicit
scope; the CLI already did. `local_allow_all` remains an explicit factory only.
Tests: `tests/unit/test_policy.py::test_engine_requires_explicit_scope`.

**AC-02 — Path-boundary-safe prefixes.** `AuthorizationScope.__post_init__` canonicalizes and
validates `allowed_path_prefixes` (reject absolute, empty/blank, and `..` traversal;
lower-case + forward-slash to match identity rules). `permits` matches an exact path or a
descendant by complete path segments (`norm == p or norm.startswith(p + "/")`), so
`projects/alpha` no longer grants `projects/alpha-restricted`.
Tests: `tests/unit/test_policy.py::{test_path_prefix_rejects_absolute_empty_and_traversal,
test_path_prefix_segment_boundary_no_sibling_leak, test_path_prefix_slash_and_case_normalization}`.

**AC-03 — Claim-supporting citations.** `passages.locate` now finds the supporting passage on
the actual retrieval signal across the whole source (frontmatter/title/metadata as well as
body); returns an empty locator when evidence is absent or the source is empty.
`validate_against_text` verifies the full heading hierarchy encloses the locator (not
leaf-anywhere), verifies the locator range, and rejects empty excerpts. The engine validates
every citation before emitting it and **declines** citations with no supporting passage
(`_cite_scored`/`_cite_note` return `None`; declined citations are dropped). Additive parser
unchanged. Consequence: a project that mentions a term only via a linked note yields no
material citation for the project itself (its evidence lives in the neighbour) — recorded in
`test_projects_mentioning_via_linked_note`.
Tests: `tests/unit/test_passages_ac03.py::{test_metadata_title_match_cites_frontmatter,
test_duplicate_leaf_heading_requires_full_path, test_renamed_parent_invalidates_citation,
test_locator_moved_outside_section_invalid, test_empty_excerpt_rejected,
test_empty_source_declines, test_evidence_absent_declines}`; plus
`tests/integration/test_citations_resolve.py::*` and `tests/unit/test_passages.py::*`.

**AC-04 — Narrow legacy reader.** `compat.py` accepts only mapping shapes; validates the
legacy ranking value is a number in `[0,1]` or `None`; when both `confidence` and
`relative_relevance` are present it requires equality and always removes the old key, else
raises `LegacyContractError`; never maps to `answer_confidence`; nested citations validated.
One-release removal boundary retained.
Tests: `tests/unit/test_compat.py::{test_maps_confidence_to_relevance, test_both_keys_equal_drops_old,
test_both_keys_conflict_rejected, test_wrong_type_rejected, test_out_of_range_rejected,
test_non_mapping_rejected, test_nested_citations_mapped_and_bad_shape_rejected,
test_never_synthesizes_answer_confidence, test_none_value_allowed}`.

**AE-01 — Equivalent p95-to-p95 benchmark.** New `scripts/benchmark_regression.py` measures the
complete public `QueryEngine.run(query)` end-to-end on a prebuilt engine with identical
fixture, query, warm-up, run count, and percentile method for both versions (adaptive
construction: candidate requires a scope, baseline does not). Stage timings remain diagnostics
in `benchmark_query.py` (auth-stress scope fixed to a source-id allowlist).

Environment: Linux sandbox (x86-64), Python 3.10.12; synthetic 1,000-note vault; query
`"links"`; 3 warm-ups; 100 measured runs; nearest-rank percentiles; exact commands:
`PYTHONPATH=src:. python scripts/benchmark_regression.py --notes 1000 --runs 100`
(candidate) and the same script under `PYTHONPATH` of the v0.3 baseline extracted at
`ce0dc35` via `git archive`.

| Version | min | p50 | p95 | p99 | max |
|---|---|---|---|---|---|
| v0.3 baseline (`ce0dc35`) | 6.597 | 7.763 | 11.831 | 12.227 | 14.620 |
| v0.3.1 candidate | 7.258 | 8.213 | 12.259 | 13.241 | 13.286 |

Regression (p95→p95): (12.259 − 11.831) / 11.831 = **+3.6%**, within the ≤20% gate. A 50-run
repeat gave candidate p95 13.223 vs baseline 12.337 (+7.2%), also within gate. Security
filtering and citation validation were not weakened to meet the gate.

## Duplicate-ID validation vs query disclosure (clarification)

Documented in `docs/software/QUERY_TRUST_CONTRACTS.md`: whole-vault validation (validator/
health) flags duplicate IDs across all notes for the owner; request-scoped querying detects
duplicates **only within the authorized view**, raising `DuplicateIdentityError` before index/
graph construction, so an excluded source can never surface through a request-visible error,
count, or trace. Test: `tests/integration/test_authorization.py::test_duplicate_explicit_id_fails_closed`.

## Commands and results (Rev 2)

- `python -m pytest -q` → **180 passed** (was 163; +17 remediation tests).
- `ruff check src tests scripts` → **All checks passed**.
- `mypy` → **Success: no issues found in 52 source files** (cache on local disk; FUSE
  `.mypy_cache` sqlite `disk I/O error` is environmental).
- `git diff --check` → clean.
- Unchanged-vault evidence unchanged and still passing
  (`tests/integration/test_readonly_v031.py`).

## Deviations, debt, unresolved

- `projects_mentioning` now emits a material citation only for notes whose own text supports
  the term; graph-only mentions appear in prose without a (false) self-citation. This is the
  intended AC-03 consequence, not a regression.
- Recorded debt from Rev 1 stands (per-request authorized view; heuristic passage selection
  now validated; `ContextPackage` literal contract string). No new debt introduced. No
  unresolved defects.

## Exit statement (Rev 2)

**Ready for CTO re-review of the correction diff `62f2269..HEAD`.** AC-01–AC-04 and AE-01 are
corrected with adversarial tests and equivalent p95 evidence; the duplicate-ID design is
documented. QA remains blocked pending a superseding CTO architecture disposition. Branch not
merged, not pushed; parked conversation candidate untouched.
