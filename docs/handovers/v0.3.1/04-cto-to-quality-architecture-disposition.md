# Handoff 04 — CTO to Quality & Release

| Field | Value |
|---|---|
| Sender | Chief Architect / CTO |
| Intended receiver | Quality & Release Manager |
| Milestone | v0.3.1 — Query Trust Contracts |
| Review date | 2026-07-27 |
| Review type | Independent architecture-conformance review |
| Repository | `JMurray40/AI-Operating-System` |
| Reviewed branch | `feature/v0.3.1-query-trust-contracts` |
| Reviewed HEAD | `62f2269245890b3f55925056c93e156c179d4b5b` |
| Reviewed diff | `a6c89c5be8ce78a4d9d6359a62c94aa83a84d513..62f2269245890b3f55925056c93e156c179d4b5b` |
| Worktree | `C:\Users\jmurr\Projects\AI-Operating-System\.worktrees\v0.3.1-engineering` |
| Initial worktree state | Clean |
| Architecture disposition | **Refactor first** |
| QA authorization | Withheld pending engineering correction and CTO re-review |

## 1. Executive disposition

**Architecture disposition: Refactor first.**

The candidate is directionally aligned with the accepted v0.3.1 architecture. It
introduces a structurally authorized view before index and graph construction, separates
relative retrieval relevance from answer confidence, preserves the ADR-0012 layered
pipeline, adds exact-byte revision fingerprints and additive source provenance, enforces
the arithmetic context-budget invariant, versions affected outputs, and keeps the release
offline and read-only.

It is not yet architecture-conformant enough to proceed to Quality & Release. Four trust
contract defects and one evidence defect remain:

1. an omitted `AuthorizationScope` silently becomes a local allow-all scope;
2. allowed path prefixes use raw string-prefix matching rather than path-boundary
   containment;
3. citation construction/validation does not fully prove that the cited heading hierarchy
   and passage support the retrieval/material claim;
4. the legacy reader is not narrowly bounded and can preserve an ambiguous `confidence`
   key when both old and new keys are supplied;
5. the performance gate compares candidate p95 against a v0.3 median rather than an
   equivalent v0.3 p95.

These are contract-boundary defects, not documentation-only conditions. Return the
candidate to the Principal Engineer. Do not begin the QA role against this commit.

## 2. Scope and evidence reviewed

The review began from the project control index and inspected:

- [CTO implementation brief](02-cto-to-principal-engineer-implementation-brief.md);
- [Principal Engineer review](03-principal-engineer-to-cto-engineering-review.md);
- [ADR-0012](../../adr/ADR-0012-Query-Engine-Is-A-Layered-Deterministic-Pipeline.md);
- [ADR-0014](../../adr/ADR-0014-Retrieval-Relevance-Is-Separate-From-Answer-Confidence.md);
- [ADR-0015](../../adr/ADR-0015-Authorization-Precedes-Retrieval-And-Graph-Expansion.md);
- [ADR-0016](../../adr/ADR-0016-Citations-Bind-Passages-To-Source-Revisions.md);
- [ADR-0017](../../adr/ADR-0017-Stable-Source-Identity-Is-Separate-From-Location.md);
- all 40 changed files in the exact reviewed diff;
- implementation, tests, benchmark harness, compatibility reader, documentation, and
  engineering evidence.

The requested branch, HEAD, ancestry, and initially clean working tree were verified.
The reviewed range contains four implementation/test/documentation commits and no chat,
conversation, streaming, provider, embedding, persistence, plugin, MCP, agent, automation,
or vault-write feature.

The Engineering Review reports 163 passing tests, clean Ruff, clean mypy, and clean
`git diff --check`. This CTO pass inspected the implementation and tests independently.
It could not independently execute Python in the Windows review environment: no Python
launcher was callable, and the shared project virtual-environment interpreter returned
an operating-system access-denied error. This does not convert the reported test results
into failures, but Quality must independently rerun them after the architecture blockers
are corrected.

## 3. Requirement and ADR conformance

| Contract | Finding | Status |
|---|---|---|
| R1 / ADR-0014 — relevance | `ScoredNote`, citations, trace JSON, and text output use `relative_relevance`; `answer_confidence` is null and never synthesized | Conformant |
| R2 — context budget | Negative budgets fail; zero is empty; oversized chunks truncate/omit; a fixed separator is charged; property tests cover budgets 0–39 | Conformant with minor documentation debt |
| R3 / ADR-0016 — citations | Exact-byte fingerprint and additive line/heading provenance exist, but support and locator validation are incomplete | Blocking deviation |
| R4 / ADR-0015 — authorization | Authorized notes are selected before index and graph construction; excluded notes do not enter downstream collaborators | Structurally conformant, with two blocking entry/filter defects |
| R5 / ADR-0017 — identity | Explicit and path-derived identities are separated from exact-byte revisions; duplicate authorized explicit IDs fail | Mostly conformant; duplicate-validation scope needs explicit resolution |
| R6 — versioning/compatibility | Affected result, citation, context, and trace outputs carry `jarvis.query.v0.3.1`; index version remains separate | Versioning conformant; legacy reader blocking deviation |
| R7 — release scope | Query trust only; conversation remains excluded; documentation uses the approved release sequence | Conformant |
| ADR-0007 — read-only | Repository reads bytes only; no write capability or external effect was introduced; unchanged-vault test records hash, size, path set, and mtime | Conformant on inspected design |
| ADR-0012 — layering | Policy, identity, authorization view, passages, ranker, context, results, trace, and compatibility are separate collaborators; engine remains orchestration | Conformant, with acceptable constructor coupling/debt |

## 4. Blocking architecture findings

### AC-01 — Missing scope does not fail closed

**Affected:** R4, ADR-0015, implementation brief §4.3.

`QueryEngine.__init__` accepts `scope: AuthorizationScope | None = None` and evaluates:

```python
self._scope = scope or local_allow_all()
```

This makes an omitted scope an implicit unrestricted local policy up to the `restricted`
ceiling. The implementation guide simultaneously states that absence of scope never means
unrestricted. Existing tests still construct `QueryEngine(notes)` without a scope, which
locks the bypass in as compatibility behavior.

The accepted brief requires an explicit scope at every v0.3.1 query boundary and says
missing scope fails closed. The CLI already constructs `local_allow_all(...)` explicitly;
library callers must do the same.

**Required correction:**

- require a non-null `AuthorizationScope` at the v0.3.1 engine boundary;
- remove the constructor fallback;
- update every supported caller/test to pass an explicit scope;
- add a regression test proving omitted/null scope is rejected rather than broadened;
- keep `local_allow_all` as an explicit factory, not a default authority grant.

### AC-02 — Path-prefix authorization is not path-boundary safe

**Affected:** R4, ADR-0015, security boundary.

`AuthorizationScope.permits` normalizes the source relative path and uses
`norm.startswith(prefix)`. The allowed prefixes themselves are not canonicalized or
validated, and matching is not constrained to a complete path segment. A grant for
`Projects/Alpha` can therefore also grant `Projects/Alpha-Restricted`; separator, case,
absolute-path, empty-prefix, and traversal-like inputs lack a defined validation contract.

This is a fail-open authorization bug at the pre-retrieval boundary.

**Required correction:**

- canonicalize and validate allowed relative-path prefixes during scope construction;
- reject absolute, empty/ambiguous, or parent-traversal prefixes;
- compare exact path or descendant path using path-segment boundaries;
- define and test case behavior consistently with repository identity rules;
- add negative tests for sibling-prefix collisions, slash variants, `..`, absolute paths,
  empty prefixes, and near-match names.

### AC-03 — Citation support and heading binding are incomplete

**Affected:** R3, ADR-0016, C3.

