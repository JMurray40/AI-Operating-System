# PRD: MCP Integration

| Field | Value |
|---|---|
| Status | Draft |
| Target | v0.7 |
| Owner | Platform/Integrations |
| Depends on | Tool gateway, capability policy, secrets, plugin host, protocol compatibility tests |

## Problem statement

MCP can connect Jarvis to a broad tool ecosystem, but remote server descriptions and tool outputs are untrusted. Directly exposing MCP tools to models would bypass consistent permissions, auditing, and data-loss controls.

## Goals

- Import and expose MCP capabilities through one governed gateway.
- Normalize discovery, invocation, resources, prompts, errors, and cancellation.
- Preserve protocol interoperability without making MCP the internal domain model.
- Prevent servers or content from escalating authority.

## User stories

- Connect a local or remote MCP server and inspect its declared capabilities.
- Approve tools individually and scope their data access.
- See exactly which server/tool will run and what data will leave the system.
- Diagnose protocol/version failures.
- Expose approved Jarvis tools to an external MCP client in a later phase.

## Functional requirements

1. Register local stdio and approved remote transports.
2. Pin server identity/configuration and record protocol capabilities.
3. Discover tools/resources/prompts and map them to internal typed descriptors.
4. Treat descriptions, schemas, resources, and outputs as untrusted.
5. Validate arguments and results with size/type limits.
6. Route every invocation through policy, approval, timeout, cancellation, audit, and redaction.
7. Separate server credentials through a secrets broker.
8. Detect capability drift and require review before newly declared tools activate.
9. Provide health, logs, reconnect/backoff, and disable controls.
10. Prevent recursive MCP/Jarvis tool loops and enforce call-depth budgets.

## Non-functional requirements

- One failing server cannot block others.
- No raw secret reaches model context or logs.
- Tool identity is stable across reconnects or marked changed.
- Transport security and server authentication are required remotely.
- Invocation is idempotent only when the tool contract explicitly supports it.

## Architecture considerations

MCP is an edge adapter to the internal Tool Gateway. Internal permissions use Jarvis capability vocabulary; servers cannot declare themselves pre-approved. Maintain protocol version adapters and captured conformance fixtures. Do not conflate MCP servers with trusted plugins: a plugin extends Jarvis; an MCP server provides external protocol capabilities.

## Edge cases

Tool schema changes; server spoofing; prompt injection in descriptions/results; huge resources; cancellation ignored; duplicate tool names; server asks for OAuth interactively; nested tool call loops; remote server disappears after approval.

## Acceptance criteria

- Conformance tests cover at least local and remote reference servers.
- Capability drift disables affected tools pending review.
- Injection corpus cannot alter system policy.
- Disallowed egress and secret-exfiltration tests pass.
- Every invocation has server identity, tool version/schema hash, approval, arguments digest, and outcome in audit.

## Future enhancements

Jarvis MCP server mode, delegated OAuth, server marketplace metadata, remote attestation, streaming resources, and enterprise gateway policy.
