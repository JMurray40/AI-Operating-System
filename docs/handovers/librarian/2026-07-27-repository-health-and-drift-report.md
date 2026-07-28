# Repository Health and Documentation Drift Report

| Field | Value |
|---|---|
| Role | Historian / Librarian |
| Audit date | 2026-07-27 |
| Status | Read-only audit report |
| Repository | `JMurray40/AI-Operating-System` |
| Primary worktree observed | `feature/v0.4-conversation` at `4b09050b76fd9a448af3ce91b4aa66963d23dad2` |
| v0.3.1 engineering worktree observed | `feature/v0.3.1-query-trust-contracts` at `3918257ba1f5325b2f56f89a81574c4144c6004f` |
| v0.3.1 governance worktree observed | `codex/v0.3.1-governance-base` at `a6c89c5be8ce78a4d9d6359a62c94aa83a84d513` |
| v0.3.1 QA worktree observed | Detached at `09a4ca5a6e0d9b73a1e37a9e086abe788c894c72` |
| Audit boundary | Documentation, coordination, handoffs, ADRs, PRDs, roadmaps, changelog, and repository navigation |
| Mutation policy | No code, staging, commit, merge, push, branch, or existing-worktree change; this report is the only created artifact |

## 1. Executive assessment

**Repository health score: 50/100 — material documentation drift; coordination is not
safe to consume from the primary worktree without cross-worktree knowledge.**

The repository has unusually strong source material for its age: formal governance,
defined roles, an explicit handoff contract, numbered ADRs, indexed PRDs, architecture and
implementation reports, adversarial QA records, and a coordination page intended to make
conversation history unnecessary. Local links in the primary worktree are structurally
healthy.

The central integrity problem is that the most current operational record is split across
worktrees. The primary worktree's control page says the CTO should act from Handoff 00,
while the v0.3.1 engineering worktree's later control page says the Principal Engineer
should act from Handoff 06 on an evidence-only correction. A new agent entering through
the documented primary control page cannot discover that effective incoming artifact
without knowing to inspect another worktree.

Release naming also has two competing histories:

- the approved sequence is **v0.3 Query Engine**, **v0.3.1 Query Trust Contracts**,
  **v0.4 Project Resume**, and **v0.5 conversation**; but
- the primary README, changelog, handbook, ADR index revision history, software
  architecture, CLI guide, and conversation implementation report still call conversation
  **v0.4**.

The contradictions are recorded in review and coordination artifacts, but they have not
been propagated into the repository's main navigation and release authorities.

## 2. Scorecard

| Category | Weight | Score | Weighted result | Assessment |
|---|---:|---:|---:|---|
| Repository navigation | 15 | 55 | 8.25 | Strong root reading order, but no root link to the control page or handbook |
| Cross-reference integrity | 15 | 87 | 13.05 | Primary tree has no broken local file targets; engineering tree has two |
| ADR/PRD integrity | 15 | 45 | 6.75 | Accepted ADRs omitted from the primary index; PRD release targets are stale |
| Roadmap/release consistency | 20 | 30 | 6.00 | Approved release identities conflict with multiple high-visibility documents |
| Changelog/historical integrity | 15 | 45 | 6.75 | Unreleased history conflates parked v0.4 conversation with approved v0.4 Project Resume |
| Handoff discoverability | 15 | 35 | 5.25 | Current incoming artifact is not discoverable from the primary start page |
| Governance/process consistency | 5 | 75 | 3.75 | Governance is coherent; its artifact rules are not consistently reflected in status metadata |
| **Total** | **100** |  | **49.80 raw** |  |

The reported health score is the weighted result rounded to the nearest whole number.
Future reports should retain this rubric so movement is comparable across milestones.

## 3. Authorities and audit method

The audit began with:

- `docs/coordination/README.md`
- `docs/GOVERNANCE.md`
- `docs/WAYS_OF_WORKING.md`
- `Operating Handbook - AI Agent Roles.md`
- `docs/handovers/v0.3.1/`

The following were then compared:

