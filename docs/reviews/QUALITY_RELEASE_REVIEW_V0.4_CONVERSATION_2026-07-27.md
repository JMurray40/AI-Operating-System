# Quality & Release Review — v0.4 Conversation Candidate

| Field | Value |
|---|---|
| Role | Quality & Release Manager |
| Review date | 2026-07-27 |
| Candidate | Uncommitted workspace on `feature/v0.4-conversation` |
| Review type | Independent release readiness assessment |
| Disposition | **Not ready** |

## Executive disposition

The current conversation candidate is **not ready to merge or release**.

The implementation demonstrates useful session-only reference resolution and preserves
read-only fixture contents in the reviewed end-to-end scenario. The updated automated
suite and static checks pass. Those positive results do not satisfy the release gates for
a chat surface, however.

The candidate activates Architecture Review Board conditions C1 and C3 while leaving
both unresolved, lacks the required implementation report and acceptance evidence, has
material gaps in automated coverage, and emits an incorrect conversation turn number in
Trace Mode.

This disposition evaluates the workspace evidence observed on 2026-07-27. It is not an
assessment of intent or of any earlier architecture recommendation.

## Evidence executed

| Check | Result |
|---|---|
| Full automated suite | Pass — 156 tests in 75.15 seconds |
| Ruff | Pass |
| mypy | Pass — 51 source files |
| Two-turn CLI chat probe | Completed |
| Follow-up reference resolution | Demonstrated for “What is its status?” |
| Fixture SHA-256 comparison before/after chat | Unchanged |
| Real provider behavior | Not exercised; mock only |
| Conversation benchmark | Present but not executable as documented; import failure |
| Implementation report | Not present |

## Release blockers

### QR-01 — Retrieval relevance is presented as answer confidence

**Severity:** Blocking

`ConversationAnswer.confidence` is copied from the first citation's ranking confidence.
The CLI and JSON contract then display it as answer confidence. In the reviewed run, a
lexical match produced `"confidence": 1.0`, although the answer was only a retrieval
summary.

This is the ambiguity prohibited by v0.3 ARB condition C1, whose gate is a real provider
or conversational answer integration.

**Required:** Rename retrieval confidence to relative relevance throughout affected
contracts and UI. Define separate, non-probabilistic answer-confidence semantics, or omit
answer confidence until such semantics are approved.

### QR-02 — Citations do not meet the generated/conversational claim contract

**Severity:** Blocking

Conversation citations still contain only note identity, relative path, ranking value,
and ranking reason. They do not include a claim-supporting passage or section anchor,
excerpt, or source revision/fingerprint.

This leaves v0.3 ARB condition C3 unresolved at its conversational/generated-answer gate.

**Required:** Implement and test the approved passage/revision citation contract before
releasing a conversational answer surface, or explicitly re-scope the feature so it does
not claim generated evidence-backed answers.

### QR-03 — Trace Mode reports the wrong turn index

**Severity:** Blocking

The session records the first turn at index `0`, but Trace Mode reports it as turn `1`.
The second recorded turn is reported as turn `2`. Trace construction occurs after the
turn is recorded and uses the session count rather than the recorded turn's index.

**Required:** Use one documented indexing convention across CLI labels, stored turns,
JSON, and text traces. Add a regression test for the first and subsequent turns.

### QR-04 — Streaming acceptance is not demonstrated

**Severity:** Blocking if streaming remains in v0.4 scope

The CLI `--stream` option obtains a completed answer and then prints its words
incrementally. It does not use `ConversationManager.ask_stream()` or provider
`stream_summarize()`. The manager's stream method also calls the non-streaming `ask()`
before emitting deltas. This is progressive rendering, not provider-response streaming,
and cannot validate partial failure, cancellation, usage timing, or finalization rules.

**Required:** Either implement and test normalized streaming end to end, including
mid-stream failure behavior, or remove streaming from the release claim and defer it
explicitly.

### QR-05 — Required release evidence is incomplete

**Severity:** Blocking

The updated candidate includes conversation manager, CLI, stream-event, failure,
read-only, scale, session, and reference-resolution coverage. Important release-contract
gaps remain:

- Trace tests do not detect the off-by-one turn index demonstrated end to end.
- Streaming tests validate post-completion event chunking, not provider-response
  streaming, partial-response retention, or cancellation.
- No tests enforce the required relevance-versus-answer-confidence contract.
- No tests enforce passage anchors, excerpts, and source revision/fingerprint.
- Interactive command behavior and provider compatibility remain incomplete.

The handover also requires an implementation report, benchmark results, trust-contract
conformance review, and separate ARB disposition. The implementation report and v0.4
benchmark results were not present. `scripts/benchmark_conversation.py` failed with
`ModuleNotFoundError: No module named 'tests'` when executed directly from the repository
root using the project interpreter.

**Required:** Supply the standard implementation report and automated evidence for the
approved acceptance matrix. A passing legacy suite is necessary but not sufficient.

## Non-blocking observations

- The candidate remained read-only in the reviewed two-turn fixture run.
- Session-only state and deterministic most-recent-entity resolution are reasonable
  foundations.
- Existing v0.1–v0.3 checks remained green in this workspace snapshot.
- Product and release naming are inconsistent: the handover recommends v0.4 as Project
  Resume and v0.5 as visible-context chat, while the branch calls conversation work v0.4.
  The Product Owner must confirm the release identity before closure.
- The source package contains generated `__pycache__` artifacts locally. They were not
  shown as Git candidates, but release packaging should continue to exclude them.

## Required re-review package

Submit all of the following together:

1. Product Owner confirmation of release identity and approved scope.
2. Implementation report with changed contracts, compatibility, security analysis,
   deviations, technical debt, and rollback approach.
3. Resolution or approved deferral of ARB conditions C1 and C3.
4. Fix and regression test for Trace Mode turn numbering.
5. Streaming implementation evidence or explicit removal from scope.
6. Automated positive, negative, boundary, compatibility, failure, CLI, read-only, and
   regression tests for the conversation layer.
7. Executed benchmark results and an unchanged-vault assertion.
8. Separate Architecture Review Board disposition.

After these items are available, Quality & Release should rerun the complete suite,
static checks, benchmark, CLI acceptance scenarios, contract review, and vault-integrity
checks before issuing a new disposition.

## Final recommendation to the Product Owner

Do not merge or release this candidate in its current state. Return it to engineering
for completion against the approved trust contracts and release evidence. Preserve the
read-only, session-only design while correcting the contract, trace, streaming, and test
gaps above.
