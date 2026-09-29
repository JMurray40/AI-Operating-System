# Handoff 15 - Personal Recall absence-control correction

Date: 2026-09-23
Sender: Chief of Staff
Receiver: Principal Engineer
Task: `V06-PR-03`
Disposition: **AUTHORIZED - ONE CONSOLIDATED BENCHMARK-CONTRACT CORRECTION**

## Review disposition

[Verified] Handoff 14 proves the snapshot mechanism worked: one immutable 27-file snapshot was validated, three deterministic runs completed, all positive recall gates passed, citations bound valid source bytes, performance passed and prohibited effects remained zero.

[Verified] The failed acceptance gate conflated two distinct requirements from the accepted plan:

- The two `negative` questions are authorization-safety controls. Handoff 246 and Handoff 258 require excluded sources and their identities/content to remain absent. They do not require the retrieval engine to return no authorized citations.
- The one `missing` question requires coverage `none` **or equivalent** and no unsupported answer. S1 is explicitly retrieve-only. Its ranked, cited passages are candidate search results, not an asserted answer.

[Inferred] Applying `coverage != none` to all three rows is therefore not a valid implementation of the accepted matrix. Citation coverage describes the returned passages; it does not establish that the system asserted the absent fact.

## Required correction

Correct and verify the benchmark contract without editing the private manifest, source snapshot, accepted Core retrieval algorithm or Product Owner gates:

1. Preserve every Handoff 14 failed artifact unchanged.
2. Keep the retained snapshot byte-identical and reverify its closed inventory before and after execution.
3. Evaluate `negative` rows solely as authorization controls:
   - every returned source must belong to the authorized snapshot;
   - no excluded source identity, content or path may appear in private or public results;
   - authorized candidate citations are permitted and remain subject to ordinary citation validation.
4. Add an explicit typed S1 response semantic distinguishing **ranked retrieval candidates** from an **answer claim**. This may be benchmark/result-contract metadata within the authorized seven-file candidate; it must not invent an answer-generation layer.
5. For the `missing` row, require:
   - no answer claim is emitted;
   - the result is explicitly labeled unresolved/retrieve-only (fixed typed value);
   - any returned candidates remain clearly identified as candidates, not an answer;
   - every candidate citation still validates against the immutable snapshot;
   - no expected/alternate answer source is claimed as found.
6. Add adversarial tests proving:
   - an excluded identity/content leak fails a negative control even if all citations otherwise validate;
   - authorized incidental candidates do not fail an authorization-negative control;
   - a missing row with any asserted answer claim fails;
   - a missing row labeled unresolved with valid candidate citations passes;
   - public evidence cannot expose question text, source identity/content or raw errors.
7. Run the full synthetic/Core gates and Ruff.
8. Run one corrected three-repetition proof against the same retained snapshot.
9. Return one complete superseding Handoff 16 with exact candidate/evidence identities and reconciliation to the preserved Handoff 14 failure.

## No gate weakening

This correction does not waive absence behavior. It makes the gate test the actual S1 contract:

- authorization-negative questions prove non-disclosure of excluded material;
- the missing-answer question proves no unsupported answer claim;
- citations continue to prove only the provenance of ranked candidates.

The positive recall, determinism, performance, privacy, source-integrity and no-effects gates remain unchanged.

## Execution and handoff policy

Ordinary in-scope defects must be corrected and retested inside this task. Do not return another handoff for an internal bug. Return early only for required human action, missing authority, unsafe/irreversible action, unavailable external capability or a scope-changing architecture/privacy decision.

The retained snapshot must not be deleted or recreated. Cleanup remains separately governed after independent acceptance. No source-vault write, manifest edit, broader scope, provider, credential, network access, embedding, persistent index, frontend activation, commit, merge or push is authorized.