- primary, governance, engineering, and QA worktree artifact presence;
- all Markdown local file targets in the primary worktree, excluding nested worktrees;
- all Markdown local file targets in the v0.3.1 engineering worktree;
- ADR files, declared statuses, and `docs/adr/README.md`;
- PRD files, declared statuses/targets, and `docs/prd/README.md`;
- `README.md`, `CHANGELOG.md`, `docs/ROADMAP.md`, and
  `docs/product/VERSION_ROADMAP.md`;
- the project turnover, Operating Handbook, coordination page, implementation reports,
  architecture reviews, and v0.3.1 handoff revisions.

This report distinguishes:

1. **accepted product direction**, which has governance precedence;
2. **committed worktree state**;
3. **uncommitted or worktree-local documentation evidence**; and
4. **parked implementation claims**, which are not release history.

## 4. Findings by severity

### Critical

#### L-CRIT-01 — The documented start page does not expose the current incoming artifact

**Paths**

- `docs/coordination/README.md`
- `docs/handovers/v0.3.1/00-chief-of-staff-to-cto-finalize-implementation-brief.md`
- `.worktrees/v0.3.1-engineering/docs/coordination/README.md`
- `.worktrees/v0.3.1-engineering/docs/handovers/v0.3.1/06-chief-of-staff-to-principal-engineer-evidence-correction.md`

**Evidence**

The primary control page identifies Handoff 00 as the current incoming handoff, names the
CTO as the next responsible role, and says Chief of Staff validation is still blocked.
The engineering worktree's later control page instead records:

- the implementation brief as validated;
- engineering as returned for evidence-only correction;
- QA disposition as `Refactor first`;
- CTO Revision 6 as `EVIDENCE CORRECTION REQUIRED`; and
- Handoff 06 as the current Principal Engineer input.

Handoffs 03 through 06 are absent from the primary worktree's handover directory. A new
agent following the required start procedure cannot reach the effective artifact from
primary-tree navigation.

**Impact**

An agent can accept the wrong role, repeat completed work, or act against an obsolete
gate. This defeats the explicit requirement that work be recoverable without conversation
history.

**Recommended correction**

After the active review cycle is safely closed, publish one canonical coordination
revision on the designated authoritative branch. It should name the exact current
incoming path, worktree/branch, candidate commit, effective revision, receiver, and blocker.
Do not copy partial state between worktrees without an identified synchronization commit.

### High

#### L-HIGH-01 — Approved release naming is contradicted by high-visibility documentation

**Approved naming**

- v0.3 — Query Engine
- v0.3.1 — Query Trust Contracts
- v0.4 — Project Resume
- v0.5 — conversation / Visible-Context Chat

**Contradictory paths**

- `README.md`
- `CHANGELOG.md`
- `Operating Handbook - AI Agent Roles.md`
- `docs/adr/README.md`
- `docs/software/ARCHITECTURE.md`
- `docs/software/CLI_USAGE.md`
- `docs/software/V0.4_IMPLEMENTATION_REPORT.md`
- `docs/software/CONVERSATION.md`
- `docs/reviews/QUALITY_RELEASE_REVIEW_V0.4_CONVERSATION_2026-07-27.md`

**Evidence**

The primary README and changelog present conversation as v0.4. The handbook directs the
Principal Engineer to implement v0.4 conversational intelligence. The ADR index says
ADR-0013 was added for the v0.4 conversation layer. The architecture and CLI guides label
conversation v0.4, and the implementation report is named as a v0.4 report.

By contrast, the Product Owner approval, coordination page, project turnover, executive
review, v0.3.1 brief, and v0.4 acceptance tests establish Project Resume as v0.4 and move
conversation to v0.5.

**Impact**

Release identity is not reproducible from the repository. Search results can support
either answer, and the parked branch name appears more authoritative than the accepted
Product Owner decision.

**Recommended correction**

Do not rewrite the parked branch's history. Mark its documents explicitly as a
pre-resequencing candidate, record that the implementation is to be reconciled as v0.5,
and update all current navigation/release authorities to the approved sequence. Preserve
the former v0.4 identity in revision history.

