# AI Operating System

> A local-first, human-owned foundation for personal knowledge, AI assistance, and safe automation.

| Field | Value |
|---|---|
| Purpose | Orient contributors to the AI Operating System |
| Status | Foundation |
| Version | 0.1.0 |
| Owner | Jason |
| Revised | 2026-07-27 |

## Vision

AI Operating System is the engineering home for a long-term personal AI platform. It connects durable knowledge, interchangeable AI providers, external tools, and future applications without allowing any single model or vendor to own the system.

The architecture follows three clear responsibilities:

> **Obsidian stores knowledge. GitHub stores engineering artifacts. Jarvis orchestrates everything.**

The intended experience is simple: select a project, instantly understand where work stopped, give an approved AI the right context, complete useful work, and preserve the result as durable knowledge.

## Long-term goals

- Make knowledge portable, searchable, and useful across Claude, ChatGPT, Gemini, Ollama, and future models.
- Provide a safe orchestration layer for tools, agents, MCP integrations, and local automation.
- Resume any project from its current goals, decisions, sessions, code activity, and resources.
- Discover useful relationships and contradictions across projects.
- Support desktop, mobile, voice, and home-automation interfaces without coupling knowledge to any interface.
- Remain useful when an AI provider, database, index, or application is unavailable.

## Architecture overview

```mermaid
flowchart TB
    U["User Interfaces<br/>Chat · Dashboard · Obsidian · Voice · Mobile"]
    J["Jarvis Orchestrator<br/>Context · Routing · Tools · Permissions"]
    K["Knowledge Layer<br/>Obsidian Markdown"]
    S["Search Layer<br/>Full text · Links · Semantic index"]
    O["Operational Database<br/>Conversations · Jobs · Costs · Audit"]
    A["AI Providers<br/>Claude · OpenAI · Gemini · Ollama"]
    E["External Systems<br/>GitHub · Files · Cloud · Calendar · Email"]

    U --> J
    J --> K
    J --> S
    J --> O
    J --> A
    J --> E
    S --> K
```

See [System Architecture](docs/SYSTEM_ARCHITECTURE.md) for boundaries and data flows.

## Philosophy

1. The human owns the knowledge.
2. Knowledge has one authoritative home.
3. External assets are referenced, not copied indiscriminately.
4. AI models reason; they do not become permanent memory.
5. Search indexes are derived and rebuildable.
6. Consequential actions require explicit permission.
7. Every meaningful AI session should improve the durable knowledge base.
8. Complexity must be earned through real usage.

## Repository structure

```text
AI-Operating-System/
├── README.md                 Project orientation
├── CONTRIBUTING.md           Contribution and review workflow
├── CHANGELOG.md              Version history
├── docs/                     Product and architecture specifications
│   └── adr/                  Architecture Decision Records
├── prompts/                  Versioned reusable prompts
├── templates/                Canonical Obsidian note templates
├── schemas/                  Machine-readable schema definitions
├── examples/                 Non-sensitive examples and fixtures
├── research/                 Time-bounded engineering investigations
├── meeting-notes/            Project governance records
└── .github/                  GitHub collaboration configuration
```

## Roadmap

The project advances through validated milestones:

1. Foundation
2. Knowledge System
3. Cross-AI Memory
4. Read-only Jarvis
5. Project Resume
6. Relationship Engine
7. Automation
8. Voice and additional interfaces

Each milestone has explicit dependencies and completion criteria in the [Roadmap](docs/ROADMAP.md). No Jarvis application code is included in the foundation release.

## Obsidian and this repository

The Obsidian vault and this repository complement rather than duplicate one another.

| Obsidian vault | GitHub repository |
|---|---|
| Personal and project knowledge | Product and engineering specifications |
| Decisions about ongoing work | Architecture Decision Records for the software |
| AI session summaries | Prompts, templates, schemas, and implementation plans |
| Project dashboards and resources | Source code and technical tests when implementation begins |
| Human-editable context | Reviewed, version-controlled engineering artifacts |

[The BRAIN v2 specification](docs/THE_BRAIN_V2_SPEC.md) defines the vault. This repository defines and eventually implements the software that interacts with it.

