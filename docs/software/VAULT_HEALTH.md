# Vault Health & Performance (Phase 2)

Phase 2 adds real-vault support, performance instrumentation, and a vault health
report. Everything remains **strictly read-only**: no file is created, modified,
renamed, or deleted, and `.obsidian/` is never read.

## Running it

```bash
jarvis vault-report /path/to/your/Obsidian/Vault
jarvis vault-report /path/to/vault --format json
jarvis vault-report /path/to/vault --no-timing
jarvis vault-report /path/to/vault --output health.txt   # file output is OPT-IN
```

The report is generated **in memory** and printed. A file is written only when
`--output` is supplied (disabled by default).

## Health checks

| Category | Severity | Meaning |
|---|---|---|
| Missing frontmatter | warning | Note has no YAML frontmatter. |
| Duplicate IDs | error | Two or more notes share the same `id`. |
| Orphan notes | warning | No resolved incoming or outgoing links. |
| Broken wikilinks | warning | A link/reference target does not resolve. |
| Invalid schemas | error | Frontmatter fails syntax/shape/vocabulary/integrity (per `VAULT_SCHEMA.md`). |
| Missing aliases | info | Filename differs from the title and no alias covers the filename. |
| Circular references | info | A cycle of links (Tarjan strongly-connected component). Advisory — reciprocal links are normal in Obsidian. |

Interpretation notes:
- **Missing aliases** flags a real Obsidian pitfall: if a file is named differently from
  its title and no alias bridges them, links by the other name silently break. It is
  informational, not a failure.
- **Circular references** are reported for awareness only. Bidirectional links between a
  dashboard and its notes are expected and healthy; review only if a cycle implies a
  modelling problem.

## Exit codes
`vault-report` returns `0` (healthy), `2` (warnings only), or `1` (any error-severity
finding), matching the rest of the CLI.

## Report structure
`SUMMARY` (vault, note count, findings by category) · `PERFORMANCE` (per-stage timings) ·
`ERRORS` · `WARNINGS` · `INFO` · `RECOMMENDATIONS`.

## Performance instrumentation

Per-stage wall-clock timings (`time.perf_counter`) are collected for **parse**,
**resolve**, **validate**, and **total**, plus note count and throughput. Include them
with `--timing` (default on) or omit with `--no-timing`. Also available programmatically
via `jarvis_core.metrics.PerfReport`.

### Measured throughput (synthetic vaults, build sandbox)

| Notes | Parse | Resolve | Validate | Total | Throughput |
|---|---|---|---|---|---|
| 100 | 32 ms | 0.4 ms | 0.8 ms | 34 ms | ~3,000 notes/s |
| 500 | 168 ms | 1.9 ms | 3.9 ms | 175 ms | ~2,900 notes/s |
| 1,000 | 321 ms | 4.0 ms | 7.5 ms | 335 ms | ~3,000 notes/s |

Runtime is linear in note count and dominated by file I/O during parsing. Numbers are
indicative (sandbox hardware); treat them as relative, not absolute.
