# Current Project Handoff

| Field | Current value |
|---|---|
| Updated | 2026-08-15 |
| Updated by | Principal Engineer (return) |
| Milestone | v0.5 Personal Prototype |
| Active worklist | [v0.5 personal prototype](worklists/v0.5-prototype.json) |
| Current task | `V05-PT-35` - Formally evaluate exact qwen2.5:7b with synthetic-only evidence |
| Task status | `ready_for_review` |
| Owner | Principal Engineer |
| Reviewer | Chief Architect / CTO |
| Product Owner decision | [PT32 acceptance and next gates](reviews/V05-PT-32-PRODUCT-OWNER-ACCEPTANCE-AND-NEXT-GATES.md) |
| Architecture | [Handoff 138](../../.worktrees/v0.3.1-release/docs/handovers/v0.5/138-cto-to-product-owner-sensitivity-aware-provider-routing-disposition.md) |
| CTO disposition | [Handoff 141](../../.worktrees/v0.3.1-release/docs/handovers/v0.5/141-cto-to-product-owner-local-model-security-and-profile-disposition.md) |
| Documentation pin | `d345910f6239f5707975c77c45ea3759249d145e` (tree `a68b0d0657fc752cfe2ef017ffaecdbe8ffd27aa`) |
| Exact candidate | `08b0b11383031d6e91f6f26145bfdffc710ca36b` (tree `df041615730ee65faa6001f717f2ccff3b8d726c`) |
| Latest return | [Handoff 145](../../.worktrees/v0.3.1-release/docs/handovers/v0.5/145-principal-engineer-to-cto-qwen25-7b-synthetic-evaluation-return.md) |
| PT34 evaluation disposition | [Handoff 144](../../.worktrees/v0.3.1-release/docs/handovers/v0.5/144-cto-to-product-owner-local-model-evaluation-disposition.md) |
| Product Owner authorization | [PT35 authorization](reviews/V05-PT-34-PRODUCT-OWNER-QWEN-EVALUATION-AUTHORIZATION.md) |
| PT33 clearance | [Handoff 142a](../../.worktrees/v0.3.1-release/docs/handovers/v0.5/142a-cto-to-chief-of-staff-local-runtime-confinement-clearance.md) |
| Current state | qwen2.5:7b synthetic evaluation returned READY FOR REVIEW. Latency median 3.07 s PASS; p95 120.3 s FAIL under fixed counting (COLD load + one warm-4K timeout); quality 80/100 numeric but hostile-output critical failure fails the zero-critical clause; concurrency/cancellation/controls/stability pass; typed context-limit remains an untyped-hang outlier. No profile is active. |
| Next role | Chief Architect / CTO |
| Required next action | Review Handoff 145 and evidence under `docs/evidence/v0.5/pt35-qwen25-7b-synthetic/`; decide the exact local profile disposition per the authorized pass_route and route a Product Owner profile decision. |
| Product Owner action | Pending CTO review of PT35; PO decides the consequential profile disposition after CTO acceptance. |

## Do not do

- Do not continue PT35 sampling, retry the retained run, or substitute a model.
- Do not activate any local profile, load a model, run inference, install, download, update, or expose private data.
- Do not modify the accepted executable candidate or documentation pin.
- Do not change the current confinement state (startup shortcut, rules, listener) outside a separately authorized task.
- Do not activate Engineering, Quality, packaging, certification, merge, push, publication, release, or unrelated work.

## Required validation

```text
python scripts/validate_worklist.py docs/coordination/worklists/v0.5-prototype.json
```