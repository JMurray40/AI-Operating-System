# Handoff 01 — CTO to Principal Engineer: Project Resume Implementation Brief

| Field | Value |
|---|---|
| Sender | Chief Architect / CTO |
| Receiver | Principal Engineer |
| Milestone | v0.4 — Read-only Project Resume CLI Pilot |
| Date | 2026-07-27 |
| Status | **Ready for Chief of Staff validation and engineering branch creation** |
| Repository | `AI-Operating-System` |
| Released architecture baseline | `main@2022c2dffeda8341011b45ceaedd550dd53bf742` |
| Reconciliation state | Clean `main@eef990908330723226bc7e4a92e3da700efa4d51` before this CTO package |
| Engineering branch | `feature/v0.4-project-resume` |
| Exact implementation base | The clean `main` commit containing this brief, ADR-0018 through ADR-0021, and the ADR index update; Chief of Staff must validate, commit, and pin its full SHA before creating the branch |
| Released prerequisite | v0.3.1 |
| Required engineering handoff | `docs/handovers/v0.4/02-principal-engineer-to-cto-engineering-review.md` |

## 1. Objective and architecture disposition

Implement a read-only Project Resume CLI vertical slice over the released v0.3.1 trust
pipeline. A user selects exactly one project and receives a deterministic, sourced
briefing containing:

- objective and authoritative current state;
- current priorities and next action;
- accepted decisions;
- recent sessions;
- open tasks and questions;
- resources;
- explicitly authorized local Git activity; and
- visible conflicts, staleness, omissions, unavailable dependencies, and missing context.

Every material statement must have validated revision-bound evidence. The product must
remain useful from local vault evidence when repository activity is denied or unavailable.

**Architecture disposition: READY FOR CHIEF OF STAFF VALIDATION AND ENGINEERING BRANCH
CREATION.**

This brief becomes implementation-effective only after the Chief of Staff:

1. validates this package;
2. commits it to clean `main`;
3. records that exact full commit SHA in the implementation authorization; and
4. creates `feature/v0.4-project-resume` from that exact commit.

The Principal Engineer must not begin from `eef9909`, `2022c2d`, “latest main,” this
uncommitted worktree, or the parked conversation branch.

## 2. Authoritative inputs

Read in this order:

1. [Project Control](../../coordination/README.md)
2. [v0.4 Planning Index](README.md)
3. [Chief of Staff implementation-finalization handoff](01-chief-of-staff-to-cto-implementation-finalization.md)
4. [Accepted v0.4 Acceptance Tests](../../product/V0.4_PROJECT_RESUME_ACCEPTANCE_TESTS.md)
5. [Product Owner repository-activity decision](00-product-owner-repository-activity-scope-decision.md)
6. [v0.3.1 final release acceptance](../v0.3.1/08-product-owner-final-release-acceptance.md)
7. [ADR-0012](../../adr/ADR-0012-Query-Engine-Is-A-Layered-Deterministic-Pipeline.md)
8. [ADR-0014](../../adr/ADR-0014-Retrieval-Relevance-Is-Separate-From-Answer-Confidence.md)
9. [ADR-0015](../../adr/ADR-0015-Authorization-Precedes-Retrieval-And-Graph-Expansion.md)
10. [ADR-0016](../../adr/ADR-0016-Citations-Bind-Passages-To-Source-Revisions.md)
11. [ADR-0017](../../adr/ADR-0017-Stable-Source-Identity-Is-Separate-From-Location.md)
12. [ADR-0018](../../adr/ADR-0018-Project-Resume-Uses-Exact-Tiered-Project-Identity.md)
13. [ADR-0019](../../adr/ADR-0019-Project-Resume-Uses-Explicit-Authority-Temporal-And-Conflict-Ordering.md)
14. [ADR-0020](../../adr/ADR-0020-Project-Resume-Claims-Require-Validated-Evidence-And-Two-Hard-Budgets.md)
15. [ADR-0021](../../adr/ADR-0021-Repository-Activity-Is-A-Request-Scoped-Local-Read-Only-Git-Capability.md)
16. [Validated planning brief](00-cto-to-principal-engineer-project-resume-planning-brief.md)
17. [Security Threat Model](../../reviews/SECURITY_THREAT_MODEL.md)
18. released v0.3.1 implementation and tests at the pinned implementation base.

