# Handoff 18 - Personal Recall closeout authorization

Date: 2026-09-23
Sender: Chief of Staff
Receiver: Principal Engineer
Task: `V06-PR-05`
Disposition: **AUTHORIZED - PRIVATE SNAPSHOT CLEANUP AND EXACT CANDIDATE FREEZE**

## Authority

[Verified] The Product Owner approved both Handoff 17 closeout recommendations:

1. securely delete the accepted temporary private snapshot; and
2. freeze the exact seven-file Personal Recall candidate in one native-Windows Git commit without merge or push.

## Required sequence

Perform this as one bounded closeout task:

1. Reverify the accepted Core commit `429c1c37d6bf17aab02b2d741b11a72d01d9a430` and tree `c08ccaf8044952299054fb0e2a41a788f8c325f0`.
2. Recompute the seven-file candidate digest and require exact equality with `3858c2958204284553ed3d2bdf1ebb44a2d06e7b7abf64cc07869b7b35efa532` before staging.
3. Reverify the retained snapshot has exactly 27 Markdown files, 32,190 bytes, full inventory file SHA-256 `e8cb54d9ec1fe1cabd348a0cc1845bb7a2ce64e838e633449e3171c3ea6ea75a`, canonical projection SHA-256 `b9571c0fe49cb345c2c6af96f841304d6d9190fa41955ba9576b3f02d8985afb`, zero mismatches and zero extras.
4. Preserve all non-snapshot private evidence, the redacted public aggregate and Handoff 14 failed evidence.
5. Remove only `.worktrees/v0.6-pr01/data/v0.6-evidence/personal-recall/private/pr03/snapshot/`. Clear read-only attributes only as required to delete that exact directory. Do not delete its inventory or benchmark evidence.
6. Verify the snapshot directory is absent and record a privacy-safe deletion statement. Do not list private filenames or paths beyond the governed snapshot root.
7. Run the focused Personal Recall tests, Ruff and `git diff --check` using native Windows tooling.
8. Stage exactly these seven candidate files:
   - `config/personal_recall_policy.v1.json`
   - `scripts/personal_recall.py`
   - `src/jarvis_core/personal_recall/__init__.py`
   - `src/jarvis_core/personal_recall/benchmark.py`
   - `src/jarvis_core/personal_recall/corpus.py`
   - `src/jarvis_core/personal_recall/policy.py`
   - `tests/unit/test_personal_recall.py`
9. Confirm no public aggregate, private evidence, cache, generated file or unrelated user change is staged.
10. Create one native-Windows Git commit with message `Add read-only personal recall prototype`.
11. Record the exact commit, tree and parent; confirm the candidate worktree is clean except ignored caches and retained evidence.
12. Return one Handoff 19 to Chief of Staff. Stop without merge, push, tag, release, frontend activation or benchmark rerun.

## Stop conditions

Stop before deletion or commit if any bound identity differs, the exact snapshot target cannot be resolved safely, any non-snapshot evidence would be removed, the staged set differs from the seven paths, tests/lint/whitespace fail, native Windows Git is unavailable or an unrelated user change overlaps the candidate.

Ordinary execution issues must be resolved inside this task when safe and in scope. Do not create serial handoffs for internal implementation details.

## Boundary

This authorization is intentionally destructive only for the exact temporary snapshot directory identified above. Its removal is not recoverable unless another copy exists; Product Owner explicitly approved that cleanup after evidence acceptance. No source-vault write, manifest edit, evidence deletion, benchmark run, provider/network use, merge, push, tag, release or activation is authorized.
