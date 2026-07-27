# ADR-0012: The Query Engine Is a Layered, Deterministic, Citation-Based Pipeline

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-07-27 |
| Deciders | Jason |
| Related | [ADR-0007](ADR-0007-Read-Only-Is-The-Default-Operating-Mode.md), [ADR-0010](ADR-0010-AI-Providers-Are-Accessed-Through-A-Versioned-Abstraction.md), [Search PRD](../prd/SEARCH_ENGINE.md), [System Principles](../SYSTEM_PRINCIPLES.md), [Querying](../software/QUERYING.md) |

## Context

v0.2 shipped a small offline `ask` prototype whose routing, retrieval, and ranking lived
inside a single class. v0.3 must grow this into a useful query engine — lexical search,
explainable ranking, context assembly, source citations, and a trace mode — without
introducing any write capability (ADR-0007) and without letting a specific AI provider
leak into query logic (ADR-0010).

A single expanding class would become a "God object": routing, indexing, scoring, and
context building would couple together and resist testing. The Search PRD also anticipates
a later index projection and hybrid lexical/vector ranking, so the retrieval and ranking
seams need to be explicit now.

### Roadmap reconciliation

The repository's [Version Roadmap](../product/VERSION_ROADMAP.md) frames v0.3 as
"Read-only Chat and Provenance" (chat UI, provider adapters, citations). The v0.3
build brief in hand frames it as an "Intelligent Query Engine" (query layer, lexical
search, ranking, context, citations, trace, and the `ask`/`search`/`summarize`/`explain`
commands). These overlap on the load-bearing themes — read-only, provenance/citations,
provider abstraction, deterministic context. This ADR implements the query-engine framing
and treats the conversational chat UI and cloud/Ollama provider adapters as the remaining,
still-open part of the v0.3 milestone. No architectural decision is reversed; the chat
surface is deferred, not cancelled.

## Decision

The query engine is a layered pipeline of small, single-responsibility modules under
`jarvis_core.query`, wired by constructor injection:

1. `tokenizer` — pure deterministic tokenization/normalization (no stemming/embeddings).
2. `index.LexicalIndex` — inverted index + per-note field token counts over title,
   aliases, tags, filename, frontmatter, wikilinks, and body.
3. `intent.IntentParser` — text → `ParsedQuery`. The only place free text is parsed.
4. `ranking.Ranker` — deterministic, explainable scoring driven by a configurable
   `RankingWeights`; every hit carries per-signal contributions and a relative confidence.
5. `context_builder.QueryContextBuilder` — token-budgeted, provider-independent expansion
   of ranked seeds along the resolved graph.
6. `results` / `trace` — citations and an inspectable per-run trace.
7. `engine.QueryEngine` — orchestration only. It exposes the stable v0.2 `ask()` and the
   v0.3 `run`/`search`/`summarize`/`explain` surface, and reaches providers solely through
   the `Provider` abstraction.

Determinism is a hard requirement: identical question + vault + weights → byte-identical
output. Ties break on relative path; the optional recency signal is off by default.

## Alternatives considered

### Keep one growing query class

Rejected: routing, indexing, ranking, and context assembly have different reasons to
change and different test surfaces; fusing them produces a God object and brittle tests.

### Introduce embeddings / a vector index now

Rejected for v0.3 (explicitly out of scope). Lexical-first keeps results deterministic and
explainable and avoids a vector store dependency. The layering leaves a clean seam for a
later hybrid ranker that fuses with — rather than replaces — lexical search.

### Persist an on-disk index / background watcher

Rejected for v0.3. The in-memory index rebuilt per run is simple, correct, and fast enough
at target sizes; a persisted projection is a later concern (Search PRD) and a background
watcher is explicitly deferred.

## Tradeoffs

- More modules and explicit contracts than a single class (more files, clearer seams).
- The index is rebuilt per run, so very large vaults pay a construction cost each
  invocation; acceptable at v0.3 target sizes and bounded near-linearly.
- Lexical-only retrieval cannot match synonyms or paraphrases; this is documented and is
  the job of a later semantic version.

## Consequences

- Retrieval, ranking, and context each have an isolated test surface; all are pure over
  their inputs.
- A real AI answerer can plug in behind the same context pipeline via the provider
  abstraction without touching query logic.
- Every answer is traceable to sources with a confidence and reason, satisfying the
  provenance requirement shared by both v0.3 framings.
- `ask()`/`QueryResult` remain backwards compatible; existing callers and tests are
  unaffected.

## Revisit conditions

Revisit when adding hybrid semantic ranking, a persisted/incremental index, or
sensitivity-scoped retrieval — each of which the Search PRD anticipates and each of which
this layering is designed to accommodate without a rewrite.