The accepted tests and Product Owner decisions control scope. If an implementation detail
in the planning brief conflicts with ADR-0018 through ADR-0021 or this final brief, the
accepted ADR/final-brief rule controls.

## 3. Base, branch, and workspace preconditions

The Chief of Staff authorization must fill this block before engineering starts:

```text
validated_main_commit: <full 40-character SHA>
engineering_branch: feature/v0.4-project-resume
engineering_worktree: <absolute path>
worktree_clean: true
branch_head_equals_validated_main_commit: true
conversation_commits_present: false
```

The Principal Engineer must independently verify:

- the exact pinned commit exists and is the current branch base;
- the worktree is clean;
- the branch contains released v0.3.1;
- ADR-0018 through ADR-0021 and this brief are present;
- no commit from `feature/v0.4-conversation` is in the branch;
- no unrelated user changes are overwritten.

Any mismatch is blocking and must be returned to the Chief of Staff.

## 4. Released v0.3.1 contracts to reuse

The implementation must reuse, not duplicate or weaken:

| Released contract | Required use |
|---|---|
| `AuthorizationScope` and `build_authorized_view()` | Filter before project selection, indexing, graph expansion, claims, trace, and errors |
| `source_identity()` / stable `source_id` | Canonical project/evidence identity and duplicate-ID fail-closed behavior |
| `FileSystemKnowledgeRepository.root` and exact source bytes | Mandatory current-source boundary |
| `Locator`, `locate()`, `validate()` | Full heading/line locator, bounded excerpt, exact fingerprint/current-byte validation |
| `Citation` and coverage semantics | Vault evidence shape and supported/incomplete distinction |
| `QueryContextBuilder` token estimator/invariant | Evidence-budget accounting rules and regression fixtures |
| `CONTRACT_VERSION` / `INDEX_VERSION` | Trace provenance and compatibility assertions |
| `QueryTrace` safe policy/source/omission patterns | Non-disclosing trace fields |
| deterministic tokenizer/ranker/relation resolver | Discovery channels only; never identity or authority |
| CLI text/JSON/exit conventions | New `resume` command behavior |
| read-only repository and unchanged-vault tests | Source integrity proof |

The existing `ProjectContextLoader` predates the v0.3.1 authorization/citation contracts.
Do not use it as the Project Resume trust boundary. Preserve its existing supported
behavior, but build Project Resume over the authorized v0.3.1 contracts.

## 5. Required additive architecture

Add a cohesive application package:

```text
src/jarvis_core/project_resume/
    __init__.py
    contract.py
    request.py
    identity.py
    authority.py
    evidence.py
    budget.py
    repository_activity.py
    local_git.py
    assembler.py
    results.py
    render.py
    trace.py
```

Responsibility boundaries:

- `request` — immutable request, explicit evaluation time, budgets, authorization,
  optional repository grant;
- `identity` — ADR-0018 exact selection only;
- `authority` — ADR-0019 ordering, supersession, staleness, conflicts;
- `evidence` — claim-to-current-citation binding through reusable query citation logic;
- `budget` — ADR-0020 evidence and output planning;
- `repository_activity` — port, grant, fixture values, typed degradation;
- `local_git` — ADR-0021 process adapter only;
- `assembler` — orchestration; no parsing, policy, subprocess, rendering, or scoring logic;
- `results` — frozen versioned semantic result types;
- `render` — deterministic text/JSON;
- `trace` — Project Resume-safe trace composition.

Extract the private current-source/citation creation behavior from `QueryEngine` into a
small reusable query-layer service, for example:

```text
src/jarvis_core/query/evidence.py
    CurrentSourceResolver
    CitationFactory
```

`QueryEngine` must use the extracted service itself. This is a behavior-preserving
refactor with v0.3.1 regression tests. Project Resume must not copy `_current_bytes()`,
`_make_citation()`, path confinement, fingerprint comparison, locator validation, or
coverage rules.

Do not broaden the generic repository interface with Git subprocess behavior. Local Git
activity is a distinct capability port.

## 6. Versioned contracts

Use:

```text
PROJECT_RESUME_CONTRACT_VERSION = "jarvis.project-resume.v0.4.0"
PROJECT_RESUME_TRACE_VERSION = "jarvis.project-resume-trace.v0.4.0"
REPOSITORY_ACTIVITY_CONTRACT_VERSION = "jarvis.repository-activity.local-git.v0.4.0"
```

