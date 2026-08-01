# Chief of Staff to Principal Engineer — v0.4 Implementation Authorization

| Field | Value |
|---|---|
| Sender | Chief of Staff |
| Receiver | Principal Engineer |
| Milestone | v0.4 — Read-only Project Resume CLI Pilot |
| Date | 2026-07-27 |
| Status | **Authorized for implementation** |
| Repository | `AI-Operating-System` |
| Immutable implementation base | `3253b052a3986e7d2c94124fbac86c03980e0765` |
| Branch | `feature/v0.4-project-resume` |
| Worktree | `C:\Users\jmurr\Projects\AI-Operating-System\.worktrees\v0.4-engineering` |
| Required engineering handoff | `docs/handovers/v0.4/02-principal-engineer-to-cto-engineering-review.md` |

## Role and primary question

Act as Principal Engineer. Implement the accepted v0.4 Project Resume vertical slice while
preserving every v0.3.1 trust boundary and the four accepted Project Resume ADRs.

Conversation history and verbal summaries are not authoritative. Read
[Project Control](../../coordination/README.md), the [v0.4 Index](README.md), and the
[Final CTO Implementation Brief](01-cto-to-principal-engineer-implementation-brief.md)
before planning or changing code.

## Authorization and startup verification

The Product Owner authorized v0.4 implementation. The CTO architecture package was
validated, committed to `main`, and published as exact immutable base:

```text
3253b052a3986e7d2c94124fbac86c03980e0765
```

The engineering branch was created directly from that commit. This authorization and
the associated routing updates are the branch's first documentation-only child commit,
so the Principal Engineer's starting `HEAD` is expected to be one authorized coordination
commit after the immutable implementation base.

Before implementation:

1. verify the worktree path and branch above;
2. verify the worktree is clean;
3. verify `3253b052a3986e7d2c94124fbac86c03980e0765` is the branch's implementation base;
4. verify the diff from that base to starting `HEAD` contains only this authorization and
   v0.4 coordination/index updates;
5. verify ADR-0018 through ADR-0021 and the final CTO brief are present;
6. verify released executable `956c2ed1dd1144e836014b049a89c47e971818a0`
   is an ancestor;
7. verify no commit unique to `feature/v0.4-conversation` is present; and
8. verify the parked conversation worktree is not modified.

Stop and report any mismatch.

## Required planning behavior

Before editing implementation files, present a concise implementation plan that:

- maps work increments to A1–A12 and ADR-0018 through ADR-0021;
- identifies contract, CLI, local-Git, security, fixture, benchmark, packaging, privacy,
  and documentation increments;
- names the intended logical commit boundaries;
- identifies tests/evidence run at each boundary; and
- surfaces only genuinely unresolved architecture or product decisions.

The implementation is already authorized. After presenting the plan, proceed without
waiting for routine approval unless a mandatory escalation point in the CTO brief is
triggered. Do not silently decide an unresolved architecture, scope, privacy, write,
network, or capability question.

## Binding scope

Implement the [Final CTO Implementation Brief](01-cto-to-principal-engineer-implementation-brief.md)
in full, including:

- exact authorized project selection and ambiguity handling;
- explicit authority, temporal, supersession, conflict, and staleness semantics;
- revision-bound material claims and visible coverage;
- independent hard evidence and serialized-output budgets;
- deterministic semantic results and safe trace;
- fixture plus explicitly granted local read-only Git activity only;
- deterministic text and JSON `jarvis resume` output;
- typed degradation without loss of safe local-vault usefulness;
- A1–A10 and A12 technical evidence;
- the A11 consented/manual collection mechanism with eight-week strategic results left
  explicitly pending;
- packaging, non-author, recovery, performance, pilot, privacy, and unchanged-source
  evidence; and
- all required documentation and final engineering handoff.

The exact base, accepted tests, ADRs, final brief, and this authorization together define
the implementation contract. A lower-precedence planning document cannot broaden it.

## Local Git boundary

ADR-0021 is exact. Use only its three fixed argument-array command shapes with
`shell=False`. In the log command, every global `-c` option—including
`-c i18n.logOutputEncoding=UTF-8`—must appear before `-C <root>` and the `log`
subcommand.

Do not add GitHub, network, credentials, remote discovery, arbitrary Git commands,
user-supplied Git options/revisions/pathspecs, or a generic connector framework.

## Explicit exclusions

Do not implement or import:

- visible-context or multi-turn chat;
- any commit or code from `feature/v0.4-conversation`;
- providers, generation, streaming, or egress;
- durable conversation state or memory;
- vault writes, migrations, repairs, or briefing persistence;
- embeddings, vectors, or persisted semantic indexes;
- plugins, MCP, agents, tools/actions, automation, watchers, or background services;
- dashboard UI, mobile, voice, team, marketplace, or enterprise work;
- live GitHub, remote APIs, credentials, fetch, pull, or network access; or
- unrelated refactors.

Do not modify, switch, merge, rebase, stash, reset, stage, or otherwise touch the parked
conversation worktree.

## Evidence and repository controls

- Keep commits logical and reviewable; do not amend completed milestone commits.
- Preserve unrelated user changes.
- Never write to canonical pilot vaults or Git repositories.
- Store private pilot evidence only in the approved ignored destination.
- Commit only redacted evidence allowed by the CTO brief.
- Treat Git subjects/authors and vault text as untrusted data.
- Retain raw benchmark samples and bind evidence to the exact candidate SHA.
- Record skips, deviations, unavailable pilot access, environmental limitations, and
  unproven A11 outcomes honestly.
- Do not claim technical or strategic completion when its required evidence is absent.

## Required checks and handoff

Satisfy every check and evidence destination in the final CTO brief. At minimum, complete
the full existing and new test suite, Ruff, mypy, whitespace checks, unchanged-vault/Git
proof, security tests, benchmarks, packaging/recovery evidence, both pilot evaluations,
privacy review, and exclusion audit.

Produce:

```text
docs/handovers/v0.4/02-principal-engineer-to-cto-engineering-review.md
```

The handoff must satisfy Section 27 of the final CTO brief, pin exact base and candidate
HEAD, map A1–A12 and all ADRs to evidence, disclose anything incomplete, and recommend an
exact CTO review range.

Stop after the clean engineering candidate and handoff are committed. Do not perform the
CTO or QA reviews, merge, push, tag, release, or begin v0.5 work.

## Exit statement

**AUTHORIZED FOR PRINCIPAL ENGINEER IMPLEMENTATION** on
`feature/v0.4-project-resume` from immutable base
`3253b052a3986e7d2c94124fbac86c03980e0765`.
