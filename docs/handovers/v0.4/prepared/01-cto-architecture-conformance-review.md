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