Required immutable request:

```text
ProjectResumeRequest
  request_id
  workspace_id
  project_selector
  authorization_scope
  source_root
  evidence_token_budget
  output_token_budget
  evaluation_time
  repository_activity_grant | None
  trace_requested
  contract_version
```

Rules:

- scope and source root are mandatory;
- `evaluation_time` is explicit ISO-8601 UTC input, never an implicit wall-clock semantic
  dependency;
- when request ID is omitted by CLI, derive it deterministically from semantic request
  fields and safe scope summary;
- repository activity is absent/denied without a valid grant;
- negative budgets and malformed inputs fail before discovery;
- no request field authorizes writes or network access.

Required result:

```text
ProjectResumeResult
  contract_version
  request_id
  project_identity | None
  status
  sections[]
  citations[]
  repository_citations[]
  conflicts[]
  omissions[]
  limitations[]
  coverage
  trace | None
```

Statuses:

```text
complete | partial | ambiguous | not_found | invalid_identity |
policy_error | budget_error | failed
```

Every type must have deterministic `to_dict()` serialization with fixed field order and
no runtime-only object representations.

## 7. Project identity and safe selection

Implement ADR-0018 exactly:

1. build the authorized view;
2. select only authorized `type=project` notes;
3. apply exact tier precedence: canonical ID, title, alias, filename stem;
4. stop at the first tier with matches;
5. select only if exactly one match exists;
6. return safe sorted candidates for same-tier ambiguity;
7. return not-found without a substitute;
8. fail closed for duplicate explicit IDs/malformed identity.

Do not construct a request-visible index or graph from unauthorized notes. Do not use
relative relevance, fuzzy matching, recency, path order, or graph position to break ties.

## 8. Evidence discovery channels

After exact project selection, discover evidence through typed channels:

- canonical project/dashboard passages;
- notes with typed `projects` metadata resolving to the selected stable identity;
- authorized outgoing and incoming relationships;
- query retrieval materially bound to the selected project;
- local repository activity, only with an explicit valid grant.

Each selected source records its channel and reason. Graph-selected and relevance-ranked
sources remain distinct. Deduplicate by stable source identity plus current fingerprint.
Duplicate explicit IDs fail closed.

All channels operate on the authorized view. Cycles terminate by visited stable
identity/revision. Configure and test maximum graph depth, fan-out, sources per channel,
and total candidates; report bounded safe omissions.

## 9. Claim, citation, coverage, and rendering rules

Implement ADR-0020.

Required sections in fixed order:

1. Project;
2. Current state;
3. Next action and priorities;
4. Accepted decisions;
5. Recent sessions;
6. Open tasks and questions;
7. Resources;
8. Repository activity;
9. Conflicts, staleness, and missing context;
10. Evidence coverage and omissions.

Every material fact must have at least one citation validated against current bytes
immediately before result emission. Metadata-derived claims must cite a locator/excerpt
containing the material metadata signal, not an unrelated body passage.

Local Git material claims require exact object/snapshot evidence under ADR-0021. A fixture
record and real Git record use the same semantic activity contract.

Rendering:

- text and JSON consume the same semantic result;
- supported passages and incomplete references are structurally and visibly distinct;
- never render `0-0` as a passage citation;
- label inference, conflict, staleness, unavailable dependency, and unknown;
- empty sections say “no supported evidence available,” never “none exist”;
- incomplete-only output returns warning/partial status;
- ambiguous, not-found, policy, and budget outcomes have stable distinct exit codes;
- no result text is produced through a real provider.

## 10. Authority, temporal, supersession, and conflicts

Implement ADR-0019 without using retrieval relevance as authority.

Required tests include:

- accepted decision versus newer draft;
- current authoritative project state versus older session;
- later accepted decision with explicit `supersedes`;
- later accepted decision without supersession evidence;
- two supported material conflicts;
- undated evidence;
- stale evidence at the exact threshold;
- excluded evidence that would otherwise resolve a conflict.

Conflict output contains only authorized current citations. Never silently choose,
summarize away, or merge unresolved material conflicts.

## 11. Hard evidence and output budgets

