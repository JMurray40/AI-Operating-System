# PRD: Memory System

| Field | Value |
|---|---|
| Status | Draft |
| Target | v0.5 |
| Owner | Product/Knowledge |
| Depends on | Atomic writes, schema compatibility, backup/rollback, identity, approval UI |

## Problem statement

Provider memory and chat history are fragmented and opaque. Automatically saving everything creates noise and risk. Users need a deliberate promotion process that turns useful outcomes into durable, portable knowledge while preventing duplicates, contradictions, and silent edits.

## Goals

- Separate conversation, working, durable, and derived memory.
- Propose—not silently perform—durable knowledge changes.
- Preserve provenance, history, and rollback.
- Make retrieval and forgetting predictable across providers.

## Memory classes

| Class | Owner | Retention |
|---|---|---|
| Conversation | Operational DB | Configurable |
| Task working state | Workflow runtime | Until completion/expiry |
| Durable knowledge | Vault | Until superseded/archived |
| Preferences | Settings/approved vault profile | Explicit |
| Search memory | Rebuildable index | Rebuildable |
| Provider-native memory | Provider | Optional, never canonical |

## User stories

- Review a session summary and exact changes before saving.
- Accept a new decision separately from a project update.
- See possible duplicates or conflicts before creating a note.
- Correct or forget durable facts and understand downstream effects.
- Know which source and session created a memory.

## Functional requirements

1. Extract typed candidates: session summary, decision, preference, project update, concept, research, task, and relationship.
2. Validate candidates against schemas and controlled vocabulary.
3. Search for existing identity, semantic duplicates, and conflicts.
4. Present create/update/link/supersede/skip choices with before/after diff and confidence rationale.
5. Require explicit approval per candidate or approved batch.
6. Verify expected pre-write hash, write atomically, validate, and log result.
7. Support rollback and supersession without erasing history.
8. Track provenance: task, conversation, provider, model role, sources, approver, timestamps, revisions.
9. Implement retention and deletion for operational transcripts independently from durable notes.
10. Allow provider memory opt-out and export.

## Non-functional requirements

- Zero silent durable writes.
- Crash-safe write transaction and tested restoration.
- Idempotent candidate acceptance.
- Duplicate rate and correction rate measured.
- Sensitive fields redacted before provider egress.
- Human-readable output remains valid without Jarvis.

## Architecture considerations

Use a `MemoryCandidate` envelope distinct from a vault note. Promotion is a policy-controlled command producing an append-only audit event and a source revision. Avoid a generalized “memory database” that competes with the vault. Preferences that must be machine-fast still require an explicit canonical ownership decision.

## Edge cases

Concurrent edits; renamed targets; conflicting accepted decisions; candidate based on hallucination; partial approval; private source summarized into less-restricted note; forgotten content lingering in indexes/backups/provider memory; multiple sessions proposing the same update.

## Acceptance criteria

- Every write requires an approved candidate and matching pre-write revision.
- Injected source text cannot cause unreviewed memory creation.
- Duplicate acceptance is idempotent.
- Rollback restores content and link integrity.
- Deletion/forget workflow removes active projections and documents unavoidable backup retention.
- Pilot users accept ≥70% of high-confidence candidates with <5% later correction.

## Future enhancements

Team review, confidence calibration, automated low-risk formatting fixes, knowledge decay reviews, personal preference portability, and cryptographic provenance.
