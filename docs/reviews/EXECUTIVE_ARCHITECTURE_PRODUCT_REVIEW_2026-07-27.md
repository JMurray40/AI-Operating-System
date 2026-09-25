# Executive Architecture and Product Review

| Field | Value |
|---|---|
| Purpose | Assess Jarvis as a product, architecture, and engineering investment after the v0.3 Query Engine |
| Status | Final executive review |
| Version | 1.0.0 |
| Owner | CTO / CPO / Architecture Review Board |
| Reviewed | 2026-07-27 |
| Baseline | `main` through the v0.3 Query Engine and Jarvis v1 Foundation Package |
| Related | [Product Strategy](../product/PRODUCT_STRATEGY.md), [Version Roadmap](../product/VERSION_ROADMAP.md), [v0.3 Architecture Review](arb/2026-07-27-v0.3-architecture-review.md), [Jarvis Bible](../JARVIS_BIBLE.md) |

## Executive conclusion

Jarvis is a **well-governed prototype with a credible product thesis**, not yet a product or platform.

The project is ahead of most early personal-AI projects in architectural restraint, documentation, testing discipline, data ownership, and security intent. The decision to build a read-only, deterministic lexical foundation before adding models, agents, plugins, or writes is correct. The code is modular enough to evolve, and the documentation makes the reasoning unusually inspectable.

The principal danger is no longer poor architecture. It is **strategic overreach**. The repository describes a future spanning personal knowledge, chat, memory, semantic search, plugins, MCP, agents, automation, desktop, mobile, voice, teams, enterprise controls, and a marketplace. A small team can eventually explore that landscape, but it cannot validate all of those businesses and architectures at once.

The next investment should prove one claim:

> Jarvis can help a real user resume an important project faster and with more trustworthy context than their current combination of Obsidian, GitHub, search, and AI chat.

Until that is demonstrated repeatedly, “AI Operating System” is a direction, not market validation. Project Resume, evidence quality, and measured daily utility should dominate the path to v1.0.

## Decision summary

| Question | Assessment |
|---|---|
| Is the architecture healthy? | Yes for a single-user, local-first prototype |
| Is v0.3 technically credible? | Yes, with trust-contract conditions documented by the ARB |
| Is the current roadmap realistic? | Technically coherent but too broad and optimistic for a small team |
| Should agents or automation begin now? | No |
| Should a real provider be connected now? | Only after authorization, citation, confidence, and context-budget gates |
| What should come next? | Query hardening, then a read-only Project Resume vertical slice |
| Is commercial potential proven? | No; differentiation and willingness to pay remain hypotheses |
| Would further investment be justified? | Yes as staged product discovery, not as an immediate platform build-out |

# Part 1 — Executive Assessment

Scores use `1 = absent or structurally unsound` and `10 = proven, scalable, and operationally mature`.

| Area | Score | Assessment |
|---|---:|---|
| Architecture | 7/10 | Strong boundaries, canonical/derived separation, read-only posture, and provider neutrality. Identity, authorization, persistence, and public contracts remain immature. |
| Product direction | 7/10 | The Project Resume and durable cross-AI knowledge thesis is compelling. The roadmap dilutes it with too many adjacent products. |
| Engineering maturity | 6/10 | Tests, linting, typing, ADRs, and CI are strong for the stage. Release artifacts, independent validation, observability, compatibility policy, and operational experience are early. |
| Documentation quality | 9/10 | Exceptional breadth, rationale, cross-linking, and governance. The risk is documentation outrunning validated behavior and creating false certainty. |
| Scalability | 4/10 | Good behavior at 1,000 notes, but no evidence yet for 100,000+, dense graphs, large files, multi-user isolation, or thousands of plugins. |
| Maintainability | 7/10 | Small modules, explicit contracts, tests, and ADRs support change. Dual APIs, graph scans, terminology drift, and premature platform contracts need control. |
| Technical-debt control | 7/10 | Debt is named honestly and review gates exist. Several known trust-contract issues must be resolved before they become API/UI commitments. |
| Risk management | 6/10 | Threat modeling and staged permissions are strong. Enforcement mechanisms, incident procedures, dependency governance, and real-world security tests remain future work. |

**Overall maturity: 6.6/10.** This is high for a prototype and low for a commercial platform. The project has little evidence yet about sustained usage, user comprehension of citations, quality on a messy vault, proposal-review burden, installation/recovery, willingness to pay, or supportability by anyone other than the founder.

# Part 2 — Architecture Review

## Query pipeline

**Strengths:** Responsibilities are separated; lexical retrieval is deterministic and explainable; dependencies are injected without a framework; indexes remain derived; and Trace Mode predates network complexity.

