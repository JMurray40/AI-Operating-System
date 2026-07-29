# Handoff 25 — CTO Command-Scope Exact-Candidate Clearance

**From:** Chief Architect / CTO  
**To:** Chief of Staff; Principal Engineer for the separately bounded packaging step; independent A12 reviewer after activation  
**Date:** 2026-07-29  
**Scope:** Final bounded architecture/security conformance review of the v0.4 Project Resume local-Git correction  
**Disposition:** **ARCHITECTURE CONFORMANT — EXACT CANDIDATE CLEARED FOR BOUNDED WHEEL AND A12 EVIDENCE**

## 1. Exact review identity

- Branch: `feature/v0.4-project-resume`
- Reviewed parent: `a7292fd71aa678d10c66c1645340e54199060045`
- Reviewed candidate: `ff402d7f82c061426a5e960f7177d916c355bbf2`
- Reviewed range: `a7292fd71aa678d10c66c1645340e54199060045..ff402d7f82c061426a5e960f7177d916c355bbf2`
- Candidate worktree at review: clean
- Changed files:
  - `src/jarvis_core/project_resume/local_git.py`
  - `tests/unit/test_project_resume_local_git.py`
- Diff size: 458 insertions, 1,237 deletions; net removal of 779 lines

Authoritative inputs:

- Handoff 22, `22-cto-command-scope-safe-directory-convergence-decision.md`;
- Handoff 23, `23-chief-of-staff-to-principal-engineer-command-scope-activation.md`; and
- Handoff 24, `24-chief-of-staff-to-cto-command-scope-candidate-validation.md`.

## 2. Explicit architecture disposition

**Candidate `ff402d7f82c061426a5e960f7177d916c355bbf2` conforms to Handoff 22 Option A and closes CS-01 through CS-22.**

The correction is an environment-only authorization projection at the Git process boundary. It does not create or trust a configuration artifact, does not weaken authorization, and does not add a general Git execution capability.

The candidate is cleared only for the four separately bounded evidence steps in Section 7. This is not QA, merge, push, tag, release, or general implementation clearance.

## 3. Architecture and security findings

### 3.1 Complete removal of the file-based security subsystem

The reviewed implementation removes:

- temporary configuration directories and files;
- ACL creation and inspection;
- owner/SID derivation and per-identity namespaces;
- stale-artifact discovery and cleanup;
- marker, manifest, and fingerprint state;
- substitution and artifact-authentication machinery;
- cleanup-specific exception paths; and
- the injectable file-store abstraction and all dormant fallback behavior.

The executable module no longer imports the file-security dependencies and contains no configuration-file creation or cleanup path. The remaining test use of `tempfile` observes the host temporary directory before and after execution; it is not product artifact creation.

This closes Handoff 20’s provenance, reparse-cleanup, transient named-file substitution, and `mkdtemp` findings by removal of their shared architectural cause.

### 3.2 Authorization and exact-root binding

Authorization remains structurally ahead of every subprocess, including the non-repository version diagnostic. A missing grant, project mismatch, or root mismatch returns a typed denial without invoking Git.

The request and grant roots are resolved and compared before use. The root must exist as a directory. The `safe.directory` value is then derived from that resolved root in canonical forward-slash form. Empty, relative, wildcard terminal forms, interpolation forms, quote/control forms, and unusable configuration representations fail closed before a repository command.

Git’s returned top-level root must resolve to the same exact authorized root. Parent, sibling, linked-worktree, submodule, and other mismatched-root results are withheld.

### 3.3 Exact command-scope environment

For each of the three repository commands, the candidate projects exactly:

```text
GIT_CONFIG_COUNT=1
GIT_CONFIG_KEY_0=safe.directory
GIT_CONFIG_VALUE_0=<exact canonical granted root>
```

The environment is built from an allowlist rather than inherited. Ambient `GIT_CONFIG_*`, `GIT_DIR`, worktree, alternates, credential, proxy, SSH, askpass, editor, pager, and tracing controls do not flow into the subprocess.

`GIT_CONFIG_NOSYSTEM=1` remains enabled and `GIT_CONFIG_GLOBAL` remains bound to the platform null device. No second indexed command-scope value exists. The version diagnostic receives no `safe.directory` projection.

### 3.4 Git-version floor

`MINIMUM_GIT_VERSION` is exactly `(2, 38, 0)`.

The fixed, non-repository `git --version` diagnostic runs only after authorization and root validation. A missing executable, failed diagnostic, malformed version, or version below 2.38.0 fails closed before any repository-activity command. Exact 2.38.0 and the approved 2.55 runtime are accepted.

