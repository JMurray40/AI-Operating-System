# ADR-0014: Retrieval Relevance Is Separate from Answer Confidence

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-07-27 |
| Deciders | Jason |
| Related | ADR-0012, AI Behavior Standard, v0.3 ARB review |

## Context

The v0.3 ranker normalizes a result's score against the top result and calls the value
`confidence`. Conversation work then presents that ranking value as answer confidence.
The value only describes relative position within one retrieval result set. It does not
measure truth, evidence sufficiency, citation coverage, or model correctness.

## Decision

Use `relative_relevance` for retrieval ranking. It is deterministic, query-local, and
non-probabilistic. It must not be compared across queries or displayed as confidence in
an answer.

Answer confidence is a separate evidence assessment based on authority, directness,
citation coverage, identity certainty, temporal fit, conflict, retrieval completeness,
and validation. v0.3.1 will not emit numeric answer confidence. A later release may emit
the qualitative levels defined by the AI Behavior Standard after calibration evidence
exists.

## Consequences

- Ranking, citation, trace, CLI, and JSON contracts require a pre-1.0 rename.
- Existing numeric values must never be migrated into answer-confidence fields.
- Conversational/generated answers remain blocked until their evidence assessment and
  citation coverage contracts are implemented and evaluated.

## Alternatives rejected

- Keep `confidence` and document it: rejected because user-facing consumers already
  interpret it as correctness.
- Convert normalized rank directly to answer confidence: rejected because ranking alone
  cannot establish claim support.
- Invent a model self-rating: rejected as uncalibrated and provider-dependent.
