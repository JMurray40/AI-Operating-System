# Handoff 22 — CTO Command-Scope `safe.directory` Convergence Decision

**From:** Chief Architect / CTO  
**To:** Chief of Staff; Principal Engineer after Chief-of-Staff activation  
**Date:** 2026-07-29  
**Scope:** Bounded v0.4 Project Resume local-Git architecture convergence  
**Status:** **OPTION A SELECTED AND FROZEN — COMMAND-SCOPE CONFIGURATION APPROVED**

## 1. Authoritative inputs

This disposition is based on:

- Handoff 20, `20-cto-to-principal-engineer-independent-temp-root-security-review.md`;
- Handoff 21, `21-chief-of-staff-to-cto-command-scope-convergence-decision.md`;
- the Chief-of-Staff Windows Git 2.55 process-boundary result recorded in Handoff 21;
- ADR-0021 and its authorization-before-local-Git, read-only, privacy, and fixed-command invariants; and
- the documented Git configuration-scope boundary between Git 2.37.4 and Git 2.38.0.

The previously reviewed candidate remains:

`a7292fd71aa678d10c66c1645340e54199060045`

It is not architecture-cleared. Its file-based temporary configuration design is superseded by this decision.

## 2. Explicit architecture disposition

**DISPOSITION: OPTION A IS APPROVED AND FROZEN.**

For an authorized repository request, Jarvis may supply exactly one process-scoped Git configuration value:

```text
GIT_CONFIG_COUNT=1
GIT_CONFIG_KEY_0=safe.directory
GIT_CONFIG_VALUE_0=<exact canonical granted repository root>
```

The value is passed only in the environment of the three already accepted ADR-0021 repository-activity commands. System configuration and ambient global configuration remain disabled. No persistent or temporary Git configuration file is permitted.

This is a request-scoped authorization projection, not a relaxation of Git ownership protection. Without a valid exact-root grant, Jarvis must not supply `safe.directory`, and repository activity remains unavailable.

## 3. Minimum supported Git version

The minimum supported Git version for authorized Project Resume repository activity is:

**Git 2.38.0**

Reason:

- Git 2.37.4 documentation expressly stated that `safe.directory` was not respected when supplied through `GIT_CONFIG_*` environment variables or `-c`.
- Git 2.38.0 documentation defines `GIT_CONFIG_COUNT`, `GIT_CONFIG_KEY_<n>`, and `GIT_CONFIG_VALUE_<n>` as command-scope configuration; defines protected configuration as system, global, and command scopes; and states that `safe.directory` is respected only in protected configuration.
- The approved Windows Git 2.55 runtime has independently demonstrated the required different-owner behavior with the exact environment mechanism and with system/global configuration disabled.

Primary references:

