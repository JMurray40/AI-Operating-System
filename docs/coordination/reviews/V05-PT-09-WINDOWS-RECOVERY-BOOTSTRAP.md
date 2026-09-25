# V05-PT-09 Native-Windows Recovery Bootstrap Return

| Field | Value |
|---|---|
| Task | `V05-PT-09` |
| Date | 2026-08-12 |
| Status | Blocked; mandatory rollback completed |
| Authority | [V05-PT-08 acceptance](V05-PT-08-ACCEPTANCE.md) |

## Stop

The operator performed the root checkout inventory after capturing the protected-file baseline.
Native Git status refreshed the root checkout index's stat cache, changing the root index bytes.
The post-preservation protected-hash comparison correctly detected the change and stopped before
branch or recovery-worktree creation.

This was an execution-order error. Handoff 105 places the root inventory before Handoff 108's
linked-worktree protected baseline. A compliant future attempt must finish the root inventory
with optional locks disabled before capturing the protected baseline, then make no further root
checkout status call inside the protected window.

## Rollback and preserved state

The newly created private staging directory was resolved, proven outside both repositories, and
removed as Handoff 108 requires. No recovery branch or worktree exists. No source file, broken
worktree file, linked-worktree index, ref, configuration, object, or candidate was changed.

The root index cache bytes changed; no repair or restoration was attempted. The failure process
held the pre/post digests in memory but stopped before exporting them, so exact digest evidence
is unavailable. This limitation is disclosed for CTO review.

No retry, implementation, network, live capability, merge, push, publication, or release work
occurred.
