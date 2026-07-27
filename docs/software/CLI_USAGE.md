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
| `jarvis ask "<question>" [--path <dir>]` | Answer a question from the vault, offline and deterministic. |

`<name>` matches a project note's title, alias, id, or filename stem.

## Common options
- `--path <dir>` — vault/fixture directory (defaults to bundled sample fixtures).
- `--format text|json` — output format (default `text`).
- `--log-level DEBUG|INFO|WARNING|ERROR` — default `INFO`.
- `--max-files N` — discovery cap (default 5000).
- `--provider mock` — only the mock provider is available in this prototype.
- `--model-role <role>` — role alias for `summarize-project` (default `fast`).
- `--timing / --no-timing` — include performance metrics in `vault-report` (default on).
- `--output <file>` — also write the `vault-report` output to a file (opt-in; off by default).
- `--memory` — capture peak memory in `vault-report` (opt-in; adds overhead).
- `--deterministic` — omit the `vault-report` timestamp for reproducible snapshots.

## Exit codes
| Code | Meaning |
|---|---|
| 0 | Success / validation OK |
| 1 | Fatal error (bad path, project not found, validation errors) |
| 2 | Completed with validation warnings (non-fatal) |

## Examples
```bash
jarvis inspect tests/fixtures/ai-operating-system --format json
jarvis validate tests/fixtures/edge-cases            # exit 1: contains a syntax error
jarvis load-project "AIOS" --path tests/fixtures/ai-operating-system --format json
jarvis summarize-project "FileOrbit" --path tests/fixtures/fileorbit
jarvis vault-report tests/fixtures/edge-cases          # exit 1: contains errors
jarvis vault-report /path/to/real/ObsidianVault        # real vault, read-only
```
