# Jarvis Core (Prototype) — Software Docs

Jarvis Core is the first, read-only software foundation for the AI Operating System.
It reads an Obsidian-compatible fixture directory, parses notes and metadata, resolves
relationships, assembles a deterministic **project context package**, validates it, and
sends it to a **mock** AI provider — all with no network, no API keys, no database, and
no writes to any source it reads.

> Phase 2 adds real-vault loading, performance instrumentation, and a vault health
> report (`jarvis vault-report`) — all still strictly read-only. See
> [VAULT_HEALTH.md](VAULT_HEALTH.md).

> Scope guardrail: this prototype implements the read-only slice of
> [IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md) Phase 3. It deliberately omits the
> web UI, SQLite persistence, real providers, agents, MCP, and any write capability.

## Documents

- [SETUP.md](SETUP.md) — install and run locally.
- [ARCHITECTURE.md](ARCHITECTURE.md) — prototype design and data flow (with diagram).
- [CLI_USAGE.md](CLI_USAGE.md) — commands, options, and exit codes.
- [TESTING.md](TESTING.md) — how to run tests, lint, and type checks.
- [FIXTURE_DESIGN.md](FIXTURE_DESIGN.md) — how the sample vaults are built.
- [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) — what it does not do yet.
- [DEFERRED_DECISIONS.md](DEFERRED_DECISIONS.md) — choices left open for review.
- [EXTENDING.md](EXTENDING.md) — how future provider and storage adapters plug in.
- [VAULT_HEALTH.md](VAULT_HEALTH.md) — Phase 2: real-vault health report and performance.

## Governing documents

Conforms to [VAULT_SCHEMA.md](../VAULT_SCHEMA.md), [KNOWLEDGE_STANDARD.md](../KNOWLEDGE_STANDARD.md),
[SYSTEM_PRINCIPLES.md](../SYSTEM_PRINCIPLES.md), and the accepted ADRs — especially
[ADR-0004 (dashboards)](../adr/ADR-0004-Project-Dashboards-Are-The-Primary-Navigation-Layer.md)
and [ADR-0005 (inventory before modification)](../adr/ADR-0005-Inventory-Before-Modification.md).
The language choice is proposed in
[ADR-0006](../adr/ADR-0006-Use-Python-For-Jarvis-Core-Prototype.md).
