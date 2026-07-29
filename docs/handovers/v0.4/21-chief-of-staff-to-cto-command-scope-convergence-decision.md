# Handoff 21 — Chief of Staff to CTO: Command-scope Convergence Decision

**Date:** 2026-07-29

**Disposition:** **PAUSE ENGINEERING — CTO ARCHITECTURE DECISION REQUIRED**

**Current candidate:** `a7292fd71aa678d10c66c1645340e54199060045`

## Why this decision is required

Handoff 20 introduces four more blocking requirements around an ephemeral global-config
file. One requirement also tightens an option explicitly permitted by Handoff 17:
Handoff 17 allowed stable before/after identity, content, owner, and ACL verification as
an alternative to a held binding; Handoff 20 now rejects that approach because a transient
replace/use/restore interval remains.

Engineering should not add another temporary-file security layer until the CTO evaluates
whether the file is needed at all.

## Verified simpler mechanism

Current Git documentation defines **command scope** as including both:

- `git -c key=value`; and
- `GIT_CONFIG_COUNT`, `GIT_CONFIG_KEY_<n>`, and `GIT_CONFIG_VALUE_<n>`.

It also defines system, global, and command scopes as protected configuration. Modern
`safe.directory` is honored from protected configuration.

Primary reference:
[Git configuration scopes and protected configuration](https://git-scm.com/docs/git-config.html#SCOPES).

The Chief of Staff performed a read-only process-boundary check on the approved current-PC
Git 2.55.0 Windows runtime, with:

- `GIT_TEST_ASSUME_DIFFERENT_OWNER=1`;
- system configuration disabled;
- global configuration pointed at the null file; and
- the exact canonical Survivor Group Tracker root supplied as the single command-scope
  `safe.directory` value.

Results:

```text
command-scope environment configuration: exit 0, exact root returned
same command without safe.directory: exit 128
```

No repository file, Git configuration, ownership, ref, index, worktree, object, pilot, or
classification was changed.

## Recommended architecture

Replace the entire ephemeral-file mechanism with exactly three additional allowlisted child
environment entries created only after the existing exact grant/root validation:

```text
GIT_CONFIG_COUNT=1
GIT_CONFIG_KEY_0=safe.directory
GIT_CONFIG_VALUE_0=<exact canonical granted root>
```

Retain:

- `GIT_CONFIG_NOSYSTEM=1`;
- `GIT_CONFIG_GLOBAL` pointed at the null file;
- the existing environment built from scratch;
- exact grant/project/root checks;
- exact top-level equality;
- shell-free subprocess execution;
- redaction and caps; and
- the three accepted Git command arrays byte-for-byte unchanged.

This removes rather than mitigates every Handoff 20 blocker:

| Handoff 20 blocker | Command-scope effect |
|---|---|
| Stale-artifact provenance | No artifact or sweep exists |
| Junction/reparse cleanup | No cleanup traversal exists |
| Transient replace/use/restore | No named config file exists to replace |
| Untyped `mkdtemp` failure | No temporary directory is created |

The value is passed as one environment value directly to Git, not parsed by a shell or Git
config-file syntax. It must still be the already-resolved exact granted root and must never
be `*`, a parent wildcard, or an unvalidated user string.

## Compatibility decision

Older Git documentation excluded command-line `safe.directory`; modern Git documentation
includes command scope in protected configuration. The CTO must therefore:

1. accept a documented minimum supported Git version whose official behavior includes
   command-scope protected configuration; or
2. reject command scope and explicitly freeze the more complex file-based acceptance matrix.

The approved A10/A12 current-PC runtime is Git 2.55.0 and passes the mechanism.

## Required CTO output

Produce one frozen, final disposition choosing either:

### Option A — Recommended: command-scope environment

- approve the three exact environment entries above;
- identify the minimum supported Git version;
- authorize deletion of the ephemeral-file/ACL/stale-cleanup subsystem;
- freeze one complete acceptance matrix, including absence of config artifacts and exact
  different-owner success/denial behavior; and
- state that no additional temporary-file lifecycle requirement applies.

### Option B — File mechanism

- reject command scope with a concrete compatibility or security reason;
- freeze the complete final file-lifecycle acceptance matrix, including the exact required
  held-handle mechanism and authenticated stale-artifact format; and
- state that satisfying that matrix closes the boundary without later tightening.

## Gate state

Do not return Handoff 20 directly to Engineering until this architecture decision is made.
No code change, wheel, A10, A12, QA, merge, push, tag, release, pilot change, classification
change, or v0.5 work is authorized.