## Working with the project

Start with:

1. [The Jarvis Bible](docs/JARVIS_BIBLE.md)
2. [Foundation Executive Summary](docs/JARVIS_V1_FOUNDATION_EXECUTIVE_SUMMARY.md)
3. [Executive Product and Architecture Summary](docs/EXECUTIVE_PRODUCT_ARCHITECTURE_SUMMARY.md)
4. [Product Vision](docs/PRODUCT_VISION.md) and [Product Strategy](docs/product/PRODUCT_STRATEGY.md)
5. [System Principles](docs/SYSTEM_PRINCIPLES.md)
6. [Version Roadmap](docs/product/VERSION_ROADMAP.md)
7. [The BRAIN v2](docs/THE_BRAIN_V2_SPEC.md)
8. [System Architecture](docs/SYSTEM_ARCHITECTURE.md) and [Enterprise Review](docs/reviews/ENTERPRISE_ARCHITECTURE_REVIEW.md)
9. [Storage Architecture](docs/STORAGE_ARCHITECTURE.md) and [Security Threat Model](docs/reviews/SECURITY_THREAT_MODEL.md)
10. [AI Behavior Standard](docs/AI_BEHAVIOR_STANDARD.md), [UX Specification](docs/ux/UX_INTERACTION_SPECIFICATION.md), and [Query Evaluation](evaluations/QUERY_EVALUATION_BENCHMARK.md)
11. [Capability PRDs](docs/prd/README.md)
12. [Plugin SDK](docs/sdk/PLUGIN_SDK_SPECIFICATION.md) and [Agent Specifications](docs/agents/AGENT_SPECIFICATIONS.md)
13. [Architecture Decision Matrix](docs/ARCHITECTURE_DECISION_MATRIX.md), [ADRs](docs/adr/), and [Architecture Review Board](docs/governance/ARCHITECTURE_REVIEW_BOARD.md)
14. [Implementation Plan](docs/IMPLEMENTATION_PLAN.md), [Quality Checklists](docs/ENGINEERING_QUALITY_CHECKLISTS.md), and [Developer Experience](docs/DEVELOPER_EXPERIENCE_STRATEGY.md)
15. [Prompt Library](prompts/PROMPT_LIBRARY.md), [Demo Vault](docs/demo/DEMO_VAULT_SPECIFICATION.md), and [Future Research Backlog](research/FUTURE_RESEARCH_BACKLOG.md)

All human and AI contributions follow [CONTRIBUTING.md](CONTRIBUTING.md) and the [AI Behavior Standard](docs/AI_BEHAVIOR_STANDARD.md).

## Current status

Version `0.1.0` established the read-only Jarvis Core foundation. Phase 2 adds real-vault health reporting, deterministic offline querying, metrics, and implementation-ready product architecture while preserving read-only operation. Version `0.3` (in review) turns the query prototype into an intelligent read-only query engine: a dedicated lexical index, deterministic and explainable ranking, source citations, a token-budgeted context builder, trace mode, and the `search` / `summarize` / `explain` commands — with no write capability introduced. See the [Querying guide](docs/software/QUERYING.md), [ADR-0012](docs/adr/ADR-0012-Query-Engine-Is-A-Layered-Deterministic-Pipeline.md), and the [v0.3 Implementation Report](docs/software/V0.3_IMPLEMENTATION_REPORT.md).

## Related documents

- [Product Vision](docs/PRODUCT_VISION.md)
- [System Principles](docs/SYSTEM_PRINCIPLES.md)
- [Implementation Plan](docs/IMPLEMENTATION_PLAN.md)
- [Knowledge Standard](docs/KNOWLEDGE_STANDARD.md)
- [Vault Schema](docs/VAULT_SCHEMA.md)
- [Storage Architecture](docs/STORAGE_ARCHITECTURE.md)
- [Migration Execution Plan](docs/MIGRATION_EXECUTION_PLAN.md)
- [Architecture Decision Matrix](docs/ARCHITECTURE_DECISION_MATRIX.md)

## Revision history

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-07-27 | Initial engineering foundation |