The implementation correctly fingerprints exact bytes and adds source text,
`body_start_line`, heading paths, inclusive line ranges, and bounded excerpts. Stale
fingerprints, out-of-range locators, and excerpt mismatch have tests.

However:

1. validation checks only whether the final heading name exists anywhere in the source;
   it does not prove the full heading path encloses the locator or that the locator still
   denotes the cited section;
2. passage selection searches body text only. A result ranked by title, alias, tag,
   filename, or frontmatter can receive an arbitrary first-body passage that does not
   contain or support the winning evidence;
3. unranked/summarization citations use empty evidence terms and select the first body
   section, even when the material value came from frontmatter;
4. empty excerpts are accepted by `validate`, and citation construction does not invoke
   validation before emitting a citation;
5. the required empty-source and changed-heading-hierarchy cases are absent from the
   tests.

This does not yet establish a claim-supporting passage contract. It establishes document
revision plus a body locator.

**Required correction:**

- bind validation to the complete heading hierarchy at the locator, not leaf-heading
  existence anywhere;
- recompute or otherwise verify section bounds against the locator and heading path;
- select a passage that corresponds to the actual retrieval/supporting signal, including
  metadata/frontmatter evidence, or explicitly decline to emit a material citation when
  no supporting passage exists;
- reject empty supporting excerpts for material citations;
- validate constructed citations at the result boundary before emission;
- add tests for duplicated leaf headings under different parents, moved/renamed parents,
  locator moved outside its section, metadata-only matches, title/alias/frontmatter
  matches, empty body/source, empty excerpt, and stale bytes.

The additive parser approach remains acceptable. A change to canonical Markdown parsing
semantics is not required or authorized.

### AC-04 — Legacy reader is broader than the approved compatibility boundary

**Affected:** R6, ADR-0014, implementation brief §5.

The compatibility helpers accept arbitrary dictionaries without verifying a legacy
contract/shape. When both `confidence` and `relative_relevance` are supplied, the current
condition leaves `confidence` in the returned object. This preserves exactly the ambiguous
term that new outputs prohibit.

The reader is currently used only by its tests, so tightening it has low compatibility
risk.

**Required correction:**

- accept only the documented legacy result/citation shapes;
- reject conflicting old/new fields, or verify equality and always remove the old key;
- validate value type/range appropriate to legacy relative ranking;
- never map any ranking value to `answer_confidence`;
- add malformed, both-key, conflicting-key, wrong-type, and nested-shape tests;
- retain the documented one-release removal boundary.

### AE-01 — The ≤20% performance gate is not demonstrated

**Affected:** performance acceptance evidence; not an implementation-architecture defect.

The Engineering Review reports candidate 1,000-note total query p95 of 35.7 ms and compares
it with a v0.3 `total(query)` value of 35.7 ms explicitly described as a median. The v0.3
benchmark at the base commit reports medians only. Comparing a candidate p95 to a baseline
median cannot demonstrate the brief's p95-to-p95 regression gate.

The candidate harness also manually composes the stages and labels index plus graph build
as retrieval. It does not measure the complete public `QueryEngine` call, while the legacy
harness has different stage contents. The result may be fast, but the stated 0% regression
is not supported by equivalent measurements.

**Required correction:**

- measure a v0.3 1,000-note p95 on the same machine/environment using an equivalent
  logical workload and percentile method;
- measure candidate p95 with the same run count, warm-up policy, fixture, query, and
  end-to-end boundary;
- report raw samples or a reproducible raw summary, p50/p95/p99, and the exact regression
  calculation;
- use at least the brief's 10 measured runs; more runs are recommended because with 10,
  p95 and p99 collapse to the maximum under the present estimator;
- keep stage timings as diagnostics, but make the release gate an equivalent total-pipeline
  p95 comparison.

Until corrected, performance status is **not demonstrated**, not failed.

## 5. Security and trust-boundary assessment

### Strengths

- Authorization precedes both `LexicalIndex` and `RelationshipResolver`; this is the
  correct structural boundary.
- The index, candidate set, relationship graph, context builder, citations, conflicts,
  and trace operate only on the authorized subset.
- Restricted one-hop graph neighbors and excluded-only terms have negative tests.
- Trace exposes only authorized candidate/source identities plus one aggregate exclusion
  count.
- Unknown/missing note sensitivity fails closed.
- Fingerprints use SHA-256 over exact bytes, preserving CRLF/LF revision differences.
- Identity, revision, and current location are separate concepts.
- No network or write capability was added.

### Residual and blocking risks

- AC-01 can broaden authority when a caller forgets scope.
- AC-02 can broaden a path grant to a similarly prefixed sibling.
- AC-03 can present a precise-looking citation that is revision-valid but not
  claim-supporting.
- Duplicate explicit IDs are checked only after authorization. ADR-0017 says duplicates
  within a workspace are validation failures, while ADR-0015 prohibits excluded sources
  from influencing request-visible behavior. Engineering must document whether duplicate
  detection is a separate vault-validation phase or intentionally scoped to the authorized
  view. Do not reveal an excluded duplicate through query errors. This is a design
  clarification required in the correction handoff, but it need not block safe query
  execution if validation and query disclosure remain separated.
- Aggregate timing remains a possible coarse side channel. No source-identifying timing
  detail is emitted; constant-time retrieval is not required for this local pilot.

## 6. Layering, coupling, and technical debt

The candidate remains compatible with ADR-0012. `authorized.py`, `policy`, `identity`,
`passages`, `ranking`, `context_builder`, `results`, and `trace` retain distinct reasons to
change. `QueryEngine` wires these collaborators and routes intents; it has not absorbed
their internal policy or parsing logic.

The request-authorized view is constructed once per `QueryEngine` instance, making an
engine instance scope-bound. That is acceptable for v0.3.1 and materially safer than
post-retrieval filtering. Re-indexing and rebuilding the relationship report for each
scope is acceptable at the approved 1,000-note scale, subject to corrected benchmark
evidence.

Recorded debt:

- Before persisted/shared/hybrid retrieval, introduce the previously recommended
  `Retriever`/authorized-projection port so policy is not coupled to in-memory index
  construction.
- A shared projection must prove that excluded terms, graph edges, counts, caches, and
  traces cannot influence request-visible behavior before replacing the isolated view.
- `ContextPackage.to_dict()` hard-codes the contract string instead of importing the
  version constant. This is minor drift risk, not a release blocker; consolidate when it
  can be done without creating an undesirable module dependency.
- Context accounting charges excerpt words plus one separator token, while chunk metadata
  fields are outside the selection budget. This is acceptable only because the v0.3.1
  contract defines the emitted provider-neutral content as excerpts plus separators.
  Documentation should state that titles/paths/roles are audit metadata, not provider
  prompt tokens. A future provider adapter must re-measure its full prompt envelope.
- Passage selection is heuristic. That is acceptable after it is made signal-supporting
  and validated; semantic claim entailment remains a later generated-answer concern.

## 7. Required correction package

The Principal Engineer must return a superseding engineering commit and updated
[Engineering Review](03-principal-engineer-to-cto-engineering-review.md) or a new revision
that records:

1. AC-01 through AC-04 corrections and exact new tests;
2. corrected p95-to-p95 baseline and candidate benchmark evidence;
3. the duplicate-ID validation/query-disclosure design clarification;
4. full test, Ruff, mypy, `git diff --check`, benchmark, and unchanged-vault results;
5. exact new HEAD and diff range from this reviewed commit;
6. confirmation that no excluded scope was imported.

The CTO must re-review the correction diff. Quality & Release remains blocked until the
CTO issues a superseding architecture disposition that explicitly allows QA to begin.

## 8. Prospective QA scope after architecture clearance

This candidate is **not currently allowed to proceed**, so the following is not an
authorization to start QA. If a superseding CTO disposition clears the corrections,
Quality & Release must independently assess:

