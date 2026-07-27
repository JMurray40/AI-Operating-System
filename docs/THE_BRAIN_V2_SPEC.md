# The BRAIN v2

## Master Specification for a Personal AI Knowledge System

**Status:** Draft for review  
**Version:** 0.1  
**Date:** 2026-07-26  
**System owner:** Jason  
**Primary knowledge platform:** Obsidian  
**Future orchestration layer:** Jarvis

---

## 1. Purpose

This document is the authoritative design specification for **The BRAIN v2**, a local-first personal knowledge system that can be used consistently by Jason, Claude, ChatGPT, Gemini, Ollama, coding assistants, and future Jarvis services.

The system combines:

- Jason's existing Obsidian organization, including Inbox, Projects, Areas, Resources, Templates, Archive, Sessions, Conversations, and System content.
- The AI Memory Vault operating pattern: `CLAUDE.md`, `VAULT-INDEX.md`, a pointer-only `MEMORY.md`, and Daily Notes.
- A broader knowledge architecture built around projects, areas, concepts, decisions, people, organizations, resources, and structured AI session summaries.
- External systems such as GitHub, local folders, cloud storage, calendars, email, and other software without copying all their content into Obsidian.
- A future Jarvis layer for search, context assembly, model routing, dashboards, relationship discovery, and controlled automation.

This is a living specification. Changes should be intentional, documented, and versioned. The system is expected to evolve, but its core principles should remain stable.

---

## 2. Vision

The BRAIN v2 is the durable, human-owned map of Jason's work and knowledge.

It should make it possible to:

1. Resume any project quickly.
2. find information regardless of which AI or application produced it.
3. preserve useful outcomes from AI sessions without filling the vault with raw transcripts.
4. connect overlapping ideas across projects and areas.
5. record important decisions and recognize when they are contradicted or superseded.
6. locate files and assets without duplicating them into the vault.
7. give any approved AI enough structured context to assist effectively.
8. remain useful if a model, application, integration, or database is replaced.

The desired long-term experience is:

> Open a project, understand its current state, retrieve the relevant knowledge and resources, begin work with an informed AI, and preserve the results back into the system.

---

## 3. Goals and Non-Goals

### 3.1 Goals

- Establish Obsidian as the primary home for durable knowledge.
- Provide one coherent structure across personal, business, and technical work.
- Make projects, areas, people, organizations, concepts, decisions, sessions, and resources first-class objects.
- Use consistent metadata that both humans and software can understand.
- Connect notes to repositories, folders, documents, websites, cloud locations, and applications.
- Capture structured summaries from all meaningful AI work.
- Support safe, reviewable AI-assisted maintenance.
- Enable progressively better keyword, metadata, link, semantic, and relationship search.
- Deliver daily value before the full Jarvis vision is complete.

### 3.2 Non-Goals

The BRAIN v2 is not intended to:

- Replace GitHub as the source of truth for source code and repository documentation.
- Replace file systems or cloud storage as the source of truth for binary and working files.
- Store passwords, API keys, tokens, or other secrets.
- Preserve every raw AI conversation as primary knowledge.
- Give an AI unrestricted authority to rename, move, merge, overwrite, or delete content.
- Turn Obsidian into an operational log database.
- Require a vector database, knowledge graph database, or Jarvis application to remain usable.
- Produce an elaborate folder hierarchy before real usage demonstrates a need.

---

## 4. System Boundaries

The architecture separates durable knowledge, external assets, operational state, and rebuildable indexes.

| Layer | Responsibility | Primary technology | Authority |
|---|---|---|---|
| Knowledge | Meaning, context, decisions, summaries, relationships, indexes | Obsidian Markdown vault | Durable source of truth |
| Assets | Code, documents, spreadsheets, media, datasets, published content | GitHub, local folders, cloud storage, business applications | Source system remains authoritative |
| Operational state | Conversations, jobs, usage, costs, approvals, execution logs, dashboard state | Future Jarvis database | Operational source of truth |
| Search index | Full-text, embeddings, extracted entities, similarity data | Rebuildable local index | Derived from authoritative sources |
| Orchestration | Context assembly, model routing, tools, workflows, permissions | Future Jarvis services | Replaceable application layer |
| Reasoning | Analysis and generation | Claude, OpenAI, Gemini, Ollama, and future models | Temporary processing layer |

### 4.1 Core architectural rule

> Obsidian stores knowledge. External systems store assets. Jarvis connects and operates across both.

An index may accelerate discovery, but it must be rebuildable. An LLM may interpret information, but it must not become the only place where durable knowledge exists.

---

## 5. Design Principles

### 5.1 The vault belongs to the human

No model or vendor owns the knowledge base. Markdown must remain directly readable and editable without Jarvis or an AI provider.

### 5.2 Knowledge has one authoritative home

Avoid multiple editable master copies. If a resource is authoritative elsewhere, the vault records context and a pointer rather than duplicating the artifact.

### 5.3 Reference assets; do not absorb them indiscriminately

Source code belongs in repositories. Spreadsheets, PDFs, images, and other working files remain in their appropriate storage systems. Obsidian explains what they are, why they matter, and where they live.

### 5.4 Every important object is linkable

Projects, areas, people, organizations, concepts, decisions, sessions, and significant resources should be represented by stable notes or links.

### 5.5 Projects and areas are different

- A **project** has an outcome, milestone, or completion condition.
- An **area** is an ongoing responsibility without a natural end date.

Projects may support one or more areas.

### 5.6 Links express meaning; folders support navigation

Folders provide a predictable home. Links and metadata represent relationships. A note should not be duplicated into several folders merely because it relates to several subjects.

