# Handoff 09 — Principal Engineer to CTO: Conversation Engineering Review (WP1–WP3)

| Field | Value |
|---|---|
| From | Principal Engineer |
| To | Chief Architect / CTO |
| Milestone | v0.5 — Visible-Context Conversation |
| Controlling briefs | Handoff 07, Handoff 08, Handoff 08a |
| Engineering base | `e11703974219425b463a45a97e1d7d2a04de81dc` |
| Engineering branch | `feature/v0.5-visible-context-conversation` |
| Scope delivered | WP1 (offline core) + WP2 (Google adapter via fake transport) + WP3 (CLI, benchmarks, packaging/recovery docs) |
| Disposition requested | **Independent CTO review of the WP1–WP3 candidate.** WP4 remains unauthorized. |

## 1. Candidate identity and worktree state

- Branch `feature/v0.5-visible-context-conversation`, base
  `e11703974219425b463a45a97e1d7d2a04de81dc` (unchanged; verified independently).
- The WP1–WP3 implementation, this handoff, and its host-validated evidence form one
  milestone candidate commit on the branch. The exact commit identity is emitted and routed
  by the Chief of Staff after the commit succeeds; the base remains the exact identity above.
- No merge, push, tag, release, or QA was performed. No historical-candidate or Voice-Shell
  content is present.

## 2. Implemented

**WP1 — contracts and offline application core** (`src/jarvis_core/conversation/`):
`contract`, `request`, `session`, `references`, `context`, `snapshot`, `approval`, `prompt`,
`evidence`, `results`, `render`, `trace`, `application`, `__init__` (14 modules). Two-phase
prepare/dispatch; immutable digest-bound `ContextSnapshot` (canonical SHA-256, copy-on-remove);
non-replayable `EgressApproval`; deterministic prompt projection with a complete hard budget;
claim taxonomy with current-byte citation revalidation; redacted allowlisted trace; safe
text/JSON rendering; the 12-step fail-closed turn state machine.

**Handoff 08a corrections** (folded into WP1): provider-specific credential preflight
(Decision A) and bounded one-hop authorized graph-neighbour expansion, ≤25 neighbours / ≤26
total, ordered by `(source_id, relpath)`, capped-as-safe-aggregate (Decision B).

**WP2 — Google adapter without live calls** (`src/jarvis_core/providers/`):
`conversation` (provider-neutral complete-response contract + `MockConversationProvider` +
`CredentialProvider` boundary), `transport` (injected seam + hardened stdlib `HttpsTransport`),
`credentials` (`EnvCredentialProvider` with injectable environment; `StaticCredentialProvider`),
`google_gemini` (sole Google wire boundary). Exact content projection, header allowlist,
endpoint/scheme/operation/redirect/proxy/telemetry/fallback denial, normalized usage/cost with
provenance, full redaction. Exercised only via fake transport and an in-process capturing seam.

**WP3 — CLI, benchmarks, packaging/recovery, docs**: `jarvis chat` (scripted + interactive,
digest-bound approval, exit-code contract, text/JSON parity) wired additively into the released
CLI; `scripts/benchmark_conversation.py`; `docs/software/V0.5_CONVERSATION_GUIDE.md`.

## 3. Deferred (not in this candidate)

Real-provider evidence (WP4), streaming, durable transcripts/resume/archive/search/export,
provider memory, tools/MCP/agents, multimodal, second-hop graph traversal, and a GUI —
all excluded by Handoff 07/ADR-0022–0024.

## 4. File and public-contract inventory

New source: `src/jarvis_core/conversation/` (14 modules, ~2,744 lines incl. `cli.py`) and
`src/jarvis_core/providers/{conversation,transport,credentials,google_gemini}.py` (~826 lines).
New tests: `tests/unit/test_conversation_wp1.py`, `…_wp1_08a.py`, `…_wp2.py`, `…_wp3.py`,
`tests/integration/test_cli_chat.py`. New tooling/docs: `scripts/benchmark_conversation.py`,
`docs/software/V0.5_CONVERSATION_GUIDE.md`. Modified released file: `src/jarvis_core/cli.py`
(one import + one `add_chat_subparser(sub)` call; no existing command altered).

Public contract versions:

```text
CONVERSATION_CONTRACT_VERSION = jarvis.conversation.v0.5.0
CONTEXT_SNAPSHOT_VERSION      = jarvis.conversation-context.v0.5.0
EGRESS_APPROVAL_VERSION       = jarvis.conversation-egress.v0.5.0
PROMPT_CONTRACT_VERSION       = jarvis.conversation-prompt.v0.5.0
PROVIDER_CONTRACT_VERSION     = jarvis.provider-complete-response.v0.5.0
CONVERSATION_TRACE_VERSION    = jarvis.conversation-trace.v0.5.0
GOOGLE_ADAPTER_VERSION        = jarvis.provider.google-gemini.v0.5.0
```

## 5. Requirement and C01–C30 mapping

| ID | Evidence (tests) | Coverage |
|---|---|---|
| C01 | `test_c01_session_numbering_and_reset`, `test_c01_no_durable_state` | full |
| C02 | `test_cli_api_digest_parity`, `test_manifest_prepare_only_exit_success`, `test_text_and_json_have_equivalent_status` | full |
| C03 | `test_remote_eligibility_fails_closed`, `test_a2_google_prepare_unavailable_credential_before_retrieval`, request/scope validation in `request.py`/`application.py` | core paths; broader missing-policy matrix recommended for QA |
| C04 | `test_b3/_b4/_b5` (excluded sources cannot influence; traversal cannot cross an excluded intermediary), remote sensitivity cap in `context.py` | full for graph/authorization boundary |
| C05 | `test_c05_project_selection_exact`, `…_not_found_fails_closed`, `test_b1..b11` | full |
| C06 | `test_c06_no_provider_call_during_prepare`, `test_a2` (spy proves pipeline not run) | full |
| C07 | `test_c07_removal_is_immutable_new_digest` | full |
| C08 | `test_c08_canonical_serialization_deterministic`, CLI reproducible-digest tests | full |
| C09 | `test_c09_approval_replay_after_removal_blocked`, `…_expired_approval_blocked`, `…_prompt_version_change_after_approval_blocked` | full |
| C10 | `test_c10_current_byte_drift_blocks_dispatch` | full |
| C11 | `test_c11_prompt_budget_hard_boundary` + block-cost budgeting (benchmark proves fit at 100–5,000 notes) | full |
| C12 | `test_c12_source_text_cannot_change_instructions` | full |
| C13 | `test_c13_capture_exact_content_fields_and_header_allowlist`, `…_credential_in_header_only`, `…_endpoint_host_escape_denied`, `…_scheme_and_operation_escape_denied`, `…_redirect_denied_single_attempt_no_fallback` | full |
| C14 | `test_c14_mock_and_google_share_normalized_contract` | full |
| C15 | `test_c15_secret_absent_from_all_surfaces_end_to_end`, `test_a3`, `test_a5` | full |
| C16 | `test_c16_c18_taxonomy_distinct`, `test_c16_stale_citation_withholds_answer` | full |
| C17 | `test_c17_metadata_claim_binds_current_metadata_evidence` | full |
| C18 | `test_c16_c18_taxonomy_distinct` (fact/inference/model_knowledge/unknown/assumption distinct) | full |
| C19 | `test_c19_coverage_labels` | full |
| C20 | `test_c20_no_numeric_answer_confidence` | full |
| C21 | `test_c21_exact_retry_reuses_snapshot_new_attempt`, `test_c21_drift_blocks_retry` | full |
| C22 | `test_c22_cancellation_is_terminal_once`, `test_cancellation_before_send_no_dispatch`, benchmark cancel-ack | full |
| C23 | `test_application_maps_failure_classes`, timeout/malformed/non-200/blocked degraded tests | full |
| C24 | `test_c24_usage_provenance_never_silent_zero`, `test_usage_absent_is_unknown_not_zero` | full |
| C25 | `test_c25_sanitizer_neutralizes_active_content` | full |
| C26 | `test_c26_trace_has_no_content` | full |
| C27 | `test_c27_cross_workspace_sessions_isolated` | core; two-workspace concurrency stress recommended for QA |
| C28 | `test_c28_c29_no_vault_mutation_or_store` | full |
| C29 | `test_c28_c29_no_vault_mutation_or_store` (no operational store; session-only) | full |
| C30 | full released unit + integration regression (484 passed) | full |

## 6. Provider profile, endpoint, allowlists, credential boundary

