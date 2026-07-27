# ADR-0008: Plugins Require Declarative Permission Manifests

| Field | Value |
|---|---|
| Status | Proposed |
| Date | 2026-07-27 |
| Deciders | Pending architecture and security review |
| Related | [Plugin SDK](../sdk/PLUGIN_SDK_SPECIFICATION.md), [Plugin PRD](../prd/PLUGIN_SYSTEM.md), [Security Threat Model](../reviews/SECURITY_THREAT_MODEL.md) |

## Context

Plugins may access knowledge, files, networks, secrets, providers, tools, events, or interface surfaces. In-process code with ambient authority would allow a defective or malicious plugin to read the vault, exfiltrate secrets, or perform actions unrelated to its purpose. Runtime prompts and publisher signatures do not provide sufficient containment.

## Decision

Every plugin must ship a validated declarative manifest identifying:

- stable plugin/publisher/version identity;
- compatible SDK and protocol ranges;
- contributions and their typed schemas;
- requested capabilities and resource scopes;
- network destinations;
- secret audiences;
- runtime/isolation requirements;
- state schema and migration behavior.

A manifest request is not permission. Installation presents the request; the user or administrator grants a scoped subset. Capability increases during update require renewed approval. The host enforces grants outside the plugin process.

## Alternatives considered

### Trust signed plugins

Rejected as sufficient control. Signing establishes provenance, not safety or least privilege.

### Ask for permission only when a plugin first uses a resource

Rejected as the sole mechanism because users cannot evaluate overall installation risk and behavior becomes nondeterministic.

### Run plugins in the core process

Rejected for third-party plugins because crashes, dependencies, and arbitrary code would share the core trust boundary.

### Give plugins the same permissions as the user

Rejected because ambient authority creates unacceptable blast radius.

## Tradeoffs

- Plugin development and installation require more ceremony.
- Capability vocabulary and sandbox enforcement add platform work.
- Some integrations need multiple understandable grants.

## Consequences

- Plugin discovery can occur without activation.
- Grants are inspectable, revocable, auditable, and scoped.
- Updates are blocked when requested authority expands.
- First-party extensions use the same public capability model.
- Permission manifests must be versioned and covered by compatibility tests.
- Plugins must operate out of process or within an equivalently enforceable sandbox.

## Approval conditions

Accept after the capability vocabulary, sandbox boundary, grant lifecycle, manifest schema, and adversarial conformance tests are approved.
