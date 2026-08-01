# Changelog

| Field | Value |
|---|---|
| Purpose | Record notable project changes |
| Status | Active |
| Version | 0.1.0 |
| Owner | Jason |
| Revised | 2026-07-27 |
| Related | [Roadmap](docs/ROADMAP.md) |

This project follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and intends to use semantic versioning once application releases begin.

## [Unreleased]

### Added — Read-only Project Resume (v0.4, in progress)

Read-only, offline project briefing assembled over the v0.3.1 trust pipeline (ADR-0018–0021).
Release evidence — reference-hardware benchmarks, the 30s pilot latency gate, non-author
clean-Windows packaging, and the eight-week dogfood scorecard — remains **PENDING**; the
mechanisms are built and tested, results are not fabricated.

- Exact tiered project selection (ADR-0018): canonical id → title → alias → filename stem; the
  first matching tier controls; exactly one match selects, ambiguity returns safe candidates
  without choosing, no match returns not-found without substitution, duplicate/malformed
  identity fails closed. `jarvis_core.project_resume.identity`.
- Typed evidence discovery over the authorized view — canonical passage, `projects` metadata,
  authorized relationships (bounded BFS), and project-bound retrieval — with dedup by identity +
  fingerprint, cycle termination, configured caps, and bounded non-disclosing omissions.
- Explicit authority/temporal/supersession/conflict ordering (ADR-0019): typed authority class
  and dated/undated/stale state from explicit dates and the request evaluation time; supersession
  only via an explicit resolved reference; materially conflicting top-class claims are retained
  and marked, never merged or silently chosen.
- Claim-to-current-citation binding and coverage (ADR-0020) through the reusable query-layer
  citation service; supported vs incomplete are distinct; metadata claims cite the metadata
  locator.
- Two hard budgets (ADR-0020): evidence and full-output, measured on the final serialization,
  shedding lowest-priority claims or failing closed with `budget_error`; trace charged to a
  sub-budget inside the output budget.
- Request-scoped, denied-by-default local read-only Git activity (ADR-0021): a distinct capability
  port with a deterministic fixture adapter and a hard-capped, allowlisted-environment,
  three-command subprocess adapter; typed redacted degradation; exact granted-root canonicalization.
- Frozen versioned result/trace/repository contracts with deterministic `to_dict()`; text and JSON
  rendered from one semantic result; non-disclosing trace with isolated timings.
- CLI: `jarvis resume "<selector>"` (`--path/--format/--trace/--as-of/--evidence-budget/
  --output-budget/--include-repository-activity/--repository-root`) and the read-only
  `jarvis resume-doctor` diagnostic + derived-state rebuild. Exit codes extend the existing
  `0/1/2` convention with `3` ambiguous, `4` not-found, `5` invalid, `6` policy, `7` budget.
- Tooling: `scripts/benchmark_project_resume.py` (per-stage + total latency, peak memory) and
  `scripts/evaluate_project_resume.py` + `evaluations/v0.4-project-resume-dogfood-template.tsv`
  (offline dogfood aggregation, no telemetry). Guide: `docs/software/PROJECT_RESUME.md`.

## [0.3.1] - 2026-07-27

### Added — Query Trust Contracts

Released from merge `00f1813` with Product Owner approval, independent QA disposition
**Ready**, Librarian disposition **Ready for final release**, and frozen executable
`956c2ed`.

- Authorization before retrieval (ADR-0015): immutable `AuthorizationScope` on every query
  entry point; sensitivity/allowlist filtering applied before the request-visible index and
  graph are built; fail-closed on unknown policy/sensitivity; only an aggregate
  `excluded_count` is disclosed. `jarvis_core.policy` package.
- Retrieval relevance renamed to `relative_relevance` (ADR-0014); no numeric answer
  confidence is emitted (`answer_confidence` reserved/null).
- Passage-and-revision citations (ADR-0016): stable `source_id`, `source_fingerprint`
  (SHA-256 of exact bytes), deterministic heading-path + line-range locator, bounded
  excerpt, and citation validation (stale/out-of-range/excerpt-mismatch). Parser retains
  exact-source provenance additively.
- Stable source identity separate from location and revision (ADR-0017); duplicate explicit
  IDs fail closed.
- Hard context-budget invariant `0 <= total_tokens <= token_budget` with deterministic
  separator accounting and typed truncation/omission reasons.
- Versioned results/citations/context/trace (`contract_version: jarvis.query.v0.3.1`,
  distinct `index_version`); single-release legacy `confidence` compatibility reader.
- CLI runs under an explicit local allow-all scope; text/JSON use relevance terminology and
  passage citations; trace adds request id, workspace fingerprint, index/contract version,
  and a safe authorization summary.
- Benchmark reports p50/p95/p99 per stage plus peak memory and an authorization-stress
  case. The retained five-attempt paired protocol reports an 11.56% median p95 regression
  against v0.3, within the accepted 20% aggregate gate; individual-attempt variance,
  including results above 20%, remains disclosed in release evidence.