#### L-HIGH-02 — The primary ADR index omits four accepted ADRs

**Paths**

- `docs/adr/README.md`
- `docs/adr/ADR-0014-Retrieval-Relevance-Is-Separate-From-Answer-Confidence.md`
- `docs/adr/ADR-0015-Authorization-Precedes-Retrieval-And-Graph-Expansion.md`
- `docs/adr/ADR-0016-Citations-Bind-Passages-To-Source-Revisions.md`
- `docs/adr/ADR-0017-Stable-Source-Identity-Is-Separate-From-Location.md`

**Evidence**

ADR-0014 through ADR-0017 each declare `Accepted`, and the coordination page says the
Product Owner accepted them. The primary ADR index ends at ADR-0013. The v0.3.1
engineering worktree has an updated index, but that is not the index exposed by the
primary worktree.

**Impact**

Navigation understates the accepted architecture governing the active milestone.

**Recommended correction**

Once the authoritative documentation base is selected, add ADR-0014 through ADR-0017 to
the canonical index with their accepted statuses, v0.3.1 relationship, and approval
record. Retain prior index revision history.

#### L-HIGH-03 — Handoff documents do not make their latest effective revision obvious

**Paths**

- `.worktrees/v0.3.1-engineering/docs/handovers/v0.3.1/03-principal-engineer-to-cto-engineering-review.md`
- `.worktrees/v0.3.1-engineering/docs/handovers/v0.3.1/04-cto-to-quality-architecture-disposition.md`
- `.worktrees/v0.3.1-engineering/docs/handovers/v0.3.1/05-quality-to-product-owner-release-review.md`

**Evidence**

Handoff 03 contains multiple appended readiness statements and at least six evidence
revisions, while its top metadata still says `Ready for architecture
fitness/conformance review`. Handoff 04 contains earlier `READY FOR QUALITY & RELEASE`
language followed later by Revision 6's `EVIDENCE CORRECTION REQUIRED`. A reader can stop
at an obsolete disposition before reaching the superseding material.

The documents contain useful supersession language internally, but their top metadata does
not state:

- current effective revision;
- current effective disposition;
- superseded revision numbers;
- candidate commit governed by that revision; or
- the next incoming artifact.

**Impact**

The latest state depends on reading an entire long document and correctly interpreting
append order.

**Recommended correction**

Require a top-level `Effective revision`, `Effective as of commit`, `Current disposition`,
`Supersedes`, and `Next artifact` block. Preserve all earlier revisions below it. For
future major re-reviews, prefer a separately numbered superseding handoff over repeated
append-only dispositions in one file.

#### L-HIGH-04 — The primary changelog treats parked conversation work as the leading v0.4 release

**Path**

- `CHANGELOG.md`

**Evidence**

The first Unreleased section is `v0.4 — Read-Only Conversational Intelligence, in review`.
The accepted sequence reserves v0.4 for Project Resume, and Quality & Release has said the
conversation candidate is not ready. The changelog does not yet contain a v0.3.1 Trust
Contracts closeout entry in the primary worktree.

**Impact**

The changelog implies a release direction that governance has superseded and can be
mistaken for shipped history.

**Recommended correction**

Separate `Released`, `Accepted but not released`, `In review`, and `Parked/resequenced`
states. Add v0.3.1 only after its actual release decision and merge evidence exist. Retain
the conversation candidate as historical work under a clearly parked/resequenced heading.

#### L-HIGH-05 — The canonical roadmap has not absorbed the accepted release sequence

**Paths**

- `docs/product/VERSION_ROADMAP.md`
- `docs/ROADMAP.md`
- `docs/coordination/README.md`
- `docs/handovers/2026-07-27-JARVIS-PROJECT-TURNOVER.md`
- `docs/reviews/EXECUTIVE_ARCHITECTURE_PRODUCT_REVIEW_2026-07-27.md`

**Evidence**

`VERSION_ROADMAP.md` still defines:

- v0.3 as Read-only Chat and Provenance;
- v0.4 as Project Resume and Dashboard; and
- v0.5 as Proposed Memory.

