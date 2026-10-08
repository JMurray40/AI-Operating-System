# ADR-0022: Conversation Is a Session-Only Application Layer

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-08-01 |
| Deciders | Product Owner, advised by Chief Architect / CTO |
| Related | ADR-0007, ADR-0010, ADR-0012, ADR-0014 through ADR-0017, v0.5 planning package |

## Context

Visible-context conversation needs cross-turn state without turning a transcript into
durable knowledge or coupling mutable state to the deterministic query pipeline. The draft
Chat PRD asks for a durable operational conversation store, while the parked historical
candidate used process-local state. Neither choice has been approved for v0.5.

## Proposed decision

v0.5 conversation is a separate application layer composed over the released query and
evidence services. It does not modify the ADR-0012 pipeline.

Conversation state is process-local and session-only. It contains user turns, provider
responses, explicit context choices, immutable request snapshots, visible reference
resolution, usage, and redacted diagnostics. It is destroyed when the process exits or the
user resets the session. It is not written to the vault, an operational database, logs, or
provider-managed memory.

The supported surfaces are:

1. an interactive and scripted CLI; and
2. a versioned in-process application API used by that CLI and tests.

No HTTP service or graphical interface is part of v0.5. A future persistent conversation
store requires a new decision covering encryption keys, retention, archive, search, export,
deletion, backup residuals, migration, and subject access. Durable memory remains governed
by ADR-0009 and cannot be created implicitly from a session.

## Consequences

- v0.5 can deliver multi-turn visible context without introducing a new durable private-data
  store or vault write authority.
- Conversation resume across processes, archive, search, export, deletion workflows, and
  branch history are deferred.
- A crash loses the session. This is an accepted limitation, not silent persistence.
- The application API remains a seam for a later UI or operational store.
- Historical conversation data has no migration path because no released conversation
  contract or canonical data exists.

## Alternatives rejected for v0.5

- Persist transcripts now: rejected because encryption, retention, deletion, recovery, and
  migration would materially expand the release trust boundary.
- Store transcripts in the vault: rejected because it violates the read-only release
  boundary and confuses operational conversation with durable knowledge.
- Put session state in `QueryEngine`: rejected because it couples mutable application state
  to the deterministic retrieval core.

## Revisit conditions

Revisit only after the Product Owner authorizes durable conversation lifecycle work or a
first-party UI requires a process-independent session boundary.
