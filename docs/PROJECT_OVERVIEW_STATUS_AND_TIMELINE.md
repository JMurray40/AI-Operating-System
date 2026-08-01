# AI Operating System — Project Overview, Current Status, and Timeline

| Field | Value |
|---|---|
| Audience | Product Owner, collaborators, and new project agents |
| Status date | 2026-08-01 |
| Product Owner | Jason Murray |
| Current released version | v0.4.0 — Project Resume |
| Current active phase | v0.5 Visible-Context Conversation planning |
| Implementation authority | Not yet granted for v0.5 |
| Authoritative control page | [Project Control](coordination/README.md) |

## Executive summary

AI Operating System is a local-first, human-controlled platform for connecting personal
knowledge, software projects, and AI providers without allowing any one model or vendor to
own the user's information.

The practical goal is:

> Select a project, understand where work stopped, inspect exactly what context an AI will
> receive, complete useful work, and preserve approved outcomes without silently changing
> the user's knowledge base.

The project has moved beyond a concept or prototype. It now has a governed engineering
process, a deterministic query foundation, hardened trust contracts, and a released
Project Resume workflow. Version v0.4.0 has been merged, tagged, independently reviewed,
and published.

The current work is planning v0.5: a narrow visible-context conversation capability. Its
architecture package has been drafted but is not yet approved or committed. Three bounded
documentation corrections are required before Jason receives the final scope decision.
No v0.5 implementation is currently authorized.

## What the project is

The system separates responsibilities deliberately:

- **Obsidian/Markdown holds durable human-owned knowledge.**
- **GitHub holds reviewed software, architecture, evidence, and release history.**
- **Jarvis is the local orchestration layer.**
- **AI providers are replaceable reasoning services, not permanent memory.**
- **Derived indexes and caches are rebuildable.**
- **Sensitive content and consequential actions require explicit authorization.**

The long-term product is intended to support:

- trustworthy search and evidence-backed answers;
- rapid project resumption;
- inspectable AI conversation;
- proposal-based durable memory;
- semantic discovery and relationship analysis;
- controlled plugins and MCP integrations;
- bounded agents and automation; and
- later desktop, mobile, and voice interfaces.

These capabilities are being released incrementally. Each release must pass architecture,
engineering, evidence, security, Quality, Product Owner, and documentation gates before the
next implementation begins.

## What has been completed

### 1. Project governance and operating model

The project now has:

- an Operating Handbook defining Product Owner, Chief of Staff, CTO, Principal Engineer,
  Quality, and Librarian responsibilities;
- a single coordination entry point and role-based handoff system;
- Architecture Decision Records for consequential technical choices;
- explicit acceptance matrices and stop conditions;
- independent architecture and Quality review gates;
- exact commit, tree, wheel, evidence, and release identities; and
- a documentation closeout process that preserves historical decisions while exposing the
  latest effective state.

This process has sometimes been slower than ordinary feature development, but it has also
identified real privacy, authorization, citation, packaging, Git, evidence, and release
hazards before they reached users.

### 2. Query Engine foundation — v0.3

Delivered capabilities include:

- deterministic lexical retrieval;
- explainable relative ranking;
- source citations;
- token-budgeted context;
- trace mode; and
- search, summarize, and explain workflows.

This established the read-only information-retrieval foundation. Conversation and remote
provider work were deliberately deferred until the trust boundary was stronger.

### 3. Query Trust Contracts — v0.3.1

Released as tag `v0.3.1`.

The hardening release added:

- explicit authorization before retrieval and graph expansion;
- fail-closed handling of missing or unclassified scope;
- separation of retrieval relevance from answer confidence;
- citations bound to supporting passages and source revisions;
- stable source identity separate from file location;
- current-source validation before citation emission;
- strict compatibility boundaries; and
- independently retained performance and packaging evidence.

This release created the trust foundation required by Project Resume and future generated
answers.

### 4. Project Resume — v0.4.0

Released and published as annotated tag `v0.4.0`.

Project Resume provides a deterministic, sourced briefing that helps a user return to a
project and understand:

- current status;
- accepted and conflicting decisions;
- recent sessions and activity;
- important resources;
- missing or ambiguous context;
- evidence coverage and limitations; and
- optionally authorized local, read-only Git activity.

Important release controls included:

- exact project identity rather than fuzzy guessing;
- explicit authority, time, supersession, and conflict ordering;
- claim-specific evidence and current-byte citations;
- hard context and output budgets;
- request-scoped Git access with no repository mutation;
- real pilot measurements on the current PC;
- independent clean-environment installation and recovery testing;
- a verified wheel bound byte-for-byte to the accepted executable;
- adversarial Quality review; and
- final repository documentation reconciliation.

The accepted technical identities are:

| Item | Identity |
|---|---|
| v0.4 release tag | `v0.4.0` |
| Integrated release commit | `6cf9b72355d65768d3ea549a5af34006e2b6d3b6` |
| Frozen executable | `ff402d7f82c061426a5e960f7177d916c355bbf2` |
| Accepted wheel SHA-256 | `8dcc1378a1ac4c3b96dbfea94c0443e92ffaec54fafeb1db5aa73e449a768cd3` |
| Final Quality disposition | `Ready` |