Later accepted direction defines v0.3 as the Query Engine foundation, inserts v0.3.1 Trust
Contracts, keeps Project Resume at v0.4, and moves conversation to v0.5. The broad
milestone roadmap uses a third naming scheme based on Milestones 0–7.

**Impact**

Roadmap alignment cannot be checked mechanically, and PRD targets inherit obsolete
release identities.

**Recommended correction**

Publish a roadmap revision with an explicit old-to-new mapping. Preserve the original
v0.3 acceptance criteria and show each as completed, deferred, or moved. Add a crosswalk
between numbered milestones and semantic versions.

### Medium

#### L-MED-01 — PRD index targets conflict with approved release identities

**Paths**

- `docs/prd/README.md`
- `docs/prd/CHAT_INTERFACE.md`
- `docs/prd/DASHBOARD.md`
- `docs/prd/MEMORY_SYSTEM.md`
- `docs/prd/SEARCH_ENGINE.md`

**Evidence**

The PRD index still assigns Chat to v0.3 and Memory to v0.5. The accepted release decision
moves conversation to v0.5, which now collides with the Memory PRD target. Dashboard is
v0.4, but the active v0.4 definition is specifically Project Resume and has a separate
acceptance-test document rather than a clearly accepted Project Resume PRD. Search remains
targeted to v0.2 lexical/v0.6 hybrid even though the v0.3 Query Engine and v0.3.1 Trust
Contracts materially change its public contract.

All ten capability PRDs declare `Draft`; the index calls them
`implementation-ready feature requirements` without distinguishing accepted from draft
requirements.

**Recommended correction**

Add columns for PRD status, current target, superseded target, governing ADRs, and
implementation/release status. Either create/accept a Project Resume PRD or explicitly
designate the v0.4 acceptance tests and approved Product Owner artifact as its requirement
authority.

#### L-MED-02 — ADR accepted-status semantics are historically incomplete

**Paths**

- `docs/adr/README.md`
- `docs/adr/ADR-0001-The-Brain-Is-The-Durable-Knowledge-Layer.md`
- `docs/adr/ADR-0002-Markdown-Is-The-Canonical-Storage.md`
- `docs/adr/ADR-0003-GitHub-Is-The-Source-Of-Truth-For-Code.md`
- `docs/adr/ADR-0006-Use-Python-For-Jarvis-Core-Prototype.md`

**Evidence**

ADR-0001 through ADR-0003 and ADR-0006 remain Proposed even though the repository and
implementation rely on their decisions. ADR-0006 is present as a file but is not a link
in the primary index; the row says to reconcile it before commit.

This audit does not infer that those ADRs should be accepted. It records that operational
practice and declared decision status differ.

**Recommended correction**

Have the decision owner explicitly accept, reject, supersede, or mark each as
`Implemented while Proposed`. Do not silently convert statuses or rewrite the original
decision records.

#### L-MED-03 — The Operating Handbook duplicates volatile project state

**Paths**

- `Operating Handbook - AI Agent Roles.md`
- `docs/coordination/README.md`

**Evidence**

The handbook contains `Current Priorities` and `Immediate Next Actions`, including
`Implement v0.4 Read-Only Conversational Intelligence`. The coordination page says v0.3.1
is active and conversation is parked/resequenced to v0.5.

The stable organizational handbook and volatile coordination ledger therefore both claim
to describe current work.

**Recommended correction**

Keep role definitions, artifact contracts, and durable workflow in the handbook. Replace
volatile priorities with one link to the coordination page. Preserve this obsolete
priority list in revision history.

#### L-MED-04 — The old turnover remains labeled “Current handover”

**Paths**

- `docs/handovers/2026-07-27-JARVIS-PROJECT-TURNOVER.md`
- `docs/coordination/README.md`

**Evidence**

The project turnover declares `Status | Current handover`, but later role-specific
v0.3.1 handoffs now govern the active work. Some decisions requested in the turnover have
since been accepted and recorded.

**Recommended correction**

Mark the turnover as a historical program-level baseline and link to the coordination
page for current execution state. Do not delete or rewrite its original recommendations.