### 5.7 AI sessions must increase the value of the vault

A meaningful session should leave behind a concise summary, decisions, open questions, next actions, and connections—not merely a transcript.

### 5.8 Humans approve structural or consequential changes

AI may analyze and propose. Moves, merges, mass renames, destructive edits, and deletions require explicit review and approval.

### 5.9 Preserve provenance and history

Important claims and summaries should link to their source. Superseded decisions remain available and point to the replacement.

### 5.10 Use controlled vocabularies

Prefer a small, documented set of note types, statuses, and topic names. AI should suggest an existing term before creating a synonym.

### 5.11 Start simple and earn complexity

Use Markdown, YAML, links, templates, and ordinary search first. Add embeddings, agents, databases, and automations only when usage demonstrates their value.

### 5.12 Security is part of the knowledge architecture

The vault must not contain secrets. Sensitive material must be labeled and exposed to external models only under an explicit policy.

---

## 6. Canonical Vault Structure

The target structure evolves Jason's current organization rather than replacing it wholesale.

```text
The BRAIN/
├── 00 Inbox/
├── 01 Dashboard/
│   ├── Home.md
│   ├── Today.md
│   ├── Active Priorities.md
│   └── Weekly Review.md
├── 02 Projects/
│   ├── Jarvis/
│   ├── Cloud Organizer Pro/
│   ├── Murray & Associates/
│   ├── Survivor Group Tracker/
│   ├── Adult Coloring Books/
│   └── Town.com Routines/
├── 03 Areas/
│   ├── Business/
│   ├── Career/
│   ├── Finance/
│   ├── Health/
│   ├── Home/
│   └── Learning/
├── 04 Knowledge/
│   ├── Concepts/
│   ├── Research/
│   ├── Reference/
│   ├── Standards/
│   ├── Playbooks/
│   ├── Books/
│   └── Prompts/
├── 05 People & Organizations/
│   ├── People/
│   └── Organizations/
├── 06 Resources/
│   ├── Repositories/
│   ├── Local Folders/
│   ├── Cloud Locations/
│   ├── Websites/
│   ├── Software/
│   └── Hardware/
├── 07 Decisions/
├── 08 Sessions/
│   ├── 2026/
│   └── Raw Transcripts/
├── 09 Templates/
├── 90 Archive/
└── 99 System/
    ├── About Me.md
    ├── VAULT-INDEX.md
    ├── AI Profiles/
    ├── Agent Configurations/
    ├── Schemas/
    ├── Controlled Vocabularies/
    ├── Dashboards/
    ├── Automation/
    ├── Prompt Library/
    ├── Change Logs/
    └── Indexes/
```

### 6.1 Folder rationale

| Folder | Purpose |
|---|---|
| `00 Inbox` | Frictionless capture awaiting classification and review |
| `01 Dashboard` | Human-facing navigation and review pages |
| `02 Projects` | Outcome-oriented work with project home notes |
| `03 Areas` | Ongoing responsibilities and standards of maintenance |
| `04 Knowledge` | Reusable knowledge independent of a single project |
| `05 People & Organizations` | Relationship context and entity notes |
| `06 Resources` | Curated pointers to important external assets and systems |
| `07 Decisions` | First-class decision records with lifecycle and provenance |
| `08 Sessions` | Structured summaries; raw transcripts only when justified |
| `09 Templates` | Canonical note templates |
| `90 Archive` | Inactive or replaced content retained for history |
| `99 System` | Rules, schemas, indexes, AI configuration, and vault operations |

### 6.2 Folder rules

- Do not reorganize the entire vault merely to match this tree.
- Create folders when content is ready to use them.
- Preserve existing paths until a migration batch is approved.
- Prefer links over duplication when one note belongs to several contexts.
- Avoid nesting beyond what materially helps navigation.

---

## 7. Metadata Standard

### 7.1 Common frontmatter

Every durable note should use the following common fields where applicable:

```yaml
---
id: note-20260726-001
type: concept
title: Semantic Search
status: active
created: 2026-07-26
updated: 2026-07-26
aliases: []
projects: []
areas: []
topics: []
people: []
organizations: []
related: []
sources: []
sensitivity: private
confidence: confirmed
---
```

### 7.2 Field rules

| Field | Rule |
|---|---|
| `id` | Stable and unique; never reused after deletion or archival |
| `type` | One value from the controlled note-type vocabulary |
| `title` | Human-readable canonical name |
| `status` | One approved lifecycle value |
| `created` | Original creation date in `YYYY-MM-DD` |
| `updated` | Date of last meaningful content change |
| `aliases` | Alternate names that improve discovery |
| `projects` | Wikilinks to related project home notes |
| `areas` | Wikilinks to ongoing areas |
| `topics` | Controlled topic terms or concept links |
| `people` | Wikilinks to person notes |
| `organizations` | Wikilinks to organization notes |
| `related` | Explicit semantic relationships not captured elsewhere |
| `sources` | URLs, note links, repository files, or external resource references |
| `sensitivity` | `public`, `internal`, `private`, or `restricted` |
| `confidence` | `unverified`, `inferred`, `supported`, or `confirmed` |

### 7.3 Controlled statuses

Use only statuses appropriate to the note type:

- `inbox`
- `draft`
- `active`
- `waiting`
- `blocked`
- `completed`
- `published`
- `superseded`
- `archived`

---

## 8. Note Types and Schemas

### 8.1 Project

A project represents outcome-oriented work.

