# Future Research Backlog

| Field | Value |
|---|---|
| Purpose | Maintain evidence-seeking product and architecture investigations |
| Status | Active backlog |
| Version | 1.0.0 |
| Owner | Product and Architecture |
| Revised | 2026-07-27 |

## Scoring

- **Value:** H = material user/platform value; M = useful optimization; L = exploratory.
- **Complexity:** S = days; M = weeks; L = multi-month/cross-disciplinary.
- **Priority:** P0 before the associated capability; P1 near-term; P2 later; P3 speculative.

These are research items, not committed features. Each completed item should produce evidence, recommendation, rejected alternatives, risks, and an ADR trigger.

## Knowledge, identity, and memory

| # | Title | Description | Business value | Complexity | Priority | Dependencies |
|---:|---|---|---|:---:|:---:|---|
| 1 | Stable Entity Identity | Compare readable IDs, UUID/ULID, and content-derived identity across rename/merge. | Prevents wrong links and unsafe writes. | M | P0 | v0.1 models |
| 2 | Alias Collision Semantics | Define detection and human disambiguation for duplicate names. | Protects retrieval trust. | S | P0 | Stable identity |
| 3 | Context Package v1 | Publish ownership, compatibility, and evolution rules. | Enables clients/providers without drift. | M | P0 | Current package |
| 4 | Memory Candidate Schema | Model proposed create/update/link/supersede actions. | Enables safe durable memory. | M | P0 | Vault schema |
| 5 | Provenance Envelope | Unify source, revision, locator, actor, model, and derivation metadata. | Makes answers/actions auditable. | M | P0 | Identity |
| 6 | Knowledge Freshness | Define stale, superseded, reviewed, and expiry semantics. | Reduces outdated guidance. | M | P1 | Note lifecycle |
| 7 | Contradiction Taxonomy | Distinguish temporal change, scope difference, and real conflict. | Improves useful conflict detection. | M | P1 | Provenance |
| 8 | Duplicate Resolution UX | Test merge, alias, canonicalize, and keep-separate workflows. | Reduces vault clutter safely. | M | P1 | Memory proposals |
| 9 | Knowledge Decay Review | Surface unreviewed or aging facts without deleting them. | Maintains long-term quality. | M | P2 | Freshness |
| 10 | Preference Ownership | Decide settings DB versus vault profile for user preferences. | Avoids duplicate memory stores. | S | P0 | Storage architecture |

## Retrieval and context

| # | Title | Description | Business value | Complexity | Priority | Dependencies |
|---:|---|---|---|:---:|:---:|---|
| 11 | SQLite FTS Benchmark | Test indexing/query at 10k, 100k, and 1M notes. | Validates simplest scalable search. | M | P0 | Synthetic corpus |
| 12 | Chunk Boundary Study | Compare heading, paragraph, token, and semantic chunks. | Improves citations/relevance. | M | P1 | Search benchmark |
| 13 | Hybrid Rank Fusion | Compare RRF and weighted lexical/vector ranking. | Better semantic retrieval. | M | P1 | Embeddings |
| 14 | Local Embedding Models | Benchmark privacy, speed, multilingual quality, and size. | Enables private semantic search. | M | P1 | Reference hardware |
| 15 | Retrieval Evaluation Set | Build golden queries with judged results. | Makes search quality measurable. | M | P0 | Pilot knowledge |
| 16 | Context Budget Optimizer | Allocate tokens across project, decision, session, and evidence. | Reduces cost and omission. | L | P1 | Context v1 |
| 17 | Context Selection Explanation | Define reason codes and UI for included/excluded sources. | Builds user trust. | M | P0 | Context planner |
| 18 | Temporal Retrieval | Rank by event/effective time, not only modification date. | Improves current-state answers. | M | P2 | Freshness |
| 19 | Query Privacy Leakage | Test whether counts/scores reveal restricted content. | Prevents side-channel leaks. | M | P0 | Search ACL |
| 20 | Federated Search | Compare local projection versus live queries across SaaS. | Expands reach without copying. | L | P2 | Connectors |

## Provider and model gateway