#### L-MED-05 — Multiple same-sequence handoffs weaken chronological navigation

**Path**

- `.worktrees/v0.3.1-engineering/docs/handovers/v0.3.1/`

**Evidence**

The directory contains:

- two sequence-02 artifacts;
- five sequence-04 artifacts, including four remediation-prompt revisions and the CTO
  disposition;
- three sequence-05 artifacts for remediation, QA prompting, and QA disposition.

The filenames accurately name sender and receiver, but sequence numbers no longer
represent a single linear chain. Revision suffixes are inconsistent (`rev2`, `rev3`,
`rev4`, while the first revision has no suffix).

**Recommended correction**

Choose one convention:

1. global monotonically increasing handoff sequence numbers; or
2. stage number plus explicit revision and effective-status index.

Do not rename accepted historical artifacts without a migration record; introduce the
new rule for future handoffs and add a manifest mapping the existing chain.

#### L-MED-06 — Cross-worktree documentation does not form one coherent link graph

**Paths**

- `.worktrees/v0.3.1-engineering/docs/software/V0.4_IMPLEMENTATION_REPORT.md`
- `.worktrees/v0.3.1-engineering/docs/adr/ADR-0013-Conversation-Is-A-Read-Only-Session-Only-Layer.md`
- `.worktrees/v0.3.1-engineering/docs/software/CONVERSATION.md`

**Evidence**

The v0.3.1 engineering tree has two broken local targets:

- `V0.4_IMPLEMENTATION_REPORT.md` → `../adr/ADR-0013-Conversation-Is-A-Read-Only-Session-Only-Layer.md`
- `V0.4_IMPLEMENTATION_REPORT.md` → `CONVERSATION.md`

The report is present in that tree, but its linked conversation documents are not.

**Recommended correction**

The v0.3.1 branch should either exclude the parked conversation report entirely or retain
an explicitly historical stub whose links resolve within the same revision. Do not rely
on files that exist only in another worktree.

### Low

#### L-LOW-01 — Root navigation does not expose the mandatory coordination start page

**Paths**

- `README.md`
- `CONTRIBUTING.md`
- `docs/coordination/README.md`
- `Operating Handbook - AI Agent Roles.md`

**Evidence**

No root README or contributor-guide link points to the coordination control page or the
Operating Handbook. Only the coordination page links to the handbook. A contributor must
already know the control page exists.

**Recommended correction**

Add a single prominent “Current work and handoffs” entry to root navigation after the
coordination system is committed on the authoritative branch.

#### L-LOW-02 — The primary ADR index metadata version does not match its own revision history

**Path**

- `docs/adr/README.md`

**Evidence**

The metadata table says Version `0.2.0`, while revision history contains `0.3.0` and
`0.4.0`.

**Recommended correction**

Update the document metadata version as part of the next accepted index revision and add
an automated consistency check.

#### L-LOW-03 — Document states are not consistently distinguished

**Affected classes**

- accepted governance;
- proposed/accepted ADRs;
- draft PRDs;
- in-review implementation reports;
- parked work;
- QA-rejected candidates;
- released capability.

**Evidence**

High-level indexes often show only a title and target, while status is buried in the
document. “Added,” “implemented,” “in review,” and “released” are used close together
without a shared lifecycle vocabulary.

**Recommended correction**

Adopt canonical document/release states and require them in indexes:
`Draft`, `Proposed`, `Accepted`, `Implementation complete`, `In review`, `Returned`,
`Parked`, `Merged`, `Released`, `Superseded`, and `Historical`.

## 5. Broken cross-reference report

### Primary worktree

| Check | Result |
|---|---:|
| Markdown files checked, excluding nested worktrees | 127 |
| Local Markdown file targets checked | All discovered targets |
| Broken local file targets | **0** |

This result validates local file existence, not the continuing truth of the linked claim.
It also does not certify external URLs or every Markdown heading fragment.

### v0.3.1 engineering worktree

