# Handoff 02 — Chief of Staff to Product Owner: v0.5 Planning Validation

**From:** Chief of Staff
**To:** Product Owner — Jason
**Date:** 2026-08-01
**Planning base:** `main@1813f845a6d3250d33fd8f5862579b89dab03306`
**Scope:** Validation of the proposed v0.5 Visible-Context Conversation planning package
**Disposition:** **VALIDATED — READY FOR PRODUCT OWNER SCOPE DECISIONS; IMPLEMENTATION NOT AUTHORIZED**

## 1. Validated package

The proposed package contains:

- [Requirements](../../software/V0.5_VISIBLE_CONTEXT_CONVERSATION_REQUIREMENTS.md);
- [Architecture](../../software/V0.5_VISIBLE_CONTEXT_CONVERSATION_ARCHITECTURE.md);
- [Acceptance tests](../../product/V0.5_VISIBLE_CONTEXT_CONVERSATION_ACCEPTANCE_TESTS.md);
- [Historical candidate assessment](../../software/V0.5_HISTORICAL_CONVERSATION_CANDIDATE_ASSESSMENT.md);
- [CTO planning disposition](01-cto-to-product-owner-conversation-planning-disposition.md);
- proposed ADR-0022 through ADR-0024; and
- the updated ADR index.

The separate [project overview and timeline](../../PROJECT_OVERVIEW_STATUS_AND_TIMELINE.md)
provides a plain-language status summary but does not create requirements or authority.

## 2. Chief-of-Staff review result

The package is coherent with the released v0.3.1 trust contracts and v0.4 Project Resume
boundaries. It:

- keeps conversation above the deterministic query/evidence pipeline;
- requires source authorization and destination eligibility before retrieval;
- requires visible context inspection and digest-bound approval before prompt assembly and
  remote dispatch;
- binds all deterministic prompt inputs and their versions to the approved snapshot;
- separates approved content-bearing provider fields from allowlisted transport metadata
  and opaque credential transport;
- keeps retrieval relevance separate from answer assurance;
- requires current passage/revision evidence for supported generated claims;
- treats source text, user input, and provider output as untrusted data;
- provides no vault-write, tool, plugin, MCP, agent, fallback, or general network port;
- keeps conversation state bounded, process-local, and non-durable;
- excludes real and simulated streaming from v0.5;
- requires one real provider plus a deterministic mock before release;
- preserves explicit failure, cancellation, privacy, usage, cost, trace, and evidence
  semantics; and
- parks the historical conversation branch as a design spike rather than accepted code or
  evidence.

The prior Chief-of-Staff findings are closed:

1. approval now binds prompt-template, assembler, history serialization, token estimator,
   safety instruction, and output-reserve inputs and versions;
2. C09 blocks dispatch if any bound input changes after approval;
3. C13 separately validates exact content fields, transport allowlists, credentials,
   endpoint behavior, redirects, telemetry, and fallback;
4. attachment wording no longer conflicts with the hard exclusion; and
5. source authorization, destination eligibility, user approval, prompt assembly, and
   dispatch ordering is stated consistently.

## 3. Recommended scope

Approve the CTO's narrow slice:

- CLI plus versioned in-process application API;
- session-only state;
- visible context and per-turn removal/approval;
- immutable, digest-bound request snapshots;
- one approved real provider and one deterministic mock;
- normalized complete-response dispatch without streaming;
- evidence-backed claims, safe rendering, and redacted trace; and
- all documented non-goals as hard exclusions.

This is the smallest release that provides real conversational value while proving the
provider-egress trust boundary.

## 4. Product Owner decisions required

### PO-01 — Roadmap sequence

**Recommendation:** Keep v0.5 as Visible-Context Conversation, move Proposed Memory to
v0.6, and move Semantic Search and Relationship Intelligence to v0.7. Renumber Plugin/MCP,
Agents, and Automation after those releases during roadmap reconciliation.

### PO-02 — Session lifecycle

**Recommendation:** Accept proposed ADR-0022. v0.5 retains no transcript after reset or
process exit and provides no archive, search, export, resume, or transcript-deletion
workflow because Jarvis stores no transcript.

### PO-03 — Product surface

**Recommendation:** Approve CLI plus an in-process application API. Defer graphical UI and
public HTTP service.

### PO-04 — Streaming

**Recommendation:** Accept proposed ADR-0024. Defer provider-response streaming and prohibit
simulated post-completion streaming.

### PO-05 — Real provider

**Decision required:** Select exactly one real provider and approve its endpoint,
data-use/retention terms, credential source, model role/configuration, request/evidence
budget, and permitted release-test spend. Mock-only evidence is insufficient.

The provider choice must not be inferred from an existing consumer subscription. ChatGPT,
Claude, or Gemini subscription access does not by itself authorize or fund the associated
developer API.

### PO-06 — Per-turn egress approval

**Recommendation:** Accept proposed ADR-0023. Every remote turn requires visible context
inspection and approval bound to the immutable snapshot. No workspace-level “always
approve” bypass is included in v0.5.

### PO-07 — Scope exclusions

**Recommendation:** Approve every documented non-goal as a hard exclusion, including
durable transcripts, memory proposals, attachments, tools, plugins, MCP, agents, graphical
UI, public server, semantic retrieval, streaming, automatic provider fallback, live GitHub,
and vault writes.

## 5. Evidence and implementation boundary

The proposed C01–C30 acceptance matrix is complete enough to govern a future implementation
brief. It is not executed evidence. Historical candidate tests and benchmarks do not count.

Product Owner approval of PO-01 through PO-07 will authorize:

- acceptance of the proposed product scope and ADRs;
- controlled roadmap reconciliation; and
- preparation of a separate CTO implementation brief.

It will not itself authorize:

- a branch or worktree;
- source, test, script, package, or provider changes;
- provider calls or evidence spend;
- Principal Engineering implementation;
- reuse or modification of the historical candidate;
- QA, merge, tag, release, or publication; or
- v0.6 implementation.

Those actions require later exact, role-specific authorization.

## 6. Chief-of-Staff recommendation

**Approve PO-01 through PO-04, PO-06, and PO-07 as recommended. Select and bound one real
provider under PO-05.** After those decisions are recorded, authorize documentation-only
roadmap reconciliation and a CTO implementation brief for separate Chief-of-Staff
validation.