**Weaknesses:** Candidate generation lacks a `Retriever` port; relative rank is called confidence; citations lack supporting passages and source revisions; authorization is absent from retrieval; the context hard-cap contract has an oversized-first-chunk defect; and dual answer surfaces create debt.

**Before v1.0:**

1. Define one versioned `QueryRequest`, `QueryResult`, `Citation`, and `Trace` contract.
2. Add request scope: workspace, user, sources, sensitivity ceiling, and provider egress.
3. Separate retrieval relevance, evidence coverage, and answer confidence.
4. Add passage anchors, fingerprints, and citation validation.
5. Extract retrieval before adding persistence or embeddings.
6. Keep intents as typed capabilities rather than an expanding regex language.

## Parser and knowledge model

**Strengths:** Markdown/YAML remains portable; parsing is deterministic; defects have fixture coverage; schemas establish a migration path.

**Weaknesses:** File names, aliases, IDs, and links can become ambiguous; Obsidian dialect features will widen parser scope; filesystem timestamps are unstable identity; source revision is not yet explicit.

**Before v1.0:** require stable IDs for managed entities, define rename/collision behavior, version parsing rules, preserve unknown syntax, add content fingerprints, and build a real-world Obsidian compatibility corpus.

## Graph

**Strengths:** Relationships are rebuildable, defects are visible, and one-hop traversal is explainable.

**Weaknesses:** Scan-based adjacency invites performance errors; wikilinks are untyped; authored and inferred edges lack distinct provenance; traversal can cross sensitivity boundaries.

**Before v1.0:** precompute adjacency, type edges, keep inferred edges as proposals, authorize traversal, and benchmark actual graph density.

## Provider abstraction

**Strengths:** Providers do not own knowledge or query logic; mock-first development preserves determinism.

**Weaknesses:** A minimal summarization interface cannot represent streaming, structured outputs, cancellation, usage, safety events, multimodality, or provider limits. Neutrality can become a lowest-common-denominator trap.

**Before v1.0:** define a capability-negotiated protocol with versioned requests/events, structured output, cancellation, usage, policy labels, context limits, and data-retention attributes.

## CLI

The CLI is an excellent reference and diagnostics client, but not evidence of mainstream usability. Preserve it, version its JSON contracts, and organize future commands around jobs—`resume`, `find`, `ask`, `inspect`, and `review`—rather than internal modules.

## Testing strategy

**Strengths:** Unit/integration coverage, determinism, read-only validation, malformed input, scale fixtures, and a permanent 260-question benchmark.

**Weaknesses:** Test count alone is not quality evidence; the benchmark is not yet an executed scoring system; performance focuses on medians at 1,000 notes; security, migration, fuzz, compatibility, and usability coverage remain limited.

Before v1.0, execute judged retrieval/citation benchmarks, add property-based parsing, adversarial security tests, p50/p95/p99 and memory measurements, upgrade/restore tests, and human trust/usability evaluation.

## ADR process

The ADR and standing review processes are major strengths. The risks are ceremony, unenforced intent, and status drift. Create ADRs only for durable decisions, link them to enforcement tests, review superseded decisions quarterly, and maintain one release-status source.

## Plugin strategy

Designing permissions and isolation first is correct. “Thousands of plugins” is not a validated requirement, signing is not trust, and a marketplace creates significant moderation and liability. Prove the capability gateway with two or three first-party connectors before publishing an SDK.

# Part 3 — Product Review

## Roadmap realism

The sequence is coherent, but the breadth and pace are not realistic for one engineer plus AI assistance. It combines a knowledge engine, chat app, memory system, plugin runtime, agent platform, automation service, four client surfaces, team product, and enterprise marketplace.

Three changes are recommended:

1. **Project Resume before general chat.** It is the clearest differentiated job and can use the current read-only engine.
2. **A trust-contract hardening release before real providers.**
3. **One Tool Gateway before plugins, MCP, agents, or automation.**

Missing concerns include product instrumentation, weekly dogfood review, installation/update/recovery, stable source identity, provider egress, design-partner and pricing research, retention/deletion, accessibility, and comparison against simply using existing tools.

Being considered too early: general agents, a marketplace, enterprise multi-tenancy, voice, deep mobile, and million-note/thousand-plugin targets. Being postponed too long: Project Resume, real-vault evaluation, understandable trust semantics, and operational simplicity.

Use one loop through v1.0:

```text
Select project
  -> retrieve evidence
  -> inspect and correct context
  -> produce a sourced briefing
  -> work
  -> propose a durable outcome
  -> approve or reject
  -> resume faster next time
```

