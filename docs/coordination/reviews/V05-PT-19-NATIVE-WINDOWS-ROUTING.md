# V05-PT-19 Native-Windows Recovery Routing

| Field | Value |
|---|---|
| Role | Chief of Staff |
| Date | 2026-08-12 |
| Incoming task | `V05-PT-19` |
| Incoming artifact | [Handoff 121](../../../.worktrees/v0.3.1-release/docs/handovers/v0.5/121-principal-engineer-to-cto-personal-prototype-implementation-return.md) |
| Disposition | **NATIVE-WINDOWS INSPECTION AND LOCK CLEANUP AUTHORIZED** |

## Finding

Engineering stopped correctly before implementation. Direct file hashing reproduced the accepted
Handoff 120 source and Git-identity baseline. Linux-hosted Git then refreshed the administrative
index and stranded a zero-byte `index.lock`; no source file changed.

## Authorized correction

Task `V05-PT-20` is authorized for the Chief of Staff using native Windows PowerShell and Git only.
It may:

1. confirm no Git process is using the recovery worktree;
2. record the current administrative index and lock identities;
3. remove only the exact zero-byte stale `index.lock` identified by Handoff 121;
4. use native Windows Git with optional index refresh writes disabled to verify HEAD, tree, branch,
   staged semantics, working-tree scope, and the seven accepted source hashes; and
5. decide whether the same recovery worktree is safe to reuse or must be replaced.

The changed index byte identity is not required to return to its earlier cache representation if
its staged tree is semantically identical to the frozen parent and every source identity remains
correct. No source edit, index reset, checkout, clean, stash, commit, branch mutation, or broad lock
cleanup is authorized.

## Stop conditions

Stop on an active Git process, a nonzero or differently located lock, staged content, unexpected
source path, ref/HEAD/tree mismatch, source-hash mismatch, or any need for a destructive repair.

## Return

Write `docs/coordination/reviews/V05-PT-20-NATIVE-WINDOWS-RECOVERY-RETURN.md`, update the active
worklist and canonical baton, and route the result to the Chief Architect / CTO. `V05-PT-19`
remains blocked until that review accepts the recovered baseline.
