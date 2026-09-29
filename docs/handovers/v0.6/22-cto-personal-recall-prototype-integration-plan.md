# Handoff 22 - Personal Recall to JARVIS integration plan

Date: 2026-09-24
Sender: Chief Architect / CTO
Receiver: Chief of Staff
Task: `V06-PR-06`
Disposition: **READY FOR REVIEW - IMPLEMENTATION NOT AUTHORIZED**

## 1. Outcome, authority and boundary

[Recommended] Add a typed `recall <question>` operation to the accepted personal JARVIS CLI. It searches locally, displays up to five ranked, revision-bound candidates, and never dispatches a conversation or provider request. The first Engineering outcome includes the real Core-to-shell integration, synthetic private-classified notes, adversarial tests, an operator demonstration, and two immutable Git candidates. It does not enable access to the live vault or activate a device or provider.

This is the implementation contract proposed for approval, not an implementation authorization. All design requirements below are [Recommended] unless explicitly marked [Verified]. No demonstration, benchmark, provider call, private-content read, executable edit, worktree creation or commit was performed during planning. The demonstration in section 9 is a future acceptance gate, not a claim of an already working implementation.

Controlling inputs, in precedence order:

- [Product Owner S0/S1 decision](../v0.5/257-product-owner-personal-recall-planning-decision.md) and [implementation decision](../v0.5/259-product-owner-personal-recall-s0-s1-implementation-authorization.md).
- [Product Owner sensitivity-routing decision](../../../../../docs/coordination/reviews/V05-PT-30-PRODUCT-OWNER-ACCEPTANCE-AND-NEXT-GATES.md), with [Handoff 138](../v0.5/138-cto-to-product-owner-sensitivity-aware-provider-routing-disposition.md). The ADR-0025 copy in the release documentation still says proposed; this plan relies on the recorded Product Owner decision, not an inferred ADR acceptance.
- Accepted trust contracts ADR-0014/0015/0016/0017: relevance is not confidence; authorization precedes retrieval; citations bind passages to revisions; identity is separate from location.
- [Handoff 20](20-chief-of-staff-personal-recall-closeout-acceptance.md), [Handoff 18](18-chief-of-staff-personal-recall-closeout-authorization.md), and the current [Handoff 21 planning authorization](21-chief-of-staff-personal-recall-integration-planning-authorization.md).
- [Voice Git acceptance](../v0.5/202-cto-pt51-native-voice-candidate-acceptance.md), [PT63 acceptance](../v0.5/244-chief-of-staff-pt63-local-voice-acceptance.md), and [PT64 acceptance](../v0.5/256-chief-of-staff-pt64-phase-b-acceptance.md).

No durable memory, embeddings, persistent index, background watcher, source-vault write, benchmark rerun, manifest change, legacy runtime integration, live voice, model/provider activation, acquisition, credential, merge, push, tag, packaging or release is included. PR01 remains terminally blocked. The deleted private proof snapshot must not be recreated. Retained private/public evidence and all unrelated changes remain untouched.

## 2. Exact bases and reconciliation

[Verified] Native Git object inspection on 2026-09-24 resolves these bases:

| Repository | Existing readable checkout | Branch/state | Commit | Tree | Parent |
|---|---|---|---|---|---|
| Core: `C:/Users/jmurr/Projects/AI-Operating-System` | `.worktrees/v0.6-pr01` | Detached HEAD; no source branch claimed | `cf7ac875cea1843295e825ea4322696d42af9ce1` | `56b27a9d6663eabb39692925f662c663ca6adc62` | `429c1c37d6bf17aab02b2d741b11a72d01d9a430` |
| Voice: `C:/Users/jmurr/Projects/J.A.R.V.I.S` | `C:/Users/jmurr/Projects/AI-Operating-System/.worktrees/v0.5-pt50-voice` | `codex/v0.5-pt50-durable-gemini` | `0588d3b05af2f225e63457583e7c321b283ddeb2` | `0acf74ae09ad09cc86dc5e6eb9d90aec37ba4528` | `7a1016cb78b7109a20068a252265437936208c20` |

[Verified] Core status has only `docs/evidence/v0.6/` untracked; Voice status has `data/` and `docs/evidence/` untracked. Neither reported tracked changes. Ignore-file access warnings occurred; these are not clean-environment attestations. Do not stage either checkout wholesale. The coordination root is parked on `feature/v0.4-conversation`; the handoff repository is `.worktrees/v0.3.1-release`, `main`, observed HEAD `e25d4d8`. Neither is an executable base.

[Verified] PT63/64 are later accepted **overlay proofs**, not newer committed frontend bases. [Handoff 242](../v0.5/242-principal-engineer-local-voice-prototype-return.md) binds PT63 to Voice `0588d3b...` plus an eleven-file archive; PT64 accepts overlay digest `c2fa7864ffa56629b44425f079568221cc61be29c63370c9c4f8a0b8078d152d`. Their device allowance is consumed and neither accepts general frontend activation. Selecting the accepted text-shell Git base preserves those proofs; it does not supersede or silently import their overlays. Voice/audio integration is a later decision.

Proposed future branches and worktrees, created only after the next authorization:

- Core branch `codex/v0.6-recall-integration-core`, checkout `C:/Users/jmurr/Projects/AI-Operating-System/.worktrees/v0.6-recall-core`, exact Core parent above.
- Voice branch `codex/v0.6-recall-integration-voice`, checkout `C:/Users/jmurr/Projects/AI-Operating-System/.worktrees/v0.6-recall-voice`, registered in the J.A.R.V.I.S repository, exact Voice parent above.
- Abort if either name/path already exists with a different identity; do not reset, reuse or delete it. No cherry-picks or merging of device overlays.

## 3. Inspected public interfaces and intentional additions

[Verified] Inspection used actual source files in both exact checkouts, not only reports:

