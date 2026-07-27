# Changelog

| Field | Value |
|---|---|
| Purpose | Record notable project changes |
| Status | Active |
| Version | 0.1.0 |
| Owner | Jason |
| Revised | 2026-07-27 |
| Related | [Roadmap](docs/ROADMAP.md) |

This project follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and intends to use semantic versioning once application releases begin.

## [Unreleased]

### Added (Phase 2 — Real Vault Pilot, in review)

- Real Obsidian-vault loading from a configurable directory (still strictly read-only).
- Performance instrumentation (`jarvis_core.metrics`): per-stage timings for parse,
  relationship resolution, validation, and total runtime, with throughput.
- Vault health analyzer and `jarvis vault-report` command: missing frontmatter,
  duplicate IDs, orphan notes, broken wikilinks, invalid schemas, missing aliases, and
  circular references, rendered as a human-readable report (file output opt-in).
- Synthetic-vault generators and scale tests at 100/500/1,000 notes plus a
  one-of-each-defect vault; 54 tests total.

### Planned

- Validate the knowledge standard against two pilot projects.
- Define the read-only vault inventory milestone.

### Added

- `SYSTEM_PRINCIPLES.md` as the enduring project-governance philosophy.
- Accepted ADR-0004 establishing project dashboards as the primary navigation layer.
- Accepted ADR-0005 requiring inventory before significant modification.

## [0.1.0] - 2026-07-27

### Added

- Foundational product, architecture, behavior, schema, and roadmap documents.
- The BRAIN v2 master specification.
- Initial Architecture Decision Records.
- Obsidian note templates and machine-readable schema.
- Contribution, issue, pull request, and documentation validation configuration.

## Revision history

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-07-27 | Initial changelog |