| Source | Broken target |
|---|---|
| `docs/software/V0.4_IMPLEMENTATION_REPORT.md` | `../adr/ADR-0013-Conversation-Is-A-Read-Only-Session-Only-Layer.md` |
| `docs/software/V0.4_IMPLEMENTATION_REPORT.md` | `CONVERSATION.md` |

### Navigation failure that is not a syntactically broken link

The primary coordination page's link to Handoff 00 resolves correctly but is
operationally stale. This is more dangerous than a 404 because the link looks valid while
directing the reader to an obsolete stage.

## 6. ADR/PRD consistency report

### ADR summary

| Range | File status | Primary index status | Finding |
|---|---|---|---|
| ADR-0001–0003 | Proposed | Proposed | Relied upon in practice; decision owner review needed |
| ADR-0004–0005 | Accepted | Accepted | Consistent |
| ADR-0006 | Proposed | Proposed, unlinked | Index/navigation defect; implementation relies on Python |
| ADR-0007 | Accepted | Accepted | Consistent |
| ADR-0008–0009 | Proposed | Proposed | Consistent |
| ADR-0010 | Accepted | Accepted | Consistent |
| ADR-0011 | Proposed | Proposed | Consistent |
| ADR-0012 | Accepted | Accepted | Consistent |
| ADR-0013 | Accepted | Accepted | Status consistent; release association is stale |
| ADR-0014–0017 | Accepted | Missing | High-severity index omission |

No duplicate ADR number was found. Numbering is sequential through ADR-0017. No ADR
declares itself superseded. This audit recommends status review but does not change or
reinterpret any accepted ADR.

### PRD summary

| Capability | Declared status | Indexed target | Consistency finding |
|---|---|---|---|
| Search | Draft | v0.2 lexical; v0.6 hybrid | Does not expose v0.3/v0.3.1 implementation and contract state |
| Chat | Draft | v0.3 | Superseded target; accepted sequence moves conversation to v0.5 |
| Dashboard | Draft | v0.4 | Broadly aligned, but Project Resume authority is not clearly this PRD |
| Memory | Draft | v0.5 | Target collision with accepted v0.5 conversation |
| Knowledge graph | Draft | v0.6 | No immediate naming conflict |
| Plugins/MCP | Draft | v0.7 | No immediate naming conflict |
| Agents | Draft | v0.8 | No immediate naming conflict |
| Automation | Draft | v0.9 | No immediate naming conflict |
| Mobile | Draft | v1.2 | No immediate naming conflict |

The PRD index does not claim that any PRD is accepted, but its purpose says it indexes
implementation-ready requirements. That description should be qualified while every PRD
remains Draft.

## 7. Duplicate, superseded, stale, and contradictory record map

| Record | Classification | Effective replacement or governing record |
|---|---|---|
| `Operating Handbook - AI Agent Roles.md` current-priority sections | Stale | `docs/coordination/README.md` plus accepted Product Owner handoff |
| `docs/handovers/2026-07-27-JARVIS-PROJECT-TURNOVER.md` status “Current handover” | Stale program baseline | v0.3.1 role-specific handoffs and coordination page |
| Primary `docs/coordination/README.md` Handoff 00 pointer | Stale | Engineering-tree coordination page and Handoff 06 |
| Handoff 00 `Ready for CTO action` | Superseded in substance | Product Owner approval, CTO brief, validation, engineering and review chain |
| Handoff 02 CTO brief `Ready for validation` | Superseded in substance | `02-chief-of-staff-to-principal-engineer-validated-prompt.md` |
| Handoff 04 earlier `READY FOR QUALITY & RELEASE` | Explicitly superseded | Handoff 04 Revision 6 `EVIDENCE CORRECTION REQUIRED` |
| `CHANGELOG.md` v0.4 conversation heading | Contradictory current naming | Product Owner decision: Project Resume v0.4; conversation v0.5 |
| README v0.4 conversation status | Contradictory current naming | Same Product Owner decision |
| `VERSION_ROADMAP.md` v0.3/v0.5 identities | Stale roadmap | Approved v0.3/v0.3.1/v0.4/v0.5 sequence |
| ADR-0013 index revision “v0.4 conversation” | Historical identity not marked as such | Resequencing decision; retain history, mark current association v0.5 |
| Multiple handoff sequence-04 and sequence-05 files | Duplicate sequence namespace | No manifest currently identifies exact chronological order |

