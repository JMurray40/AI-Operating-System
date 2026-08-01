# Handoff 07 — CTO to Principal Engineer: Conversation Implementation Brief

| Field | Value |
|---|---|
| Sender | Chief Architect / CTO |
| Receiver | Principal Engineer |
| Milestone | v0.5 — Visible-Context Conversation |
| Date | 2026-08-01 |
| Status | **Ready for Chief-of-Staff validation; implementation not authorized** |
| Repository | `AI-Operating-System` |
| Drafting base | Clean `main@5224d6ff4ddb9b5ef1670c820cd774ac66d80607` |
| Engineering branch | `feature/v0.5-visible-context-conversation` |
| Exact implementation base | The clean `main` commit containing this brief and all accepted v0.5 planning/provider decisions; Chief of Staff must validate, commit, and pin its full SHA before creating the branch |
| Released prerequisites | v0.3.1 Query Trust Contracts; v0.4 Project Resume |
| Approved real provider | Google Gemini Developer API / native model `gemini-3.5-flash-lite` |
| Required activation handoff | Handoff 08 — Chief of Staff validation and implementation authorization |
| Required engineering handoff | `docs/handovers/v0.5/09-principal-engineer-to-cto-conversation-engineering-review.md` |

## 1. Objective and architecture disposition

Implement the smallest trustworthy multi-turn conversation slice over released Jarvis
Core. A user must be able to prepare a turn, inspect and remove authorized context, approve
an immutable digest-bound disclosure, dispatch one non-streaming request, and distinguish
validated source-supported claims from inference, model knowledge, unknowns, conflicts, and
limitations.

The release surface is an interactive/scripted CLI plus a versioned in-process application
API. Conversation state is bounded, process-local, and non-durable. The vault and Git
repositories remain read-only. There is no tool, write, plugin, MCP, agent, automation,
attachment, UI, public server, semantic retrieval, streaming, provider fallback, durable
transcript, or memory-proposal capability.

**Architecture disposition: READY FOR CHIEF-OF-STAFF VALIDATION ONLY.**

This brief becomes effective only after the Chief of Staff:

1. validates the complete documentation package;
2. commits it to clean `main`;
3. records the exact full commit SHA in a separate implementation authorization;
4. creates the named Engineering branch/worktree from exactly that commit; and
5. states the precise authority for dependencies, network documentation checks, and any
   real-provider evidence.

The Principal Engineer must not begin from `5224d6f`, “latest main,” the coordination
worktree, the historical conversation branch, or the separate Voice Shell repository.

## 2. Authoritative inputs

Read in this order:

1. [Project Control](../../coordination/README.md)
2. [v0.5 Handoff Index](README.md)
3. [Product Owner scope approval](05-product-owner-to-cto-conversation-scope-approval.md)
4. [Product Owner Google provider authorization](06-product-owner-to-cto-google-provider-authorization.md)
5. [Accepted requirements](../../software/V0.5_VISIBLE_CONTEXT_CONVERSATION_REQUIREMENTS.md)
6. [Accepted architecture](../../software/V0.5_VISIBLE_CONTEXT_CONVERSATION_ARCHITECTURE.md)
7. [Accepted acceptance tests](../../product/V0.5_VISIBLE_CONTEXT_CONVERSATION_ACCEPTANCE_TESTS.md)
8. [Historical candidate assessment](../../software/V0.5_HISTORICAL_CONVERSATION_CANDIDATE_ASSESSMENT.md)
9. [ADR-0010](../../adr/ADR-0010-AI-Providers-Are-Accessed-Through-A-Versioned-Abstraction.md)
10. [ADR-0012](../../adr/ADR-0012-Query-Engine-Is-A-Layered-Deterministic-Pipeline.md)
11. [ADR-0014](../../adr/ADR-0014-Retrieval-Relevance-Is-Separate-From-Answer-Confidence.md)
12. [ADR-0015](../../adr/ADR-0015-Authorization-Precedes-Retrieval-And-Graph-Expansion.md)
13. [ADR-0016](../../adr/ADR-0016-Citations-Bind-Passages-To-Source-Revisions.md)
14. [ADR-0017](../../adr/ADR-0017-Stable-Source-Identity-Is-Separate-From-Location.md)
15. [ADR-0018](../../adr/ADR-0018-Project-Resume-Uses-Exact-Tiered-Project-Identity.md)
16. [ADR-0019](../../adr/ADR-0019-Project-Resume-Uses-Explicit-Authority-Temporal-And-Conflict-Ordering.md)
17. [ADR-0020](../../adr/ADR-0020-Project-Resume-Claims-Require-Validated-Evidence-And-Two-Hard-Budgets.md)
18. [ADR-0021](../../adr/ADR-0021-Repository-Activity-Is-A-Request-Scoped-Local-Read-Only-Git-Capability.md)
19. [ADR-0022](../../adr/ADR-0022-Conversation-Is-A-Session-Only-Application-Layer.md)
20. [ADR-0023](../../adr/ADR-0023-Conversation-Uses-Immutable-Visible-Context-Snapshots.md)
21. [ADR-0024](../../adr/ADR-0024-V0.5-Uses-Normalized-Non-Streaming-Provider-Dispatch.md)
22. [Security Threat Model](../../reviews/SECURITY_THREAT_MODEL.md)
23. released implementation and tests at the future pinned base.