1. exact branch/HEAD, clean tree, commit ancestry, and absence of parked conversation code;
2. full tests, Ruff, mypy, `git diff --check`, and unchanged-vault evidence;
3. missing/null scope rejection and explicit CLI/local scope construction;
4. path-prefix boundary, traversal, normalization, and near-match attacks;
5. excluded-source non-disclosure across candidates, rankings, graph paths, conflicts,
   answers, citations, trace, exceptions, logs, and aggregate counts;
6. sensitivity ceilings, unknown labels, allowed source IDs/types, workspace separation,
   and duplicate-ID behavior;
7. exact-byte fingerprints across LF/CRLF and stale-source changes;
8. full heading-path/locator binding, metadata-derived support, excerpts, empty sources,
   and pre-emission citation validation;
9. every context-budget boundary, separator accounting, deterministic truncation, and
   serialized total;
10. absence of retrieval `confidence` from new outputs and absence of numeric answer
    confidence;
11. contract/index version separation and adversarial legacy-reader inputs;
12. deterministic structured output for identical snapshot, explicit request ID, scope,
    query, and configuration;
13. corrected equivalent p95-to-p95 performance comparison at 100/500/1,000 notes,
    authorization stress, graph restriction, and peak memory;
14. documentation/implementation agreement and one formal QA release disposition.

QA must treat generated/provider-backed answers, chat, streaming, Project Resume, memory,
plugins, MCP, agents, automation, writes, and the parked conversation branch as out of
scope.

## 9. Explicit exclusions and forbidden next work

- Do not merge or push this candidate.
- Do not begin Quality & Release review at this commit.
- Do not modify or merge the parked conversation candidate.
- Do not add chat, streaming, real providers, embeddings, persistence, writes, plugins,
  MCP, agents, automation, background services, or Project Resume.
- Do not weaken authorization, citation, or performance gates to preserve compatibility.

## 10. Exit statement

**Refactor first.** The v0.3.1 architecture is fundamentally viable, and the authorized
view plus layered trust collaborators are the correct direction. Commit
`62f2269245890b3f55925056c93e156c179d4b5b` is returned to engineering for AC-01 through
AC-04 and corrected performance evidence. Quality & Release is not authorized to begin
until a superseding CTO architecture-conformance review clears the correction package.

---

# SUPERSEDING CTO REVISION — Rev 2

| Field | Value |
|---|---|
| Revision | 2 — supersedes the disposition above for the remediated candidate |
| Review date | 2026-07-27 |
| Reviewed branch | `feature/v0.3.1-query-trust-contracts` |
| Reviewed HEAD | `91636228e72f14c15fbc07c1733da00b8647f27f` |
| Prior reviewed implementation | `62f2269245890b3f55925056c93e156c179d4b5b` |
| CTO return commit | `4285e28ff356529404bfab8e20ceb097a8e6aadf` |
| Remediation diff | `62f2269245890b3f55925056c93e156c179d4b5b..91636228e72f14c15fbc07c1733da00b8647f27f` |
| Initial worktree state | Clean |
| Superseding architecture disposition | **Refactor first** |
| QA authorization | Withheld; Quality & Release must not start |

## R2.1 Executive disposition

**Architecture disposition: Refactor first.**

The remediation is materially improved and remains within the approved v0.3.1 scope.
AC-01 and AC-02 are closed. AC-03 and AC-04 are only partially closed, and AE-01 remains
unproven against the accepted total-pipeline definition.

Quality & Release is not authorized to review commit
`91636228e72f14c15fbc07c1733da00b8647f27f`. The remaining defects are at the citation,
compatibility, and release-evidence boundaries and must be corrected before QA.

## R2.2 State and scope verification

The superseding review verified:

- branch `feature/v0.3.1-query-trust-contracts`;
- HEAD `91636228e72f14c15fbc07c1733da00b8647f27f`;
- initially clean worktree;
- `62f2269245890b3f55925056c93e156c179d4b5b` is an ancestor of HEAD;
- `4285e28ff356529404bfab8e20ceb097a8e6aadf` is an ancestor of HEAD;
- remediation commits are limited to the CTO findings, tests, benchmark evidence,
  documentation, and handoffs;
- no chat, conversation, streaming, real-provider, embedding, persistence, write, plugin,
  MCP, agent, automation, background-service, or Project Resume implementation was added.

The review inspected the Rev 2 Engineering Review, the complete remediation diff, current
implementation and tests, and ADR-0012 plus ADR-0014 through ADR-0017.

As in Rev 1, the Windows review environment did not expose a callable Python runtime, so
the reported `180 passed`, Ruff, mypy, and benchmark executions were reviewed as evidence
but not independently rerun. Quality must rerun all checks after architecture clearance.

## R2.3 Finding status

| Finding | Superseding assessment | Status |
|---|---|---|
| AC-01 — explicit scope | `QueryEngine` now requires keyword-only `scope`; omitted scope raises `TypeError`; explicit `None` raises `PolicyError`; supported callers pass an explicit scope | **Closed** |
| AC-02 — safe path prefixes | Prefixes are canonicalized, absolute/empty/traversal inputs rejected, case/slashes normalized, and exact/descendant segment boundaries enforced | **Closed** |
| AC-03 — citation binding | Full heading hierarchy and non-empty excerpts are checked; metadata evidence can be located; however exact-byte pre-emission validation and claim-specific unranked citations remain incomplete | **Open — blocking** |
| AC-04 — bounded reader | Old-key removal, conflict detection, numeric/range checks, and nested-list validation were added; arbitrary mappings and non-legacy shapes remain accepted | **Open — blocking** |
| AE-01 — p95 gate | p95 is now compared with p95 using the same `run()` harness, but the harness excludes construction explicitly required by the accepted total query pipeline | **Open — blocking evidence** |
| Duplicate-ID clarification | Whole-vault validation and request-authorized duplicate detection are separated without exposing excluded identities | **Closed** |

## R2.4 Closed findings

### AC-01 — Explicit authorization scope

The constructor no longer defaults to `local_allow_all`. An omitted keyword fails at the
Python boundary and explicit `None` fails with `PolicyError`. The CLI and supported
candidate callers construct an explicit scope.

The adaptive regression benchmark contains a no-scope baseline branch solely so the same
script can run against historical v0.3 code. In the v0.3.1 environment it supplies the
explicit scope. This does not create a candidate runtime bypass.

**Assessment:** conforms to ADR-0015 and the implementation brief.

### AC-02 — Path-prefix authorization

The remediation:

- normalizes case and slash direction;
- rejects absolute, drive-qualified, blank, empty, and `..` traversal prefixes;
- compares either exact normalized path or `prefix + "/"` descendants;
- prevents sibling and near-match grants.

The case-insensitive behavior is consistent with the existing path-derived identity
normalization. Remaining redundant-separator or `.` inputs fail restrictive rather than
broadening access.

**Assessment:** the authorization boundary is fail-closed and architecture-conformant.

### Duplicate-ID clarification

The documented split is acceptable:

- owner-level vault validation reports duplicates across the complete vault;
- request execution checks only the authorized view before index/graph creation;
- excluded duplicates cannot affect request-visible errors, traces, or counts.

This reconciles ADR-0017 data integrity with ADR-0015 non-disclosure without merging the
two trust contexts.

## R2.5 Remaining blocking findings

### AC-03R2 — Pre-emission validation does not bind the fingerprint to current bytes

`QueryEngine._cite_scored` and `_cite_note` call `validate_against_text(...)`. That helper
checks cached text structure, locator range, heading hierarchy, and excerpt. It does not
check `source_fingerprint` against current exact source bytes.

