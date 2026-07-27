# AI Behavior Standard

| Field | Value |
|---|---|
| Purpose | Govern human-supervised AI work across the project and vault |
| Status | Draft |
| Version | 0.1.0 |
| Owner | Jason |
| Revised | 2026-07-27 |
| Related | [Development Guide](DEVELOPMENT_GUIDE.md), [Knowledge Standard](KNOWLEDGE_STANDARD.md), [The BRAIN v2 §11–16](THE_BRAIN_V2_SPEC.md) |

## Applicability

This standard applies to Claude Code, ChatGPT, Gemini, Ollama, Jarvis agents, and future AI clients.

## Startup procedure

Before meaningful work, an AI must:

1. read repository instructions and relevant ADRs;
2. read the product or milestone document governing the task;
3. read `VAULT-INDEX.md` when vault context is authorized;
4. read the relevant project dashboard, active decisions, and recent sessions;
5. determine the authoritative location of affected artifacts;
6. limit context to what the task requires; and
7. state material assumptions.

## Memory rules

- Obsidian is the durable knowledge layer.
- Provider memory and `MEMORY.md` are pointers, not competing stores.
- Operational conversation history belongs outside the vault.
- Raw transcripts are retained only when justified.
- Secrets are never written to prompts, the vault, repository, or logs.

## Write behavior

AI-generated content must:

- use canonical templates and controlled vocabulary;
- preserve IDs and provenance;
- distinguish fact, inference, proposal, and decision;
- prefer references over duplicate assets;
- update only files within the approved scope;
- preserve meaningful history; and
- remain concise enough for future retrieval.

## Session closeout

A meaningful session produces or proposes:

- objective;
- work completed;
- decisions made or proposed;
- files, resources, issues, and commits involved;
- problems and resolutions;
- open questions and next actions;
- related notes and cross-project connections; and
- an update to the project's **Resume here** section.

Use [Session Summary](../templates/session-summary.md).

## Decision creation

Create a decision candidate when a choice constrains future work, changes system boundaries, adopts technology, or resolves a material tradeoff. Human approval determines whether it becomes accepted. Do not bury durable decisions only in session notes.

## Approval requirements

Explicit approval is required before:

- moving, renaming, merging, archiving, or deleting knowledge;
- bulk metadata changes;
- rewriting accepted decisions;
- exposing private or restricted data to a cloud provider;
- external writes, messages, installations, or destructive actions;
- changing permissions, schemas, or security boundaries; and
- publishing AI-generated changes.

Read-only analysis within approved scope is allowed.

## Safety

- Use least privilege and approved roots.
- Show the exact target and intended change.
- Prefer atomic and recoverable writes.
- Validate after changes.
- Record consequential actions in an audit trail.
- Treat semantic similarity as a suggestion.
- Stop when authority or target scope is ambiguous.

## Review requirements

AI-generated changes require human review proportional to risk. Architecture, security, schema, migration, and automation changes require explicit approval regardless of test results.

## Revision history

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-07-27 | Initial cross-provider behavior standard |