The Product Owner decisions, accepted ADRs, requirements, and this final brief control over
the draft Chat PRD and historical candidate. Provider facts are time-sensitive; Handoff 06
controls the approved profile, while current official Google documentation must be
reverified at the separately authorized preflight and evidence gates.

## 3. Base, branch, and workspace preconditions

The Chief-of-Staff implementation authorization must fill this block before Engineering:

```text
validated_main_commit: <full 40-character SHA containing Handoff 07>
engineering_branch: feature/v0.5-visible-context-conversation
engineering_worktree: <absolute path>
worktree_clean: true
branch_head_equals_validated_main_commit: true
historical_conversation_commit_is_ancestor_of_validated_base: false
historical_conversation_content_in_worktree: false
historical_conversation_commits_cherry_picked: false
voice_shell_content_present: false
dependency_acquisition_scope: <explicitly authorized or none>
live_provider_scope: none unless separately activated
```

The Principal Engineer independently verifies and records all values. Any mismatch is
blocking. Do not overwrite unrelated user changes or use a dirty worktree as a candidate.

## 4. Frozen product and provider scope

### 4.1 Product surface

- Add `jarvis chat` interactive and deterministic scripted modes.
- Expose the same behavior through a versioned in-process application API.
- Require explicit workspace scope and allow optional exact project selection.
- Use a two-phase `prepare` then `dispatch` flow for remote turns.
- Keep all session, snapshot, approval, response, and trace state in memory only.

### 4.2 Google profile

The domain identity is:

```text
provider_id: google-gemini-developer-api
model_id: gemini-3.5-flash-lite
host: generativelanguage.googleapis.com
scheme: https
operation: generateContent
streaming: false
thinking_level: minimal
maximum_input_tokens: 64000
maximum_output_tokens: 8000
timeout_seconds: 60
automatic_retries: 0
requests_per_approval: 1
maximum_estimated_cost_usd_per_request: 0.05
maximum_release_evidence_spend_usd: 10.00
```

The implementation must keep provider and native model identity separate. Do not use a
LiteLLM composite model string as domain identity. The request path and authentication
header must be isolated in the Google adapter, verified from then-current official Google
REST documentation, recorded with a version/date, and restricted to the exact approved
host, API version, native model, and complete-response operation. No arbitrary base URL,
endpoint override, cross-host redirect, same-host redirect, proxy inheritance, or alternate
operation is permitted in release mode.

Only these Google request capabilities are allowed:

- text-only content necessary for the deterministic approved prompt;
- fixed system/safety instruction representation;
- bounded generation configuration required for the approved output reserve; and
- `thinking_level=minimal` using the currently documented field shape.

The adapter must reject or omit streaming, Live API, grounding, URL context, file search,
files/media, cached content, tools/function calls, code execution, computer use, stored
interactions, datasets, feedback/log sharing, fallback, and hidden retries. Deprecated or
unsupported sampling parameters are omitted, not simulated.

The credential comes only through a typed credential-provider interface whose production
implementation reads `GEMINI_API_KEY` from the process environment at dispatch preflight.
Missing credential yields typed `unavailable_credential` before retrieval or dispatch.
Tests inject canaries and fake providers; they never read a live key.