| Current surface | Observed contract | Integration decision |
|---|---|---|
| Core `personal_recall/__init__.py` | Exports `RecallPolicy`, `load_policy`, `inventory_sources`, `build_corpus`, `run_benchmark`; no versioned application/session service | Add application and immutable DTO exports without removing existing exports |
| `personal_recall/policy.py` | Closed policy schema v1; exactly five ordered Markdown root rules; explicit workspace/policy ID/version; ceiling exactly `private` | Reuse unchanged; policy is owner-controlled, never inferred from content |
| `personal_recall/corpus.py` | Inventory, frozen-byte acquisition, parse, fingerprints, reparse/exclusion checks; ordinary corpus built in memory | Reuse; add optional bounded/cancellable read controls for the new application, preserving existing default behavior |
| `personal_recall/benchmark.py` | Sealed 24-question proof, three runs, private/public outputs; substitutes an acquired-byte citation resolver through a private engine member | Never call from integration; never copy its private-member mutation or proof retry loop |
| `query/engine.py` | `QueryEngine(notes, *, scope, source_root, weights=None, token_budget=..., provider=None)`; `search(query, *, limit=20)` forces SEARCH; `run` also routes summarize/relationship intents | Use only public `search(query, limit=5)`, with a Core-owned denying provider sentinel; never `run`, `ask`, `summarize`, or `explain` |
| `query/results.py`, `query/passages.py` | Frozen `Citation`, `QueryAnswer`, `Locator`; source ID/kind, path/title, exact byte fingerprint, heading path, inclusive line range, excerpt, relevance/reason; citation coverage | Reuse exact values; project closed recall DTOs, not `QueryAnswer.to_dict()` |
| `policy/scope.py`, `query/authorized.py` | Explicit immutable `AuthorizationScope`; authorization before index and relationship construction; duplicate authorized explicit IDs rejected | Construct scope inside Core from the bound policy; never use `local_allow_all` |
| Core conversation | `ConversationApplication`; contract `jarvis.conversation.v0.5.0` | Unchanged; recall never creates a turn, approval, prompt, history entry or egress grant |
| Voice `contracts.py` | `VoiceCoreBridgeProtocol`: prepare/remove/approve/dispatch/cancel/retry/reset; `CitationView` has only source/revision/passage/locator strings | Keep conversation protocol compatible; add separate recall protocol/DTOs, since existing citation view loses structured locator and relevance semantics |
| Voice `core_bridge.py` | `JarvisCoreVoiceBridge`, captured binding/generation, lock-free Core calls, atomic publication; mock default with narrowly injected local/Gemini seams | Preserve unchanged; put recall in a sibling shell-owned adapter with no provider seam |
| Voice `controller.py` | `VoiceShellController`; async dispatch/poll/cancel/reset/close and speech safety | Add optional recall bridge and explicit recall methods; never convert recall candidates into `CoreTurnView` or speech |
| Voice `cli.py` | Keyboard loop; `--fixture synthetic`; states IDLE/approval/dispatch/retry/failed; Gemini ordinary execution exits 8 as inactive | Add opt-in recall mode and reserved typed recall commands; existing invocation stays compatible |
| Voice `prototype.py` | Creates/deletes owned synthetic fixture, loads conversation notes, supplies Core preflight | Keep conversation fixture intact; new recall fixture harness owns its separate fixture and invokes the same CLI |
| Voice structural tests | Exactly 12 runtime modules; only `core_bridge.py`, `live_gemini_pilot.py`, `prototype.py` may import Core | Extend exact module inventory to 14, allowing only new `recall_bridge.py` to import the recall public API; no blanket exception |

Dependency direction is `CLI -> VoiceShellController -> VoiceRecallBridgeProtocol -> JarvisCoreRecallBridge -> jarvis_core.personal_recall public application API`. Core never imports Voice. Contracts/controller/CLI/fixture harness never import Core. The adapter imports only the new public recall exports, not query, corpus, policy internals, conversation, providers or legacy runtime. Core retains retrieval, policy, citation and publication authority.

The shell protocol mirrors `open_session`, `recall`, `cancel`, `reset`, `close` using shell-owned `RecallSessionView`, `RecallRequestView`, `RecallResultView` and `RecallCancelView` with the same closed fields/semantics defined below. The bridge constructor accepts a shell-owned immutable fixture-binding description and constructs Core's binding internally. It maps values explicitly, never passes shell objects into Core as if they were Core DTOs. A public adapter preflight helper returns only version/readiness categories to the harness. The controller worker calls the synchronous bridge `recall`; `poll_recall` inspects the worker's one immutable completion, without issuing another search. Existing conversation methods, DTO defaults and mock bridge implementations remain compatible when recall injection is absent.

## 4. Frozen application, DTO and error contract

### Application operations

Add `PERSONAL_RECALL_CONTRACT_VERSION = "jarvis.personal-recall.v1"`. Keep `jarvis.query.v0.3.1` and every conversation/provider version unchanged. Bridge compares the literal expected version with the application's advertised version before any source read; missing/mismatched Core becomes `CORE_UNAVAILABLE` with no fallback.

Public API:

```text
PersonalRecallApplication(binding: RecallWorkspaceBinding)
  open_session() -> RecallSessionRef
  recall(session: RecallSessionRef, request: RecallRequest,
         cancellation: RecallCancellation) -> RecallResult
  cancel(session: RecallSessionRef, request_id: str) -> RecallCancelResult
  reset(session: RecallSessionRef) -> RecallSessionRef
  close(session: RecallSessionRef) -> None
```

`RecallCancellation` is a read-only `is_requested() -> bool` protocol implemented by a shell-owned event token. Core also records cancellation under its own session lock. `RecallCancelResult` is one of `requested`, `already_terminal`, `unknown_request`; cancellation acknowledgment is not a fabricated terminal result. Session references contain an opaque instance ID plus integer generation. Close is idempotent; stale generations fail closed. No factory, provider, arbitrary callback executor, note list or raw dictionary is accepted through the shell API.

`RecallWorkspaceBinding` is a frozen startup value with `mode="synthetic"`, absolute fixture root, absolute policy path, policy SHA-256, expected policy ID/version/workspace ID and root digest. The first implementation accepts only the synthetic mode. The harness creates and binds these values; typed queries cannot change them. A future owner-approved private binding must be a separately authorized activation and use the same API with its own exact binding; it is not an ambient environment variable or arbitrary `--vault` flag. No live-vault selector is added in this task.