| # | Title | Description | Business value | Complexity | Priority | Dependencies |
|---:|---|---|---|:---:|:---:|---|
| 21 | Provider Protocol v1 | Normalize messages, streaming, structured output, tools, usage, cancellation. | Avoids provider lock-in. | L | P0 | Chat PRD |
| 22 | Capability Negotiation | Represent model features without lowest-common-denominator design. | Enables best-provider use. | M | P0 | Provider v1 |
| 23 | Model Role Routing | Evaluate deterministic policy versus learned routing. | Balances quality/cost/privacy. | M | P1 | Provider metrics |
| 24 | Provider Egress Policy | Map sensitivity to allowed destinations and retention terms. | Protects private data. | M | P0 | Threat model |
| 25 | Local Model Baseline | Benchmark Ollama models for summarization, extraction, and injection resistance. | Private fallback. | M | P1 | Reference hardware |
| 26 | Cost Attribution | Allocate tokens/cost to task, project, agent, and workflow. | Controls spend. | S | P1 | Operational schema |
| 27 | Provider Failure Semantics | Standardize partial streams, retryability, and degraded response. | Improves reliability. | M | P0 | Provider v1 |
| 28 | Structured Output Reliability | Compare schema adherence and repair strategies. | Supports automation safely. | M | P1 | Provider adapters |
| 29 | Prompt Portability | Evaluate prompts across providers and versions. | Reduces behavioral drift. | M | P1 | Evaluation harness |
| 30 | Model Data-Use Registry | Track provider privacy, region, retention, and training policies. | Informs safe routing. | M | P1 | Connector governance |

## Security and privacy

| # | Title | Description | Business value | Complexity | Priority | Dependencies |
|---:|---|---|---|:---:|:---:|---|
| 31 | Sensitivity Label Model | Define inheritance, downgrade, redaction, and mixed-context rules. | Core privacy enforcement. | L | P0 | Workspace model |
| 32 | Approval Token Design | Bind approval to action digest, target revision, actor, and expiry. | Prevents replay/spoofing. | M | P0 | Permission model |
| 33 | Prompt Injection Corpus | Assemble Markdown, web, email, PDF, MCP, and tool attacks. | Tests real defense. | M | P0 | Security harness |
| 34 | Safe Markdown Rendering | Select sanitizer and remote-content policy. | Prevents UI compromise. | M | P0 | Chat UI |
| 35 | Windows Secret Store | Evaluate Credential Manager/DPAPI and portability. | Protects credentials. | M | P0 | Provider integration |
| 36 | Plugin Sandbox | Compare restricted process, container, AppContainer, and WASM. | Enables safe ecosystem. | L | P0 | Plugin SDK |
| 37 | Audit Integrity | Compare hash chaining, signing, and protected append stores. | Supports incident evidence. | M | P1 | Audit schema |
| 38 | Backup Encryption | Define key ownership, rotation, and restore UX. | Protects complete knowledge copy. | M | P1 | Backup strategy |
| 39 | Data Deletion Semantics | Map deletion across vault, index, DB, provider, device, backups. | Supports privacy and trust. | L | P1 | Retention policy |
| 40 | Local Malware Assumptions | Define what application can/cannot protect after host compromise. | Honest security boundary. | S | P0 | Threat model |

## Plugins, MCP, and integrations

| # | Title | Description | Business value | Complexity | Priority | Dependencies |
|---:|---|---|---|:---:|:---:|---|
| 41 | Plugin RPC Transport | Benchmark named pipes, sockets, gRPC, and JSON-RPC. | Stable language-neutral SDK. | M | P1 | Isolation choice |
| 42 | Plugin Signing Governance | Design publisher identity, revocation, and key recovery. | Marketplace trust. | L | P1 | Distribution model |
| 43 | Declarative Widgets | Test safe dashboard extension schema. | Extensibility without JS risk. | M | P2 | Dashboard contracts |
| 44 | Plugin State Migration | Prototype transactional upgrade/rollback. | Reliable plugin updates. | M | P1 | Plugin host |
| 45 | MCP Compatibility Matrix | Test protocol versions and popular servers. | Predictable integration. | M | P1 | MCP gateway |
| 46 | MCP Capability Drift | Detect server tool/schema changes safely. | Prevents silent escalation. | M | P0 | MCP registry |
| 47 | OAuth Broker | Design delegated auth without sharing refresh tokens. | Secure SaaS connectors. | L | P0 | Secrets broker |
| 48 | GitHub Adapter Scope | Define repos, issues, PRs, commits, webhooks, and caching. | High-value project context. | M | P1 | GitHub auth |
| 49 | Calendar Identity | Reconcile provider event IDs, recurrence, and updates. | Reliable scheduling context. | M | P2 | Calendar connector |
| 50 | Cloud Drive Change Tokens | Compare Drive/OneDrive/Dropbox incremental models. | Efficient external indexing. | L | P2 | Connector framework |

