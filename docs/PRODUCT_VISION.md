# Product Vision

| Field | Value |
|---|---|
| Purpose | Define the product's intended value and boundaries |
| Status | Active |
| Version | 0.2.0 |
| Owner | Jason |
| Revised | 2026-07-27 |
| Related | [Product Strategy](product/PRODUCT_STRATEGY.md), [The BRAIN v2](THE_BRAIN_V2_SPEC.md), [Architecture](SYSTEM_ARCHITECTURE.md), [Version Roadmap](product/VERSION_ROADMAP.md) |

## Mission

Help people turn fragmented digital activity into durable, trustworthy knowledge and safe, resumable action—without surrendering ownership to an application or AI provider.

## Vision

Create a personal AI operating system that helps Jason begin, conduct, and preserve meaningful work across projects without surrendering ownership of knowledge to a model or application.

The product is an enduring system rather than a finished chatbot. Its interfaces and providers will change; its human-owned knowledge and design principles should remain stable.

## Design philosophy

- **Local-first:** essential knowledge remains readable and useful on Jason's computer.
- **Provider-independent:** models are selected by role and may be replaced.
- **Knowledge-centered:** AI work produces durable outcomes, not transcript accumulation.
- **Permission-aware:** consequential actions are visible, scoped, and approved.
- **Incremental:** each milestone must deliver usable value.
- **Composable:** integrations use explicit contracts rather than hidden coupling.

## User experience goals

The system should make five experiences exceptionally good:

1. **Resume:** “Where did I leave off?” produces an accurate project briefing.
2. **Ask:** questions use the right project, decision, and resource context.
3. **Work:** the best available model and approved tools support the task.
4. **Capture:** a meaningful session becomes a concise summary and linked decisions.
5. **Connect:** the system surfaces relevant overlap, conflict, and reusable knowledge.

## What success looks like

- The system saves at least 30 minutes on a typical project-switching day.
- Jason relies on project dashboards and session summaries to resume work.
- Knowledge remains coherent across several AI providers.
- External assets are easy to locate without unnecessary duplication.
- An unavailable model or index does not make the vault unusable.
- Every automated write is attributable and recoverable.

## Minimum viable product

The MVP is a **read-only Daily Brain**, not a voice assistant:

- search approved Obsidian notes;
- browse active projects;
- assemble a project resume;
- show recent sessions and decisions;
- link to approved GitHub repositories and local resources;
- maintain conversation history outside the vault; and
- perform no autonomous structural edits.

## Future milestones

After the read-only MVP proves useful:

- controlled note and session capture;
- relationship and contradiction discovery;
- provider routing;
- approved workflows and schedules;
- desktop and mobile interfaces;
- voice;
- home and business automation.

## Explicit non-goals

- A cinematic dashboard without useful capabilities.
- Unrestricted computer control.
- A large multi-agent hierarchy before core workflows work.
- Replacing Obsidian, GitHub, cloud storage, or calendars as their domains' sources of truth.
- Capturing every possible datum.

## Revision history

| Version | Date | Change |
|---|---|---|
| 0.2.0 | 2026-07-27 | Added mission and delegated measurable strategy to the Product Strategy |
| 0.1.0 | 2026-07-27 | Initial product vision |
