# Handoff 24 — Chief of Staff to CTO: Command-scope Candidate Validation

**Date:** 2026-07-29

**Disposition:** **READY FOR FINAL BOUNDED CTO CONFORMANCE REVIEW**

**Candidate:** `ff402d7f82c061426a5e960f7177d916c355bbf2`

**Parent:** `a7292fd71aa678d10c66c1645340e54199060045`

## Bounded scope

The correction changes exactly:

- `src/jarvis_core/project_resume/local_git.py`
- `tests/unit/test_project_resume_local_git.py`

The range contains 458 insertions and 1,237 deletions, a net removal of 779 lines. The
temporary-file, ACL, owner/SID, stale-cleanup, substitution-detection, marker, manifest,
and artifact-authentication subsystem is removed. No fallback remains.

## Engineering evidence

- Targeted gate: 68 passed, 1 CS-21 placeholder skipped.
- Full gate: 404 passed, 2 skipped.
- Ruff clean.
- mypy clean across 67 files.
- `git diff --check` clean.
- CS-01 through CS-20 and CS-22 are mapped to named tests in the Engineering return.
- The three accepted repository command arrays remain byte-identical.

## Independent CS-21 validation

The Chief of Staff ran the candidate under the independent Windows sandbox identity
`CodexSandboxOffline` against the host-owned v0.4 engineering repository.

Control behavior:

```text
ordinary Git under the independent identity:
fatal: detected dubious ownership
exit 128
```

Candidate behavior:

```text
LocalGitRepositoryActivityAdapter with exact request grant:
RepositoryActivitySnapshot
adapter exit 0
```

The adapter used the approved command-scope environment, with system configuration disabled
and global configuration bound to the null device. No persistent or temporary Git
configuration was used.

The complete executable local-Git suite was also run under that independent identity:

```text
68 passed, 1 skipped
```

The sole skip is the deliberate CS-21 placeholder. CS-21 itself is satisfied by the real
process-boundary result above, not by the placeholder.

Post-validation:

- exact HEAD remained `ff402d7f82c061426a5e960f7177d916c355bbf2`;
- engineering worktree remained clean;
- Ruff and mypy remained clean; and
- the controlled test temporary directory was removed.

## Required CTO review

Review the exact range
`a7292fd71aa678d10c66c1645340e54199060045..ff402d7f82c061426a5e960f7177d916c355bbf2`
against Handoff 22 CS-01 through CS-22.

If conformant, issue an exact-candidate disposition separately authorizing:

1. a fresh private integrity-bound wheel built from `ff402d7`;
2. independent byte-for-byte payload verification against that candidate;
3. renewed limited A12 offline installation/reinstallation, granted-repository and doctor
   validation, network denial, no-artifact verification, and complete canonical/reachable
   integrity comparison; and
4. only explicitly identified reuse of unaffected prior A12 evidence.

The wheel bound to `014076c` remains superseded.

## Still closed

This handoff does not authorize a wheel, A10, A12, QA, merge, push, tag, release, pilot or
classification changes, unrelated work, or v0.5.