## Agents and automation

| # | Title | Description | Business value | Complexity | Priority | Dependencies |
|---:|---|---|---|:---:|:---:|---|
| 51 | Agent Manifest Schema | Formalize inputs, outputs, capabilities, budgets, and evaluations. | Consistent bounded agents. | M | P0 | Agent PRD |
| 52 | Delegation Safety | Model depth, capability attenuation, cancellation, and lineage. | Prevents runaway agents. | L | P0 | Agent runtime |
| 53 | Agent Evaluation Harness | Compare versions/providers on fixed tasks and rubrics. | Controls behavior regressions. | L | P0 | Reference agents |
| 54 | Budget Enforcement | Enforce cost/token/time/tool budgets below model. | Prevents resource runaway. | M | P0 | Runtime |
| 55 | Human Checkpoint UX | Test interruption timing and approval comprehension. | Reduces fatigue and errors. | M | P1 | Approval model |
| 56 | Workflow Event Store | Compare relational state machine and event-sourced models. | Durable automation. | L | P0 | Operational DB |
| 57 | Idempotent Effects | Catalog connector idempotency and reconciliation patterns. | Prevents duplicate actions. | L | P0 | Tool contracts |
| 58 | Compensation Patterns | Define rollback for email, files, calendar, and SaaS writes. | Safer automation. | M | P1 | Connector semantics |
| 59 | Trigger Storm Control | Debounce, coalesce, rate-limit, and backpressure events. | Stable background operation. | M | P1 | Event bus |
| 60 | Long-Running Case Model | Explore pauses lasting days with refreshed authority/context. | Complex workflows. | L | P2 | Durable runtime |

## User experience and accessibility

| # | Title | Description | Business value | Complexity | Priority | Dependencies |
|---:|---|---|---|:---:|:---:|---|
| 61 | Project Resume Study | Measure time saved and missing context in real use. | Validates flagship value. | M | P0 | Pilot dashboards |
| 62 | Context Preview UX | Test source selection, sensitivity, and token tradeoffs. | Builds informed trust. | M | P0 | Chat prototype |
| 63 | Approval Fatigue | Measure grouping, risk tiers, and comprehension. | Keeps safety usable. | M | P1 | Memory pilot |
| 64 | Nontechnical Setup | Prototype vault/provider onboarding and diagnostics. | Broadens adoption. | L | P1 | Desktop shell |
| 65 | Accessibility Baseline | Audit CLI, web, dashboard, graph, and mobile requirements. | Inclusive product. | M | P0 | UI design |
| 66 | Screen-Sharing Privacy | Design quick-hide and sensitive widget behavior. | Prevents accidental exposure. | S | P1 | Dashboard |
| 67 | Failure Language | Standardize actionable, nontechnical error messages. | Improves recovery. | S | P1 | Error taxonomy |
| 68 | Notification Policy | Study urgency, batching, quiet hours, and sensitive previews. | Avoids attention overload. | M | P2 | Mobile/desktop |
| 69 | Voice Confirmation | Evaluate unambiguous confirmations in noisy settings. | Safer voice control. | M | P2 | Voice prototype |
| 70 | Explainable Suggestions | Test why-now evidence for proactive connections. | Prevents “creepy” behavior. | M | P1 | Relationship engine |

## Storage, sync, and operations

| # | Title | Description | Business value | Complexity | Priority | Dependencies |
|---:|---|---|---|:---:|:---:|---|
| 71 | Operational Schema | Define task, conversation, approval, event, audit, and connector state. | Foundation for services. | L | P0 | Architecture decisions |
| 72 | SQLite Concurrency | Test WAL, backups, migrations, and worker access. | Validates local runtime DB. | M | P0 | Operational schema |
| 73 | Vault Snapshot Consistency | Detect files changing during scan/index. | Prevents mixed context. | M | P1 | Revision model |
| 74 | Atomic Vault Writes | Compare temp/replace/fsync behavior across OS/sync folders. | Safe memory writes. | L | P0 | Write PRD |
| 75 | Obsidian Sync Conflicts | Test common multi-device conflict patterns. | Protects canonical knowledge. | M | P1 | Sync choice |
| 76 | Schema Migration Framework | Define forward/backward compatibility and rollback. | Enables safe upgrades. | L | P0 | Public schemas |
| 77 | Index Rebuild SLO | Establish recovery time/resource targets by corpus size. | Operable search. | M | P1 | Search benchmark |
| 78 | Diagnostics Bundle | Design privacy-safe health/support export. | Reduces support cost. | M | P1 | Observability |
| 79 | Update Rollback | Test signed staged updates and database/schema rollback. | Reliable productization. | L | P1 | Desktop packaging |
| 80 | Disaster Recovery Drill | Define and execute vault/DB/config/secret recovery. | Demonstrates resilience. | M | P1 | Backup strategy |