```yaml
---
id: project-jarvis
type: project
title: Jarvis
status: active
created: 2026-07-26
updated: 2026-07-26
areas:
  - "[[Technology]]"
owner:
  - "[[Jason]]"
goal: Create a useful personal AI operating system.
current_milestone: Establish The BRAIN v2
priority: high
start_date: 2026-07-26
target_date:
projects: []
topics:
  - artificial-intelligence
  - knowledge-management
resources:
  - "[[Jarvis OS Repository]]"
related: []
sensitivity: private
---
```

### 8.2 Area

An area represents an ongoing responsibility.

```yaml
---
id: area-business
type: area
title: Business
status: active
created: 2026-07-26
updated: 2026-07-26
owner:
  - "[[Jason]]"
standard: Maintain reliable, documented business operations.
review_frequency: weekly
projects:
  - "[[Murray & Associates]]"
topics: []
related: []
sensitivity: private
---
```

### 8.3 Concept

A concept connects reusable knowledge across projects and areas.

```yaml
---
id: concept-semantic-search
type: concept
title: Semantic Search
status: active
created: 2026-07-26
updated: 2026-07-26
aliases:
  - meaning-based search
projects:
  - "[[Jarvis]]"
  - "[[Cloud Organizer Pro]]"
areas:
  - "[[Technology]]"
topics:
  - search
  - embeddings
related:
  - "[[Knowledge Retrieval]]"
sources: []
sensitivity: internal
confidence: supported
---
```

### 8.4 Research

```yaml
---
id: research-20260726-001
type: research
title: Comparing Local Embedding Models
status: draft
created: 2026-07-26
updated: 2026-07-26
question: Which local embedding model best fits the vault index?
projects:
  - "[[Jarvis]]"
topics:
  - embeddings
  - local-ai
sources: []
conclusions: []
confidence: unverified
sensitivity: internal
---
```

### 8.5 Person

```yaml
---
id: person-jason
type: person
title: Jason
status: active
created: 2026-07-26
updated: 2026-07-26
organizations: []
roles: []
projects: []
contact_reference:
related: []
sensitivity: private
---
```

Contact secrets or sensitive personal details should remain in an appropriate contact system; the note may point to that record.

### 8.6 Organization

```yaml
---
id: org-murray-associates
type: organization
title: Murray & Associates
status: active
created: 2026-07-26
updated: 2026-07-26
organization_type: business
people: []
projects:
  - "[[Murray & Associates Website]]"
resources: []
related: []
sensitivity: private
---
```

### 8.7 Resource

```yaml
---
id: resource-jarvis-repository
type: resource
title: Jarvis OS Repository
status: active
created: 2026-07-26
updated: 2026-07-26
resource_type: github_repository
uri: https://github.com/example/Jarvis-OS
local_path:
source_of_truth: external
access: private
projects:
  - "[[Jarvis]]"
related: []
sensitivity: private
---
```

### 8.8 Decision

```yaml
---
id: decision-20260726-001
type: decision
title: Use Obsidian as the Durable Knowledge Layer
status: accepted
created: 2026-07-26
updated: 2026-07-26
decision_date: 2026-07-26
decision_makers:
  - "[[Jason]]"
projects:
  - "[[Jarvis]]"
areas:
  - "[[Technology]]"
supersedes: []
superseded_by:
review_date:
sources: []
sensitivity: private
---
```

### 8.9 Session summary

```yaml
---
id: session-20260726-claude-001
type: session-summary
title: Jarvis — Vault Architecture Session
status: completed
created: 2026-07-26
updated: 2026-07-26
session_date: 2026-07-26
provider: Claude
model_role: architecture
projects:
  - "[[Jarvis]]"
objective: Define the master vault architecture.
repositories: []
files_changed: []
commits: []
decisions:
  - "[[Use Obsidian as the Durable Knowledge Layer]]"
related: []
transcript_reference:
sensitivity: private
---
```

### 8.10 Prompt

```yaml
---
id: prompt-vault-inventory
type: prompt
title: Read-Only Vault Inventory
status: active
created: 2026-07-26
updated: 2026-07-26
providers:
  - general
use_case: Inventory an Obsidian vault without changing it.
version: 1.0
projects:
  - "[[Jarvis]]"
related: []
sensitivity: internal
---
```

### 8.11 Daily note

```yaml
---
id: daily-2026-07-26
type: daily
title: 2026-07-26
status: active
created: 2026-07-26
updated: 2026-07-26
date: 2026-07-26
projects: []
areas: []
sessions: []
decisions: []
sensitivity: private
---
```

---

## 9. Project Dashboard Standard

Every active project should have one canonical home note. Supporting notes may live in the same project folder or in their appropriate first-class folders and link back to the project.

```markdown
---
id: project-example
type: project
title: Project Name
status: active
created: 2026-07-26
updated: 2026-07-26
areas: []
owner:
  - "[[Jason]]"
goal:
current_milestone:
priority: medium
resources: []
sensitivity: private
---

# Project Name

## Purpose

One concise explanation of the project's intended outcome and value.

## Current state

- **Status:** Active
- **Current milestone:** 
- **Last meaningful update:** 
- **Next review:** 

## Resume here

State exactly where work stopped, what is ready, and the best next action.

## Outcomes and success criteria

- [ ] Outcome or measurable success condition

## Current priorities

1. 
2. 
3. 

## Next actions

- [ ] 

## Open questions and blockers

- 

## Decisions

- [[Decision title]]

## Knowledge and research

- [[Relevant concept]]
- [[Research note]]

## People and organizations

- [[Person]]
- [[Organization]]

## Resources

| Resource | Type | Authority | Location |
|---|---|---|---|
| Repository | GitHub | Source of truth | [[Repository resource note]] |
| Working files | Local folder | Source of truth | [[Folder resource note]] |
| Published site | Website | Deployment | [[Website resource note]] |

## Recent sessions

- [[Session summary]]

## Recent changes

- Date — concise change and its source

## Related projects and areas

- [[Related project]]
- [[Supporting area]]

## Archive notes

What should be retained when the project becomes inactive.
```

