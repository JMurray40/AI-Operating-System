# Handoff 13 - Personal Recall temporary snapshot proof authorization

Date: 2026-09-23
Sender: Chief of Staff
Receiver: Principal Engineer
Task: `V06-PR-03`
Disposition: **AUTHORIZED - ONE CONSOLIDATED PRIVATE SNAPSHOT PROOF CYCLE**

## Authority

[Verified] The Product Owner approved the recommended route in Handoff 12: a temporary, private, hash-bound snapshot of the already approved Personal Recall source scope.

[Verified] `V06-PR-01` remains terminally blocked under its live-vault proof authority. This authorization does not revive or retry that design.

## Required complete outcome

Return one review-ready package that completes all of the following in one task:

1. Reverify the accepted Core identity and seven-file candidate digest from Handoff 11.
2. Reverify the existing private 24-question manifest without exposing its content.
3. Create one temporary snapshot containing only eligible Markdown files from the five approved folders under `C:\Users\jmurr\The BRAIN`.
4. Store the snapshot outside Git within the governed private evidence boundary.
5. Reject path escapes, reparse points, duplicates, case collisions, unsupported files, classification-policy failures and any source above the approved `private` sensitivity ceiling.
6. Produce a canonical inventory binding each included relative path, byte length and SHA-256 digest; do not place paths, note content or questions in public evidence.
7. Mark the snapshot read-only and independently verify that its complete inventory exactly matches the canonical inventory before benchmark execution.
8. Run the existing 24-question lexical benchmark three times against that same immutable snapshot and candidate.
9. Verify answer correctness, missing-answer behavior, source-backed citations, three-run determinism, performance, privacy and absence of writes/network/provider activity using the previously accepted gates.
10. Produce private raw evidence and one redacted public aggregate packet with exact hashes.
11. Return one consolidated Handoff 14 for independent Chief-of-Staff review.
12. Retain the snapshot unchanged until review. Do not delete it during Engineering execution; cleanup requires a separate explicit Chief-of-Staff authorization after evidence acceptance.

## Correction and stop policy

Ordinary defects in snapshot construction, validation, benchmark orchestration or evidence generation must be diagnosed, corrected and retested inside `V06-PR-03`. They do not justify separate handoffs.

Stop early only for:

- required human action;
- missing authority;
- an unsafe or irreversible action;
- an unavailable external capability; or
- a scope-changing architecture or privacy decision.

If an early stop is required, report the root cause, completed diagnosis and one concrete next route. Do not request serial permission for internal implementation details.

## Boundaries

- Snapshot creation is a private, temporary copy operation; the source vault remains read-only.
- No persistent search index, embedding, durable memory, provider, credential, network access, watcher, background service, legacy-memory function or frontend activation.
- No broader folder scope or file type.
- No weakening, rebasing or silently updating snapshot identity after the benchmark starts.
- No public disclosure of note paths, titles, content, questions, expected answers or private error text.
- No snapshot deletion until separately authorized after independent review.
- No commit, merge or push is required unless a source correction is actually necessary and separately permitted by the existing candidate boundary.

## Return statement

The return must state the snapshot inventory count and digest; candidate and manifest identities; all commands and results; three-run outcome; citation, determinism, performance, privacy and no-effects results; private/public evidence paths and hashes; any in-task corrections; remaining limitations; and confirmation that the source vault was not modified and the retained snapshot awaits governed cleanup.
