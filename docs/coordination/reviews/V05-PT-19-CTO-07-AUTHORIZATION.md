# V05-PT-19 PT19-CTO-07 Correction Authorization

| Field | Value |
|---|---|
| Decision | `COS-05-PT-19-CTO-07` |
| Task | `V05-PT-19` |
| Owner | Principal Engineer |
| Reviewer | Chief Architect / CTO |
| Status | Authorized |
| Controlling review | [Handoff 128](../../../.worktrees/v0.3.1-release/docs/handovers/v0.5/128-cto-native-candidate-and-final-prototype-conformance-disposition.md) |

## Objective

Close only PT19-CTO-07. After a cancellation, reset, or close timeout returns, the invalidated
lifecycle must be unable to enter `speech.speak()` or `speech.process()`. The implementation must
not depend on persistent interrupt behavior specific to `MockSpeechOutput`.

## Authorized scope

- Modify `voice_shell/controller.py`.
- Modify only directly required existing tests already inside the frozen eleven-path ceiling.
- Add deterministic adapter-invocation spies proving that `speak()` and `process()` are never
  invoked when timeout wins before adapter entry.
- Preserve both ordinary lock orders and prove cancel, reset, and close independently.
- Re-run the impacted Voice gates and unchanged frozen-Core checks.
- Complete native-Windows Git closure in the same cycle, creating one new exact clean candidate
  descendant of `edf344a36a09322d5a836d1804ae939b69de06c5`.
- Append the exact candidate identity and evidence to Handoff 121.

## Acceptance conditions

The return must demonstrate no late speech-adapter call, `RETRY_READY`, public result, duplicate
speech, deadlock, or retained worker. It must bind the new commit, tree, parent, exact changed
paths, clean worktree, tests, Ruff, mypy, repeatable prototype result, and reused or rerun Core
evidence. The next return goes directly to CTO review.

## Exclusions and stop conditions

Do not broaden `SpeechOutputProtocol`, modify Jarvis Core, add a twelfth path, activate a live
capability, merge, push, publish, certify, or release. Stop on any need for those actions, any
unexpected path, failing gate, Git lock/state anomaly, or inability to complete native-Windows
candidate closure. Do not split implementation and commit closure into separate relay tasks.
