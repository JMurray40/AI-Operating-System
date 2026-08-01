# Handoff 05 — Product Owner to CTO: v0.5 Conversation Scope Approval

**From:** Product Owner — Jason Murray  
**To:** Chief Architect / CTO  
**Date:** 2026-08-01  
**Decision base:** `main@f3ab481f8bb79278fc674f13848700aa192ef3d5`  
**Milestone:** v0.5 — Visible-Context Conversation  
**Disposition:** **SCOPE AND ADRS APPROVED — CTO IMPLEMENTATION BRIEF AUTHORIZED; IMPLEMENTATION NOT AUTHORIZED**

## 1. Accepted decisions

The Product Owner approves the validated recommendations in
[Handoff 01](01-cto-to-product-owner-conversation-planning-disposition.md) and
[Handoff 02](02-chief-of-staff-to-product-owner-planning-validation.md):

1. v0.5 remains **Visible-Context Conversation**.
2. Proposed Memory moves to **v0.6**.
3. Semantic Search and Relationship Intelligence move to **v0.7**. Later unreleased
   plugin, agent, and automation milestones may be renumbered during roadmap closeout.
4. ADR-0022, ADR-0023, and ADR-0024 are accepted.
5. The first v0.5 product surface is a CLI plus a versioned in-process application API.
6. Conversation state is bounded, process-local, and session-only.
7. Every remote turn requires inspection and digest-bound approval of immutable visible
   context before prompt assembly and dispatch.
8. Release scope requires exactly one approved real provider adapter plus a deterministic
   mock adapter.
9. Provider-response streaming and simulated post-completion streaming are excluded.
10. Durable transcripts, memory proposals, attachments, tools, plugins, MCP, agents,
    graphical UI, public server, semantic retrieval, automatic provider fallback, live
    connectors, and vault writes are excluded.
11. The historical `feature/v0.4-conversation@4b09050b76fd9a448af3ce91b4aa66963d23dad2`
    remains read-only design-spike material. It is not an implementation base or accepted
    evidence and must not be reused wholesale.

## 2. Accepted architecture package

- [Requirements](../../software/V0.5_VISIBLE_CONTEXT_CONVERSATION_REQUIREMENTS.md)
- [Architecture](../../software/V0.5_VISIBLE_CONTEXT_CONVERSATION_ARCHITECTURE.md)
- [Acceptance tests](../../product/V0.5_VISIBLE_CONTEXT_CONVERSATION_ACCEPTANCE_TESTS.md)
- [Historical candidate assessment](../../software/V0.5_HISTORICAL_CONVERSATION_CANDIDATE_ASSESSMENT.md)
- [ADR-0022](../../adr/ADR-0022-Conversation-Is-A-Session-Only-Application-Layer.md)
- [ADR-0023](../../adr/ADR-0023-Conversation-Uses-Immutable-Visible-Context-Snapshots.md)
- [ADR-0024](../../adr/ADR-0024-V0.5-Uses-Normalized-Non-Streaming-Provider-Dispatch.md)

Acceptance establishes requirements and gates; it is not implementation evidence.

## 3. Open provider-selection gate

The Product Owner has approved the requirement for one real provider but has not yet named
or funded that provider. Before the CTO can issue an implementation-ready brief, the
Product Owner must separately approve:

- provider and model;
- exact endpoint and redirect policy;
- credential source;
- provider data-use and retention terms;
- model role and bounded configuration;
- per-request and total evidence budgets; and
- permitted release-test spend.

A consumer subscription does not imply developer API access or authorize API spending.
Engineering must not infer a provider from historical code, environment variables, local
subscriptions, the separate J.A.R.V.I.S Voice Shell project, or agent-model choices.

## 4. CTO authorization

The CTO is authorized to prepare the final v0.5 implementation brief and may identify
provider-neutral work packages, dependencies, branch/base requirements, and the complete
C01–C30 evidence mapping. The brief must expose the provider-selection gate and may not
silently select a provider.

Required output:

`docs/handovers/v0.5/06-cto-to-principal-engineer-conversation-implementation-brief.md`

The brief is not effective until the Chief of Staff validates it against an exact clean
documentation commit and separately authorizes Engineering.

## 5. Prohibited next work

This decision does not authorize:

- a v0.5 implementation branch or worktree;
- source, test, script, package, or provider changes;
- provider credentials, calls, network access, or evidence spend;
- modification, merge, rebase, or cherry-pick of the historical conversation candidate;
- Principal Engineering, QA, merge, push, tag, or release work;
- v0.6 implementation; or
- inclusion of the separate J.A.R.V.I.S Voice Shell prototype in v0.5.

## 6. Exit statement

**Ready for CTO implementation-brief preparation, with provider-specific authorization
blocked pending a separate Product Owner decision. v0.5 implementation remains
unauthorized.**
