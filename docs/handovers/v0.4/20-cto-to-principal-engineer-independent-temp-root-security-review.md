# Handoff 20 — CTO to Principal Engineer: Independent Temp-root Security Review

**Date:** 2026-07-29

**Disposition:** **RETURN TO ENGINEERING — HANDOFF 18 CLOSED NARROWLY; CLEANUP AUTHENTICATION
AND SUBSTITUTION RESISTANCE REMAIN BLOCKING**

**Candidate reviewed:** `a7292fd71aa678d10c66c1645340e54199060045`

**Review range:** `9620c047db7eeba8ba896866283c0d547209f67b..a7292fd71aa678d10c66c1645340e54199060045`

**Reviewed files:**

- `src/jarvis_core/project_resume/local_git.py`
- `tests/unit/test_project_resume_local_git.py`

## 1. Scope and identity

This is the bounded CTO security review requested by Handoff 19. It reviews only the
specified range for closure of Handoff 18 while confirming that LG-SEC-01 through
LG-SEC-04 and ADR-0021 remain satisfied.

The engineering worktree was clean on `feature/v0.4-project-resume` at exact candidate
`a7292fd71aa678d10c66c1645340e54199060045`.

The range changes exactly the local-Git adapter and its unit tests, adding 108 lines and
removing 34. `git diff --check` passes. No wheel was built or reviewed.

The independent Windows sandbox identity that previously reported 47 passing and 19
failing local-Git tests now reports all 68 passing. This is valid evidence that the
cross-identity fixed-directory availability defect was removed.

## 2. Executive finding

Handoff 18 is closed in its narrow sense:

- the shared fixed `jarvis-safe-root` is removed;
- a fresh per-request directory is created with an explicit `dir=` beneath the validated
  temporary base;
- the request prefix is derived from the running identity rather than reused across
  identities;
- raw SID bytes are not placed in the directory name;
- an inaccessible or foreign-owner prefix-matching directory is skipped rather than
  reused or modified; and
- the previously failing independent identity now executes the full local-Git suite.

The candidate is not architecture/security conformant as a whole. The cleanup namespace
is identity-scoped but not artifact-authenticated. The stale sweep can delete unrelated
same-identity entries and can traverse a Windows junction/reparse artifact. The
substitution checks still observe only before and after the complete Git sequence and
cannot detect a transient replace/use/restore sequence. An untyped `mkdtemp` failure also
remains outside the adapter's redacted setup mapping.

These defects prevent preservation of LG-SEC-01/LG-SEC-03 and the Handoff 19
foreign-artifact, reparse, cleanup, and substitution invariants.

## 3. Handoff 18 closure

### 3.1 Independent identity namespace

**Status:** **CLOSED**

The correction replaces the shared fixed child with:

- a 16-hex-character token derived from SHA-256 of the current Windows user SID; and
- a fresh `mkdtemp` request directory under a prefix containing that token.

No raw SID is written. The token is stable and linkable within the machine's temporary
namespace, but it is not the SID itself and is used only to separate identity namespaces.
It must not be emitted through product output, errors, trace, or committed evidence.

### 3.2 Foreign-identity artifact behavior

**Status:** **CLOSED FOR DIFFERENT OWNER/ACL; NOT CLOSED FOR SAME-IDENTITY FOREIGN ARTIFACTS**

An inaccessible or owner/ACL-mismatched entry raises from `_verify_owner_only` and is
skipped under the bounded sweep. The added regression test proves that such an entry does
not block a fresh request and remains untouched.

The proof does not establish that a prefix-matching entry with the current user's exact
owner/ACL was created by this component. Another same-identity process can create that
shape. Identity ownership is necessary but is not artifact provenance.

## 4. Blocking findings

### ITR-SEC-01 — Stale cleanup is not artifact-authenticated

**Severity:** Blocking

`_sweep_stale_configs` deletes any old directory that:

- matches the predictable current-identity prefix;
- is a directory;
- is not reported as a symlink; and
- passes the current-user owner/ACL predicate.

It does not require a component-created marker, authenticated manifest, expected exact
structure, recorded creation identity, or content proof. A same-user process can create a
matching directory and have its contents removed after the age threshold.

The stale cleanup must prove that an entry is a Jarvis-created stale security artifact,
not merely something owned by the same Windows identity. If provenance cannot be proven,
the entry must be skipped without modification.

### ITR-SEC-02 — Junction/reparse traversal remains possible

**Severity:** Blocking

The stale sweep rejects `entry.is_symlink()` but does not reject every Windows reparse
point or junction. `_remove_tree_proven` then enumerates and recursively removes children
for paths reported as directories.

On the supported Windows boundary, a junction/reparse entry can be directory-like without
being safely covered by a POSIX-style symlink check. Cleanup must inspect and reject
reparse attributes/junctions before enumeration, use non-following identity checks, and
never recurse through an unproven directory handle.

A process-boundary test must create the supported Windows junction/reparse case and prove
that neither the target nor the entry is traversed or modified.

### ITR-SEC-03 — Transient ABA substitution is not detected

**Severity:** Blocking

The adapter verifies config/parent identity, bytes, owner, and ACL:

1. immediately before the complete three-command Git sequence; and
2. after the sequence, before cleanup.

This detects persistent substitution. It does not detect a same-owner process replacing
the config after the first verification, allowing Git to consume the replacement, and
restoring the original identity/content/security state before the second verification.

The accepted detection alternative requires detection at the consumption boundary, not
only at the edges of the complete operation. Engineering must either:

