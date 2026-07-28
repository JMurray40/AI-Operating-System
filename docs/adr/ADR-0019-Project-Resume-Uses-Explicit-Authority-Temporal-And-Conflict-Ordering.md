# ADR-0019: Project Resume Uses Explicit Authority, Temporal, Supersession, and Conflict Ordering

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-07-27 |
| Deciders | Chief Architect / CTO, under Product Owner v0.4 authorization |
| Related | ADR-0014, ADR-0015, ADR-0016, v0.4 Acceptance Test A4 |

## Context

Retrieval relevance cannot decide which statement is authoritative or current. A new draft
does not override an accepted decision. An old session summary may conflict with current
project state. Fluent synthesis that silently resolves these cases would hide material
uncertainty and weaken user trust.

## Decision

Every Project Resume claim carries a typed authority class, temporal state, and support
state. The accepted authority order for the same subject is:

1. explicitly accepted decision or explicitly authoritative project-state passage;
2. current canonical project dashboard/current-state passage;
3. explicit current priority, task, milestone, or next-action passage/metadata;
4. completed session summary;
5. draft or proposed discussion;
6. inferred relationship or weak fallback evidence.

Within the same authority class, order by:

1. effective date descending;
2. source `updated` date descending;
3. stable source identity ascending;
4. passage locator ascending.

Undated evidence sorts after dated evidence in the same class and is labeled `undated`.
Retrieval relevance may order discovery within a channel but cannot change authority or
temporal precedence.

Supersession exists only when current authorized evidence explicitly establishes it:

- a validated `supersedes` relationship to a stable source identity; or
- an explicit supersession statement whose supporting passage and target both validate.

Date, title similarity, shared tags, or later retrieval rank do not establish
supersession.

When materially different claims remain supported and neither validly supersedes the
other:

- retain both;
- mark both `conflicting`;
- expose the conflict and evidence;
- do not manufacture a merged answer; and
- reduce answer-level coverage/assurance accordingly.

Staleness is determined from explicit source dates, a request-supplied deterministic
evaluation time, and configured thresholds. The wall clock is not an implicit semantic
input.

Excluded evidence cannot create, resolve, order, or appear in a conflict.

## Consequences

- Authority, recency, relevance, and confidence remain separate concepts.
- Accepted decisions outrank newer drafts.
- Current project state outranks older session summaries.
- Explicit supersession is inspectable and citation-bound.
- Missing dates and unresolved conflicts remain visible.
- Determinism tests must fix the evaluation time and source snapshot.

## Alternatives rejected

- Newest statement wins: rejected because draft recency is not authority.
- Highest relevance wins: rejected by ADR-0014.
- Let a provider reconcile conflicts: rejected because v0.4 has no real generation and
  because unsupported reconciliation obscures evidence.
- Hide stale/conflicting material: rejected because it creates false completeness.
