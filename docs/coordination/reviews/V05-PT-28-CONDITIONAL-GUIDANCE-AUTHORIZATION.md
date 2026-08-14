# V05-PT-28 Conditional Guidance Correction Authorization

Close only PT28-CTO-01 from Handoff 136. Capture visible state before context removal, approval,
poll, and retry and print automatic guidance only when state actually changes. Preserve startup and
explicit-reset exceptions. Add four injected unchanged-state failure tests.

Only `voice_shell/cli.py` and `tests/voice_shell/test_interactive.py` may change. Preserve all
closed behavior and rerun Handoff 135's matrix. Leave PT28 `in_progress` for same-task Chief of
Staff native closure if needed; do not create an environment task.
