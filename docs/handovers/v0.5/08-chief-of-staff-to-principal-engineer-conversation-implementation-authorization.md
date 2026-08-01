# Handoff 08 — Chief of Staff to Principal Engineer: Conversation Implementation Authorization

**From:** Chief of Staff

**To:** Principal Engineer

**Date:** 2026-08-01

**Milestone:** v0.5 — Visible-Context Conversation

**Disposition:** **AUTHORIZED FOR WP1–WP3 IMPLEMENTATION ONLY**

## 1. Exact repository identity

```text
validated_main_commit: e11703974219425b463a45a97e1d7d2a04de81dc
engineering_branch: feature/v0.5-visible-context-conversation
engineering_worktree: C:\Users\jmurr\Projects\AI-Operating-System\.worktrees\v0.5-engineering
worktree_clean: true
branch_head_equals_validated_main_commit: true
historical_conversation_commit_is_ancestor_of_validated_base: false
historical_conversation_content_in_worktree: false
historical_conversation_commits_cherry_picked: false
voice_shell_content_present: false
```

The Principal Engineer must independently verify every value before planning or editing.
Any mismatch is a stop condition.

## 2. Controlling brief

Read [Handoff 07](07-cto-to-principal-engineer-conversation-implementation-brief.md) in
full after starting at [Project Control](../../coordination/README.md) and the
[v0.5 Handoff Index](README.md). Handoff 07 and its linked accepted artifacts control.
Conversation history and the historical candidate are not authoritative.

Required Engineering output:

`docs/handovers/v0.5/09-principal-engineer-to-cto-conversation-engineering-review.md`

## 3. Authorized work

Engineering may implement only Handoff 07:

- WP1 — contracts and offline application core;
- WP2 — Google adapter through fake transport and local capture only; and
- WP3 — CLI, deterministic benchmarks, packaging/recovery mechanisms, tests, and docs.

Engineering must present its pre-implementation plan before editing and surface any
load-bearing judgment call under Handoff 07 Section 20.

## 4. Dependency and network authority

```text
dependency_acquisition_scope: none
new_runtime_dependencies: prohibited
new_development_dependencies: prohibited
live_provider_scope: none
credential_scope: none
```

Use the existing environment and standard library. If cancellation or transport controls
cannot be implemented safely without a new dependency, stop and request a bounded CTO and
Chief-of-Staff decision before installing or changing anything.

Read-only public documentation checks are authorized only against official Google domains
needed to confirm the approved Gemini REST model, endpoint, request field, pricing, terms,
and retention contracts. Do not transmit repository content, source context, prompts,
credentials, identifiers, private paths, or test data. Documentation access does not
authorize an API call.

Loopback-only synthetic HTTP capture is authorized for tests when bound to the local host,
uses generated non-private fixtures, performs no external resolution or egress, and is
fully torn down by the test. Environment proxy inheritance must remain disabled.

## 5. Provider and spending boundary

- Do not read, validate, or use `GEMINI_API_KEY`.
- Do not call Google, Ollama, or any provider endpoint.
- Do not create a billing project, credential, stored interaction, cache, dataset, or log.
- Do not spend against the USD 10 evidence budget.
- WP4 remains blocked pending a later exact-candidate activation.

All Google behavior in this cycle uses an injected fake transport or bounded loopback
capture. Missing-credential behavior is tested with injected canaries and controlled
environment isolation, never Jason's live environment.

## 6. Historical and external-project boundary

The historical `feature/v0.4-conversation` branch may be inspected only through the
accepted historical assessment already in the implementation base. Do not switch to,
merge, rebase, cherry-pick, copy, or execute it.

The separate `C:\Users\jmurr\Projects\J.A.R.V.I.S` Voice Shell repository is out of scope.
Do not read, copy, integrate, or use it as implementation evidence.

## 7. Git and candidate controls

- Work only in the named v0.5 Engineering worktree.
- Preserve unrelated user changes and every other worktree.
- Use normal milestone commits; do not amend, rebase, merge, push, tag, or release.
- Do not stage or commit secrets, private evidence, generated wheels, caches, environments,
  raw provider payloads, or local benchmark artifacts unless Handoff 07 explicitly requires
  a safe tracked documentation artifact.
- Stop with one clean exact candidate and Handoff 09 ready for CTO review.

## 8. Required validation

Produce the complete Handoff 07 evidence for WP1–WP3, including:

- C01–C30 offline/capture coverage where applicable;
- full released regression suite;
- Ruff, mypy, Markdown links, and `git diff --check`;
- independently recomputable raw benchmark samples under the approved repository boundary;
- package inventory and offline install/recovery mechanisms without claiming independent
  A12 execution;
- vault/repository immutability and privacy evidence; and
- exact requirement-to-test/evidence mapping.

Real-provider outcomes remain explicitly pending and must not be fabricated.

## 9. Exit statement

**Principal Engineering is authorized to implement WP1–WP3 from exact base
`e11703974219425b463a45a97e1d7d2a04de81dc` in the named clean worktree. WP4, live
credentials, provider calls, dependency acquisition, QA, merge, push, tag, release, Voice
Shell work, and v0.6 work remain unauthorized.**