The full `validate(...)` function performs the fingerprint check, but it is not called by
the engine before emission. If a source changes after repository discovery and before the
query result is constructed, the engine can emit a citation carrying the stale discovery
fingerprint and cached passage. External validation can later reject it, but the mandatory
pre-emission boundary did not.

This does not satisfy the Rev 1 correction:

> validate constructed citations at the result boundary before emission

or ADR-0016's requirement that stale citations fail validation.

**Required correction:**

1. At citation emission, validate exact current bytes against the stored fingerprint plus
   locator, hierarchy, and excerpt.
2. Keep the operation read-only and prevent relative-path escape from the configured
   source root.
3. If retaining exact bytes in the parsed source object is chosen instead of rereading,
   document that this proves discovery-revision consistency but does not detect a
   post-discovery file change; the emitted citation must then be explicitly revision-bound
   and checked for currentness before being described as current.
4. Add an integration test that discovers notes, mutates the source, then queries and proves
   that no stale citation is emitted as valid.
5. Preserve CRLF/LF exact-byte behavior and add a non-normalized byte-change case.

### AC-03R2 — Unranked citations are not claim-specific

Ranked citations now search the complete source for a query term, including frontmatter.
This closes the metadata-only retrieval case.

However `_cite_note(..., evidence=frozenset())` remains used by project summarization and
relationship explanation. With no evidence terms, `locate` selects the first non-empty
content. That passage is structurally valid but may not support:

- the project status, priority, resume, or other summarized values; or
- the direct/shared relationship claimed by `explain`.

Dropping an unsupported graph-only project citation is correct, but the same
claim-support rule must apply to these unranked/material paths.

**Required correction:**

1. Supply claim-specific evidence/locators for relationship and summarization citations,
   including frontmatter fields and actual link passages.
2. Alternatively, omit the material claim or mark its citation coverage incomplete; do
   not attach arbitrary first content as support.
3. Add tests where the first body section is unrelated and the actual status/link evidence
   appears later or only in frontmatter.
4. Prove every emitted material citation supports the adjacent deterministic claim. Full
   semantic entailment for future generated answers remains out of scope.

### AC-04R2 — Legacy shape validation remains too permissive

The reader now correctly removes `confidence`, rejects conflicting old/new values, rejects
boolean/wrong-type/out-of-range ranking values, and validates that nested citations form a
list.

It still accepts arbitrary mappings as valid legacy results or citations. Examples that
currently pass through include:

```python
read_legacy_citation({"unrelated": "value"})
read_legacy_result({"relative_relevance": "not validated"})
```

The implementation does not require the documented legacy keys, reject unknown keys,
distinguish legacy result from citation shape, or validate `relative_relevance` when the
old key is absent. A function described as the narrowly bounded one-release legacy reader
must not become a generic dictionary normalizer.

**Required correction:**

1. Define exact allowed and required key sets for the v0.3 result and citation payloads.
2. Reject unknown keys and missing required identity/result fields.
3. Reject new-only payloads at the legacy boundary, or route them through a separately
   versioned current reader.
4. Validate `relative_relevance` whenever present, including new-only and both-key cases.
5. Validate every nested citation against the citation shape.
6. Add unknown-key, missing-key, wrong-shape, new-only wrong-type/range, and result-as-
   citation/citation-as-result tests.

The one-release removal target remains acceptable.

### AE-01R2 — Equivalent total-pipeline p95 is still not demonstrated

The new benchmark fixes the percentile mismatch: it compares p95 with p95 over identical
fixtures, query, warm-ups, run count, and percentile method.

It explicitly constructs the engine before timing and measures only:

```python
engine.run(query)
```

The accepted implementation brief defines the measured pipeline to include:

- authorized index/view construction;
- candidate retrieval;
- ranking;
- graph/context expansion;
- citation construction and validation;
- total query pipeline.

Authorization, index construction, and relationship-graph construction occur in
`QueryEngine.__init__`, not `run()`. Excluding construction therefore removes the
per-scope authorized-view cost whose coupling and performance the gate was intended to
assess. The candidate and baseline `run()` measurements are mutually comparable, but they
do not measure the accepted total pipeline.

**Required correction:**

1. Use the same synthetic vault and pre-parsed note set for both versions.
2. For each measured sample, time equivalent engine construction plus one public query,
   or otherwise include authorized-view/index/graph construction in a clearly equivalent
   total.
3. Use identical query, run count, warm-up policy, percentile estimator, hardware, Python,
   and fixture implementation.
4. Report v0.3 and v0.3.1 p50/p95/p99, raw samples or reproducible summary, and the exact
   p95 regression calculation.
5. Retain the current prebuilt-engine result as a useful steady-state diagnostic, not the
   release gate.
6. Demonstrate the candidate total-pipeline p95 is no more than 20% above the equivalent
   v0.3 p95.

Performance remains **not demonstrated**, not failed.

## R2.6 Architecture, security, and debt assessment

No new unapproved scope or architectural regression was found in the remediation.

- ADR-0012 layering remains intact: policy, authorized view, passages, compatibility,
  ranking, context, results, trace, and orchestration retain separate responsibilities.
- Authorization still occurs before request-visible index and graph construction.
- Excluded sources remain absent from candidates, graph expansion, results, conflicts,
  context, citations, and trace except for the approved aggregate count.
- Exact-byte SHA-256 fingerprints and additive source provenance remain intact.
- Retrieval relevance remains separate from answer confidence.
- Context budgeting and versioning were not weakened.
- The per-scope authorized view remains acceptable at the 1,000-note target, subject to
  corrected total-pipeline evidence.

Existing technical debt from Rev 1 remains accepted and unchanged. The remediation adds no
reason to introduce persistence, a shared index, provider-specific tokens, or a broader
compatibility framework.

## R2.7 Required engineering return

Return a Rev 3 correction package containing:

1. AC-03R2 exact-byte/current-revision validation before citation emission;
2. claim-specific relationship and summarization citation behavior;
3. AC-04R2 exact legacy shape validation;
4. AE-01R2 equivalent total-pipeline p95 evidence;
5. exact tests mapped to each item;
6. full test, Ruff, mypy, `git diff --check`, unchanged-vault, and benchmark results;
7. exact correction branch, new HEAD, and diff range from
   `91636228e72f14c15fbc07c1733da00b8647f27f`;
8. confirmation that the candidate remains unmerged, unpushed, and within v0.3.1 scope.

The CTO must perform another superseding conformance review. Do not route directly to QA.

## R2.8 QA status and prospective scope

**Quality & Release is not authorized to begin.** There is therefore no active QA review
scope or QA output assignment for this commit.

If a later CTO revision clears the remaining blockers, it must explicitly name:

- branch and exact cleared HEAD;
- complete evidence package and corrected benchmark;
- active QA review matrix;
- required output
  `docs/handovers/v0.3.1/05-quality-to-product-owner-release-review.md`.

Until then, that output must not be produced.

## R2.9 Exit statement

**Refactor first.** AC-01, AC-02, and the duplicate-ID design are cleared. AC-03 and AC-04
remain partially open, and AE-01 remains unproven under the accepted total-pipeline
definition. Commit `91636228e72f14c15fbc07c1733da00b8647f27f` is returned to engineering.
Quality & Release is not authorized to begin.

---

# FINAL SUPERSEDING CTO REVISION — Rev 3

| Field | Value |
|---|---|
| Revision | 3 — supersedes CTO Rev 2 for the Rev 3 engineering candidate |
| Review date | 2026-07-27 |
| Reviewed branch | `feature/v0.3.1-query-trust-contracts` |
| Reviewed HEAD | `47b1a0bf5609d29abb3633273fec2721b853ef45` |
| Prior reviewed implementation | `91636228e72f14c15fbc07c1733da00b8647f27f` |
| Chief-of-Staff return commit | `ac03c3c9971be7957027d9b7ffa4f33abfc9f8a8` |
| Correction diff | `91636228e72f14c15fbc07c1733da00b8647f27f..47b1a0bf5609d29abb3633273fec2721b853ef45` |
| Initial worktree state | Clean |
| Architecture disposition | **Refactor first** |
| Quality & Release authorization | Withheld |