`RecallRequest`: `contract_version`, `request_id` (opaque, nonempty, at most 64 ASCII identifier characters), `question` (1..2,000 Unicode characters after whitespace validation), `max_results` (integer 1..5; bool invalid). No destination, root, policy, sensitivity override or generation inference from text. Unknown fields, nonfinite numbers, mutable container substitutes and invalid enum values fail closed. Query text is not echoed in the result or diagnostics.

### Result fields and mapping

All nested DTOs are frozen dataclasses with immutable tuples/enums/scalars; no `Note`, `Path`, dict, exception, trace, engine, provider or mutable frontmatter crosses the application result boundary. Strings and tuples have validated bounds; serialization is a closed allowlist, not reflective dumping.

| DTO field | Type / rule |
|---|---|
| `RecallResult.contract_version` | Exact literal above |
| `session_instance`, `generation`, `request_id` | Exact admitted request binding; shell checks all three before display |
| `status` | `completed`, `blocked`, `failed`, `cancelled` |
| `result_type`, `resolution`, `answer_claim` | Always `ranked_retrieval_candidates`, `unresolved`, `none`; finding a match does not resolve a factual question |
| `mode`, `destination`, `sensitivity_ceiling` | `retrieve_only`, `local_no_provider`, `private` |
| `policy_id`, `policy_version`, `policy_digest`, `root_digest` | Bound configuration, copied from startup; digests are SHA-256, no absolute root path |
| `coverage` | `complete`, `partial`, `incomplete`, `none`; copied from Core citation coverage of the represented candidates; display explicitly says citation coverage, never answer completeness |
| `limitations` | Tuple from closed enum: `RETRIEVE_ONLY`, `LEXICAL_SEARCH`, `TOP_K_LIMIT`, `AUTHORIZED_SCOPE_ONLY`, optionally `NO_MATCH` or `NO_SEARCHABLE_TERMS`; no excluded counts |
| `candidates` | Ordered tuple, at most 5; empty for any non-completed terminal result |
| `error_code` | None on completion; fixed safe category otherwise |

Each `RecallCandidate` contains `rank` (1..5), `source_id` (1..512 chars), `source_identity_kind` (`explicit`/`path_derived`), `title` (up to 256), `relative_path` (up to 1,024; no absolute path/traversal), `sensitivity` (known label no higher than private), `revision_fingerprint` (`sha256:` plus 64 lowercase hex chars), frozen `RecallLocator(heading_path, line_start, line_end)`, `excerpt`, `relative_relevance`, `reason`, `citation_coverage`. Heading path: at most 64 components of 256 characters each; reason: at most 512; excerpt: existing maximum 600 characters and six lines. Relevance must be finite and within the existing normalized range 0..1, or None. Locator lines are positive inclusive integers for a supported citation. Incomplete references use the existing zero-line/no-excerpt semantics and must never masquerade as supported.

Copy citation identity/kind, path, fingerprint, locator, excerpt, relevance and reason verbatim from Core. Sensitivity comes from the authorized parsed note at that exact relative path. Never derive source identity from the UI rank or revision. Reject an overlong provenance field with `RESOURCE_LIMIT`; do not truncate a locator, path, identity or verbatim excerpt and claim the original binding. Display-only escaping is separate from the stored DTO. Core identity may itself contain a relative path: it is private display data, not a safe log key.

Do not relay `QueryAnswer.answer`, `question`, `excluded_count`, arbitrary trace fields or exceptions. Candidate ordering is Core ordering; the shell must not rescore, sort, or present relevance as confidence. `complete` only means all displayed citations are supported. It does not claim all notes, every relevant result, or the answer were found. No candidate-to-conversation attach/approve/retry operation is provided.

### Safe terminal taxonomy

`INVALID_REQUEST`, `SCOPE_DENIED`, `POLICY_CHANGED`, `SOURCE_UNAVAILABLE`, `MALFORMED_SOURCE`, `STALE_SOURCE`, `SOURCE_BOUNDARY`, `DUPLICATE_IDENTITY`, `RESOURCE_LIMIT`, `BUSY`, `SESSION_INVALID`, `CANCELLED`, `INTERNAL_FAILURE`; bridge adds `CORE_UNAVAILABLE` and `CONTRACT_MISMATCH`. Unknown Core errors map to `INTERNAL_FAILURE`. No raw error message, filename, parser snippet, source count, timing-by-source or traceback is displayed or persisted. Errors have zero candidates. No-match is a successful unresolved retrieval, not a denial or system failure. The UI never reveals whether a denied note exists.

## 5. Acquisition, sensitivity and lifecycle

Core verifies binding/policy hash and exact roots before enumeration, then constructs explicit scope from policy workspace, five allowed prefixes, request ID and private ceiling. Missing/unknown/conflicting classification fails closed. Restricted sources and excluded folders never enter the index, graph, ranks, display or history. Note frontmatter cannot elevate or override the external classification policy. Request text is data, including instructions to ignore policy or summarize a note.

Use the accepted corpus helpers and parser. Add keyword-only optional controls to `inventory_sources`, `acquire_sources`, `build_corpus`, and their read helper: bounded bytes/count/deadline plus cooperative cancellation. Existing callers/defaults remain unchanged. The new application always supplies caps: at most 1,000 authorized Markdown files, 1 MiB per file, 16 MiB total acquired bytes, and 10 seconds of cooperative operation time. Reads stop at cap+1, including a file that grows while open; no unbounded `read()` on this path. Walk entry budget is 10,000, depth at most 32; failure is typed, not partial success. Check cancellation/deadline between directory entries, files and bounded read chunks, before indexing and after retrieval. These are prototype resource limits, not new recall benchmarks or guarantees that blocked OS I/O can be forcibly interrupted.

