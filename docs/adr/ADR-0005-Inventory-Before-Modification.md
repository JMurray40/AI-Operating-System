# ADR-0005: Inventory Before Modification

| Field | Value |
|---|---|
| Purpose | Require a read-only baseline before significant knowledge-system changes |
| Status | Accepted |
| Version | 1.0.0 |
| Owner | Jason |
| Date | 2026-07-27 |
| Related | [System Principles](../SYSTEM_PRINCIPLES.md), [Implementation Plan](../IMPLEMENTATION_PLAN.md), [The BRAIN v2](../THE_BRAIN_V2_SPEC.md) |

## Context

Knowledge systems become difficult to maintain when structural changes are made without understanding the existing state.

Folder migrations, metadata transformations, link repairs, bulk renames, template installation, and plugin changes can:

- lose or obscure useful content;
- break links and application behavior;
- overwrite newer work;
- remove provenance;
- create duplicate concepts;
- produce changes that cannot be measured; and
- make recovery depend on memory or manual reconstruction.

AI increases both the speed of analysis and the potential scope of a mistaken change. A read-only baseline is therefore required before a significant transformation.

## Decision

Before any significant migration, refactoring, reorganization, or metadata transformation:

1. perform a complete read-only inventory of the approved scope;
2. record a timestamped baseline;
3. identify files, folders, metadata, links, integrations, and application-managed state;
4. classify proposed changes and affected authorities;
5. establish backup and rollback procedures;
6. define validation and completion criteria; and
7. obtain explicit human approval for the exact write scope.

Inventory reports must be stored outside the live source when writing them into that source could affect the baseline or introduce sensitive data into an inappropriate repository.

The inventory does not authorize modification. Analysis, recommendation, approval, and execution remain separate phases.

## Alternatives

### Modify first and rely on version history

Rejected. Version history may not include application settings, derived state, untracked files, external resources, or concurrent changes. It also does not establish intended outcomes.

### Back up without inventory

Rejected as insufficient. A backup provides recovery material but does not explain what exists, what relationships matter, or how success will be measured.

### Inventory only the files expected to change

Rejected for significant transformations. Dependencies such as backlinks, plugin configuration, external resource pointers, and managed folders may exist outside the immediate target.

### Let AI infer the current state during migration

Rejected. Mixing discovery and mutation makes scope drift, review, validation, and rollback harder.

## Consequences

### Positive

- Safer migrations.
- Explicit rollback capability.
- Measurable before-and-after results.
- Better AI planning and smaller change scopes.
- Improved visibility into plugins, integrations, and managed paths.
- Clear separation between observation, recommendation, approval, and execution.

### Negative

- Significant changes require additional preparation.
- Baselines may become stale when active systems continue to change.
- Inventory artifacts may contain sensitive paths or metadata.
- Tools must distinguish read-only analysis from write behavior.

### Mitigations

- Recheck drift immediately before execution.
- Store private baseline reports outside public repositories.
- Keep inventories proportionate to the risk and scope.
- Automate repeatable validation without automating approval.
- Record exclusions and scan errors explicitly.

## Evidence

Phase 1A of The BRAIN migration established a read-only baseline before Phase 1B classification and pilot design. It identified:

- existing plugin and bridge dependencies;
- application-managed folders;
- current note and metadata coverage;
- link and orphan status;
- empty placeholders;
- existing projects and templates; and
- safe boundaries for the pilot.

That baseline materially changed the recommended approach from folder-led migration to classification-led design.

## Revision history

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-07-27 | Accepted initial decision |