## R3.1 Executive disposition

**Architecture disposition: Refactor first.**

Rev 3 closes AC-04R2 and AE-01R2. It also closes most of AC-03R2: current-file checking is
path-confined and fail-closed when `source_root` is configured; missing and changed files
are declined; exact discovery bytes are retained; ranked citations remain material-only;
and summarize/explain passage selection is now claim-specific.

AC-03R2 is not completely closed:

1. `source_root` remains optional at a citation-producing engine boundary, allowing a
   citation to be emitted as `coverage="supported"` without checking current on-disk bytes;
2. `coverage="incomplete"` is present in structured output but hidden by the CLI text
   renderer, which presents the object under “Sources” with a misleading `0-0` line range.

These are visible trust-contract defects. Quality & Release is not authorized to begin
against `47b1a0bf5609d29abb3633273fec2721b853ef45`.

## R3.2 Verification and review scope

The review verified:

- exact requested branch and HEAD;
- initially clean worktree;
- Rev 2 implementation `91636228e72f14c15fbc07c1733da00b8647f27f`
  is an ancestor of HEAD;
- Chief-of-Staff return commit
  `ac03c3c9971be7957027d9b7ffa4f33abfc9f8a8` is an ancestor of HEAD;
- the Rev 3 diff is confined to AC-03R2, AC-04R2, AE-01R2, their tests,
  documentation, and handoffs;
- no chat, streaming, provider, embedding, persisted-index, write, plugin, MCP,
  agent, automation, background-service, or Project Resume scope was introduced.

The review inspected the Rev 3 Engineering Review, the complete correction diff, current
citation and compatibility code, currentness/claim tests, regression benchmark, ADR-0016,
and the accepted implementation brief.

The reported evidence is 190 passing tests, clean Ruff, clean mypy, clean
`git diff --check`, passing unchanged-vault evidence, and total-pipeline p95 regression
of +9.1%. The Windows CTO environment still did not expose a callable Python runtime, so
those commands were not independently rerun. This is not a new architecture finding;
Quality must rerun them after architecture clearance.

## R3.3 Finding disposition

| Finding | Final Rev 3 assessment | Status |
|---|---|---|
| AC-01 | No regression; explicit authorization scope remains mandatory | **Closed** |
| AC-02 | No regression; path canonicalization and segment-boundary enforcement remain intact | **Closed** |
| Duplicate-ID handling | No regression; owner validation and request non-disclosure remain separated | **Closed** |
| AC-03R2 — path/currentness with root | Current bytes are re-read within a resolved root; escape, missing file, unreadable file, and fingerprint mismatch fail closed | **Closed when `source_root` is present** |
| AC-03R2 — root omission | Discovery bytes are accepted as if sufficient for a supported citation, even though post-discovery currentness cannot be determined | **Open — blocking** |
| AC-03R2 — claim-specific evidence | Ranked citations require support; summarize/explain search for project/link evidence rather than arbitrary first content | **Closed** |
| AC-03R2 — incomplete coverage visibility | Structured output labels incomplete coverage, but CLI text does not display it and renders line `0-0` under “Sources” | **Open — blocking** |
| AC-04R2 | Exact legacy result/citation key sets, required keys, nested validation, old-key removal, and ranking-value validation are enforced | **Closed** |
| AE-01R2 | Equivalent construction-plus-query p95 comparison reports +9.1%, within the ≤20% gate | **Closed** |

## R3.4 AC-03R2 findings

### AC-03R3-01 — `source_root` must be mandatory or citation emission must fail closed

The accepted implementation brief requires citation validation to prove:

> the current bytes match `source_fingerprint`

With a configured root, the implementation satisfies this:

- `(source_root / relpath).resolve()` is checked with `is_relative_to(source_root)`;
- symlink/path escape resolves outside and is rejected;
- missing/unreadable files return no current bytes;
- post-discovery mutation changes the fingerprint and declines the citation;
- CRLF/LF and appended raw-byte changes are fingerprint-visible.

Without a root, `_current_bytes` returns `note.source_bytes`. This validates only that the
stored discovery fingerprint matches the stored discovery snapshot. It cannot determine
whether the source currently exists or changed after discovery. Nevertheless, the engine
can emit the citation with:

```text
coverage="supported"
```

The fallback therefore proves snapshot self-consistency, not current-source validity.
Documenting the distinction does not satisfy the accepted current-byte invariant.

**Required correction — choose one fail-closed contract:**

1. Make `source_root` mandatory for `QueryEngine` because all supported query surfaces can
   produce citations; update all callers and tests accordingly.

   **Or**

2. Permit snapshot-only construction, but prohibit `supported` citation emission without
   a current-source resolver. Return no citation or an explicitly separate unavailable/
   snapshot-only evidence object that cannot be mistaken for a validated citation.

The preferred v0.3.1 design is option 1: the filesystem repository already owns the root,
the CLI supplies it, and a required root keeps the citation guarantee uniform. A future
non-filesystem repository may satisfy the same port through an explicit read-only
current-source resolver rather than weakening the contract.

Add tests proving:

- omission of the current-source boundary fails at construction or citation emission;
- all supported query constructors supply it;
- path escape and symlink escape fail closed;
- missing/unreadable source fails closed;
- post-discovery raw-byte mutation declines the citation;
- a discovery snapshot alone is never labeled `supported` under the current-byte
  contract.

### AC-03R3-02 — Incomplete coverage is not explicit in the text interface

Using `coverage="incomplete"` is acceptable for an authorized source reference when the
claim-specific evidence gap is made unmistakable and it is not represented as a
passage-valid citation.

The structured JSON includes `coverage`, an empty excerpt, and locator `0-0`. That is
machine-visible. The CLI text renderer, however, ignores `coverage` and prints every object
under:

```text
Sources:
  - <title> (<path>:0-0) [relative relevance=n/a] <reason>
```

This makes an incomplete reference appear to be a normal source citation. The user does
not see that the claim lacks a supporting passage. It violates the AI Behavior Standard's
visible-uncertainty and citation-coverage rules.

**Required correction:**

- render supported passage citations and incomplete references separately in text;
- never display `0-0` as a source line range;
- use explicit language such as “Evidence coverage incomplete — source referenced, but no
  claim-supporting passage was found”;
- expose an answer-level citation-coverage/limitations signal so a consumer need not infer
  incomplete support by scanning citations;
- ensure exit/status behavior does not treat an answer containing only incomplete
  references as fully evidence-backed;
- add CLI text and JSON tests proving the gap is visible and cannot be confused with
  supported evidence.

The accepted R3 citation structure still applies to `coverage="supported"`. An incomplete
reference with no locator/excerpt must not be counted as a valid material citation.

## R3.5 AC-04R2 final assessment

The compatibility reader now:

- defines exact legacy result and citation key sets;
- requires the documented identity/result fields;
- rejects unknown keys and result/citation shape confusion;
- rejects new-only payloads at the legacy boundary;
- validates old and new ranking values when present;
- requires equal old/new values and always removes `confidence`;
- validates every nested citation;
- never produces answer confidence.

This is the narrowly bounded, one-release reader required by R6 and ADR-0014.

**AC-04R2 is closed.**

## R3.6 AE-01R2 final assessment

The revised benchmark times, for each sample:

1. `QueryEngine` construction over the same pre-parsed note set; and
2. one public query.

