# PRD: Plugin System

| Field | Value |
|---|---|
| Status | Draft |
| Target | v0.7 |
| Owner | Platform |
| Depends on | Capability model, isolation, secrets broker, event and audit schemas |

## Problem statement

Hard-coding every integration makes core unmaintainable; loading arbitrary third-party code makes the personal knowledge system unsafe. The product needs extensibility with enforceable permissions, lifecycle management, and compatibility.

## Goals

- Extend data sources, tools, workflows, UI contributions, and renderers safely.
- Make permissions understandable and revocable.
- Isolate failures and untrusted code from core.
- Support a governed ecosystem without breaking older installations.

## User stories

- Install a signed plugin and review requested capabilities.
- Grant one repository or folder rather than all files.
- Disable/revoke a plugin and see what data/state remains.
- Diagnose an unhealthy plugin without exposing vault content.
- Develop against a local SDK and compatibility suite.

## Functional requirements

1. Discover packaged plugins through explicit directories/registry, never arbitrary import scanning.
2. Validate signed manifest, package hash, publisher, SDK range, entry points, and capabilities.
3. Install, configure, activate, suspend, update, roll back, and uninstall.
4. Run third-party plugins out of process with authenticated IPC.
5. Broker filesystem, network, secrets, provider, event, UI, and tool capabilities.
6. Support scoped grants and just-in-time approval.
7. Enforce quotas, timeouts, cancellation, rate limits, and health checks.
8. Namespace plugin state and migrations.
9. Emit auditable lifecycle and invocation events.
10. Provide local developer mode visibly distinct from trusted production mode.

## Non-functional requirements

- Plugin crash cannot crash core.
- Revocation takes effect before the next invocation.
- Plugin cannot enumerate undeclared resources.
- Install/update is transactional and rollbackable.
- Startup remains useful when a plugin is incompatible or corrupt.

## Architecture considerations

The detailed contract is in [Plugin SDK Specification](../sdk/PLUGIN_SDK_SPECIFICATION.md). Prefer language-neutral JSON/MessagePack RPC over importing Python modules. First-party plugins use the same public contract. UI extensions must be declarative or sandboxed; never inject remote JavaScript into the trusted shell.

## Edge cases

Publisher key revoked; manifest capability increases during update; state migration fails; plugin hangs; dependency conflict; offline verification; plugin removed while a workflow is running; malicious telemetry.

## Acceptance criteria

- Reference hostile plugin fails sandbox escape and undeclared access tests.
- Capability increase blocks update pending approval.
- Crash/hang isolation and rollback tests pass.
- Two independently developed reference plugins pass conformance.
- Uninstall documents and offers removal of plugin-owned state and secrets.

## Future enhancements

Marketplace, paid plugins, remote execution, WASM sandbox, organizational allowlists, certification levels, and reproducible builds.