The **Resume here** section is mandatory for every active project. It is the primary input for a future Jarvis “Resume Project” feature.

---

## 10. Resource Linking Strategy

### 10.1 Source-of-truth decision

Before importing content, answer:

1. Is this knowledge or an asset?
2. Where is its authoritative editable copy?
3. Does the vault need the full content, a summary, or only a pointer?

### 10.2 Default authority by asset class

| Information or asset | Default authoritative home | Vault representation |
|---|---|---|
| Knowledge, reasoning, and decisions | Obsidian | Full note |
| Project overview and current context | Obsidian | Project dashboard |
| Source code and repository documentation | GitHub repository | Resource note and contextual summary |
| Blog or website source managed in code | Publishing repository/CMS | Content index, metadata, strategy, and pointer |
| PDF, spreadsheet, image, video, or dataset | Local or cloud file system | Resource note or link |
| Calendar event | Calendar provider | Link/reference plus durable meeting outcome if valuable |
| Email | Email provider | Link/reference plus extracted decision or action if valuable |
| AI conversation | Provider/Jarvis database or archive | Structured session summary |
| API credentials and secrets | Secret store/environment | Never stored in vault |
| Search embeddings | Rebuildable index | Not copied into notes |
| Application logs and costs | Jarvis database | Summaries or dashboards only |

### 10.3 Resource identifiers

Prefer portable URIs where possible:

- `https://github.com/owner/repository`
- `https://...` for web and cloud resources
- repository-relative paths for files tracked in Git
- absolute local paths only when necessary
- stable application deep links when supported

Windows paths must be written as strings and checked when a drive or folder moves.

### 10.4 Resource note policy

Create a dedicated resource note when the resource:

- is reused by multiple projects;
- requires context beyond a simple URL;
- has access, authority, lifecycle, or ownership information;
- should appear in relationship search; or
- is important enough to recover or relocate later.

A single direct link inside a project note is sufficient for minor, project-specific resources.

---

## 11. AI Memory and Boot Architecture

### 11.1 Separation of responsibilities

| File | Purpose |
|---|---|
| `CLAUDE.md` or equivalent agent instruction file | Repository-specific behavior, safety, and development rules |
| `99 System/VAULT-INDEX.md` | Map of the vault, canonical notes, schemas, and retrieval order |
| `MEMORY.md` | Minimal pointer telling an AI where authoritative memory lives |
| Daily Notes | Chronological human and AI audit trail |
| Session summaries | Durable outcomes of meaningful AI work |

### 11.2 `MEMORY.md` must remain a pointer

`MEMORY.md` should not become a competing knowledge store. Its content should be comparable to:

```markdown
# Memory

The authoritative long-term knowledge base is the Obsidian vault.

Before meaningful work:

1. Read `99 System/VAULT-INDEX.md`.
2. Read the relevant project dashboard.
3. Read linked active decisions and recent session summaries.
4. Follow repository-specific instructions in `CLAUDE.md`.

Do not store secrets or durable project knowledge in this file.
```

### 11.3 `VAULT-INDEX.md` responsibilities

The index should contain:

- The purpose of the vault.
- Canonical folder map.
- Note-type and schema locations.
- Controlled vocabularies.
- Links to active projects and areas.
- Links to `About Me` and relevant organizations.
- Instructions for finding decisions, sessions, and resources.
- Current migration or system notices.
- AI startup and closeout checklists.

It should be concise enough to read at the beginning of a session and link to details rather than repeat them.

---

## 12. AI Session Lifecycle

### 12.1 Start

For meaningful work, the AI should:

1. Read its local instructions (`CLAUDE.md`, `AGENTS.md`, or equivalent).
2. Read `VAULT-INDEX.md`.
3. Identify the relevant project, area, or capture destination.
4. Read the project dashboard's **Resume here**, priorities, open questions, and recent sessions.
5. Read active decisions and only the knowledge required for the task.
6. Confirm the authoritative locations of any external assets.
7. State assumptions when the project association or authority is uncertain.

### 12.2 Work

During the session, the AI should:

- Keep durable facts separate from tentative ideas.
- Record sources for external claims.
- Recognize potential decisions instead of silently embedding them in prose.
- Note contradictions with active decisions.
- Track changed files, commits, issues, and resources when relevant.
- Avoid unrelated vault cleanup.
- Never expose restricted content to a cloud model without approval.

### 12.3 Close

At the end of a meaningful session, the AI should prepare:

- Objective.
- Work completed.
- Decisions made or proposed.
- Files and resources changed.
- Problems encountered and resolutions.
- Open questions.
- Next actions.
- Related notes and possible cross-project connections.
- A proposed update to the project's **Resume here** section.

### 12.4 Save

The default durable artifact is a session summary in `08 Sessions/YYYY/`.

The AI may also propose:

- A new decision record.
- An update to an existing project dashboard.
- A new concept or research note.
- An inbox item when classification is uncertain.

Edits outside an approved workflow must be presented for review.

### 12.5 Raw transcript policy

Raw transcripts are optional evidence, not primary knowledge. Retain them only when:

- exact wording matters;
- a provider does not retain the session;
- the session contains reusable prompts or detailed research provenance; or
- legal, business, or audit requirements justify retention.

When retained, store or link the transcript separately and point to it from the summary.

---

## 13. Decision Records

Decisions are first-class because they preserve rationale and enable conflict detection.