- Profile: `provider_id=google-gemini-developer-api`, `model_id=gemini-3.5-flash-lite`,
  host `generativelanguage.googleapis.com` (https), operation `generateContent`,
  non-streaming, `thinking_level=minimal`, timeout 60s, 0 retries, 1 request/approval,
  per-request ceiling USD 0.05.
- Documentation reference: `https://ai.google.dev/api/generate-content` (v1beta
  `models.generateContent`), recorded `2026-08-01` as an **implementation reference**; the
  exact request/thinking field shapes and pricing **must be reconfirmed at the WP4 preflight**
  (H07 §4.2). This is not a live-doc verification.
- Content fields: `systemInstruction`, `contents` (single user turn), `generationConfig`
  (`maxOutputTokens`, `temperature=0`, `candidateCount=1`, `thinkingConfig.thinkingBudget=0`).
  Transport headers allowlist: `content-type`, opaque `x-goog-api-key` only.
- Credential boundary: `EnvCredentialProvider` reads `GEMINI_API_KEY` through an injectable
  environment; `is_available()` is presence-only; the secret never enters snapshot, approval,
  prompt, trace, error, or log, and materializes only at the adapter for one attempt. **No live
  key was read; tests inject canaries and a fake environment.**

## 7. Dependency inventory and network evidence

- **No new runtime or development dependency.** Standard library only (`http.client`, `ssl`,
  `json`, `threading`, `dataclasses`, `enum`). No provider SDK, LiteLLM, or build backend added.
- Network evidence: none — no live call in this cycle. The adapter was proven only against a
  fake transport and an in-process capturing seam; `HttpsTransport` guards (https-only,
  request-size bound, pre-cancel) are unit-tested without a socket.

## 8. Benchmarks (raw samples retained; independently recomputed)

Harness: `scripts/benchmark_conversation.py` (reuses the released vault generator and
`_stats_ms` percentile method). Runs=20, warmup=3, fixed evaluation time. The figures below
are the authoritative rerun on the accepted current-PC reference host under Python 3.14.4.

| Notes | prepare p50/p95/p99 (ms) | peak (MiB) | app-overhead p95 (ms) | cancel-ack p95 (ms) |
|---|---|---|---|---|
| 100 | 25.337 / 31.081 / 40.848 | 0.815 | 25.289 | 23.778 |
| 500 | 138.236 / 155.812 / 158.798 | 3.502 | 30.402 | 21.511 |
| 1,000 | 259.461 / 286.866 / 296.499 | 6.565 | 30.736 | 25.515 |
| 5,000 | 1,372.560 / 1,793.782 / 1,978.079 | 35.713 | 39.555 | 17.974 |

Gates (H07 §13) all pass: 5,000-note prepare p95 1,793.782 ms < 2 s; app overhead p95 < 250 ms;
cancellation ack p95 < 500 ms; bounded peak memory. The JSON artifact with raw samples is
reproducible via `--json`; it is not committed (no evidence-artifact repository boundary was
granted).

## 9. Regression, static, docs, packaging/recovery, privacy, immutability

- Full released regression on the host: **490 passed, 2 skipped**. The skips are the existing
  unsupported-symlink case and the independently gated CS-21 separate-Windows-logon case.
- Conversation acceptance: **69 tests pass** (WP1 24, 08a 15, WP2 19, WP3 3, CLI 8).
- Static on the host: all new WP1-WP3 Python files are Ruff-formatted; the released CLI
  retains its prior formatting with only the two authorized wiring lines; `ruff check src
  tests scripts` is clean; `mypy` **Success, 86 source files** with mypy 2.3.0.
- Docs: `git diff --check` clean; the guide adds no relative Markdown links (lychee-safe).
- Packaging/recovery: no new dependency; the conversation package ships in the existing
  `jarvis-core` wheel/entry point (mechanisms documented; **independent A12 execution is not
  claimed**). Offline mock fixture rerun via `jarvis chat … --approve <digest>`;
  missing-credential/provider-unavailable proven to fail closed; session-only state means
  nothing to recover after a crash.
- Privacy/immutability: vault byte-integrity proven unchanged before/after
  (`test_c28_c29_…`); no operational store; trace/secret canary scans pass.

## 10. Historical-candidate reuse statement

**None.** No file, function, or serialized contract from `feature/v0.4-conversation` was
copied, cherry-picked, or executed. Every module was written fresh against released main
contracts. Ideas were reimplemented conceptually, not ported.

## 11. Load-bearing judgment calls (all resolved; noted for the record)

