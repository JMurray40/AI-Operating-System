# Querying the Vault — `ask`, `search`, `summarize`, `explain`

The query engine answers questions from the vault **offline and deterministically**. It
does NOT call an AI model over the network or require API keys — it routes a question to a
structured intent and answers from a lexical index and the resolved graph. It is the
read-only foundation a future AI-backed answerer can build on, plugging in behind the same
`Vault → Parser → Graph → Index → Rank → Context → answer` pipeline.

```bash
jarvis ask "Summarize the FileOrbit project."
jarvis ask "What projects mention QuickBooks?"
jarvis ask "Show every note related to Home Automation." --trace
jarvis search "QuickBooks" --path /path/to/vault
jarvis summarize "Home Automation"
jarvis explain "Project A" "Project B"
```

## Intents

| Pattern | Intent | Answer |
|---|---|---|
| "summarize \<project>" | `summarize_project` | Builds the project context package and returns a deterministic summary + cited sources. |
| "what/which projects mention \<term>" | `projects_mentioning` | Projects whose own text or a linked note mentions the term. |
| "show/list notes related to \<term>" | `related_to` | Notes matching the term plus their one-hop graph neighbours. |
| "relationship between \<A> and \<B>" | `explain_relationship` | Whether two notes are directly linked and which notes they share. |
| anything else | `search` | Ranked lexical search across all notes. |

## Ranking

Ranking is deterministic and explainable. A note's score is the sum of weighted signals:

| Signal | Meaning |
|---|---|
| `exact_title` / `exact_alias` | The query phrase equals the note's title / an alias. |
| `title` / `alias` / `tag` / `filename` / `frontmatter` / `wikilink` / `body` | Term frequency in that field (body is capped to avoid keyword stuffing). |
| `graph_proximity` | The note is a one-hop neighbour of a strong direct match. |
| `backlinks` | Incoming links (capped) — a light authority signal. |
| `recency` | Optional; **off by default** so results are reproducible across clock time. |

Weights live in `RankingWeights` (one source of truth, no magic numbers in the ranker).
Ties break on relative path, so identical inputs always produce identical output. Each
result reports the exact signals that contributed, e.g.
`title_match (+12); filename_match (+6); body_match (+1)`.

## Citations

Every answer lists its sources: title, relative path, a **confidence** (0–1, relative to
the top hit), and a **reason** (the ranking signals that selected it, or the role the note
played in an assembled context). You should always be able to see where an answer came
from.

## Trace mode

`jarvis ask "…" --trace` prints a full record of how the answer was produced: the parsed
intent and terms, the candidate notes, the per-signal ranking explanation, the context
selected and what was excluded (and why), the provider, per-stage timings, and token
counts. It is the first tool to reach for when a question returns something surprising.

## Guarantees & limits

- **Read-only** and offline; no model, no keys, no writes, no background indexing.
- **Deterministic**: identical question + vault → identical output (stable ordering).
- **Lexical, not semantic**: synonyms and paraphrases are not understood — that is the job
  of a future semantic-search version, which will fuse with (not replace) lexical search.
- The index is in-memory and rebuilt per run; there is no persisted index in v0.3.

## v0.3.1 note

Ranking values are now labelled **relative relevance** (a query-local normalization), not
confidence, and no numeric answer confidence is produced. Every query runs under an
authorization scope, and citations bind a passage (heading path + line range) to an exact
source revision (fingerprint). See [Query Trust Contracts](QUERY_TRUST_CONTRACTS.md).
