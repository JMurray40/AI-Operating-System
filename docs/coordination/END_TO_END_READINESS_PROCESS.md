# End-to-End Readiness Process

| Field | Value |
|---|---|
| Purpose | Discover the complete operational dependency chain before execution begins |
| Owner | Chief of Staff |
| Applies to | Jarvis and reusable future projects |
| Companion | [Version Worklist Process](WORKLIST_PROCESS.md) |

## The problem this prevents

A fail-closed stop is healthy when execution encounters an unexpected defect. Repeated stops for
missing software, privileges, media, human decisions, or environment capabilities are planning
failures. They indicate that the team validated only the next task instead of the complete route.

No execution task should begin until the project can answer, for the entire outcome:

1. Which environments are used?
2. Which exact software, versions, components, media, and services are required?
3. Which privileges and human-only actions are required?
4. Which network paths are allowed or forbidden?
5. Which evidence proves each stage?
6. What happens on every known failure?
7. Which retries are allowed?
8. How long should each wave take?
9. How does the earliest bootstrap failure produce a host-observable typed result?
10. Which internal failures are repaired autonomously within the same task?

## Readiness packet

Create a packet from [the reusable template](worklists/templates/readiness-packet.json) before
authorizing execution. CTO owns architecture and security requirements; Principal Engineering
probes feasibility and tool availability; Quality defines independently reproducible evidence;
Chief of Staff reconciles the whole packet; Product Owner accepts the cost, risks, human actions,
and authorization envelope.

The packet inventories environments; exact software and versions; sources, integrity, and
licenses; privileges; capacity; network controls; human actions; preflight checks; rollback;
evidence; privacy; fallbacks; retry budgets; and effort estimates.

`status` may become `ready` only when every prerequisite is proven and `unresolved` is empty. A
waiver requires an explicit Product Owner artifact; JSON cannot waive anything.

## Failure classification

| Class | Meaning | Response |
|---|---|---|
| `planning_gap` | Required fact, tool, privilege, or human route was not established | Return to readiness; do not create a correction loop |
| `environment_drift` | A previously proven environment fact changed | Re-run the affected readiness checks |
| `implementation_defect` | Authorized work behaved incorrectly despite green readiness | Return the bounded task for correction |
| `evidence_defect` | Result may be correct but cannot be independently proven | Correct evidence only when executable scope is unchanged |
| `external_change` | Vendor, platform, endpoint, law, or service changed | CTO re-evaluates the affected architecture assumption |
| `operator_stop` | Human reached an explicit stop boundary | Preserve state and follow the predeclared route |

A missing prerequisite discovered during execution is not treated as an Engineering defect.

An `implementation_defect` or `evidence_defect` does not normally end the owner's work turn. If
the repair is reversible, in scope, and covered by the retry budget, the owner corrects it and
continues to the review-ready outcome. “Fail closed” must not become “handoff on every failure.”

## Execution waves

Group tasks into outcome-sized waves instead of issuing a new Product Owner decision for every
handoff. A typical wave contains one operator task, one independent review, and automatic
Chief-of-Staff activation of the next covered task when evidence passes.

One Product Owner authorization envelope may cover several waves conditionally. It lists covered
task IDs, entry criteria, excluded actions, retry budget, and activation rule. Chief of Staff may
activate only the next task after its predecessor is accepted and its preflight remains green. A
new Product Owner decision is required only when scope, cost, privacy, network, credentials,
destructive action, external effect, or accepted risk changes.

Independent review remains mandatory where required; repetitive decisions between already
approved stages disappear.

## Worklist 1.2 execution and delivery contract

Schema 1.1 added top-level readiness and authorization envelopes plus a task `execution` object.
Schema 1.2 retains those controls and adds the outcome-sized delivery policy:

- wave and task kind;
- exact environment;
- required capabilities, software, privileges, and human actions;
- preflight checks;
- activation condition;
- pass and fail routes;
- retry policy; and
- active and elapsed-time estimate.
- one consolidated reviewer punch list;
- same-task handling of in-scope defects;
- explicit human-action routing;
- a correction-round ceiling followed by root-cause review; and
- the five permitted early-stop classes.

The validator rejects an active schema-1.1 or 1.2 execution task unless readiness is `ready`, and
rejects a schema-1.2 queue that omits or weakens the delivery policy. Earlier schemas remain
supported for retained queues; new projects should begin at 1.2.

## Readiness review procedure

1. Chief of Staff defines the complete outcome and environments.
2. CTO supplies architecture, security, vendor, and version requirements.
3. Principal Engineering runs one read-only host and tool inventory covering the full route.
4. Quality supplies the end-to-end evidence and reproducibility matrix.
5. Chief of Staff resolves contradictions, hidden human steps, and missing fallbacks.
6. The team runs one consolidated preflight; no mutation occurs.
7. Product Owner approves the readiness packet and authorization envelope.
8. Chief of Staff marks readiness `ready` and activates Wave 1.
9. Each accepted wave automatically routes to the next covered wave.
10. A planning gap pauses the envelope and returns here rather than creating ad hoc handoffs.

## Definition of ready

Execution is ready only when every prerequisite has an observed passing value; tools are installed
or their acquisition is an approved wave; privileges are proven under the real identity; human
actions have exact boundaries; network policies and environments are demonstrable; output paths,
rollback, cleanup, fallbacks, retry budgets, evidence, and effort are explicit.

## Adoption

For a new project, copy the worklist schema, validator, schema-1.2 worklist template, readiness
template, this document, and the Version Worklist Process. Complete readiness before implementation
or environment construction. Do not wait for execution to reveal the software stack.
