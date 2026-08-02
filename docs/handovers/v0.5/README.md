# v0.5 Visible-Context Conversation Handoff Index

## Current state

**Milestone:** v0.5 — visible-context conversation

**Phase:** Principal Engineering implementation — WP1–WP3 only

**Implementation:** WP1–WP3 authorized under Handoff 08; WP2–WP3 paused pending Handoff 08a WP1 correction; WP4 unauthorized

**Current incoming artifact:**
[CTO WP1 architecture clarification](08a-cto-to-principal-engineer-wp1-architecture-clarification.md)

## Released prerequisites

- v0.3.1 Query Trust Contracts: released as `v0.3.1`.
- v0.4 Project Resume: released as `v0.4.0`.
- v0.4 repository closeout: validated at
  `0fda11812144e758f7fc11462a8bdf70ccdff9ec`.

## Historical candidate

The repository retains historical branch `feature/v0.4-conversation` at
`4b09050b76fd9a448af3ce91b4aa66963d23dad2`. It predates the approved release sequence
and must not be merged, renamed, rebased, or treated as a v0.5 implementation candidate
during planning.

Its historical Quality review is
[Not ready](../../reviews/QUALITY_RELEASE_REVIEW_V0.4_CONVERSATION_2026-07-27.md).

## Approved sequence and scope

- v0.5: Visible-Context Conversation.
- v0.6: Proposed Memory.
- v0.7: Semantic Search and Relationship Intelligence.
- CLI plus versioned in-process API, session-only state, one approved real provider plus
  deterministic mock, and per-turn visible-context approval.
- No streaming, durable transcripts, tools, agents, MCP, plugins, UI, public server,
  semantic retrieval, provider fallback, live connectors, or vault writes.

ADR-0022 through ADR-0024 are accepted. Google `gemini-3.5-flash-lite` is the approved
v0.5 real-provider target under the limits in Handoff 06. Ollama is deferred beyond v0.5.
Credentials, calls, and spending remain unauthorized until later exact gates.

## Required next handoff

Principal Engineering must complete the bounded WP1 correction in Handoff 08a, then
implement only WP2–WP3 from the exact base/worktree in Handoff 08 and produce
`09-principal-engineer-to-cto-conversation-engineering-review.md`. WP4 and all live-provider
activity remain separately blocked.
