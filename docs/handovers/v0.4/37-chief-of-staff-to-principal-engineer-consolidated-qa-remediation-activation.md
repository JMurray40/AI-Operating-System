# Handoff 37 — Chief of Staff to Principal Engineer: Consolidated QA Remediation Activation

**Date:** 2026-07-30

**Disposition:** **AUTHORIZED — EXECUTE HANDOFF 36 AS ONE COMPLETE CYCLE**

**Starting branch:** `feature/v0.4-project-resume`

**Starting evidence commit:** `61734825be2cf096608ade0fd6eefc2c731ede68`

**Frozen runtime:** `ff402d7f82c061426a5e960f7177d916c355bbf2`

**Frozen wheel SHA-256:** `8dcc1378a1ac4c3b96dbfea94c0443e92ffaec54fafeb1db5aa73e449a768cd3`

## Activation

Execute Handoff 36 Sections 4 through 9 and its complete regression matrix exactly.

Complete QF-01, QF-02, and QF-03 before returning:

1. retain all 120 synthetic attempts and all 480 timing observations, plus the frozen
   5,000-note memory observation;
2. implement the Product Owner's weighted A11 numerator/denominator, validation, sampling,
   privacy, example-exclusion, and zero-denominator semantics;
3. stage only the accepted wheel and identity manifest under `dist/release/ff402d7/`;
4. recoverably quarantine every stale same-named wheel outside release selection;
5. run the complete regression gate once;
6. prove 68/68 runtime payload and 6/6 metadata byte equivalence;
7. update the private manifest, public evidence, and Engineering handoff with binary-safe
   exact identities; and
8. create one remediation commit and stop.

## Convergence rules

- Do not return partial findings.
- Do not rerun pilots or A12.
- Do not change `src/`, packaging metadata, ADRs, benchmark scripts, runtime tests, pilots,
  classifications, local-Git, authorization, citations, budgets, or private baselines.
- A private ignored driver may expose already produced frozen-harness observations only as
  authorized by Handoff 36.
- Do not delete stale wheels; quarantine must remain recoverable.
- Do not claim wheel or A12 applicability as accepted; propose it for the next CTO review.
- Stop the complete cycle if any Handoff 36 stop condition occurs.

## Required return

Return every item in Handoff 36 Section 9, including:

- exact remediation commit and complete changed-file scope;
- raw observation counts and recomputation;
- final public/private artifact hashes;
- A11 schema/formula/test mapping;
- staging and quarantine inventory;
- complete regression results and skips;
- payload/metadata equivalence;
- unchanged pilot/A12/runtime proof;
- privacy, link, whitespace, and clean-state results; and
- one consolidated residual-limitations section.

Freeze and stop for Chief of Staff validation.

## Still closed

No Quality review, merge, push, tag, release, publication, A11 collection, pilot or
classification changes, unrelated work, or v0.5 is authorized.
