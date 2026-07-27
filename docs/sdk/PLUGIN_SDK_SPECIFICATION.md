# Plugin SDK Specification

| Field | Value |
|---|---|
| Purpose | Define the public, capability-safe extension contract |
| Status | Draft; no implementation authorization |
| Version | 0.1.0 |
| Owner | Platform Architecture |
| Revised | 2026-07-27 |
| Related | [Plugin PRD](../prd/PLUGIN_SYSTEM.md), [Security Threat Model](../reviews/SECURITY_THREAT_MODEL.md) |

## Design goals

- Language-neutral, out-of-process extensions.
- Least-privilege capabilities and explicit user consent.
- Stable contracts with negotiated compatibility.
- Failure, update, and removal isolation.
- First-party and third-party plugins use the same SDK.

## Extension types

| Type | Contribution |
|---|---|
| Data source | Enumerate/read authorized canonical or external records |
| Tool | Propose or perform typed actions |
| Trigger | Emit normalized events |
| Workflow step | Deterministic or mediated transformation |
| Agent profile | Manifest/instructions/evaluations, no new runtime |
| Renderer | Declarative rendering for an artifact type |
| Dashboard widget | Sandboxed/declarative view backed by approved queries |

One package may declare multiple contributions, each with its own capabilities.

## Package and manifest

```yaml
schema: jarvis.plugin/v1
id: com.example.github-insights
name: GitHub Insights
version: 1.2.0
publisher: com.example
sdk: ">=1.0 <2.0"
runtime:
  protocol: jarvis-plugin-rpc/1
  command: ["plugin-host"]
contributions:
  tools:
    - id: repository.summary
      input_schema: schemas/repository-summary-input.json
      output_schema: schemas/repository-summary-output.json
capabilities:
  - github.repository.read
network:
  domains: ["api.github.com"]
state_schema: 2
```

Manifest, schemas, package contents, signature, and publisher identity are hashed. Unknown fields follow schema compatibility policy; security-sensitive unknowns fail closed.

## Lifecycle

1. **Discover:** locate package from explicit source.
2. **Verify:** signature, publisher trust, package hash, manifest, SDK range, malware/advisory checks.
3. **Review:** show contributions, data access, network destinations, secrets, and risk.
4. **Install:** place immutably, initialize namespaced state, do not activate yet.
5. **Grant:** user/admin assigns scoped capabilities.
6. **Activate:** launch isolated process and complete handshake.
7. **Operate:** invoke with per-call task grant, quotas, audit, and cancellation.
8. **Update:** verify, compare capability/state changes, migrate transactionally, health-check, then switch.
9. **Suspend/revoke:** stop new calls immediately and cancel where safe.
10. **Uninstall:** terminate, remove package, offer deletion/export of state, grants, and secrets.

## Registration and discovery

Plugins register contributions only during handshake. Dynamic capability invention is prohibited. Core returns:

- runtime/SDK versions;
- granted capability handles (not raw secrets);
- locale and supported feature flags;
- size/time limits;
- correlation identity.

Duplicate global plugin IDs fail. Contribution IDs are namespaced by plugin ID.

## IPC protocol

Use framed authenticated RPC over OS-local transport. Required messages:

- `hello`, `capabilities`, `ready`, `health`;
- `invoke`, `progress`, `result`, `error`, `cancel`;
- `event.subscribe`, `event.deliver`, `event.ack`;
- `config.validate`, `config.changed`;
- `state.migrate`, `shutdown`.

Every request includes protocol version, request/task IDs, deadline, capability token, trace ID, and payload schema URI. Payload limits and backpressure are enforced by host.

## Permission model

Capabilities are verbs over scoped resources:

```text
vault.note.read(project:ai-operating-system)
github.repository.read(JMurray40/AI-Operating-System)
filesystem.file.propose_write(C:\Approved\Folder)
network.connect(api.github.com:443)
secret.use(github.oauth; audience=api.github.com)
```

Plugins receive opaque handles, not ambient filesystem/network/secrets. A manifest request is not a grant. Grants may be once, task, session, workspace, or persistent; high-risk capabilities cannot be persistent by default.

## Configuration and secrets

- Plugin declares JSON Schema for non-secret configuration.
- Core renders/validates settings and returns redacted configuration.
- Secrets are stored by the broker and referenced by opaque ID.
- Secret use is audience-bound and audited; values never enter logs or model context.
- Export excludes secrets unless a dedicated secure transfer exists.

## Events and hooks

Events use `jarvis.event/v1`: ID, type, source, workspace, timestamp, source revision, sensitivity, correlation, and payload schema. Delivery is at-least-once; consumers must be idempotent.

Initial hooks:

- source discovered/changed/deleted;
- project resumed;
- task started/completed/failed;
- approval requested/resolved;
- workflow triggered;
- plugin health/capability changed.

Plugins cannot block the core event loop. Synchronous pre-action hooks are policy extensions reserved for trusted first-party/admin components, not ordinary plugins.

## Tool contract

A tool declares title, purpose, side-effect class, input/output JSON Schemas, idempotency support, timeout, cancellation support, and data egress. Output is untrusted and includes structured value, user-safe summary, provenance, effect receipt, and warnings.

## UI contributions

Prefer declarative forms, tables, charts, Markdown, and command descriptors. If code-based UI is later supported, run it in a sandboxed origin with no direct core API, DOM, filesystem, or unrestricted network access. UI contribution receives the same capability-scoped bridge.

## Versioning and compatibility

- SDK uses semantic versioning after 1.0.
- Protocol and schemas are independently versioned.
- Host negotiates feature flags, not guessed behavior.
- Minor versions add optional capabilities; major versions may break contracts.
- At least two prior major host versions receive a documented compatibility window after v2.0.
- Deprecations publish replacement, detection warning, migration guide, and removal release.
- Plugins publish minimum/maximum tested host versions.

## State migration

Plugin state is namespaced and versioned. Update runs migration on a copy, validates, then atomically switches. Failure restores package, state, configuration, and grants. Core never interprets opaque plugin state as canonical knowledge.

## Distribution and trust

Trust levels: local-development, unverified, verified-publisher, reviewed, enterprise-approved. Signing proves package/publisher continuity, not safety. Registry supports revocation, security advisories, provenance, SBOM, hashes, and reproducible-build evidence.

## Reference example

A read-only GitHub plugin:

1. requests one repository read scope and `api.github.com`;
2. receives an OAuth handle bound to GitHub;
3. exposes `repository.status`;
4. returns structured commits/issues plus source URLs and retrieval time;
5. cannot read vault notes unless separately granted;
6. cannot create issues because no write capability exists.

## Conformance suite

- manifest/schema validation;
- handshake and version negotiation;
- capability denial/expiry/revocation;
- timeout/cancellation/backpressure;
- crash/restart/state migration;
- malicious input/output and injection;
- undeclared filesystem/network/secret access;
- update capability escalation;
- audit completeness;
- deterministic mock host.

## Open decisions

- Primary sandbox technology (restricted process, container, or WASM).
- Package signing root and registry governance.
- Whether declarative widgets ship in v1 of the SDK.
- Remote plugin workers and enterprise attestation.

These require ADRs before SDK implementation.

## Revision history

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-07-27 | Initial complete SDK design |
