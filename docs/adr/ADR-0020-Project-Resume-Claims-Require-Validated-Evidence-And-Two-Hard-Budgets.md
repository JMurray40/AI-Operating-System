# ADR-0020: Project Resume Claims Require Validated Evidence and Two Hard Budgets

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-07-27 |
| Deciders | Chief Architect / CTO, under Product Owner v0.4 authorization |
| Related | ADR-0014, ADR-0016, v0.4 Acceptance Tests A1, A5, A6, A8 |

## Context

A Project Resume is a multi-section briefing, not a list of search hits. It needs
claim-level evidence, visible incomplete/conflicting coverage, deterministic omissions,
and a hard bound on both selected evidence and emitted output. The v0.3.1 context budget
does not by itself account for Project Resume headings, labels, limitations, citations,
separators, JSON structure, or trace.

## Decision

Project Resume adds versioned `ProjectResumeResult`, `BriefingSection`, `BriefingClaim`,
`EvidenceCitation`, `CoverageSummary`, `Conflict`, `Omission`, and `Limitation` contracts.

Each material claim records:

- stable claim ID derived from semantic inputs;
- section and deterministic position;
- text;
- statement kind: `fact`, `inference`, or `unknown`;
- authority class and temporal state;
- support state: `supported`, `incomplete`, or `conflicting`;
- one or more evidence IDs; and
- no numeric answer confidence.

A material fact is `supported` only when at least one current citation validates immediately
before result emission. Vault citations reuse ADR-0016: stable source identity, exact
source fingerprint, full heading/line locator, bounded matching excerpt, path/title, and
retrieval reason where applicable.

Local Git activity citations use the same trust shape at a different source boundary:
canonical repository identity, exact Git object ID/HEAD snapshot, deterministic record
locator, bounded record excerpt, command-contract version, and snapshot fingerprint.

An inference is visibly labeled and cites every material premise. An unknown is a
limitation, not a negative fact. Stale, missing, deleted, unreadable, escaped, malformed,
or changed evidence cannot support a verified claim. Incomplete references are not
rendered as passage citations.

Answer-level coverage is `complete`, `partial`, `incomplete`, or `none`, with supported,
incomplete, and conflicting counts plus explicit limitations. An incomplete-only result
cannot return fully-evidence-backed success.

Two independent hard budgets apply:

1. **Evidence budget** — every selected passage/record and its evidence wrapper.
2. **Output budget** — the complete serialized text or JSON result, including headings,
   labels, claim text, separators, citations, conflicts, omissions, limitations, coverage,
   and requested trace.

Both use the released deterministic token estimator unless a new estimator is separately
accepted. The serialized form is measured before emission. No first item, wrapper,
citation, trace, or error fallback may exceed its configured budget.

Allocation is deterministic:

1. reserve required structural, coverage, limitation, and citation overhead;
2. reserve minimum capacity for project identity, current state, and evidence coverage;
3. allocate remaining capacity by accepted section priority;
4. order within a section by authority, temporal fit, stable source identity, and locator;
5. stop before the next item would exceed either budget; and
6. record bounded, non-disclosing omissions.

If the mandatory minimum structure cannot fit, return a bounded `budget_error`; do not emit
an over-budget partial structure. Trace uses a declared sub-budget and cannot silently
expand the ordinary result.

For identical source bytes, authorization, connector snapshot, request (including
evaluation time), configuration, and output format, the semantic structured result and
citations are byte-identical. Timings live in a diagnostics field excluded from semantic
byte-identity assertions.

## Consequences

- Project Resume requires its own result contract version.
- v0.3.1 citation/current-source logic should be extracted into a reusable service rather
  than copied.
- Text and JSON renderers must share the same semantic result and coverage rules.
- Budget tests must include every wrapper and exact-boundary case.
- No provider prose or self-rated confidence is needed.

## Alternatives rejected

- Cite only each section: rejected because material claims need inspectable support.
- Count only evidence passages: rejected because emitted wrappers can exceed the budget.
- Truncate rendered strings after construction: rejected because it can sever citations
  and create invalid JSON.
- Treat incomplete references as supported: rejected because it misstates evidence.