# Part 4 — Technical Debt Review

| Priority | Debt or risk | Impact | Action |
|---|---|---|---|
| Critical before providers | Relative rank named confidence | False trust and misleading API | Rename/version before UI integration |
| Critical before providers | Note-level citations | Generated prose may appear supported when it is not | Add passage anchors, revisions, validation |
| Critical before broader data | No sensitivity-aware retrieval | Private content can reach context, trace, or egress | Scope retrieval before candidate generation |
| High | Context budget not a strict invariant | Provider limits/cost can be exceeded | Define and test hard-cap behavior |
| High | Dual answer surfaces | Divergent behavior and support burden | Make legacy API an adapter |
| High | Ambiguous identity | Incorrect relationships and context | Stable IDs and collision policy |
| Medium | Scan-based graph calls | Performance regressions | Precompute adjacency |
| Medium | Zero-score graph results mixed with relevance | Misleading ordering | Type selection channels |
| Medium | Per-invocation index build | Larger-vault latency | Measure threshold, then project incrementally |
| Medium | Heuristic intent grammar | Brittleness | Keep small; use typed UI/API for complexity |

Future debt is likely if provider details leak into domain logic, runtime state becomes canonical, prompts become undocumented business logic, permission logic is duplicated, clients interpret trust states differently, or enterprise concerns contaminate the personal product.

Refactor in this order: trust contracts; identity/revision; Retriever and adjacency; one result/trace contract; operational permission/event model; persisted index only after measurement.

# Part 5 — Competitive Position

Jarvis does not yet compete as an end-user product. Its differentiation is architectural: owned Markdown, provider replacement, evidence and trace, progressive permissions, Project Resume, and clean data boundaries. That matters commercially only when the experience is easier than assembling existing tools.

| Product | Current strength | Jarvis risk | Jarvis opportunity |
|---|---|---|---|
| Obsidian | Local files, links, graph, plugins | Plugins may provide “good enough” AI | Become its governed cross-system intelligence layer |
| Logseq | Blocks, journals, queries, local-first | Strong daily/task workflows | Support project/document work without block lock-in |
| Tana | Typed structure and integrated AI | Faster structured workflow delivery | Portable Markdown/YAML plus governance |
| Capacities | Polished objects, queries, AI | Already combines typed knowledge and AI | Ownership, provider choice, orchestration |
| Mem | Low-friction AI recall | Jarvis may feel administratively heavy | Convenient recall with inspectable memory |
| Reflect | Focus, backlinks, encryption, mobile | Simplicity may win | Optional operations without disturbing writing |
| Notion AI | Collaboration, connectors, enterprise search | Huge product/distribution advantage | Local-first sensitive individual workflows |

