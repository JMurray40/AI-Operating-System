# PRD: Chat Interface

| Field | Value |
|---|---|
| Status | Draft | 
| Target | v0.3 |
| Owner | Product |
| Depends on | Search, provider gateway, operational conversation store, egress policy |

## Problem statement

AI conversations currently lose project context, hide what was sent to providers, and fragment history across vendors. Users need one trustworthy conversational surface that assembles authorized knowledge, exposes sources, and remains useful when providers change.

## Goals

- Provide project-aware streaming chat over interchangeable providers.
- Make context, provenance, sensitivity, cost, and model role visible.
- Preserve conversation state operationally without treating transcripts as durable knowledge.
- Maintain read-only vault behavior through v0.3.

## Non-goals

Tool execution, autonomous agents, silent memory writes, unrestricted web browsing, and perfect cross-provider response equivalence.

## User stories

- As a user, I can start from a project dashboard so the conversation receives relevant context.
- I can inspect and remove context items before sending.
- I can switch provider/model role and understand privacy/cost implications.
- I can open the source behind an answer.
- I can turn a useful outcome into a memory proposal later without saving the entire transcript.

## Functional requirements

1. Create, title, archive, export, and search conversations.
2. Support text input, Markdown output, code blocks, attachments by reference, stop/regenerate, and streaming.
3. Require a selected workspace; project is optional but explicit.
4. Display a context drawer containing source title, locator, reason selected, sensitivity, token estimate, and exclusion control.
5. Display provider, model role, latency, estimated cost, and request status.
6. Render citations linked to immutable source revision/locator; distinguish model knowledge from retrieved evidence.
7. Persist messages, provider metadata, context manifest, and user feedback in the operational store.
8. Enforce provider egress policy before dispatch; explain blocked content.
9. Treat retrieved text and attachments as untrusted data, not system instructions.
10. Offer retry with same context snapshot and branch-from-message.
11. Provide keyboard navigation, accessible streaming announcements, and reduced-motion behavior.
12. Never mutate the vault in this release.

## Non-functional requirements

- First visible token p95 under 2.5 seconds excluding provider delay; UI input remains responsive.
- Conversation metadata encryptable at rest; transport encrypted.
- Provider timeout, cancellation, and retry do not duplicate messages.
- No cross-workspace context contamination.
- Structured logs redact message content by default.
- WCAG 2.2 AA target.

## Architecture considerations

Use an application API rather than coupling UI to providers. A versioned `ChatRequest` references a context snapshot, provider role, conversation branch, and policy decision. Stream normalized events (`started`, `delta`, `citation`, `usage`, `completed`, `failed`) so first-party clients share behavior. Keep raw provider payloads behind adapters and bounded retention.

## Edge cases

- Source changes after context assembly: cite snapshot revision and show staleness.
- Provider fails mid-stream: retain partial response as failed, not completed.
- Citation points to removed content: show unavailable provenance, never retarget silently.
- Context exceeds limit: explain ranking/truncation and allow user control.
- User pastes an instruction claiming higher privilege: it remains user content.
- Offline/local model unavailable: show actionable status without losing the draft.

## Acceptance criteria

- Two provider adapters pass the same contract suite, one may be mock/local.
- Every retrieved claim citation resolves to the exact source revision.
- Security tests prove disallowed sensitivity never reaches a cloud adapter.
- Identical retry uses the same context manifest.
- Vault hash is unchanged after full chat tests.
- Usability test participants can inspect context and switch providers without instruction.

## Future enhancements

Multimodal messages, shared conversations, voice, tool proposals, memory proposal workflow, compare-provider view, and reusable conversation branches.
