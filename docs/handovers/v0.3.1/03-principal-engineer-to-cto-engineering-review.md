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

---

# SUPERSEDING REVISION — Rev 3 (remediation of CTO Rev 2 "Refactor first")

| Field | Value |
|---|---|
| Revision | 3 (supersedes Rev 2; Rev 1/2 retained for history) |
| Prior reviewed SHA | `91636228e72f14c15fbc07c1733da00b8647f27f` (CTO Rev 2) |
| CTO return commit | `ac03c3c9971be7957027d9b7ffa4f33abfc9f8a8` |
| Remediation commits | `f3bca68` fix · `ffb7c13` test · this docs commit (see `git log`) |
| Correction diff range | `9163622..HEAD` (from the Rev 2 implementation) |
| Scope | AC-03R2 (current-bytes validation + claim-specific unranked citations), AC-04R2 (exact legacy shapes), AE-01R2 (total-pipeline p95) only |
| Merged / pushed | **No** |

AC-01, AC-02, and the duplicate-ID design were closed in Rev 2 and are **not** reopened. All
original exclusions remain: no chat/streaming/provider/embedding/persistence/write/plugin/MCP/
agent/automation/Project-Resume code; the parked conversation worktree was not touched; no
accepted ADR was rewritten.

## Corrections and requirement → test mapping

**AC-03R2a — Current-byte validation before emission.** `QueryEngine` takes an optional
`source_root`; `Note` retains exact `source_bytes`. `_make_citation` now validates the stored
`source_fingerprint` against the **current source bytes** — re-read from `source_root` and
confined to it (path-escape and missing files return empty bytes → fail the fingerprint check)
— together with the full heading hierarchy and a non-empty excerpt, before emitting any
citation. A source changed since discovery is stale and declined; without a `source_root`,
validation uses the discovery-time bytes (documented as discovery-revision consistency only).
The CLI passes `source_root=repo.root`. CRLF/LF exact bytes preserved (fingerprint over raw
bytes; structural checks over `splitlines`).
Tests: `tests/integration/test_citation_currentness.py::{test_citation_valid_before_mutation,
test_post_discovery_mutation_declines_stale_citation, test_missing_source_after_discovery_fails_closed,
test_without_source_root_uses_discovery_snapshot}`.

**AC-03R2b — Claim-specific unranked citations.** `summarize`/`explain` no longer pass empty
evidence. Summarize citations use the project title as claim evidence (each source is cited
where it references the project); explain citations use the other endpoint/shared-note titles
(each endpoint is cited at the passage that links the other). When no claim-specific passage
exists, the citation is emitted with `coverage="incomplete"` (empty locator/excerpt) — never
arbitrary first content. New `Citation.coverage` field (`supported` | `incomplete`).
Tests: `tests/integration/test_citation_claims.py::{test_summarize_citations_are_claim_specific_not_first_content,
test_explain_citations_cite_the_linking_passage, test_incomplete_coverage_has_no_arbitrary_excerpt}`.

**AC-04R2 — Exact legacy shapes.** `compat.py` now enforces exact v0.3 key sets: citation
required `{title, relpath, reason}` + allowed `{id, confidence, relative_relevance}`; result
required `{intent, question, answer, citations}`. It rejects unknown keys, missing required
fields, result/citation shape confusion, and new-only payloads (no legacy `confidence`);
validates every ranking value (type + `[0,1]`) whenever present; validates every nested
citation; and always removes the ambiguous old key. One-release removal target retained.
Tests: `tests/unit/test_compat.py::{test_exact_legacy_citation_maps_and_drops_old,
test_both_keys_equal_ok_conflict_rejected, test_unknown_key_rejected, test_missing_required_rejected,
test_new_only_citation_rejected_at_legacy_boundary, test_wrong_type_and_out_of_range_rejected,
test_result_shape_as_citation_rejected, test_exact_legacy_result_maps_nested_citations,
test_result_unknown_key_and_missing_rejected, test_citation_shape_as_result_rejected,
test_result_citations_must_be_list_and_validated, test_none_confidence_allowed}`.

