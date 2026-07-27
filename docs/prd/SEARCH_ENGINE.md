# PRD: Search Engine

| Field | Value |
|---|---|
| Status | Draft |
| Target | v0.2 lexical; v0.6 hybrid |
| Owner | Product/Search |
| Depends on | Parser, source revisions, index projection ADR, benchmark corpus |

## Problem statement

Filesystem scanning and one-hop links work for a small prototype but cannot provide fast, explainable retrieval across millions of notes and external sources. Search must scale without making the index authoritative or leaking sensitive content.

## Goals

- Fast lexical, metadata, relationship, and later semantic retrieval.
- Explainable ranking with exact source locators.
- Incremental, rebuildable, sensitivity-scoped indexes.
- A query contract usable by context building, chat, dashboards, and agents.

## User stories

- Search by phrase, title, type, project, date, source, person, or status.
- Understand why a result matched and preview the relevant section.
- Filter to local/private content or a project.
- Find related concepts while distinguishing direct matches from inferred similarity.
- Rebuild the index without losing knowledge.

## Functional requirements

1. Index notes as documents and heading-bounded sections with path, stable ID, revision hash, metadata, links, and sensitivity.
2. Support exact phrase, token/prefix, field filters, date ranges, exclusions, and deterministic pagination.
3. Return score components, highlighted snippets, source locator, revision, and index freshness.
4. Incrementally add/update/delete projections from content hashes.
5. Detect identity collisions and index errors without dropping the entire corpus.
6. Provide full rebuild, consistency check, statistics, and health commands.
7. In v0.6 add hybrid lexical/vector ranking, feedback, related-note candidates, and contradiction candidate retrieval.
8. Enforce workspace and sensitivity before ranking and again before returning results.
9. Maintain a versioned query/result schema and index-model metadata.

## Non-functional requirements

- v0.2: 100k notes, p95 query <500 ms, incremental update <2 seconds per ordinary note.
- v1.0: 1M notes, p95 <1 second on published reference hardware.
- Deterministic lexical results for a fixed snapshot and configuration.
- Index may be deleted safely and rebuilt.
- Content encryption follows storage threat model; logs never contain raw snippets by default.

## Architecture considerations

Begin with SQLite FTS plus normalized metadata/edge tables. Define `SourceStore`, `IndexWriter`, and `KnowledgeQuery` ports so canonical reads, projection maintenance, and querying are separate. Store vectors behind the same result contract; do not expose vendor vector IDs as domain identity. Use rank fusion rather than replacing lexical search.

## Edge cases

Duplicate IDs; renamed files; alias collisions; malformed YAML; giant notes; binary attachments; unavailable external sources; multilingual text; zero-result queries; stale embeddings; sensitivity changes; path case differences.

## Acceptance criteria

- Golden-query benchmark reports precision@10, recall, latency, and explanation correctness.
- Full rebuild and incremental update yield equivalent logical results.
- Removing a source removes all projections.
- Source content and index can be compared through revision hashes.
- Access-control tests prove filtered documents cannot influence snippets or counts.
- Hybrid mode beats lexical baseline on semantic benchmark without regressing exact lookup materially.

## Future enhancements

OCR/transcription, federated search, learned ranking, temporal decay, personal relevance profiles, query suggestions, cross-language retrieval, and enterprise search connectors.