### 5. Pilot and release evidence

The project established repeatable methods for:

- manually controlled sensitivity onboarding;
- private evidence retention with public redacted summaries;
- canonical and reachable Git-integrity checks;
- raw benchmark retention and independent recomputation;
- candidate-specific wheel staging and stale-artifact quarantine;
- offline installation, uninstall, reinstall, and recovery; and
- separating technical release evidence from longer-term product-learning results.

The eight-week v0.4 dogfood outcome, called A11, remains pending and unproven. Its
collection mechanism and sourcing metric are complete. This is a strategic learning item,
not an unresolved v0.4 technical defect.

## Where the project is now

### Released state

- v0.3 Query Engine: merged.
- v0.3.1 Query Trust Contracts: released.
- v0.4 Project Resume: released, tagged, and pushed.
- v0.4 repository closeout: validated and published.

### Active work: v0.5 Visible-Context Conversation planning

The proposed v0.5 slice is intentionally smaller than the original chat vision:

- interactive and scripted CLI;
- a versioned in-process application API;
- process-local, session-only conversation state;
- explicit workspace and optional exact project scope;
- a visible context manifest before remote disclosure;
- user removal of context items;
- immutable context snapshots and per-turn approval;
- deterministic mock provider plus one real provider;
- complete-response, non-streaming generation;
- claim-level citations and visible evidence coverage;
- usage, cost, cancellation, failure, and privacy reporting; and
- no vault writes, persistent transcripts, memory, tools, attachments, UI, public server,
  semantic retrieval, provider fallback, or streaming.

The CTO has drafted requirements, architecture, acceptance tests, a historical-candidate
assessment, and three proposed ADRs. Chief-of-Staff review found the overall slice coherent
but returned three documentation issues for correction:

1. bind approval to every deterministic prompt input and version, not only the context
   snapshot;
2. distinguish approved content bytes from necessary allowlisted transport metadata and
   opaque credentials in the real-provider test; and
3. correct wording about attachments and the ordering of source authorization,
   destination eligibility, user approval, prompt assembly, and dispatch.

These are planning-contract corrections. They are not implementation defects because v0.5
implementation has not begun.

### Historical conversation candidate

The old `feature/v0.4-conversation` branch remains parked and read-only. It is treated as a
design spike, not a release candidate. Useful concepts may be reimplemented, but its old
confidence, citation, scope, trace, and simulated-streaming contracts cannot be reused as
accepted evidence.

### Decisions Jason must make next

After the CTO corrects the planning package, the Product Owner must decide:

1. whether v0.5 remains Visible-Context Conversation;
2. whether Proposed Memory becomes v0.6 or moves later;
3. how that choice displaces the existing v0.6 Semantic Search assignment;
4. whether conversation remains session-only for v0.5;
5. whether the release surface is CLI plus in-process API;
6. whether provider-response streaming is deferred;
7. which single real provider, endpoint, model role, retention terms, credential method,
   request budget, and evidence spend are approved;
8. whether every remote turn requires explicit visible-context approval; and
9. whether the documented exclusions remain hard boundaries.

## What happens next

The immediate sequence is:

1. **CTO planning correction** — correct the three bounded contract issues and return the
   complete package unstaged.
2. **Chief-of-Staff validation** — verify internal consistency, links, scope, and exact
   planning base; commit the proposed package if valid.
3. **Product Owner decision** — approve or amend the v0.5 scope, roadmap sequence, proposed
   ADRs, and real-provider choice.
4. **Roadmap reconciliation** — update release numbering only after Jason's decision.
5. **CTO implementation brief** — convert approved product decisions into a bounded
   engineering contract and evidence plan.
6. **Chief-of-Staff engineering activation** — pin an exact clean base and authorize a new
   v0.5 branch/worktree.
7. **Principal Engineering** — implement in ordered milestones with tests and handoffs.
8. **CTO conformance review** — verify the exact candidate against accepted ADRs and
   architecture.
9. **Independent Quality review** — run the adversarial C01–C30 matrix, packaging,
   performance, privacy, and real-provider checks.
10. **Product Owner release decision** — authorize integration, tag, and publication.
11. **Librarian closeout** — reconcile documentation and route the next milestone.

## Timeline

### How to read this timeline

The project uses evidence gates rather than date-driven releases. The ranges below are
planning estimates, not promises. They assume one experienced engineer working with AI
assistance, timely Product Owner decisions, access to the selected provider, and no major
architecture return.

Agent credit limits, manual handoffs, provider approval, security findings, and independent
evidence runs can increase elapsed calendar time even when engineering effort is unchanged.

### Near-term v0.5 estimate

