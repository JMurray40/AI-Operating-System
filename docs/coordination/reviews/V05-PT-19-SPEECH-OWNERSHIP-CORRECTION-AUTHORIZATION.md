# V05-PT-19 Speech-Ownership Correction Authorization

| Field | Value |
|---|---|
| Role | Chief of Staff |
| Date | 2026-08-13 |
| Task | `V05-PT-19` |
| Authority | [Handoff 126](../../../.worktrees/v0.3.1-release/docs/handovers/v0.5/126-cto-to-principal-engineer-personal-prototype-speech-claim-return.md) |
| Disposition | **BOUNDED CORRECTION AUTHORIZED** |

`PT19-CTO-05` is an ordinary implementation defect within the frozen eleven-file boundary.
Engineering must keep claimed speech ownership observable for the complete adapter-call lifetime,
or use equivalent dedicated synchronization, without holding the controller lock across speech.
Add deterministic tests for both claim/invalidation orders across cancel, reset, and close, then
complete the native-Windows exact-candidate gate and local commit in the same cycle.

No new task, planning round, recovery round, twelfth path, Core change, or live capability is
authorized.
