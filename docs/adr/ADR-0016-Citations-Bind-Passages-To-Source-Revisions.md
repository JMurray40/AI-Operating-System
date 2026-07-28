# ADR-0016: Citations Bind Supporting Passages to Source Revisions

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-07-27 |
| Deciders | Jason |
| Related | ADR-0012, AI Behavior Standard |

## Context

A note title and path identify a document but do not prove which passage supports a
claim or whether the source changed after retrieval. Generated and synthesized answers
need evidence that a user and validator can inspect precisely.

## Decision

A material-answer citation binds a stable source identity to:

- the exact source fingerprint parsed;
- a deterministic passage locator;
- a bounded supporting excerpt;
- human-readable path and title;
- retrieval relevance and reason where applicable.

The locator must resolve against the cited fingerprint, and the excerpt must match the
resolved passage. Stale or unresolvable citations fail validation. Entity identity is
separate from source revision: a source may retain its identity while its fingerprint
changes.

## Consequences

- Parsers must retain sufficient line/heading provenance.
- Result and trace contracts become versioned.
- Source changes invalidate old passage validation instead of silently retargeting it.
- Excerpts inherit source sensitivity and authorization constraints.

## Alternatives rejected

- Note-level citations only: rejected because they cannot demonstrate claim support.
- Excerpt without revision: rejected because identical text may move or the source may
  change materially.
- Line number only: rejected because line numbers are fragile without a bound revision.
