# Handoff 03 — Chief of Staff to CTO: J.A.R.V.I.S. Voice Frontend Review Request

**From:** Chief of Staff
**To:** Chief Architect / CTO
**Date:** 2026-08-01
**Related milestone:** v0.5 planning and later interface roadmap
**External repository:** `C:\Users\jmurr\Projects\J.A.R.V.I.S`
**Observed branch/HEAD:** `main@ce5edd187baae0a5bcda9e598b31d4f0a1e30048`
**Review mode:** Read-only; dirty working state preserved
**Disposition:** **CTO REVIEW REQUIRED — DO NOT INTEGRATE OR TREAT AS A FRONTEND YET**

## 1. Product Owner request

Jason has been building a J.A.R.V.I.S. interface project separately and requested Chief of
Staff / CTO review for possible relationship to AI Operating System.

The repository was inspected read-only. No file, credential, Git state, process, provider,
vault, Google account, microphone, TTS service, or system tool was changed or invoked.

## 2. What the repository currently is

The project is described as a frontend, but its executable architecture is a separate
voice-first agent runtime. It contains:

- push-to-talk microphone capture and local Whisper transcription;
- streaming LLM dispatch through LiteLLM;
- automatic primary/fallback model routing;
- ElevenLabs, local Kokoro, and Edge TTS fallbacks;
- in-process conversation history and system prompt assembly;
- direct local tool execution;
- direct Obsidian vault reads and writes;
- proactive commitment state and notices;
- Google Gmail and Calendar access;
- browser and application launching; and
- system volume, mute, shutdown, and shutdown-cancellation controls.

This is materially broader than a presentation layer. It combines interface, provider
gateway, memory, retrieval, tools, connectors, proactive behavior, and operating-system
control in one process.

## 3. Repository state

The observed worktree is dirty and is not a reviewable frozen candidate. It contains
modified, deleted, and untracked files, including new runtime modules and local credential
artifacts. The staging area and exact working-tree bytes were not altered.

Repository inventory found:

- 434 tracked paths;
- 348 tracked paths under an embedded `voice_line/Kokoro-FastAPI` tree;
- 148 tracked binary/model/media/package artifacts by extension; and
- zero first-party tests outside the vendored Kokoro project and local virtual environment.

The first-party Python files inspected parse syntactically, but syntax alone does not
establish runnable or safe behavior.

## 4. Immediate security findings

### JV-SEC-01 — Credential artifacts are not safely excluded

`.env` is ignored, but `credentials.json`, `token_personal.json`, and
`token_business.json` are untracked and not covered by the current `.gitignore`. They are
one broad staging command away from disclosure.

The reviewed reachable Git history did not expose those exact filenames. Their contents
were deliberately not opened or echoed during this review. That does not prove the tokens
have never been copied, logged, backed up, or disclosed elsewhere.

**Required:** stop broad staging; ignore exact credential/token patterns; inventory every
secret location without printing values; confirm file permissions and provider console
state; rotate/revoke any credential whose handling history cannot be established.

### JV-SEC-02 — OAuth storage and scopes are unsafe for this maturity level

`auth_setup.py` writes Python pickle objects into files named `.json`, and runtime code
loads those files with `pickle.load`. Pickle is code-executing deserialization and must not
be used for credential persistence. The scopes include Gmail modification and Calendar
event modification even though the exposed runtime functions are described as read-only.

**Required:** use the provider's documented JSON credential serialization, least-privilege
read-only scopes, OS-backed secret storage where appropriate, explicit account identity,
and a revocation/recovery procedure.

### JV-SEC-03 — Tool confirmation is prompt-only, not enforced

The model prompt asks for confirmation, but `JarvisBrain.process_turn` executes every
returned tool call directly through `getattr(...); func(**args)`. There is no application
authorization record, capability grant, typed confirmation state, replay protection, or
separation between proposed and executed actions.

This affects vault writes, session logging, commitments, browser/app launching, Google
access, and system shutdown. `launch_application` also passes model-influenced text to
`subprocess.Popen(..., shell=True)`, creating command-injection risk.

**Required:** remove tool execution from the model loop. A later capability gateway must
validate a declarative tool ID, typed arguments, exact target, scope, user confirmation,
expiry, and result before any side effect. Eliminate `shell=True` and arbitrary executable
strings.

### JV-SEC-04 — Untrusted vault content becomes system authority

All Markdown files under a configured context folder are concatenated into the system
prompt and described as “absolute truth” and instructions. The separate injection scanner
and redactor are not imported into the first-party runtime. Pattern detection would not be
an authorization mechanism even if connected.

**Required:** use Jarvis Core's authorization, sensitivity, immutable context snapshot,
passage citation, and untrusted-content contracts. Vault content must never become system
instructions or grant tools, network, or write authority.

### JV-SEC-05 — Network activity is implicit and broader than disclosed

