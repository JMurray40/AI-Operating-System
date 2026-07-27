# Querying the Vault — `jarvis ask`

`jarvis ask` answers questions from the vault **offline and deterministically**. It does
NOT call an AI model, use the network, or require API keys — it routes a question to a
structured intent and answers from the graph and a keyword index. It is the read-only
foundation a future AI-backed `ask` can build on.

```bash
jarvis ask "Summarize the FileOrbit project."
jarvis ask "What projects mention QuickBooks?"
jarvis ask "Show every note related to Home Automation." --path /path/to/vault
jarvis ask "invoices" --format json
```

## Intents

| Pattern | Intent | Answer |
|---|---|---|
| "summarize \<project>" | `summarize_project` | Builds the project context package and returns a deterministic summary + source notes. |
| "what/which projects mention \<term>" | `projects_mentioning` | Projects whose own text or a linked note mentions the term. |
| "show/list notes related to \<term>" | `related_to` | Notes matching the term plus their one-hop graph neighbours. |
| anything else | `search` | Keyword search across all notes, ranked by frequency. |

Output is text (answer + `Sources:` list) or JSON (`--format json`) with `intent`,
`answer`, and `matches`. Exit code is `0` when something was found (or a project summary
was produced) and `2` when nothing matched.

## Guarantees & limits

- **Read-only** and offline; no model, no keys, no writes.
- **Deterministic**: identical question + vault → identical output (stable ordering).
- Matching is **keyword/graph based**, not semantic. Synonyms and paraphrases are not
  understood — that is the job of the future AI adapter, which will plug in behind the
  same context pipeline (`Vault → Parser → Graph → Context → answer`).