Remote sensitivity eligibility is exactly:

| Sensitivity | Eligibility |
|---|---|
| `public` | Eligible after all checks and per-turn approval |
| `internal` | Eligible after all checks and per-turn approval |
| `private` | Denied before retrieval for this destination |
| `restricted` | Denied before retrieval for this destination |
| missing/unknown | Denied before retrieval |

The approval display must disclose the then-current Google retention/abuse-monitoring
terms. Do not claim zero data retention. Optional logging, sharing, datasets, feedback,
grounding, explicit caching, and stored interactions remain disabled or unused.

### 4.3 Hard exclusions

Do not implement Ollama, another real provider, automatic fallback, general provider
registry discovery, streaming/event deltas, attachments, multimodal input, durable storage,
resume/archive/search/export/delete transcripts, memory proposals, semantic retrieval,
tools, plugins, MCP, agents, automation, browsers/connectors, vault writes, voice, GUI,
public HTTP, provider-managed chat sessions, or background calls.

## 5. Required additive architecture

Add one cohesive package without moving conversation state into `QueryEngine`:

```text
src/jarvis_core/conversation/
    __init__.py
    contract.py
    request.py
    session.py
    references.py
    context.py
    snapshot.py
    approval.py
    prompt.py
    application.py
    results.py
    evidence.py
    render.py
    trace.py
```

Extend providers through narrow modules such as:

```text
src/jarvis_core/providers/
    conversation.py
    credentials.py
    google_gemini.py
    transport.py
```

Module names may differ when a cleaner arrangement is justified in the Engineering Review,
but these boundaries may not collapse:

- `session`: bounded volatile state and deterministic eviction only;
- `references`: pure visible resolution/ambiguity logic over authorized session state;
- `context`: released authorized query/evidence services, never post-filtered retrieval;
- `snapshot`: canonical immutable serialization and digest;
- `approval`: digest-bound approval validation and expiry;
- `prompt`: deterministic content-bearing request projection and complete budget;
- `application`: orchestration and terminal-state machine only;
- `evidence`: claim-to-current-citation validation, coverage/conflict/limitation assembly;
- `render`: common semantic result to safe text/JSON;
- `trace`: safe event allowlist, not chain-of-thought;
- `conversation provider protocol`: provider-neutral complete-response contract;
- `credentials`: opaque secret retrieval boundary;
- `transport`: injected request runner for timeout, cancellation, capture, redirect, proxy,
  malformed, overflow, and redaction tests;
- `google_gemini`: the sole Google wire-format translation boundary.

Do not copy the historical conversation package wholesale. Port only individually reviewed
ideas and write new tests against released contracts.

## 6. Released contracts to reuse without weakening

| Released contract | Required use |
|---|---|
| `AuthorizationScope` and authorized views | Destination-aware source filtering before candidates/graph/context |
| Stable `source_id` and duplicate-ID failure | Session focus, snapshot items, citations |
| Mandatory current `source_root` | Prepare, pre-dispatch, retry, and pre-emission validation |
| Query passage/locator/evidence service | Exact fingerprints, excerpts, headings/lines and current-byte checks |
| `relative_relevance` | Discovery/ranking only; never answer assurance |
| ADR-0019 authority/conflict rules | Generated claim support and unresolved conflict visibility where applicable |
| ADR-0020 budget and coverage rules | Full prompt/output accounting and supported/incomplete distinction |
| Project selection resolver | Optional exact project scope; no relevance/fuzzy guess |
| Released text/JSON conventions | Stable semantic parity and exit behavior |
| Read-only repository boundaries | No canonical or reachable Git mutation |

Project Resume may supply reusable services but is not silently inserted as conversation
context. ADR-0021 grants no provider network authority and no new Git command.

## 7. Versioned contracts

Use new explicit versions, with exact strings documented before first writer fixtures:

```text
CONVERSATION_CONTRACT_VERSION = "jarvis.conversation.v0.5.0"
CONTEXT_SNAPSHOT_VERSION = "jarvis.conversation-context.v0.5.0"
EGRESS_APPROVAL_VERSION = "jarvis.conversation-egress.v0.5.0"
PROMPT_CONTRACT_VERSION = "jarvis.conversation-prompt.v0.5.0"
PROVIDER_CONTRACT_VERSION = "jarvis.provider-complete-response.v0.5.0"
CONVERSATION_TRACE_VERSION = "jarvis.conversation-trace.v0.5.0"
GOOGLE_ADAPTER_VERSION = "jarvis.provider.google-gemini.v0.5.0"
```

