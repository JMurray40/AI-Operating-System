# Deferred Decisions

Recorded per the build decision rules (record meaningful assumptions; flag material
architecture choices for review).

1. **Language floor (ADR-0006, Proposed).** Code targets Python `>=3.10` because the
   build sandbox runs 3.10.12, while the instruction requested 3.12+. Confirm the
   supported floor when accepting ADR-0006.
2. **Full JSON-Schema validation.** The validator implements the five stages
   pragmatically. Whether to validate strictly against `schemas/note.schema.json`
   (and fail vs. warn on unknown fields during the draft phase) is deferred.
3. **Context package schema ownership.** `ContextPackage` uses an internal
   `context-package/0.1.0` version. Whether this becomes a published schema under
   `schemas/` is deferred.
4. **Dashboard as a distinct type vs. a `project` note.** ADR-0004 treats the dashboard
   as the project's canonical note; this prototype follows that (dashboard == `type:
   project`). If a dedicated dashboard type is later introduced, the loader's project
   lookup changes in one place.
5. **Resource authority vocabulary.** `source_of_truth` values (e.g. `external`) are
   accepted as free strings; a controlled vocabulary is deferred.
6. **Provider role catalog.** Role aliases (`coding`, `research`, `fast`, `private`,
   `vision`) are accepted as strings; formalizing them is deferred to the real provider
   work.

7. **Incremental / cached parsing.** Phase 2 re-parses the whole vault each run. Whether
   to add mtime-based caching or an index is deferred to a later phase.
8. **Health severity policy.** Whether orphans and missing frontmatter should ever be
   errors (vs. warnings) is deferred; current defaults treat only duplicate IDs and
   invalid schemas as errors.
