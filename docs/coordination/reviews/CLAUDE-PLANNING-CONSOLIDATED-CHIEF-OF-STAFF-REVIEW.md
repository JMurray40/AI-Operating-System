# Claude Planning — Consolidated Chief-of-Staff Review

**Date:** 2026-09-11

**Reviewer:** Chief of Staff

**Boundary:** Independent review of the ten advisory packages under
`J.A.R.V.I.S/Claude-Planning/`. This review does not authorize implementation,
alter a candidate, or supersede the active `V05-PT-58` baton.

## Executive disposition

The advisory cycle was worthwhile. Seven packages are accepted wholly or with a
punch list; three require a current-state rebase before they should drive work.
None should become ten separate execution chains. Accepted recommendations should
be consolidated into four future worklist items after Product Owner approval.

## Package dispositions

### 1. Pocket TTS evaluation — ACCEPT WITH PUNCHLIST

The engine comparison and protocol-preserving integration approach are useful.
However, PT53–PT58 have since performed more authoritative planning and live
acquisition work. Treat this document as research support for PT58, not as a new
TTS task. Reconcile any licensing, model-identity, dependency, or Windows claims
against the final PT58 closed manifest before citing them as accepted facts.

### 2. Frontend usability review — RETURN FOR REWORK

The backlog was written against PT51-era behavior. Subsequent interactive-shell,
usability, local-Qwen, and Gemini work materially changed the frontend. Preserve
the evaluation method, but re-run the review against the current accepted Voice
candidate after PT58. Do not open tickets from the existing priority labels.

### 3. v0.6 memory and semantic-search plan — ACCEPT WITH PUNCHLIST

The recommended order is sound: ship a read-only, rebuildable local search index
before durable agent-written memory. Open planning work only after the v0.5
personal prototype is usable. The task must first resolve version naming, define a
small personal-use MVP, and keep durable memory as a separate later authorization.

### 4. Adversarial test proposals — ACCEPT WITH PUNCHLIST

The proposal identifies valuable failure classes, especially malformed provider
responses, approval replay, cancellation races, citation manipulation, and secret
leakage. Before implementation, rebase every test against current Core and Voice
contracts, remove tests already covered by later PT work, and separate executable
regressions from tests blocked on unimplemented capabilities. Adopt the remaining
high-value tests as one bounded test-hardening task, not one task per category.

### 5. Codebase architecture audit — ACCEPT WITH PUNCHLIST

The concentration of debt in obsolete Voice planning/quarantine copies is
credible and actionable. Open a preservation-and-consolidation task, but authorize
inventory, canonical-owner selection, and archive proposals first. No directory
may be deleted or moved until exact recoverability and current references are
verified. Provider implementation findings must remain separate from cleanup.

### 6. Documentation consolidation — RETURN FOR REWORK

The proposed document set and reader-oriented structure are useful, but several
status documents were already stale when delivered and are older than PT58.
Regenerate `CURRENT_ARCHITECTURE`, `WHAT_CURRENTLY_WORKS`, `HOW_TO_RUN`, known
limitations, troubleshooting, provider policy, and decision history from the
accepted post-PT58 state. Link to canonical evidence rather than duplicating it.

### 7. Governance simplification — ACCEPT

This is the highest-value cross-project result. Adopt a tiered workflow,
capability-aware preflight, graded review outcomes, consolidated correction lists,
and a correction allowance within the same task. Preserve strict controls for
credentials, network changes, destructive operations, live provider calls, and
release evidence. Pilot the lighter process on the next low/medium-risk task and
measure handoff count, elapsed time, and correction rounds.

### 8. Future tool-permission framework — ACCEPT WITH PUNCHLIST

The capability vocabulary, risk tiers, visible approval for irreversible actions,
digest binding, cancellation, and append-only receipts are good design inputs.
Keep this as architecture work only. Reconcile it with ADR-0008 and the existing
blocked PT54 external-prior-art review before accepting any ADR or changing a
protocol. Do not implement tools during v0.5 voice work.

### 9. Mock scenario corpus — ACCEPT WITH PUNCHLIST

The synthetic fixtures are useful, particularly for demos and repeatable
regressions. Schema-validate all fixture files, reclassify scenarios against the
current implemented routing state, and distinguish executable expected outcomes
from aspirational design examples. Integrate the validated subset through the
single adversarial-test task described above.

### 10. Independent reviewer rubric — ACCEPT

Adopt this as the standard for Claude's advisory file-level reviews. It correctly
separates file verification from Windows runtime, hardware, network, and execution
claims and prevents an advisory reviewer from changing the worklist or baton.
Every such review must state its limitations and use “recommended disposition,”
never the authoritative “disposition.”

## Proposed consolidation into four future tasks

1. **Process pilot:** implement and measure the governance-simplification workflow.
2. **Current-state documentation refresh:** run after PT58 reaches a stable checkpoint.
3. **Adversarial and mock-fixture hardening:** rebase, deduplicate, schema-check,
   and implement the valuable current-contract tests.
4. **v0.6 architecture planning:** read-only semantic search first; durable memory
   later; include tool-permission/ADR reconciliation as a separate planning lane.

The frontend usability re-review and Voice repository cleanup should be acceptance
criteria within the documentation/current-state and architecture-hygiene work,
not independent handoff chains unless their rebased findings reveal code defects.

## Routing recommendation

Product Owner should approve or return the four-task consolidation as one bundled
decision. If approved, only the process pilot should be activated immediately and
only if it does not conflict with PT58. The other three remain planned until their
stated activation conditions are met.

No code, credential, provider, Windows configuration, Voice repository file,
candidate, worklist, or canonical baton was modified by this review.
