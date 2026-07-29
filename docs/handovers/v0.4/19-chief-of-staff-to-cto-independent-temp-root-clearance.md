# Handoff 19 — Chief of Staff to CTO: Independent Temp-root Clearance

**Date:** 2026-07-29

**Disposition:** **READY FOR BOUNDED CTO SECURITY REVIEW**

**Corrected candidate:** `a7292fd71aa678d10c66c1645340e54199060045`

**Review range:** `9620c047db7eeba8ba896866283c0d547209f67b..a7292fd71aa678d10c66c1645340e54199060045`

## Chief of Staff validation

- Branch is `feature/v0.4-project-resume`.
- Worktree is clean at the exact candidate.
- The correction changes only:
  - `src/jarvis_core/project_resume/local_git.py`
  - `tests/unit/test_project_resume_local_git.py`
- The range adds 108 lines and removes 34.
- `git diff --check` passes.
- Engineering reports 404 passed, 1 unrelated symlink skip, Ruff clean, and mypy clean
  across 67 files.
- The independent Windows sandbox identity that exposed Handoff 18 now passes all 68
  local-Git tests, Ruff, and mypy.
- The controlled pytest temporary directory was removed after validation.

The previous independent result was 47 passed and 19 failed because product code attempted
to resolve an owner-only shared `jarvis-safe-root` created by the host identity. That shared
fixed directory is no longer used. The corrected candidate creates a fresh per-request
directory under a SID-derived namespace and passes under the independent identity.

## Required CTO review

Review only the range above and determine whether it closes Handoff 18 without regressing
Handoff 17 findings LG-SEC-01 through LG-SEC-04 or ADR-0021.

Confirm:

1. no shared fixed owner-only child is created or reused;
2. the namespace is bound to the current Windows identity without disclosing the SID;
3. the fresh per-request directory is confined, owner/ACL verified, and reparse-safe before
   any repository root is written;
4. inaccessible, foreign-owned, substituted, or malicious prefix-matching artifacts are never
   reused or modified;
5. stale cleanup is bounded to artifacts proven to belong to the current identity;
6. before/after identity, bytes, owner, ACL, and cleanup proofs remain fail-closed;
7. setup and cleanup errors remain typed and redacted;
8. LG-SEC-04 exact serialization remains closed;
9. repository state remains read-only; and
10. the three accepted Git command arrays remain byte-for-byte unchanged.

## If accepted

Issue an exact-candidate disposition for `a7292fd71aa678d10c66c1645340e54199060045`
that separately authorizes:

1. a fresh private integrity-bound wheel from that exact executable;
2. independent verification that every runtime payload byte matches the candidate;
3. a renewed limited A12 run covering offline install/reinstall, the granted repository and
   doctor paths under the independent identity, network denial, and complete canonical and
   reachable-Git integrity comparison; and
4. only explicitly identified reuse of unaffected earlier evidence.

The wheel bound to `014076c` remains superseded.

## Still closed

This routing does not authorize wheel creation, A12, A10, QA, merge, push, tag, release,
pilot edits, classification changes, architecture clearance, or v0.5 work.
