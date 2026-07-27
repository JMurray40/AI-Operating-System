# PRD: Agent Framework

| Field | Value |
|---|---|
| Status | Draft |
| Target | v0.8 |
| Owner | Platform/AI |
| Depends on | Provider gateway, tool policy, context planner, workflow runtime, evaluation harness |

## Problem statement

Specialized tasks benefit from different instructions, context, tools, and outputs. Ad hoc “agents” implemented as prompts with broad access create inconsistent behavior, recursive delegation, unclear responsibility, and uncontrolled cost.

## Goals

- Define agents as versioned, bounded task configurations.
- Enforce budgets, capabilities, context, output contracts, and human checkpoints.
- Support delegation without losing accountability.
- Evaluate behavior independently of model provider.

## User stories

- Select an appropriate specialist and see its plan, sources, permissions, and budget.
- Approve a proposed consequential action at the point of use.
- Cancel a task and all delegated work.
- Inspect artifacts, reasoning summaries, failures, and cost.
- Compare agent versions on a benchmark.

## Functional requirements

1. Agent manifest defines identity, version, purpose, accepted task schema, output schema, context policy, tool capabilities, model-role preference, budgets, and escalation rules.
2. Every run creates an immutable task record and context snapshot.
3. Support plan, execute, observe, checkpoint, complete/fail/cancel states.
4. Enforce token, cost, time, tool-call, concurrency, and delegation-depth budgets below the model.
5. Delegation passes least-privilege sub-capabilities and records parent/child lineage.
6. Agents exchange typed artifacts, not shared mutable scratch memory.
7. Tool calls pass through the same gateway as direct user workflows.
8. Require human checkpoint for high-risk actions, ambiguity, policy conflict, or budget increase.
9. Provide replay in dry-run/mock mode and versioned evaluation suites.
10. Prevent an agent from modifying its own manifest or grants.

## Non-functional requirements

- Provider-neutral execution semantics.
- Cancellation p95 reaches active workers within five seconds.
- Complete audit lineage from user task to every child action.
- Deterministic orchestration for mocked provider/tool responses.
- Agent failure cannot corrupt canonical knowledge or other tasks.

## Architecture considerations

Use one workflow runtime for agents and automation. “Agent” adds reasoning/policy configuration; it is not a separate process topology. Keep orchestration state in the operational DB and accepted artifacts in canonical systems. Supervisors coordinate but cannot override the Policy Decision Point.

## Edge cases

Circular delegation; conflicting agent recommendations; partial child failure; provider context-window exhaustion; tool output injection; cancelled external side effect; stale approval; agent version changes mid-run; unavailable specialist.

## Acceptance criteria

- Eight reference profiles validate against the manifest schema.
- Recursion, budget, cancellation, and least-privilege tests pass.
- Every consequential tool call has an attributable grant/approval.
- Benchmark results compare agent/provider versions without changing fixtures.
- Failed run leaves canonical sources unchanged unless an approved idempotent action completed and is logged.

## Future enhancements

Team-owned agents, learned routing, agent marketplace, long-running cases, distributed workers, formal policy proofs, and simulation environments.