This includes the candidate's authorized-view, index, relationship graph, retrieval,
ranking, citation/current-byte validation, and result construction. The baseline and
candidate use the same synthetic fixture, query, warm-up count, 100 measured runs,
percentile method, machine, and Python version.

Reported 1,000-note p95:

| Version | Total-pipeline p95 |
|---|---:|
| v0.3 baseline | 35.219 ms |
| v0.3.1 candidate | 38.430 ms |
| Regression | +9.1% |

The result is below the accepted +20% ceiling. The prebuilt-engine measurement is correctly
retained as a diagnostic rather than substituted for the release gate.

**AE-01R2 is closed.**

## R3.7 Architecture and security assessment

Rev 3 does not regress ADR-0012 layering. The additional current-source logic is currently
inside `QueryEngine`; at this prototype scale that is tolerable, but the next repository
variant should introduce a small read-only source-revision resolver port rather than adding
filesystem-specific branches to orchestration.

The following remain architecturally sound:

- authorization before index and graph construction;
- excluded-source non-disclosure;
- exact-byte fingerprints;
- stable identity separated from revision/location;
- full heading hierarchy and claim-specific passage selection;
- hard context budget;
- relevance/answer-confidence separation;
- versioned outputs and strict legacy boundary;
- isolated, per-scope authorized view;
- local, offline, read-only behavior.

The only remaining release blockers are the uniform current-source requirement and visible
incomplete-coverage semantics described above.

## R3.8 Required final engineering correction

Return a narrowly scoped final correction containing:

1. mandatory current-source validation for every citation-producing boundary, preferably
   by requiring `source_root` for the current filesystem implementation;
2. explicit separation/rendering of supported citations and incomplete evidence
   references;
3. answer-level coverage/limitation semantics and correct exit behavior;
4. tests for omitted current-source boundary, path/symlink confinement, mutation/missing
   source, snapshot-only behavior, CLI text, JSON, and incomplete-only answers;
5. full tests, Ruff, mypy, `git diff --check`, unchanged-vault, and benchmark confirmation;
6. exact new HEAD and diff from
   `47b1a0bf5609d29abb3633273fec2721b853ef45`;
7. confirmation that the branch remains unmerged, unpushed, and within v0.3.1 scope.

The CTO must issue one more superseding architecture disposition. Do not begin QA directly.

## R3.9 QA status

**Quality & Release is not authorized to begin.**

No QA output is authorized for this HEAD. After a future CTO clearance, the required QA
artifact remains:

```text
docs/handovers/v0.3.1/05-quality-to-product-owner-release-review.md
```

The clearing disposition must pin the exact branch/HEAD and active QA evidence matrix.

## R3.10 Exit statement

**Refactor first.** AC-04R2 and AE-01R2 are closed. AC-03R2 is substantially improved but
remains open because supported citations can still bypass current-source validation when
`source_root` is omitted, and incomplete evidence coverage is not visible in CLI text.
Commit `47b1a0bf5609d29abb3633273fec2721b853ef45` is returned to engineering. Quality &
Release is not authorized to begin.

---

# Final Superseding CTO Revision 4 — Final Conformance Review

**Date:** 2026-07-27

**Role:** Chief Architect / CTO

**Supersedes:** Final Superseding CTO Revision 3 above

**Reviewed branch:** `feature/v0.3.1-query-trust-contracts`

**Reviewed HEAD:** `649e5a2ecfc98b2c4c9f23b5456716bb5f05f7f9`

**Prior candidate:** `47b1a0bf5609d29abb3633273fec2721b853ef45`

**Chief-of-Staff return commit:** `33434b6e99824bc32517dad8bd574cf7d0d5b072`

**Correction diff:** `47b1a0bf5609d29abb3633273fec2721b853ef45..649e5a2ecfc98b2c4c9f23b5456716bb5f05f7f9`

## R4.1 Verification and reviewed evidence

Before this disposition was appended, the worktree was clean, the branch and HEAD matched
the values above, and the prior candidate and Chief-of-Staff return commits were present in
the reviewed history.

The independent review covered:

- Final Superseding CTO Revision 3;
- Engineering Review Rev 4;
- the complete correction diff;
- the current query engine, result contract, CLI rendering and exit handling;
- currentness, authorization, citation-claim, CLI text/JSON, versioning, scale, and
  read-only tests;
- the benchmark harnesses and their documented entry points;
- ADR-0016 and the previously accepted ADR-0012/0014–0017 compatibility constraints.

The correction is narrowly scoped to the returned findings. No unapproved feature scope or
layering change was found.

## R4.2 AC-03R3-01 — mandatory current-source boundary

The public `QueryEngine` constructor now requires both an explicit authorization scope and
a `source_root`. Explicit `None` fails at construction. Supported citations are validated
against bytes read from a resolved current path beneath that root; the discovery snapshot
is no longer a validation fallback.

The current-byte path correctly fails closed for:

- lexical or resolved path escape;
- symlink escape;
- missing or non-file sources;
- unreadable sources;
- post-discovery mutation, including byte-level changes that normalize to the same text.

However, one supported repository entry point was not migrated:

```text
scripts/benchmark_query.py
```

Both its warm-up and its 1,000-note memory measurement construct the current
`QueryEngine(notes, scope=scope)` without `source_root`. The constructor now requires that
argument, so the documented v0.3.1 authorized-query benchmark raises before it can execute.
This is an active compatibility surface: it remains named in the implementation brief,
`CHANGELOG.md`, and `docs/software/TESTING.md`.

The regression is not a route to snapshot-only `coverage="supported"`; it fails closed.
Nevertheless, AC-03R3-01 explicitly required every supported citation-producing engine
boundary to supply a valid current-source root, and the final correction leaves this
documented boundary unusable.

**AC-03R3-01 remains open.**

## R4.3 AC-03R3-02 — visible and structural coverage semantics

The answer contract now separates `supported_citations()` from
`incomplete_citations()` and emits an answer-level `citation_coverage` object with label,
counts, and a limitation when coverage is partial or incomplete.

The text CLI:

- renders only validated passages under `Sources (supporting passages)`;
- renders incomplete references under an explicit evidence-coverage warning;
- does not render an incomplete `0-0` locator as a passage citation;
- prints answer-level coverage; and
- returns warning status when an answer has no supported citation.

JSON retains the incomplete reference as structured provenance while distinguishing it
through citation coverage and the answer-level coverage object. A snapshot-only,
missing-file, escaped-path, or changed-byte path cannot be represented as supported
evidence.

**AC-03R3-02 is closed.**

## R4.4 Earlier findings and performance evidence

The correction diff does not regress the previously closed findings:

- **AC-01 remains closed:** authorization precedes index, candidate, graph, context, and
  citation construction, with excluded-source non-disclosure preserved.
- **AC-02 remains closed:** path-prefix canonicalization, traversal rejection, segment
  boundaries, and case behavior remain unchanged.
- **Duplicate-ID handling remains closed:** fail-closed ambiguity handling is unchanged.
- **AC-04R2 remains closed:** the legacy reader retains exact shape validation and removes
  ambiguous `confidence`.
- **AE-01R2 remains closed:** the equivalent construction-plus-query p95 comparison reports
  33.812 ms for v0.3 and 38.075 ms for v0.3.1, a **+12.6%** regression, within the
  accepted 20% gate.

The hard context budget, exact-byte fingerprints, additive line/heading provenance, full
heading-hierarchy validation, claim-specific retrieval binding (including
metadata-derived evidence), empty-excerpt rejection, relevance/confidence separation, and
ADR-0012 layered pipeline remain unregressed.

The per-request authorized view remains acceptable bounded coupling for v0.3.1. The
existing recommendation to introduce a read-only source-revision resolver port before
adding another repository implementation remains technical debt, not a release blocker.

## R4.5 Security and trust-boundary assessment

