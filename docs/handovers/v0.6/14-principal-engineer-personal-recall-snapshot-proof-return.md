# Handoff 14 - Personal Recall temporary snapshot proof return

Date: 2026-09-23
Sender: Principal Engineer
Receiver: Chief of Staff
Task: `V06-PR-03`
Disposition: **BLOCKED - SNAPSHOT RETAINED; ABSENCE-CONTROL ACCEPTANCE FAILED**

## Outcome and decision boundary

[Verified] The approved private snapshot was created once, made read-only and independently verified against a closed 27-file inventory before the first benchmark. The existing 24-question manifest ran three times on the same snapshot. The completed proof did **not** pass: both negative controls and the one missing-answer control received source-backed citations, while the accepted gate requires no citation for these three questions. This is `benchmark:negative_control`, not a source-integrity, availability, privacy or network stop. The benchmark must not be described as accepted or activated.

[Verified] A second, diagnostic-only three-run pass over the **same unchanged retained snapshot** recovered private raw measurements that the initial failed proof had not retained. It reproduced the same gate failure. No new snapshot, live-vault proof retry, manifest edit, question rewording, source-scope expansion, Core edit or gate relaxation occurred. The first attempt record remains unchanged.

The remaining issue is a scope-changing benchmark/product decision: decide whether the three human-authored absence questions genuinely require zero citations under the accepted lexical contract, or whether a separately authorized design should handle fact-level absence despite lexical matches. Engineering cannot change the private manifest, Core retrieval behavior or accepted gate under Handoff 13. Do not delete the snapshot; cleanup requires later explicit authorization.

## Frozen identities and private snapshot

- Accepted Core commit: `429c1c37d6bf17aab02b2d741b11a72d01d9a430`; tree: `c08ccaf8044952299054fb0e2a41a788f8c325f0`. Core was not edited.
- Seven-file candidate canonical sorted path-to-file-SHA-256 JSON digest before task edits: `721ce3bb0c739fb14aa519274506e0db7fdcf2661b856baf0588e5e864aa5546`; final digest after in-task snapshot and failed-evidence corrections: `f862be10d65d7a835aa11cf4a4e70a359f46855d9e53dce28af3a19470181766`. The candidate remains uncommitted in `.worktrees/v0.6-pr01/`.
- Private manifest: 24 schema-valid questions in the fixed category counts; raw file SHA-256 `9d70850c5a2a0b746c506c70c4df90e0ba73c892a4e3554e48907c3b5a4decdc`; canonical parsed-manifest SHA-256 `54f5cea7eacebdcec9508843128f239de98eafb64927de4c78a6a965f5bb8f53`. The file was not changed.
- Retained private snapshot: `.worktrees/v0.6-pr01/data/v0.6-evidence/personal-recall/private/pr03/snapshot/`. It contains exactly 27 approved Markdown files totaling 32,190 bytes. Every snapshot file has the Windows read-only attribute. The canonical relative-path/length/content-hash projection SHA-256 is `baa147d7505d1eaf798203388aba4a0e4bce8b661935cce441c2938024a8cf4f`. The private full inventory file (also binding timestamps) SHA-256 is `e8cb54d9ec1fe1cabd348a0cc1845bb7a2ce64e838e633449e3171c3ea6ea75a`.
- Snapshot validation rejected path escapes, reparses, duplicates/case collisions, unsupported files and above-ceiling classifications in synthetic controls. The real closed-world post-proof verification found no extra, missing or changed file. One read-only current source-vault inventory after the proof had the same 27 relative-path/length/content-hash identities as the retained snapshot. Engineering issued no vault write operation.

## Three-run measurements and gates

| Check | Observed result |
|---|---|
| Initial inventory, acquisition, post-acquisition inventory, final inventory | Passed, 27 sources at every checkpoint |
| Three-run determinism | Passed; all private result rows identical across runs |
| Exact + metadata top-five recall | 10/10; accepted threshold at least 9 |
| Project + relationship top-five recall | 8/8; accepted threshold at least 6 |
| Paraphrase top-five recall | 3/3 |
| Negative and missing-answer controls | **Failed**: 3/3 had citation coverage, while all require `none` |
| Emitted citation fingerprint/locator validation | Passed for all returned citations; this does not make the absence answers correct |
| Parse/index duration | 38.168, 8.053 and 8.001 ms in the diagnostic pass |
| Query p95 | 4.666 ms, below the 500 ms ceiling |
| Peak measured memory | 1,889,605 bytes |
| Network/provider/persistent-index/legacy-memory activity | All zero; network/DNS/socket hooks were active during the proof |
| Source integrity | Passed before and after both proof passes |
| Overall acceptance | **Failed**; no successful aggregate packet was published |

The redacted failed aggregate carries fixed category counts, timings, hashes and the fixed failure category only. A privacy scan found no question text or expected source path in it. Private raw rows identify sources by inventory index and remain under the Git-ignored private evidence boundary.

## Evidence and verification

- Original private attempt: `.worktrees/v0.6-pr01/data/v0.6-evidence/personal-recall/private/pr03/benchmark-attempt-evidence.json`, SHA-256 `0aa9eb07757db05e4a105efe2add53e510e87b0b27afaf700d93802800104e53`. It records all checkpoints passing and three repetitions completing, but its first implementation collapsed the post-run gate into generic `snapshot:validation_failure`; the console fixed category was `benchmark:negative_control`.
- Private failed raw measurements: `.worktrees/v0.6-pr01/data/v0.6-evidence/personal-recall/private/pr03/benchmark-failed-results.json`, SHA-256 `e3f71fa800163f6acfbe296e4f7b9ac74fd072434170af68bad57cbbc3a4c7ee`.
- Redacted public failed aggregate: `.worktrees/v0.6-pr01/docs/evidence/v0.6/personal-recall-s0s1-snapshot-failed-aggregate.json`, SHA-256 `394b428d4334ff32c202ea1e3dc4188f8f05520ea5987cb7c4e4356f4627a601`. The expected successful public aggregate is absent.
- Initial one-shot proof command: `python scripts/personal_recall.py snapshot-proof --repo <candidate> --policy config/personal_recall_policy.v1.json --public docs/evidence/v0.6 --private data/v0.6-evidence/personal-recall/private --manifest data/v0.6-evidence/personal-recall/private/benchmark-manifest.json`; nonzero exit with `recall_failure=benchmark:negative_control`.
- Diagnostic-only command used the same arguments with `snapshot-diagnostic`; it verified the retained snapshot before and after, returned `snapshot_diagnostic=benchmark:negative_control`, and wrote the two exclusive failed-result files. It did not recreate the snapshot or use the vault as benchmark input.
- Final offline repository test command: root `.venv` Python `-m pytest -q` in the candidate; 826 passed, three documented environment skips. Ruff check of the seven candidate files passed. The new adversarial test ensures a failed negative gate retains three private runs without leaking a source path into public metrics.
- Active worklist validation passed. The baton, authority, handoff and evidence locators resolve; UTF-8 and trailing-whitespace checks passed; `git diff --check` passed in the governed and candidate repositories.
- No production, frontend, provider, credential, model, embedding, network, watcher, background service, persistent index, commit, merge or push. The retained snapshot awaits independent review and later governed cleanup; it was **not** deleted.

## Requested reviewer route

Independently verify the retained snapshot inventory, private/raw-to-public metric reconciliation, absence-control rows and privacy boundary. Decide the scope-changing treatment of the three absence questions and whether a new proof design/authority is warranted. Preserve the failed outcome and do not rerun or delete under the current authority.