### 7.1 Request and session

`PrepareTurnRequest` is frozen and contains request ID, session ID, workspace ID,
authorization scope, mandatory source root, user text, optional exact project selector,
provider profile, explicit evaluation time, context/prompt/output budgets, history limits,
trace request, and contract version.

Session IDs are random non-semantic identifiers. Public turn numbers start at 1. Request,
snapshot, approval, and attempt IDs are distinct. Session history has hard turn/token/byte
limits; deterministic eviction is shown to the user and cannot retain hidden provider or
source content.

### 7.2 Context snapshot

`ContextSnapshot` is immutable and canonically serialized. It binds:

- request/session/workspace identity and normalized user input;
- visible reference-resolution assumptions;
- provider, model, exact endpoint policy, thinking level, timeout, retry count, feature
  disable set, input/output limits, and their versions;
- policy and authorization summaries;
- ordered context items with stable ID, path/title, sensitivity, fingerprint, full locator,
  bounded excerpt, selection reason, relative relevance when applicable, and token count;
- visible user exclusions, safe omissions, and budget accounting;
- prompt-template, assembler, history-serialization, token-estimator,
  safety-instruction, and output-reserve versions plus output-reserve value;
- versioned price table and per-request cost ceiling; and
- explicit evaluation time.

The SHA-256 digest covers the exact canonical semantic serialization and excludes only
declared diagnostics/timings. Context removal creates a new object and digest.

### 7.3 Approval

`EgressApproval` binds actor confirmation, request and snapshot digest, workspace,
destination/model/role, every prompt/provider/policy version and bound value, approval time,
expiry, one permitted request, and approval contract version. It is in-memory and cannot be
replayed across workspace, session, request, snapshot, destination, model, policy, version,
or expiry. There is no workspace-level “always approve.”

### 7.4 Provider request and result

The provider-neutral request separates:

1. deterministic approved content-bearing fields;
2. allowlisted transport metadata;
3. opaque credential transport; and
4. local diagnostics excluded from the wire.

The Google adapter must prove exact content projection. It may add only the explicitly
allowlisted HTTPS method/path/host headers and opaque API-key header. It must reject
undeclared fields, redirects, proxies, telemetry, fallback, and hidden retries.

The normalized result includes one of `completed`, `failed`, `cancelled`, or `blocked`;
bounded text when valid; provider/model/adapter identities; usage with reported/estimated/
unknown provenance; cost with currency/rate-table version; safe finish reason; timings; and
redacted error code. Raw provider payloads never cross the adapter boundary.

### 7.5 Answer evidence

Each material claim is `fact`, `inference`, `model_knowledge`, `unknown`, or `assumption`.
Facts require current valid citations. Inferences cite all material premises. Model
knowledge is visibly not vault-supported. Empty excerpts, note-only citations, stale
fingerprints, incomplete references, and `0-0` locators cannot support claims.

Answer coverage is `complete`, `partial`, `incomplete`, or `none`, with supported,
incomplete, and conflicting counts and visible limitations. Retrieval relevance and
qualitative evidence assurance remain separate; no numeric answer confidence is emitted.

## 8. Required turn ordering and fail-closed behavior

Remote turns must follow exactly:

1. validate immutable request, workspace, source root, provider profile, limits, and
   credential availability;
2. determine destination eligibility and apply sensitivity/source authorization before
   candidate generation and graph expansion;
3. resolve visible references without using excluded state;
4. retrieve, rank, expand, budget, and validate current source bytes;
5. create and display the complete immutable context snapshot;
6. apply each user removal by creating and displaying a new snapshot;
7. acquire approval bound to the final digest and all prompt/provider inputs;
8. revalidate approval, destination/policy, credential presence, cost ceiling, source-root
   confinement, current bytes, locators, excerpts, prompt inputs, and versions;
9. deterministically assemble content-bearing request fields and prove the complete input
   budget;
