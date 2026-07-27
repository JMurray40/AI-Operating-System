# ADR-0011: MCP Is Mediated by an Isolated Gateway

| Field | Value |
|---|---|
| Status | Proposed |
| Date | 2026-07-27 |
| Deciders | Pending architecture and security review |
| Related | [MCP PRD](../prd/MCP_INTEGRATION.md), [Plugin SDK](../sdk/PLUGIN_SDK_SPECIFICATION.md), [Security Threat Model](../reviews/SECURITY_THREAT_MODEL.md) |

## Context

MCP provides valuable interoperability with tools, resources, and prompts. MCP server descriptions, schemas, resources, prompts, and outputs are controlled outside Jarvis and may be malformed, compromised, or intentionally hostile. Connecting servers directly to models would allow external text to influence tool selection and action without consistent policy.

MCP is a protocol boundary, not an authorization or trust boundary.

## Decision

MCP servers connect through an isolated MCP Gateway that adapts protocol capabilities into the internal Tool Gateway.

The gateway:

- authenticates and pins server identity/configuration;
- treats discovered metadata and outputs as untrusted;
- normalizes tools/resources/prompts into versioned internal descriptors;
- validates arguments/results and enforces size, depth, timeout, and cancellation;
- routes every invocation through Jarvis capability, egress, approval, secret, and audit controls;
- detects capability/schema drift and disables affected capabilities pending review;
- prevents recursive call loops and enforces budgets;
- isolates server failure from core and other servers.

MCP servers cannot declare themselves trusted or pre-approved.

## Alternatives considered

### Expose all MCP tools directly to the model

Rejected because tool descriptions and model choices would effectively control authority.

### Treat MCP servers as ordinary trusted plugins

Rejected because MCP servers have different lifecycle, transport, discovery, and trust semantics.

### Avoid MCP and build proprietary integrations only

Rejected because it discards ecosystem interoperability and duplicates connector work.

### Use MCP as the internal Jarvis tool model

Rejected because internal policy, identity, provenance, and effect semantics must remain under Jarvis control and evolve independently.

## Tradeoffs

- Gateway mediation adds latency and protocol translation.
- Some MCP features may not map immediately.
- Compatibility and adversarial testing become ongoing responsibilities.

## Consequences

- MCP and native/plugin tools share one enforcement and audit model.
- Server capability changes cannot activate silently.
- Secrets are brokered and audience-bound.
- Remote MCP requires authenticated encrypted transport.
- Jarvis MCP server mode, if added, is a separate outbound exposure decision.

## Approval conditions

Accept after the internal Tool Gateway contract, capability model, server identity, transport policy, drift handling, and MCP conformance/adversarial suites are approved.
