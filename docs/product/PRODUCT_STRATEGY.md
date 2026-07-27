# Product Strategy

| Field | Value |
|---|---|
| Purpose | Define the decade-scale product mission, outcomes, boundaries, and measures |
| Status | Draft for approval |
| Version | 0.2.0 |
| Owner | Chief Product Officer |
| Revised | 2026-07-27 |
| Related | [Product Vision](../PRODUCT_VISION.md), [System Principles](../SYSTEM_PRINCIPLES.md), [Version Roadmap](VERSION_ROADMAP.md) |

## Mission

Help people turn fragmented digital activity into durable, trustworthy knowledge and safe, resumable action—without surrendering ownership to an application or AI provider.

## Vision

AI Operating System becomes a local-first coordination platform where a person can select any project, understand its state, enlist the best available AI and tools, approve consequential actions, and preserve useful outcomes in portable form. Components, models, interfaces, and storage providers remain replaceable.

The platform is not “one omniscient assistant.” It is a policy-enforced operating layer connecting:

- human-owned knowledge;
- provider-neutral reasoning;
- typed tools and agents;
- external systems that retain their own authority; and
- interfaces appropriate to the moment.

## Product thesis

Current AI products optimize isolated conversations. Users lose time rebuilding context, reconciling contradictory memories, locating external artifacts, and verifying actions. AI Operating System wins by making provenance, continuity, permissions, and interoperability the product—not invisible plumbing.

## Guiding principles

1. **Trust before autonomy.** Earn broader permissions through observable reliability.
2. **Knowledge before chat history.** Preserve decisions and outcomes, not indiscriminate transcripts.
3. **Context is a product surface.** Show what was selected, omitted, compressed, and why.
4. **One canonical owner per object.** Reference external assets; do not manufacture drifting masters.
5. **Progressive capability.** Read-only first, proposals second, approved writes third, bounded automation last.
6. **Provider and interface neutrality.** No model, database, UI, or plugin becomes irreplaceable.
7. **Determinism at boundaries.** Schemas, permissions, audit records, and context packages are testable.
8. **Local-first, not local-only.** Preserve useful offline capability while integrating valuable services.
9. **Humans resolve ambiguity.** AI may rank and explain; it must not conceal uncertainty.
10. **Operational simplicity is a feature.** A decade-scale product requires understandable failure and recovery.

## Target users

### Primary: multi-project knowledge workers

Individuals who alternate among software, business, creative, home, and personal work and use several AI providers. They value continuity, ownership, and a reliable “resume project” experience.

### Secondary: professionals with sensitive workflows

Accountants, consultants, researchers, creators, and small businesses that need traceability, scoped data access, reviewable outputs, and repeatable workflows.

### Future: teams and enterprises

Organizations that need governed agent execution across approved knowledge repositories and SaaS systems. Enterprise capability requires tenant isolation, identity federation, administrative policy, legal hold, data residency, and compliance evidence; these must not be improvised onto the personal edition.

## Core jobs to be done

- “When I return to work, tell me where I stopped and what matters now.”
- “Find what I already know across projects and systems without inventing connections.”
- “Let me use different AIs without rebuilding memory.”
- “Show why an answer is relevant and where every important claim came from.”
- “Perform repetitive work safely, with approvals proportional to risk.”
- “Leave my knowledge better organized after meaningful work.”

## Success metrics

| Outcome | Initial metric | Mature target |
|---|---|---|
| Resume speed | Median time to useful project context | Under 30 seconds |
| Context trust | Briefings with traceable source coverage | ≥95% material claims sourced |
| Retrieval quality | Precision@10 on personal benchmark queries | ≥0.85 |
| Knowledge durability | Meaningful sessions producing accepted durable outcomes | ≥80% |
| Safety | Consequential actions executed without required approval | Zero |
| Recovery | Successful tested restoration of canonical stores | 100% scheduled tests |
| Reliability | Successful bounded workflow completion | ≥99.5% excluding provider outages |
| Portability | Core knowledge usable without Jarvis | 100% canonical Markdown readable |
| Provider independence | Critical workflows supporting ≥2 providers or local fallback | 100% by v1.0 |
| User value | Weekly active use and self-reported time saved | ≥3 hours/week for primary user |

Metrics must be segmented by workspace and sensitivity. Engagement alone is not success; the system should reduce work, not create administration.

## Non-goals

- Replacing Obsidian, GitHub, calendars, email, or file systems as canonical owners.
- Building a general autonomous computer operator before permissions and audit are proven.
- Storing every interaction forever.
- Promising perfect memory, factual certainty, or fully automatic knowledge organization.
- Supporting arbitrary third-party code in the core process.
- Becoming a social network, advertising platform, or model-training data source.
- Enterprise multi-tenancy before the personal single-user architecture is explicitly separated from it.
- Premature visual spectacle, voice, or multi-agent choreography without validated utility.

## Strategic sequencing

1. Make read-only context trustworthy.
2. Deliver search and chat with visible provenance.
3. Add durable memory through proposals and approval.
4. Establish capability-based plugins and MCP policy.
5. Add bounded agents and workflow automation.
6. Expand to mobile and teams only after identity and synchronization contracts exist.

## Key assumptions to test

- Project dashboards remain the most useful primary navigation at larger scale.
- Markdown/YAML can remain canonical while indexes handle millions of notes.
- Users will review proposed memory changes if review is fast and explainable.
- A provider-neutral internal protocol can represent enough common capability without collapsing to the lowest common denominator.
- Local-first deployment remains maintainable for nontechnical users.

## Revision history

| Version | Date | Change |
|---|---|---|
| 0.2.0 | 2026-07-27 | Added measurable product strategy and explicit non-goals |
