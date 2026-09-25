# ADR-0015: Authorization Precedes Retrieval and Graph Expansion

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-07-27 |
| Deciders | Jason |
| Related | ADR-0007, ADR-0012, Security Threat Model |

## Context

Filtering after retrieval allows excluded sources to influence ranking, graph traversal,
conflict detection, traces, timing, and error messages. Removing them only from final
context is therefore not a sufficient privacy boundary.

## Decision

Every query executes under an immutable, workspace-scoped `AuthorizationScope`.
Authorization and sensitivity filtering occur before request-visible index candidate
generation and before graph expansion. Unknown or incomplete policy fails closed.

Excluded source identities and content may not appear in result objects, citations,
context, traces, conflicts, or user-visible errors. A trace may report only safe aggregate
counts and the policy rule/version used.

## Consequences

- Query entry points require an explicit scope.
- Indexing may use a request-scoped authorized view over a shared projection, but the
  implementation must prove excluded terms cannot influence request-visible behavior.
- Graph adjacency must be filtered before traversal.
- Authorization tests become mandatory for every new retrieval or relationship channel.

## Alternatives rejected

- Filter final context only: rejected because upstream leakage and ranking influence
  remain.
- Trust callers to pass prefiltered notes: rejected because the policy boundary would be
  implicit and inconsistently testable.
- Log excluded identities in Trace Mode: rejected because trace is itself a disclosure
  surface.
