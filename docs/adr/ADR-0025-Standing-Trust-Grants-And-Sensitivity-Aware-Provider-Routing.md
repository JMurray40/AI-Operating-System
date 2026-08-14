# ADR-0025: Standing Trust Grants and Sensitivity-aware Provider Routing

| Field | Value |
|---|---|
| Status | Proposed - Product Owner approved in principle; exact package pending validation |
| Date | 2026-08-14 |
| Deciders | Product Owner, advised by Chief Architect / CTO |
| Related | ADR-0010, ADR-0015, ADR-0022, ADR-0023, ADR-0024 |
| Supersedes | ADR-0023 per-turn human confirmation and ADR-0024 single-real-adapter/no-selection scope only |

## Context

Per-turn approval of ordinary context makes the personal prototype feel like an approval workflow
rather than an agent. The Product Owner wants eligible `public` and `internal` context to use an
approved Gemini destination under a standing policy, while `private` and `restricted` context uses
an approved local Ollama model when feasible. Unknown material must remain untrusted, and local
failure must never become permission for remote disclosure.

## Decision

Jarvis may activate one exact owner-approved standing trust grant for the current process. The grant
binds its schema/version/digest, owner, workspace/project scope, destination, provider/model role and
identity, maximum sensitivity, hard limits, allowed operations, prompt-construction versions,
activation/expiry, and revocation generation. It contains no credential and permits no wildcard.
The user explicitly activates the exact digest once per process; activation is volatile. Strict
mode retains digest-bound per-turn human approval.

Every turn still produces an immutable visible `ContextSnapshot/v1`. The standing grant replaces
only the human confirmation for requests wholly inside its envelope. The snapshot binds the policy
digest and all existing semantic inputs. Dispatch revalidates policy, route, authorization,
sensitivity, limits, current bytes, snapshot digest, prompt versions, expiry, and revocation before
prompt assembly. Any drift blocks the request.

Route selection occurs before candidate generation and graph expansion using only explicit request
scope, declared maximum sensitivity, policy, and provider-readiness metadata:

| Declared maximum sensitivity | Eligible destination |
|---|---|
| `public`, `internal` | Exact approved Gemini profile under standing grant or strict approval |
| `private`, `restricted`, or a mixed ceiling including either | Exact approved local Ollama profile only |
| missing, malformed, unknown | None; excluded/fail closed |

One request has one route. Jarvis does not split context across destinations. Local unavailability,
model mismatch, capacity failure, cancellation, or timeout blocks the sensitive request; it never
falls back to Gemini. A user may create a new lower-ceiling request that visibly omits higher-tier
material and reports incomplete coverage. That is not declassification or fallback.

The local adapter uses the same versioned, non-streaming provider gateway, immutable snapshot,
budget, cancellation, output sanitization, citation, coverage, trace, and terminal-state contracts.
It must bind to an exact loopback-only Ollama profile with pinned runtime/model identities and no
non-loopback traffic, telemetry, update, cloud, or provider fallback. An exact local model requires
a later Product Owner decision after read-only feasibility evidence.

Policy changes invalidate activation and prepared snapshots. Narrowing and revocation take effect
immediately; broadening requires a new owner decision and activation. Per-turn approval cannot
override destination sensitivity eligibility or add denied tools, writes, endpoints, or operations.

## Consequences

- Ordinary remote turns remain inspectable and exactly bound without repetitive confirmation.
- Sensitive/mixed turns are local-only and unavailable until an exact feasible local profile is
  approved.
- Destination eligibility continues to precede retrieval under ADR-0015.
- The v0.5 gateway may contain deterministic mock, exact Gemini, and exact local Ollama adapters,
  but selection is deterministic policy evaluation, not fallback or model comparison.
- Session-only state, no streaming, read-only canonical sources, no tools/writes, and all citation,
  budget, redaction, privacy, and lifecycle contracts remain unchanged.

## Alternatives rejected

- Treat unknown as internal: rejected as implicit trust and declassification.
- Send sensitive content remotely after a warning or per-turn click: rejected because approval
  cannot override destination eligibility.
- Try local and fall back to Gemini: rejected as silent sensitive egress.
- Split one request by sensitivity: rejected because it obscures disclosure, evidence, and answer
  provenance.
- Persist a silent evergreen grant in v0.5: rejected pending a separate secure policy-store design.

## Required evidence

The acceptance matrix must prove pre-retrieval route selection, exact grant binding, tamper/expiry/
revocation handling, no wildcard or ambient routing, no remote fallback, local loopback/network
denial, cross-workspace isolation, unchanged immutable-snapshot/current-byte behavior, safe UX/JSON,
and complete Core/Voice/query/Project Resume regressions.

## Revisit conditions

Revisit persistent grants, context splitting, provider comparison, or remote treatment of higher
sensitivity only through a new Product Owner decision and ADR with equivalent privacy evidence.