- hold a platform-supported non-substitutable/deny-delete binding throughout all three
  invocations; or
- provide an equivalent process-boundary mechanism that proves each Git invocation
  consumed the exact verified object and cannot be satisfied by replace/use/restore.

Verification before each command alone is insufficient if replacement can occur between
verification and Git opening the file.

### ITR-SEC-04 — `mkdtemp` failure escapes typed/redacted setup handling

**Severity:** Blocking

The per-request `tempfile.mkdtemp(..., dir=real_base)` call occurs before the `try` that
maps setup `OSError` to `SecureConfigError`. A permission, exhaustion, path, or filesystem
failure can therefore escape the secure-store contract and the adapter's typed
`unavailable_security_setup` result.

Move creation under the fail-closed setup boundary. If no artifact was created, return
the redacted setup failure. If partial creation cannot be proven absent, return the
distinct cleanup-incomplete result.

## 5. LG-SEC status

| Finding | Status at `a7292fd` | CTO assessment |
|---|---|---|
| LG-SEC-01 cleanup lifecycle | **Open** | Normal cleanup and setup escalation improved, but stale deletion is not provenance-safe and `mkdtemp` failure is not typed. |
| LG-SEC-02 controlled temp root | **Closed for Handoff 18 availability/confinement path** | Base is resolved before request creation and request `mkdtemp` uses explicit `dir=`; ambient base inside the repository is rejected before creation. |
| LG-SEC-03 owner/ACL and substitution | **Open** | Owner/ACL predicate is retained, but same-owner artifact provenance and transient substitution remain unresolved. |
| LG-SEC-04 exact serialization | **Closed** | No regression in quoted single-value serialization or adversarial/wildcard rejection. |

## 6. Preserved ADR-0021 invariants

The range preserves:

- default denial without a grant;
- exact project/root grant binding;
- missing-root and root-mismatch denial paths;
- exact `rev-parse --show-toplevel` equality;
- `GIT_CONFIG_NOSYSTEM=1`;
- ambient global-config exclusion;
- credential, proxy, SSH, askpass, editor, pager, trace, Git-dir, worktree, index, object,
  and alternates isolation;
- capped, timed, non-interactive, `shell=False` subprocess execution;
- typed/redacted Git command failures;
- no intentional repository config, ownership, ref, index, worktree, or object mutation;
  and
- no raw SID, path, temporary location, username, remote, credential, or Git stderr in
  product failures.

## 7. Accepted Git command arrays

The range does not change the three accepted product command builders:

1. fixed repository-root verification;
2. fixed HEAD verification; and
3. fixed bounded first-parent log with
   `-c i18n.logOutputEncoding=UTF-8` before `-C <root>` and `log`.

No `safe.directory` argument, new subcommand, shell fragment, user-controlled revision,
pathspec, remote operation, credential operation, or Git write was introduced.

## 8. Required bounded remediation

Principal Engineering must remain within the adapter and directly required tests and:

1. authenticate stale artifacts as component-created before deletion;
2. reject every symlink, junction, mount-point, and Windows reparse artifact before
   enumeration or removal;
3. make recursive cleanup non-following and identity-stable;
4. close the replace/use/restore substitution interval with a consumption-boundary
   mechanism;
5. bring request-directory creation inside typed/redacted setup and cleanup handling;
6. retain the per-identity, fresh per-request namespace;
7. retain exact owner SID, protected DACL, ACE count/type/mask/flags/trustee verification;
8. retain exact config serialization, redaction, confinement, and repository
   immutability; and
9. leave the three Git command arrays unchanged.

Required tests must include:

- same-user prefix-matching foreign artifact remains untouched;
- foreign-owner artifact remains untouched;
- stale authentic artifact is removed;
- stale unauthenticated artifact is skipped;
- Windows junction/reparse artifact and its target remain untouched;
- `mkdtemp` failure maps to the correct redacted typed result;
- transient replace/use/restore cannot yield a snapshot;
- standard success/degradation cleanup still passes;
- independent Windows identity full local-Git suite; and
- full canonical/reachable repository immutability.

## 9. Wheel and A12 disposition

Candidate `a7292fd71aa678d10c66c1645340e54199060045` is not authorized for
wheel creation.

The following remain closed:

1. fresh private wheel build;
2. independent wheel payload verification;
3. A12 installation, reinstall, granted-repository, doctor, recovery, network-denial, or
   integrity revalidation; and
4. reuse of earlier A12 evidence.

The wheel bound to `014076c` remains superseded and may not be installed or cited as
evidence for this or a later candidate.

After a later exact candidate clears this bounded security gate, wheel creation, payload
verification, and limited A12 must be authorized as separate steps. Earlier evidence may
be reused only when the CTO explicitly identifies a result whose executable dependency,
documentation, environment, inputs, and affected behavior are unchanged.

## 10. Gate state

- A12 remains stopped.
- No A10 execution or rerun is authorized.
- No wheel build is authorized.
- Architecture clearance and QA remain closed.
- Merge, push, tag, release, pilot modification, classification changes, and v0.5 remain
  prohibited.

## Exit statement

**RETURN TO ENGINEERING — INDEPENDENT-ID TEMP NAMESPACE ACCEPTED; STALE-ARTIFACT
AUTHENTICATION, REPARSE-SAFE CLEANUP, CONSUMPTION-BOUNDARY SUBSTITUTION RESISTANCE, AND
TYPED REQUEST-DIRECTORY CREATION MUST BE CLOSED.**