Reuse the released deterministic estimator and enforce both ADR-0020 budgets.

Default configuration for the CLI pilot:

```text
evidence_token_budget = 8_000
output_token_budget = 4_000
trace_token_sub_budget = 1_000 (inside, not in addition to, output budget)
```

The defaults may be reduced based on benchmark evidence but may not be raised without
tests. CLI overrides must be positive bounded integers:

```text
evidence: 256..32_000
output: 256..16_000
```

Account for headings, field labels, whitespace, separators, claim text, citations,
limitations, conflicts, omissions, coverage, JSON keys/punctuation, and requested trace.
Measure the final serialization before emission. Never truncate valid JSON or separate a
claim from required evidence.

Required cases: zero/negative, below-minimum structure, exact boundary, one token over,
oversized first source, multibyte text, large metadata, many citations, cycles, fan-out,
trace enabled, text/JSON differences, and error fallback.

## 12. Local Git boundary

Implement ADR-0021 exactly. Additional implementation constraints:

- define `ProcessRunner` as an injected protocol;
- locate Git once through an approved executable-resolution function and record its
  version in diagnostics;
- use `subprocess` argument arrays and `shell=False`;
- run only the three accepted command shapes;
- hard-cap records at 50, timeout at 10 seconds, stdout at 1 MiB, stderr at 8 KiB;
- do not call `status`, `diff`, remote, fetch, submodule, worktree, maintenance, config
  write, credential, or hook commands;
- do not pass a project selector, commit text, URI, or source metadata as an argument;
- canonicalize and compare the `rev-parse --show-toplevel` result to the exact granted
  root;
- strip/allowlist environment as ADR-0021 specifies;
- return typed denied/unavailable/malformed/stale results;
- redact absolute paths, usernames, environment, raw stderr, remotes, and credentials;
- treat activity subjects/authors as untrusted data, never instructions;
- never retry automatically.

CLI activation requires both:

```text
--include-repository-activity
--repository-root <path>
```

The request grant binds that root to the selected project for one invocation. A root
present without the flag does nothing; the flag without a root is invalid. No repository
path is inferred from a URI or vault content.

The deterministic fixture adapter is mandatory and must run without Git installed.

## 13. CLI contract

Add:

```text
jarvis resume <project-selector>
  [--path <vault-root>]
  [--format text|json]
  [--trace]
  [--as-of <ISO-8601-UTC>]
  [--evidence-budget <tokens>]
  [--output-budget <tokens>]
  [--include-repository-activity --repository-root <local-git-root>]
```

v0.4 output is stdout only. Do not add a product output-file write path. Pilot evidence and
manual scorecards are test/release workflows outside the runtime command.

Exit codes must extend existing documented conventions without reassigning current codes.
At minimum distinguish:

- complete supported briefing;
- partial/warning briefing;
- ambiguous selector;
- not found;
- invalid input/policy/budget;
- internal failure.

Update CLI usage, help snapshots, text/JSON examples, and exit-code documentation.

## 14. Trace and determinism

Trace must include:

- request ID;
- vault aggregate fingerprint;
- Project Resume, query, citation, trace, policy, index, and repository-activity contract
  versions;
- safe policy summary;
- selected authorized project identity and identity tier;
- selected authorized evidence identities/locators and channel reasons;
- conflicts, limitations, and safe omission aggregates;
- local Git HEAD/snapshot fingerprint when granted;
- stage timings in diagnostics.

Trace must not include excluded source identity/content, rejected ambiguity candidates
outside scope, raw Git stderr, absolute repository paths, environment values, credentials,
remote URLs, or connector secrets.

Semantic byte-determinism excludes measured timings and explicitly labeled runtime
diagnostics. Tests compare the semantic result after removing only fields designated by
the contract; do not broadly normalize output to hide nondeterminism.

## 15. Read-only and security invariants

Before/after evidence must prove no change to:

- vault files, metadata, paths, timestamps attributable to Jarvis, or inventory;
- Git worktree files;
- Git `HEAD`, refs, packed refs, config, index, or object contents;
- external fixture resources;
- durable conversation or application state.

Output remains ephemeral stdout. Derived test/benchmark artifacts go only to explicit
non-vault paths.

Adversarial tests:

