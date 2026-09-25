# V05-PT-11 Native-Windows Recovery Bootstrap Return

| Field | Value |
|---|---|
| Task | `V05-PT-11` |
| Date | 2026-08-12 |
| Status | Blocked before preservation export |
| Authority | [V05-PT-10 acceptance](V05-PT-10-ACCEPTANCE.md) |

The attempt created only the authorized external evidence-journal directory and completed the
root semantic inventory in memory with optional locks disabled. Persistence then failed because
the installed Windows PowerShell version does not recognize `Set-Content -Encoding utf8NoBOM`.

No protected baseline, payload staging, patch export, file copy, branch, recovery worktree, or
implementation was created. A compatible UTF-8 stop record was written to the retained journal
with SHA-256 `bc4a86442e5e8291b5c99eaa26c66567c9814fd53a7964bf6119e85732c4fd3a`.
The recovery branch/path remain absent and the Voice root remains at `bb3bae1...`.

The correction is mechanical: use a PowerShell-version-compatible byte-writing method for JSON
and digest files, validate it before any Git command, and retain all Handoff 110 ordering and
stop controls. No silent retry occurred.