## Enterprise and platform

| # | Title | Description | Business value | Complexity | Priority | Dependencies |
|---:|---|---|---|:---:|:---:|---|
| 81 | Tenant Isolation Model | Compare process, DB, index, key, and storage boundaries. | Prerequisite for teams. | L | P1 | v1.5 strategy |
| 82 | Identity Federation | Evaluate OIDC/SAML, SCIM, service accounts, and device trust. | Enterprise access. | L | P2 | Tenant model |
| 83 | Policy Administration | Design centrally managed capability/data/provider rules. | Governed enterprise use. | L | P2 | PDP |
| 84 | Data Residency | Map canonical, index, provider, log, and backup regions. | Regulated adoption. | L | P2 | Deployment model |
| 85 | Legal Hold/eDiscovery | Define retention/export across knowledge and operations. | Enterprise compliance. | L | P3 | Team workspaces |
| 86 | Customer-Managed Keys | Evaluate envelope encryption and key outage behavior. | High-trust deployments. | L | P3 | Enterprise storage |
| 87 | Marketplace Economics | Model pricing, review, liability, and support for plugins. | Platform revenue. | L | P3 | SDK adoption |
| 88 | Plugin Certification | Define automated/manual security and quality levels. | Ecosystem trust. | L | P2 | Marketplace |
| 89 | Public API Governance | Establish compatibility, quotas, auth, and deprecation. | Enables platform builders. | L | P2 | Internal API stable |
| 90 | Usage Metering | Measure providers/plugins/workflows without surveillance. | Cost and platform economics. | M | P2 | Privacy model |

## Domain and frontier capabilities

| # | Title | Description | Business value | Complexity | Priority | Dependencies |
|---:|---|---|---|:---:|:---:|---|
| 91 | Financial Data Lineage | Trace every analytic figure to source record/formula. | Enables trustworthy finance agent. | L | P1 | Finance fixtures |
| 92 | Bookkeeping Controls | Model entities, periods, control totals, and approval segregation. | Safe bookkeeping workflows. | L | P1 | Accounting integration |
| 93 | Coding Workspace Isolation | Compare worktrees, containers, and disposable environments. | Safer coding agent. | M | P1 | Coding agent |
| 94 | Research Source Quality | Develop authority/freshness/corroboration scoring. | Better research outcomes. | M | P1 | Research benchmarks |
| 95 | Home Safety Policy | Classify devices/actions and physical fail-safe requirements. | Safe home automation. | L | P2 | Device integrations |
| 96 | Multimodal Knowledge | Define OCR, image, audio, video provenance and chunking. | Expands usable knowledge. | L | P2 | Storage/search |
| 97 | On-Device Speech | Benchmark private STT/TTS latency and quality. | Private voice interface. | M | P2 | Desktop/mobile |
| 98 | Personal Temporal Model | Connect commitments, events, decisions, and project time safely. | Better planning/briefings. | L | P2 | Calendar + graph |
| 99 | Contradiction Resolution Agent | Test evidence-based conflict packets, never auto-resolution. | Maintains knowledge coherence. | L | P2 | Contradiction taxonomy |
| 100 | Proactive Connection Briefing | Evaluate “connections you missed” precision and user control. | Signature differentiated feature. | L | P1 | Relationship engine |

## Portfolio rules

- No more than three P0 investigations should run concurrently.
- Research must define a decision or uncertainty it will resolve.
- A prototype without benchmark or recommendation is incomplete.
- P2/P3 work may be promoted only when its dependency and user outcome are active.
- Findings that change a trust boundary, canonical store, public contract, or irreversible migration require an ADR.

## Revision history

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-07-27 | Initial 100-item research portfolio |
