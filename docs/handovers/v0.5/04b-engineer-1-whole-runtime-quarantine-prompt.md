# Handoff 04b — Engineer 1 Whole-Runtime Quarantine Prompt

## Role and exact start

You own only V2 legacy-runtime quarantine for J.A.R.V.I.S.

- Start from clean `codex/security-boundary-phase1` at
  `bb1222b0a52387e894d53a296f691c51de70c23a`.
- Do not merge or rebase the V1 baseline, Engineer 2, or any other branch.
- Treat the reconciled V1 baseline `bb3bae1` as future integration identity only.

## Objective

Extend the accepted selected-file containment boundary to every reachable first-party
legacy entrypoint. No default or documented Phase 1 invocation may import or initialize
audio, TTS, heartbeat, filesystem state, network, provider, credential, tool, browser,
subprocess, system-control, background-task, or vendored Kokoro capability.

## Required implementation

1. Inventory every first-party Python entrypoint, including `__main__` guards, documented
   commands, root launchers, and package launchers. Classify vendored code separately.
2. Quarantine the executable legacy `voice_line` path before any live import. The default
   entrypoint must return a fixed typed/non-sensitive disabled outcome and must not import
   `ears`, `mouth`, `heartbeat`, provider, tool, auth, audio, network, or OS-hook modules.
3. Remove the legacy runtime from any default packaging, launcher, and documentation path.
   Do not delete historical source unless separately authorized.
4. Exclude `voice_line/Kokoro-FastAPI/`, local model files, services, examples, and vendored
   tests from the Phase 1 package/runtime/import boundary.
5. Preserve the accepted Engineer 1 deny-by-default behavior and 18-test corpus.
6. Add no replacement Core interface and do not import or call `voice_shell`.

## Required adversarial evidence

Prove offline that:

- importing and invoking every reachable first-party entrypoint performs no live import or
  initialization;
- the actual legacy launcher fails closed before audio, TTS, heartbeat, filesystem,
  network, provider, credential, tool, thread, task, or process activity;
- environment variables and confirmation text cannot activate it;
- vendored Kokoro is not imported, packaged, scanned as first-party runtime, or started;
- no local secret/state path or value enters output, logs, fixtures, or history;
- the original 18 security tests still pass; and
- the repository lint/type/whitespace gates for changed first-party files pass.

Use injected spies and AST/import-graph inspection. A scan limited to the original seven
files is insufficient.

## Return

Produce a bounded correction plus a manifest containing the exact start/end identities,
changed files, reachable-entrypoint inventory, tests, unavailable live checks, and the
statement: **legacy runtime quarantined; not a Core interface; no live capability**.

Stop for Chief-of-Staff validation and CTO review. Do not merge, push, connect to Core, add
live adapters, modify Engineer 2, or begin V4.
