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
