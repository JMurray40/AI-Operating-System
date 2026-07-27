# Migration Execution Plan

| Field | Value |
|---|---|
| Purpose | Provide the repeatable runbook for migrating The BRAIN safely |
| Status | Draft — execution prohibited until approved |
| Version | 0.1.0 |
| Owner | Jason |
| Revised | 2026-07-27 |
| Related | [The BRAIN v2](THE_BRAIN_V2_SPEC.md), [Vault Schema](VAULT_SCHEMA.md), [Knowledge Standard](KNOWLEDGE_STANDARD.md), [Naming and Taxonomy](NAMING_AND_TAXONOMY.md), [ADR-0005](adr/ADR-0005-Inventory-Before-Modification.md) |

## Scope and authority

This plan governs structural migration of `C:\Users\jmurr\The BRAIN`. It is a runbook, not authorization. No phase may write to the live vault until its exact operation list, backup, validation plan, and rollback path receive human approval.

The completed Phase 1A inventory is the initial baseline. The AI Operating System and Cloud Organizer Pro dashboards form the accepted pilot; they do not authorize broader migration.

## Migration phases

| Phase | Goal | Expected outputs | Human gate |
|---|---|---|---|
| 0. Baseline | Record the current state read-only | Manifest, inventory, plugin/config snapshot, link and metadata reports | Accept baseline |
| 1. Classification | Decide what each note is | Classification, relationships, metadata recommendations, exceptions | Approve classifications |
| 2. Pilot | Test standards on representative projects | Two dashboards, sessions, index, validation report | Accept or roll back pilot |
| 3. Standards | Finalize taxonomy, schemas, templates, and naming | Approved standards and templates | Approve architecture |
| 4. Project migration | Migrate active projects in small batches | Dashboards, metadata, links, batch log | Approve every batch |
| 5. Shared knowledge | Normalize concepts, resources, people, organizations, and decisions | Canonical notes and redirect/alias map | Approve merges and renames |
| 6. Historical content | Classify sessions, conversations, daily notes, and archives | Summaries, retained evidence, archival index | Approve archive policy |
| 7. Stabilization | Measure integrity and usability | Final inventory, comparison report, unresolved exceptions | Accept migration |

## Pilot and batch sequence

1. AI Operating System — greenfield dashboard and governance workflow.
2. Cloud Organizer Pro / FileOrbit — existing project transformed without losing facts.
3. Murray & Associates Website — project with content and external publishing assets.
4. Survivor Group Tracker — software project with repository documentation.
5. Remaining active projects, one at a time.
6. Areas and shared knowledge only after project navigation is stable.

Each post-pilot batch should contain no more than one complex project or ten low-risk notes.

## Required backups

Before each write batch:

- close Obsidian and any vault watcher capable of writing;
- create a timestamped copy outside the live vault;
- record relative path, size, modification time, and SHA-256 for every file;
- verify backup file count and hashes;
- record Obsidian configuration and enabled plugins;
- retain the previous accepted backup until the new batch is accepted.

A sync service, Git history, or recycle bin may supplement but never replace the verified backup.

## Execution procedure

### 1. Prepare

- Confirm the baseline has not drifted.
- Resolve exact source and destination paths.
- Classify each operation as create, edit, move, rename, merge, archive, or delete.
- Identify affected links, aliases, attachments, templates, dashboards, and external pointers.
- Produce a human-readable operation manifest.

### 2. Review checkpoint

The human reviews:

- before/after previews;
- uncertain classifications;
- merge and deletion candidates;
- canonical-source decisions;
- privacy or cloud-AI exposure;
- rollback instructions.

Silence is not approval.

### 3. Execute

- Stop on any precondition mismatch.
- Apply only listed operations.
- Preserve dates and provenance where meaningful.
- Never modify `.obsidian`, plugin data, secrets, or agent-managed files unless separately authorized.
- Record actual results and hashes.

### 4. Validate

- Parse every changed note and its YAML.
- Resolve internal links and attachment references.
- Confirm each active project has one dashboard.
- Confirm external resources point to the authoritative system.
- Compare all untouched files with the pre-write manifest.
- Reopen Obsidian and visually inspect properties, links, templates, and plugin behavior.

### 5. Accept or roll back

Accept only after automated and manual checks pass. Otherwise close Obsidian, reverse new files and moves, restore modified files from backup, then verify against the pre-write manifest.

## Validation checklist

- [ ] Backup exists outside the vault and hashes match.
- [ ] Obsidian and write-capable watchers were closed during writes.
- [ ] Exact operation list was approved.
- [ ] No operation occurred outside approved scope.
- [ ] YAML parses without duplicate top-level keys.
- [ ] No new unresolved internal links exist without an approved exception.
- [ ] Original facts and provenance were preserved.
- [ ] Canonical ownership is explicit for every external asset.
- [ ] Project dashboards provide a usable **Resume here** path.
- [ ] No secrets or unnecessary raw private content were introduced.
- [ ] Obsidian and enabled plugins behave normally after reopening.
- [ ] Final inventory and execution report were saved outside the vault.

## Success criteria

Migration succeeds when:

- every active project has one reliable dashboard;
- notes conform to an approved type or documented exception;
- metadata and names are consistent enough for deterministic retrieval;
- duplicate editable masters are eliminated or explicitly governed;
- all structural changes are attributable and reversible;
- the final vault has no unexplained missing files or newly broken links;
- the user can resume representative projects faster than before migration.

## Responsibilities

| Actor | Responsibilities |
|---|---|
| AI | Inventory, classify, draft previews, identify relationships and risk, generate operation manifests, validate, and report |
| Human | Decide authority and ambiguity, approve exact writes, review sensitive content, visually validate Obsidian, accept or reject batches |
| Automation | Execute only approved deterministic operations, hash files, log outcomes, and stop on mismatch |

AI must never infer approval for moves, merges, overwrites, archival, deletion, bulk metadata changes, or exposure of private notes to cloud providers.

## Rollback levels

| Level | Trigger | Response |
|---|---|---|
| File | One note is incorrect | Restore that file and remove its newly created counterpart |
| Batch | Links, metadata, or plugin behavior fail | Restore all files touched by the batch |
| Migration | Widespread structural or trust failure | Restore the last accepted full-vault backup |

Rollback never deletes the backup used for recovery.

## Post-migration review

After seven working days, evaluate:

- time required to resume projects;
- missing or excessive metadata;
- navigation friction;
- false relationships and duplicate concepts;
- plugin side effects;
- manual maintenance burden;
- whether the next batch should proceed, change, or stop.

## Revision history

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-07-27 | Initial non-executing migration runbook |
