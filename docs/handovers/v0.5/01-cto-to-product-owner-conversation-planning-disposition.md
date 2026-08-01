# Handoff 01 — CTO to Product Owner: v0.5 Conversation Planning Disposition

**From:** Chief Architect / CTO

**To:** Product Owner

**Date:** 2026-08-01

**Planning base:** `main@1813f845a6d3250d33fd8f5862579b89dab03306`

**Historical input:** `feature/v0.4-conversation@4b09050b76fd9a448af3ce91b4aa66963d23dad2`, inspected read-only

**Disposition:** **PROPOSED SCOPE IS ARCHITECTURALLY COHERENT — PRODUCT DECISIONS REQUIRED; IMPLEMENTATION NOT AUTHORIZED**

## 1. Package

This planning disposition is supported by:

- [Requirements](../../software/V0.5_VISIBLE_CONTEXT_CONVERSATION_REQUIREMENTS.md);
- [Architecture](../../software/V0.5_VISIBLE_CONTEXT_CONVERSATION_ARCHITECTURE.md);
- [Acceptance tests](../../product/V0.5_VISIBLE_CONTEXT_CONVERSATION_ACCEPTANCE_TESTS.md);
- [Historical candidate assessment](../../software/V0.5_HISTORICAL_CONVERSATION_CANDIDATE_ASSESSMENT.md); and
- proposed ADR-0022 through ADR-0024.

The package is documentation-only. It is not an implementation brief.

## 2. Recommended product slice

Approve a narrow v0.5 Visible-Context Conversation release with:

- interactive/scripted CLI and a versioned in-process application API;
- process-local, bounded, session-only conversation state;
- deterministic visible follow-up assumptions;
- full context inspection and removal before remote egress;
- immutable snapshot and digest-bound approval per remote request;
- released authorization, source identity, citation, conflict and budget contracts;
- deterministic mock plus exactly one approved real provider adapter;
- complete-response, non-streaming dispatch with cancellation, usage/cost and normalized
  failure; and
- no vault writes, durable memory, operational transcript store, tools, attachments,
  graphical UI, public server, provider fallback, or semantic retrieval.

This is the smallest coherent slice that proves the new provider trust boundary and gives a
user real conversational value without combining it with storage, UI, streaming, tools, or
memory risks.

## 3. Product Owner decisions

### PO-01 — Release identity and roadmap collision

**Recommendation:** Keep `v0.5 = Visible-Context Conversation`; assign Proposed Memory to
`v0.6`; move the currently assigned v0.6 Semantic Search and Relationship Intelligence to
`v0.7` or a later Product Owner-selected release, then renumber later unreleased milestones
deliberately.

**Consequences:** This preserves the already published conversation expectation and puts
reviewable memory immediately after conversation, but it creates a real collision with the
current v0.6 semantic-search assignment and may cascade into v0.7+ numbering. The accepted
roadmap must be amended explicitly after approval; this planning package does not edit it.

**Alternative:** Keep current v0.6 Semantic Search, place Proposed Memory at v0.7 or later,
and shift Plugin/MCP and subsequent unreleased releases. This avoids delaying semantic
retrieval but prolongs the gap between useful conversations and proposal-based durable
outcomes.

**Decision required:** Choose and record one complete sequence. Do not use the older draft
PRD target or parked ADR-0013 as authority.

### PO-02 — Session lifecycle

**Recommendation:** Approve proposed ADR-0022: v0.5 is session-only with no durable
conversation store.

**Consequence:** Strong privacy and smaller recovery surface; sessions cannot resume,
archive, search, export, or be deleted after process exit because Jarvis retains nothing.
Provider retention remains governed by the selected provider and must be disclosed.

**Alternative:** Include an encrypted operational store now. This requires a separate
architecture cycle for keys, retention, archive/search/export/delete, backups, migration,
crash recovery, and subject access, and materially delays v0.5.

### PO-03 — Product surface

**Recommendation:** Approve CLI plus in-process application API; defer graphical UI and
public HTTP service.

**Consequence:** Context visibility and policy behavior are testable now, and the API forms
a later UI seam. The release is not yet a consumer desktop experience.

### PO-04 — Streaming

**Recommendation:** Approve proposed ADR-0024 and defer real provider-response streaming.

**Consequence:** No first-token latency claim or dynamic partial output. The release avoids
shipping simulated streaming and can prove terminal, failure and cancellation behavior
first. A later decision must cover event ordering, partial retention and accessibility.

