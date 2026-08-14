# V05-PT-19 Scope-Conflict Routing

| Field | Value |
|---|---|
| Role | Chief of Staff |
| Date | 2026-08-13 |
| Incoming artifact | [Handoff 121 revision 2](../../../.worktrees/v0.3.1-release/docs/handovers/v0.5/121-principal-engineer-to-cto-personal-prototype-implementation-return.md) |
| Disposition | **ROUTE ONE BOUNDED ARCHITECTURE CORRECTION** |

Engineering's stop is valid. Handoff 105 requires controller-level asynchronous dispatch,
polling, and cancellation, but Handoff 120's seven-path boundary excludes the controller and the
existing mock implementation that must conform to the revised protocol.

Task `V05-PT-21` is authorized for the Chief Architect / CTO. The preferred disposition is to
extend the implementation boundary to:

- `voice_shell/controller.py`;
- `voice_shell/mock_bridge.py`; and
- only existing tests that directly require correction for the revised controller/protocol shape,
  identified explicitly by path.

The CTO must preserve Handoff 105 Section 3; leaving operational cancellation unusable is not an
acceptable shortcut. The output must freeze the final path list, required behavior, regression
matrix, and stop conditions so Engineering can resume without another planning or recovery task.
No implementation is authorized in this review.
