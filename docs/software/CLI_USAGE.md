# CLI Usage

`jarvis` is read-only. It never writes to the directory it scans.

## Commands

| Command | Purpose |
|---|---|
| `jarvis inspect <path>` | Discover and parse notes; print counts, types, and parse errors. |
| `jarvis validate <path>` | Validate notes across the five schema stages. |
| `jarvis load-project "<name>" [--path <dir>]` | Assemble and print a project context package. |
| `jarvis summarize-project "<name>" [--path <dir>] [--provider mock]` | Send the package to a provider. |
| `jarvis vault-report <path>` | Analyze a vault and print a read-only health report (with timings). |
| `jarvis ask "<question>" [--path <dir>] [--trace]` | Answer a question from the vault, offline and deterministic. |
| `jarvis search "<terms>" [--path <dir>] [--limit N]` | Ranked lexical search with cited sources. |
| `jarvis summarize "<name>" [--path <dir>]` | Summarize a project with cited sources. |
| `jarvis explain "<A>" "<B>" [--path <dir>]` | Explain how two notes are related. |

`<name>` matches a project note's title, alias, id, or filename stem.

## Query commands (v0.3)

`ask`, `search`, `summarize`, and `explain` share the read-only query engine. Every
answer lists its sources with a confidence (0–1, relative to the top hit) and the reason
it was selected. Ranking is deterministic and lexical only — synonyms and paraphrases are
not understood (that is a later semantic-search version).

`--trace` (on `ask`) shows exactly how an answer was produced: parsed intent, candidate
notes, per-signal ranking explanation, the context selected and what was excluded (and
why), the provider, per-stage timings, and token counts. Use it to debug why a question
returned what it did.

```bash
jarvis search "QuickBooks" --path /path/to/vault
jarvis summarize "FileOrbit" --path tests/fixtures/fileorbit
jarvis explain "FileOrbit" "File Deduplication" --path tests/fixtures/fileorbit
jarvis ask "What projects relate to bookkeeping?" --trace --path /path/to/vault
```

## Common options
- `--path <dir>` — vault/fixture directory (defaults to bundled sample fixtures).
- `--format text|json` — output format (default `text`).
- `--log-level DEBUG|INFO|WARNING|ERROR` — default `INFO`.
- `--max-files N` — discovery cap (default 5000).
- `--provider mock` — only the mock provider is available in this prototype.
- `--model-role <role>` — role alias for `summarize-project` (default `fast`).
- `--trace` — on `ask`, show intent, ranking, context, provider, timings, and tokens.
- `--limit N` — on `search`, cap the number of ranked results (default 20).
- `--timing / --no-timing` — include performance metrics in `vault-report` (default on).
- `--output <file>` — also write the `vault-report` output to a file (opt-in; off by default).
- `--memory` — capture peak memory in `vault-report` (opt-in; adds overhead).
- `--deterministic` — omit the `vault-report` timestamp for reproducible snapshots.

## Exit codes
| Code | Meaning |
|---|---|
| 0 | Success / validation OK |
| 1 | Fatal error (bad path, project not found, validation errors) |
| 2 | Completed with validation warnings, or a query returned no matches |

## Examples
```bash
jarvis inspect tests/fixtures/ai-operating-system --format json
jarvis validate tests/fixtures/edge-cases            # exit 1: contains a syntax error
jarvis load-project "AIOS" --path tests/fixtures/ai-operating-system --format json
jarvis summarize-project "FileOrbit" --path tests/fixtures/fileorbit
jarvis vault-report tests/fixtures/edge-cases          # exit 1: contains errors
jarvis vault-report /path/to/real/ObsidianVault        # real vault, read-only
```

## v0.3.1 query trust contracts

`ask`, `search`, `summarize`, and `explain` run under an explicit local authorization scope
(`local_allow_all`). Sources list a passage locator (`relpath:line_start-line_end`) and a
**relative relevance** value — never "confidence" — plus the reason selected. If policy
excludes any sources, an aggregate `(<n> source(s) excluded by policy)` line is shown; the
excluded identities and content are never disclosed. `--trace` additionally shows the
request id, workspace fingerprint, contract/index version, and a safe authorization summary.
See [Query Trust Contracts](QUERY_TRUST_CONTRACTS.md).