- traversal, absolute/mixed paths, symlink/junction escape, case/segment boundaries;
- selector Unicode, control characters, option-looking text, huge input;
- duplicate project IDs and title/alias collisions;
- unauthorized/restricted project and linked evidence;
- excluded-term influence across selection/ranking/graph/conflict/trace/errors;
- post-discovery byte mutation, missing/unreadable source, BOM/newline/encoding changes;
- prompt injection in vault/Git text treated as inert data;
- malicious Git config/environment, fake executable, timeout, output flood, malformed NUL
  records, invalid object IDs/timestamps, raw error secrets;
- Git root outside grant, parent discovery, worktree `.git` file, bare repo, submodule,
  linked worktree, missing Git;
- output-budget and error-path disclosure.

Unknown policy or dependency state fails closed for that capability while preserving safe
local-vault completion where possible.

## 16. Affected-file forecast

Expected additions/changes:

```text
src/jarvis_core/project_resume/**
src/jarvis_core/query/evidence.py
src/jarvis_core/query/engine.py
src/jarvis_core/cli.py
src/jarvis_core/config.py                    (only typed bounded defaults if needed)
tests/unit/test_project_resume_*.py
tests/integration/test_project_resume_*.py
tests/security/test_project_resume_*.py      (or existing security layout)
tests/fixtures/project-resume/**
tests/support/project_resume_*.py
scripts/benchmark_project_resume.py
scripts/evaluate_project_resume.py           (release/evaluation only; no telemetry)
docs/software/PROJECT_RESUME.md
docs/software/CLI_USAGE.md
docs/software/ARCHITECTURE.md
docs/software/TESTING.md
CHANGELOG.md
evaluations/v0.4-project-resume-dogfood-template.tsv
```

The Principal Engineer owns exact decomposition within these boundaries. Changes outside
this forecast require explanation; changes to schemas, providers, conversation, plugins,
MCP, or automation require stop-and-escalate.

## 17. Requirement-to-test and evidence matrix

| Acceptance | Mandatory evidence |
|---|---|
| A1 exact project | Canonical ID/title/alias/stem tiers; all ten sections; every material vault/Git claim revision-bound |
| A2 ambiguous/missing | Same-tier collisions, cross-tier precedence, duplicate IDs, safe candidate fields, no fuzzy/substitute selection |
| A3 authorization | Filter before selection/index/graph; sensitivity/workspace/path/source scopes; repository grant denied by default; non-disclosure in claims/conflicts/errors/trace |
| A4 ordering | Accepted over draft, current state over old session, explicit supersession only, visible unresolved conflict/staleness |
| A5 citations | Full hierarchy/locator/excerpt/current fingerprint; metadata signal; changed/deleted/unreadable/escaped source; exact Git object/snapshot |
| A6 budgets | Evidence and full-output exact-boundary/one-over/oversized-first/multibyte/cycle/fan-out/wrapper/citation/trace tests |
| A7 read-only | Vault and Git before/after inventories/hashes/status; stdout only; fixture state unchanged; no durable conversation state |
| A8 determinism/trace | Byte-identical semantic result for identical inputs; explicit evaluation time; all required versions/fingerprints; timing isolated; trace redaction |
| A9 degradation | Git denied/missing/timeout/overflow/malformed/stale; local result partial and useful; no retries; unavailable not “no activity” |
| A10 performance | Pilot and synthetic retrieval p50/p95/p99 plus total p50/p95/p99, memory, source/omission counts, raw samples |
| A11 value | Eight-week consented/manual event records, weekly claim review, ≥80% useful rated briefings, strategic target reporting |
| A12 packaging | Clean supported environment, non-author runs both pilots, diagnostics, rebuild/recovery, missing/corrupt derived index, unchanged canonical sources |

Minimum automated suites:

- unit: identity, authority, supersession, claims, staleness, budgets, Git parsing/redaction;
- fixture: exact, ambiguous, missing, conflict, restricted, oversized, cyclic, Git states;
- integration: CLI text/JSON/exit, current-byte validation, local Git process, degradation,
  trace, unchanged sources;
- compatibility: all v0.3.1 tests and existing CLI behavior;
- security: scope/path/process/environment/injection/non-disclosure;
- performance: synthetic plus two pilot vaults;
- packaging: clean-environment installation and recovery.

## 18. Performance reference and protocol

Canonical release reference profile:

