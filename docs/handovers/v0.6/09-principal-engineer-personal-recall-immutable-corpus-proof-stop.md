# Handoff 09 - Personal Recall immutable-corpus proof stop

Date: 2026-09-23
Sender: Principal Engineer
Receiver: Chief of Staff
Task: `V06-PR-01`
Disposition: **BLOCKED - HANDOFF 08 PROOF ATTEMPT CONSUMED**

## Outcome

[Verified] Engineering implemented the bounded Handoff 08 correction in the isolated native-Windows candidate, completed the synthetic and accepted-Core gates, and made exactly one real-vault proof invocation. That invocation returned the fixed safe category `source_integrity_failure`. It wrote neither `benchmark-results.json` nor the public aggregate packet. It was not retried. The three-run determinism, recall, citation and performance gates therefore remain unproven.

[Verified] A single read-only diagnostic inventory after the failure matched the governed v2 baseline exactly: 27 paths, no additions/removals, and no size, nanosecond-timestamp or SHA-256 difference. This does not invalidate the fail-closed result. The current implementation uses the same fixed category at the initial inventory, immediately post-acquisition inventory and final post-run inventory; the retained output does not identify which checkpoint failed. Engineering does not claim that no question ran, or that the source was stable throughout the attempt.

## Candidate and completed correction

- Accepted Core base: commit `429c1c37d6bf17aab02b2d741b11a72d01d9a430`, tree `c08ccaf8044952299054fb0e2a41a788f8c325f0`; Core source was not edited.
- Isolated candidate: `.worktrees/v0.6-pr01/`, seven source/config/test files; sorted repository-relative path-to-file-SHA-256 JSON canonical digest `2c4bfd42702f14aa1cb26fecde88fcc6e009a0ea20407cc0cc7fc9ac7e0a4f27`. No candidate file changed after full tests and before or after the proof invocation.
- The adapter performs an initial full governed inventory, acquires each authorized source once through the existing path/reparse/metadata/size/timestamp/SHA-256 checks, immediately takes another full live inventory, parses one in-memory corpus, and runs three query/index repetitions over those same immutable source bytes and Note objects. Core's citation factory is rebound only inside this adapter to a read-only resolver over the acquired byte map. Material citations are independently validated against those bytes. A final full live inventory precedes any result publication. All three inventory passes necessarily read source bytes to prove current hashes; the *one-open* rule applies to corpus acquisition and excludes these separately required integrity inventories.
- New private-result rows use numeric inventory indices and locator digests rather than source paths, IDs, excerpts or note text. The CLI emits fixed safe failure categories without raw exception text. No raw source bytes or parsed note content is persisted by the correction. Existing governed private baseline and human manifest remain preserved and unchanged.

## Verification and preserved evidence

- Synthetic tests cover one acquisition per source, identical Note object ordering across all three repetitions, no live citation reopen, mutations before/during acquisition and at both inventory boundaries, prior policy/reparse/privacy/network/citation controls, and public/private result redaction. Full repository result: 807 passed, three documented environment skips. Ruff passed on all seven candidate files.
- Immediately before the proof, policy resolution found exactly five approved roots, the 27-source live inventory matched the v2 baseline, the complete private manifest validated, and both result files were absent.
- Private manifest SHA-256: `9d70850c5a2a0b746c506c70c4df90e0ba73c892a4e3554e48907c3b5a4decdc`. Governed v2 baseline SHA-256: `6406d6a5289e6f6016e38b7e2aa38ca64b4499f30449cb55022ad88397a0cb41`.
- Both earlier stopped attempts and the private baseline/manifest remain in the existing Git-ignored evidence directory. No private question, filename, note text, answer, citation or vault path is reproduced here. No commit, merge, push, frontend activation, provider, model, embedding, credential, network download, persistent index or vault write occurred.

## Boundary and route

Handoff 08 requires a stop if either inventory check fails and authorizes only one complete proof attempt. That attempt is consumed; Engineering must not rerun or reinterpret the matching later diagnostic inventory as a pass. The checkpoint ambiguity is a typed-observability gap for separate review, not permission for another test. A further attempt, checkpoint-specific diagnostic change, or altered source-integrity design requires Chief-of-Staff disposition under the governing process. Product Owner action: none requested now.