- [Git 2.37.4 `git-config`](https://git-scm.com/docs/git-config/2.37.4)
- [Git 2.38.0 `git-config`](https://git-scm.com/docs/git-config/2.38.0)

Git versions below 2.38.0 are unsupported for granted repository activity. If the version is missing, unparsable, below the floor, or cannot be bound to the invocation, Jarvis must fail closed with a typed, redacted unavailable result. It must not fall back to a configuration file, user/global configuration, repository configuration, ownership mutation, or a relaxed command.

The existing fixed `git --version` capability diagnostic may establish the version without a repository path. It is not a repository-activity command and may not be expanded into additional repository inspection. The three ADR-0021 repository command arrays remain the complete repository-activity allowlist.

## 4. Exact command-scope contract

For every granted repository request, all of the following are mandatory:

1. Authorization completes before any repository-activity subprocess starts.
2. The request project identity equals the grant project identity.
3. The requested repository root, granted root, and actual canonical root are the same exact canonical directory.
4. Canonicalization resolves existing path components and rejects traversal, aliases, ambiguous relative paths, non-directories, and repository escape.
5. The configured value is the exact canonical granted root. It is never a parent, child, prefix, pattern, or inferred root.
6. Empty values, `*`, wildcard forms, interpolation forms, NUL, CR, LF, and any noncanonical representation are rejected.
7. The subprocess environment is constructed from an allowlist. Ambient `GIT_CONFIG_*` variables are not inherited.
8. The command-scope configuration is exactly:
   - `GIT_CONFIG_COUNT` equal to ASCII `1`;
   - `GIT_CONFIG_KEY_0` equal to ASCII `safe.directory`; and
   - `GIT_CONFIG_VALUE_0` equal to the exact canonical granted root.
9. No additional indexed Git configuration key or value is supplied.
10. `GIT_CONFIG_NOSYSTEM=1` remains set.
11. `GIT_CONFIG_GLOBAL` remains bound to the platform null device.
12. The same validated environment contract is used for all three accepted commands in that request.
13. The configuration value and private root never appear in logs, traces, returned errors, snapshots, exception text, or telemetry.
14. The three accepted Git command arrays remain byte-for-byte unchanged. This decision authorizes an environment-only change.
15. Git commands remain read-only and must not mutate repository configuration, ownership, worktree bytes, index, refs, reachable objects, or remotes.
16. Any missing grant, mismatched grant, failed canonicalization, unsupported Git version, Git denial, or environment-integrity failure produces a typed unavailable result and no repository snapshot.

## 5. Handoff 20 findings

The absence of any configuration artifact closes the architectural causes identified in Handoff 20:

- **provenance and authentication:** there is no reusable named artifact whose origin must be proven;
- **reparse-safe stale cleanup:** there is no stale configuration namespace or cleanup traversal;
- **transient named-file substitution:** there is no named configuration file to replace before or during Git consumption; and
- **`mkdtemp` confinement and post-create races:** no temporary directory is created.

The file/ACL/owner/SID/held-handle/stale-sweep subsystem is therefore not hardened further. It is removed in full. Retaining dormant fallback code is prohibited because it would preserve an unapproved alternate trust path and unnecessary security debt.

## 6. Bounded Engineering correction authorized after activation

After Chief-of-Staff activation, Engineering is authorized only to:

1. remove the complete temporary-file, ACL, SID namespace, stale-cleanup, and artifact-authentication subsystem used for local-Git configuration;
2. add the exact command-scope environment contract in Section 4;
3. enforce the Git 2.38.0 minimum and typed fail-closed behavior;
4. retain the three existing Git command arrays without byte changes;
5. update directly affected unit/integration tests and narrowly necessary documentation; and
6. freeze and return one new exact candidate with the required evidence below.

No wheel build, A10, A12, QA, merge, push, tag, release, pilot change, classification change, unrelated refactor, or v0.5 work is authorized by this disposition.

The private wheel bound to `014076c` remains superseded. No wheel may be built until the resulting executable candidate receives a later exact-candidate CTO disposition.

## 7. Final acceptance matrix

Engineering and independent review must demonstrate every row:

| ID | Scenario | Required result |
|---|---|---|
| CS-01 | No authorization grant | No `safe.directory` value, no repository command, typed unavailable |
| CS-02 | Project identity mismatch | Denied before Git; no private-root disclosure |
| CS-03 | Requested/granted canonical-root mismatch | Denied before Git |
| CS-04 | Missing, non-directory, escaped, aliased, or noncanonical root | Denied before Git |
| CS-05 | Empty, wildcard, interpolation, CR/LF, or NUL configuration value | Denied before Git |
| CS-06 | Git 2.37.4 or lower | Typed unsupported-version result; no repository command |
| CS-07 | Git version missing or unparsable | Typed unsupported/unavailable result; no repository command |
| CS-08 | Git 2.38.0 boundary | Exact command-scope mechanism accepted by the adapter contract |
| CS-09 | Approved Windows Git 2.55, different owner, exact grant | All permitted read-only activity succeeds |
| CS-10 | Same different-owner repository without command-scope value | Git denies access; no snapshot is emitted |
| CS-11 | Missing or mismatched grant on different-owner repository | Adapter denies before Git or withholds snapshot |
| CS-12 | Hostile ambient `GIT_CONFIG_COUNT/KEY/VALUE` variables | Ambient values are absent; only the exact allowlisted triplet reaches Git |
| CS-13 | Ambient system/global Git configuration | System disabled and global bound to null; behavior unchanged |
| CS-14 | Captured subprocess environment | Exactly one command-scope key/value and the exact canonical granted root |
| CS-15 | Captured command arrays | Byte-identical to the three accepted ADR-0021 arrays |
| CS-16 | Git top-level result differs from exact granted root | Snapshot withheld; typed mismatch |
| CS-17 | Timeout, overflow, malformed output, or command failure | Typed unavailable result; no private data or snapshot |
| CS-18 | Before/after canonical project state | Worktree bytes, status, index, refs, configuration, ownership, remotes, and reachable object graph unchanged |
| CS-19 | Before/after host filesystem inspection | No Jarvis Git-configuration file, directory, ACL artifact, or stale-cleanup namespace exists |
| CS-20 | Error, trace, snapshot, diagnostics, and CLI rendering | No configured root, private path, Git subject/author/remote, raw error, or environment value leaks |
| CS-21 | Independent Windows identity | The full local-Git suite and real process-boundary different-owner test pass |
| CS-22 | No Git or unsupported Git | Vault briefing remains safe and partial; repository activity is explicitly unavailable |

## 8. Required returned evidence

The Engineering handoff must provide:

- exact branch, parent, candidate commit, and bounded diff;
- changed-file list proving removal of the full file-based subsystem;
- a source-level comparison proving all three Git command arrays are byte-identical;
- captured-environment tests proving exact serialization and ambient-variable exclusion;
- Git-version boundary tests for below-floor, exact-floor, current approved runtime, missing, and malformed versions;
- different-owner process-boundary results both with and without the exact command-scope value;
- independent-identity results for the complete local-Git test set;
- proof that no configuration artifact or temporary namespace is created;
- before/after canonical and reachable Git integrity evidence;
- redaction and denial-path evidence; and
- full relevant test totals and commands.

## 9. Gate state

- Handoff 20 is not returned to Engineering as a request to harden the file-based design.
- This handoff supersedes that remediation path and freezes command-scope configuration as the only accepted design.
- Candidate `a7292fd` remains not cleared.
- Engineering may begin only the bounded correction in Section 6 after Chief-of-Staff activation.
- A10 and A12 remain paused.
- Architecture clearance, wheel creation, QA, merge, push, tag, release, pilot/classification changes, and v0.5 work remain unauthorized.

**Final CTO decision:** Option A is accepted. Exact-root, command-scope `safe.directory` on Git 2.38.0 or newer is the sole approved compatibility mechanism for authorized different-owner repository reads.
