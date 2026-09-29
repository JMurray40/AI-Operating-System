# Handoff 01 - Personal Recall S0/S1 mandatory source-integrity stop

Date: 2026-09-22
Sender: Principal Engineer
Receiver: Chief of Staff
Milestone: `v0.6 Personal Recall - Read-only S0/S1`
Task: `V06-PR-01`
Disposition: **BLOCKED — SOURCE IDENTITY DRIFT BEFORE PRIVATE BENCHMARK**

## Executive disposition

[Verified] The isolated synthetic candidate and Phase 0 preflight were created under Handoffs 258-259. The full test suite passes. The real-vault Phase 2 benchmark was **not run**. A baseline reconciliation detected that one previously inventoried source path had disappeared and one different path had appeared. The source count (27), total bytes, and set of content hashes were unchanged, but path identity was not. Path-derived source IDs and the canonical inventory digest therefore cannot be claimed stable. The origin and timing of the path change are unknown.

This is the mandatory source-integrity boundary in Handoff 258, not an ordinary implementation defect. Engineering stopped before parsing the real corpus, running questions, or producing an aggregate success packet. The Product Owner's private 24-question template remains unfilled and outside Git; the operator was told to pause it.

## Repository and candidate identity

- Accepted Core commit: `429c1c37d6bf17aab02b2d741b11a72d01d9a430`; tree: `c08ccaf8044952299054fb0e2a41a788f8c325f0`.
- Clean isolated worktree created at `.worktrees/v0.6-pr01/` from that commit. No produced commit, merge, or push.
- Candidate consists of exactly seven new files: `config/personal_recall_policy.v1.json`, `scripts/personal_recall.py`, `src/jarvis_core/personal_recall/{__init__,policy,corpus,benchmark}.py`, and `tests/unit/test_personal_recall.py`.
- Canonical candidate digest: SHA-256 `3c53deee0282082cc11888134b003958bd32346615a86e61fb98dcedf8be10be`. Recompute by taking each of those seven repository-relative path-to-file-SHA-256 pairs, serializing the mapping as UTF-8 JSON with sorted keys and compact separators, appending LF, and SHA-256 hashing those bytes.
- Policy file SHA-256: `2208a20ad1931e642ca5af654e7130236650227adbf9ebc1c61b4f983735d686`.

## Work completed and evidence

1. Read Handoffs 246, 257-259, the canonical baton, worklist, and repository process. Validated the worklist before work.
2. Verified the accepted Core commit/tree and created the native Windows isolated worktree. Python 3.11 provides the required standard-library features. No dependency or network acquisition occurred.
3. Loaded the closed external policy outside the vault, resolved the exact approved vault root and five include roots, rejected reparse entries, and opened candidate Markdown sources only in binary read mode for a private baseline inventory. The initial preflight report records 27 sources, 31,908 bytes, five included roots, and private digests. It is at `.worktrees/v0.6-pr01/data/v0.6-evidence/personal-recall/private/preflight.json`; the corresponding private named inventory is beside it. Both are Git-ignored. This preflight records a point-in-time snapshot, not final source integrity.
4. Implemented a closed policy loader, read-only path/corpus adapter, in-memory Core lexical query construction, three-run private benchmark machinery, citation validation, and redacted aggregate schema. No existing Core source file changed. The candidate rejects provider intent, malformed policy, unknown labels, source changes, parse failures, path escape, reparse entries, and duplicate identities.
5. Ran synthetic adversarial tests: 14 passed; one symlink creation test skipped because this Windows account cannot create a symlink. The full accepted-Core suite passed: 800 passed, 3 skipped. The other skips are the existing citation symlink and separate Windows-logon identity cases. Ruff passed on all seven candidate files. These checks were rerun after the final path-exclusion correction.
6. On the first read-only inventory reconciliation after synthetic gates, observed one old-only path and one new-only path. Counts and content hash sets matched; the old path no longer existed. No raw note text or path appears in this public handoff. No benchmark question, answer, citation, raw result, or source identity was placed in Git or public evidence.

## Incomplete gates and limits

- The private 24-question manifest was not authored or executed. Exact/metadata recall, project/relationship recall, negative controls, missing answer, three-run determinism on real inputs, query p95, cold parse/index time, and peak memory remain **unmeasured**.
- No public aggregate packet was emitted. Do not infer acceptance or activation from the synthetic suite.
- The stop is based on source **path identity** drift, even though content-hash sets matched. It does not establish who renamed or moved the source. It does not establish that the vault was otherwise quiescent.
- The symlink adversarial case remains unexecuted under this Windows account; production path checks did execute over the observed entries.
- The private preflight and template are retained pending a governed retention decision. No cleanup is authorized or performed.

## Exclusions and next route

No vault write, persistent index, embedding, durable memory, provider, credential, network request, legacy-memory function, watcher, background service, voice recall, frontend activation, merge, push, publication, certification, or release action was performed by Engineering. The observed path change was external to this candidate, but its origin is unknown.

Chief of Staff should review this typed stop and decide the controlled route for a new stable source baseline before any real-vault benchmark resumes. Engineering must not silently replace the frozen baseline or claim Phase 2 completion. Product Owner action is not requested by this return; any changed authorization should be routed by the Chief of Staff.
