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

### Added (v0.4 — Read-Only Conversational Intelligence, in review)

- Conversation layer under `jarvis_core.conversation` (read-only, session-only; see
  ADR-0013), composed over the v0.3 query engine with state isolated from retrieval:
  `ConversationSession` (in-memory turns + entity memory + token budget),
  `ReferenceResolver` (deterministic pronoun/ellipsis resolution), `explanation`
  taxonomy, `ConversationAnswer` provenance, `StreamEvent`, `ConversationTrace`, and
  `ConversationManager`.
- Multi-turn follow-ups: pronouns ("it", "its", …) resolve to the in-focus entity; every
  resolution is surfaced as a visible assumption; unrelated recent topics flag ambiguity.
- Provenance on every answer: reasoning summary, confidence, an explicit
  fact / inference / relationship / unknown / assumption basis, cited sources, and
  conflicting-evidence detection.
- Optional streaming via a `SupportsStreaming` provider capability (base `Provider`
  contract unchanged); normalized events (started/delta/citation/usage/completed/failed);
  graceful provider-failure handling.
- New CLI command `jarvis chat` (scripted `--turns`, interactive stdin with
  `:history`/`:reset`/`:trace`, plus `--trace` and `--stream`).
- Conversation benchmark (`scripts/benchmark_conversation.py`) and scale tests at
  100/500/1,000/5,000 notes; reference resolution is negligible/constant overhead.
- 32 new tests (156 total): reference resolution, session/entity memory, taxonomy,
  conflicting notes, provider failure, streaming, trace, CLI chat, and scale.
- No persistent memory, no vault writes, no embeddings/vectors, no agents or MCP.

### Added (v0.3 — Intelligent Query Engine, in review)

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
| 0.1.0 | 2026-07-27 | Initial changelog |