### 13.1 Decision template

```markdown
---
id: decision-YYYYMMDD-NNN
type: decision
title:
status: proposed
created: YYYY-MM-DD
updated: YYYY-MM-DD
decision_date:
decision_makers:
  - "[[Jason]]"
projects: []
areas: []
supersedes: []
superseded_by:
review_date:
sources: []
sensitivity: private
---

# Decision title

## Context

What problem, constraint, or opportunity required a decision?

## Decision

What was decided?

## Rationale

Why was this option selected?

## Alternatives considered

### Alternative

- Benefits:
- Costs:
- Reason not selected:

## Consequences

### Positive

- 

### Negative or risky

- 

## Affected projects and systems

- [[Project]]

## Follow-up

- [ ] 

## Evidence and sources

- 
```

### 13.2 Decision lifecycle

```text
Proposed → Accepted → Implemented
                 ↘ Superseded → Archived
Proposed → Rejected
Accepted → Revisit
```

If a newer choice replaces an older decision:

- retain the old record;
- set its status to `superseded`;
- populate `superseded_by`;
- have the new decision populate `supersedes`; and
- update affected project dashboards.

---

## 14. Daily Notes Workflow

Daily Notes provide a lightweight chronological record. They do not replace project dashboards or session summaries.

### 14.1 Daily note template

```markdown
---
id: daily-YYYY-MM-DD
type: daily
title: YYYY-MM-DD
status: active
created: YYYY-MM-DD
updated: YYYY-MM-DD
projects: []
areas: []
sessions: []
decisions: []
sensitivity: private
---

# YYYY-MM-DD

## Focus

- 

## Schedule

- 

## Work completed

- 

## Still in progress

- 

## Decisions

- [[Decision]]

## AI sessions

- [[Session summary]]

## Files, commits, and external activity

- 

## Ideas and observations

- 

## Interesting connections

- 

## Questions remaining

- 

## Profile or system updates to review

- 

## Tomorrow / next

- [ ] 
```

### 14.2 Morning flow

1. Review the prior Daily Note.
2. Review calendar commitments.
3. Select up to three primary outcomes.
4. Link the projects and areas expected to receive attention.
5. Pull the **Resume here** section for the selected project.

### 14.3 During the day

- Capture quickly; do not interrupt work to classify every item.
- Link completed AI session summaries.
- Record potentially durable decisions as candidates.
- Use `00 Inbox` for information requiring later thought.

### 14.4 Closeout

1. Summarize meaningful progress.
2. Link completed session summaries and decisions.
3. Update the affected project dashboard.
4. Move unresolved tasks to the correct project or next Daily Note.
5. Record any useful cross-project connection.

### 14.5 Weekly review

The Weekly Review should surface:

- Active projects with no recent update.
- Inbox items awaiting classification.
- Proposed decisions awaiting approval.
- Blocked work.
- Sessions not connected to a project or area.
- Broken resource pointers.
- Candidate duplicates or contradictions.
- New connections worth exploring.

---

## 15. External System Integration

### 15.1 General integration contract

Every connector should define:

- authoritative source;
- stable external identifier;
- supported read and write actions;
- permission level;
- synchronization direction;
- conflict behavior;
- provenance captured in the vault;
- sensitivity rules; and
- failure and recovery behavior.

### 15.2 Permission levels

| Level | Meaning |
|---|---|
| `READ_ONLY` | May inspect only approved data |
| `PRE_APPROVED` | May perform explicitly scoped, low-risk actions |
| `CONFIRM_HIGH_RISK` | May perform routine actions but must confirm consequential ones |
| `CONFIRM_EACH_TIME` | Must receive approval before every change |
| `DISABLED` | Integration or action is unavailable |

### 15.3 GitHub

**Authority:** Repositories remain authoritative for code, issues, pull requests, releases, and repository documentation.

The vault should store:

- repository resource notes;
- project-to-repository relationships;
- durable architecture knowledge;
- decision records;
- summarized development sessions;
- links to important issues, pull requests, commits, and files.