| Phase | Provisional effort | Exit condition |
|---|---:|---|
| Correct and approve planning package | 1–3 focused days | Jason approves scope, roadmap treatment, provider, and proposed ADRs |
| Final architecture and implementation brief | 2–4 focused days | Exact engineering contracts, milestones, exclusions, and evidence matrix accepted |
| Core session/API/context implementation | 2–3 engineer-weeks | Session, prepare, snapshots, approval, budgets, and visible context pass tests |
| Provider gateway and real-adapter boundary | 1–2 engineer-weeks | Mock and one real adapter pass egress, secret, endpoint, failure, cost, and cancellation tests |
| Answer validation, citations, rendering, and trace | 1–2 engineer-weeks | Claim/evidence, coverage, privacy, safe rendering, and trace contracts pass |
| CLI, packaging, performance, and documentation | 1–2 engineer-weeks | Installed workflow, benchmarks, recovery, accessibility, and docs complete |
| CTO and independent Quality review | 1–3 engineer-weeks | Architecture conformance and all C01–C30 gates pass |
| Release integration and closeout | 2–5 focused days | Product Owner approval, merge, tag, push, and Librarian closeout |

**Provisional v0.5 total:** approximately **6–10 focused engineer-weeks**, plus Product
Owner decision time and any external provider/evidence scheduling. This range should be
replaced by the Principal Engineer's implementation estimate after scope and provider
approval.

### Parallel v0.4 learning timeline

The A11 Project Resume dogfood evaluation runs independently over an eight-week real-usage
window. Its result may inform product refinements, but it does not reopen the released v0.4
technical identity unless a material defect is discovered.

### Roadmap after v0.5

The exact post-v0.5 sequence is awaiting Jason's decision. The current options are:

#### Recommended sequence

| Release | Capability | Current estimate/status |
|---|---|---|
| v0.5 | Visible-Context Conversation | Planning; provisional 6–10 engineer-weeks |
| v0.6 | Proposed Memory | Scope and estimate not yet approved |
| v0.7 or later | Semantic Search and Relationship Intelligence | Existing estimate: 7–10 engineer-weeks |
| Following release | Plugin and MCP Foundations | Existing estimate: 10–14 engineer-weeks plus security testing |
| Following release | Bounded Agent Framework | Existing estimate: 10–14 engineer-weeks |
| Following release | Automation Preview | Existing estimate: 10–13 engineer-weeks |
| v1.0 stabilization | Trusted Personal AI Operating System | Existing estimate: 12–18 stabilization weeks |

#### Alternative sequence

Keep Semantic Search immediately after conversation and place Proposed Memory after it.
This preserves the existing semantic-search priority but delays the workflow for turning
useful conversation outcomes into reviewed durable knowledge.

No post-v0.5 numbering should be treated as accepted until the roadmap collision is
explicitly resolved.

## Key risks and controls

| Risk | Current control |
|---|---|
| Sensitive context reaches a provider without informed approval | Authorization before retrieval, visible context, immutable snapshots, digest-bound per-turn approval |
| Retrieval score is mistaken for answer confidence | Separate relative relevance and qualitative evidence coverage; no numeric answer confidence |
| Generated claims cite stale or unrelated content | Passage/revision citations and current-byte validation |
| Provider adds hidden telemetry, tools, fallback, or redirects | One allowlisted adapter, bounded transport contract, exact egress evidence, fail-closed tests |
| Conversation becomes an uncontrolled memory store | Session-only state; no transcript database or vault writes in v0.5 |
| Historical code bypasses released trust contracts | Historical branch remains parked; implementation starts from current released `main` |
| Scope expands into UI, streaming, memory, tools, or semantic search | Explicit non-goals and Product Owner approval before any scope change |
| Evidence is irreproducible | Raw observations, exact identities, private/public digest binding, independent recomputation |
| Release artifacts are confused by filename | Candidate-specific staging and path/size/digest identity |
| Process overhead delays delivery | Consolidated findings, bounded corrections, exact handoffs, and no unnecessary reruns |

## Definition of success for the next release

v0.5 will be successful when a user can:

1. start a bounded local conversation session;
2. submit a question within an explicit authorized workspace;
3. inspect the exact evidence selected for the provider;
4. remove context and see a new immutable approval identity;
5. approve one remote turn knowingly;
6. receive a useful answer from one real provider;
7. distinguish supported source claims, inference, model knowledge, unknowns, and
   limitations;
8. open valid citations to current supporting passages;
9. understand cost, usage, failure, cancellation, and policy status; and
10. finish without Jarvis modifying the vault, persisting a transcript, leaking excluded
    content, or silently broadening network authority.

## Current stop line

The project is **ready to finish v0.5 planning**, but it is **not authorized to implement
v0.5**.

The next valid artifact is the corrected CTO planning package followed by Chief-of-Staff
validation and explicit Product Owner decisions. No branch creation, code work, provider
call, evidence run, roadmap renumbering, or historical-candidate modification should occur
before those gates.

## Reference documents

- [Project Control](coordination/README.md)
- [Version Roadmap](product/VERSION_ROADMAP.md)
- [System Roadmap](ROADMAP.md)
- [v0.4 Project Resume Guide](software/PROJECT_RESUME.md)
- [v0.5 Planning Authorization](handovers/v0.5/00-chief-of-staff-to-cto-conversation-planning-authorization.md)
- [Draft Chat PRD](prd/CHAT_INTERFACE.md)
- [Historical Conversation Quality Review](reviews/QUALITY_RELEASE_REVIEW_V0.4_CONVERSATION_2026-07-27.md)
