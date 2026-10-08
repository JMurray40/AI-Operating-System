# Handoff 06 — Product Owner to CTO: Google Provider Authorization

**From:** Product Owner — Jason Murray

**To:** Chief Architect / CTO

**Date:** 2026-08-01

**Decision base:** `main@2a928be881a62bf22ac1736ec38aa965531642e7`

**Milestone:** v0.5 — Visible-Context Conversation

**Disposition:** **GOOGLE PROVIDER PROFILE APPROVED FOR IMPLEMENTATION-BRIEF DESIGN — IMPLEMENTATION AND API USE NOT AUTHORIZED**

## 1. Approved provider identity

- Provider: Google Gemini Developer API.
- Native model ID: `gemini-3.5-flash-lite`.
- Provider and model are represented separately. The LiteLLM-style string
  `gemini/gemini-3.5-flash-lite` is not the canonical domain model identity.
- Approved host: `generativelanguage.googleapis.com` over HTTPS only.
- Cross-host redirects and arbitrary endpoint overrides are prohibited.
- Dispatch uses one complete, non-streaming response per approved attempt.

The CTO must verify the exact stable model ID, endpoint path, pricing, availability, and
terms again at implementation and release-evidence time because provider facts can change.

Official references reviewed for this decision:

- [Gemini 3.5 Flash-Lite model](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite)
- [Current Gemini model guidance and pricing](https://ai.google.dev/gemini-api/docs/latest-model)
- [Gemini API terms](https://ai.google.dev/gemini-api/terms)
- [Abuse-monitoring policy](https://ai.google.dev/gemini-api/docs/usage-policies)
- [Zero-data-retention guidance](https://ai.google.dev/gemini-api/docs/zdr)

## 2. Provider capability boundary

The v0.5 Google adapter must not enable:

- streaming or Live API;
- Google Search or Maps grounding;
- URL context, file search, code execution, function calling, computer use, or other tools;
- file or attachment upload;
- explicit or implicit context caching;
- stored interactions, datasets, feedback submission, or optional log sharing;
- provider fallback, background calls, or hidden retries; or
- any host other than the approved Google API host.

If Google fails, Jarvis returns a typed visible failure. It does not switch providers.

## 3. Ollama decision

The planned local Ollama adapter is **deferred beyond v0.5**. v0.5 may define a
provider-neutral interface but must not implement, package, test as release scope, or
silently invoke Ollama.

A later Ollama increment requires its own exact model identity, resource limits, context
and quality evidence, privacy contract, packaging/recovery evidence, and Product Owner
authorization. Any future local retry is a new explicitly selected attempt, never an
automatic fallback from Google.

## 4. Credential decision

The pilot credential source is the `GEMINI_API_KEY` process environment variable behind a
typed credential-provider interface.

- The key must not appear in Git, Markdown, `.env` committed to Git, configuration domain
  objects, prompts, traces, logs, fixtures, exceptions, evidence, or handoffs.
- A missing credential returns a typed, redacted unavailable result before retrieval or
  dispatch.
- Tests use canaries and injected fake credential providers, never a live key.
- A local `.env` may be used only as an ignored operator convenience outside release
  evidence; the application contract remains the process environment variable.
- Windows Credential Manager is a later hardening option and must not block v0.5. The
  interface must permit a future provider without changing conversation semantics.

## 5. Data-use and sensitivity decision

Real-provider evidence must use a billing-enabled Google project. Optional API logging,
data sharing, datasets, feedback submission, grounding, caching, and stored interactions
must be disabled or unused.

Remote eligibility ceiling:

| Classification | Google dispatch eligibility |
|---|---|
| `public` | Eligible only after visible inspection and per-turn digest-bound approval |
| `internal` | Eligible only after visible inspection and per-turn digest-bound approval |
| `private` | Denied |
| `restricted` | Denied |
| Unclassified | Denied |

The visible approval must disclose that Google may retain prompts, supplied context, and
outputs for abuse monitoring under its then-current terms. No claim of zero data retention
is permitted without separately verified and approved project-level eligibility.

## 6. Request limits

- Thinking level: `minimal`.
- Maximum input: 64,000 tokens.
- Maximum output: 8,000 tokens.
- Timeout: 60 seconds.
- Automatic retries: none.
- Requests per approval: one.
- Sampling parameters deprecated for this model are omitted rather than simulated.
- The immutable approval snapshot binds provider, model, endpoint policy, thinking level,
  input/output limits, timeout, retry count, feature-disable set, and their versions.

Any material setting change after approval invalidates that approval.

## 7. Cost authorization

- Maximum estimated cost per approved request: **USD 0.05**.
- Maximum cumulative real-provider v0.5 release-evidence spend: **USD 10.00**.
- Pre-dispatch estimation must fail closed above the request ceiling.
- The evidence runner must stop before exceeding the cumulative ceiling.
- Usage and cost evidence must exclude prompt, context, response, credential, and private
  source content.

The price table used for estimation must be versioned, visible, and reverified against
Google's official pricing before real-provider evidence begins.

## 8. Authority and next handoff

The provider-selection gate in
[Handoff 05](05-product-owner-to-cto-conversation-scope-approval.md) is closed by this
decision. The CTO may now prepare a complete provider-specific implementation brief at:

`docs/handovers/v0.5/07-cto-to-principal-engineer-conversation-implementation-brief.md`

The brief remains ineffective until committed, independently validated by the Chief of
Staff against its exact base, and followed by a separate implementation authorization.

## 9. Prohibited work

This decision does not authorize:

- creating a branch or worktree;
- installing a Google SDK or dependency;
- creating, reading, validating, or transmitting a live API key;
- any Google or Ollama call;
- implementation, tests, evidence execution, spending, QA, merge, push, tag, or release;
- modification of the historical conversation candidate; or
- J.A.R.V.I.S Voice Shell integration.

## 10. Exit statement

**Provider selection is complete for CTO implementation-brief preparation. v0.5
implementation and all real-provider activity remain unauthorized.**