Capture an inventory, acquire exactly those bytes, parse in memory, instantiate `QueryEngine` with explicit authorized scope and a Core-owned provider sentinel whose only generation method raises a fixed failure. Call `search` only. Do not expose sentinel injection and do not initialize Gemini/Ollama/readiness/credentials. Recheck the complete authorized inventory, exact hashes and policy binding before publishing; a changed, added, removed, unavailable or replaced source rejects the whole result. Use normal current-source citation resolution, then independently validate each returned fingerprint/locator/excerpt against the verified source bytes. Do not set `engine._citations`, substitute a snapshot resolver, or call the benchmark. The result describes the revision validated during that request, not a perpetual promise about the live filesystem.

Reparse/symlink checks apply to the root and every ancestor/component traversed, not just the leaf. Reject junctions, escapes, case-colliding identities and duplicate explicit IDs. No filesystem proof here claims resistance to a privileged concurrent adversary replacing mount points after validation; the synthetic fixture is process-owned. A future private activation must separately establish a stable readable source boundary; this plan does not reopen the failed live-vault proof. Whole-result denial is acceptable when the authorized corpus contains a malformed note. Never show its name in the failure.

Core owns up to eight sessions; the CLI uses one. One admitted operation per session, no queue; repeated/cross-session request IDs cannot obtain another session's result. Core captures session instance/generation and request identity under a lock, releases the lock for I/O/retrieval, and checks cancellation, generation and binding again in the same critical section that publishes the terminal result. Cancel/reset/close and terminal publication have one ordered winner. Late success cannot resurrect a cancelled or superseded generation.

The controller has one active worker across conversation and recall. Recall can start only from IDLE with no prepared conversation, active dispatch, speech or pending reset. Introduce `start_recall`, `poll_recall`, and optional recall bridge injection; do not pass recalled bytes to conversation methods. CLI presents `RECALLING` and `RECALL_RESULTS` states separately. A second request while recalling returns BUSY. Failed recall does not poison subsequent conversation state.

`cancel` sets both token and Core cancellation, immediately hides pending/cached recall content, and shows "Cancellation requested" until the worker returns. `reset` invalidates Core generation, clears views and joins the worker before reporting ready; `close` also closes the Core recall session. Use the existing controller bounded worker-join discipline: if the worker does not quiesce within two seconds, show a fixed cleanup failure, admit no new work, and retain ownership of resources until termination. Do not delete the fixture underneath a live worker. No daemon worker silently survives a reported successful close. Publication that won before cancellation can be cleared, but already displayed terminal text cannot be erased from terminal scrollback.

Recall content exists only in the active process and its authorized local terminal display. Clear references on new recall/reset/cancel/close; no application log, trace, telemetry, history file, clipboard copy, JSON transcript, query hash or note fingerprint in public evidence. Memory deallocation is not physical-memory sanitization. Terminal scrollback remains an operator-controlled local surface, so private activation needs an appropriate local console; the current demo contains synthetic data only.

### Provider boundary

Personal Recall has no remote or local-model generation at all. Even public/internal candidates do not flow automatically to the existing conversation bridge. Private/mixed/local-only material cannot be declassified by an approval click, command wording, lower-ceiling retry or a standing grant. An absent/unavailable local model is not a recall failure and cannot trigger a remote fallback. A future synthesis request must be separately authorized, select the accepted exact destination before retrieval, rebuild a fresh immutable visible snapshot, and revalidate policy/bytes/approval at dispatch. Private or mixed requests may then use only an authorized accepted local path; otherwise they remain blocked. This plan neither asserts that a local path is currently activated nor activates it.

## 6. User-visible contract

Opt-in invocation: `python -m voice_shell.cli --core-mock --fixture synthetic --recall`. Existing flags/default behavior are unchanged; combining recall with `--destination gemini` rejects before fixture/source access. No natural-language automatic routing is added. The explicit `recall ` command is case-insensitive only for its command prefix; question text retains its original case and Unicode.

| Action/state | Required visible behavior |
|---|---|
| Startup | `PERSONAL RECALL / LOCAL / RETRIEVE ONLY / SYNTHETIC`; "Nothing is sent to a model."; IDLE help includes `recall <question>` |
| `recall Aurora launch` | Controller starts worker; "Searching local notes. Commands: poll, cancel, reset, help, quit."; no approval request |
| `poll` while pending | "Still searching"; no partial rows or raw diagnostics |
| Successful poll | "Candidates, not answers. Question remains unresolved." Ordered ranks, title, relative path, sensitivity, relevance labeled relative, verbatim escaped excerpt, source ID/kind, full revision fingerprint and heading/line locator; citation coverage and scope/top-five/lexical limitations |
| Empty or stop-word-only result | "No matching candidates in the authorized scope" or "No searchable terms"; coverage none, unresolved; never "the information does not exist" |
| Denied scope/policy | "Recall unavailable for this scope"; no note existence/count hints |
| Malformed/unavailable source | "Recall stopped: source could not be read safely"; safe category; no partial candidate list |
| Stale source/policy | "Sources or policy changed. Reset and search again." No automatic retry or stale result |
| Result `inspect <n>` | Render only the selected already validated DTO; label it the captured revision, not a newly opened live file; reject bad index; no external editor/URI launch |
| `cancel`, `reset`, `quit`, EOF, Ctrl-C | Clear recall view and follow section 5 cleanup. Normal quit/EOF exit 0; Ctrl-C exit 6; failed Core preflight or cleanup exit 7. Argparse usage errors remain exit 2 |
| Core missing/version mismatch | Fixed Core-unavailable message before reads; no mock recall fallback |
| `approve`, `retry`, `remove`, provider-like command during recall | State-invalid message; never sends data to conversation or a model |
| New recall after results | Discard previous DTOs, start a fresh request/inventory; no cache reuse |
| Ordinary question after results | Require `reset` first; then existing synthetic conversation flow. It has only its original fixture, no recalled context |

Reserve recall command syntax in every CLI state so it cannot accidentally become a conversation question when recall is disabled or busy. Strip/escape terminal control characters, ANSI/OSC, bidi formatting controls and embedded command-looking newlines for display; never execute content or create clickable file/protocol links from notes. Preserve the original DTO bytes/strings for validation. Help is state-specific and emitted only on an actual state change; existing usability fixes remain intact.

## 7. Exact proposed implementation path ceiling

