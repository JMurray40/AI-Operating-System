# V05-PT-27 Acceptance and V05-PT-28 Authorization

Handoff 135 is accepted. Engineering is authorized to implement its exact two-path correction
against `7132b0c464574f8d589ccf9893a253cb97fc6b97`: idempotent `reset` in `IDLE`, automatic
state-valid guidance after transitions, and test doubles that perform real teardown with zero
fixture delta.

Only `voice_shell/cli.py` and `tests/voice_shell/test_interactive.py` may change. Produce a
superseding Handoff 121 revision and one clean native candidate. The same-task two-surface rule
applies; no environment blocker or extra task is permitted. All Handoff 135 exclusions bind.
