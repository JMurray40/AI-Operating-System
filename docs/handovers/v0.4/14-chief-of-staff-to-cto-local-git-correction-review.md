# Handoff 14 — Chief of Staff to CTO: Local Git Correction Review

**Date:** 2026-07-29

**Disposition:** **READY FOR BOUNDED CTO CONFORMANCE REVIEW**

**Corrected executable candidate:** `9e5b7414e8604f0b9fee89cc66a575066f5bb248`

**Prior executable:** `014076c429d47de83be4ca6543264082aa62633f`

**Documentation parent:** `79a4999a9d8d6f0ff4a6daf47e758e8dbffc85bb`

## Chief of Staff validation

- Branch is `feature/v0.4-project-resume`.
- Worktree is clean and HEAD matches the corrected candidate above.
- The correction commit changes exactly:
  - `src/jarvis_core/project_resume/local_git.py`
  - `tests/unit/test_project_resume_local_git.py`
- Relative to the documentation parent, the delta is 207 lines: source `+71/-5`,
  tests `+141`.
- Relative to the original executable, only one source module is executable-relevant.
  The remaining intervening changes are the previously reviewed documentation-only commits.
- `git diff --check` passes.
- Independent targeted validation passes: 26 tests, Ruff, and mypy.

The first independent test invocation encountered an environmental `PermissionError` while
pytest attempted to access its default user temporary directory. It was not a product failure.
The identical suite was rerun with a controlled workspace temporary directory; all 26 tests
passed and the temporary directory was removed.

## Required CTO review

Review only the correction from
`79a4999a9d8d6f0ff4a6daf47e758e8dbffc85bb..9e5b7414e8604f0b9fee89cc66a575066f5bb248`
for conformance with ADR-0021 and the security invariants in Handoff 13.

Confirm or reject:

1. the process-owned ephemeral global Git configuration is an acceptable implementation of
   request-scoped `safe.directory`;
2. the configuration contains exactly the already-validated granted root and never `*`;
3. ambient system/global configuration remains disabled;
4. repository configuration, ownership, refs, index, worktree, and object graph remain
   untouched;
5. denied, missing-grant, mismatch, and failure paths cannot retain or broaden the exception;
6. temporary-file creation, permissions, deletion, and failure behavior are fail-closed and
   non-disclosing; and
7. the three accepted Git command shapes and root-confinement checks remain unchanged.

## If accepted

Issue a candidate-specific disposition for
`9e5b7414e8604f0b9fee89cc66a575066f5bb248` and authorize:

1. engineering to build a fresh private, integrity-bound wheel from that exact executable;
2. Chief of Staff verification that every runtime payload byte matches the candidate;
3. a renewed, limited A12 rerun covering installation/reinstallation and the affected
   granted-repository/doctor controls; and
4. reuse of unaffected A12 evidence only where the CTO explicitly finds it still applicable.

A fresh wheel identity is mandatory. The wheel bound to executable `014076c` is superseded
and must not be installed as evidence for `9e5b741`.

## Still closed

No QA, A10 rerun, A12 execution, merge, push, tag, release, pilot edit, additional
classification, architecture clearance, or v0.5 work is authorized by this routing.
