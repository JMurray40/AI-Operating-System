# Architecture Decision Records

| Field | Value |
|---|---|
| Purpose | Index durable architecture decisions |
| Status | Active |
| Version | 0.5.0 |
| Owner | Jason |
| Revised | 2026-07-27 |
| Related | [System Architecture](../SYSTEM_ARCHITECTURE.md), [Development Guide](../DEVELOPMENT_GUIDE.md) |

## Index

| ADR | Title | Status |
|---|---|---|
| [0001](ADR-0001-The-Brain-Is-The-Durable-Knowledge-Layer.md) | The BRAIN is the durable knowledge layer | Proposed |
| [0002](ADR-0002-Markdown-Is-The-Canonical-Storage.md) | Markdown is canonical storage | Proposed |
| [0003](ADR-0003-GitHub-Is-The-Source-Of-Truth-For-Code.md) | GitHub is the source of truth for software | Proposed |
| [0004](ADR-0004-Project-Dashboards-Are-The-Primary-Navigation-Layer.md) | Project dashboards are the primary navigation layer | Accepted |
| [0005](ADR-0005-Inventory-Before-Modification.md) | Inventory before modification | Accepted |
| [0006](ADR-0006-Use-Python-For-Jarvis-Core-Prototype.md) | Use Python for the Jarvis Core prototype | Proposed |
| [0007](ADR-0007-Read-Only-Is-The-Default-Operating-Mode.md) | Read-only is the default operating mode | Accepted |
| [0008](ADR-0008-Plugins-Require-Declarative-Permission-Manifests.md) | Plugins require declarative permission manifests | Proposed |
| [0009](ADR-0009-Durable-Memory-Is-Proposal-Based.md) | Durable memory is proposal-based | Proposed |
| [0010](ADR-0010-AI-Providers-Are-Accessed-Through-A-Versioned-Abstraction.md) | AI providers use a versioned abstraction | Accepted |
| [0011](ADR-0011-MCP-Is-Mediated-By-An-Isolated-Gateway.md) | MCP is mediated by an isolated gateway | Proposed |
| [0012](ADR-0012-Query-Engine-Is-A-Layered-Deterministic-Pipeline.md) | The query engine is a layered, deterministic, citation-based pipeline | Accepted |
| [0014](ADR-0014-Retrieval-Relevance-Is-Separate-From-Answer-Confidence.md) | Retrieval relevance is separate from answer confidence | Accepted |
| [0015](ADR-0015-Authorization-Precedes-Retrieval-And-Graph-Expansion.md) | Authorization precedes retrieval and graph expansion | Accepted |
| [0016](ADR-0016-Citations-Bind-Passages-To-Source-Revisions.md) | Citations bind supporting passages to source revisions | Accepted |
| [0017](ADR-0017-Stable-Source-Identity-Is-Separate-From-Location.md) | Stable source identity is separate from location | Accepted |
| [0018](ADR-0018-Project-Resume-Uses-Exact-Tiered-Project-Identity.md) | Project Resume uses exact, tiered project identity | Accepted |
| [0019](ADR-0019-Project-Resume-Uses-Explicit-Authority-Temporal-And-Conflict-Ordering.md) | Project Resume uses explicit authority, temporal, supersession, and conflict ordering | Accepted |
| [0020](ADR-0020-Project-Resume-Claims-Require-Validated-Evidence-And-Two-Hard-Budgets.md) | Project Resume claims require validated evidence and two hard budgets | Accepted |
| [0021](ADR-0021-Repository-Activity-Is-A-Request-Scoped-Local-Read-Only-Git-Capability.md) | Repository activity is a request-scoped local read-only Git capability | Accepted |

Accepted ADRs are not rewritten to reflect a later choice. A new ADR supersedes the earlier record.

## Revision history

| Version | Date | Change |
|---|---|---|
| 0.5.0 | 2026-07-27 | Added accepted ADR-0018 through ADR-0021 for v0.4 Project Resume |
| 0.4.0 | 2026-07-27 | Added accepted ADR-0014 through ADR-0017 for v0.3.1 Query Trust Contracts |
| 0.3.0 | 2026-07-27 | Added ADR-0012 for the v0.3 query-engine architecture |
| 0.2.0 | 2026-07-27 | Added ADR-0006 through ADR-0011 to the decision history |
| 0.1.0 | 2026-07-27 | Initial ADR index |
