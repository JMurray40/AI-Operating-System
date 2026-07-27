# Architecture Decision Matrix

| Field | Value |
|---|---|
| Purpose | Summarize the current architectural decisions and unresolved decision work |
| Status | Active |
| Version | 1.0.0 |
| Owner | Jason |
| Revised | 2026-07-27 |
| Related | [Architecture Decision Records](adr/), [System Principles](SYSTEM_PRINCIPLES.md), [System Architecture](SYSTEM_ARCHITECTURE.md) |

## Current decisions

| Topic | Current decision | Record | Status |
|---|---|---|---|
| Durable knowledge | The BRAIN is the human-owned durable knowledge layer | [ADR-0001](adr/ADR-0001-The-Brain-Is-The-Durable-Knowledge-Layer.md) | Accepted |
| Knowledge format | Markdown with structured metadata is canonical | [ADR-0002](adr/ADR-0002-Markdown-Is-The-Canonical-Storage.md) | Accepted |
| Software authority | GitHub is the source of truth for code and repository engineering artifacts | [ADR-0003](adr/ADR-0003-GitHub-Is-The-Source-Of-Truth-For-Code.md) | Accepted |
| Project navigation | Project dashboards are the primary navigation and context-loading layer | [ADR-0004](adr/ADR-0004-Project-Dashboards-Are-The-Primary-Navigation-Layer.md) | Accepted |
| Migration safety | Establish and verify an inventory before significant modification | [ADR-0005](adr/ADR-0005-Inventory-Before-Modification.md) | Accepted |
| Prototype language | Python is used for Jarvis Core prototype; supported floor remains under review | ADR-0006 in authoritative v0.1 | Proposed |
| Default operating mode | Jarvis is structurally read-only unless a separate effect capability is granted | [ADR-0007](adr/ADR-0007-Read-Only-Is-The-Default-Operating-Mode.md) | Accepted |
| Plugin permissions | Plugins declare capabilities in manifests; grants are separate and enforced externally | [ADR-0008](adr/ADR-0008-Plugins-Require-Declarative-Permission-Manifests.md) | Proposed |
| Durable memory | AI-generated memory is proposed, reviewed, and atomically committed | [ADR-0009](adr/ADR-0009-Durable-Memory-Is-Proposal-Based.md) | Proposed |
| AI providers | Providers are accessed through a versioned, capability-aware abstraction | [ADR-0010](adr/ADR-0010-AI-Providers-Are-Accessed-Through-A-Versioned-Abstraction.md) | Accepted |
| MCP | MCP is adapted through an isolated gateway and the internal Tool Gateway | [ADR-0011](adr/ADR-0011-MCP-Is-Mediated-By-An-Isolated-Gateway.md) | Proposed |
| Storage ownership | Each durable object has one canonical owner; other copies declare their role | Not yet recorded | Proposed |
| Runtime state | Operational state is separate from durable knowledge; SQLite is the initial candidate | Not yet recorded | Proposed |
| Search | Search indexes and embeddings are rebuildable projections | Not yet recorded | Proposed |
| AI providers | Models are interchangeable reasoning engines, not durable memory authorities | Covered by principles; ADR pending if implementation requires | Principle |
| Automation | Events do not imply permission; consequential writes retain approval gates | Not yet recorded | Proposed |

## Decision status meanings

| Status | Meaning |
|---|---|
| Proposed | Documented direction awaiting explicit architectural approval |
| Accepted | Approved and binding until superseded |
| Superseded | Replaced by a later ADR |
| Rejected | Considered and intentionally not selected |
| Principle | Governed currently by system principles; an ADR may be added when a concrete implementation decision is required |

## Recommended next ADRs

| Candidate | Decision question | Trigger |
|---|---|---|
| ADR-0012 — Canonical Storage Ownership | Must every durable object have one declared authoritative system? | Approval of [Storage Architecture](STORAGE_ARCHITECTURE.md) |
| ADR-0013 — Operational State Is Separate from Durable Knowledge | What belongs in the runtime database, and is SQLite the initial implementation? | Runtime schema design |
| ADR-0014 — Search Indexes Are Rebuildable Projections | What guarantees make search disposable and reproducible? | Search implementation |
| ADR-0015 — Automation Events Do Not Confer Authority | How are unattended events separated from approval to act? | First background write workflow |

This matrix summarizes ADRs but never replaces their context, alternatives, or consequences.

## Revision history

| Version | Date | Change |
|---|---|---|
| 1.1.0 | 2026-07-27 | Added ADR-0006 through ADR-0011 and renumbered future candidates |
| 1.0.0 | 2026-07-27 | Initial executive decision summary |
