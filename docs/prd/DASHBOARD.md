# PRD: Dashboard

| Field | Value |
|---|---|
| Status | Draft |
| Target | v0.4 |
| Owner | Product |
| Depends on | Application API, project context, search, operational state |

## Problem statement

Folder trees and graph views do not answer the operational question “What should I work on, and where did I stop?” Users need a calm, accurate surface that turns canonical project knowledge and live system state into actionable orientation.

## Goals

- Make project dashboards the primary navigation layer.
- Provide fast, sourced Resume briefings and next actions.
- Compose reusable widgets without making UI configuration canonical knowledge.
- Expose system health, freshness, and approval queues.

## User stories

- Open Jarvis and see active priorities, stale projects, inbox, and system health.
- Open a project and resume from goals, state, decisions, sessions, resources, and repository activity.
- Rearrange widgets without changing vault knowledge.
- Understand stale or missing data rather than seeing fabricated completeness.

## Functional requirements

1. Home dashboard: active projects, today, inbox, approvals, recent sessions, health, and suggestions.
2. Project dashboard: purpose, Resume, milestone, priorities, decisions, sessions, resources, questions, activity, and related concepts.
3. Each datum links to its canonical source and freshness.
4. Widget registry supports versioned type, data contract, size, permissions, refresh policy, empty/error states.
5. Layout and display preferences live in operational settings; project meaning remains in the vault.
6. Provide search, project switcher, keyboard navigation, and responsive layouts.
7. Suggestions are labeled advisory and dismissible.
8. Never interpret missing data as zero or completed.

## Non-functional requirements

- First useful render p95 <1.5 seconds from warm local index.
- Offline mode shows last-known state with timestamp.
- Widgets fail independently.
- WCAG 2.2 AA; usable at 200% zoom.
- No widget can fetch data outside its granted capabilities.

## Architecture considerations

Clients render server-defined data contracts but first-party code owns trusted widget implementations. Do not allow arbitrary remote JavaScript in dashboards. Cache derived views by context/source revision. A project dashboard note is canonical project context; the UI dashboard is a projection, not a competing editable document.

## Edge cases

Project renamed or aliased; duplicate project identity; repository unavailable; very large decision history; stale calendar token; widget schema upgraded; user has no active projects; private widget visible during screen sharing.

## Acceptance criteria

- Two pilot projects resume accurately with all material statements sourced.
- Layout changes do not modify the vault.
- Stale/unavailable connectors are visibly distinguished.
- Widget failure does not block the page.
- Accessibility and keyboard test suite passes.
- Median project reorientation time improves against baseline.

## Future enhancements

Shared team dashboards, mobile layouts, voice briefing, custom signed widgets, temporal comparison, and proactive relationship insights.