## 8. Handoff-system assessment

### Does the system clearly identify the latest effective revision?

**No.**

The engineering worktree's coordination page identifies the current stage and Handoff 06,
which is good. However:

- the primary start page is stale;
- the latest artifacts are absent from the primary handover directory;
- long handoffs append superseding reviews without updating top metadata;
- same-sequence filenames do not define one chronological order; and
- no handover manifest lists effective revision, candidate commit, disposition, and
  supersession.

### Can a new agent discover its current incoming artifact without conversation history?

**No, not reliably from the documented repository entry point.**

From the primary worktree, the agent will select Handoff 00 and the CTO role. Only an
agent that already knows to inspect `.worktrees/v0.3.1-engineering` will discover that the
effective receiver is the Principal Engineer and the effective incoming artifact is:

```text
docs/handovers/v0.3.1/06-chief-of-staff-to-principal-engineer-evidence-correction.md
```

At the audited engineering-tree state, the assignment is documentation/evidence-only:
retain complete paired benchmark JSON, bind it to exact execution identities and SHA-256,
recompute the stated arithmetic, append the evidence addendum, and make no executable
change. QA remains blocked until renewed CTO clearance.

## 9. Suggested changelog

These are suggestions only. They must not be added until the corresponding lifecycle
events are authorized and true.

### v0.3 — Query Engine

- Record v0.3 as the released Query Engine foundation rather than the original complete
  Read-only Chat and Provenance milestone.
- Record chat, conversation storage, and real provider adapters as explicitly deferred.
- Link ADR-0012, the implementation report, and the v0.3 ARB review.

### v0.3.1 — Query Trust Contracts

- Add only after Product Owner release approval and merge.
- Summarize the relevance terminology correction, explicit authorization scope,
  passage/revision citations, stable source identity, context-budget invariant, contract
  versioning, and trace hardening.
- Include final test, benchmark, unchanged-vault, architecture, and QA dispositions.
- Do not claim the performance gate is closed until the retained evidence correction and
  superseding QA disposition exist.

### Parked conversation candidate

- Preserve that conversation was initially implemented and reviewed under the name v0.4.
- Mark it `Parked / not released / to be reconciled as v0.5`.
- Link the `Not ready` QA review.
- Do not list it as the current v0.4 release.

### v0.4 — Project Resume

- Reserve the heading for the approved Project Resume scope.
- Link `docs/product/V0.4_PROJECT_RESUME_ACCEPTANCE_TESTS.md`.
- Add implementation claims only after v0.3.1 closes and v0.4 work is separately
  authorized.

## 10. Recommended reading order for new contributors

Until navigation is corrected, the following order best reflects governance precedence
and current program context:

1. `docs/coordination/README.md` from the explicitly designated authoritative worktree.
2. The exact `Current incoming handoff` named there.
3. `docs/GOVERNANCE.md`.
4. `docs/WAYS_OF_WORKING.md`.
5. `Operating Handbook - AI Agent Roles.md`, excluding its stale current-priority section.
6. The Product Owner decision linked by the incoming handoff.
7. Accepted ADRs linked by the incoming handoff.
8. Accepted requirements/PRDs and acceptance tests linked by the incoming handoff.
9. The relevant implementation or engineering report.
10. The latest effective CTO/architecture disposition.
11. The latest effective QA disposition.
12. `README.md`, `CHANGELOG.md`, and roadmaps for broader history, with the version-name
    drift in this report kept in mind.

For the audited v0.3.1 state, a contributor should use the engineering worktree's control
page and Handoff 06, not the primary worktree's Handoff 00 pointer.

## 11. Recommended corrections by timing

### Immediate coordination safety

1. Designate one authoritative coordination branch/worktree and publish its identity.
2. Make the top of the control page name exact incoming artifact, receiver, candidate
   commit, effective revision, and synchronization commit.
