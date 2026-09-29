# Handoff 21 - Personal Recall integration planning authorization

Date: 2026-09-23
Sender: Chief of Staff
Receiver: Chief Architect / CTO
Task: `V06-PR-06`
Disposition: **AUTHORIZED - CONSOLIDATED PERSONAL-PROTOTYPE INTEGRATION PLAN**

## Objective

Prepare one implementation-ready architecture package for exposing the accepted v0.6 Personal Recall read-only S0/S1 capability through the personal JARVIS prototype.

This task is planning and exact-contract reconciliation only. It must produce a complete implementation boundary so Engineering can execute once, without discovering ordinary prerequisites through serial handoffs.

## Accepted inputs

- Personal Recall Core candidate commit `cf7ac875cea1843295e825ea4322696d42af9ce1`, tree `56b27a9d6663eabb39692925f662c663ca6adc62`.
- [Handoff 20](20-chief-of-staff-personal-recall-closeout-acceptance.md), which accepts the read-only S0/S1 proof and freezes its limitations.
- The currently accepted J.A.R.V.I.S personal-prototype candidate and its active Voice Shell/Core bridge contracts, to be identified from Git and the canonical coordination record rather than inferred from chat.
- Existing sensitivity-aware provider-routing decisions, including local handling expectations for private material.

## Required package

Return one Handoff 22 containing all of the following:

1. Exact Core and J.A.R.V.I.S repository, branch, commit and tree identities proposed as implementation bases.
2. Current public API inventory for Personal Recall and the frontend bridge/controller/CLI surfaces that would consume it.
3. A one-way dependency design preserving `Voice Shell -> shell-owned bridge -> versioned Core application API`; no legacy runtime imports.
4. User-visible flows for:
   - asking JARVIS to search or recall personal notes;
   - displaying ranked results and revision-bound citations;
   - clearly labeling unresolved/retrieve-only results as candidates rather than answers;
   - handling no result, denied scope, malformed note, stale source, cancellation, reset and Core unavailable states.
5. Sensitivity and provider behavior:
   - Personal Recall itself remains local and provider-free;
   - no note content is sent to Gemini or another remote provider by default;
   - any later use of recalled context in a remote-model prompt remains separately governed by the accepted routing/approval policy;
   - private/local-only content must fail closed or route only to the accepted local path when that path is available and authorized.
6. A bounded immutable DTO and lifecycle mapping from Core recall results to the frontend, including source identity, citation locator, revision fingerprint, coverage/result semantics and safe errors.
7. Exact source/test/document paths permitted for implementation in both repositories, with no placeholders.
8. Dependency, environment and executor preflight: required Python/runtime versions, editable/install arrangement, Windows versus Linux responsibilities, Git permissions and any generated-artifact cleanup.
9. One consolidated test matrix covering contract, structural isolation, authorization, privacy, citations, cancellation/reset, concurrency, deterministic rendering, CLI behavior and an offline end-to-end mock/fixture demonstration.
10. A working-prototype demonstration plan that a nontechnical Product Owner can run locally, with expected visible behavior and rollback.
11. Explicit exclusions: no durable memory, embeddings, persistent index, automatic background vault watching, source-vault writes, live voice activation, provider activation, merge, push or release unless separately authorized.
12. One implementation task proposal sized to complete code, tests, demonstration and immutable candidate commits in one Engineering cycle. Ordinary internal defects must remain inside that task.

## Required review discipline

- Inspect the actual accepted code and contracts; do not design from handoff summaries alone.
- Resolve all known path, environment, dependency, executor and Git-precondition questions before returning.
- Reuse existing DTOs and application operations where possible; identify every intentional contract addition.
- Do not propose direct imports between the legacy runtime and Voice Shell.
- Do not create a sequence of discovery tasks. Return one complete package or one genuine scope-changing blocker with a recommended route.

## Boundary

No source code, private vault content, credential, provider, model, microphone, speaker, worktree, branch, commit, merge or push may be changed by this planning task. Read-only repository inspection and documentation/worklist updates are authorized.
