# Handoff 04 — CTO to Product Owner: Combined Voice Architecture Disposition

| Field | Value |
|---|---|
| Role | Chief Architect / CTO |
| Date | 2026-08-02 |
| Repository reviewed | `C:\Users\jmurr\Projects\J.A.R.V.I.S` |
| Common base | `ad37c65f8aa5e4f144248e4b89ebbbe17686885f` |
| Engineer 1 candidate | `codex/security-boundary-phase1@bb1222b0a52387e894d53a296f691c51de70c23a` |
| Engineer 2 candidate | `codex/voice-shell-phase1@f32499a815143a1e892356706e38644557c946de` |
| Review mode | Read-only architecture and security-boundary review |
| Disposition | **DO NOT MERGE OR CONNECT — CONVERGE THROUGH A THIRD MOCK-ONLY INTEGRATION GATE** |

## 1. Executive decision

The two branches do not form a client/server pair and must not call each other.

- Engineer 1 is a **containment lane** for selected legacy `voice_line` brain, provider,
  tool, authentication, subprocess, injection, and redaction boundaries.
- Engineer 2 is a **replacement presentation-shell lane** under the new `voice_shell`
  package, with typed mock ports and no live capabilities.

Their useful relationship is architectural, not a direct runtime dependency. Engineer 1's
deny-by-default controls become mandatory integration requirements. Engineer 2's shell is
the only eligible forward presentation architecture. The legacy `JarvisBrain` is not the
Core adapter and must not sit between `voice_shell` and Jarvis Core.

A future connection has one direction only:

```text
Voice Shell presentation
    -> shell-owned VoiceCoreBridge
        -> versioned Jarvis Core conversation application API
```

Jarvis Core must not import the Voice Shell, `voice_line`, the Voice Shell security package,
audio libraries, TTS/STT libraries, or capability code. The Voice Shell must not read the
vault, call a model/provider, load Core credentials, execute tools, or reconstruct Core
policy.

## 2. Exact review findings

### 2.1 Engineer 1 — bounded containment, not repository-wide safety

`bb1222b` materially improves the selected legacy boundary:

- provider construction is sealed to a deterministic mock;
- fallback, retry, streaming, credential loading, subprocess, and capability execution are
  unavailable in the reviewed replacements;
- capability requests produce non-executable, default-denied proposals;
- rejected arguments are neutralized;
- provider failures and returned reasons are bounded/redacted; and
- 18 focused offline tests were reported for those selected files.

These properties are useful and should be preserved as negative requirements.

They do **not** secure the repository as a whole. The unchanged legacy tree still contains
an executable `voice_line/main.py` that imports audio, mouth/TTS, signals, and heartbeat
components. Unchanged heartbeat code writes state/notices. Unchanged mouth and the vendored
Kokoro tree contain network and live-service surfaces. The Engineer 1 structural scan is
limited to seven selected files and therefore cannot prove that the legacy entrypoint or
package is mock-only.

**Engineer 1 disposition:** acceptable as a containment patch and test corpus; not
merge-ready as a complete safety baseline, not a Core interface, and not authority to run
the legacy application.

### 2.2 Engineer 2 — sound mock shell, incomplete Core boundary

`f32499a` establishes a cleaner forward direction:

- new `voice_shell` package separate from `voice_line`;
- typed audio, transcription, Core, speech, and cancellation protocols;
- deterministic in-memory/mock adapters;
- bounded audio/transcription validation;
- explicit state transitions and fixed public outcome/error enums;
- no arbitrary adapter error text in public events;
- approval-required, cancellation, malformed, and failure outcomes are not spoken; and
- 27 offline tests plus strict typing/lint/format evidence were reported.

The package itself does not import live audio, model, provider, vault, credential, connector,
subprocess, browser, or network libraries.

Its current `CoreClientProtocol.process(text) -> CoreResponse` is intentionally only a mock
seam and is **not compatible enough** with the accepted Jarvis conversation architecture.
It cannot represent separate prepare, context inspection/removal, digest-bound approval,
dispatch, retry, current-byte drift, safe trace, or in-flight Core cancellation. Its string
citation and free-form usage containers are weaker than Jarvis's versioned evidence
contracts. It also labels ASR confidence simply `confidence`, which could be confused with
the prohibited answer-confidence meaning.

**Engineer 2 disposition:** suitable as a mock-only presentation-shell candidate after a
bounded contract correction; not ready for a Jarvis Core adapter or real audio/TTS/STT.

### 2.3 Mechanical compatibility does not establish architectural compatibility

Both commits descend directly from `ad37c65` and their changed paths do not overlap, so a
future Git integration is likely mechanically straightforward. That is not permission to
merge. Combining them unchanged would leave two competing orchestration paths:

1. the partially contained legacy `voice_line` runtime; and
2. the new `voice_shell` controller.

It would also leave the broad legacy/vendored capability surface in the same executable
repository without a proven package or entrypoint boundary.

