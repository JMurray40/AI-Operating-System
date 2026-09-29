# Handoff 04 - Personal Recall benchmark input pause

Date: 2026-09-22
Sender: Principal Engineer
Receiver: Product Owner for private input, then Principal Engineer
Task: `V06-PR-01`
Disposition: **IN PROGRESS — REQUIRED HUMAN BENCHMARK INPUT**

## Completed under Handoff 03

[Verified] The accepted Core worktree remains at commit `429c1c37d6bf17aab02b2d741b11a72d01d9a430`, tree `c08ccaf8044952299054fb0e2a41a788f8c325f0`. The candidate is isolated at `.worktrees/v0.6-pr01/`. Its current seven-file canonical digest is SHA-256 `17195cd27756a49829981a3dc3c84f73f11b85c763e32d80b4887e6e9c654bde` (sorted repository-relative path-to-file-SHA-256 JSON, compact separators, LF terminator).

[Verified] A synthetic regression creates a filename containing exactly `U+2014`, takes two inventories, serializes and deserializes the path as UTF-8 JSON, and rejects the `U+00E2 U+20AC U+201D` sequence. The synthetic suite includes policy, read-only, exclusion, network/DNS, duplicate-identity, citation-drift, source-drift, and public-schema controls.

[Verified] Two complete read-only inventories of the approved five-folder Markdown corpus were taken several seconds apart and matched byte for byte. Each contains 27 entries, one `U+2014` path, and no mojibake or replacement-character path. The second was separately bound as `data/v0.6-evidence/personal-recall/private/baseline-inventory-v2.json`; the historical `baseline-inventory.json` was preserved. The renewed `preflight-v2.json` passed, and a later read-only inventory still matched the bound baseline. All of these records are under the Git-ignored private evidence root.

[Verified discrepancy] Direct UTF-8 inspection of the retained historical baseline found one proper `U+2014` path and no mojibake; its SHA-256 `6406d6a5289e6f6016e38b7e2aa38ca64b4499f30449cb55022ad88397a0cb41` equals both new snapshots and the v2 baseline. This differs from Handoff 03's description of the retained baseline. No historical record was edited. The initial observed mismatch remains documented in Handoffs 01-03, but current evidence does not support a claim that the retained baseline bytes are defective.

[Verified] The final code passes 803 repository tests with three documented environment skips. Ruff passes. The native Windows symlink creation test is one skip; no path outside the approved five folders was read as note content. No vault file was renamed or written, and no dependency, provider, credential, network call, persistent index, or model was used.

## Required human action

The private benchmark template at `.worktrees/v0.6-pr01/data/v0.6-evidence/personal-recall/private/benchmark-manifest.json` has 24 closed-schema records but zero filled question fields. The Product Owner/human principal must fill the questions, expected relative source paths, and reasons locally; the adjacent private v2 baseline lists eligible source paths. Do not paste the question text, paths, answers, or notes into chat or Git. Reply `manifest ready` after saving. No change to the approved category counts or sensitivity ceiling is authorized.

Engineering will then validate the manifest, run three cold in-memory lexical passes, reverify source integrity, enforce recall/citation/privacy/performance gates, and return one complete redacted review package or one typed mandatory stop. The benchmark has **not** run yet; no public aggregate result or success claim exists.

This pause is for the human-authored input expressly required by Handoff 258. It does not request a new Product Owner scope decision or authorize a new task.