The baseline is moving quickly: Obsidian emphasizes filesystem-compatible knowledge and graph relationships ([About](https://obsidian.md/help/obsidian), [Graph](https://obsidian.md/help/Plugins/Graph%2Bview)); Logseq supports Markdown graphs, blocks, queries, and plugins ([docs](https://docs.logseq.com/)); Capacities combines typed objects, contextual AI, queries, and AI connectors ([objects](https://docs.capacities.io/reference/content-types), [AI](https://docs.capacities.io/reference/ai-assistant)); Mem offers AI-assisted collections ([docs](https://help.mem.ai/features/collections)); Reflect offers networked notes, encryption, mobile, calendar, and AI ([site](https://reflect.app/)); and Notion Research Mode searches workspaces, connected apps, and the web while showing sources ([docs](https://www.notion.com/help/research-mode)).

Jarvis should position itself as a **trustworthy project-continuity layer for work spanning tools and AI providers**, not another notes application.

# Part 6 — Engineering Review

| Area | Assessment | Highest-value improvement |
|---|---|---|
| Testing | Strong prototype discipline | Execute benchmark scoring; add security, property, migration, and usability tests |
| Documentation | Exceptional, possibly excessive | Mark authority/status; remove duplication; connect requirements to tests |
| Performance | Appropriate at 1,000 notes | Measure real vault, cold/warm percentiles, memory, and worst cases |
| Code organization | Healthy | Add ports only when a second implementation is imminent |
| Developer experience | Good for founder, unproven for newcomer | Test clean setup/recovery with another person |
| Release process | Emerging | Define preview/beta/stable and require ARB/release evidence |
| CI/CD | Suitable baseline | Add Windows, dependency/secret/license/SAST checks and benchmark artifacts |
| Branch strategy | Appropriate if simple | Protected `main`, short branches, required checks, release tags |
| Versioning | Ambiguous | Separate product, document, schema, and protocol versions |

Do not introduce a long-lived development branch. Pin CI actions for supply-chain control. Preserve the CLI as the diagnostic reference even after a desktop client exists.

# Part 7 — Product Vision

## One year

A realistic outcome is a dependable personal knowledge/developer tool: read-only Project Resume, visible-context chat with one local and one cloud provider, evidence inspection, proposed session/decision memory, GitHub/calendar reads, a basic desktop shell, and robust backup/update diagnostics.

Commercially, this could support a design-partner beta for technical professionals, consultants, accountants, and researchers. Retention and time saved matter more than user count.

## Three years

If retention is proven and the team grows: a mature desktop product, secure companion access, hybrid relationship intelligence, a capability gateway, curated connectors, bounded recurring workflows, and limited small-team support.

The strongest business may be a premium personal/professional product or verticalized high-trust workflow, not a general platform.

## Five years

With adoption, capital, and a multidisciplinary team: a governed personal/team context platform, portable cross-provider memory, certified integrations, policy-controlled agents, durable workflows, multiple clients, and enterprise deployment options.

This becomes a platform only if Jarvis owns a durable control point—trusted context, permission governance, or cross-provider memory. A connector bundle around Obsidian is not a defensible platform.

# Part 8 — Prioritized Roadmap

## 1. v0.3.1 — Query Trust Contracts

- **Objective:** Correct safety and semantics before providers.
- **Features:** relevance rename, hard budget, passage/revision citations, request scope, result/trace v1, roadmap reconciliation.
- **Dependencies:** ARB conditions C1–C5.
- **Risks:** compatibility churn.
- **Success:** unauthorized notes cannot enter candidates/context/trace; citations validate; budget invariant holds.

## 2. v0.4 — Project Resume CLI Pilot

- **Objective:** Prove the signature workflow without AI or writes.
- **Features:** `resume`, project identity, sessions, decisions, tasks, resources, repository links, missing-context warnings.
- **Dependencies:** trust contracts and two pilot projects.
- **Risks:** metadata quality and ambiguous identity.
- **Success:** resume under 30 seconds; ≥80% useful; measurable time saved; every statement traceable.

## 3. v0.4.1 — Real-Vault Evaluation

- **Objective:** Turn dogfood into evidence.
- **Features:** executable 260-case suite, judged retrieval, actual-vault performance, correction capture, privacy-safe metrics.
- **Dependencies:** stable query contracts.
- **Risks:** benchmark overfitting.
- **Success:** published retrieval/citation metrics and four weeks without critical regression.

## 4. v0.5 — Visible-Context Chat

- **Objective:** Add conversation after trust controls.
- **Features:** local API, preview, Ollama and one cloud adapter, streaming, egress labels, cost/latency, retained/deletable conversations.
- **Dependencies:** secrets and operational event model.
- **Risks:** leakage, citation mismatch, cost.
- **Success:** validated citations, provider switching, verified deletion, zero disallowed egress.

## 5. v0.6 — Proposed Memory

- **Objective:** Close the resume/work/preserve loop.
- **Features:** session and decision proposals, exact diffs, expected hashes, atomic writes, backup, conflicts, audit, rollback.
- **Dependencies:** successful chat pilot and write-security ADR.
- **Risks:** vault damage and approval fatigue.
- **Success:** zero silent writes; recovery passes; review median under two minutes.

## 6. v0.7 — Hybrid Retrieval and Relationships

- **Objective:** Improve recall only where lexical search fails.
- **Features:** local embeddings, hybrid fusion, typed relationship/contradiction proposals, feedback.
- **Dependencies:** judged lexical baseline and Retriever port.
- **Risks:** opacity, false edges, compute.
- **Success:** meaningful benchmark improvement; explainable edges; scoped rebuildable embeddings.

## 7. v0.8 — Capability and Tool Gateway

- **Objective:** Create one boundary for every future effect.
- **Features:** grants, approvals, secrets, egress, audit, cancellation, idempotency, first-party read connectors.
- **Dependencies:** operational database and threat review.
- **Risks:** permission complexity.
- **Success:** undeclared actions impossible; revocation and negative security tests pass.

## 8. v0.9 — Curated Plugins and MCP

- **Objective:** Validate extensibility with a tiny trusted catalog.
- **Features:** isolated host, manifests, compatibility, safe mode, mediated MCP, 2–3 integrations.
- **Dependencies:** Tool Gateway.
- **Risks:** supply-chain and support burden.
- **Success:** malicious fixture remains confined; plugin failure cannot crash core.

## 9. v0.10 — Bounded Workflow Preview

- **Objective:** Automate narrow flows without general agents.
- **Features:** workflows, schedules, approval nodes, retries, dead-letter, execution history.
- **Dependencies:** reliable connectors and Tool Gateway.
- **Risks:** duplicate effects and stale approvals.
- **Success:** restart-safe, idempotent, fully audited reference workflows.

## 10. v1.0 — Trusted Personal Jarvis

- **Objective:** Productize the validated loop.
- **Features:** desktop shell, installer/updater, Resume, search, chat, memory review, curated connectors, workflows, backup/recovery, diagnostics.
- **Dependencies:** prior gates, external security review, 90-day dogfood.
- **Risks:** packaging, support, upgrade failure, scope.
- **Success:** clean install/recovery, two-version rollback, no critical findings, core SLOs, retained use and measured savings.

General agents, voice, broad mobile, teams, marketplace, and enterprise work should remain post-v1.0.

# Part 9 — Blind Spots

1. The vault may be too incomplete or stale for reliable synthesis.
2. “One brain” may conflict with legal, privacy, and cognitive separation.
3. Users also navigate through people, dates, clients, and urgency—not only projects.
4. Markdown is poor for some transactional or high-volume data.
5. Local-first does not automatically mean private.
6. Supporting many providers may add more complexity than value.
7. Users may rubber-stamp or abandon memory approvals.
8. Relationship noise can destroy trust.
9. AI-assisted coding does not remove the human review bottleneck.
10. Enterprise is a different architecture and business, not a natural checkbox.

Before investing another year, validate repeated weekly Project Resume use, 15–30 minutes saved per meaningful switch, 90–95% citation correctness, maintenance cost below value, external design-partner retention, willingness to pay, non-author installation/recovery, privacy expectations, real hybrid-search lift, and sustainable connector maintenance.

# Part 10 — Executive Recommendations

## Ten strongest aspects

1. Human-owned Markdown/YAML knowledge.
2. Canonical/derived/operational separation.
3. Read-only-first progression.
4. Explainable lexical baseline.
5. Provider abstraction before proliferation.
6. Tests, typing, linting, fixtures, and CI.
7. ADR and independent review discipline.
8. Explicit extensibility threat awareness.
9. Concrete Project Resume thesis.
10. Willingness to defer fashionable technology.

## Ten biggest weaknesses

1. No validated end-user experience.
2. Too many products in one roadmap.
3. Differentiation remains theoretical.
4. Incomplete provider trust contracts.
5. Limited real-vault quality evidence.
6. Unproven install/update/recovery.
7. Immature identity/revision semantics.
8. Documentation may exceed governance capacity.
9. Unsupported strategic scale assumptions.
10. Undefined commercial user and pricing hypotheses.

## Ten highest-ROI improvements

1. Ship read-only Project Resume.
2. Measure weekly savings and corrections.
3. Correct confidence terminology.
4. Add passage/revision citations.
5. Enforce sensitivity before retrieval/egress.
6. Execute the 260-case benchmark.
7. Stabilize identity and collisions.
8. Test setup/recovery with another person.
9. Collapse roadmaps to one current plan.
10. Recruit design partners before expanding scope.

## Five most important decisions ahead

1. Stable entity, resource, rename, and source-revision identity.
2. Request authorization, sensitivity, and provider egress.
3. Claim-to-passage evidence and answer-confidence contracts.
4. Operational state for permissions, audit, jobs, secrets, and retention.
5. One capability boundary for tools, plugins, MCP, workflows, and agents.

## Single biggest mistake

**Do not build the platform before proving the indispensable workflow.**

Agents, plugins, voice, mobile, enterprise, and a marketplace can consume years without daily value. If evidence-backed Project Resume is not indispensable, the larger platform will not rescue the product.

## Investment decision

**Invest in the next 9–12 months as staged product validation, not as a broad platform commitment.**

The disciplined architecture, real problem, low-risk progression, founder dogfood environment, and testable Project Resume hypothesis justify continued investment. The lack of retention, willingness-to-pay, polished UX, operational evidence, and validated differentiation does not yet justify a larger platform bet.

The next funding or staffing gate should require repeated weekly use, measurable savings, high citation correctness, manageable maintenance, and external design-partner interest.

## Final directive

Authorize v0.3.1 trust hardening, v0.4 Project Resume, and eight weeks of real-vault dogfood. Defer general agents, marketplace, broad automation, voice, teams, and enterprise work.

Run the standing Architecture Review Board after each material implementation. Advance only when user value, trust, security, recovery, and operability evidence passes—not when a feature list is complete.

## Revision history

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-07-27 | Initial executive architecture, product, and investment review |