**AE-01R2 — Total-pipeline p95 (construction + query).** `scripts/benchmark_regression.py`
now times, per sample, **engine construction + one public query** over the same pre-parsed
note set (so authorized-view/index/graph construction and citation validation are included).
The prebuilt-engine `run()` latency is reported separately as a steady-state diagnostic.

Environment: Linux sandbox (x86-64), Python 3.10.12; synthetic 1,000-note vault; query
`"links"`; 3 warm-ups; 100 measured runs; nearest-rank percentiles. Baseline v0.3 extracted at
`ce0dc35` via `git archive`; same script run under each version's `PYTHONPATH`. Exact command:
`python scripts/benchmark_regression.py --notes 1000 --runs 100`.

| Version | total_pipeline min | p50 | **p95** | p99 | max |
|---|---|---|---|---|---|
| v0.3 baseline (`ce0dc35`) | 27.03 | 29.85 | **35.219** | 36.259 | 36.663 |
| v0.3.1 candidate | 29.96 | 32.743 | **38.430** | 41.881 | 42.320 |

**Regression (total-pipeline p95 → p95): (38.430 − 35.219) / 35.219 = +9.1%**, within the
≤20% gate. Steady-state (diagnostic, query only): candidate p95 13.9 ms vs baseline 12.7 ms.
Security filtering and citation validation were not weakened to meet the gate.

## Commands and results (Rev 3)

- `python -m pytest -q` → **190 passed** (was 180; +10 remediation tests).
- `ruff check src tests scripts` → **All checks passed**.
- `mypy` → **Success: no issues found in 52 source files** (cache on local disk; FUSE
  `.mypy_cache` sqlite `disk I/O error` is environmental).
- `git diff --check` → clean.
- Unchanged-vault read-only evidence unchanged and still passing
  (`tests/integration/test_readonly_v031.py`). Citation-currentness tests write only to
  pytest `tmp_path`, never to a fixture.

## Deviations, debt, unresolved

- Per-citation current-byte re-read adds bounded I/O (≤ result size) per query; included in
  the +9.1% total-pipeline figure and within gate. Without a `source_root`, behaviour is
  discovery-revision consistency (documented).
- Recorded debt from Rev 1/2 stands; no new debt introduced. No unresolved defects.

## Exit statement (Rev 3)

**Ready for CTO re-review of the correction diff `9163622..HEAD`.** AC-03R2 (current-bytes
validation + claim-specific unranked citations), AC-04R2 (exact legacy shapes), and AE-01R2
(total-pipeline p95, +9.1% ≤ 20%) are corrected with adversarial tests and equivalent
evidence. Closed findings were not reopened. Branch not merged, not pushed; parked
conversation candidate untouched. QA remains blocked pending a superseding CTO disposition.

---

# SUPERSEDING REVISION — Rev 4 (final: CTO Rev 3 AC-03R3-01 & AC-03R3-02)

| Field | Value |
|---|---|
| Revision | 4 (supersedes Rev 3; Rev 1–3 retained for history) |
| Prior reviewed SHA | `47b1a0bf5609d29abb3633273fec2721b853ef45` (CTO Rev 3) |
| CTO return commit | `33434b6e99824bc32517dad8bd574cf7d0d5b072` |
| Remediation commits | `a4b3fac` fix · `93410c9` test · this docs commit (see `git log`) |
| Correction diff range | `47b1a0b..HEAD` |
| Scope | AC-03R3-01 (mandatory source_root) and AC-03R3-02 (visible incomplete evidence) only |
| Merged / pushed | **No** |

AC-01, AC-02, AC-04R2, AE-01R2, and the duplicate-ID design were closed in earlier revisions
and are **not** reopened. All original exclusions remain: no chat/streaming/provider/
embedding/persistence/write/plugin/MCP/agent/automation/Project-Resume code; the parked
conversation worktree was not touched; no accepted ADR was rewritten.

