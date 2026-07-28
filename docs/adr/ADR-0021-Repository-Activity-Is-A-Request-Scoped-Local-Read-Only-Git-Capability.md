# ADR-0021: Repository Activity Is a Request-Scoped Local Read-Only Git Capability

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-07-27 |
| Deciders | Product Owner and Chief Architect / CTO |
| Related | ADR-0003, ADR-0007, ADR-0015, v0.4 Acceptance Tests A3, A7, A9 |

## Context

v0.4 may include deterministic fixture activity and local read-only Git activity. Live
GitHub, credentials, network access, plugins, MCP, and a generic connector framework are
excluded. A subprocess boundary can still introduce path escape, argument injection,
unbounded output, hangs, environment/config influence, error disclosure, and repository
mutation.

## Decision

Project Resume depends on a narrow `RepositoryActivityPort`, not on `subprocess`:

```text
load_activity(project_id, repository_root, grant, evaluation_time)
  -> RepositoryActivitySnapshot
   | RepositoryActivityDenied
   | RepositoryActivityUnavailable
   | RepositoryActivityMalformed
   | RepositoryActivityStale
```

Two adapters are accepted:

1. deterministic fixture adapter, independent of an installed Git executable; and
2. local read-only Git adapter.

No network adapter or generic capability framework is accepted.

### Capability and path boundary

Repository activity is denied by default. A frozen request-scoped grant binds:

- workspace ID;
- selected canonical project ID;
- one canonical repository root;
- operation `read_recent_commits`;
- maximum records;
- timeout and output caps; and
- policy/contract version.

The adapter resolves the requested path strictly, rejects missing/non-directory roots,
rejects traversal and symlink/junction escape from the granted root, and confirms that
`git rev-parse --show-toplevel` resolves exactly to that root. It does not discover parent,
sibling, remote, submodule, or linked repositories implicitly.

### Permitted process invocations

Commands are argument arrays with `shell=False`. No user text becomes an option, revision,
format string, pathspec, environment assignment, or shell fragment. Only these operations
are permitted:

1. repository-root verification using fixed `git --no-pager -C <root> rev-parse
   --show-toplevel`;
2. current HEAD object identity using fixed `git --no-pager --no-replace-objects -C <root>
   rev-parse --verify HEAD`; and
3. bounded first-parent commit activity using fixed `git --no-pager --no-replace-objects
   -c color.ui=false -c core.pager=cat -c core.fsmonitor=false
   -c i18n.logOutputEncoding=UTF-8 -C <root> log --no-color --no-decorate
   --first-parent --date=iso-strict
   --pretty=format:%H%x00%cI%x00%an%x00%s%x00 --max-count=<N> HEAD`.

`N` is generated from a validated integer in the grant, bounded to 1–50. No other Git
subcommand, flag, revision, ref, pathspec, config mutation, fetch, remote, status, diff,
submodule, worktree, maintenance, credential, or hook operation is allowed.

### Environment and execution

The child environment starts from an allowlist, not an inherited copy. It includes only
the platform process essentials (`PATH`; fixed `TMP`/`TEMP`; and on Windows `SystemRoot`,
`COMSPEC`, and `PATHEXT`) plus:

- `PATH` only as needed to locate the approved Git executable;
- `GIT_CONFIG_NOSYSTEM=1`;
- `GIT_CONFIG_GLOBAL` to the platform null file;
- `GIT_OPTIONAL_LOCKS=0`;
- `GIT_TERMINAL_PROMPT=0`;
- `GIT_PAGER=cat` and `PAGER=cat`;
- `LC_ALL=C`, `LANG=C`, and `TZ=UTC`;
- a fixed temporary directory outside the repository when required.

It removes Git directory/worktree/index/object overrides, alternates, config injection,
askpass, SSH, proxy, credential, pager, editor, and tracing variables. No stdin is
provided.

Each command has a five-second default timeout, configurable only downward/up to a hard
ten-second maximum. The process group is terminated on timeout. Stdout is capped at 1 MiB
and stderr at 8 KiB; overflow returns `unavailable`. Error output is classified and
redacted to an allowlisted code/message and never exposes command lines, environment,
absolute paths, usernames, remote URLs, credentials, or raw stderr.

### Deterministic parsing and evidence

The log format is NUL-delimited and parsed as exact groups of four fields: full object ID,
committer ISO timestamp, author display name, and subject. Malformed field counts, invalid
object IDs/timestamps, invalid encoding, duplicates, or cap violations return
`malformed`; partial output is not accepted.

Records sort by committer timestamp descending and object ID ascending. The semantic
snapshot contains canonical repository identity, HEAD object ID, records, contract
version, and a SHA-256 fingerprint over the exact normalized record bytes. Wall-clock
capture time is diagnostics only. Staleness uses the request's explicit evaluation time
and configured threshold.

### Read-only proof and test seams

The adapter exposes no write method. Integration evidence inventories and hashes
worktree files and material Git metadata (`HEAD`, refs, config, index, and packed refs)
before and after execution and confirms unchanged Git status/content. Tests inject:

- a `ProcessRunner` protocol for deterministic success, timeout, overflow, malformed, and
  redaction cases without installed Git;
- the fixture activity adapter;
- temporary real Git repositories for process-boundary tests when Git is available.

Tests must prove no hooks, network, credentials, or repository mutations occur.

## Consequences

- Local Git failure yields a typed limitation while local vault evidence remains usable.
- “Unavailable” is not rendered as “no activity.”
- Repository activity requires explicit request authorization separate from note scope.
- Git object IDs and snapshot fingerprints provide revision-bound evidence.
- The adapter is deliberately narrow and is not reusable authority for future commands.

## Alternatives rejected

- Use GitHub/API access: rejected by Product Owner scope.
- Run arbitrary read-looking Git commands: rejected because argument and config surfaces
  are too broad.
- Use `shell=True`: rejected due to injection risk.
- Inherit the full environment: rejected due to credential, config, proxy, and path
  influence.
- Parse human default output: rejected because it is locale/config dependent.
- Treat failure as empty activity: rejected because missing evidence is not zero.