```text
OS: Windows 11 23H2 x86-64
CPU allocation: 4 logical x86-64 CPUs
Memory allocation: 8 GiB
Storage: SSD-backed local filesystem
Python: CPython 3.10.12
Git: installed local Git; exact version recorded with evidence
Power: AC / non-battery-saver
Load: no intentionally concurrent benchmark workload
```

If the physical host exposes more resources, constrain the benchmark process/VM to this
profile or document why equivalent constraint is unavailable. Record CPU model, physical
RAM, storage model/type, OS build, Python, Git, power plan, and relevant process
affinity/allocation in evidence. Do not attribute variance causally without
instrumentation.

Protocol:

1. fixture/synthetic benchmarks run with repository activity disabled and fixture-enabled;
2. pilot benchmarks run with repository activity denied, unavailable, and authorized
   local Git;
3. warm up three times;
4. run at least 30 measured attempts per mode;
5. retain raw stage and total samples;
6. use the released nearest-index percentile estimator and predeclare it;
7. report discovery, authorization, identity, retrieval, graph, authority/conflict,
   citation validation, Git, rendering, total, and peak memory;
8. record source, claim, citation, conflict, and omission counts;
9. report cold and warm pilot runs separately;
10. fail if either pilot's valid total run is 30 seconds or more;
11. report p50/p95/p99 separately for retrieval and total;
12. never tune by weakening trust contracts.

Synthetic scale points: 100, 500, 1,000, and 5,000 notes, including high fan-out and cyclic
fixtures. The 30-second gate applies to each real pilot vault; synthetic data characterizes
scaling and must terminate within documented budgets.

Raw committed evidence destination:

```text
docs/evidence/v0.4/project-resume-performance-<candidate-short-sha>.json
```

The artifact must include candidate SHA, command, environment, protocol, raw samples,
derived statistics, gate rule, and SHA-256 digest. Do not commit pilot passages, absolute
paths, usernames, remote URLs, or secrets.

## 19. Pilot evidence and privacy controls

Pilot projects:

- AI Operating System;
- Cloud Organizer Pro.

Private raw pilot evidence goes only to the user-approved ignored destination:

```text
data/v0.4-evidence/<candidate-short-sha>/
```

`data/` is already ignored. The evaluation command must require an explicit destination,
refuse a path inside either canonical vault, and display what metadata will be recorded.
No automatic upload, telemetry, network call, or background collection is permitted.

Commit only a redacted manifest/summary:

```text
docs/evidence/v0.4/pilot-evaluation-<candidate-short-sha>.json
```

Allowed committed fields: candidate SHA, contract versions, hashed snapshot identity,
project display name already accepted in product scope, counts, timings, coverage totals,
defect categories, gate results, private-artifact SHA-256, and reviewer disposition.
Forbidden: source passages, full note titles/paths beyond accepted project names, task
text, questions, Git subjects/authors/remotes, usernames, absolute paths, or credentials.

## 20. Dogfood evidence and consent

Provide a manual template:

```text
evaluations/v0.4-project-resume-dogfood-template.tsv
```

Actual event records default to:

```text
data/v0.4-dogfood/events.jsonl
```

Collection is off by default. A user must explicitly initialize the destination outside
the vault after seeing a consent notice listing every field. No CLI resume invocation may
silently append an event. Manual use of the template is acceptable and preferred for the
first pilot.

Required event fields are those in A11: success/abandonment, time to useful orientation,
estimated time saved, incorrect/missing context, citation defects, correction/metadata
time, and requested features. Use stable pseudonymous event IDs and project IDs; do not
record briefing text or citations.

Only redacted weekly aggregates may be committed:

```text
docs/evidence/v0.4/dogfood-summary-<week>.json
```

A11 is an eight-week strategic validation gate. Technical candidate completion may occur
before eight weeks, but:

- v0.4 must not be declared strategically validated;
- the ≥80% useful-rated gate must not be claimed early;
- the 15–30 minute and 90–95% sourcing targets remain explicitly unproven; and
- v0.5 is not unlocked by technical candidate completion.

## 21. Packaging, diagnostics, and recovery

Required clean-environment evidence:

1. install the package on a clean supported Windows environment using documented commands;
2. run `jarvis --help` and both pilot `resume` commands;
3. run without Git and obtain a safe partial local-vault briefing;
4. run with authorized local Git;
5. diagnose missing Git, invalid vault, denied repository root, and corrupt/missing derived
   index;
6. rebuild only derived state;
7. prove canonical vault and Git source state unchanged;
8. uninstall/reinstall and repeat a fixture briefing;
9. have a non-author follow only the documentation.

Evidence destination:

```text
docs/evidence/v0.4/packaging-recovery-<candidate-short-sha>.md
```

Any recovery procedure that modifies canonical sources is release-blocking.

## 22. Documentation deliverables

Update or create:

- `docs/software/PROJECT_RESUME.md`;
- CLI usage and exit codes;
- architecture/data-flow diagram;
- testing and benchmark instructions;
- result/trace/repository-activity contract examples;
- identity, authority, conflict, staleness, coverage, and budget rules;
- Git capability and redaction model;
- installation, diagnostics, rebuild, and recovery;
- pilot evaluation/privacy procedure;
- dogfood consent/template instructions;
- changelog and roadmap naming: Project Resume is v0.4, conversation remains v0.5.

Do not rewrite accepted ADRs after implementation. If engineering discovers a conflicting
decision, stop and request a superseding ADR.

## 23. Explicit exclusions and forbidden work

Do not implement:

- visible-context or multi-turn chat;
- any code/commit from `feature/v0.4-conversation`;
- real provider generation, provider streaming, or provider egress;
- durable conversation state or proposed memory;
- vault writes, schema migration, metadata repair, or generated-brief persistence;
- embeddings, vectors, hybrid retrieval, or persisted semantic indexes;
- plugins, MCP, generic connector/capability frameworks;
- agents, tools/actions, automation, watchers, jobs, or background services;
- dashboard UI/widgets, mobile, voice, team, enterprise, or marketplace work;
- live GitHub, remote APIs, fetch/pull, credentials, network access;
- arbitrary Git commands or user-supplied Git arguments;
- unrelated refactoring.

The old provider/context/conversation code is not authorization to use those capabilities.

## 24. Known risks and technical debt

| Risk/debt | Required treatment |
|---|---|
| Private `QueryEngine` citation logic | Extract once into shared service; preserve all v0.3.1 behavior |
| Legacy `ProjectContextLoader` can appear reusable but lacks trust contracts | Do not use as Project Resume boundary; preserve compatibility |
| Local Git subprocess/config/environment complexity | ADR-0021 strict allowlist, injected runner, real-process adversarial tests |
| Git commit text contains untrusted/possibly private data | Treat as data; bounded output; redact committed evidence |
| Exact authority subjects/supersession may be sparse in real vaults | Show conflict/unknown; do not infer silently |
| Two serialization budgets are easy to miscount | Plan then serialize/measure; exact-boundary tests for text and JSON |
| Timing and determinism conflict | Timings are diagnostics-only; semantic result remains deterministic |
| Pilot evidence privacy | Private ignored destination; redacted committed manifest; explicit consent |
| Eight-week A11 timing | Separate technical candidate from strategic validation |
| Path-derived fallback identity changes on rename | Label weaker identity; do not write IDs |
| Windows symlink/junction test limitations | Run supported tests with privilege detection; do not treat skips as proof |

## 25. Mandatory escalation points

Stop and return to the CTO/Chief of Staff if:

- the pinned implementation base is absent, dirty, or differs from authorization;
- an accepted ADR conflicts with released code;
- exact project identity requires fuzzy/semantic selection;
- current-source citation validation cannot be reused without behavior change;
- a material claim cannot be bound to current evidence;
- output budgeting would require truncating after serialization;
- local Git needs a command outside ADR-0021;
- Git isolation requires inheriting credentials/config/network settings;
- a pilot requires live GitHub or provider generation;
- a schema/vault write appears necessary;
- a test requires importing the parked conversation code;
- reference hardware or pilot access is unavailable for release evidence;
- the requested scope expands beyond this brief.

Record the issue; do not silently choose a product or architecture policy.

## 26. Definition of Done

Technical candidate completion requires:

1. A1–A10 and A12 automated/manual technical evidence complete.
2. A11 collection mechanism/template and consent boundary complete, with strategic results
   explicitly pending until eight weeks.