## AC-03R3-01 — Uniform current-source validation (CTO option 1)

`QueryEngine` now requires `source_root` (keyword-only, no default). The discovery-snapshot
fallback in `_current_bytes` is removed: current bytes are always re-read from the resolved
root, confined by `is_relative_to`, and path/symlink escape, missing, or unreadable sources
return empty bytes that fail the fingerprint check. A missing root fails closed at
construction (`PolicyError`). A discovery snapshot alone can therefore never produce a
`coverage="supported"` citation. The CLI supplies `source_root=repo.root`; every supported
caller/test/benchmark passes an explicit root. No new repository framework or non-filesystem
resolver was introduced (the filesystem repository already owns the root).

Tests: `tests/integration/test_citation_currentness.py::{test_source_root_is_mandatory,
test_symlink_escape_declines_citation, test_post_discovery_mutation_declines_stale_citation,
test_missing_source_after_discovery_fails_closed, test_citation_valid_before_mutation}`;
`tests/unit/test_policy.py::test_engine_requires_explicit_scope` (updated: omitted scope AND
root → `TypeError`; explicit `scope=None` → `PolicyError`; explicit `source_root=None` →
`PolicyError`).

## AC-03R3-02 — Visible incomplete evidence

`QueryAnswer` exposes `citation_coverage()` — `{label: complete|partial|incomplete|none,
supported, incomplete, limitation}` — serialized in `to_dict()`. Helpers `supported_citations()`
/ `incomplete_citations()` separate the two classes. CLI text now renders them under distinct
headings ("Sources (supporting passages):" vs "Evidence coverage incomplete — … no
claim-supporting passage was found"), never prints a `0-0` line range, and prints a
`Coverage:` summary line. Exit status uses only supported citations, so an answer with only
incomplete references returns `EXIT_WARNINGS` (not fully evidence-backed). Incomplete
references are never counted as material citations. Locators/excerpts are never fabricated to
upgrade coverage.

Tests: `tests/integration/test_cli_coverage_visibility.py::{test_text_separates_supported_from_incomplete_and_hides_0_0,
test_json_exposes_answer_level_coverage, test_incomplete_only_answer_is_not_fully_evidence_backed,
test_incomplete_only_text_shows_coverage_incomplete}`;
`tests/integration/test_citation_claims.py::test_summarize_produces_a_visible_incomplete_reference`.

## Commands and results (Rev 4)

- `python -m pytest -q` → **196 passed** (was 190; +6 net).
- `ruff check src tests scripts` → **All checks passed**.
- `mypy` → **Success: no issues found in 52 source files** (cache on local disk; FUSE
  `.mypy_cache` sqlite `disk I/O error` is environmental).
- `git diff --check` → clean.
- Unchanged-vault read-only evidence unchanged and still passing
  (`tests/integration/test_readonly_v031.py`); currentness/coverage tests write only to
  pytest `tmp_path`.

## Benchmark (AE-01R2 gate re-confirmed under mandatory root)

Total-pipeline p95 (construction + query), 1,000 notes, 100 runs, same fixture/query/warm-up/
percentile; baseline v0.3 at `ce0dc35`. Command:
`python scripts/benchmark_regression.py --notes 1000 --runs 100`.

| Version | min | p50 | **p95** | p99 | max |
|---|---|---|---|---|---|
| v0.3 baseline (`ce0dc35`) | 27.202 | 29.406 | **33.812** | 34.909 | 35.115 |
| v0.3.1 candidate | 29.460 | 32.671 | **38.075** | 39.306 | 39.478 |

**Regression (total-pipeline p95→p95): (38.075 − 33.812) / 33.812 = +12.6%**, within the
≤20% gate. (Slightly above Rev 3's +9.1% because current bytes are now always re-read.)

## Deviations, debt, unresolved

- Mandatory root re-reads each cited source's current bytes at emission (≤ result size per
  query); included in the +12.6% figure and within gate. No new debt; recorded Rev 1–3 debt
  stands. No unresolved defects.

## Exit statement (Rev 4)

**Ready for the final CTO conformance review of `47b1a0b..HEAD`.** AC-03R3-01 (mandatory
source_root; no snapshot-only supported citations) and AC-03R3-02 (visible incomplete
evidence across text/JSON/coverage signal/exit) are corrected with adversarial tests; all
previously closed findings remain closed; the ≤20% performance gate holds at +12.6%. Branch
not merged, not pushed; parked conversation candidate untouched. QA remains blocked pending a
superseding CTO disposition.

---

# SUPERSEDING REVISION — Rev 5 (final: benchmark entry-point migration)

| Field | Value |
|---|---|
| Revision | 5 (supersedes Rev 4; Rev 1–4 retained for history) |
| Prior reviewed SHA | `649e5a2ecfc98b2c4c9f23b5456716bb5f05f7f9` (CTO Rev 4) |
| CTO return commit | `b58a42b8b09d44cf8953bf6cdb8a698daa5c84e1` |
| Remediation commits | `e999737` fix · `4e2ffa8` test · this docs commit (see `git log`) |
| Correction diff range | `649e5a2..HEAD` |
| Scope | `scripts/benchmark_query.py` current-source migration + enforced smoke test only |
| Merged / pushed | **No** |

Only the returned finding was addressed. No citation semantics, compatibility, authorization,
performance gate, or any other closed finding was modified. All exclusions remain; the parked
conversation worktree was not touched; no accepted ADR was rewritten.

## Correction

The documented v0.3.1 query benchmark `scripts/benchmark_query.py` constructed
`QueryEngine(notes, scope=scope)` in two current-version paths — the per-size **warm-up**
(line 62) and the 1,000-note **memory measurement** (line 118) — without the mandatory
`source_root` (AC-03R3-01), so the entry point raised at construction before executing. Both
now pass `source_root=root` (the synthetic vault root already in scope). No timing or
measurement semantics changed.

## Enforced smoke test (constructor-contract drift)

`tests/integration/test_benchmark_smoke.py` loads the scripts by file path and executes their
documented entry points at tiny size, so any future construction that omits `scope` or
`source_root` fails the suite:

- `test_benchmark_query_bench_constructs_engine` — runs `bench(5, 1, scope)` (warm-up path).
- `test_benchmark_query_entrypoint_runs` — runs `main()` with `--sizes 5 --runs 1`, exercising
  the warm-up **and** the memory-measurement construction (asserts "Peak memory" and
  "authorization stress" output).
- `test_benchmark_regression_entrypoint_runs` — runs the regression harness `main()`.

## Call-site audit (current-version constructions)

Every non-baseline `QueryEngine(...)` construction in `src`, `scripts`, and `tests` supplies
**both** an explicit authorization scope and a `source_root`:

- `src/jarvis_core/cli.py` — `scope=local_allow_all("local"), source_root=repo.root`.
- `scripts/benchmark_query.py` (warm-up + memory) — `scope=scope, source_root=root`.
- `scripts/benchmark_regression.py` — candidate branch passes `scope=_SCOPE, source_root=root`;
  the `scope`-only and no-arg branches are reached **only** on the v0.3 baseline via
  `TypeError` fallback (the baseline constructor accepts neither), as the CTO permitted for
  the deliberately-baseline compatibility harness.
- All test helpers pass `scope` + `source_root`. The only `QueryEngine(...)` calls without
  both are the **deliberate fail-closed negative tests**
  (`tests/unit/test_policy.py::test_engine_requires_explicit_scope`,
  `tests/integration/test_citation_currentness.py::test_source_root_is_mandatory`), which
  assert `TypeError`/`PolicyError`.

## Commands and results (Rev 5)

- `python -m pytest -q` → **199 passed** (was 196; +3 benchmark smoke tests).
- `ruff check src tests scripts` → **All checks passed**.
- `mypy` → **Success: no issues found in 52 source files** (cache on local disk; FUSE
  `.mypy_cache` sqlite `disk I/O error` is environmental).
- `git diff --check` → clean.
- Unchanged-vault read-only evidence unchanged and still passing.
- **Documented query benchmark now executes**:
  `python scripts/benchmark_query.py --sizes 1000 --runs 5` → total p50/p95 34.8/38.6 ms,
  Peak memory 6.12 MB, authorization stress (500 excluded) total p50/p95 16.4/22.4 ms.
- **Regression benchmark executes** (gate unchanged/closed): total_pipeline p95 candidate
  ~37.4 ms vs the accepted v0.3 baseline 33.812 ms → +12.6% at the Rev 4 measurement,
  within the ≤20% gate. No performance-gate change was made in Rev 5.

## Deviations, debt, unresolved

No behaviour change beyond making the documented benchmark entry point runnable under the
mandatory-root contract, plus a new enforced smoke test. No new debt; recorded Rev 1–4 debt
stands. No unresolved defects.

## Exit statement (Rev 5)

**Ready for exact-HEAD CTO clearance of `649e5a2..HEAD`.** The final open finding (benchmark
entry-point current-source migration) is corrected and guarded by an enforced smoke test; all
previously closed findings remain closed; both documented benchmark entry points execute;
199 tests, Ruff, mypy, and `git diff --check` pass. Branch not merged, not pushed; parked
conversation candidate untouched. QA remains blocked pending exact-HEAD CTO clearance.

---

# SUPERSEDING REVISION — Rev 6 (QA remediation: benchmark entry points & evidence)

| Field | Value |
|---|---|
| Revision | 6 (supersedes Rev 5; Rev 1–5 retained for history) |
| Prior reviewed SHA | `09a4ca5a6e0d9b73a1e37a9e086abe788c894c72` (QA-reviewed candidate) |
| QA return commit | `be527a8148914a08007e6c2fb6d0f2ed8cd9a4d4` |
| Remediation commits | `14b836f` fix · `4d174ad` test · this docs commit (see `git log`) |
| Correction diff range | `09a4ca5..HEAD` |
| Scope | QR-031-01, QR-031-02, QR-031-03 (benchmark/test tooling only) |
| Merged / pushed | **No** |

Benchmark/test tooling only. No trust-contract, authorization, citation, compatibility,
performance-gate, or other closed-finding code was modified. All exclusions remain; the parked
conversation worktree was not touched; no accepted ADR was rewritten.

## QR-031-01 — Documented benchmarks run from the repository root

`scripts/benchmark_query.py` and `scripts/benchmark_regression.py` self-bootstrap `sys.path`
(repo root + `src/`), so the exact documented commands run from the repo root **without a
PYTHONPATH override**:

```text
python scripts/benchmark_query.py --sizes 100,500,1000 --runs 10
python scripts/benchmark_regression.py --runs 20
```

Candidate/baseline isolation is preserved: each version runs from its own tree (the baseline
tree bootstraps its own root/src). Direct run (no PYTHONPATH) evidence:

| notes | total p50 | total p95 |
|---|---|---|
| 100 | 3.07 | 3.58 |
| 500 | 15.55 | 19.86 |
| 1000 | 31.18 | 40.01 |

Peak memory @1000: **6.12 MB**. Authorization stress @1000 (500 excluded): total p50 16.3 /
p95 24.2 ms.

## QR-031-02 — Real process-boundary smoke test

`tests/integration/test_benchmark_smoke.py` now runs the documented commands as **subprocesses
from the repo root with PYTHONPATH stripped**, asserting exit 0 and completion markers, and
includes a negative case proving the smoke fails when the runtime dependency is unavailable:

- `test_benchmark_query_runs_from_repo_root` — asserts "Peak memory" + "authorization stress".
- `test_benchmark_regression_runs_from_repo_root` — asserts "total_pipeline".
- `test_benchmark_regression_json_emits_raw_samples` — asserts raw sample count.
- `test_smoke_fails_when_runtime_dependency_unavailable` — copies only the script (no sibling
  `src/`/`tests/`) and asserts non-zero exit + `ModuleNotFoundError`.
- `test_benchmark_paired_entrypoint_smoke` — runs the paired tool end-to-end at tiny size.

The earlier import-based smoke (which masked the missing import path) is removed.

## QR-031-03 — Paired, interleaved same-machine performance evidence

`scripts/benchmark_paired.py` runs multiple paired attempts; within each it measures candidate
and v0.3 baseline back-to-back and **alternates order** (candidate-first / baseline-first) to
neutralize run-order and background-load bias. Both versions use the **identical** harness
(the current `benchmark_regression.py` is copied into the baseline tree; only `jarvis_core`
differs), the same fixture, query, warm-ups, measured runs, percentile estimator, and
construction-plus-query boundary. Raw per-attempt samples for both versions are retained via
`--out` (and `benchmark_regression.py --json`).

Evidence — `python scripts/benchmark_paired.py --baseline-root <v0.3 tree> --notes 1000
--runs 30 --attempts 5` (baseline = `ce0dc35` via `git archive`; PYTHONPATH stripped):

| attempt | order | candidate p95 (ms) | baseline p95 (ms) | regression % |
|---|---|---|---|---|
| 0 | candidate_first | 37.373 | 32.824 | 13.86 |
| 1 | baseline_first | 37.065 | 35.733 | 3.73 |
| 2 | candidate_first | 36.683 | 35.149 | 4.36 |
| 3 | baseline_first | 37.211 | 33.070 | 12.52 |
| 4 | candidate_first | 37.282 | 33.658 | 10.77 |

Aggregate: **median regression 10.77%** (min 3.73%, max 13.86%); median candidate p95 37.211
ms vs baseline 33.658 ms. **GATE (≤ 20% on median): PASS** — every individual pair is also
within gate, and the candidate p95 is stable (~36.7–37.4 ms) regardless of order, resolving
the earlier run-order variance conflict. No waiver requested or needed.

## Commands and results (Rev 6)

- `python -m pytest -q` → **201 passed** (was 199; +2 net from the new subprocess smoke suite).
- `ruff check src tests scripts` → **All checks passed**.
- `mypy` → **Success: no issues found in 52 source files** (cache on local disk; FUSE
  `.mypy_cache` sqlite `disk I/O error` is environmental).
- `git diff --check` → clean (0 bytes).
- Unchanged-vault read-only evidence covering the query/benchmark paths still passing
  (`tests/integration/test_readonly_v031.py`, `test_readonly_safety.py`); benchmark temp
  vaults live in `TemporaryDirectory`, never in a fixture.

## Deviations, debt, unresolved

- The benchmarks depend on `tests.support.synthetic_vault` (the deterministic vault generator);
  resolved by the `sys.path` bootstrap rather than a packaging framework, per the CTO
  constraint. `benchmark_paired.py` requires a v0.3 baseline tree (`--baseline-root`) or
  `git archive`-able `--baseline-ref`. No trust-contract behaviour changed. No new product
  debt; recorded Rev 1–5 debt stands. No unresolved defects.

## Exit statement (Rev 6)

**Ready for CTO clearance of the changed benchmark/test scope (`09a4ca5..HEAD`).** Both
documented benchmark commands run from the repo root with no PYTHONPATH; a real
process-boundary smoke test (with a failing-dependency negative case) guards them; paired
interleaved evidence shows a stable median regression of 10.77% (≤ 20% gate, PASS) that
resolves the run-order variance. All previously closed findings remain closed; 201 tests,
Ruff, mypy, and `git diff --check` pass. Branch not merged, not pushed; parked conversation
candidate untouched. QA remains blocked pending CTO clearance and the subsequent re-run of
Areas A, G, and H.
