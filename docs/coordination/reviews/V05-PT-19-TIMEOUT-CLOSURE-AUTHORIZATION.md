# V05-PT-19 Timeout Closure Authorization

| Field | Value |
|---|---|
| Role | Chief of Staff |
| Date | 2026-08-13 |
| Task | `V05-PT-19` |
| Authority | [Handoff 127](../../../.worktrees/v0.3.1-release/docs/handovers/v0.5/127-cto-to-principal-engineer-personal-prototype-speech-timeout-return.md) |
| Disposition | **CONSOLIDATED FINAL CORRECTION AUTHORIZED** |

Engineering must close `PT19-CTO-06` as a complete ownership invariant, not another local patch:
no cancel, reset, or close path—including wait exhaustion and synchronization failure—may return
while the invalidated lifecycle can still start or continue speech, publish retry state, or retain
a process worker. The implementation must make the operation non-publishable before any timeout
return while preserving bounded shutdown and never holding the controller lock across speech,
waiting, or callbacks.

Deterministic tests must cover cancel/reset/close for successful waits, timeout waits, adapter
faults, synchronization faults, and release-after-timeout. The return is not ready until the full
native-Windows matrix passes and the authorized local candidate commit, tree, diff, Core identity,
and repository evidence are bound. No partial Linux-only review return is requested.
