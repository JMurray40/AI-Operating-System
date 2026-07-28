# Prepared Prompt — CTO Architecture Conformance Review

**Inactive until:** the Principal Engineer has committed a clean candidate and completed
`docs/handovers/v0.4/02-principal-engineer-to-cto-engineering-review.md`.

Act as Chief Architect / CTO. Determine whether the exact v0.4 candidate conforms to the
accepted Project Resume architecture and is fit to enter independent QA.

Work read-only from a frozen review worktree at `<CANDIDATE_SHA>`. Begin with
`docs/coordination/README.md`, the v0.4 index, the Principal Engineer handoff, the final
CTO implementation brief, ADR-0012 and ADR-0014 through ADR-0021, and A1–A12.
Conversation history is not authoritative.

Verify:

- exact branch/base/candidate identity and complete diff;
- no parked conversation commit or excluded capability;
- authorization before selection, retrieval, graph, conflict, Git, trace, and errors;
- exact tiered project identity and safe ambiguity;
- authority, temporal, supersession, conflict, and staleness rules;
- current revision-bound claim support and visible coverage;
- independent hard evidence/output budgets across text, JSON, trace, and errors;
- ADR-0021's exact three-command local-Git allowlist, environment isolation, bounds,
  parsing, redaction, degradation, and non-mutation evidence;
- deterministic semantics and diagnostics isolation;
- A1–A10/A12 evidence, A11 mechanism with eight-week results explicitly pending;
- pilot privacy, performance, packaging, recovery, compatibility, and documentation; and
- all skips, deviations, waivers, and unproven claims.

Do not fix code, change ADRs, run QA, merge, push, or touch the parked candidate.

Append one exact-HEAD disposition to:

```text
docs/handovers/v0.4/03-cto-to-quality-architecture-disposition.md
```

Use one disposition: `Ready for Quality & Release`, `Refactor first`, `Re-scope`, or
`Stop`. If cleared, include the full adversarial QA matrix and exact evidence identities.

## Activation block — Chief of Staff completes before handoff

```text
review_worktree: <ABSOLUTE_DETACHED_WORKTREE>
engineering_branch: feature/v0.4-project-resume
immutable_base: 3253b052a3986e7d2c94124fbac86c03980e0765
authorized_start: faba0f90f5b4c016e9323cab92f205d5e987067e
candidate_sha: <FULL_40_CHARACTER_SHA>
engineering_handoff_commit: <FULL_40_CHARACTER_SHA>
engineering_handoff_path: docs/handovers/v0.4/02-principal-engineer-to-cto-engineering-review.md
required_output: docs/handovers/v0.4/03-cto-to-quality-architecture-disposition.md
```

Do not start if any field remains unresolved.

## Mandatory startup checks

1. Confirm detached `HEAD` equals `candidate_sha` and the review worktree is clean.
2. Confirm the candidate descends from the immutable base and authorized start.
3. Confirm neither parked tip `4b09050b76fd9a448af3ce91b4aa66963d23dad2`
   nor any candidate-only conversation change was merged or copied.
4. Confirm the engineering handoff is committed and binds its evidence to this exact SHA.
5. Inventory the entire base-to-candidate diff, commits, generated files, ignored release
   evidence, and changes outside the affected-file forecast.
6. Confirm the source worktree remains untouched; conduct review from the frozen copy.

## Required conformance record

For every A1–A12 item and ADR-0018–0021 decision, record:

| Field | Required content |
|---|---|
| Requirement | Exact acceptance/ADR clause |
| Implementation | File, contract, and behavior |
| Evidence | Test, fixture, benchmark, inventory, or manual record |
| Result | Pass, fail, partial, unavailable, or not yet due |
| Risk | Concrete defect, accepted residual risk, or none |

Independently sample executable evidence. Recompute retained benchmark statistics and
digests from raw data. Inspect the implementation rather than accepting handoff summaries.
Separate technical candidate completion from A11's eight-week strategic validation.

## Escalation and output rules

Any material architecture defect, trust-boundary weakening, missing current-source proof,
over-budget serializer, unconfined Git capability, private-evidence leak, or excluded
scope is blocking. State the smallest bounded correction without implementing it.

The disposition must pin base, candidate, evidence commits/digests, reviewed worktree,
commands, skips, deviations, residual risks, and affected QA scope. `Ready for Quality &
Release` must contain a complete adversarial QA matrix and authorize only the exact SHA.
Stop immediately after committing the disposition artifact locally. Do not push.
