# Vault Schema

| Field | Value |
|---|---|
| Purpose | Define how The BRAIN v2 schema is implemented and validated |
| Status | Draft |
| Version | 0.1.0 |
| Owner | Jason |
| Revised | 2026-07-27 |
| Related | [The BRAIN v2 §7–8](THE_BRAIN_V2_SPEC.md), [Knowledge Standard](KNOWLEDGE_STANDARD.md), [JSON Schema](../schemas/note.schema.json) |

## Scope

The BRAIN v2 specification defines the complete conceptual schemas and examples. This document deliberately avoids repeating them. It defines implementation requirements shared by templates, validators, and future Jarvis services.

## Common contract

Every durable note requires:

| Property | Type | Constraint |
|---|---|---|
| `id` | string | Unique and stable |
| `type` | enum | Registered note type |
| `title` | string | Non-empty canonical title |
| `status` | enum | Registered lifecycle status |
| `created` | date | ISO date |
| `updated` | date | ISO date, not before `created` |
| `sensitivity` | enum | `public`, `internal`, `private`, or `restricted` |

Relationship fields are arrays even when they contain one item. Empty arrays are allowed. Unknown fields are allowed during the draft phase but should be documented before repeated use.

## Registered types

`project`, `area`, `concept`, `research`, `reference`, `playbook`, `person`, `organization`, `resource`, `decision`, `session-summary`, `prompt`, `daily`, and `meeting`.

## Type-specific minimums

| Type | Additional required properties |
|---|---|
| `project` | `goal`, `priority` |
| `resource` | `resource_type`, `source_of_truth` |
| `decision` | `decision_date` |
| `session-summary` | `session_date`, `provider`, `objective` |
| `daily` | `date` |
| `research` | `question`, `confidence` |
| `meeting` | `meeting_date` |

## Compatibility policy

- Adding an optional field is a minor schema change.
- Adding a required field requires a migration plan.
- Removing or redefining a field is a breaking change.
- Stable IDs are never rewritten merely because a title or path changes.
- Templates and validation schemas must change in the same pull request.

## Resource representation

Simple resources may be linked directly. Reusable or governed resources use a resource note with:

- stable identifier;
- resource type;
- URI or local path;
- source-of-truth designation;
- access classification;
- related projects; and
- verification information.

## Validation stages

1. **Syntax:** valid Markdown and YAML.
2. **Shape:** common and type-specific fields.
3. **Vocabulary:** known types, statuses, and sensitivities.
4. **Integrity:** unique IDs and resolvable links.
5. **Policy:** no secrets and correct external authority.

## Revision history

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-07-27 | Initial schema implementation contract |