There is no compatibility fallback to a file, system/global configuration, repository configuration, ownership mutation, or relaxed command.

### 3.5 Fixed commands and read-only boundary

The reviewed diff makes no change to `_cmd_toplevel`, `_cmd_head`, or `_cmd_log`. Direct comparison and executable assertions confirm the three repository command arrays are byte-identical to the accepted arrays. The only added command constructor is the separately allowed non-repository `git --version` capability diagnostic.

`safe.directory` is never placed in an argument array. Repository commands remain bounded, read-only, non-shell argument arrays with output, record, and time limits.

### 3.6 Redaction, immutability, and absence of artifacts

Raw stderr is not returned. Typed denial, unavailable, malformed, timeout, overflow, version, and environment-integrity results use allowlisted messages that contain neither the configured root nor subprocess details. Successful snapshots contain no repository-root field.

Real-process tests demonstrate:

- successful command-scope reads;
- Git denial when the command-scope triplet is removed under the different-owner simulation;
- stable repository `HEAD`, configuration, index, and refs;
- no `safe.directory` persistence in repository configuration; and
- no Jarvis temporary/configuration artifact before or after execution.

Handoff 24 additionally records that exact candidate identity and worktree cleanliness survived the independent Windows-identity validation.

## 4. CS-01 through CS-22 disposition

| Row | CTO determination | Principal evidence |
|---|---|---|
| CS-01 | Closed | Missing grant denies before every subprocess |
| CS-02 | Closed | Project mismatch denies before Git |
| CS-03 | Closed | Requested/granted canonical-root mismatch denies before Git |
| CS-04 | Closed | Missing/non-directory and returned-root escape paths fail closed |
| CS-05 | Closed | Invalid configuration representations are rejected before repository activity |
| CS-06 | Closed | Git 2.37.4 is below the enforced floor and runs no repository command |
| CS-07 | Closed | Failed and unparsable version results run no repository command |
| CS-08 | Closed | Exact Git 2.38.0 boundary is accepted |
| CS-09 | Closed | Real different-owner simulation succeeds only with the exact command-scope triplet |
| CS-10 | Closed | Removing the triplet produces Git denial and no snapshot |
| CS-11 | Closed | Missing/mismatched grants cannot reach the different-owner mechanism |
| CS-12 | Closed | Hostile ambient Git configuration and repository overrides are excluded |
| CS-13 | Closed | System configuration is disabled and global configuration is null |
| CS-14 | Closed | Captured repository environments contain the exact single triplet |
| CS-15 | Closed | All three repository command arrays are byte-identical; no `safe.directory` argument |
| CS-16 | Closed | Returned top-level mismatch is denied and the snapshot is withheld |
| CS-17 | Closed | Timeout, overflow, malformed data, and process failure degrade through typed results |
| CS-18 | Closed | Real subprocess read leaves measured repository control state unchanged |
| CS-19 | Closed | File subsystem symbols/imports are absent and no configuration artifact is created |
| CS-20 | Closed | Failures and snapshots do not disclose root, raw error, or command-scope value |
| CS-21 | Closed | Chief-of-Staff independent identity: ordinary Git denied, adapter succeeded; 68 executable local-Git tests passed |
| CS-22 | Closed | Missing/unsupported Git is explicit and does not authorize repository activity |

## 5. Independent CTO validation

The CTO review independently confirmed:

- exact branch and HEAD;
- a clean engineering worktree;
- the exact two-file correction range;
- full source removal of the temporary-file security subsystem;
- no changed line in the three accepted repository command constructors;
- `git diff --check` clean for the reviewed range; and
- targeted executable result: **68 passed, 1 intentionally skipped**.

The skipped item is the in-suite CS-21 placeholder. CS-21 is satisfied by the independent Windows process-boundary evidence in Handoff 24, including the separate **68-pass** local-Git execution under that identity.

Engineering/Chief-of-Staff retained evidence also records:

- full suite: 404 passed, 2 skipped;
- Ruff: clean; and
- mypy: clean across 67 files.

The first local CTO test attempt could not access the host identity’s default pytest temporary directory under sandbox isolation. The rerun used a bounded reviewer-owned temporary base, passed, and that base was removed. This was a reviewer-environment condition, not a candidate failure or repository mutation.

## 6. Technical-debt assessment

The command-scope design is materially smaller and has a narrower trust boundary than the superseded file design. It removes cross-identity ACL behavior, artifact lifecycle, stale recovery, and substitution races rather than carrying them as dormant compatibility debt.