10. dispatch exactly once through the Google adapter;
11. parse and bound the response, then validate claim support and current citations;
12. render safe text/JSON and append only bounded in-memory session state.

Any failure prevents every later step. A live credential check occurs before retrieval so a
missing key cannot cause private discovery work. Secret values are never retained. No
provider/network call occurs before step 10.

Exact retry reuses the same snapshot digest and creates a new attempt ID, but repeats every
step-8 validation. Drift blocks retry and requires a new prepare. Changed input, context,
provider, role, workspace, or configuration is a new request.

## 9. CLI behavior

Provide documented commands for:

- interactive conversation;
- deterministic scripted mock conversation;
- preparing and printing a numbered context manifest;
- removing context by stable displayed item ID;
- explicitly approving or declining remote dispatch;
- cancelling an active attempt;
- inspecting bounded session history and safe trace;
- retrying the exact approved snapshot; and
- resetting the session.

Remote scripted mode must require an explicit non-interactive approval artifact/value bound
to the exact prepared snapshot; it cannot infer approval from a flag default, piped input,
environment, or workspace setting. Avoid printing secret values, absolute private paths,
raw errors, raw payloads, message bodies in trace, or hidden context.

Text and JSON must share one semantic result, terminal status, coverage, citations,
limitations, usage/cost provenance, and one-based turn number. Exit codes distinguish
success, user decline/cancel, policy block, unavailable provider/credential/network,
validation failure, and internal failure without using raw provider status as the public
contract.

## 10. Transport and dependency boundary

Prefer a small audited HTTP transport with injectable test seam, disabled environment
trust/proxy inheritance, redirect following off, strict TLS verification, bounded request
and response bodies, connect/read/write/pool timeouts, and cancellation support. If a new
runtime dependency is required, Engineering must:

1. stop until the Chief-of-Staff implementation authorization explicitly permits its
   acquisition;
2. justify why the standard library cannot satisfy cancellation and transport controls;
3. pin or bound it consistently with project policy, record transitive dependencies and
   licenses, and update packaging/recovery documentation;
4. prove the provider SDK, build backend, LiteLLM, or unrelated client stack was not added;
   and
5. exercise installed-wheel behavior in an isolated environment.

Do not install a Google SDK merely for convenience. A SDK is permitted only by a new
explicit CTO/Chief-of-Staff correction after demonstrating that it cannot introduce hidden
retry, fallback, caching, telemetry, endpoint, or content behavior.

## 11. Implementation work packages

### WP1 — Contracts and offline application core

Implement frozen types, volatile bounded session, visible reference resolution, authorized
prepare pipeline, immutable snapshot/digest, context removal, approval validation, prompt
projection, terminal state machine, evidence validation, renderers, trace, and mock adapter.
Complete C01–C12 and C16–C30 offline where applicable.

### WP2 — Google adapter without live calls

Implement credential interface, injected transport, exact Google request/response
translation, endpoint/redirect/proxy/feature denial, timeout/cancellation, usage/cost, and
redaction. Use fake transport and a local capture server only. Complete C13–C15 and all
provider degraded cases without a real key or internet.

### WP3 — CLI, benchmarks, packaging, recovery, and documentation

Add the CLI surface, deterministic fixtures, benchmark harness, installed-wheel smoke,
uninstall/reinstall/recovery procedures, privacy/operator guide, provider configuration
guide, and complete regression coverage. Benchmark direct repository-root commands must
fail visibly on import/startup errors and retain completion markers and raw samples.

### WP4 — Separately activated real-provider evidence

Do not execute this work package under the general implementation authorization. It
requires a later explicit activation confirming a billing-enabled Google project, accepted
credential handling, current model/path/terms/pricing, logging/sharing/caching settings,
private-data boundary, request list, and remaining USD 10.00 evidence budget.

Only `public` or `internal` synthetic/approved evidence may be sent. Never send private,
restricted, unclassified, pilot, or canonical content without a separately named grant.
Stop before either the USD 0.05 request ceiling or USD 10.00 cumulative ceiling can be
exceeded.

## 12. C01–C30 implementation/evidence map

