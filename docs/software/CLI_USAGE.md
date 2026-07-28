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
| `jarvis resume "<selector>" [--path <dir>] [--trace]` | Assemble a deterministic, sourced project briefing (v0.4). |

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
| 0 | Success / validation OK / complete supported briefing |
| 1 | Fatal error (bad path, project not found, validation errors) / internal failure |
| 2 | Completed with validation warnings, a query returned no matches, or a partial briefing |
| 3 | `resume`: ambiguous project selector (candidates shown, none chosen) |
| 4 | `resume`: project not found (no substitute) |
| 5 | `resume`: invalid input or identity |
| 6 | `resume`: policy error |
| 7 | `resume`: budget error |

Codes 3–7 are `resume`-specific and extend the existing convention without reassigning 0/1/2.

## Examples
```bash
jarvis inspect tests/fixtures/ai-operating-system --format json
jarvis validate tests/fixtures/edge-cases            # exit 1: contains a syntax error
jarvis load-project "AIOS" --path tests/fixtures/ai-operating-system --format json
jarvis summarize-project "FileOrbit" --path tests/fixtures/fileorbit
jarvis vault-report tests/fixtures/edge-cases          # exit 1: contains errors
jarvis vault-report /path/to/real/ObsidianVault        # real vault, read-only
```

## Project Resume (v0.4)

`jarvis resume "<selector>"` assembles a deterministic, fully-sourced project briefing over
the released read-only trust pipeline. It selects exactly one project by exact tier (canonical
id → title → alias → filename stem), never substitutes a near match, and reports ten fixed
sections: project, current state, next action and priorities, accepted decisions, recent
sessions, open tasks and questions, resources, repository activity, conflicts/staleness/missing
context, and evidence coverage and omissions. Every material claim is bound to a passage-and-
revision citation validated against current bytes immediately before output; unsupported claims
are shown as incomplete, never as verified. Output is stdout only (no product output-file path).

```bash
jarvis resume "Alpha" --path /path/to/vault
jarvis resume "Alpha" --path /path/to/vault --format json --trace
jarvis resume "Alpha" --path /path/to/vault --as-of 2026-07-28T00:00:00Z
jarvis resume "Alpha" --path /path/to/vault \
  --include-repository-activity --repository-root /path/to/local/git/repo
```

Resume-specific options:

- `--as-of <ISO-8601-UTC>` — explicit evaluation time for staleness and byte-determinism
  (defaults to now). Pass it for reproducible output.
- `--evidence-budget <256..32000>` / `--output-budget <256..16000>` — two independent hard
  budgets. The final serialization is measured before emission; over-budget results shed the
  lowest-priority claims or fail closed with exit code 7 rather than truncating output.
- `--include-repository-activity --repository-root <local-git-root>` — enable local, read-only
  Git activity for this one invocation. Both flags are required together; repository activity is
  denied by default and never inferred from a URI or vault content. An unavailable or
  non-matching repository degrades to a limitation while local vault evidence stays usable.
- `--trace` — add a non-disclosing trace: contract/index/repository versions, workspace
  fingerprint, explicit evaluation time, safe authorization summary, selected identity/tier,
  discovery channels, included evidence identities, coverage, budgets, and isolated timings.
  Excluded identities and rejected ambiguity candidates are never disclosed.

## v0.3.1 query trust contracts

`ask`, `search`, `summarize`, and `explain` run under an explicit local authorization scope
(`local_allow_all`). Sources list a passage locator (`relpath:line_start-line_end`) and a
**relative relevance** value — never "confidence" — plus the reason selected. If policy
excludes any sources, an aggregate `(<n> source(s) excluded by policy)` line is shown; the
excluded identities and content are never disclosed. `--trace` additionally shows the
request id, workspace fingerprint, contract/index version, and a safe authorization summary.
See [Query Trust Contracts](QUERY_TRUST_CONTRACTS.md).
