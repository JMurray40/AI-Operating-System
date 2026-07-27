# ADR-0007: Read-Only Is the Default Operating Mode

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-07-27 |
| Deciders | Jason |
| Related | [System Principles](../SYSTEM_PRINCIPLES.md), [Security Threat Model](../reviews/SECURITY_THREAT_MODEL.md), [ADR-0005](ADR-0005-Inventory-Before-Modification.md) |

## Context

Jarvis operates over high-value personal and project knowledge. Parsing, retrieval, context assembly, AI reasoning, and source inspection provide substantial value without requiring mutation. Combining reads and writes too early would make ordinary questions capable of damaging canonical knowledge and would make “read-only” depend on model behavior rather than system capability.

Version 0.1 proves the read path through a repository contract with no write method and mutation-safety tests.

## Decision

Jarvis operates read-only by default.

Read-only is enforced structurally:

- adapters receive no write method or writable handle;
- effectful tools are absent from the task capability set;
- dry-run and inspection modes cannot invoke write paths;
- tests verify canonical inputs remain unchanged.

Write capability is a separate, explicitly enabled subsystem. It requires a scoped action, policy decision, human approval where applicable, expected target revision, atomic operation, audit record, validation, and rollback.

## Alternatives considered

### Allow writes but require confirmation

Rejected as the default because a broad write-capable process still increases blast radius and confirmation can be spoofed, misunderstood, or bypassed by defects.

### Let the model decide when a write is safe

Rejected because probabilistic model judgment is not an authorization boundary.

### Clone the vault for every operation

Useful for testing, but insufficient as the product policy and too expensive for every read.

## Tradeoffs

- Some workflows require an extra proposal and approval step.
- Read and write adapters may duplicate a small amount of integration work.
- Early releases automate less.

These costs buy testable safety, simpler reasoning, and user trust.

## Consequences

- All new capabilities must state whether they are read, propose, or execute.
- Chat, search, context, and initial agents remain useful without write authority.
- A future write API cannot be added casually to the existing read repository contract.
- Release tests must prove that read-only workflows cannot mutate canonical or external systems.
- Failures default to no effect.

## Revisit conditions

This decision may be refined when bounded pre-approved automation exists, but read-only remains the default for new connectors, plugins, agents, workspaces, and installations.