## 3. Frozen component ownership

| Concern | Owner | Prohibited ownership |
|---|---|---|
| Push-to-talk state and presentation | Voice Shell | Jarvis Core |
| Audio capture/playback adapters | Future Voice Shell increment | Core, legacy brain |
| Speech-to-text/text-to-speech adapters | Future Voice Shell increment | Core provider gateway |
| Context discovery and authorization | Jarvis Core | Voice Shell, transcription, legacy brain |
| Context manifest, removal and approval | Jarvis Core semantic contract; Shell renders/returns choices | Voice Shell reimplementation |
| Provider/model/credential/egress | Jarvis Core only | Voice Shell and `voice_line` |
| Citations, coverage, limitations and trace | Jarvis Core | Shell inference or string reconstruction |
| Tools/actions | Future Core capability gateway | Voice Shell, model, legacy tools |
| Durable memory/transcripts | Future separately approved Core architecture | Voice Shell and v0.5 |
| Public speech projection | Voice Shell from Core-approved presentation fields | Raw provider Markdown/payload |

## 4. Required replacement bridge contract

No implementation is authorized by this disposition. Before a Core connection is proposed,
a new versioned `VoiceCoreBridge` contract must be reviewed. It must be shell-owned and
adapt the released Core API without changing Core semantics.

Minimum operations:

```text
prepare_turn(transcript, session_ref, cancellation_ref) -> PreparedTurnView
remove_context(request_ref, snapshot_digest, context_item_id) -> PreparedTurnView
approve_turn(request_ref, snapshot_digest, approval_input) -> ApprovalView
dispatch_turn(request_ref, snapshot_digest, approval_ref, cancellation_ref) -> CoreTurnView
cancel_attempt(attempt_ref) -> CancellationView
retry_attempt(request_ref, snapshot_digest, approval_ref, cancellation_ref) -> CoreTurnView
reset_session(session_ref) -> ResetView
```

The bridge must preserve, not flatten:

- request/session/attempt identities and one-based turn number;
- context item IDs, sensitivities, locators, reasons, token counts, and snapshot digest;
- explicit context omissions and limitations without excluded-source disclosure;
- approval-required versus approved/declined/expired/drifted status;
- completed, failed, cancelled, blocked, and unavailable terminal states;
- supported citations as typed source/revision/passage objects;
- answer coverage, conflicts, limitations, usage/cost provenance, and safe trace reference;
  and
- retry identity and current-byte/policy revalidation requirements.

The Shell may render a reduced view, but the bridge cannot convert typed Core states into
free-form strings or infer missing state. Unknown remains unknown, never zero or success.

`TranscriptionResult.confidence` must be renamed `recognition_confidence` or
`asr_confidence` and documented as adapter-local speech-recognition metadata, never answer
confidence or retrieval relevance.

## 5. Visible approval and speech rules

Voice input cannot replace the accepted visual/inspectable context approval contract.
Until a separately approved accessible approval surface exists:

- `APPROVAL_REQUIRED` ends the voice attempt without Core dispatch;
- the Shell may announce a fixed, non-sensitive prompt directing the user to the approved
  context interface, but it must not speak source excerpts, paths, sensitivities, approval
  tokens, or hidden context;
- spoken “yes,” transcription text, wake words, PTT release, silence, timeout, or prior
  approval cannot authorize egress;
- approval is accepted only through a Core-issued digest-bound approval operation;
- changes to transcript, context, provider, policy, prompt versions, or source bytes require
  a new visible prepare/approval cycle; and
- approval-required, failed, cancelled, blocked, and malformed provider content is never
  spoken as an answer.

## 6. Speech-output boundary

The Shell must never speak raw provider Markdown or a generic `CoreResponse.text`. A future
Core response for voice must contain an explicit bounded `speech_text` projection produced
only after claim/citation validation and safe rendering. It must exclude citation URLs,
absolute paths, code/control sequences, active markup, raw errors, secrets, trace content,
and approval material.

Limitations may be spoken only from fixed/bounded Core presentation fields and must remain
distinguishable from a supported answer. Citations and full context remain available on the
visual/CLI surface rather than being flattened into spoken strings.

## 7. Cancellation and concurrency boundary

The current synchronous `process(text)` seam cannot prove cancellation of an in-flight Core
operation. The future bridge must:

- create a distinct Core attempt and cancellation reference;
- propagate cancellation to Core, transcription, and speech independently;
- make terminal completion exactly once under cancel/complete races;
- prevent late Core completion from entering speech after cancellation;
- clear queued speech and prevent duplicate/reordered utterances;
- never retry or fallback automatically; and
- bound audio, transcript, request, response, time, memory, and concurrency.

## 8. Required convergence sequence

No merge is authorized now. The only acceptable future sequence is:

### Gate V1 — repository and secret containment

Chief of Staff must establish a clean exact base, preserve/resolve the dirty root worktree,
inventory ignored/untracked credential artifacts without exposing values, and confirm no
credential or private content enters either candidate or integration history.

