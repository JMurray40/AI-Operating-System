# ADR-0018: Project Resume Uses Exact, Tiered Project Identity

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-07-27 |
| Deciders | Chief Architect / CTO, under Product Owner v0.4 authorization |
| Related | ADR-0015, ADR-0017, v0.4 Project Resume Acceptance Tests A1–A3 |

## Context

Project Resume must select one project without allowing fuzzy retrieval, aliases, titles,
paths, or excluded notes to silently choose the wrong identity. Titles and aliases may
collide. Paths may change. Explicit IDs may be malformed or duplicated. Selection itself
is an authorization and disclosure boundary, not a relevance-ranking problem.

## Decision

Project selection operates only over the request-scoped authorized view after sensitivity
and workspace policy have been applied. Only notes with `type=project` participate.

The resolver compares one normalized selector through these tiers, in order:

1. exact workspace-scoped canonical `source_id`;
2. exact title;
3. exact alias;
4. exact filename stem, explicitly labeled as weaker path-derived identity.

Normalization is limited to Unicode normalization already accepted by the query tokenizer,
surrounding-whitespace trimming, and accepted case folding. The resolver does not perform
fuzzy, prefix, substring, stemming, semantic, graph, or relative-relevance matching.

The first tier containing matches controls the outcome:

- one match: `selected`;
- more than one match: `ambiguous`;
- no match at any tier: `not_found`;
- duplicate explicit canonical IDs or malformed identity state: `invalid`, fail closed.

An exact canonical-ID match therefore outranks a title/alias/stem collision at a weaker
tier. Ambiguity at the controlling tier is never broken by path order, relevance, recency,
graph proximity, or other heuristics.

Safe ambiguous candidates contain only already-authorized canonical ID (when available),
display title, current relative path, and identity tier. They are sorted by canonical
source identity and relative path. They contain no excerpts, relationship details,
restricted counts, ranking explanations, conflicts, or trace data.

Excluded projects cannot influence the outcome, candidate list, error wording, trace, or
timing diagnostics except through ADR-0015-permitted safe aggregates.

## Consequences

- Project Resume cannot use `QueryEngine.search()` to choose a project.
- The v0.3.1 authorized-view and stable-source-identity contracts are reused.
- Existing path-derived fallback IDs remain readable but visibly weaker.
- A rename of a fallback-identified project may appear as an identity change.
- Users must disambiguate equal-tier collisions explicitly.
- Negative and non-disclosure tests are required for every tier.

## Alternatives rejected

- Use the top retrieval result: rejected because relevance is not identity certainty.
- Prefer the newest or closest graph node: rejected because it silently guesses.
- Return every known project on not-found: rejected because it can disclose unrelated
  authorized context and encourages substitution.
- Match before authorization: rejected because excluded identities could influence
  selection and ambiguity.
