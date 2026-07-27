# Fixture Design

Fixtures are **synthetic** and sanitized. No private vault content is copied
(ADR-0005 / safety constraints). They live under `tests/fixtures/`.

## `ai-operating-system/`
A clean, valid pilot vault: one project dashboard (`type: project`) plus linked
decisions, a session summary, a resource, a concept, and an area. Every non-project note
references the project via `projects:` frontmatter and the dashboard links back out, so
the loader and resolver are exercised from both directions.

## `fileorbit/`
The second pilot project (the greenfield rename of "Cloud Organizer Pro"). Same shape as
above, used to prove multi-project loading and alias resolution (`aliases: ["Cloud
Organizer Pro"]`).

## `edge-cases/`
Deliberately messy, to exercise resilience. Includes:
- a note with **no frontmatter**;
- an **unresolved wikilink**;
- a **malformed YAML** file (reported as a syntax error, not a crash);
- an **orphan** note (no links in or out);
- an **embed** (`![[...]]`) of a note and an image;
- **conflicting aliases** (two notes claim "Shared Alias"; first-by-path wins);
- a **valid project dashboard**.

## Conventions
- Frontmatter follows the common contract: `id`, `type`, `title`, `status`, `created`,
  `updated`, `sensitivity`, plus type-specific fields from `VAULT_SCHEMA.md`.
- `sensitivity: internal` on synthetic notes (never real private data).
- IDs use lowercase type prefixes matching `^[a-z0-9][a-z0-9-]*$`.
