# Handoff 00 — Chief of Staff to CTO

| Field | Value |
|---|---|
| Sender | Chief of Staff |
| Receiver | Chief Architect / CTO |
| Milestone | v0.3.1 — Query Trust Contracts |
| Date | 2026-07-27 |
| Status | Ready for CTO action |
| Repository | `JMurray40/AI-Operating-System` |
| Observed branch | `feature/v0.4-conversation` |
| Observed workspace HEAD | `4b09050b76fd9a448af3ce91b4aa66963d23dad2` |
| Required output | Superseded by Product Owner approval handoff; CTO output is now `docs/handovers/v0.3.1/02-cto-to-principal-engineer-implementation-brief.md` |

## Product Owner direction

Complete v0.3.1 before proceeding with the completed-but-unapproved conversation candidate.
The conversation work may be reviewed for dependency and compatibility information, but it
must remain parked and must not be merged or released during this stage.

## CTO objective

Convert the proposed v0.3.1 requirements into an implementation-ready, governance-compliant
brief for the Principal Engineer. Resolve architectural ambiguity before engineering begins.

Primary question:

> Is this the right architecture?

## Authoritative inputs

Read these from the repository; conversation history is not authoritative.

1. [Governance](../../GOVERNANCE.md)
2. Accepted ADRs, especially
   [ADR-0007](../../adr/ADR-0007-Read-Only-Is-The-Default-Operating-Mode.md),
   [ADR-0012](../../adr/ADR-0012-Query-Engine-Is-A-Layered-Deterministic-Pipeline.md),
   [ADR-0014](../../adr/ADR-0014-Retrieval-Relevance-Is-Separate-From-Answer-Confidence.md),
   [ADR-0015](../../adr/ADR-0015-Authorization-Precedes-Retrieval-And-Graph-Expansion.md),
   [ADR-0016](../../adr/ADR-0016-Citations-Bind-Passages-To-Source-Revisions.md), and
   [ADR-0017](../../adr/ADR-0017-Stable-Source-Identity-Is-Separate-From-Location.md).
3. [v0.3.1 requirements](../../software/V0.3.1_QUERY_TRUST_CONTRACTS_REQUIREMENTS.md)
4. [v0.3 ARB review](../../reviews/arb/2026-07-27-v0.3-architecture-review.md)
5. [Ways of Working](../../WAYS_OF_WORKING.md)
6. [Project turnover](../2026-07-27-JARVIS-PROJECT-TURNOVER.md)
7. Relevant source, tests, and the parked
   [conversation implementation report](../../software/V0.4_IMPLEMENTATION_REPORT.md)
   only where they expose dependency or compatibility impact.

If any artifact conflicts, apply the Governance order of precedence and escalate any
unresolved decision to the Product Owner. Do not silently reconcile conflicts.

## Required work

1. Confirm whether ADR-0014 through ADR-0017 are accepted, proposed, or require Product
   Owner/ARB action before they can constrain implementation.
2. Reconcile the v0.3.1 requirements with the accepted roadmap and release naming.
3. Identify the correct engineering base:
   - inspect the repository and active worktree;
   - do not assume the current conversation branch is the correct base;
   - do not switch branches, merge, stash, stage, or alter the Principal Engineer's work;
   - name the required base branch and exact commit SHA in the brief.
4. Map every v0.3.1 requirement to concrete acceptance criteria and required evidence.
5. Identify public contract changes, compatibility boundaries, migration behavior, security
   gates, performance thresholds, and documentation impacts.
6. Define how the parked conversation candidate will be handled after v0.3.1 without
   importing conversational scope into this release.
7. Record every decision that still requires Product Owner approval.

## Required implementation-brief contents

The outgoing brief must contain every item required by the
[Implementation Brief Contract](../../WAYS_OF_WORKING.md#implementation-brief-contract):

- repository;
- base branch;
- exact base commit SHA;
- milestone;
- related PRDs;
- related ADRs and their status;
- acceptance criteria;
- out-of-scope items;
- Definition of Done;
- performance targets and test sizes;
- testing expectations;
- documentation expectations;
- known risks.

Also include:

- requirement-to-test/evidence matrix;
- affected contracts and compatibility plan;
- explicit authorization and non-disclosure invariants;
- citation locator/fingerprint validation cases;
- unchanged-vault evidence method;
- commands/checks the Engineer must report;
- required engineering handoff path:
   `docs/handovers/v0.3.1/03-principal-engineer-to-cto-engineering-review.md`.

## Explicitly out of scope

- Conversational or chat feature implementation.
- Real AI providers.
- Embeddings or vector databases.
- Durable memory or conversation persistence.
- Plugins, MCP, agents, automation, or background services.
- Vault writes.
- Merging or releasing the parked conversation candidate.
- Silent roadmap or release-number changes.

## Exit criteria

This handoff is complete only when:

1. the CTO has produced the required brief at the specified path;
2. the brief is internally consistent with accepted higher-precedence artifacts;
3. unresolved Product Owner decisions are explicit;
4. the Chief of Staff can validate the brief without reconstructing context from chat;
5. the Principal Engineer can execute it without making product or architecture decisions.

## Exit statement

**Ready for CTO action.** Engineering remains blocked until the CTO brief is complete,
Chief of Staff validation is recorded, and the Product Owner approves any material open
decisions.
