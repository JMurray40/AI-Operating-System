# Handoff 15 — CTO to Principal Engineer: Local Git Security Disposition

**Date:** 2026-07-29

**Disposition:** **RETURN TO ENGINEERING — TEMPORARY-CONFIG LIFECYCLE IS NOT FAIL-CLOSED**

**Candidate reviewed:** `9e5b7414e8604f0b9fee89cc66a575066f5bb248`

**Correction range:** `79a4999a9d8d6f0ff4a6daf47e758e8dbffc85bb..9e5b7414e8604f0b9fee89cc66a575066f5bb248`

**Reviewed files:**

- `src/jarvis_core/project_resume/local_git.py`
- `tests/unit/test_project_resume_local_git.py`

## 1. Scope and reviewed authority

This is the bounded architecture and security-conformance review requested by:

- `13-a12-to-principal-engineer-packaging-recovery-revalidation.md`; and
- `14-chief-of-staff-to-cto-local-git-correction-review.md`.

The review is pinned to the exact candidate and range above. No earlier Project Resume
implementation decision was reopened except where the correction changes the ADR-0021
process boundary.

The worktree was clean on branch `feature/v0.4-project-resume` at the exact candidate.
The range contains 207 inserted lines and 5 removed lines across exactly the two reviewed
files. `git diff --check` passes.

The previously verified wheel bound to executable `014076c` is superseded. It is not
evidence for `9e5b741` and is not authorized for installation or reuse as this
candidate's artifact.

## 2. Executive architecture finding

The architectural approach is directionally acceptable: a request-scoped, process-owned
global Git configuration can express one exact `safe.directory` without trusting ambient
system/global configuration or mutating the repository.

The submitted implementation is not yet acceptable because its temporary-config
lifecycle is not fail-closed:

1. the config is created through the ambient `tempfile` location rather than an explicit,
   controlled temporary directory proved outside the repository;
2. restrictive ownership/permissions are asserted but not established and verified for
   the supported Windows boundary; and
3. deletion failure is silently suppressed after the Git result has already been
   accepted, leaving a file containing the private canonical repository root while
   reporting success.

Handoff 14 expressly requires temporary-file creation, permissions, deletion, and failure
behavior to be fail-closed and non-disclosing. These are blocking security findings.

## 3. Findings

### LG-SEC-01 — Cleanup failure is silently accepted

**Severity:** Blocking

**Location:** `src/jarvis_core/project_resume/local_git.py`, request cleanup following
`_load_activity_with_env`

The adapter returns the activity result from inside `try` and then suppresses every
`OSError` from `os.unlink(global_config)` in `finally`. If deletion fails:

- the caller can receive a successful repository snapshot;
- the request-scoped exception remains on disk;
- the file retains the canonical private repository root; and
- no typed failure or safe limitation records that the security cleanup did not complete.

This conflicts with ADR-0021's request-scoped boundary and Handoff 14 items 5 and 6.
Cleanup is part of the security result, not best-effort housekeeping.

The operation must not return a successful snapshot when secure cleanup cannot be proven.
Cleanup failure must produce a typed, redacted, fail-closed result and must never expose
the temporary path or repository root.

### LG-SEC-02 — Temporary location is ambient and not confined

**Severity:** Blocking

**Location:** `_write_safe_directory_config`

`tempfile.mkstemp(...)` is called without an explicit `dir`. It therefore selects its
location from the parent process's temporary-directory resolution, while ADR-0021
requires a fixed temporary directory outside the repository when needed.

The child Git environment's `TMP`/`TEMP` values do not govern where the parent creates
this config. A hostile, misconfigured, or repository-local ambient temp setting can place
the exception inside the granted worktree or Git directory, creating the very canonical
or Git-state mutation the adapter must prohibit.

The adapter must select, canonicalize, and validate an explicit process-owned temporary
root. It must prove that neither the directory nor the config resolves within the granted
repository or its Git control paths and must reject symlink, junction, or reparse escape.

### LG-SEC-03 — Process ownership and restrictive permissions are not verified

**Severity:** Blocking

**Location:** `_write_safe_directory_config`

Exclusive file creation is a useful primitive, but the implementation does not establish
or verify the supported Windows ACL/ownership boundary before writing the private root and
passing the file to Git. The tests assert existence, contents, and later absence only.
They do not prove:

- the containing directory is process/user controlled;
- another local identity cannot read or replace the file;
- the file cannot be followed or substituted;
- the effective Windows permissions are restrictive; or
- a permission-setting/verification failure stops before Git executes.

The implementation and process-boundary tests must prove the security property on the
supported Windows environment. A platform on which that property cannot be established
must degrade safely before repository access.

### LG-SEC-04 — Config serialization is not proven exact for adversarial roots

**Severity:** Blocking

**Location:** `_write_safe_directory_config`

The resolved path is interpolated directly into Git config syntax. Forward slashes avoid
backslash escapes but do not by themselves prove that Git parses the value as exactly one
literal directory for every supported path.

The correction must use a Git-config-safe literal serialization or reject roots whose
representation could introduce comments, line breaks, sections, wildcard semantics, or
multiple values. Tests must parse/consume the generated config through the supported Git
boundary and prove:

- exactly one `safe.directory` value exists;
- it equals the already-canonical granted root;
- it is never `*` and never a semantic parent wildcard such as `<root>/*`; and
- no additional key, include, or section can be introduced.

This is a hardening requirement for Handoff 14 item 2, not authority to add another Git
command shape.

## 4. Conformance findings that remain valid

The bounded correction preserves several important invariants:

### 4.1 Grant and root checks

