# ADR-0013: Conversation Is a Read-Only, Session-Only Layer over the Query Engine

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-07-27 |
| Deciders | Jason |
| Related | [ADR-0007](ADR-0007-Read-Only-Is-The-Default-Operating-Mode.md), [ADR-0010](ADR-0010-AI-Providers-Are-Accessed-Through-A-Versioned-Abstraction.md), [ADR-0012](ADR-0012-Query-Engine-Is-A-Layered-Deterministic-Pipeline.md), [Chat PRD](../prd/CHAT_INTERFACE.md), [Memory PRD](../prd/MEMORY_SYSTEM.md) |

## Context

v0.4 adds multi-turn conversation so a user can ask follow-ups ("What is FileOrbit?" →
"Who is working on it?" → "What are its risks?") without repeating themselves. This
introduces conversation *state* — the first mutable, cross-turn state in Jarvis. Done
carelessly, that state becomes a back door to persistence, provider coupling, or vault
writes, all of which prior ADRs forbid (ADR-0007 read-only; ADR-0010 provider abstraction).

The roadmap slots "Read-only Chat and Provenance" here; the Chat PRD requires visible
provenance, streaming, provider independence, and that retrieved text be treated as data,
not instructions. Memory (durable, proposal-based) is explicitly a *later* version
(Memory PRD / v0.5) and must not be pulled forward.

## Decision

Conversation is a thin, read-only, **session-only** layer composed over the v0.3 query
engine, not a rewrite of it.

- **State is isolated from retrieval.** A `conversation` package owns session state
  (`ConversationSession`), reference resolution (`ReferenceResolver`), provenance/taxonomy
  (`explanation`, `results`), streaming events, and orchestration (`ConversationManager`).
  Retrieval stays in `query`; the manager resolves references, hands a plain query to the
  engine, and enriches the result. The two never merge.
- **Memory is session-only and in-process.** Turns and entity memory live in RAM for the
  active process. No disk writes, no conversation logs, no vault mutation. Ending the
  process ends the memory. Persistent/durable memory remains deferred to v0.5.
- **Provenance is mandatory.** Every answer carries citations (source, confidence,
  reason), a reasoning summary, an explicit statement taxonomy
  (fact / inference / relationship / unknown / assumption), and any conflicting evidence.
- **Reference resolution is deterministic and explainable.** Pronouns/ellipsis resolve to
  the most-recent in-focus entity via a pure function of (input, entity stack); every
  resolution is recorded as an `assumption` the user can see.
- **Providers stay behind the abstraction.** Streaming is an *optional* capability
  (`SupportsStreaming`) added beside the existing `Provider` contract; conversational logic
  never depends on a concrete provider. Provider failures degrade gracefully (a `failed`
  answer/event; the vault is untouched).
- **Retrieved text is data, not instructions** (Chat PRD req. 9): the conversation layer
  only reads titles/relpaths/fields, never executes note content.

## Alternatives considered

### Fold conversation into the query engine

Rejected: it would couple mutable session state to the deterministic, stateless retrieval
core and blur the ADR-0012 layering. Keeping conversation as a separate composed layer
preserves testability and keeps the query engine pure.

### Persist conversation history to disk now

Rejected: transcripts-as-durable-knowledge is precisely what the Memory PRD defers, and
any write path re-opens the read-only question (ADR-0007). Session-only memory delivers the
follow-up experience with zero persistence risk.

### Add a streaming method to the base `Provider` contract

Rejected: it would force every provider to implement streaming. An optional
`SupportsStreaming` protocol keeps the core contract minimal and streaming truly optional.

## Tradeoffs

- Conversation memory is lost when the process ends (no resume). Acceptable for v0.4; a
  deliberate boundary, not a gap.
- Reference resolution is heuristic (most-recent focus, token-overlap ambiguity), so exotic
  anaphora may resolve imperfectly — but always visibly, as a stated assumption.
- Two answer surfaces (`QueryAnswer`, `ConversationAnswer`) now coexist; the conversational
  one wraps the query one rather than replacing it.

## Consequences

- The follow-up experience ships without any new persistence or write capability.
- Every conversational answer is auditable to sources with an explicit basis taxonomy.
- A future durable-memory subsystem (v0.5) can consume session turns as *proposals* without
  changing this layer's read-only stance.
- Provider adapters (cloud/Ollama) can be added later behind `Provider`/`SupportsStreaming`
  without touching conversation logic.

## Revisit conditions

Revisit when durable memory (v0.5) introduces an approved write path, or when a real
streaming provider is integrated — neither changes the read-only, session-only default
established here.
