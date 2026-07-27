# Naming and Taxonomy

| Field | Value |
|---|---|
| Purpose | Define stable vocabulary, identifiers, filenames, aliases, and classification rules |
| Status | Draft |
| Version | 0.1.0 |
| Owner | Jason |
| Revised | 2026-07-27 |
| Related | [Knowledge Standard](KNOWLEDGE_STANDARD.md), [Vault Schema](VAULT_SCHEMA.md), [The BRAIN v2](THE_BRAIN_V2_SPEC.md) |

## Taxonomy

| Type | Definition | Lifecycle | Example |
|---|---|---|---|
| Project | Outcome-oriented work with a goal or milestone | Active → completed/paused/archived | AI Operating System |
| Area | Ongoing responsibility without a defined end | Active → inactive/archived | Personal Finance |
| Concept | Reusable idea or domain knowledge | Draft → reviewed → superseded/archived | Semantic Search |
| Research | Evidence and analysis answering a question | Draft → reviewed/archived | Embedding Model Comparison |
| Resource | Descriptive pointer to an external asset or system | Active → unavailable/archived | Cloud Organizer Pro Repository |
| Decision | Durable choice with context and consequences | Proposed → accepted → superseded/rejected | Use Project Dashboards |
| Session | Structured outcome of a meaningful work session | Completed; amend only for correction | Knowledge Pilot |
| Person | Context about an individual | Active → inactive/archived | Jason |
| Organization | Context about a company or group | Active → inactive/archived | Murray & Associates |
| Meeting | Record of an interaction with outcomes | Scheduled → completed/cancelled | Architecture Review |
| Daily note | Date-bound capture and audit trail | Open → reviewed | 2026-07-27 |
| Template | Reusable note structure | Draft → active → deprecated | Project Dashboard |
| Attachment | Supporting binary owned by or referenced from the vault | Active → archived | Diagram PNG |
| Archive | Lifecycle state/location, not a semantic note type | Archived | Completed project |

Classification asks what a note **is**, not where it currently lives. A note has one canonical `type` and may relate to many projects, areas, topics, people, and resources.

## Controlled values

Use lowercase kebab-case for machine values:

```yaml
type: session-summary
status: active
topics:
  - semantic-search
  - knowledge-management
sensitivity: private
```

Do not create spelling or capitalization variants when an equivalent term exists.

## Display names and filenames

- Use Title Case for named entities and human-facing note titles.
- Use natural singular names for a single entity: `Decision`, `Project`, `Person`.
- Folder collections may be plural: `Projects`, `Sessions`, `Templates`.
- Use `YYYY-MM-DD` for dates.
- Avoid redundant extensions such as `.md.md`.
- Avoid encoding the folder or type in filenames when YAML and location already provide it.
- Project dashboard filename: `<Canonical Project Name>.md`.
- Session filename: `YYYY-MM-DD-<provider>-<project-or-subject>-<short-purpose>.md`.
- Decision filename: `YYYY-MM-DD-<decision-title>.md` unless a stable ADR identifier applies.
- Attachments: `YYYY-MM-DD-<subject>-<descriptor>.<ext>` when date adds retrieval value.

Existing unconventional names may remain during the pilot; rename only through an approved migration operation with link validation.

## Identifiers

IDs are stable, lowercase, and independent of filenames:

```yaml
id: project-ai-operating-system
id: decision-2026-07-27-project-dashboard-navigation
id: session-2026-07-27-codex-knowledge-pilot
```

Once assigned, an ID does not change when a title or filename changes. Globally unique identifiers may be introduced when synchronization requires them; human-readable IDs are sufficient for the initial vault.

## Aliases

Aliases represent confirmed alternate names, previous names, abbreviations, or product names:

```yaml
title: Cloud Organizer Pro
aliases:
  - FileOrbit
```

Do not use aliases to combine uncertain or merely related concepts. Record uncertainty as a relationship candidate for review.

## Relationship fields

| Field | Contains |
|---|---|
| `projects` | Canonical project references |
| `areas` | Ongoing responsibility references |
| `topics` | Controlled concept terms |
| `people` | Canonical person references |
| `organizations` | Canonical organization references |
| `resources` | Typed external references |
| `related` | Meaningful note relationships not captured above |

Use links only when the target note exists or is created in the same approved batch. Until then, use a plain controlled label to avoid broken links.

## Dashboard naming

The canonical project note is the dashboard; do not create both `Project Name.md` and `Project Name Dashboard.md`. Its H1 equals the canonical project name and it contains a `Resume here` section.

## Archive rules

- Archive is a state first and a folder second.
- Preserve original IDs and aliases.
- Do not add `Archived` to filenames unless needed to avoid ambiguity.
- Superseded decisions link to their replacement.
- Archived projects remain discoverable but leave active navigation.

## Naming review checklist

- [ ] One canonical term exists.
- [ ] The type describes meaning rather than location.
- [ ] The filename is readable and stable.
- [ ] The ID is unique and immutable.
- [ ] Aliases are confirmed.
- [ ] Controlled values use lowercase kebab-case.
- [ ] Links resolve.
- [ ] The name does not create a duplicate master.

## Revision history

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-07-27 | Initial taxonomy and naming rules |
