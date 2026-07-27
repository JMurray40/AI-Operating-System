# ADR-0010: AI Providers Are Accessed Through a Versioned Abstraction

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-07-27 |
| Deciders | Jason |
| Related | [System Principles](../SYSTEM_PRINCIPLES.md), [Architecture Review](../reviews/ENTERPRISE_ARCHITECTURE_REVIEW.md), [Agent PRD](../prd/AGENT_FRAMEWORK.md) |

## Context

Claude, OpenAI, Gemini, Ollama, and future providers expose different message formats, streaming events, structured outputs, tool calls, usage data, safety behavior, and retention terms. Hard-coding one provider into application or domain logic would make project memory, interfaces, evaluation, and workflows dependent on that vendor.

Version 0.1 establishes a minimal provider protocol and deterministic mock. That contract is intentionally too narrow for chat and agents.

## Decision

All AI provider access passes through a versioned provider gateway and normalized domain protocol.

Application code selects model roles and required capabilities rather than provider model names. Adapters translate normalized requests/events to provider APIs and report supported capabilities. Provider-specific features remain available through explicit negotiated extensions; they do not leak implicitly into core domain objects.

Policy determines whether a provider may receive a context package based on workspace, sensitivity, destination, user configuration, and provider data-use terms.

## Alternatives considered

### Standardize directly on one provider API

Rejected because it creates strategic lock-in and makes local/private fallback difficult.

### Use only a lowest-common-denominator interface

Rejected because it would prevent safe use of valuable structured, streaming, multimodal, and tool capabilities.

### Allow each feature to call providers directly

Rejected because policy, audit, error, usage, and compatibility behavior would diverge.

### Adopt a third-party gateway as the domain contract

Rejected as the architectural boundary. A gateway library/service may be an adapter implementation, but Jarvis owns its stable internal contract.

## Tradeoffs

- Adapters and conformance tests require ongoing maintenance.
- Some provider behavior cannot be perfectly normalized.
- Capability negotiation and versioning add design work.

## Consequences

- Provider changes do not alter canonical knowledge formats.
- Mock and replay adapters can drive deterministic tests.
- Usage, cost, errors, streaming, cancellation, and policy are normalized.
- The v0.1 `summarize()` protocol must be superseded before real chat/agent implementation.
- Provider-specific model identifiers remain configuration, not durable project knowledge.
- At least two adapters must pass the same contract suite before v1.0.

## Revisit conditions

Revisit the normalized surface when a materially useful provider capability cannot be expressed without unsafe or pervasive provider-specific branching.
