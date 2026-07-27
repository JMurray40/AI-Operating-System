# Demo Vault Specification

| Field | Value |
|---|---|
| Purpose | Define a synthetic, realistic vault demonstrating and testing every major Jarvis capability |
| Status | Specification; fixture content not yet implemented |
| Version | 1.0.0 |
| Owner | Product and Evaluation |
| Revised | 2026-07-27 |
| Related | [Query Benchmark](../../evaluations/QUERY_EVALUATION_BENCHMARK.md), [Vault Schema](../VAULT_SCHEMA.md) |

## Design goals

The demo vault is small enough to understand and rich enough to expose errors. It MUST be synthetic, redistributable, stable across releases, and contain both ideal notes and deliberate defects. It demonstrates value without relying on private data.

## Narrative

Jason runs a small bookkeeping company, develops AI Operating System and FileOrbit, maintains a Murray & Associates website, studies knowledge systems, and experiments with safe home automation. Alex helps with product/software work; Casey reviews bookkeeping; two different people named Taylor create an identity-disambiguation case.

## Structure and representative notes

| Category | Representative notes | Capabilities demonstrated |
|---|---|---|
| Projects | AI Operating System, FileOrbit/Cloud Organizer Pro, Murray Website, Home Energy | Dashboard Resume, aliases, status, resources, cross-project concepts |
| People | Jason, Alex, Casey, Taylor Product, Taylor Vendor, Jordan | Identity, roles, privacy, ambiguous names, temporal changes |
| Meetings | Architecture Review, FileOrbit Planning, Client Onboarding, Plugin Security | Attendees, decisions vs discussion, actions, exact quotes, conflicting dates |
| Research | FTS Benchmark, Hybrid Search, Local Embeddings, Plugin Sandbox, Chunking | Evidence, methods, stale research, conflicting sources, citations |
| Tasks | Query release, benchmark, plugin review, migration plan, client follow-ups | Due/status/owner, dependencies, duplicates, automation risk |
| Bookkeeping | July transactions/reconciliation, journal 1008, invoice 1042, client summaries | Client isolation, calculations, approvals, missing receipts, current-policy caution |
| Books | Thinking in Systems, Designing Data-Intensive Applications | Highlights, concepts, linked decisions, source-versus-personal interpretation |
| Daily Notes | Fixed dates from June–July 2026 | Temporal queries, commitments, focus shifts, retrospective gaps |
| Companies | Murray & Associates, Northwind, Contoso | Organization membership, client boundaries, resource authority |
| Technologies | SQLite FTS, Ollama, MCP, OAuth, XChaCha20, Python | Explanations, ADR provenance, current vs planned capability |
| Concepts | Semantic Search, Metadata Standards, Local-First, Permissions, Feedback Loops | Explicit/inferred edges, shared projects, merge candidates |
| Decisions | Markdown canonical, dashboards, provider abstraction, memory proposals, auth supersession | Accepted/proposed/superseded, conflicts, provenance |
| Resources | GitHub repositories, local folders, websites, camera storage | Typed pointers, source of truth, unavailable links, no duplicated artifacts |

## Required deliberate edge cases

- confirmed alias: FileOrbit = Cloud Organizer Pro;
- two people named Taylor;
- duplicate alias collision on a separate synthetic project;
- proposed SQLite decision beside accepted decisions;
- Firebase decision superseded by Supabase;
- meeting with frontmatter/body date conflict;
- note without attendees and note without due date;
- unresolved and broken resource links;
- two near-duplicate concept notes that should not auto-merge;
- stale research and unavailable citation;
- restricted person/financial/home-presence notes;
- prompt injection text inside a research source and MCP description;
- orphan note, malformed YAML copy, duplicate ID, and circular decision dependency;
- source changed after context snapshot;
- incomplete event interval during a network outage.

## Note requirements

Every normal note has stable `id`, `type`, title, status, created/updated/reviewed, sensitivity, provenance, and relationships appropriate to its type. Every project has Purpose, Current state, Resume here, priorities, next actions, decisions, resources, sessions, and open questions.

Defect notes violate exactly one primary rule when possible so failures are diagnosable.

## Scale layers

1. **Canonical demo:** approximately 120 hand-authored notes mapped to benchmark expectations.
2. **Medium generated mirror:** 10,000 deterministic notes preserving category ratios.
3. **Large scale corpus:** 100,000 and 1,000,000 notes for indexing/performance only.

Generated scale notes never replace hand-authored semantic regression cases.

## Expected relationships

Core explicit path examples:

- Book → Feedback Loops → Review Loops decision.
- Jarvis → Metadata Standards → FileOrbit.
- Jarvis → Permissions → Home Automation.
- Alex → FileOrbit and Murray Website.
- Research Provider Protocol → Provider Abstraction decision.

Inferred edges are stored in expected evaluation data, not canonical note frontmatter.

## Privacy and safety

All names, clients, amounts, credentials, addresses, and device data are fictional. Secrets use obvious nonfunctional markers. The fixture MUST never contain valid tokens or resemble a real client dataset closely enough for confusion.

## Acceptance criteria

- All 260 benchmark cases reference existing note IDs/locators or deliberate missing evidence.
- Schema-valid set passes validation; defect set produces the expected isolated findings.
- Fixed snapshot yields deterministic retrieval and citations.
- No personal vault content or external network is required.
- License and provenance permit public redistribution.

## Revision history

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-07-27 | Initial demonstration and evaluation vault design |
