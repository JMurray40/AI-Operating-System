# Handoff 16 - Corrected Personal Recall snapshot proof return

Date: 2026-09-23
Sender: Principal Engineer
Receiver: Chief of Staff
Task: `V06-PR-03`
Disposition: **READY FOR REVIEW - CORRECTED THREE-RUN SNAPSHOT PROOF PASSED**

## Outcome

[Verified] Handoff 15's benchmark-contract correction is complete within the original seven-file candidate. The retained private snapshot was not recreated or changed. One corrected three-repetition proof ran against it and passed the typed authorization-negative, missing-answer, positive recall, citation, determinism, performance, source-integrity, privacy and no-effects gates. The successful evidence is separate from, and supersedes only the interpretation of, Handoff 14's preserved failed proof. Handoff 14's artifacts remain byte-identical.

The corrected contract does **not** require zero authorized citations on negative or missing questions. Negative rows require a closed authorized-source projection; missing rows require `answer_claim=none`, `resolution=unresolved`, and `candidate_role=candidate_not_answer`. Every emitted candidate citation remains bound to and validated against the immutable snapshot. This is S1 retrieval metadata, not answer generation or a change to Core retrieval. A strict check of Core's search-report form rejects asserted answer prose before it can be classified as retrieve-only. Private rows and the public aggregate use closed schemas with no source-path, title, content, question-text or raw-error field.

## Frozen identities and preservation

- Accepted Core commit `429c1c37d6bf17aab02b2d741b11a72d01d9a430`, tree `c08ccaf8044952299054fb0e2a41a788f8c325f0`; no Core edit.
- Seven-file candidate in `.worktrees/v0.6-pr01/`: Handoff 14 digest `f862be10d65d7a835aa11cf4a4e70a359f46855d9e53dce28af3a19470181766`; final canonical sorted path-to-file-SHA-256 JSON digest `3858c2958204284553ed3d2bdf1ebb44a2d06e7b7abf64cc07869b7b35efa532`. Changes are confined to the candidate benchmark, entry point and synthetic tests. No commit, merge or push.
- Private manifest raw SHA-256 `9d70850c5a2a0b746c506c70c4df90e0ba73c892a4e3554e48907c3b5a4decdc`, canonical parsed SHA-256 `54f5cea7eacebdcec9508843128f239de98eafb64927de4c78a6a965f5bb8f53`; unchanged, 24 questions.
- Retained snapshot `.worktrees/v0.6-pr01/data/v0.6-evidence/personal-recall/private/pr03/snapshot/`: 27 read-only Markdown files, 32,190 bytes, canonical relative-path/length/content-hash projection SHA-256 `baa147d7505d1eaf798203388aba4a0e4bce8b661935cce441c2938024a8cf4f`. Full private inventory SHA-256 `e8cb54d9ec1fe1cabd348a0cc1845bb7a2ce64e838e633449e3171c3ea6ea75a`. Closed-world inventory and Windows read-only attributes were reverified before and after proof. No source-vault read/proof retry occurred during this correction; no source-vault write was issued.
- Handoff 14's three frozen private files and failed public aggregate rehashed before and after: respectively `e8cb54d9ec1fe1cabd348a0cc1845bb7a2ce64e838e633449e3171c3ea6ea75a`, `0aa9eb07757db05e4a105efe2add53e510e87b0b27afaf700d93802800104e53`, `e3f71fa800163f6acfbe296e4f7b9ac74fd072434170af68bad57cbbc3a4c7ee`, and `394b428d4334ff32c202ea1e3dc4188f8f05520ea5987cb7c4e4356f4627a601`.

## Corrected proof results

| Gate | Result |
|---|---|
| Initial, acquisition, post-acquisition and final inventory checkpoints | All pass, 27 sources each |
| Three-run determinism | Pass; all 72 typed rows validate and the 24-row sequences are identical across three runs |
| Exact + metadata top-five recall | 10/10; threshold at least 9 |
| Project + relationship top-five recall | 8/8; threshold at least 6 |
| Paraphrase top-five recall | 3/3 |
| Authorization-negative controls | 2/2; authorized incidental candidates permitted, no excluded identity/content/path representable in closed results |
| Missing-answer control | 1/1; unresolved/retrieve-only, zero answer claims, candidate citations not claims of finding an answer source |
| Candidate citations | Pass; each emitted citation validates fingerprint and locator against retained bytes |
| Parse/index duration | 36.883, 7.972 and 8.198 ms |
| Query p95 | 4.597 ms, recomputed from private raw timings, under 500 ms ceiling |
| Peak measured memory | 1,941,713 bytes |
| Network/provider/persistent-index/legacy-memory calls | 0/0/0/0; socket/DNS tripwire active in benchmark |
| Privacy | Public closed schema validates; no private question text or expected source path found in redacted packet |
| Overall | **Pass**, pending independent Chief-of-Staff review |

## Evidence and commands

- Private raw results: `.worktrees/v0.6-pr01/data/v0.6-evidence/personal-recall/private/pr03/corrected-benchmark-results.json`, SHA-256 `518b7ff5f2ec1eb9ca055a8cb72ae7d5539f7e13a9c874c607d07c9ab20a23c3`.
- Private attempt/checkpoint record: `.worktrees/v0.6-pr01/data/v0.6-evidence/personal-recall/private/pr03/corrected-benchmark-attempt-evidence.json`, SHA-256 `dc95b7aebe76db9df11f2d410a50122e0a061a94a56210781a864ef346068464`, status `passed`.
- Redacted public aggregate: `.worktrees/v0.6-pr01/docs/evidence/v0.6/personal-recall-s0s1-snapshot-corrected-aggregate.json`, SHA-256 `6c4c4377e0cb34bea4ef9a401ce3badd3df514ba60fab4cee66f35e615624f18`.
- One corrected proof invocation used `python scripts/personal_recall.py snapshot-corrected-proof --repo <candidate> --policy config/personal_recall_policy.v1.json --public docs/evidence/v0.6 --private data/v0.6-evidence/personal-recall/private --manifest data/v0.6-evidence/personal-recall/private/benchmark-manifest.json`; exit 0 and the public SHA above. The entry point rejects a second invocation because its result targets now exist.
- Full offline repository tests: `python -m pytest -q` from the candidate using the repository's existing `.venv`; 829 passed, three documented environment skips. `python -m ruff check` on the seven candidate files passed. Synthetic/adversarial controls cover allowed incidental candidates, missing-answer assertion rejection, excluded identity/content injection, public-schema leakage, exclusive evidence and retained-snapshot immutability. The Verification & Quality Assurance skill informed these tests; no Ruflo tooling or rollback was used.
- Independent read-only reconciliation revalidated the full snapshot, all 72 typed rows, three-run identity, recomputed p95, public closed schema, privacy scan and all four historical hashes. Worklist, link, UTF-8, whitespace and diff checks are recorded at return.

No provider, credential, model, embedding, network download, background service, watcher, persistent index, legacy-memory call, frontend activation, production execution, snapshot deletion or source-vault write occurred. The private snapshot remains retained for independent review and later separately authorized cleanup.