These are the only candidate source/test/document paths proposed for future authorization. `M` = modify existing; `A` = add. Paths are relative to each repository and apply in the future dedicated checkouts, not the accepted frozen checkouts. A subset is allowed; any additional path requires a consolidated scope decision before editing.

| Repo | Kind | Exact path | Purpose |
|---|---|---|---|
| Core | M | `src/jarvis_core/personal_recall/__init__.py` | Add public version/application/DTO exports |
| Core | A | `src/jarvis_core/personal_recall/contract.py` | Frozen request/result/binding/session/cancel/error contracts |
| Core | A | `src/jarvis_core/personal_recall/application.py` | Authorization, local search orchestration, validation and lifecycle |
| Core | M | `src/jarvis_core/personal_recall/corpus.py` | Optional bounded/cancellable acquisition controls and component boundary checks |
| Core | A | `tests/unit/test_personal_recall_application.py` | Contract, privacy, scope, citation, race and resource matrix |
| Core | M | `tests/unit/test_personal_recall.py` | Preserve accepted proof behavior; additive acquisition regression cases only |
| Core | A | `docs/software/PERSONAL_RECALL_APPLICATION_V1.md` | Public API and semantic contract |
| Voice | M | `voice_shell/contracts.py` | Separate shell-owned frozen recall DTO/protocol |
| Voice | A | `voice_shell/recall_bridge.py` | Only new Core import surface and strict projection |
| Voice | M | `voice_shell/controller.py` | Optional recall lifecycle and worker ownership |
| Voice | M | `voice_shell/cli.py` | Opt-in command/state rendering |
| Voice | A | `voice_shell/recall_prototype.py` | Synthetic fixture ownership, scripted demonstration and teardown |
| Voice | A | `tests/voice_shell/test_recall_bridge.py` | Version/mapping/privacy and real Core integration |
| Voice | A | `tests/voice_shell/test_recall_controller.py` | Cancel/reset/close/concurrency and no speech/dispatch |
| Voice | A | `tests/voice_shell/test_recall_interactive.py` | Commands/rendering/demonstration/fixture cleanup |
| Voice | M | `tests/voice_shell/test_structural.py` | Exact fourteen-module inventory, new import boundary and no import side effects |
| Voice | M | `tests/voice_shell/test_core_bridge_structural.py` | Preserve old provider seam and add recall-specific isolation assertions |
| Voice | A | `docs/PERSONAL_RECALL_PROTOTYPE.md` | Operator instructions and rollback |

No changes to policy JSON, benchmark runner, query algorithms, ranking/tokenizer/identity/citation engine, conversation application, provider modules, dependencies, old prototype fixtures, real voice, `.gitattributes`, `.gitignore`, Git configuration or ACLs. If a regression exposes a necessary edit outside this list, stop with the whole diagnosed scope delta; do not weaken tests or redefine success.

Future evidence-only outputs, outside executable commits:

- Core coordination root `docs/evidence/v0.6/pr07-integration/candidate-manifest.json`.
- Core coordination root `docs/evidence/v0.6/pr07-integration/checks.json`.
- Core coordination root `docs/evidence/v0.6/pr07-integration/demo.txt` (synthetic display only).
- `.worktrees/v0.3.1-release/docs/handovers/v0.6/23-principal-engineer-personal-recall-integration-return.md`.
- Existing `docs/coordination/worklists/v0.5-prototype.json` and `docs/coordination/CURRENT_HANDOFF.md`, within role transition permissions only.

Generated runtime data: exclusive temp directories with prefix `jarvis-recall-prototype-` under the OS temporary directory; existing conversation fixture retains its own ownership. Each recall directory contains only the five approved-shaped roots, synthetic Markdown and `policy.json`. No private source copying. Tests may use pytest-owned temporary roots. Do not put evidence or temp outputs inside `.git` or stage them in either candidate.

## 8. Complete environment and executor route

[Verified] Core declares Python >=3.10, PyYAML >=6.0; development tools pytest >=8, Ruff >=0.5, mypy >=1.8, types-PyYAML >=6, and build backend setuptools >=68. Voice has no `pyproject.toml` at the accepted base and its shell is importable from its checkout. Installing the root legacy `requirements.txt` is unnecessary and prohibited for this task.

[Verified] `C:/Users/jmurr/Projects/AI-Operating-System/.venv/Scripts/python.exe` is Python 3.14.4 with PyYAML 6.0.3, pytest 9.1.1, Ruff 0.16.0, mypy 2.3.0, types-PyYAML 6.0.12.20260724 and pip 26.1.2. Setuptools is absent. The `v0.6-pr01/.venv` interpreter is 3.13.14 but lacks all those packages; do not select it merely because it is next to the candidate. These are inspected metadata, not a new runtime certification.

**Install arrangement:** no installation or acquisition is required. Use the populated root environment, explicit absolute Core `src` and Voice checkout paths, Python `-B` and a launcher that prepends the exact source locations before imports. Assert `jarvis_core.__file__`, `voice_shell.__file__` and both contract literals before every test/demo process. This prevents an older editable Core installation from winning import resolution. Do not run `pip install -e`, build isolation, or package upgrades to compensate for absent setuptools. If packaging becomes a requirement, that is outside this task. The operator guide must include the same source-pinning launcher, not rely on ambient `python` or an assumed editable installation.

