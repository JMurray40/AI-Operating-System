# CLI Usage

`jarvis` is read-only. It never writes to the directory it scans.

## Commands

| Command | Purpose |
|---|---|
| `jarvis inspect <path>` | Discover and parse notes; print counts, types, and parse errors. |
| `jarvis validate <path>` | Validate notes across the five schema stages. |
| `jarvis load-project "<name>" [--path <dir>]` | Assemble and print a project context package. |
| `jarvis summarize-project "<name>" [--path <dir>] [--provider mock]` | Send the package to a provider. |

`<name>` matches a project note's title, alias, id, or filename stem.

## Common options
- `--path <dir>` — vault/fixture directory (defaults to bundled sample fixtures).
- `--format text|json` — output format (default `text`).
- `--log-level DEBUG|INFO|WARNING|ERROR` — default `INFO`.
- `--max-files N` — discovery cap (default 5000).
- `--provider mock` — only the mock provider is available in this prototype.
- `--model-role <role>` — role alias for `summarize-project` (default `fast`).

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
```