Do not copy routine `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `AGENTS.md`, or `CLAUDE.md` files into the vault. Summarize only knowledge that must be reused outside the repository.

### 15.4 Local folders

Local folder access must be limited to explicitly approved roots.

The vault may record:

- path;
- purpose;
- owner project;
- source-of-truth status;
- backup location;
- important file patterns; and
- last verified date.

Jarvis should detect missing or relocated paths and ask for correction rather than silently rewriting references.

### 15.5 Cloud storage

Google Drive, OneDrive, Dropbox, SharePoint, Box, and similar systems remain authoritative for files stored there.

Use stable share links or provider identifiers when possible. Record:

- provider;
- external ID or URI;
- display path;
- owner project;
- access scope;
- synchronization status; and
- last verified date.

### 15.6 Calendars

Calendars remain authoritative for events.

The vault should receive only durable outcomes:

- meeting preparation;
- meeting note;
- decisions;
- action items;
- people and organization links; and
- project relationships.

Routine event copies should not become permanent notes.

### 15.7 Email and messaging

Email and messaging platforms remain authoritative for messages. The vault should contain a summary or extracted knowledge only when a message creates durable value, a decision, a commitment, or project context.

Sending, deleting, moving, or labeling messages must follow explicit permission rules.

### 15.8 AI providers and coding tools

Every provider is a replaceable reasoning engine. Each meaningful session should identify:

- provider;
- model role or alias;
- associated project;
- objective;
- outcome;
- decisions;
- artifacts;
- sources; and
- next actions.

Provider-specific memory must point back to the vault rather than compete with it.

---

## 16. AI Behavior Standard

All approved AI clients should follow these rules.

### 16.1 Before work

- Read the relevant system and project instructions.
- Retrieve only the context necessary for the task.
- Search for existing concepts, projects, and decisions before creating new terminology.
- Determine the authoritative home before copying content.
- Respect sensitivity labels and model-access restrictions.

### 16.2 While working

- Distinguish facts, inferences, ideas, and decisions.
- Preserve citations and provenance.
- Prefer links to external artifacts over duplicate content.
- Use existing controlled vocabulary.
- Surface contradictions and duplicate concepts.
- Avoid changing unrelated notes.
- Never store secrets.

### 16.3 When writing

- Use templates and valid YAML.
- Preserve stable IDs.
- Update `updated` only after a meaningful change.
- Add links that express real relationships; do not create links merely to increase graph density.
- Write concise, durable summaries rather than conversational filler.
- Put uncertain captures in `00 Inbox`.

### 16.4 Approval requirements

An AI must request explicit approval before:

- moving or renaming notes;
- merging notes;
- rewriting existing durable knowledge;
- changing metadata across multiple files;
- modifying an accepted decision;
- deleting or archiving content;
- editing external systems;
- exposing private or restricted material to a cloud service; or
- performing a bulk migration.

Read-only inventory, search, link validation, and preparation of advisory reports are allowed within approved roots.

### 16.5 Prohibited behavior

An AI must not:

- silently reorganize the vault;
- create a second memory system;
- invent source links, people, organizations, or decisions;
- replace history to make the current state look cleaner;
- treat semantic similarity as proof of duplication;
- delete a supposed duplicate without human verification; or
- perform unrestricted file-system or shell actions.

---

## 17. Knowledge Relationship and Overlap Model

Relationship discovery should be layered:

1. **Exact matches:** IDs, titles, aliases, external identifiers, and checksums.
2. **Lexical matches:** shared keywords, names, and headings.
3. **Metadata relationships:** projects, areas, topics, people, organizations, and resources.
4. **Graph relationships:** wikilinks, backlinks, decisions, sources, and shared dependencies.
5. **Semantic similarity:** meaning-based comparison of notes or sections.
6. **Entity extraction:** consistent recognition of projects, products, people, companies, software, and systems.
7. **Contradiction analysis:** conflicts between current work and accepted decisions or established facts.

Similarity scores are advisory. A human determines whether notes are duplicates, related, contradictory, or independent.

The future system should be able to produce findings such as:

```text
Possible cross-project connection