The runtime can contact the selected LLM, automatic fallback model, ElevenLabs, Edge TTS,
Kokoro, Gmail, and Calendar. It contains no single allowlisted egress gateway, visible
context approval, endpoint contract, telemetry denial, exact content manifest, or unified
credential boundary.

The keep-alive task intends to call a model every 60 seconds without a user request, and
the TTS pipeline automatically tries multiple services. Provider errors can be returned to
the user with raw exception text.

**Required:** no external call may occur until each capability is separately architected
and authorized. A frontend must receive normalized results from Jarvis Core rather than
own provider or connector clients.

## 5. Correctness and reliability findings

### JV-REL-01 — Keep-alive task references undefined names

`voice_line/main.py` creates a background task that references `ears`, `llm_router`, and
`brain`, while the initialized objects are named `recorder` and `jarvis` and the router is
not imported there. The failure is swallowed by broad exception handling, so the intended
keep-alive behavior cannot be trusted and defects can remain invisible.

### JV-REL-02 — No first-party automated tests or release evidence

There is no first-party unit, integration, security, read-only, permission, provider,
audio, cancellation, concurrency, privacy, packaging, or recovery test suite. The README
contains only a title and one-line description. Dependency versions are broad lower bounds,
not a reproducible lock.

### JV-REL-03 — Vendored subsystem dominates the repository

Most tracked paths belong to an embedded Kokoro-FastAPI project, including binaries,
models, tests, examples, assets, Helm files, and web applications. Provenance, upstream
version, license obligations, vulnerability state, modification policy, and release
boundary are not documented. This obscures the small amount of first-party code and makes
artifact review impractical.

### JV-REL-04 — Error handling hides failure and may disclose internals

Broad exception handlers frequently suppress errors or return raw exception strings.
Background network failure is ignored, while provider, filesystem, path, or service details
may be spoken or placed into model history. There is no typed terminal-state or redaction
contract.

## 6. Conflicts with current AI Operating System scope

The current proposed v0.5 conversation scope explicitly excludes:

- voice and graphical interfaces;
- durable transcripts and memory proposals;
- vault writes;
- tools, plugins, MCP, agents, and automation;
- attachments and live external connectors;
- provider fallback;
- semantic retrieval; and
- provider-response streaming.

The external repository currently implements or attempts several of those excluded
capabilities. It also bypasses released ADR-0014 through ADR-0017 evidence/authorization
contracts and the proposed immutable visible-context approval boundary.

It must not be merged into Jarvis Core, used as v0.5 evidence, or allowed to influence the
v0.5 implementation base.

## 7. Potentially reusable work

The following may be useful as design research after isolation and reimplementation:

- push-to-talk interaction and interruption expectations;
- local microphone discovery and audio pre-roll;
- local Whisper transcription experiments;
- sentence-level speech queueing and barge-in behavior;
- concise voice personality guidance;
- local TTS experimentation;
- explicit visual/voice state signals; and
- hardware-specific latency and device notes.

These are user-interface concepts, not accepted code or security architecture.

## 8. Recommended architectural relationship

Treat this repository as an experimental **Voice Shell**, not as Jarvis Core and not as a
v0.5 frontend candidate.

A future approved shell should:

1. contain audio capture, presentation, and accessibility behavior only;
2. call one stable, versioned Jarvis application API;
3. have no direct vault, provider, Gmail, Calendar, browser, subprocess, memory, or system
   control access;
4. display Core-provided context, approval, citations, limitations, and proposed actions;
5. send user confirmations back to a capability gateway rather than execute tools;
6. use a separately approved voice/privacy retention contract; and
7. enter the roadmap only after the non-voice v0.5 trust boundary is released or the
   Product Owner explicitly reorders scope.

## 9. Required CTO decisions

The CTO should produce a formal disposition deciding:

1. whether to preserve this repository as a quarantined design spike or begin a separate
   voice-shell hardening project;
2. the minimum immediate secret-containment procedure;
3. whether all live provider/tool/vault-write capabilities should remain disabled pending
   a later architecture;
4. which audio/UI concepts are eligible for future requirements research;
5. the required interface contract between a future shell and Jarvis Core;
6. whether the vendored Kokoro tree must be removed, replaced by a pinned external
   dependency, or isolated as a separately governed component; and
7. the roadmap milestone at which voice work may resume.

Required outgoing artifact:

`docs/handovers/v0.5/04-cto-to-product-owner-jarvis-voice-frontend-disposition.md`

## 10. Chief-of-Staff recommendation

**Re-scope and quarantine.** Preserve the creative voice-interface work, but do not run it
with live credentials, a canonical vault, or consequential system tools until the CTO
defines an isolated shell boundary and the immediate secret/tool risks are remediated.

This review grants no authority to modify either repository, rotate credentials, run the
assistant, invoke providers, access Google, change the vault, execute tools, merge code, or
expand v0.5.
