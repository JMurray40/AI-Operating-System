# Conversation — `jarvis chat`

`jarvis chat` turns the read-only query engine into a multi-turn conversation. You can ask
follow-ups without repeating yourself, and every answer shows exactly where it came from and
how it was reached. It is **read-only and session-only**: conversation memory lives only for
the running process — nothing is written to disk, no transcript is logged, and the vault is
never modified (see [ADR-0013](../adr/ADR-0013-Conversation-Is-A-Read-Only-Session-Only-Layer.md)).

```bash
# Scripted, deterministic multi-turn (great for testing and demos):
jarvis chat --path /path/to/vault \
  --turns "What is FileOrbit?" "Who is working on it?" "What are its biggest risks?"

# Interactive session over stdin:
jarvis chat --path /path/to/vault
# then type questions; in-session commands: :history  :reset  :trace  :help  :exit
```

## How a turn works

```
user input
   ↓  ReferenceResolver         resolve "it"/"its"/… to the in-focus entity
resolved query
   ↓  QueryEngine (v0.3)        retrieve → rank → cite (unchanged, deterministic)
query answer
   ↓  ConversationManager       add provenance: facts / inferences / relationships /
                                unknowns / assumptions, plus conflicting evidence
conversational answer  +  session update (entity memory, turn history)
```

Conversation state is **isolated from retrieval**. The manager resolves references and hands
a plain query to the engine; the engine knows nothing about the conversation.

## Reference resolution

Pronouns and elliptical follow-ups ("it", "its", "they", "what about it?") resolve to the
most recently discussed entity. Resolution is deterministic and always surfaced as an
assumption you can see:

```
> What is FileOrbit?          → focus becomes "FileOrbit"
> Who is working on it?       → 'it' refers to 'FileOrbit' (most recently discussed)
```

If recent turns covered **unrelated** topics, the reference is flagged ambiguous and Jarvis
notes that it chose the most recent entity.

## Provenance on every answer

Each answer includes:

- **Reasoning summary** — a one-line "how I got here."
- **Confidence** — 0–1, relative to the strongest source.
- **Basis** — an explicit statement taxonomy, each item tagged:
  - `fact` — stated directly in a source note.
  - `relationship` — a resolved link between notes.
  - `inference` — derived from ranking/graph proximity, not stated verbatim.
  - `unknown` — asked for but not found (e.g., no owner information).
  - `assumption` — a resolution choice Jarvis made (e.g., what "it" refers to).
- **Sources** — cited notes with relative path, confidence, and the reason selected.
- **Conflicting evidence** — when multiple notes disagree (e.g., two notes share a title or
  an id), they are surfaced rather than silently merged.

## Trace mode

`--trace` (or `:trace` in an interactive session) shows the full picture for each turn:
conversation state (resolved input, focus entity, entity memory), then the underlying query
trace (candidates, ranking explanation, context, provider, timings, tokens).

## Streaming

`--stream` streams the answer text as it is produced. Streaming is **optional** and a
display concern only — the content is identical and deterministic either way. Under the hood
it uses normalized events (`started`, `delta`, `citation`, `usage`, `completed`, `failed`)
so any front end shares behavior. Providers opt into streaming via the `SupportsStreaming`
capability; the base provider contract is unchanged.

## Guarantees & limits

- **Read-only, session-only**: no persistence, no logs, no vault writes; memory ends with
  the process.
- **Deterministic**: the same turns on the same vault produce identical answers.
- **Lexical, not semantic**: follow-up *context* is tracked, but retrieval is still
  keyword/graph based — synonyms and paraphrases are a later semantic version.
- **Provider failures degrade gracefully**: a failed provider yields a `failed` answer with
  no partial fabrication; the vault is untouched.
- **No memory/agents**: durable memory, autonomous planning, and tool execution are out of
  scope (deferred to later versions).
