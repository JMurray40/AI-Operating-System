# Handoff 17 — CTO to Principal Engineer: Fail-Closed Local Git Re-review

**Date:** 2026-07-29

**Disposition:** **RETURN TO ENGINEERING — LG-SEC-01 THROUGH LG-SEC-03 REMAIN OPEN**

**Candidate reviewed:** `d5560131156015ca477fec2d8f5729f3f80216a7`

**Review range:** `9e5b7414e8604f0b9fee89cc66a575066f5bb248..d5560131156015ca477fec2d8f5729f3f80216a7`

**Reviewed files:**

- `src/jarvis_core/project_resume/local_git.py`
- `tests/unit/test_project_resume_local_git.py`

## 1. Scope and verification

This is the bounded architecture/security re-review requested by Handoff 16. It assesses
only closure of Handoff 15 findings LG-SEC-01 through LG-SEC-04 and preservation of the
ADR-0021 process boundary.

The engineering worktree was clean on `feature/v0.4-project-resume` at exact candidate
`d5560131156015ca477fec2d8f5729f3f80216a7`.

The reviewed range changes exactly:

```text
src/jarvis_core/project_resume/local_git.py
tests/unit/test_project_resume_local_git.py
```

The range adds 645 lines and removes 31. `git diff --check` passes. No wheel was built or
reviewed in this CTO activity.

## 2. Executive finding

The correction materially improves fail-closed behavior:

- normal cleanup failure now downgrades a snapshot to a typed, redacted unavailable
  result;
- standard success, denial, timeout, overflow, malformed-output, process-error, and
  ordinary raised-exception paths invoke cleanup;
- config values are quoted and adversarial/wildcard forms are rejected;
- the generated config is tested through Git as exactly one literal
  `safe.directory`; and
- the three accepted Git command arrays remain unchanged.

The candidate is nevertheless not architecture/security conformant. Three blocking
properties requested in Handoff 15 remain unproven or incorrectly implemented:

1. the temporary root still comes from ambient `tempfile.mkdtemp()` selection rather than
   an explicit controlled root;
2. setup-failure cleanup is still best effort and can leave the security exception or
   temp directory behind while claiming setup merely failed;
3. the Windows security verifier does not verify filesystem ownership and does not fully
   verify the single ACE's access mask/flags; and
4. closing and naming the config before Git consumes it leaves a same-owner substitution
   interval with no before/after file-identity proof.

LG-SEC-04 is closed. LG-SEC-01, LG-SEC-02, and LG-SEC-03 are not.

## 3. Finding-by-finding disposition

### LG-SEC-01 — Cleanup lifecycle

**Status:** **PARTIALLY REMEDIATED; STILL BLOCKING**

The adapter now makes ordinary cleanup part of the returned security result:

- a simulated removal failure cannot return `RepositoryActivitySnapshot`;
- it returns the redacted `unavailable_cleanup_incomplete` result;
- ordinary runner exceptions attempt removal before returning; and
- standard typed degradation paths also remove the config.

This closes the original “successful snapshot despite observed deletion failure” defect.

The lifecycle remains incomplete during secure-store setup. `LocalSecureConfigStore.create`
catches setup/permission/serialization failures and invokes `_best_effort_rmtree`, whose
file deletion and directory removal errors are both suppressed. The caller then returns
`unavailable_security_setup` without proving that:

- the config file was removed;
- the controlled directory was removed; or
- no private canonical root remains on disk.

This is especially material for failures after the root has been written but before file
permission verification completes. A setup failure cannot be considered fail-closed
merely because Git did not run; the private request-scoped exception must also be proven
absent or separately escalated as cleanup-incomplete.

The general exception handler also catches `Exception`, not the full lifecycle of
termination/cancellation conditions. Engineering need not promise cleanup after
unrecoverable process termination, but it must provide bounded stale-artifact prevention
or recovery so an interrupted request cannot leave a reusable exception indefinitely.

### LG-SEC-02 — Controlled temporary-root confinement

**Status:** **OPEN; BLOCKING**

`LocalSecureConfigStore.create` still calls:

```text
tempfile.mkdtemp(prefix="jarvis-safe-dir-")
```

with no explicit `dir`. That is ambient temporary-directory selection, not the explicit
controlled temporary root required by Handoff 15 and ADR-0021.

The subsequent resolved-path comparison is useful and correctly rejects a temp directory
inside the repository or a temp directory that contains the repository. It occurs only
after the directory has already been created. If ambient temp resolution points inside
the repository or Git controls, the adapter has already performed a repository write.
Cleanup is then best effort under the unresolved LG-SEC-01 path.

The child environment's fixed `TMP`/`TEMP` does not control this parent-side creation.
Engineering must supply an explicit, validated, owner-controlled parent outside the
granted repository before creating the per-request directory. The parent and resulting
directory must be checked against symlink, junction, and Windows reparse substitution
before any repository-root value is written.

### LG-SEC-03 — Ownership, ACL proof, and substitution resistance

**Status:** **OPEN; BLOCKING**

The Windows code establishes a protected one-entry DACL for the current user's SID and
then reads the security descriptor back. This is meaningful progress.

It does not satisfy Handoff 16's independent ownership proof:

- `GetNamedSecurityInfoW` requests and returns `owner`;
- the verifier never compares that owner SID to the current user SID; and
- `SetNamedSecurityInfoW` sets only DACL information, not owner information.

The verification also does not prove the one ACE is exactly the intended owner-only ACE:

- it checks ACE type and SID;
- it does not check the ACE access mask equals the intended rights; and
- it does not check ACE flags/inheritance semantics equal the intended no-inheritance
  form.