3. Every material claim currently supported, visibly incomplete, or conflicting.
4. No unauthorized source influences selection, retrieval, graph, claims, conflicts,
   errors, omissions, or trace.
5. Both hard budgets proven across all serializers.
6. Local Git capability proven confined, bounded, deterministic, redacted, degradable,
   and non-mutating.
7. Existing v0.3.1 behavior and tests remain green.
8. Full pytest, Ruff, mypy, `git diff --check`, unchanged-vault/Git, packaging, recovery,
   and benchmark evidence pass.
9. Both pilots complete below 30 seconds on the reference profile.
10. Documentation and evidence artifacts are complete and privacy-reviewed.
11. No excluded scope or parked conversation commit is present.
12. Principal Engineer produces the required handoff.
13. CTO independently reviews exact-HEAD architecture conformance before QA.
14. Quality & Release independently executes the accepted matrix.
15. Product Owner issues the release decision.

Strategic completion additionally requires eight weeks of A11 evidence and at least 80% of
rated briefings useful. Technical completion does not imply strategic completion or
authorize v0.5.

## 27. Required Principal Engineer handoff

Produce:

```text
docs/handovers/v0.4/02-principal-engineer-to-cto-engineering-review.md
```

It must contain:

- exact branch, pinned base, HEAD, and diff range;
- commit list and changed-file inventory;
- ADR/requirement-to-test mapping;
- all contract versions and compatibility effects;
- architecture, authorization, citation, budget, Git-process, privacy, and read-only
  analysis;
- full tests/static checks with exact commands/results;
- unchanged vault and Git inventories;
- raw benchmark artifact and digest;
- pilot redacted manifest and private evidence digest;
- packaging/non-author/recovery evidence;
- dogfood mechanism status and explicit eight-week pending status;
- deviations, defects, debt, skips, waivers, and unresolved risks;
- confirmation of no network/provider/conversation/excluded scope;
- exact recommended CTO review range.

Do not merge, push, start QA, or claim release readiness. Stop after the engineering
handoff.

## 28. Artifacts produced by this CTO gate

```text
docs/adr/ADR-0018-Project-Resume-Uses-Exact-Tiered-Project-Identity.md
docs/adr/ADR-0019-Project-Resume-Uses-Explicit-Authority-Temporal-And-Conflict-Ordering.md
docs/adr/ADR-0020-Project-Resume-Claims-Require-Validated-Evidence-And-Two-Hard-Budgets.md
docs/adr/ADR-0021-Repository-Activity-Is-A-Request-Scoped-Local-Read-Only-Git-Capability.md
docs/adr/README.md
docs/handovers/v0.4/01-cto-to-principal-engineer-implementation-brief.md
```

The produced commit is intentionally pending Chief of Staff validation and commit. That
commit becomes the only valid implementation base when pinned in the authorization.

## 29. Unresolved decisions

No product or architecture decision remains open for implementation start.

Operational facts still to be recorded by the Chief of Staff are:

- exact full implementation-base commit after this package is committed;
- engineering worktree path;
- Principal Engineer prompt/authorization artifact.

These are authorization controls, not delegated engineering decisions.

## 30. Required next actions

### Chief of Staff

1. Validate this brief and all four ADRs against the released code and accepted tests.
2. Confirm only the six listed CTO artifacts changed.
3. Commit the accepted package to clean `main`.
4. Record the exact full commit SHA.
5. Create `feature/v0.4-project-resume` and its clean worktree from that exact SHA.
6. Produce:

```text
docs/handovers/v0.4/02-chief-of-staff-to-principal-engineer-implementation-authorization.md
```

7. Give the Principal Engineer the exact branch, worktree, base, inputs, exclusions, and
   required output.

### Principal Engineer

Do not begin until the validated authorization exists. Then verify every precondition and
implement only this brief.

## Exit statement

**READY FOR CHIEF OF STAFF VALIDATION AND ENGINEERING BRANCH CREATION.**

The Project Resume architecture is reconciled with released v0.3.1, ADR-0018 through
ADR-0021 are accepted, repository activity is limited to fixtures plus local read-only
Git, and the implementation/test/evidence boundaries are complete. Engineering remains
blocked until the Chief of Staff commits this package, pins the exact commit, and creates
the authorized branch/worktree. Live GitHub and the parked conversation candidate remain
excluded.