The corrected production CLI and direct engine boundary fail closed when a trusted live
source root is unavailable. Path resolution and symlink confinement prevent a note
identity from redirecting validation outside the authorized source root. Current-byte
fingerprint comparison prevents stale discovery state, missing sources, and post-discovery
mutation from becoming supported citations.

Supported passages and incomplete references are now visibly and structurally distinct;
an incomplete-only answer is explicitly not fully evidence-backed. No excluded-source
content was found to re-enter results through trace, conflict, error, citation, or graph
paths.

The remaining defect is availability/compatibility rather than disclosure: the documented
benchmark boundary fails closed because it does not supply the newly mandatory root.

## R4.6 Required engineering correction

Return one minimal correction that:

1. passes the synthetic vault root to every current-branch `QueryEngine` construction in
   `scripts/benchmark_query.py`, including warm-up and memory measurement;
2. adds an automated smoke test or equivalent enforced check that runs this documented
   benchmark entry point far enough to detect constructor-contract drift;
3. searches all non-baseline current-version call sites and confirms that no supported
   `QueryEngine` construction omits either authorization scope or `source_root`;
4. reruns the full test, Ruff, mypy, `git diff --check`, unchanged-vault, and both benchmark
   harness checks;
5. reports the new exact HEAD and correction diff while preserving the equivalent
   total-pipeline p95 gate.

The compatibility branches in `scripts/benchmark_regression.py` that deliberately load the
v0.3 baseline are not subject to the v0.3.1 constructor and must remain narrowly bounded to
that comparison.

## R4.7 Explicit architecture disposition

**REFRACTOR FIRST.**

AC-03R3-02 is closed, AE-01R2 remains closed at +12.6%, and all earlier closed findings
remain unregressed. AC-03R3-01 is not fully closed because the documented current-version
benchmark is an unmigrated `QueryEngine` boundary and cannot run with the mandatory
current-source contract.

Commit `649e5a2ecfc98b2c4c9f23b5456716bb5f05f7f9` is returned to engineering for the
bounded correction in R4.6.

## R4.8 Quality & Release status

**Quality & Release is not authorized to begin.**

No adversarial QA matrix is activated and no QA artifact is authorized for this HEAD.
After a future exact-HEAD CTO clearance, the required Quality & Release output remains:

```text
docs/handovers/v0.3.1/05-quality-to-product-owner-release-review.md
```

Stop at this CTO disposition. Do not perform the Quality & Release role.

---

# Exact-HEAD CTO Clearance Revision 5

**Date:** 2026-07-27

**Role:** Chief Architect / CTO

**Supersedes:** Final Superseding CTO Revision 4 above

**Reviewed branch:** `feature/v0.3.1-query-trust-contracts`

**Reviewed HEAD:** `09a4ca5a6e0d9b73a1e37a9e086abe788c894c72`

**Prior candidate:** `649e5a2ecfc98b2c4c9f23b5456716bb5f05f7f9`

**Chief-of-Staff return commit:** `b58a42b8b09d44cf8953bf6cdb8a698daa5c84e1`

**Correction diff:** `649e5a2ecfc98b2c4c9f23b5456716bb5f05f7f9..09a4ca5a6e0d9b73a1e37a9e086abe788c894c72`

## R5.1 Exact-state verification

Before this clearance was appended, the worktree was clean. The checked-out branch and
HEAD matched the exact values above. Both the prior candidate and Chief-of-Staff return
commit are ancestors of the reviewed HEAD. The correction contains:

- the Chief-of-Staff routing record;
- the two-call-site benchmark correction;
- one benchmark smoke-test module; and
- the Rev 5 engineering evidence and coordination updates.

The implementation diff is confined to `scripts/benchmark_query.py` and
`tests/integration/test_benchmark_smoke.py`. No production query, authorization, citation,
result-contract, CLI, compatibility-reader, context-budget, or graph code changed.
`git diff --check` is clean.

## R5.2 AC-03R3-01 closure

Every current-version benchmark construction now supplies both an explicit authorization
scope and the current synthetic-vault root:

- the per-size warm-up uses
  `QueryEngine(notes, scope=scope, source_root=root)`;
- the 1,000-note memory path uses
  `QueryEngine(notes, scope=scope, source_root=root)`; and
- the candidate path in `scripts/benchmark_regression.py` continues to use
  `QueryEngine(notes, scope=_SCOPE, source_root=root)`.

The current `src`, `scripts`, and `tests` call-site audit found no positive current-version
construction lacking either argument. Calls that omit one or both arguments are limited
to explicit fail-closed contract tests and the v0.3 compatibility branches described
below.

The new smoke tests load the documented scripts by file path and:

1. call `benchmark_query.bench(5, 1, scope)`, executing the warm-up construction;
2. call the complete `benchmark_query.main()` with a small measured size, which reaches
   both the warm-up and fixed 1,000-note memory construction and then asserts the memory
   and authorization-stress completion markers; and
3. call `benchmark_regression.main()` with a small fixture and assert its
   `total_pipeline` output.

An omitted future `scope` or `source_root` at either corrected current-version site would
raise before these assertions and fail the integration suite. The test therefore detects
the constructor-contract drift returned in Revision 4.

**AC-03R3-01 is closed.**

## R5.3 Baseline adapter confinement

`scripts/benchmark_regression.py` first attempts the complete current candidate signature:

```text
QueryEngine(notes, scope=_SCOPE, source_root=root)
```

Its adaptive scope-only and no-argument branches exist solely so the same harness can load
the historical v0.3 implementation, whose constructor does not accept the v0.3.1
arguments. On the current implementation, omitting `source_root` and then omitting both
arguments still fails closed; the fallback cannot produce a current-version engine or
weaken current citation validation. The smoke test confirms that the candidate path
completes through the full signature.

This remains an acceptable, narrowly bounded benchmark compatibility adapter. It is not a
general legacy reader or production construction path.

## R5.4 Regression and performance assessment

The correction does not alter retrieval, graph, authorization, context, citation,
rendering, result, or persistence behavior. All previously closed findings and accepted
contracts therefore remain unmodified and unregressed:

- AC-01 authorization ordering and excluded-source non-disclosure;
- AC-02 canonical path-prefix authorization;
- duplicate-ID fail-closed handling;
- AC-03R3-02 supported-versus-incomplete evidence semantics;
- AC-04R2 strict, bounded legacy reading;
- exact-byte/current-source citation validation;
- full locator and heading-hierarchy validation;
- claim-specific retrieval binding, including metadata evidence;
- hard context-budget accounting;
- relevance and answer-confidence separation;
- ADR-0012 layering and ADR-0014 through ADR-0017;
- local, offline, read-only operation.

The benchmark correction supplies a required constructor argument outside the measured
stage and does not change the total-pipeline harness or gate semantics. The accepted
equivalent total-pipeline result remains:

| Version | Total-pipeline p95 |
|---|---:|
| v0.3 baseline | 33.812 ms |
| v0.3.1 candidate | 38.075 ms |
| Regression | +12.6% |

**AE-01R2 remains closed:** +12.6% is within the accepted +20% ceiling.

## R5.5 Security, architecture, and debt assessment

All supported citation-producing boundaries now require a current source root. Snapshot
bytes cannot independently yield `coverage="supported"`. Current path confinement,
symlink confinement, missing-file handling, and post-discovery exact-byte mutation checks
remain fail closed.

Supported citations and incomplete references remain visibly and structurally distinct in
text and JSON. Incomplete locators are not rendered as `0-0` passage citations, and
incomplete-only answers retain warning/not-fully-evidence-backed semantics.

No new architectural coupling or technical debt was introduced. The previously recorded
bounded debt remains: before adding another repository implementation, replace direct
filesystem current-source resolution in orchestration with a small read-only
source-revision resolver port.