### PO-05 — Real provider

**Recommendation:** Require exactly one real remote adapter plus the deterministic mock.
Product Owner must name the provider and approve endpoint, data-use/retention terms,
credential source, model role/configuration, request budget, and evidence spend before
Engineering authorization.

**Consequence:** v0.5 demonstrates actual useful generation and the real egress boundary.
Mock-only would be safer but would not validate or deliver the named product capability.

### PO-06 — Explicit egress approval

**Recommendation:** Approve proposed ADR-0023: every remote turn uses prepare, visible
manifest, optional removal, immutable snapshot, digest-bound approval, revalidation, then
dispatch. The snapshot and approval also bind the prompt-template, assembler,
history-serialization, token-estimator, safety-instruction, and output-reserve
versions/value, so content-bearing dispatch fields are deterministically derived from the
approved semantic inputs. No “always approve this workspace” bypass exists in v0.5.

**Consequence:** One extra user confirmation per remote turn, traded for an exact and
auditable disclosure boundary. Local/mock non-egress operation can be policy-approved
without pretending to authorize cloud transfer.

### PO-07 — Scope exclusions

**Recommendation:** Approve all stated non-goals as hard exclusions. In particular, do not
combine v0.5 with memory proposals, transcript persistence, attachments, tools, UI,
semantic retrieval, streaming, automatic provider fallback, or live external connectors.

## 4. Architecture findings

The recommended design is compatible with ADR-0012 because conversation composes above the
query pipeline. ADR-0015 expands structurally through dispatch: source authorization and
destination eligibility precede retrieval and graph expansion; user digest-bound egress
approval follows context inspection and precedes prompt assembly and adapter access. ADR-0014 prevents
ranking values from becoming answer confidence. ADR-0016/0017 bind generated claims to
current passages and stable identities. ADR-0018/0019/0020 may be reused for exact project
selection, authority/conflict ordering, evidence coverage and complete budgets without
turning Project Resume into a hidden chat dependency. ADR-0021 remains unchanged and grants
no new repository command or network authority.

Proposed ADR-0022 through ADR-0024 are needed because session storage, context-to-egress
binding, real-provider scope, and streaming are consequential new trust-boundary decisions.

## 5. Historical candidate decision

Keep `4b09050` parked. Its layer separation, in-memory session, visible assumptions, mock
fixtures, and failure scenarios are useful concepts. Its relevance-as-confidence,
note-level citations, implicit entry scope, title-concatenation query shim, title/ID conflict
heuristics, and post-completion “streaming” are obsolete or conflicting. No prior tests or
benchmarks count as v0.5 evidence. There is no released data to migrate.

## 6. Required evidence if implementation is later authorized

The complete C01–C30 matrix in the acceptance-tests artifact is mandatory. It includes:

- structural authorization/non-disclosure and cross-workspace tests;
- immutable context, approval tamper/replay, current-byte and prompt-budget tests;
- real-adapter exact-byte egress, endpoint, secret, telemetry and fallback denial;
- claim/citation/coverage/relevance-confidence and prompt-injection adversarial tests;
- cancellation, failure, usage/cost, trace/privacy and safe-rendering tests;
- vault/repository immutability and full released regression suites;
- p50/p95/p99 and peak memory at 100/500/1,000/5,000 notes;
- accessible CLI, clean install, offline fixture, uninstall/reinstall and recovery; and
- exact artifact identities and independently recomputable raw evidence.

Any unauthorized egress, canonical mutation, excluded-source leak, hidden telemetry,
approval mismatch, cross-workspace leak, stale/fabricated citation, secret leak, or broadened
tool/write surface is an immediate stop.

## 7. Disposition and next gate

**Explicit architecture disposition: APPROVE FOR PRODUCT OWNER SCOPE DECISION ONLY.**

The Product Owner should accept, reject, or amend PO-01 through PO-07 and explicitly decide
the roadmap collision. If accepted, the Chief of Staff must validate the exact planning
package and pin its commit. Only a later, separate CTO implementation brief and Chief-of-
Staff activation may authorize an Engineering branch or work.

Until then:

- no v0.5 implementation branch/worktree;
- no code, tests, scripts, package, provider call, evidence run, pilot, or historical-branch
  change;
- no roadmap edit that implies the Product Owner decision; and
- no v0.5 implementation, QA, merge, push, tag, release, or v0.6 work.
