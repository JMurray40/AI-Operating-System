# ADR-0017: Stable Source Identity Is Separate from Location

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-07-27 |
| Deciders | Jason |
| Related | ADR-0001, ADR-0002, ADR-0012 |

## Context

Titles, aliases, and paths change. Treating any one of them as permanent identity breaks
citations and relationships during ordinary vault maintenance. Content fingerprints
also change on every edit and therefore represent revision, not identity.

## Decision

Prefer an explicit canonical source ID stored in validated metadata. Scope it to the
workspace and preserve it across title, alias, and path changes. Where no canonical ID
exists, use a documented workspace-and-path-derived fallback and clearly label its weaker
stability.

Keep these concepts distinct:

- `source_id`: logical identity;
- `source_fingerprint`: exact source revision;
- `relpath`: current human-navigable location;
- aliases/title: discovery and display attributes.

Duplicate explicit IDs are validation failures and must not be silently merged.

## Consequences

- Existing notes remain readable through a compatibility fallback.
- Migration to explicit IDs can be proposed later; v0.3.1 remains read-only and cannot
  write IDs into notes.
- Renames with fallback IDs appear as identity changes until an approved migration exists.
- Relationship and citation contracts can distinguish a moved source from an edited one.

## Alternatives rejected

- Path as permanent identity: rejected because moves are normal.
- Content hash as identity: rejected because edits would create new logical entities.
- Title as identity: rejected because titles collide and change.
