# Handoff 04c — Engineer 2 Bridge-Shaped Mock Contract Prompt

## Role and exact start

You own only V3 mock Voice Shell contract correction for J.A.R.V.I.S.

- Start from clean `codex/voice-shell-phase1` at
  `f32499a815143a1e892356706e38644557c946de`.
- Do not merge or rebase the V1 baseline, Engineer 1, or any other branch.
- Do not import Jarvis Core; the bridge remains a deterministic mock seam.

## Objective

Replace `CoreClientProtocol.process(text)` with a shell-owned, versioned, bridge-shaped
mock contract that can preserve future Jarvis Core conversation semantics without
implementing or connecting to Jarvis Core.

## Required contract

Define frozen typed request/view objects and a `VoiceCoreBridgeProtocol` for:

```text
prepare_turn(transcript, session_ref, cancellation_ref) -> PreparedTurnView
remove_context(request_ref, snapshot_digest, context_item_id) -> PreparedTurnView
approve_turn(request_ref, snapshot_digest, approval_input) -> ApprovalView
dispatch_turn(request_ref, snapshot_digest, approval_ref, cancellation_ref) -> CoreTurnView
cancel_attempt(attempt_ref) -> CancellationView
retry_attempt(request_ref, snapshot_digest, approval_ref, cancellation_ref) -> CoreTurnView
reset_session(session_ref) -> ResetView
```

The mock DTOs must preserve fixed typed identities and states for requests, sessions,
attempts, context items, snapshot digests, omissions, approval, terminal outcomes, retry,
citations, coverage, limitations, usage/cost provenance, and safe trace references.

## Required corrections

1. Rename transcription `confidence` to `recognition_confidence` and document that it is
   adapter-local ASR metadata, never answer confidence or retrieval relevance.
2. Replace string citations with typed source/revision/passage citation DTOs.
3. Replace free-form usage dictionaries with a typed usage/cost provenance DTO.
4. Split prepare, visible approval, dispatch, cancellation, retry, and reset. Voice text,
   PTT release, silence, timeout, or prior approval must never authorize dispatch.
5. `APPROVAL_REQUIRED` must stop before dispatch and expose only a fixed non-sensitive
   presentation event. Tests may provide a synthetic digest-bound visible approval object
   directly; the controller must never infer it from transcription.
6. Replace generic response text with explicit bounded `speech_text`, present only for a
   completed, validated mock turn. Never speak raw provider text, citations, paths,
   approval material, trace, secrets, or arbitrary errors.
7. Make cancel/complete races terminal exactly once. Late completion and retry cannot
   produce speech after cancellation. No automatic retry or fallback.
8. Preserve all existing no-live-capability and fixed-public-enum controls.

## Required adversarial evidence

Prove offline that:

- prepare never dispatches;
- transcript-only or spoken approval cannot dispatch;
- digest/request/approval drift fails closed;
- removal produces a new immutable snapshot digest;
- dispatch requires the matching synthetic visible approval;
- cancellation wins safely against late completion and clears queued speech;
- retry has a new attempt identity and reuses no expired or drifted approval;
- typed citations, coverage, limitations, usage/cost, and trace references survive without
  string flattening;
- recognition confidence never enters answer confidence or dispatch policy;
- `voice_shell` imports neither `voice_line`, Engineer 1 modules, nor Jarvis Core;
- imports create no file, socket, thread, task, device, model, or service; and
- pytest, Ruff, strict mypy, privacy, and whitespace gates pass.

## Return

Produce a bounded correction with exact start/end identities, changed files, requirement-
to-test mapping, raw offline gate results, and explicit unavailable live checks.

Stop for Chief-of-Staff validation and CTO review. Do not merge, push, add real audio,
provider, credentials, vault access, tools, Core imports, or begin V4.