Concept: Document naming standards
Projects: Cloud Organizer Pro; Murray & Associates
Evidence: Two linked notes and one shared decision
Confidence: Supported
Suggested action: Compare the standards and identify reusable rules
```

---

## 18. Migration Strategy

Migration must be incremental, reversible, and evidence-based.

### 18.1 Current-state assumptions

The current vault already contains useful beginnings, including:

- Inbox;
- Projects such as Adult Coloring Books, Cloud Organizer Pro, Murray & Associates, Survivor Group Tracker, and Town.com Routines;
- Areas;
- Wiki/Resources;
- Templates;
- Archive;
- Conversations and Sessions; and
- System content.

These structures should be mapped into the target model rather than discarded.

### 18.2 Migration phases

#### Phase A — Back up and freeze

1. Create a verified backup of the entire vault, including `.obsidian`.
2. Record the backup location and date.
3. Suspend bulk structural edits during analysis.
4. Calculate an inventory baseline.

#### Phase B — Read-only inventory

Generate:

- folder and note counts;
- property and tag usage;
- broken links and orphan notes;
- duplicate and similar titles;
- notes without metadata;
- unusually large notes;
- current plugins;
- existing project candidates;
- external Markdown inventory; and
- advisory migration candidates.

No content changes occur in this phase.

#### Phase C — Install the standard

Create:

- `99 System/VAULT-INDEX.md`;
- schemas and controlled vocabularies;
- canonical templates;
- `About Me`;
- relevant organization notes;
- project dashboard template;
- decision template;
- session summary template; and
- Daily Note template.

#### Phase D — Pilot migration

Use two active projects as pilots. Recommended candidates:

- Jarvis; and
- one existing project with active files and repository history.

For each pilot:

1. Create the canonical project dashboard.
2. Link existing notes without moving them initially.
3. Add verified resource pointers.
4. normalize a small set of high-value metadata.
5. create or link active decisions.
6. test the session closeout workflow.
7. review usability for at least one week.

#### Phase E — Migrate high-value knowledge

Initial candidates include:

- `About Me` and company context that fill known gaps;
- the Tech Stack Tracker as reusable reference knowledge;
- active project dashboards;
- reusable prompts;
- durable decisions; and
- research or playbooks whose authoritative home is the vault.

#### Phase F — Link external assets

Create resource notes or project links for:

- code repositories;
- local working folders;
- cloud locations;
- websites;
- published assets;
- calendars; and
- other business systems.

Do not import repository documentation or publish targets simply to make the vault appear complete.

#### Phase G — Controlled consolidation

For each proposed move, rename, merge, archive, or deletion:

1. present source and destination;
2. explain the reason;
3. identify links that will change;
4. preserve provenance;
5. create a recoverable backup or version;
6. obtain explicit approval; and
7. write to the migration change log.

### 18.3 Special handling of existing categories

| Current category | Target treatment |
|---|---|
| Projects | Keep; add canonical dashboard notes and metadata |
| Areas | Keep as first-class ongoing responsibilities |
| Wiki/Resources | Gradually separate reusable knowledge from external resource pointers |
| Conversations | Convert valuable outcomes into session summaries; archive raw evidence selectively |
| Sessions | Normalize into structured, provider-independent summaries |
| Templates | Keep; replace duplicates with canonical templates |
| Archive | Keep; consolidate only after active content is stable |
| System | Expand into schemas, indexes, AI profiles, automation, and change logs |

### 18.4 Deduplication policy

A duplicate candidate is not a duplicate until reviewed.

For every candidate set:

- identify the authoritative copy;
- compare content and modification history;
- decide whether to merge, link, archive, or retain separately;
- update inbound links;
- preserve unique content and provenance; and
- delete only with explicit approval and a recoverable backup.

---

## 19. Implementation Roadmap

The roadmap prioritizes daily utility over platform completeness.

### Milestone 0 — Specification and safety

**Outcome:** A stable standard and recoverable starting point.

- Approve this specification.
- Back up the vault.
- Confirm controlled vocabularies.
- Create canonical templates.
- Establish the migration log.

### Milestone 1 — Usable knowledge foundation

**Outcome:** Jason can resume active projects and use Daily Notes immediately.

- Create `VAULT-INDEX.md`.
- Create `About Me` and organization context.
- Create dashboards for two pilot projects.
- Add verified repository and folder links.
- Establish Daily Notes.
- Use the **Resume here** workflow.

### Milestone 2 — Cross-AI session capture

**Outcome:** Meaningful Claude, ChatGPT, Gemini, Ollama, and coding sessions produce consistent durable summaries.

- Install provider-independent session template.
- Add startup and closeout instructions to active repositories.
- Keep `MEMORY.md` pointer-only.
- Record decisions separately.
- Link sessions to projects and Daily Notes.

### Milestone 3 — Read-only intelligence

**Outcome:** Search and relationship discovery add value without modifying the vault.

- Parse Markdown, YAML, tags, headings, and links.
- Build full-text search.
- Show broken links, orphans, and metadata gaps.
- Surface project context and related notes.
- Generate advisory overlap reports.

### Milestone 4 — Controlled capture and maintenance

**Outcome:** The system can create safe, reviewable knowledge artifacts.

- Create inbox notes.
- Draft session summaries and decisions.
- Suggest links and metadata.
- Add approval screens for edits.
- Maintain an audit trail and backups.

### Milestone 5 — Jarvis Daily Brain

**Outcome:** A simple interface saves time every day.

- Chat and search.
- Daily brief.
- Active projects.
- “Resume Project.”
- Recent sessions and decisions.
- Inbox and attention items.
- GitHub and local resource status.

### Milestone 6 — Relationship engine

**Outcome:** The system discovers useful overlap across work.

- Add semantic indexing.
- Extract entities.
- Detect duplicate concepts.
- identify possible contradictions.
- Surface cross-project connections.
- Keep all findings advisory.

### Milestone 7 — Model router and workflows

**Outcome:** Jarvis can select interchangeable reasoning engines and run controlled workflows.

- Use role aliases such as `coding`, `research`, `fast`, `private`, and `vision`.
- Add Claude, OpenAI, Gemini, and Ollama adapters.
- Track latency, cost, and provenance.
- Add human-approved workflows.
- Add recurring tasks only when real usage justifies them.

### Milestone 8 — Expanded interfaces

**Outcome:** Existing knowledge and workflows become available through additional interfaces.

- Desktop packaging.
- Mobile access.
- Optional Obsidian companion plugin.
- Notifications.
- Voice and push-to-talk.
- Home Assistant integration.

---

## 20. Future Jarvis Integration

Jarvis is the interface, librarian, context builder, analyst, and operator around The BRAIN v2. It does not replace the vault.

### 20.1 Target components

```text
Chat / Dashboard / Voice / Obsidian / Coding Tools
                         |
                         v
                 Jarvis Orchestrator
       +-----------------+------------------+
       |                 |                  |
       v                 v                  v
 Context Builder     Model Router      Tool Registry
       |                 |                  |
       +-----------------+------------------+
                         |
          +--------------+---------------+
          |                              |
          v                              v
  Obsidian Knowledge             External Systems
          |                    GitHub / Files / Cloud
          v                    Calendar / Email / Apps
  Rebuildable Index
```

### 20.2 Context Builder

Before sending a request to a model, Jarvis should assemble the smallest useful context package:

- user preferences and relevant profile information;
- project dashboard and **Resume here**;
- active decisions;
- recent session summaries;
- related concepts and research;
- open actions and blockers;
- relevant repository state;
- relevant external resources; and
- provenance and sensitivity rules.

The context package should record why each item was included.

### 20.3 “Resume Project” contract

For a selected project, Jarvis should present:

- current goal and milestone;
- where work stopped;
- recent sessions;
- recent commits or repository activity;
- active decisions;
- open actions and blockers;
- related resources;
- potentially relevant cross-project knowledge; and
- a safe option to start an AI session with this context.

### 20.4 Dashboard data

Initial widgets should be data-driven and focus on utility:

- Today.
- Active projects.
- Resume Project.
- Inbox requiring review.
- Recent sessions.
- Decisions awaiting review.
- Missing or broken resource links.
- Calendar summary.
- Model/service availability.
- Usage and cost.
- Interesting connections.

### 20.5 Write behavior

Jarvis should use an approval-first write pipeline:

```text
Capture
  → Classify
  → Search for existing knowledge
  → Detect duplicates and conflicts
  → Propose destination and links
  → Human review
  → Atomic write
  → Validate
  → Audit log
