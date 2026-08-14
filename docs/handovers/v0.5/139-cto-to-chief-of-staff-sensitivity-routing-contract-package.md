# Handoff 139 - CTO to Chief of Staff: Sensitivity-routing Contract Package

| Field | Value |
|---|---|
| Date | 2026-08-14 |
| From | Chief Architect / CTO |
| To | Chief of Staff |
| Milestone | v0.5 Personal Prototype |
| Task | `V05-PT-31` |
| Status | **READY FOR CHIEF-OF-STAFF VALIDATION - IMPLEMENTATION NOT AUTHORIZED** |
| Frozen Voice candidate | `08b0b11383031d6e91f6f26145bfdffc710ca36b` |
| Frozen Voice tree | `df041615730ee65faa6001f717f2ccff3b8d726c` |
| Product Owner decision | [PT30 acceptance](../../../../../docs/coordination/reviews/V05-PT-30-PRODUCT-OWNER-ACCEPTANCE-AND-NEXT-GATES.md) |
| Architecture source | [Handoff 138](138-cto-to-product-owner-sensitivity-aware-provider-routing-disposition.md) |

## 1. Disposition

**THE DOCUMENTATION-ONLY ADR-0025 CONTRACT PACKAGE IS COMPLETE AND READY FOR INDEPENDENT
VALIDATION.** It freezes session-active standing grants, strict-mode behavior, deterministic
destination-before-retrieval routing, local-only sensitive/mixed handling, no remote fallback,
route-visible UX, typed failure semantics, provider constraints, threat controls, and C31-C40.

ADR-0023 and ADR-0024 remain unchanged as historical accepted decisions. Proposed ADR-0025
supersedes only their per-turn-human-confirmation, single-real-adapter, and no-selection portions.
Their immutable snapshot, exact binding, non-streaming gateway, normalized terminal states,
credential isolation, and no-fallback controls remain effective.

## 2. Exact documentation inventory

This PT31 package changes or adds only:

1. `docs/adr/ADR-0025-Standing-Trust-Grants-And-Sensitivity-Aware-Provider-Routing.md`
2. `docs/adr/README.md`
3. `docs/software/V0.5_VISIBLE_CONTEXT_CONVERSATION_REQUIREMENTS.md`
4. `docs/software/V0.5_VISIBLE_CONTEXT_CONVERSATION_ARCHITECTURE.md`
5. `docs/product/V0.5_VISIBLE_CONTEXT_CONVERSATION_ACCEPTANCE_TESTS.md`
6. `docs/reviews/SECURITY_THREAT_MODEL.md`
7. `docs/software/CLI_USAGE.md`
8. `docs/software/EXTENDING.md`
9. `docs/handovers/v0.5/README.md`
10. this Handoff 139.

Pre-existing uncommitted coordination/evidence/handoff files are outside PT31 and remain preserved.
No executable, test, script, packaging, dependency, configuration, provider, pilot, model, policy,
credential, or private-evidence file was changed.

## 3. Requirement-to-contract mapping

| Accepted Handoff 138 decision | Contract location |
|---|---|
| Exact route before retrieval | ADR-0025 Decision; Requirements R2/R4; Architecture ordering; C31/C34 |
| Ordinary Gemini under standing grant | ADR-0025; Requirements R4/R11; Architecture egress authorization; C32-C34 |
| Sensitive/mixed local-only | ADR-0025 route table; Requirements R4; Architecture lifecycle; C34-C38 |
| Missing/unknown excluded | ADR-0025; Requirements R2/R4; C03/C31/C34 |
| No remote fallback or context splitting | ADR-0025; Requirements R4/R8; Architecture gateway/failure; C35/C37 |
| Session-active lifecycle and strict mode | ADR-0025; Requirements R1/R4/R11; Architecture lifecycle; C32/C33/C36/C40 |
| Exact local feasibility/profile gate | ADR-0025 consequences/evidence; EXTENDING; threat-model residual risk; C38 |
| Route-visible safe UX and typed failures | Requirements R8/R11; CLI Usage; acceptance degraded matrix/C39 |
| Immutable snapshot/current-byte/prompt binding preserved | ADR-0025; Requirements R3/R4; Architecture; C07-C13/C33 |
| Read-only, privacy and regression boundaries | Requirements R9/R10; threat model; C26-C30/C41-equivalent full gate in Handoff 138 |

The complete Handoff 138 adversarial matrix maps to existing C01-C30 plus new C31-C40. The final
full-regression requirement remains C30 and the Evidence Rules; no aggregate pass can waive a
security stop.

## 4. Frozen semantics

- `public`/`internal` ceilings may use only exact granted Gemini.
- `private`/`restricted` and mixed ceilings may use only an exact approved local Ollama profile.
- Missing/unknown sensitivity has no destination and remains excluded before selection.
- One request has one route; no split, fallback, implicit declassification, or `send anyway` path.
- A lower-ceiling remote operation is a new request with visible omissions and non-complete coverage.
- Jarvis validates but never creates, edits, broadens, or approves the owner policy.
- Standing activation is exact and process-local; strict mode cannot override destination
  eligibility.
- Local adapter traffic is loopback-only and exact-profile-bound; non-loopback, proxy, telemetry,
  update, cloud, ambient override, redirect, tools, memory, and fallback are denied.
- No exact Ollama runtime/model is approved by this package.

## 5. Validation required from Chief of Staff

Independently verify:

1. all ten governed paths and no executable scope;
2. ADR-0025's precise supersession and preservation of ADR-0023/0024 invariants;
3. no conflicting per-turn-only, one-real-adapter, automatic-fallback, or Ollama-deferred statement
   remains in the active amended contracts;
4. C01-C40 collectively cover Handoff 138's frozen adversarial matrix;
5. cross-document links, UTF-8, Markdown structure, and whitespace;
6. frozen candidate identity remains unchanged; and
7. no PT32 inventory action occurred.

If accepted, Chief of Staff may pin this documentation package and separately activate pre-authorized
PT32. Acceptance does not authorize implementation, installation, model acquisition, inference,
credentials, network changes, private-data use, packaging, certification, merge, push, publication,
or release.

## 6. Risks and unresolved decisions

The target host and Ollama/model feasibility are unknown. PT32 is limited to existing-state,
ordinary-access inventory and must distinguish facts from unavailable measurements. Exact runtime,
model, digests, license, budgets, performance, acquisition, installation, and synthetic execution
all require later decisions. Until then sensitive generation remains unavailable.

## 7. Exit statement

**READY FOR CHIEF-OF-STAFF VALIDATION.** PT31 is documentation-only. PT32 remains blocked until the
Chief of Staff accepts and pins this package. The executable candidate and every downstream gate
remain frozen.
