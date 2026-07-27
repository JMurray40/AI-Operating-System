# AI Operating System Product and Platform Review

| Field | Value |
|---|---|
| Purpose | Evaluate the concept, market, failure modes, and path from application to platform |
| Status | Draft review |
| Version | 1.0.0 |
| Owner | Chief Product Officer |
| Revised | 2026-07-27 |

## What is unique

None of the individual ingredients—Markdown, AI chat, agents, search, dashboards, MCP, or Obsidian—is unique. The differentiated product is their governance:

- canonical knowledge stays human-owned and provider-independent;
- context is assembled around resumable projects, not only conversations;
- source authority and provenance are explicit;
- all models and tools cross a common permission boundary;
- useful session outcomes are promoted into durable knowledge through review;
- the system is intended to remain useful if any component disappears.

The defensible advantage is a trusted longitudinal context and action layer, not a “Jarvis” personality or cinematic interface.

## Where it could fail

1. **Administration exceeds value.** Metadata, approvals, and dashboards become chores.
2. **Retrieval feels clever but unreliable.** False connections erode trust faster than missing results.
3. **Scope overwhelms execution.** Chat, agents, mobile, voice, plugins, and enterprise features compete before one workflow is indispensable.
4. **Local-first becomes support-heavy.** Installation, indexing, backups, and updates overwhelm nontechnical users.
5. **Authority becomes ambiguous.** Generated copies drift across vault, repo, and cloud tools.
6. **Security arrives late.** One overprivileged plugin or injected document compromises the system.
7. **Provider neutrality collapses.** The product either targets the lowest common denominator or leaks provider-specific behavior everywhere.
8. **The vault becomes an AI dumping ground.** Low-value summaries obscure high-value knowledge.

The antidote is ruthless outcome measurement: does Project Resume save time, does search retrieve trusted evidence, and do approved writes improve the vault?

## Target users

| Segment | Need | Fit |
|---|---|---|
| Multi-project individual | Continuity across AI tools and projects | Immediate primary |
| Consultant/accountant | Traceable context, client separation, repeatable workflows | Strong after security controls |
| Developer/creator | Repository context plus durable decisions and research | Strong |
| Small team | Shared context and governed automation | Later |
| Enterprise | Policy-controlled agents over heterogeneous systems | Platform stage |
| Casual note taker | Simple capture/search | Poor fit; product may be too complex |

## Missing capabilities

- identity, device trust, and workspace isolation;
- visible context selection and redaction;
- durable operational workflow/event store;
- source synchronization and conflict handling;
- evaluations for retrieval, agent behavior, and permissions;
- plugin/MCP capability mediation;
- lifecycle management for knowledge freshness and supersession;
- supportability: diagnostics, backup restore, update rollback;
- accessibility and nontechnical onboarding;
- data export, deletion, legal hold, and retention controls for teams.

## Individual use

An individual begins with one local vault, project dashboards, read-only search, chat, and Project Resume. The system proposes summaries and decisions, then later runs narrow approved workflows. Value is measured in reduced reorientation and recovered prior knowledge.

## Enterprise use

An enterprise deployment is not “the personal app with SSO.” It needs a separate control plane:

- tenant and workspace isolation;
- identity federation and service accounts;
- centrally managed policies and plugin allowlists;
- data residency and customer-managed keys;
- DLP, eDiscovery, retention, legal hold, audit export;
- approved provider/model catalog;
- workload isolation and budget controls;
- integration ownership and incident response.

Enterprise agents operate on explicit organizational roles and case/work-item context, not personal vault assumptions.

## Becoming a platform

The system becomes a platform when third parties can create value without modifying core and without weakening trust. Required platform primitives:

1. versioned artifact, task, event, context, provider, tool, and audit schemas;
2. capability-based plugin SDK and MCP gateway;
3. stable application API used by every first-party client;
4. evaluation and compatibility suites;
5. packaging, signing, revocation, and marketplace governance;
6. policy administration and usage metering;
7. clear extension boundaries: UI panels, data sources, tools, workflows, agents, renderers.

Do not call it a platform merely because it loads Python modules.

## Recommended product focus

The next indispensable loop should be:

> Search or resume → inspect sources → work with one AI → approve durable outcome → return later and resume faster.

Everything else should prove that loop rather than compete with it.

## Revision history

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-07-27 | Initial concept and platform review |