The test named as independent owner-only verification calls the same implementation
helper a second time. It therefore repeats the same incomplete predicate rather than
independently proving owner SID, protected DACL, ACE count, ACE type, access mask, ACE
flags, and trustee.

Substitution resistance is also incomplete. Exclusive non-following creation protects
the instant at which the named config is created, but the file handle is closed before
Git is invoked. No file identity, owner/ACL, content hash, or parent identity is rechecked
immediately before and after the three Git commands. A same-owner process can replace the
named file or its parent during that interval. An owner-only ACL is a user boundary, not
a process boundary.

Engineering must either keep a platform-supported non-substitutable object binding
through consumption or verify stable file/parent identities, exact bytes, owner, and ACL
at the process boundary and again before cleanup. Any mismatch must stop before returning
repository evidence.

### LG-SEC-04 — Exact Git-config serialization

**Status:** **CLOSED**

The correction:

- canonicalizes to a forward-slash value;
- rejects quotes, backslashes, newlines, carriage returns, NUL, `*`, `/*`, and `/**`
  wildcard semantics;
- emits one double-quoted `safe.directory` entry;
- uses no include directive or second value; and
- tests the generated file through Git configuration parsing, requiring exactly one key
  and exactly the canonical granted-root value.

No new product Git command is introduced; the Git parsing commands exist only in tests.
This satisfies the bounded serialization finding.

## 4. ADR-0021 invariants preserved

The re-review confirms the correction has not weakened these accepted controls:

- repository activity remains denied without an exact request grant;
- project and canonical root must match the grant before config creation;
- missing and non-directory roots fail before Git;
- `rev-parse --show-toplevel` must equal the canonical granted root;
- `GIT_CONFIG_NOSYSTEM=1` remains set;
- ambient global config is replaced, not inherited;
- credential, proxy, SSH, askpass, editor, pager, trace, Git-dir, worktree, index, object,
  and alternates overrides remain excluded;
- subprocesses remain `shell=False`, capped, timed, non-interactive, and redacted;
- repository config, ownership, refs, index, worktree, and object graph are not
  intentionally modified by the Git operations; and
- Git stderr, paths, temporary locations, usernames, remotes, and credentials are not
  emitted through typed result messages.

## 5. Accepted Git command arrays

The three product command builders remain textually unchanged across the reviewed range:

1. `git --no-pager -C <root> rev-parse --show-toplevel`;
2. `git --no-pager --no-replace-objects -C <root> rev-parse --verify HEAD`; and
3. the fixed bounded first-parent log command with
   `-c i18n.logOutputEncoding=UTF-8` before `-C <root>` and `log`.

No `safe.directory` option, new Git subcommand, shell fragment, user-controlled revision,
pathspec, remote operation, credential operation, or repository write was added to the
arrays.

## 6. Required final remediation

Principal Engineering must return another bounded correction that:

1. selects an explicit owner-controlled temporary parent outside the repository rather
   than relying on ambient `tempfile` resolution;
2. verifies the parent and per-request directory remain outside repository/Git controls
   after resolving symlink, junction, and Windows reparse behavior;
3. ensures every setup-failure path proves removal or returns a distinct
   cleanup-incomplete security result with a safe stale-artifact handling plan;
4. explicitly establishes and independently verifies that owner SID equals the current
   process user;
5. verifies the protected DACL, exact ACE count/type, exact intended access mask, ACE
   flags, and trustee SID;
6. prevents or detects config/parent substitution from exclusive creation through the
   final Git command and cleanup;
7. revalidates exact config bytes and security identity at the process boundary;
8. retains the now-accepted literal serialization and redaction behavior;
9. leaves repository state and the three Git command arrays unchanged; and
10. remains limited to this adapter and its directly required tests.

Required tests must include:

- an ambient temp setting aimed inside the repository without any repository-local
  directory ever being created;
- setup failure after private-root write plus forced cleanup failure;
- explicit owner-SID mismatch;
- incorrect ACE mask and ACE flags;
- file replacement, parent replacement, or identity mismatch between creation and Git
  execution;
- exact before/after config identity/content/security verification;
- standard success and every degradation path;
- full repository canonical/reachable immutability; and
- unchanged command arrays.

## 7. Wheel, A12, and evidence disposition

Candidate `d5560131156015ca477fec2d8f5729f3f80216a7` is not cleared for wheel creation.

The following remain unauthorized:

1. building a wheel from `d556013`;
2. treating any wheel as candidate evidence;
3. independent wheel-payload verification;
4. renewed A12 installation, granted-repository, doctor, recovery, or integrity
   revalidation; and
5. reuse of prior A12 evidence for this candidate.

The wheel bound to `014076c` remains superseded and must not be installed or cited as
evidence for `d556013` or a later executable.

After a corrected exact candidate clears a new CTO review, the wheel/payload/A12 sequence
must be separately authorized. Reuse may then be considered only for a specifically
identified prior result whose inputs, executable dependency, documentation, environment,
and affected behavior are proven unchanged.

## 8. Gate state

- A12 remains stopped.
- No A10 execution or rerun is authorized.
- No wheel build is authorized.
- Architecture clearance remains closed.
- QA remains closed.
- Merge, push, tag, release, pilot modification, additional classification, and v0.5
  remain prohibited.

## Exit statement

**RETURN TO ENGINEERING — EXACT CONFIG SERIALIZATION IS ACCEPTED; TEMP-ROOT CONTROL,
SETUP CLEANUP PROOF, WINDOWS OWNER/ACL VERIFICATION, AND SUBSTITUTION RESISTANCE MUST
STILL BE CLOSED.**
