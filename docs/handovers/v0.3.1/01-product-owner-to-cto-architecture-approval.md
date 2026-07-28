# Handoff 01 — Product Owner to CTO

| Field | Value |
|---|---|
| Sender | Jason Murray, Product Owner |
| Receiver | Chief Architect / CTO |
| Milestone | v0.3.1 — Query Trust Contracts |
| Date | 2026-07-27 |
| Status | Approved; ready for CTO action |
| Decision source | Explicit Product Owner approval in the Chief of Staff task |
| Required output | `docs/handovers/v0.3.1/02-cto-to-principal-engineer-implementation-brief.md` |

## Approved decisions

The Product Owner approved all four decisions presented by the Chief of Staff:

1. Authorize v0.3.1 implementation under the Query Trust Contracts requirements.
2. Accept ADR-0014 through ADR-0017.
3. Establish Project Resume as v0.4 and accept its acceptance tests.
4. Move visible-context conversation to v0.5; keep the existing conversation candidate
   parked and unmerged.

## Accepted artifacts

- [v0.3.1 Query Trust Contracts Requirements](../../software/V0.3.1_QUERY_TRUST_CONTRACTS_REQUIREMENTS.md)
- [ADR-0014](../../adr/ADR-0014-Retrieval-Relevance-Is-Separate-From-Answer-Confidence.md)
- [ADR-0015](../../adr/ADR-0015-Authorization-Precedes-Retrieval-And-Graph-Expansion.md)
- [ADR-0016](../../adr/ADR-0016-Citations-Bind-Passages-To-Source-Revisions.md)
- [ADR-0017](../../adr/ADR-0017-Stable-Source-Identity-Is-Separate-From-Location.md)
- [v0.4 Project Resume Acceptance Tests](../../product/V0.4_PROJECT_RESUME_ACCEPTANCE_TESTS.md)

## Required CTO action

Produce the complete, pinned implementation brief at:

```text
docs/handovers/v0.3.1/02-cto-to-principal-engineer-implementation-brief.md
```

The brief must satisfy the Implementation Brief Contract in
[Ways of Working](../../WAYS_OF_WORKING.md), including the correct engineering base branch
and exact commit SHA. It must direct the Principal Engineer to return evidence at:

```text
docs/handovers/v0.3.1/03-principal-engineer-to-cto-engineering-review.md
```

The CTO must not import chat, streaming, or other v0.5 scope into v0.3.1.

## Exit statement

**Approved and ready for CTO action.** Principal Engineer implementation remains blocked
until the CTO brief is produced and validated by the Chief of Staff.
