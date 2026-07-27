# ADR-0004: Project Dashboards Are the Primary Navigation Layer

| Field | Value |
|---|---|
| Status | Proposed |
| Version | 0.1.0 |
| Owner | Jason |
| Date | 2026-07-27 |
| Related | [The BRAIN v2](../THE_BRAIN_V2_SPEC.md), [Product Vision](../PRODUCT_VISION.md), [Roadmap](../ROADMAP.md) |

## Context

The knowledge system must provide a reliable way to begin real work. Folders, tags, backlinks, search results, and graph views are useful retrieval mechanisms, but they do not naturally assemble the operational context required to resume a project.

When Jason begins work, the intent is usually project-oriented:

- “I want to work on FileOrbit.”
- “I want to work on Murray & Associates.”
- “Where did I leave off with the AI Operating System?”

Answering these questions requires more than locating a folder. The system must assemble purpose, status, current milestone, recent sessions, decisions, resources, open questions, relationships, and the best next action.

## Decision

Each active project will have one canonical project dashboard that serves as its primary human and AI navigation layer.

The dashboard will:

- identify the project's purpose and success criteria;
- show its current state and milestone;
- include a prominent **Resume here** section;
- list current priorities, next actions, questions, and blockers;
- link decisions, sessions, knowledge, people, organizations, and resources;
- link related projects and shared capabilities; and
- point to authoritative external assets without duplicating them.

Folders, tags, backlinks, search, and future graph views remain supporting navigation tools. They do not replace the canonical project dashboard.

## Alternatives

### Folder-first navigation

Rejected as the primary model. Folders answer where a note is stored but do not assemble cross-folder project context or external resources.

### Tag-first navigation

Rejected as the primary model. Tags are useful for filtering but become inconsistent easily and do not express project state or relationship meaning.

### Backlink or graph-first navigation

Rejected as the primary model. These views reveal connections but do not distinguish current priorities, authoritative resources, or next actions.

### Search-first navigation

Retained as a supporting capability. Search helps locate information but requires the user or AI to reconstruct the project state for every work session.

### AI-generated briefing without a canonical dashboard

Rejected. A generated briefing needs a stable, human-editable project source and must not rely on provider memory or opaque inference.

## Consequences

### Positive

- Projects become resumable from one stable note.
- Humans and AI clients share the same entry point.
- Current state is separated from scattered historical evidence.
- External resources remain discoverable without being copied.
- Project relationships become visible and reviewable.
- Future Jarvis “Resume Project” behavior has a clear data contract.

### Negative

- Dashboards require deliberate maintenance.
- Stale Resume sections could mislead users or AI clients.
- The dashboard schema may feel burdensome if every field is mandatory.
- Projects must have stable identities and naming conventions.

### Mitigations

- Keep required fields minimal.
- Update Resume here after meaningful sessions.
- Measure dashboard usefulness during a two-project pilot.
- Remove fields that create maintenance burden without retrieval value.
- Preserve session summaries and decisions as evidence rather than copying their full content into dashboards.

## Implementation notes

The first pilot will compare:

- **AI Operating System:** a greenfield dashboard; and
- **Cloud Organizer Pro:** migration of an existing project note.

Broader project-dashboard adoption requires successful pilot validation and separate approval.

## Revision history

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-07-27 | Initial proposal |