### Gate V2 — Engineer 1 whole-runtime quarantine correction

On its isolated branch, Engineer 1 must extend the boundary from selected files to every
reachable first-party entrypoint. The legacy `voice_line` executable must be removed from
default packaging/entrypoints or fail closed before audio, TTS, heartbeat, filesystem,
network, provider, credential, or tool initialization. The vendored Kokoro tree must be
excluded from the Phase 1 runtime/package boundary. Tests must scan reachable imports and
exercise the actual entrypoint, not only seven files.

### Gate V3 — Engineer 2 shell contract correction

On its isolated branch, Engineer 2 may only:

- rename ASR confidence;
- replace string citations/free-form usage with typed mock presentation DTOs compatible
  with the future bridge shape;
- split the monolithic `process` seam into mock prepare/approval/dispatch/cancel states;
- preserve no-live-capability structural tests; and
- prove no import or dependency on `voice_line`, Engineer 1 runtime modules, or Jarvis Core.

This remains mock-only and does not implement the real bridge.

### Gate V4 — third integration candidate

Only after independent validation of V1–V3 may the Chief of Staff authorize a new clean
integration branch from the exact common/reconciled base. Integrate the Engineer 1
quarantine first, then the Engineer 2 replacement shell. Add a separate integration commit
that makes `voice_shell` the sole eligible Phase 1 entrypoint and proves the legacy runtime
cannot activate.

The integrated candidate remains deterministic mock-only. It must run both focused suites
plus whole-repository entrypoint, import, package, secret, filesystem, network, thread/task,
and mutation checks.

### Gate V5 — future Core bridge planning

After v0.5 conversation is released and its in-process API is stable, the CTO may propose a
bridge ADR, threat model, requirements, and acceptance matrix. Product Owner and Chief of
Staff approval are required before any Jarvis Core import, package dependency, IPC, or
request is added to the Voice Shell.

### Gate V6 — real audio/provider/capabilities

Real microphone, STT, TTS, speaker, provider, credentials, vault access, tools, connectors,
or system control each require separate architecture and evidence. A Core bridge does not
grant any of them. The Shell never receives a model/provider credential.

## 9. Combined acceptance matrix before a mock-only integration merge

| Area | Required proof |
|---|---|
| Identity | Exact base, both source commits, integration commit/tree and clean worktree |
| Legacy quarantine | Every reachable legacy entrypoint fails before live initialization |
| Sole entrypoint | Only mock `voice_shell` entrypoint is packaged/documented/runnable |
| Cross-imports | `voice_shell` imports neither `voice_line` nor security/auth legacy modules |
| Capabilities | No provider, credential, vault, connector, tool, subprocess, browser, filesystem write, network, hardware, audio service or background job reachable |
| Errors/privacy | Fixed enums only; no raw exception, path, identity, secret, transcript or adapter status disclosure |
| State | Deterministic transitions; approval-required/failure/cancel/malformed never spoken |
| Cancellation | No late completion or queued speech after cancellation |
| Resources | Audio/transcript/queue/time/memory/task/thread caps and cleanup |
| Imports | No import-time files, sockets, threads, tasks, devices, environment reads or service probes |
| Packaging | Legacy/vendored runtime excluded from the mock shell artifact |
| Regression | Engineer 1, Engineer 2 and combined adversarial suites all pass |
| Documentation | Explicit mock-only limits, recovery and no-live-capability statement |

## 10. Evidence reuse

The reported Engineer 1 18-test and Engineer 2 27-test results remain useful only for their
exact isolated commits and scopes. They may seed a combined regression suite. They do not
prove:

- repository-wide safety;
- a secure integration of the two branches;
- compatibility with Jarvis Core;
- real audio/STT/TTS behavior;
- provider/credential behavior;
- live capability authorization; or
- release readiness.

No historical Voice Shell, Jarvis v0.5, provider, or pilot evidence is imported by this
review.

## 11. Explicit disposition

**RE-SCOPE AND CONVERGE THROUGH A THIRD MOCK-ONLY INTEGRATION GATE.**

Do not merge either branch to the root branch, merge them into each other, connect either
to Jarvis Core, add real audio, invoke a provider, access a credential, or enable any live
capability from this disposition.

Engineer 1's security controls are accepted as mandatory containment requirements but its
candidate needs whole-runtime quarantine proof. Engineer 2's `voice_shell` is accepted as
the forward presentation direction but needs a bridge-shaped mock contract correction.
They meet only later in a separately authorized clean integration branch, with no direct
runtime dependency and no live capability.

The next authority, if the Product Owner accepts this disposition, is a Chief-of-Staff
activation for the bounded V1–V3 corrections. This handoff does not authorize Engineering,
merge, Core connection, audio, provider, credentials, tools, vault access, push, tag,
release, v0.5 scope expansion, or v0.6 work.