```

### 20.6 Replaceability

Jarvis must:

- use provider-independent model roles;
- treat integrations as adapters;
- keep core knowledge in portable Markdown;
- store operational data separately;
- keep indexes rebuildable; and
- remain functional in a reduced mode if a provider or integration is unavailable.

---

## 21. Governance and Change Control

### 21.1 Authority

Jason is the final authority for:

- structural changes;
- note-type and schema changes;
- controlled vocabulary;
- sensitivity policy;
- migrations;
- deletions; and
- external write permissions.

### 21.2 Specification changes

Material changes to this specification should:

1. state the problem;
2. identify affected notes, tools, and workflows;
3. explain alternatives;
4. define a migration path;
5. be recorded as a decision; and
6. update templates and validation rules together.

### 21.3 Review cadence

- Review implementation details after each pilot milestone.
- Review controlled vocabularies monthly during early adoption.
- Review the architecture quarterly.
- Avoid changing the folder system based on a single inconvenient note.

---

## 22. Quality and Acceptance Criteria

The BRAIN v2 foundation is successful when:

- Jason can identify the authoritative home of important knowledge and assets.
- Two active projects have usable dashboards with a current **Resume here** section.
- Daily Notes and session summaries are used consistently for at least two weeks.
- Multiple AI providers can produce the same session-summary structure.
- `MEMORY.md` points to the vault rather than duplicating it.
- Important decisions are independently discoverable and linked to affected projects.
- GitHub, local folders, and cloud resources can be located from project notes.
- No secrets are present in templates or migrated notes.
- Proposed structural edits are reviewable and logged.
- The vault remains fully usable without Jarvis, a vector index, or a specific LLM.

The first Jarvis release is successful when it can answer:

- “Where did I leave off?”
- “What should I work on next?”
- “What decisions govern this project?”
- “Where are the associated files and repositories?”
- “What related work have I done elsewhere?”
- “What did my recent AI sessions produce?”

---

## 23. Immediate Next Actions

1. Review and approve or amend this specification.
2. Back up the current vault and record the backup.
3. Confirm the actual current folder inventory and map it to Section 6.
4. Define the initial controlled vocabulary for note types, statuses, topics, and sensitivity.
5. Create `VAULT-INDEX.md` and the canonical templates.
6. Select two pilot projects.
7. Create their project dashboards and verified resource links.
8. Begin the Daily Note and session-summary workflow.
9. Run for one week before approving large-scale moves or renames.
10. Use observed friction to shape the first read-only Jarvis features.

---

## Appendix A — Initial Controlled Note Types

| Type | Purpose |
|---|---|
| `project` | Outcome-oriented work |
| `area` | Ongoing responsibility |
| `concept` | Reusable idea or subject |
| `research` | Question-driven investigation |
| `reference` | Stable factual or procedural knowledge |
| `playbook` | Repeatable operational method |
| `person` | Human relationship context |
| `organization` | Company, group, vendor, or institution |
| `resource` | Curated pointer to an external asset or system |
| `decision` | Choice, rationale, alternatives, and consequences |
| `session-summary` | Durable outcome of an AI or work session |
| `prompt` | Reusable prompt with provider and use-case metadata |
| `daily` | Chronological daily activity and review note |
| `meeting` | Preparation, notes, decisions, and actions for a meeting |

---

## Appendix B — Recommended Project Instruction Block

The following block may be adapted into each repository's `CLAUDE.md` or equivalent:

```markdown
## Knowledge System

The Obsidian vault is the authoritative long-term knowledge base.

Before meaningful work:

1. Read the vault's `VAULT-INDEX.md`.
2. Read the relevant project dashboard.
3. Read active decisions and recent session summaries.
4. Confirm the authoritative location of assets before editing them.

After meaningful work:

1. Prepare a structured session summary.
2. Record proposed or accepted decisions separately.
3. Update unresolved issues and next actions.
4. Suggest an update to the project's `Resume here` section.
5. Link relevant files, commits, issues, resources, and knowledge notes.
6. Surface possible duplicates, contradictions, and cross-project connections.

Safety:

- Never store passwords, API keys, or tokens in the vault.
- Do not move, rename, merge, overwrite, archive, or delete vault content without explicit approval.
- Do not copy repository documentation into the vault when a link and summary are sufficient.
- Preserve provenance and meaningful history.
```

---

## Appendix C — Migration Change Log Template

```markdown
# Migration Change — YYYY-MM-DD

## Approved by

Jason

## Scope

Exact notes, folders, or resources included.

## Backup

Location and verification date.

## Operations

| Action | Source | Destination | Reason | Result |
|---|---|---|---|---|
| Move | | | | |

## Link updates

- 

## Validation

- [ ] All intended files exist.
- [ ] YAML parses correctly.
- [ ] Inbound and outbound links resolve.
- [ ] Unique content and provenance were preserved.
- [ ] External resource pointers still open.
- [ ] No unrelated files changed.

## Recovery

Steps to reverse the migration.
```

---

## Appendix D — Open Questions for Review

These choices should be resolved during the pilot rather than assumed:

1. Should Daily Notes live in `01 Dashboard`, a dedicated `01 Daily`, or an existing Daily Notes location?
2. Should reusable prompts remain under `04 Knowledge/Prompts`, `99 System/Prompt Library`, or be split between knowledge and system prompts?
3. Which current “Wiki (Resources)” notes are true knowledge, and which are merely external resource pointers?
4. Which external system is authoritative for Murray & Associates blog content?
5. Which two projects should be used for the first migration pilot?
6. Which sensitivity classes may be sent to cloud models?
7. What stable vault path will all local AI clients use?
8. Which calendar, cloud storage, and messaging integrations should be introduced first?

Resolving these questions should not delay Daily Notes, session summaries, project dashboards, or the read-only inventory workflow.