3. Add an effective-revision block to Handoffs 03–05.
4. Do not begin new implementation from the primary control page while it remains stale.

### v0.3.1 closeout

1. Complete the evidence-only correction and renewed CTO/QA cycle.
2. Record the Product Owner release decision.
3. Merge through the governed path.
4. Reconcile ADR index, changelog, README, roadmap, PRD targets, and coordination state
   against the actual merged release.
5. Publish a Librarian closeout that identifies the merge commit and freezes this
   pre-release report as historical.

### Before v0.4 Project Resume

1. Publish the accepted release-name crosswalk.
2. Make the Project Resume requirements authority explicit.
3. Remove volatile priorities from the Operating Handbook.
4. Mark the conversation candidate as parked/resequenced without deleting its history.
5. Repair the two engineering-tree cross-references or remove the out-of-scope report
   from that branch through an authorized documentation change.

## 12. Proposed documentation closeout checklist

Use this checklist after Product Owner approval and merge for every milestone.

### Release identity and authority

- [ ] Product Owner release decision exists at a stable repository path.
- [ ] Release name and version match the accepted roadmap decision.
- [ ] Merge commit and release commit/tag are recorded.
- [ ] Parked, deferred, renamed, or superseded scope is recorded without deleting history.
- [ ] Package version, documentation version, milestone version, and release version are
      distinguished where they differ.

### Coordination and handoffs

- [ ] `docs/coordination/README.md` names the authoritative branch/worktree and update commit.
- [ ] Current role, receiver, exact incoming artifact, candidate commit, and blocker are
      stated at the top.
- [ ] Every completed handoff has an exit statement.
- [ ] Every revised handoff states its latest effective revision and superseded revisions
      at the top.
- [ ] A handover manifest presents the chain in chronological order.
- [ ] No control-page link resolves to an obsolete artifact labeled as current.
- [ ] The next agent can start without conversation history.

### ADRs and PRDs

- [ ] ADR filenames, numbers, titles, and declared statuses match the ADR index.
- [ ] Accepted ADRs name their approval evidence and related release.
- [ ] Proposed ADRs implemented in practice are explicitly reviewed by the decision owner.
- [ ] Superseded ADRs link both directions and remain in history.
- [ ] PRD index shows status, current target, former target, dependencies, related ADRs,
      implementation status, and release status.
- [ ] Acceptance-test documents identify their governing accepted requirement.

### Navigation and cross-references

- [ ] Root README links to the coordination start page.
- [ ] Root README reading order reflects current authoritative documents.
- [ ] All local file links resolve in the exact merged tree.
- [ ] Heading fragments and external links are checked separately.
- [ ] Every major document is reachable from an index without search.
- [ ] Worktree-local documents do not depend on files present only in another worktree.

### Roadmap, changelog, and release notes

- [ ] Roadmap marks every milestone criterion complete, deferred, moved, or open.
- [ ] Milestone numbers and semantic versions have an explicit crosswalk.
- [ ] CHANGELOG distinguishes Unreleased, In review, Parked, Merged, and Released.
- [ ] Suggested changelog text is reconciled against the merged diff and review evidence.
- [ ] Release notes link the PRD/requirements, ADRs, implementation report, architecture
      disposition, QA disposition, Product Owner decision, and Librarian closeout.
- [ ] Deprecations and compatibility-removal targets are recorded.

### Historical integrity

- [ ] Stale documents are marked Historical or Superseded rather than deleted.
- [ ] Revision history records what changed, why, when, and what replaced it.
- [ ] No accepted ADR or decision is silently rewritten.
- [ ] The prior Librarian report remains available.
- [ ] Open findings are carried into the next report with status and owner.
- [ ] A new 0–100 repository health score is recorded using the fixed rubric.

## 13. Exit statement

**Audit complete; documentation correction required before the repository can be called
self-orienting.**

No recommendation in this report has been implemented. No code, existing documentation,
index, handoff, staging area, commit, branch, merge, push, or worktree state was altered by
the Librarian pass. The only created artifact is this report.