## R5.6 Explicit architecture disposition

**READY FOR QUALITY & RELEASE.**

The exact candidate
`feature/v0.3.1-query-trust-contracts@09a4ca5a6e0d9b73a1e37a9e086abe788c894c72`
conforms to the accepted v0.3.1 architecture and trust contracts. AC-03R3-01 and
AC-03R3-02 are closed, all earlier findings remain closed, and the equivalent performance
gate remains satisfied.

This clearance applies only to the exact HEAD above. Any code, test, contract, benchmark,
or dependency change requires renewed disposition of the changed scope.

## R5.7 Quality & Release authorization

**Quality & Release is explicitly authorized to begin** against:

- **Branch:** `feature/v0.3.1-query-trust-contracts`
- **Exact HEAD:** `09a4ca5a6e0d9b73a1e37a9e086abe788c894c72`
- **Architecture evidence:** this Revision 5, Engineering Review Rev 5, ADR-0012 and
  ADR-0014 through ADR-0017, correction diff `649e5a2..09a4ca5`, and the complete
  implementation evidence accumulated in Engineering Reviews Rev 1 through Rev 5.
- **Required QA output:**
  `docs/handovers/v0.3.1/05-quality-to-product-owner-release-review.md`

Quality & Release must remain read-only except for its required review artifact. It must
not fix defects, merge, push, or change the candidate.

## R5.8 Activated adversarial QA matrix

Quality & Release must independently execute and record every matrix area below.

### A. Candidate identity and evidence integrity

1. Verify exact branch, HEAD, clean starting worktree, ancestry, and the complete release
   diff.
2. Confirm the reviewed implementation and evidence all refer to the same exact HEAD.
3. Run the full test suite, Ruff, mypy, and `git diff --check`.
4. Verify unchanged-vault/read-only evidence before and after representative commands.
5. Identify any untracked, generated, environment-specific, or unreviewed release input.

### B. Authorization and non-disclosure

1. Exercise workspace mismatch, sensitivity limits, source allowlists, path-prefix
   allowlists, empty scopes, and explicit deny cases.
2. Test traversal, absolute paths, mixed separators, dot segments, prefix-segment
   collisions, case behavior, and canonicalization.
3. Confirm authorization precedes index construction, candidate generation, graph
   resolution/expansion, context assembly, and citation construction.
4. Verify excluded source identity and content do not leak through results, excerpts,
   citations, traces, conflicts, errors, counts, graph paths, or ordering/timing-derived
   diagnostics.
5. Confirm ambiguous duplicate stable IDs fail closed and disclose neither candidate.

### C. Current-source and citation trust boundary

1. Verify every supported CLI, direct-engine, benchmark, and test-helper construction
   requires explicit scope and a valid `source_root`.
2. Exercise omitted and explicit-`None` roots, nonexistent roots, roots that are files,
   missing sources, unreadable sources, and sources replaced after discovery.
3. Exercise lexical traversal, resolved traversal, symlink/junction escape, symlink target
   mutation, and path confinement at segment boundaries.
4. Mutate current bytes after discovery using content changes, whitespace-only changes,
   BOM changes, CRLF/LF changes, encoding changes, and other changes that normalize to the
   same parsed text; all stale citations must fail closed.
5. Confirm snapshot-only evidence can never become `coverage="supported"`.
6. Verify exact-byte fingerprints, stable identity, additive line/heading provenance,
   full heading hierarchy, locator bounds, excerpt equality, and non-empty excerpts.
7. Test title-, tag-, alias-, frontmatter-, heading-, body-, and relationship-derived
   retrieval signals; a supported citation must bind to the actual material signal.
8. Confirm mandatory validation occurs immediately before emission and catches mutation
   between discovery and answer construction.

### D. Evidence coverage and consumer semantics

1. Exercise supported-only, mixed supported/incomplete, incomplete-only, and no-citation
   answers.
2. Verify text output visibly separates supporting passages from incomplete references.
3. Verify no incomplete `0-0` locator is rendered as a passage citation.
4. Verify JSON structurally distinguishes supported citations, incomplete references, and
   answer-level coverage.
5. Validate coverage labels, supported/incomplete counts, and limitation text for every
   combination.
6. Confirm incomplete-only answers return warning/not-fully-evidence-backed status for
   `ask`, `query`, `context`, and `brief`, including text and JSON modes.
7. Confirm a reference without a validated locator/excerpt is never counted or presented
   as claim-supporting material.

### E. Retrieval, ranking, graph, and context

1. Test deterministic candidate generation and ranking across repeated runs.
2. Verify retrieval relevance remains distinct from answer confidence in memory and every
   serialized contract.
3. Exercise graph cycles, missing targets, ambiguous targets, excluded neighbors, high
   fan-out, and depth limits.
4. Confirm graph paths cannot bypass authorization or reveal excluded nodes.
5. Verify the hard context budget for empty, minimal, exact-boundary, one-byte-over,
   multibyte, many-passage, and wrapper/separator-heavy cases.
6. Count every emitted byte/token unit required by the accepted budget contract,
   including headings, labels, separators, and wrappers.

### F. Versioning and compatibility

1. Validate current result and citation contract versions and all required fields.
2. Exercise the legacy reader with exact valid legacy shapes.
3. Reject missing keys, unknown keys, mixed old/new shapes, result/citation shape
   confusion, invalid nested citations, invalid ranking values, and unequal legacy/new
   ranking aliases.
4. Confirm ambiguous `confidence` is removed and never becomes answer confidence.
5. Verify the legacy path is reader-only, bounded to the accepted release window, and
   cannot relax current authorization or citation validation.

### G. CLI, exit behavior, and operational safety

1. Exercise `ask`, `query`, `context`, and `brief` in text and JSON modes for success,
   warning, policy failure, invalid input, and internal failure paths.
2. Verify stdout/stderr separation, deterministic JSON, stable exit codes, and no
   unsupported evidence claims.
3. Confirm local/offline behavior and absence of network, subprocess, write, deletion,
   rename, permission, timestamp, or vault-content mutation.
4. Test malformed configuration, empty vaults, scale limits, Unicode paths/content, and
   platform-relevant path behavior.

### H. Benchmark and release gate

1. Run `scripts/benchmark_query.py` through its warm-up, measured sizes, memory
   measurement, and authorization-stress phases.
2. Run `tests/integration/test_benchmark_smoke.py` and confirm constructor drift at either
   corrected site would fail it.
3. Run `scripts/benchmark_regression.py` against the exact v0.3 baseline and exact
   v0.3.1 candidate using identical fixture, query, warm-ups, sample count, percentile
   method, machine, Python version, and construction-plus-query boundary.
4. Record raw samples or a reproducible evidence location, candidate and baseline p95,
   percentage change, peak memory, and authorization-stress behavior.
5. Confirm the release result remains no more than 20% above the equivalent v0.3 p95.
6. Verify baseline-only adaptive constructor branches cannot instantiate the current
   candidate without both scope and `source_root`.

### I. QA disposition and handoff

The QA artifact must list exact branch, HEAD, environment, commands, results, failures,
waivers, residual risks, and evidence locations. It must issue one explicit Quality &
Release disposition to the Product Owner. Any failure involving authorization ordering,
non-disclosure, path confinement, exact-byte currentness, citation support, hard context
budget, contract ambiguity, read-only behavior, or the 20% performance ceiling is
release-blocking unless returned through governance and explicitly superseded.

## R5.9 Exit statement

Architecture review is complete. Quality & Release is authorized only for exact HEAD
`09a4ca5a6e0d9b73a1e37a9e086abe788c894c72` and must produce:

```text
docs/handovers/v0.3.1/05-quality-to-product-owner-release-review.md
```

Stop after this CTO disposition. Do not perform the Quality & Release review.
