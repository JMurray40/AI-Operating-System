# Handoff 35 — Product Owner: A11 Metric and QA Remediation Decision

**Date:** 2026-07-30

**Disposition:** **APPROVED FOR CTO REMEDIATION AUTHORIZATION**

## Product Owner decision

The Product Owner approves the consolidated QF-01/QF-02/QF-03 remediation plan in
Handoff 34 and freezes the A11 sourcing metric below.

## Frozen A11 sourcing metric

- `material_claims_reviewed`: count of material claims manually reviewed during the weekly
  claim-review sample.
- `material_claims_correctly_sourced`: count of those reviewed claims whose citation supports
  the claim and is bound to the correct current source or repository revision.
- `correctly_sourced_rate`:
  `material_claims_correctly_sourced / material_claims_reviewed`.
- When `material_claims_reviewed` is zero, the rate is `null`; no sourcing threshold result
  may be reported.
- Each weekly record must identify the sampling procedure and sample size without retaining
  claim text, citation text, private paths, or source content.
- Example and template rows remain excluded.
- The 90–95% target may be evaluated only with a non-zero denominator.
- The eight-week outcome remains pending until the complete approved collection period
  finishes.
- `citation_defects` remains a separate diagnostic count and is not substituted for the
  numerator or denominator.

## Approved remediation intent

The Product Owner approves routing to the CTO for one bounded authorization covering:

1. retained raw synthetic timing and memory evidence without pilot reruns;
2. the A11 template/evaluator/test/documentation changes necessary to implement the frozen
   metric;
3. candidate-specific release staging and quarantine of superseded same-named wheels;
4. one complete engineering regression gate;
5. runtime-payload equivalence proof for the accepted wheel;
6. exact-commit CTO review and explicit A12/wheel reuse determination; and
7. limited Quality revalidation of the three findings and affected review areas.

## Authority boundary

This decision defines Product intent and authorizes CTO routing. It does not itself authorize
Engineering changes, evidence execution, wheel movement, QA, merge, push, tag, release,
publication, A11 data collection, or v0.5.
