# V05-PT-27 CTO UX Correction Authorization

CTO must freeze one minimal correction for Handoff 134. The recommended choice is an idempotent
explicit `reset` in `IDLE` that re-arms the 25-turn counter and prints state-valid guidance,
preserving decline semantics and the frozen operator sequence. Require automatic valid-command
guidance after every transition and test cleanup that removes each real fixture even when
production teardown is spied or forced to fail.

Bind exact paths and tests for one Engineering correction. Do not reopen architecture or expand
scope. Output Handoff 135 at
`.worktrees/v0.3.1-release/docs/handovers/v0.5/135-cto-interactive-frontend-usability-correction-disposition.md`.