The added version diagnostic is intentionally narrow and remains separate from the three repository commands. Git 2.38.0 is now a declared capability floor, so older Git installations degrade explicitly instead of activating a fallback.

No blocking architectural deviation or new unapproved scope is present in the reviewed range.

## 7. Separately authorized next steps

The following scopes are authorized separately and in order.

### 7.1 Fresh private integrity-bound wheel

The Principal Engineer may build one fresh private wheel from exact executable commit:

`ff402d7f82c061426a5e960f7177d916c355bbf2`

The build must:

- start from a clean exact-candidate checkout;
- use the already approved isolated packaging procedure;
- introduce no source, test, script, metadata, documentation, pilot, or classification change;
- record wheel filename, size, SHA-256, build interpreter, build command, and outcome without private paths or credentials; and
- remain private and out of Git.

The wheel bound to `014076c429d47de83be4ca6543264082aa62633f` remains superseded and is not evidence for this candidate.

### 7.2 Independent byte-for-byte payload verification

Before A12 installation, an independent reviewer must:

- verify the fresh wheel’s recorded SHA-256;
- enumerate its payload;
- compare every candidate-owned executable payload byte-for-byte with exact commit `ff402d7`;
- verify declared package/version, PyYAML dependency, console entry point, and absence of unexpected executable or provider content; and
- stop on any mismatch, unexpected dependency, unbound payload, or identity ambiguity.

The verified wheel digest becomes the sole candidate installation identity.

### 7.3 Renewed limited A12

After payload verification, independent A12 is authorized only to rerun the correction-affected and installation-integrity scope:

1. create a clean isolated environment before any private pilot path is exposed;
2. verify and install the already approved PyYAML wheel offline;
3. disable and verify network denial;
4. verify the fresh candidate wheel hash;
5. install with `pip install --no-index --no-deps <verified-candidate-wheel>`;
6. verify installed command identity and operation;
7. exercise the granted repository path under the independent Windows identity, including ordinary-Git denial and adapter success with the exact request-scoped environment;
8. run `resume-doctor` and confirm the declared Git-version and unavailable/degradation behavior;
9. confirm no Git configuration or Jarvis temporary artifact is created;
10. uninstall and reinstall from the same verified candidate wheel, offline;
11. repeat installed-command and granted-repository validation after reinstall; and
12. perform the complete before/after pilot, canonical-source, worktree, index, refs, configuration, remote, ownership, and reachable-object integrity comparison under the accepted Handoff 06 boundary.

A12 must stop on a hash mismatch, unexpected dependency, network requirement or egress, missing/mismatched grant acceptance, private-data leak, canonical mutation, reachable-object change, configuration artifact, undocumented step, or inability to reproduce the independent-identity result.

### 7.4 Explicitly permitted reuse of unaffected earlier evidence

Only the following earlier evidence may be reused, with its original identity and digest cited:

- Product Owner pilot selection and classification approvals;
- accepted pre-edit, apply, and post-classification private evidence digests;
- the accepted post-classification canonical/reachable baseline;
- documentation-only ancestry and published-procedure validation that was not changed by this correction;
- the previously verified offline PyYAML wheel, if its exact retained hash is reverified before use; and
- privacy/no-provider/no-telemetry policy evidence that is procedural and independent of executable local-Git behavior.

The following may not be reused as passing evidence for `ff402d7`:

- any wheel or installed-candidate identity bound to `014076c`;
- prior candidate installation, uninstall, or reinstall outcomes;
- prior local-Git, granted-repository, `resume-doctor`, no-artifact, or process-boundary results;
- prior wheel payload comparisons; or
- any final integrity comparison made before the renewed A12 execution.

## 8. Gate state and stop conditions

- Exact candidate `ff402d7f82c061426a5e960f7177d916c355bbf2` is architecture-cleared for Sections 7.1 through 7.4 only.
- A10 is not authorized by this handoff and remains under its separate gate.
- Quality & Release is not authorized.
- Merge, push, tag, release, pilot modification, additional classification, unrelated work, and v0.5 remain prohibited.
- Any candidate or packaging-metadata change invalidates this clearance and requires a new exact-candidate review.
- The next review must bind executable commit, wheel digest, documentation identity, reused evidence, new A12 evidence, and final integrity result explicitly.

**Final CTO disposition:** **CONFORMANT — proceed only with a fresh integrity-bound `ff402d7` wheel, independent payload verification, and the renewed limited A12 scope above.**