- Final independent QA recorded 198 passing tests and one environment-limited skipped
  symlink test, with Ruff and mypy passing. No chat, streaming, real-provider, Project
  Resume, or write capability was introduced.
- Retained evidence:
  [paired performance samples](docs/evidence/v0.3.1/paired-performance-956c2ed-vs-ce0dc35.json),
  [QA disposition](docs/handovers/v0.3.1/05-quality-to-product-owner-release-review.md),
  and [Product Owner decision](docs/handovers/v0.3.1/06-product-owner-to-librarian-release-decision.md).

### Added (v0.3 — Intelligent Query Engine foundation, merged)

- Dedicated query layer under `jarvis_core.query`, composed of small, injectable
  collaborators: `tokenizer`, `LexicalIndex` (inverted index over title/aliases/tags/
  filename/frontmatter/wikilinks/body), `IntentParser`, `Ranker` (deterministic,
  explainable), `QueryContextBuilder` (token-budgeted), `results` (citations), and
  `trace`. No embeddings, vectors, or background indexing.
- Deterministic, explainable ranking: every result carries per-signal contributions and
  a confidence (relative to the top hit). Weights are configurable via `RankingWeights`.
- Source citations on every answer: title, relative path, confidence, and reason.
- New CLI commands `search`, `summarize`, and `explain`, plus `--trace` on `ask`, which
  shows intent, candidates, ranking explanation, selected/excluded context, provider,
  timings, and token counts.
- `explain_relationship` intent: describes how two notes connect (direct link and/or
  shared neighbours).
- Query benchmark harness (`scripts/benchmark_query.py`) and scale tests at
  100/500/1,000 notes; ranking backlink counts precomputed to keep scoring linear.
- 55 new tests (124 total): tokenizer, index, intent, ranking, context builder, engine
  edge cases (alias/tag/duplicate-title/broken-link/missing-frontmatter/empty), CLI
  commands, trace, and performance guardrails. Existing behaviour (`ask`/`QueryResult`)
  is preserved.

### Added (Phase 2 — Real Vault Pilot, in review)

- `jarvis ask` — an offline, deterministic query engine over the vault (summarize a
  project, find projects mentioning a term, list notes related to a term, keyword
  search). No AI provider, network, or keys.
- Versioned JSON report envelope (`schemaVersion`, `generatedBy`, `timestamp`,
  `vaultVersion` content fingerprint); `--deterministic` omits the timestamp.
- Finer performance stages (disk read vs metadata vs markdown parse vs graph) plus
  graph-size, note-cache-size, and opt-in peak-memory (`--memory`) metrics.

- Real Obsidian-vault loading from a configurable directory (still strictly read-only).
- Performance instrumentation (`jarvis_core.metrics`): per-stage timings for parse,
  relationship resolution, validation, and total runtime, with throughput.
- Vault health analyzer and `jarvis vault-report` command: missing frontmatter,
  duplicate IDs, orphan notes, broken wikilinks, invalid schemas, missing aliases, and
  circular references, rendered as a human-readable report (file output opt-in).
- Synthetic-vault generators and scale tests at 100/500/1,000 notes plus a
  one-of-each-defect vault; 54 tests total.

### Planned

- Validate the accepted two-project knowledge pilot through daily use.
- Review and approve the migration execution plan before broader vault changes.

### Added

- Jarvis v1 foundation package: definitive AI behavior constitution, 260-case query benchmark, reusable prompt library, demo vault design, multi-surface UX specification, competitive analysis, Jarvis Bible, quality checklists, and executive recommendations.
- Standing Architecture Review Board procedure for independent review after each major implementation.
- `SYSTEM_PRINCIPLES.md` as the enduring project-governance philosophy.
- Accepted ADR-0004 establishing project dashboards as the primary navigation layer.
- Accepted ADR-0005 requiring inventory before significant modification.
- Migration runbook, storage architecture, naming/taxonomy, automation/synchronization architecture, and architecture decision matrix.
- Product strategy and implementation-gated release roadmap through v2.0.
- Ten capability PRDs covering chat, agents, plugins, memory, search, graph, dashboard, mobile, automation, and MCP.
- Enterprise architecture, product/platform, and comprehensive security reviews.
- Eight bounded reference agent specifications and the public plugin SDK design.
- Developer experience strategy and 100-item future research backlog.
- Executive product and architecture summary with pre-coding decision gates.
- ADR-0007 through ADR-0011 covering read-only defaults, plugin manifests, proposal-based memory, provider abstraction, and MCP isolation.

## [0.1.0] - 2026-07-27

### Added

- Foundational product, architecture, behavior, schema, and roadmap documents.
- The BRAIN v2 master specification.
- Initial Architecture Decision Records.
- Obsidian note templates and machine-readable schema.
- Contribution, issue, pull request, and documentation validation configuration.

## Revision history

| Version | Date | Change |
|---|---|---|
| 0.3.1 | 2026-07-27 | Released Query Trust Contracts with retained trust and performance evidence |
| 0.2.0 | 2026-07-27 | Reconciled v0.3 foundation and locally merged v0.3.1 release state |
| 0.1.0 | 2026-07-27 | Initial changelog |
