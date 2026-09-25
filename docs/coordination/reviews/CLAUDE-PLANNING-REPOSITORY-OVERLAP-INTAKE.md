# Claude-Planning repository-overlap intake review

**Date:** 2026-09-10  
**Reviewer:** Chief of Staff / architecture intake  
**Effect:** Three queued evaluation tasks; no implementation authorization

## 1. Provider layer

**Disposition:** `ACCEPT_WITH_PUNCHLIST`

Open an evaluation spike, not an implementation task. The spike must compare a thin project-owned
adapter with LiteLLM as an internal implementation detail behind the unchanged `Provider` and
`ProviderResponse` contracts. It must address dependency and native-extension cost, Python 3.14
Windows support, endpoint/model allowlisting, redirect/proxy behavior, retries and fallback,
telemetry/logging defaults, credential handling, exact request/response normalization, licensing,
offline testing and removal of the legacy `voice_line/llm_router.py` path. No provider call or
dependency installation is authorized.

## 2. Voice

**Disposition:** `ACCEPT_WITH_PUNCHLIST`

Prioritize a real local voice feasibility spike after the active PT50 closure. Preserve the existing
Voice Shell protocols, approval and lifecycle boundaries. Use Backtalk only as a pattern reference
for push-to-talk, interruption, local STT/TTS and latency measurement. Do not copy or adopt it as a
dependency without a separate AGPL review. Its permission-bypass default is incompatible with this
project and its latency claim must be independently measured on the target Windows host. Compare
the already-proposed Pocket TTS path and at least one local STT option before implementation.

## 3. ADR-0008

**Disposition:** `ACCEPT_WITH_PUNCHLIST`

Perform a short primary-source prior-art review before ADR-0008 can move to Accepted. Compare the
ADR's manifest, grant, revocation, update, sandbox and audit semantics against AgentOS and its
underlying runtime's actual schemas and enforcement. AgentOS is adjacent prior art, not presumed
equivalent. The task may propose ADR wording or an options table; it may not accept the ADR or
implement the plugin system.

## Ordering

These tasks are queued and blocked from execution while PT50 is active. Recommended order after
PT50: real-voice feasibility, provider-layer evaluation, then ADR-0008 prior-art review. None may
modify the canonical baton until separately activated.