1. Credential preflight timing and the "prepare works with no provider" degraded row —
   adjudicated by Handoff 08a Decision A; implemented and tested (`test_a1..a5`).
2. Project scope as one-hop authorized graph expansion — adjudicated by Handoff 08a Decision B;
   implemented and tested (`test_b1..b11`).
3. **Budget-consistency fix (C11):** the context selector now budgets each item's full prompt
   block cost (excerpt + delimiters) against prompt headroom, single-sourced in `prompt.py`, so
   a well-formed snapshot's prompt always fits its hard budget. This corrected a WP1 modelling
   gap surfaced by the benchmark at ≥500 notes; it is an implementation fix, not a scope change.

## 12. Deviations

- The previously reported sandbox locks were absent at host preflight; no lock deletion was
  necessary. The host reran the scoped and full gates with Git 2.55.0.windows.1.
- **Google wire shape and pricing** are implementation references pending WP4 preflight
  reconfirmation; no live doc verification was performed.
- No other deviations from Handoff 07 / 08 / 08a.

## 13. Requested disposition

Please review the WP1–WP3 candidate for CTO disposition and forward to Quality & Release as
appropriate. WP4 (real-provider evidence), live credentials, provider calls, merge, push, tag,
and release remain unauthorized and were not performed.

---

# SUPERSEDING REMEDIATION REVISION — Handoff 12 (AC-05-01–05, AE-05-01)

This revision supersedes the disposition above for the AC-05 remediation cycle authorized by
Handoff 12 (correction base `588896f955c86ce64db478086ea5fd6be4cc2280`, tree
`2f7306f15eb1c6afe3a481a364150f537618c2e3`, disposition **Refactor first**).

## R1. Exact commit and tree identities

| Artifact | Identity |
|---|---|
| Executable remediation commit | `4f61cb19b2de621ded86cdbc7882c01cea5d52e3` |
| Executable tree | `4b6532beb906eb5dc64a4c09deeaa7360c77550e` |
| Parent (correction base) | `588896f955c86ce64db478086ea5fd6be4cc2280` |
| Branch | `feature/v0.5-visible-context-conversation` |
| Evidence/documentation-only commit | immediate descendant of `4f61cb19…` containing this revision plus the evidence JSON; contains no `src/`, `tests/`, scripts, dependency, or packaging change; exact SHA recorded by the Chief of Staff at commit |
| Unchanged-query baseline | `e11703974219425b463a45a97e1d7d2a04de81dc` |

The worktree was **clean** at the executable commit (verified `git status --porcelain` empty).
The performance evidence was produced only **after** that commit was frozen, so no evidence is
attributed to still-changing code.

## R2. AC-05-01–05 requirement-to-test mapping

| Requirement | Implementation | Tests |
|---|---|---|
| AC-05-01 deep semantic immutability | `conversation/immutable.py` (deep-freeze to read-only mappings/tuples, defensive copy, JSON encoder default); snapshot/approval freeze all nested collections; `ContextSnapshot.verify_integrity()` recompute before removal/approval/dispatch | `tests/unit/test_conversation_ac05_01.py` (mutation/alias/integrity, nested + approval) |
| AC-05-02 single-use approval + exact retry lifecycle | typed `AttemptRecord` + `approval_consumed`/`in_flight` state; consume-once initial dispatch; replay/concurrent/dispatch-after-terminal fail closed before prompt/provider; explicit bounded retry (eligible-terminal only, ≤5 attempts); history serialization bound into the snapshot for byte-identical retry; cancellation forced terminal-once | `tests/unit/test_conversation_ac05_02.py` |
| AC-05-03 exact Google destination profile | `google_gemini._destination_ok` exact-equality on provider/model/scheme/host/path/operation/timeout/limits/streaming/retries; bare-host + byte-exact-path reject port/user-info/encoding/query/fragment/slashes/case/alt-model/alt-api | `tests/unit/test_conversation_ac05_03.py` (20 negatives, each zero transport) |
| AC-05-04 structured claims + deterministic support | `evidence.validate_response` structured JSON contract (no markers); per-claim shape/taxonomy/ID/current-byte + lexical-overlap support; inference validates every premise; metadata binding; unsupported never upgraded; fail-closed | `tests/unit/test_conversation_ac05_04.py` (unrelated passage, partial inference, fabricated/unknown/duplicate id, metadata mismatch, adversarial punctuation, malformed) |
| AC-05-05 one safe presentation object | `conversation/presentation.py` `PresentationResult`/`present()` consumed identically by API/text/JSON/CLI; answer built from sanitized claims; raw provider payload discarded upstream (absent from results/trace/session history); shared `conversation/sanitize.py` | `tests/unit/test_conversation_ac05_05.py` (renderer==presentation, corpus sanitization, trace/history absence) |