| IDs | Required Engineering evidence |
|---|---|
| C01–C02 | Session lifecycle, one-based numbering, API/CLI semantic equivalence, process-exit non-persistence |
| C03–C05 | Missing-scope fail-closed, pre-retrieval authorization, exact project selection, excluded-source non-disclosure |
| C06–C08 | No-network prepare, complete manifest, immutable removal, canonical snapshot determinism |
| C09 | Tamper/replay/cross-workspace/expiry tests; mutate every bound prompt/provider input and version after approval and prove no prompt assembly/dispatch |
| C10–C11 | Current-byte/path/symlink/mutation failures and complete prompt/output hard-budget boundaries |
| C12 | Indirect prompt-injection corpus across body, metadata, links, code, user text, and provider output |
| C13 | Local capture comparison of exact content-bearing fields; independent allowlist checks for method/path/host/headers, opaque credential, redirects, proxies, telemetry, fallback, and undeclared fields |
| C14–C15 | Shared mock/Google conformance; secret canaries through prompt/state/trace/error/evidence scans |
| C16–C20 | Claim-to-passage validation, metadata evidence, taxonomy, coverage/conflicts/limitations, relevance-confidence separation |
| C21–C24 | Exact retry/drift, cancellation/timeout races, redacted failure classes, usage/cost provenance |
| C25–C27 | Safe Markdown/control rendering, trace allowlist, cross-workspace concurrency/isolation |
| C28–C30 | Vault/repository immutability, absence of transcript/provider memory, complete released regressions |

No aggregate pass waives a failed security case. Historical tests or benchmark numbers do
not count.

## 13. Performance and benchmark protocol

Create a direct repository-root benchmark for deterministic `prepare` at 100, 500, 1,000,
and 5,000 notes. Baseline and candidate must use equivalent fixtures, queries, scopes,
construction-plus-prepare boundaries, warm-ups, run counts, percentile method, Python,
machine, and load conditions. Retain all raw timing and peak-memory samples and independently
recompute p50/p95/p99.

Gates:

- 5,000-note prepare p95 below 2 seconds;
- unchanged query stages no more than 20% slower than their equivalent accepted baseline;
- conversation application overhead excluding retrieval/provider p95 below 250 ms;
- controlled-adapter cancellation acknowledgment p95 below 500 ms;
- hard limits prevent unbounded history, traversal, context, prompt, response, concurrency,
  time, or memory behavior.

Real-provider latency, usage, and cost are separately reported by attempt. Provider delay
cannot hide application latency. A blocked/not-found/mock/post-completion-chunking path is
not successful real-provider evidence.

## 14. Test, privacy, and security minimums

Tests must include positive, negative, boundary, property, compatibility, concurrency,
fault-injection, adversarial, CLI, installed-package, and regression cases. At minimum prove:

- no source discovery, prompt assembly, or provider access after a failed prerequisite;
- no excluded identity/content influence through results, graph paths, assumptions,
  conflicts, timing detail, trace, errors, usage, or cost;
- no provider call during prepare/inspection/removal;
- no unapproved content-bearing byte or undeclared transport field reaches the capture seam;
- no environment proxy, redirect, alternate host/path/model, fallback, retry, cache, tool,
  grounding, file, or telemetry behavior;
- no secret or private content in logs, errors, traces, crash output, fixtures, or evidence;
- no active HTML, remote image, data URL, control-sequence, or automatic link execution;
- exact-once terminal status under cancel/timeout/response races;
- no durable file/database/provider memory and no source or reachable Git mutation; and
- all supported v0.1–v0.4 commands remain compatible.

Private evidence reports only digests and safe aggregates. Do not publish prompt, context,
response, key, private paths, source content, or raw provider errors.

## 15. Accessibility requirements

- Keyboard-only use for every CLI operation.
- Stable text IDs and explicit confirmation for context removal.
- Status, sensitivity, coverage, and limitations are never color-only.
- `--no-color` and narrow-terminal output retain all trust information.
- JSON has structural parity with text.
- Cancellation is discoverable and visibly acknowledged.
- No dynamic streaming output or streaming accessibility claim.
- Interactive prompts distinguish prepare, approve, dispatch, decline, cancel, and retry.

## 16. Packaging, installation, and recovery

Engineering must produce:

- a wheel byte-bound to the exact reviewed executable tree;
- independent payload comparison to source and packaging metadata;
- clean supported-environment installation and installed-command verification;
- declared dependency inventory and acquisition record;
- offline deterministic mock fixture rerun;
- safe missing-credential/provider-unavailable checks;
- uninstall/reinstall from the same verified wheel;
- recovery from missing/corrupt derived state without canonical-source repair;
- proof that uninstall leaves no transcript store; and
- documentation sufficient for a non-author A12-style reproduction.

No wheel, dependency, or evidence artifact should be committed unless the later
implementation authorization explicitly defines its repository boundary.

## 17. Required documentation

Update or add, as applicable:

- conversation user/contract guide;
- CLI usage and JSON/exit semantics;
- architecture and provider boundary;
- Google configuration, retention disclosure, cost and troubleshooting;
- testing/benchmark protocol;
- installation, uninstall/reinstall, and recovery;
- security/privacy and known limitations;
- versioned contract and compatibility notes; and
- standard Engineering Review.

Do not mark deferred capabilities as partially supported. Do not claim ZDR, streaming,
persistence, local provider support, or a UI.

## 18. Definition of Done

Engineering is complete only when:

1. C01–C30 map to executable tests and retained evidence;
2. full tests, Ruff, mypy, documentation links, and `git diff --check` pass;
3. benchmarks satisfy Section 13 with raw samples and equivalent baseline proof;
4. all provider-neutral and Google capture/degraded tests pass without a live key;
5. any real-provider evidence was separately activated and remains within scope/cost;
6. vault/repository/private-data integrity is proven before/after;
7. package, install, offline fixture, uninstall/reinstall, and recovery evidence passes;
8. no hard exclusion entered the candidate;
9. the branch is clean at one exact candidate commit and not merged or pushed by
   Engineering unless separately authorized; and
10. the required Engineering Review is complete.

## 19. Engineering Review requirements

Write:

`docs/handovers/v0.5/09-principal-engineer-to-cto-conversation-engineering-review.md`

It must contain:

- exact branch, base, candidate commit/tree, diff range, package identity, and worktree
  cleanliness;
- implemented/deferred/tradeoffs/technical debt/security/future recommendations/lessons;
- file and public-contract inventory;
- requirement and C01–C30 mapping to exact tests/evidence;
- provider profile, endpoint documentation version/date, request field allowlists,
  credential boundary, dependency inventory, and network evidence;
- raw benchmark artifact identities and independently recomputed results;
- usage/cost attempts and remaining budget if real evidence was activated;
- full regression/static/docs/package/recovery/privacy/immutability results;
- historical-candidate reuse statement at file/function level;
- deviations or a statement of none; and
- precise requested CTO disposition.

## 20. Mandatory escalation and stop conditions

Stop and return to the CTO/Chief of Staff before proceeding if:

- exact base/branch/worktree identity differs;
- a new dependency, SDK, endpoint, API version, model, feature, sensitivity rule, price,
  term, or provider behavior is needed beyond the explicit authorization;
- official Google documentation no longer confirms the approved model/operation/profile;
- a live credential, call, network access, or spend is needed without separate activation;
- prompt serialization cannot be deterministically bound to approval;
- cancellation cannot be enforced without hidden retry or unbounded blocking;
- any excluded source can influence request-visible behavior;
- any provider content cannot be distinguished from validated evidence;
- a vault/repository/provider-memory/durable transcript write occurs;
- a secret/private path/content/raw error appears in output or evidence;
- historical candidate integration, Voice Shell work, Ollama, streaming, tools, UI,
  persistence, memory, semantic retrieval, or another excluded capability appears useful or
  necessary; or
- satisfying a test would require weakening an accepted ADR or scope decision.

Do not solve an escalation by silently broadening scope.

## 21. Explicit exclusions after Engineering return

This brief does not authorize Engineering to merge, push, tag, release, publish, conduct
CTO review or QA, modify pilots/classifications, integrate the historical candidate or
Voice Shell, perform v0.6 work, or retain/live-share private provider data. Engineering must
stop after the exact candidate and Handoff 09 are ready for independent CTO review.

## 22. Exit statement

**The architecture and implementation contract are complete for Chief-of-Staff validation.
Principal Engineering remains unauthorized until a separate handoff pins the exact commit
containing this brief, creates the clean Engineering branch/worktree, and states all
dependency and provider-evidence authorities.**
