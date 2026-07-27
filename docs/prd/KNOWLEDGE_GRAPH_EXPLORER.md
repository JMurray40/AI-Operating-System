# PRD: Knowledge Graph Explorer

| Field | Value |
|---|---|
| Status | Draft |
| Target | v0.6 |
| Owner | Product/Knowledge |
| Depends on | Stable IDs, relationship index, search, provenance |

## Problem statement

Obsidian graph views become visually noisy and do not explain why relationships matter. Users need an evidence-based explorer that helps answer questions and discover overlap without presenting inferred edges as facts.

## Goals

- Explore explicit and inferred relationships at useful scopes.
- Explain edge type, direction, source, confidence, and freshness.
- Turn discoveries into reviewable relationship or knowledge proposals.
- Remain usable from hundreds to millions of nodes.

## User stories

- Explore one project and its decisions, sessions, concepts, people, and resources.
- Compare two projects and see shared concepts and evidence.
- Filter to explicit links, metadata edges, or inferred candidates.
- Trace a decision to the sessions and sources that produced it.
- Reject a false inferred relationship and improve future ranking.

## Functional requirements

1. Support ego graph, path, comparison, timeline, and tabular views.
2. Filter by type, project, date, source, sensitivity, edge origin, and confidence.
3. Every node resolves to a canonical source; every edge exposes evidence.
4. Visually distinguish explicit, metadata-derived, extracted, semantic, and contradictory edges.
5. Apply node/edge budgets and clustering; never attempt to render the full corpus.
6. Search within the graph and pivot to a selected node.
7. Save a view as operational configuration, not canonical knowledge.
8. Propose link creation/merge/supersession through Memory approval.
9. Record user rejection/acceptance of inferred candidates.

## Non-functional requirements

- Common project ego graph renders under 2 seconds.
- Accessible table/list equivalent exists for every visualization.
- Graph queries enforce sensitivity before traversal.
- Layout changes never imply semantic change.
- Deterministic query results for a fixed index; visual layout may vary.

## Architecture considerations

Use graph projections derived from stable source identities; do not introduce a canonical graph database. Query through a bounded graph service with path length and result limits. Keep inference model/version on every inferred edge.

## Edge cases

Alias collisions; cycles; hubs with thousands of edges; deleted nodes; mixed sensitivity along a path; inferred contradiction based on outdated text; same entity in multiple workspaces.

## Acceptance criteria

- Explicit edge provenance matches source content.
- Inferred edges are never displayed as confirmed.
- Permission tests prevent existence leakage through counts or paths.
- Large-hub test applies clustering/budgets without freezing.
- Comparison view identifies benchmark shared concepts with agreed precision.

## Future enhancements

Temporal graph playback, team ownership overlays, causal hypotheses, graph-based context planning, and external knowledge graph federation.
