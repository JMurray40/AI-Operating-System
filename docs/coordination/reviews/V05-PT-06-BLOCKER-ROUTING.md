# V05-PT-06 Chief of Staff Blocker Routing

| Field | Value |
|---|---|
| Task | `V05-PT-06` |
| Date | 2026-08-12 |
| Incoming artifact | [Handoff 106](../../../.worktrees/v0.3.1-release/docs/handovers/v0.5/106-principal-engineer-to-cto-personal-prototype-recovery-return.md) |
| Disposition | Valid preflight stop; execution split at the environment boundary |

## Finding

The stop is valid. Handoff 105 requires normal native Windows Git and PowerShell for the
preservation and worktree bootstrap, while the assigned Engineering context cannot provide
them. No architecture or Product Owner decision is missing.

## Routing

`V05-PT-06` is superseded without consuming an implementation attempt. `V05-PT-07` is
authorized for the Chief of Staff, using this native Windows Codex context, to perform only:

1. the read-only preservation manifest and export defined by Handoff 105;
2. native Git creation of the new branch and worktree from the exact frozen Voice base;
3. reapplication of only the manifest-bound source delta; and
4. independent normal-Git verification that the new worktree is valid and cleanly bounded.

The Chief of Staff must not implement the controller contract or create the candidate commit.
After the bootstrap is reviewed, a new Engineering task may implement Sections 3 through 6 of
Handoff 105 in the verified worktree.

## Preserved boundaries

The broken worktree and Voice root remain read-only. Jarvis Core, live capabilities,
certification, merge, push, publication, and release remain excluded.