All prior 69 conversation tests plus the new adversarial matrices pass (124 conversation
acceptance tests in this cycle; full released unit+integration **542 passed, 2 skipped**).

## R3. AE-05-01 performance evidence (predeclared; recomputable)

Protocol fixed before results: baseline `e11703974219…`, candidate `4f61cb19…` (both
materialized via `git archive`), one shared harness (`scripts/benchmark_conversation_remediation.py`
+ `scripts/_qe_bench_runner.py`), identical synthetic vaults at 100/500/1,000/5,000 notes,
identical query/scope/root/evaluation boundary, 3 warmups + 20 measured runs per size,
candidate-first/baseline-first alternated by size, all raw wall-clock and per-run peak-memory
samples retained.

| Notes | order | baseline query p95 (ms) | candidate query p95 (ms) | candidate/baseline p95 | ≤20% |
|---|---|---|---|---|---|
| 100 | candidate_first | 26.685 | 26.028 | 0.975 | pass |
| 500 | baseline_first | 126.602 | 126.788 | 1.002 | pass |
| 1,000 | candidate_first | 245.397 | 242.334 | 0.988 | pass |
| 5,000 | baseline_first | 1487.829 | 1314.217 | 0.883 | pass |

- **Unchanged-query ≤20% p95 gate: PASS at every size.** The released query stack
  (`query`, `models`, `policy`, `repositories`, `context`, `relationships`, `parsing`,
  `identity.py`, `config.py`) is **byte-identical** between baseline and candidate
  (`git diff` empty), so the harness executes identical code in both trees; any p95 delta is
  measurement noise, disclosed as such (no post-hoc change to the accepted ≤20% rule).
- **Conversation absolute gates (candidate): PASS** — 5,000-note prepare p95 < 2 s, application
  overhead p95 < 250 ms, cancellation acknowledgement p95 < 500 ms.
- Evidence artifact: `docs/evidence/v0.5/conversation-performance-remediation.json`,
  independently generated SHA-256 **`57e031adb653db6c0f11fbc8e2bda484e20bf0c64684bd8ed315fc3480c7ae42`**.
- Independent recomputation from the retained raw samples reproduces every reported p50/p95/p99
  and ratio exactly (20/20 samples per size, per tree).

## R4. Gates, limitations, and no-live-call confirmation

- Static/tests: **Ruff clean** on changed/new files and across `src tests scripts`; **mypy
  strict Success (89 files)**; whitespace/conflict clean; privacy/secret scan of the evidence
  artifact clean (no prompts, context, responses, credentials, private paths, usernames, or
  raw errors).
- **Host verification (authoritative):** on the Windows host (git 2.55.0), the full released
  suite is **545 passed, 2 skipped** (CS-21 Windows-logon and a symlink-unsupported skip; no
  failures), Ruff **all checks passed**, mypy **Success (89 files)**. The three
  `test_project_resume_local_git` real-git tests — which cannot run in the sandbox (git 2.34
  below the 2.38 floor) — **pass on the host**, so the executable commit `4f61cb19…` is
  technically complete. Those tests are unrelated to this remediation (the released local-git
  module was not modified).
- **Limitations:** the AE-05-01 latency figures were produced in the Engineering sandbox
  (Python 3.10.12), not the accepted v0.4 reference machine; absolute milliseconds are
  environment-dependent, but the ≤20% comparison is valid because both trees run a
  byte-identical released query stack, and a reference-machine rerun remains available.
- **No live credentials, provider calls, network egress, vault writes, packaging, QA, merge,
  push, tag, release, Voice Shell, or Multica work were performed.** The Google adapter was
  exercised only through a fake transport / in-process capture; `GEMINI_API_KEY` was never read.

## R5. Requested disposition

Chief-of-Staff validation and exact-commit CTO re-review of the executable commit
`4f61cb19…` plus its descendant evidence commit. Quality, WP4, and live-provider activity
remain unauthorized.