The following PowerShell command is the exact proposed interactive entry after implementation (not runnable as a recall feature at today's base). The scripted demo substitutes `voice_shell.recall_prototype` and `['--demo']`. Engineering must copy this source-pinning setup into the operator guide and test that exact invocation:

```powershell
Set-Location 'C:/Users/jmurr/Projects/AI-Operating-System/.worktrees/v0.6-recall-voice'
& 'C:/Users/jmurr/Projects/AI-Operating-System/.venv/Scripts/python.exe' -B -c "import pathlib,runpy,sys; c=pathlib.Path('C:/Users/jmurr/Projects/AI-Operating-System/.worktrees/v0.6-recall-core/src'); v=pathlib.Path.cwd(); sys.path[:0]=[str(c),str(v)]; import jarvis_core,voice_shell; assert pathlib.Path(jarvis_core.__file__).resolve().is_relative_to(c.resolve()); assert pathlib.Path(voice_shell.__file__).resolve().is_relative_to(v.resolve()); from jarvis_core.personal_recall import PERSONAL_RECALL_CONTRACT_VERSION; from jarvis_core.conversation import CONVERSATION_CONTRACT_VERSION; assert PERSONAL_RECALL_CONTRACT_VERSION=='jarvis.personal-recall.v1'; assert CONVERSATION_CONTRACT_VERSION=='jarvis.conversation.v0.5.0'; sys.argv=['voice_shell.cli','--core-mock','--fixture','synthetic','--recall']; runpy.run_module('voice_shell.cli',run_name='__main__')"
```

Use the same setup for pytest: from the Core checkout, call `pytest.main(['tests','-q'])`; from the Voice checkout, call `pytest.main(['tests/voice_shell','-q'])`, propagating its exit code. Set source paths explicitly in each process and use owned writable temp/cache locations. Run Ruff over Core's changed Python files and Voice's changed runtime/tests; run mypy for Core with its existing `pyproject.toml`, and `mypy --strict` for Voice's four changed/new runtime modules plus `contracts.py`. Full-suite failures are diagnosed against the pinned bases inside the task, not hidden with deselection or weakened assertions.

**Native Windows is the required executor and closing environment.** Engineering implementation, complete offline gates, the operator demo and both Git commits remain one task. Use the existing native project interpreter. The ordinary native user `Mighty_Mouse/jmurr` is the required Git writer, through an approved native execution context; an agent sandbox is not assumed to possess that identity's rights. No elevation, ACL change or global trust edit is part of the plan.

[Verified] Read-only `icacls` inspection shows inherited full control for `Mighty_Mouse/jmurr` in both repositories' `.git`, alongside explicit deny entries for other SIDs. Voice ordinary Git inspection initially failed ownership validation as `CodexSandboxOffline`; command-scoped `-c safe.directory=<exact checkout>` allowed read-only inspection without persisting trust. Handoff 202 and Handoff 242 document earlier Git/LFS write failures. Current sandbox policy also treats `.git` as read-only. ACL display is not proof that a future executor can create a commit.

Before any implementation, the future authorization must name the native writer and include permission for two worktrees/branches, exact-path staging, local commits and owned synthetic temp cleanup. In that same Engineering task, native preflight resolves both Git common directories, refs/index/objects/worktree metadata and LFS temp access, checks identity (`whoami`), Git user identity without printing unrelated config, available hooks and signing requirements, free space and clean scoped status. Exercise the actual authorized worktree creation and verify it before code edits; if native Git cannot perform the authorized operations, fail the preflight before producing an uncommittable implementation. Do not bypass LFS filters, hooks, signing, deny ACLs or sandbox policy. A required host approval is routed once as `human_action`, with both repositories included; no serial per-file permission requests. The plan does not claim that such future approval has already been granted.

Git closure: stage only the changed paths in section 7; compare cached path sets against the allowlist; run whitespace validation; create one normal commit per repository on its pinned parent, no amend/rebase/merge. Record full parent/commit/tree plus cross-repository pair in the candidate manifest. Do not put either output commit's own hash inside that same commit. Evidence lives separately. Confirm both tracked trees/indexes clean and preserve pre-existing untracked evidence. Commit messages: `Add versioned local Personal Recall application` and `Integrate local Personal Recall into JARVIS prototype`.

**Linux responsibility:** optional synthetic-only development/test reproduction, not a prerequisite or a second task. It needs CPython >=3.10 with the same declared dependencies already installed, exact source trees, POSIX temp isolation and read/write permissions only for its own checkout/temp area. No Windows runtime or model artifacts are needed. Run the same path-pinned suites; POSIX symlink tests run there, Windows reparse/junction behavior must pass on Windows. Linux cannot attest Windows Git ACLs, native paths or final candidate freeze. Do not invent a Linux host/path or download dependencies when no such executor is assigned. The complete required route is Windows and has no Linux handoff dependency.

Cleanup: capture pre/post inventories of owned temp names and candidate paths. Remove only a directory whose recorded absolute ownership/root is verified and whose worker has stopped; verify absence, not just a successful delete call. Preserve failed-cleanup evidence and return failure if cleanup cannot be established. Do not delete any historical evidence, another run's fixtures, models or source notes. No global environment changes need rollback.

## 9. Working-prototype demonstration and operator rollback

Engineering must deliver both a scripted replay and the interactive command in section 6 using the same controller, bridge and Core application. `python -m voice_shell.recall_prototype --demo` creates its owned synthetic fixture, feeds the actual CLI commands, validates visible outcomes and returns a fixed exit status. It must not substitute a mock recall result. Test doubles are permitted only at failure/race injection seams. Ordinary conversation continues to use its accepted mock provider, separately from recall.

The recall fixture creates the five empty-approved-shaped directories and three UTF-8 notes: `02 Projects/Aurora.md` (explicit ID `recall-demo-aurora`, heading Launch, phrase "Aurora launch review is Thursday"), `04 Wiki (Resources)/Aurora checklist.md` (distinct explicit ID, shared Aurora terms), and `03 Areas/Restricted decoy.md` (unique token `forbidden-orchid`). The external generated policy classifies the first two roots private and the Areas root restricted; other required rules remain private. Include a hidden synthetic decoy and an excluded Sessions directory for boundary tests. No actual personal notes or sealed benchmark questions are reused. Exact fixture text and expected ordering are frozen in the test/harness, not hand-entered at demo time.

Operator guide must start with a copyable Windows setup using the existing root interpreter and exact future source paths, then these steps:

1. Launch the opt-in CLI. Expect the local/retrieve-only/synthetic banner and a ready prompt; no microphone permission, model startup or approval dialog.
2. Type `recall Aurora launch`, then `poll` until finished. Expect one or two ranked Aurora candidates (the fixture oracle fixes exact order), "Candidates, not answers", private sensitivity, revision fingerprints and heading/line citations. No spoken output.
3. Type `inspect 1`. Expect the same revision-bound passage, not a generated answer or an opened file.
4. Type `recall zzz-no-such-topic`, then `poll`. Expect zero candidates and an unresolved/no-match message. Searching `forbidden-orchid` also shows no candidates and reveals no restricted-source identity or count.
5. Type `recall Aurora`, then `cancel`; the deterministic replay uses a barrier to ensure cancellation wins. Interactive cancellation may arrive after completion; it must honestly report that outcome and clear the visible view.
6. Type `reset`, then an ordinary fixture question. Expect the existing visible-context approval flow with only the original conversation fixture. Recall sources never appear in its prepared context. Decline, reset and quit.
7. Scripted adversarial demo additionally injects a changed fixture revision, malformed fixture and missing Core: each must show its safe failure, suppress rows, and clean up. These injections are synthetic-only test actions, not operator edits to personal notes.

Success means real API/bridge/CLI flow, expected synthetic results, no provider/network/device call from recall, no retained fixture or worker, and unchanged source fixtures before their owned cleanup. `demo.txt` contains only synthetic rendered output; checks record categorical outcomes and candidate identities, never private queries or note digests.

Rollback for the nontechnical operator: type `quit` or Ctrl-C and close the terminal if a cleanup failure leaves it blocked; restart the original CLI command without `--recall` to use the accepted mock conversation. No provider, device or live-vault activation needs undoing. Engineering preserves both candidate worktrees/commits for review; any later removal requires a separate explicit cleanup decision. Do not recommend `git reset --hard` or deleting accepted evidence.

## 10. Consolidated adversarial and regression matrix

Every row is mandatory evidence in the single Engineering return. Deterministic barriers/events establish race ordering; do not use sleeps as race assertions. `C` means Core application tests, `B` bridge tests, `L` controller tests, `U` interactive tests, `S` structural tests (exact files in section 7).

| ID | Gate / adversarial inputs | Required oracle | Owner |
|---|---|---|---|
| R01 | Missing/wrong API version, old editable package, absent Core | Fail before any fixture read; exact source roots/versions asserted | B/U |
| R02 | Frozen nested DTOs; dict/list substitutions; unknown keys; bool limits; blank/oversized query; NaN/inf relevance; oversized fields | Reject closed-schema violations; no silent truncation of provenance | C/B |
| R03 | Correct explicit scope; missing workspace/policy/ceiling; changed policy bytes/ID/root | Only exact binding admits; no allow-all or broader read | C |
| R04 | Public/internal/private/restricted/unknown/conflicting labels; hostile frontmatter classification | External policy wins; restricted/unknown never index or display | C |
| R05 | Hidden/excluded directories, non-Markdown, absolute/traversal/UNC/drive paths, nested junction/symlink, root reparse, case aliases | Deny/skip according to accepted policy; no escaped byte read | C |
| R06 | Duplicate explicit IDs among authorized notes; excluded decoy ID collision | Authorized duplicate fails safely; excluded identities cannot perturb valid results | C |
| R07 | Hidden high-scoring decoys/relationships and same query with/without denied corpus | Identical allowed ordering/DTOs and no excluded count/title/ID in errors or trace | C/B |
| R08 | Prompt injection, `summarize`, relationship wording, remote-send text | Always SEARCH/retrieve-only; zero summarize/provider/dispatch calls | C/L/U |
| R09 | Exact lexical/metadata/phrase matches and score ties, case/Unicode/CRLF | Repeated result order/locators deterministic; relevance never confidence | C/B/U |
| R10 | No terms, no matches, missing-answer query with plausible matching candidates | All remain unresolved/no answer claim; no false assertion of absence | C/U |
| R11 | Valid ID vs path-derived identity; rename/cross-workspace source | Preserve Core identity semantics and expose weaker path-derived kind | C/B |
| R12 | Forged fingerprint/locator/excerpt, heading hierarchy drift, line off-by-one, CRLF-byte change | Reject mismatched revision/passage; never display a valid-citation label | C/B |
| R13 | Mutation/removal/addition before acquisition, during reads, after search before publication | Whole result stale/unavailable; no partial stale rows or auto retry | C |
| R14 | Parse failure/invalid UTF-8/unreadable file; exceptions containing secret canary/path | Fixed category only; candidates empty and no secret in stdout/stderr/evidence | C/B/U |
| R15 | Coverage complete/partial/incomplete/none projections and unsupported references | Preserve distinction; never imply factual answer coverage; malformed supported locator denied | B/U |
| R16 | Row/byte/query/depth/entry/deadline caps; growth while read; max sessions | Fixed RESOURCE_LIMIT; bounded reads; no partial result or uncontrolled worker creation | C/L |
| R17 | Import all runtime modules with file/thread/socket creation traps; AST import graph | No import-time effects; exact Core allowlist; no legacy/provider/acquisition seam | S |
| R18 | Trap DNS/socket/HTTP/subprocess/provider credentials/readiness/mock generation on recall path | All call counts zero including failures and hostile input; no model readiness dependency | C/B/L/U |
| R19 | Conversation before/after recall, approve/retry/remove in recall state, Gemini flag combination | No recalled bytes in prompts/history/approval; Gemini reject before reads | L/U |
| R20 | Cancel before start, during acquisition, before/after publication; double cancel | One ordered terminal winner; acknowledged request is not false cancellation; stale success suppressed | C/L |
| R21 | Reset during recall, immediate new request, old poll/completion | Generation isolation; no old data renders in new session; reset waits for cleanup | C/B/L |
| R22 | Close/EOF/Ctrl-C during worker; worker refuses to finish; fixture teardown failure | Honest cleanup failure; no ready/closed success while worker remains; no delete under worker | L/U |
| R23 | Double start, conversation/recall overlap, simultaneous poll/cancel/reset; cross-session/replayed refs | One worker, no queue, no result theft, no deadlock or invalid view publication | C/B/L |
| R24 | ANSI/OSC, bidi, newlines, command text, fake links in title/path/excerpt/reason | Escaped inert deterministic text; immutable provenance preserved; no action/open/speech | B/U |
| R25 | Typed commands in all states, invalid inspect index, disabled recall prefix, uppercase prefix, whitespace | State-valid guidance; invalid recall never falls through to conversation | U |
| R26 | Two identical scripted real-Core demos and interactive operator journey | Same semantic display (exclude random opaque refs/temp paths); correct exit/status and visible flow | U |
| R27 | Snapshot fixtures before/after; injected creation/load/close/delete failures; pre-existing unrelated temp dirs | No source writes; remove only owned synthetic fixture; unrelated data unchanged; no silent cleanup pass | U |
| R28 | Capture logs, stderr, public evidence and history with secret canaries | No content/IDs/queries/digests beyond deliberate synthetic display; closed evidence schema | C/B/U |
| R29 | Existing complete Core and Voice test suites, query/Project Resume/conversation and old structural boundaries | All pass against paired candidate sources; no benchmark or device test execution | Engineering |
| R30 | Ruff/mypy, compile/import, worklist, links, UTF-8, whitespace, staged path manifests and native Git freeze | Passing gates; exact two commits/trees/parents; no out-of-scope staged path | Engineering |

Run focused tests during correction; then complete Core `tests` and Voice `tests/voice_shell` suites once against the final paired source state, plus Ruff and mypy using the repository's existing configuration (Voice strict checks for changed runtime modules). Python compile checks should compile in memory or use owned test-cache directories. Run the deterministic fixture demo twice and compare semantic output; this is not a new personal recall benchmark. Repeat a complete gate only after changes invalidate it. Do not invoke the live benchmark script, PT63 replay/device pilot or any live provider gate. Platform-only skips require recorded reason; Windows junction/reparse and lifecycle/privacy gates may not be waived. Existing accepted corpus/proof unit tests remain mandatory synthetic regression tests.

## 11. One proposed Engineering task and review route

**Proposed ID:** `V06-PR-07` (not entered or authorized by the CTO).
**Owner:** Principal Engineer. **Reviewer:** Chief Architect / CTO, with Chief of Staff routing.
**Dependency:** Chief of Staff accepts PR06 and records the Product Owner's implementation decision.
**Outcome:** Native-Windows runnable, fixture-only local recall in the accepted text prototype, exact contracts and paths above, complete adversarial evidence, operator demonstration, two immutable paired candidate commits and one Handoff 23.

The authorization envelope must expressly include native writer access, worktree/branch creation, the eighteen candidate paths, synthetic temp creation/deletion, local tests/demo, two normal local commits and the six evidence/coordination outputs in section 7. It must expressly exclude all private reads, providers, device activation, acquisition, vault/policy/manifest edits, merge and push. This is one outcome-sized task: preflight, code, in-scope defect correction, complete tests, demo and Git closure are not separate discovery tasks. No task is marked accepted by its author.

Ready-for-review evidence must include every R01-R30 disposition, exact commands/runtime/import provenance, both candidate identities and per-path hashes, staged-set verification, source/temp integrity, actual Windows demonstration outcome and a privacy-safe residual-risk statement. Do not substitute an archive-only return for the required commits. If native write approval is unavailable, identify the single `human_action` blocker before implementation. A missing approved dependency/source capability is `external_capability`; an extra path, changed retrieval algorithm, live vault or synthesis requirement is `scope_change_required`. Ordinary test defects stay inside PR07.

Chief of Staff must review this complete package once, consolidate any corrections, then route the concrete implementation decision to the Product Owner. Accepting this document alone does not activate PR07, a provider, a live-vault read or a frontend. The Product Owner needs no action until that independent review is complete.

## 12. Planning evidence and limitations

[Verified] Completed read-only checks: initial and in-progress worklist validation; exact Git commit/tree/parent resolution for both selected bases; tracked/untracked status inspection; source inventory and interface inspection listed in section 3; actual policy/acquisition/search/identity/citation and CLI/controller/structural code inspection; installed runtime metadata; Git metadata ownership/ACL inspection. A `-B` import-only preflight using the populated root environment resolved Core and Voice to the exact inspected checkouts and reported `jarvis.conversation.v0.5.0` / `jarvis.query.v0.3.1`; it read no notes and ran no application. Commands were routed through RTK after reading the local command rule. Command-scoped Git trust was used only for the exact Voice checkout and repository during read-only inspection; no persistent Git setting was changed.

[Verified] No private vault/evidence contents were read, and no benchmark, device, provider, implementation or Git mutation was run. The empty recall-local environment and native writer requirement are explicitly resolved by the execution route in section 8, not hidden as assumptions about future capabilities. Linux is optional and unprovisioned. Future native worktree/commit operations remain permission-gated, so this is an implementation-ready design, not an execution authorization or a claim of pre-exercised write permission.

[Inferred] A fixture-only first integration is the smallest route that meets Handoff 21's offline demonstration and preserves the frozen proof: it validates the user-facing cross-repository workflow without reopening source-availability failures. It will not yet let the Product Owner search the actual vault. That later activation is a material boundary and is stated here explicitly rather than presented as completed usefulness.

[Recommended] Residual limitations accepted for this proposal: lexical ranking may miss paraphrases; top-five retrieval does not answer questions; terminal scrollback cannot be revoked; filesystem freshness is point-in-time; blocked filesystem I/O is cooperatively cancellable only; no live-vault stability or voice usability claim is made. Any request to remove these limitations must be separately scoped before implementation.

Artifacts produced by PR06: this Handoff 22 plus its own worklist status/history and canonical baton update only. No candidate commit produced.

[Verified] Final documentation checks passed on 2026-09-24: active worklist validator; strict UTF-8 and explicit-file whitespace checks on all three outputs; all 15 Markdown links in the handoff and baton resolve; the baton is 32 lines; the matrix has 30 gates and the candidate ceiling has 18 paths. Scoped Git diff whitespace checks passed in both documentation locations; explicit-file checks cover the new/untracked handoff as well. PR06 is `ready_for_review`; no PR07 worklist entry or dependent authorization was created. No implementation test result is claimed by these documentation checks.

**Exit:** Ready for Chief-of-Staff consolidated review. No dependent task authorized.
