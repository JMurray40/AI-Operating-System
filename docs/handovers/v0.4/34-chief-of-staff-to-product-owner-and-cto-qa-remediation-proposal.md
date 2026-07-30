# Handoff 34 — Chief of Staff to Product Owner and CTO: Consolidated QA Remediation Proposal

**Date:** 2026-07-30

**Disposition:** **ONE PRODUCT DECISION REQUIRED; CONSOLIDATED REMEDIATION RECOMMENDED**

**QA disposition:** `Not ready`, commit `aa8d5a76404359f1f43108b2abde47d3d8527aac`

## Chief of Staff validation

The Quality artifact is the sole path changed by its commit. The executable and evidence
views remain clean and unchanged.

The three findings are valid but do not require another broad implementation cycle:

| Finding | Classification | Recommended closure |
|---|---|---|
| QF-01 synthetic raw samples absent | Evidence-only | Rerun only the frozen synthetic 100/500/1,000/5,000-note protocol while retaining all raw timing and memory observations |
| QF-02 A11 sourcing denominator absent | Product mechanism | Product Owner freezes numerator/denominator; Engineering updates only the dogfood template, evaluator, tests, and directly affected documentation |
| QF-03 stale same-named wheels | Release hygiene | Create an identity-bound release staging directory containing only the verified wheel and manifest; quarantine superseded wheels outside release staging |

The Quality artifact also contains four Markdown hard-break lines that fail
`git diff --check`. Quality should correct that formatting when appending its superseding
revalidation; it is not an executable defect.

## Product Owner decision — recommended A11 sourcing metric

The Chief of Staff recommends the following exact definition:

- `material_claims_reviewed`: count of material claims manually reviewed during the weekly
  claim-review sample;
- `material_claims_correctly_sourced`: count of those reviewed claims whose citation
  supports the claim and is bound to the correct current source/repository revision;
- `correctly_sourced_rate`:
  `material_claims_correctly_sourced / material_claims_reviewed`;
- when the denominator is zero, the rate is `null` and no threshold result is reported;
- the weekly record must identify the sampling procedure and sample size, without storing
  claim text, citation text, private paths, or source content;
- example/template rows remain excluded;
- the evaluator may report the 90–95% target only after a non-zero denominator exists; and
- the eight-week outcome remains pending until the complete Product Owner-approved collection
  period finishes.

`citation_defects` may remain as a separate diagnostic count, but it is not substituted for
either the numerator or denominator.

## Consolidated remediation sequence

After Product Owner approval, request one bounded CTO authorization for:

1. **QF-01:** evidence-only synthetic rerun using the exact frozen executable and frozen
   benchmark semantics; retain every launched timing and peak-memory observation, independently
   recompute aggregates, update the private manifest/public performance evidence/Engineering
   handoff, and do not rerun pilots;
2. **QF-02:** change only the A11 template, offline evaluator, their tests, and directly
   affected documentation to implement the frozen metric above;
3. **QF-03:** stage only wheel SHA-256
   `8dcc1378a1ac4c3b96dbfea94c0443e92ffaec54fafeb1db5aa73e449a768cd3`
   in a clean candidate-specific release directory with a size/digest manifest, and move
   superseded same-named wheels into clearly labeled non-release quarantine locations;
4. re-run the full engineering gate once;
5. prove the wheel's 68 runtime payloads remain byte-identical because QF-02 changes no
   packaged runtime path or packaging metadata;
6. return through one exact-commit CTO review that explicitly determines whether the accepted
   wheel and A12 evidence remain applicable to the documentation/evaluator-only descendant; and
7. authorize Quality to revalidate only QF-01, QF-02, QF-03, affected Areas A/H/I/J, final
   identities, and regression gates.

No local-Git, pilot, classification, packaging metadata, runtime payload, or A10 pilot
evidence should be reopened.

## Required Product Owner response

Approve or revise the A11 numerator/denominator definition above. Approval also authorizes the
Chief of Staff to route the complete bounded proposal to the CTO; it does not itself authorize
Engineering changes, wheel movement, or evidence execution.

## Gate state

Quality remains `Not ready`. No Engineering remediation, evidence rerun, artifact movement,
merge, push, tag, release, publication, A11 data collection, or v0.5 work is authorized yet.
