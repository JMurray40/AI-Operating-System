# PRD: Automation Engine

| Field | Value |
|---|---|
| Status | Draft |
| Target | v0.9 |
| Owner | Platform/Automation |
| Depends on | Durable workflow runtime, event schema, policy, tools/plugins, operational DB |

## Problem statement

Repeated tasks are valuable to automate, but background execution magnifies stale context, duplicate effects, privacy violations, and hard-to-debug failures. Users need durable, observable workflows where triggers never weaken permission requirements.

## Goals

- Run deterministic and AI-assisted workflows reliably across restarts.
- Make triggers, conditions, approvals, effects, retries, and outputs visible.
- Guarantee bounded execution and idempotency where possible.
- Begin with read-only and proposal workflows.

## User stories

- Schedule a morning briefing without granting write access.
- Trigger an inbox classification proposal when a note appears.
- Approve a workflow step from one review queue.
- Pause, retry, cancel, or replay a failed run.
- Know what ran, why, what it changed, and how to recover.

## Functional requirements

1. Versioned workflow definition with trigger, inputs, steps, branches, approvals, compensation, budgets, and outputs.
2. Manual, schedule, file event, webhook, and system event triggers.
3. Durable execution state and step-level idempotency keys.
4. Typed steps: query, transform, agent, tool, approval, delay, emit, and compensation.
5. Validate workflow and capability grants before activation.
6. Re-evaluate policy at execution time and before each effect.
7. Retry with bounded backoff; dead-letter unresolved failures.
8. Concurrency controls, deduplication windows, pause/disable, and maintenance mode.
9. Timeline UI with inputs, outputs, approvals, costs, and effects.
10. Dry-run using mock providers/tools and snapshot inputs.

## Non-functional requirements

- Restart-safe; no duplicate committed external effect after recovery.
- Clock/time-zone/DST behavior explicitly tested.
- Complete audit and metrics without logging secrets.
- Backpressure protects the system from event storms.
- Workflow version is immutable for an active run.

## Architecture considerations

Adopt an append-oriented execution/event model in the operational store, not note files. Use the same Tool Gateway and Agent Runtime. “Exactly once” is not generally achievable across external APIs; use idempotency tokens, effect receipts, reconciliation, and compensation.

## Edge cases

DST repeats/skips; webhook replay; file save storms; approval expires; credential revoked mid-run; partial external success; workflow edited during run; offline machine; runaway recurrence; compensation fails.

## Acceptance criteria

- Reference workflows survive forced termination at every step boundary.
- Duplicate trigger tests produce one logical run/effect.
- Schedules never bypass approval.
- Dead-letter items are actionable and replay preserves lineage.
- Dry-run causes no external or canonical write effects.

## Future enhancements

Visual builder, reusable subflows, distributed workers, SLA policies, workflow marketplace, event replay laboratory, and enterprise approval routing.
