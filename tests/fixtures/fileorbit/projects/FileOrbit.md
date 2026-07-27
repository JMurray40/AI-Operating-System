---
id: project-fileorbit
type: project
title: "FileOrbit"
status: active
created: 2026-06-01
updated: 2026-07-25
aliases: ["Cloud Organizer Pro"]
owner:
  - "[[Jason]]"
goal: "Help users clean up cloud and desktop storage safely."
current_milestone: "Local-first duplicate detection prototype"
priority: medium
resources: ["[[FileOrbit Repository]]"]
sensitivity: internal
---

# FileOrbit

## Purpose

An application that helps users clean up cloud and desktop storage, starting with
safe, read-only duplicate detection.

## Current state

- **Status:** Active
- **Current milestone:** Local-first duplicate detection prototype
- **Last meaningful update:** 2026-07-25

## Resume here

Prototype scans a folder and reports duplicate candidates. Next: add a dry-run report
before any file operation is ever proposed.

## Decisions

- [[FileOrbit Is Local First]]

## Recent sessions

- [[FileOrbit Prototype Session]]

## Knowledge and research

- [[File Deduplication]]

## Resources

| Resource | Type | Authority | Location |
|---|---|---|---|
| [[FileOrbit Repository]] | code-repository | GitHub | github.com |

## Open questions and blockers

- What is the safest default action for suspected duplicates?

## Related projects and areas

- [[AI Operating System]]