- no grant returns the existing default-denied result before a config file is created;
- project/root mismatch is rejected before a config file is created;
- both requested and granted roots are resolved and compared exactly;
- missing/non-directory roots fail before Git execution; and
- `rev-parse --show-toplevel` still must resolve exactly to the granted root.

These controls are conformant, subject to closing the lifecycle findings above.

### 4.2 Ambient configuration isolation

- `GIT_CONFIG_NOSYSTEM=1` remains present;
- the process-created global config replaces, rather than augments, ambient global
  configuration;
- the base environment still points global config to the platform null file;
- inherited Git, credential, proxy, SSH, pager, editor, and tracing variables remain
  excluded; and
- repository config and ownership are not intentionally changed.

No expansion to ambient trust was found.

### 4.3 Accepted command shapes

The correction does not change the three ADR-0021 command arrays:

1. fixed repository-root verification;
2. fixed HEAD verification; and
3. fixed bounded first-parent log with
   `i18n.logOutputEncoding=UTF-8` before `-C` and the `log` subcommand.

No shell, new Git subcommand, user-controlled option, revision, pathspec, remote, fetch,
credential, or write command was added.

### 4.4 Redacted Git failures

Git command stderr remains capped, classified, and excluded from public result messages.
The correction does not expose command arrays, raw stderr, repository roots, usernames,
remotes, or credentials through existing Git failure paths.

This does not cure LG-SEC-01: silently ignoring cleanup failure is non-disclosing but not
fail-closed.

## 5. Required engineering remediation

Principal Engineering must return a new narrowly bounded correction that:

1. creates the ephemeral config only beneath an explicit controlled temporary root
   canonicalized outside the granted repository and Git control paths;
2. establishes and verifies supported-platform ownership and restrictive permissions
   before writing the canonical root;
3. uses exclusive, non-following creation and prevents replacement between creation and
   Git consumption;
4. serializes exactly one literal `safe.directory` entry without wildcard, comment,
   newline, include, or multi-value interpretation;
5. retains `GIT_CONFIG_NOSYSTEM=1` and isolation from ambient global configuration;
6. removes the config on success, denial, timeout, overflow, malformed output, runner
   error, and raised exception;
7. treats cleanup failure as a typed, redacted, unsuccessful repository-activity result;
8. does not mutate repository config, ownership, refs, reflogs, index, worktree, objects,
   packs, or reachable state;
9. preserves the exact three accepted Git command shapes; and
10. adds no generic configuration or compatibility framework.

The design should make cleanup outcome observable before the final successful result is
returned. It must not disclose the temp path or granted root when creation, permission
verification, Git execution, or cleanup fails.

## 6. Required tests

At minimum add deterministic and real process-boundary coverage for:

- no grant, project mismatch, root mismatch, missing root, and Git-missing paths create
  no ephemeral config;
- the controlled temp root is outside the repository and cannot resolve through a
  symlink/junction/reparse point into it;
- restrictive ownership/permissions are established and verified on the supported
  Windows profile;
- permission setup or verification failure prevents every Git invocation;
- config content parses to exactly one literal granted root;
- roots containing config-significant or wildcard-like characters fail closed or round
  trip literally;
- success removes the config before returning success;
- toplevel denial, HEAD failure, log failure, timeout, overflow, malformed output, and
  raised runner exception all remove the config;
- simulated deletion failure returns a redacted unsuccessful result and never a snapshot;
- ambient system/global config remains disabled;
- repository config/ownership and the full canonical/reachable boundary remain exact;
- the dubious-owner exact-grant path succeeds;
- missing/mismatched grants and exact-root mismatch remain denied; and
- the three accepted command arrays remain byte-for-byte unchanged.

Tests that merely check the file is normally absent after a successful in-process fake
runner are insufficient for the cleanup-failure and Windows-permission invariants.

## 7. Wheel and evidence disposition

No wheel may be built from `9e5b741` under this disposition because the executable has
not cleared the bounded architecture/security gate.

The required sequence from Handoff 14 is therefore not activated. After Engineering
returns a corrected exact commit, the CTO must review the new delta before authorizing:

1. an integrity-bound wheel built from that exact cleared executable;
2. independent verification of every runtime payload byte against that executable;
3. renewed limited A12 installation/reinstallation and granted-repository/doctor
   revalidation; and
4. any explicitly bounded reuse of unaffected earlier A12 evidence.

The wheel bound to `014076c` remains superseded and may not serve as evidence for
`9e5b741` or any later executable.

No prior A12 evidence is newly authorized for reuse by this disposition. Candidate-bound
installed-command, deterministic-fixture, pilot, diagnostics, recovery, uninstall,
reinstall, and integrity claims must be reassessed after a corrected executable and wheel
are pinned. A later CTO review may accept reuse only for an unaffected procedure or
environment fact whose inputs and executable dependency are explicitly proven unchanged.

## 8. Gate state

- A12 remains stopped.
- No fresh wheel is authorized.
- No A10 execution or rerun is authorized by this artifact.
- Candidate `9e5b741` is not architecture-cleared.
- QA remains closed.
- Merge, push, tag, release, pilot modification, additional classification, and v0.5
  remain prohibited.

Engineering may change only the bounded local-Git correction and its directly required
tests. Any broader need must return through the Chief of Staff before implementation.

## Exit statement

**RETURN TO ENGINEERING — PROCESS-OWNED `safe.directory` APPROACH CONDITIONALLY
ACCEPTABLE; TEMPORARY CONFIG CREATION, PERMISSIONS, SERIALIZATION, AND CLEANUP MUST FAIL
CLOSED.**

Stop after producing the corrected executable identity, exact changed-file list,
validation results, and architect-facing security rationale for a new bounded CTO review.
