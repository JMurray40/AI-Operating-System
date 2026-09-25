# AI Operating System — Ways of Working

| Field | Value |
|---|---|
| Purpose | Define **how** human and AI contributors collaborate on Jarvis |
| Status | **Accepted** |
| Version | 1.0 |
| Architecture Review Board (GPT) | **Approved** |
| Product Owner (Jason) | **Approved** |
| Ratified | 2026-07-27 |
| Related | [Governance](GOVERNANCE.md), [ADRs](adr/README.md), [Version Roadmap](product/VERSION_ROADMAP.md), [Developer Experience Strategy](DEVELOPER_EXPERIENCE_STRATEGY.md) |

> **[Governance](GOVERNANCE.md)** answers *who decides* — principles, roles, decision
> authority, and precedence. **This document** answers *how we collaborate* — mindsets,
> handoffs, lifecycle, reviews, and standards. Where the two touch, Governance is
> authoritative on authority; this document is authoritative on process.

---

## Role mindsets

The central risk in this model is that four of five roles are AI, and AIs tend to *agree*
with each other. Shared training and an agreeable default make consensus cheap and therefore
worthless. The countermeasure is to give each role a distinct **primary question** — a
mindset it holds no matter what the others conclude. A role that abandons its question to
agree with another has stopped adding value. (Role *authority* is defined in
[Governance](GOVERNANCE.md); this is about the *stance* each role takes.)

| Role | Primary question |
|---|---|
| Product Owner (Jason) | "Is this worth building?" |
| Chief Architect (GPT) | "Is this the right architecture?" |
| Principal Engineer (Claude) | "Can this be built well?" |
| Quality & Release (GPT, separate pass) | "What evidence says this should **not** ship?" |
| Historian / Librarian (GPT, separate pass) | "Does the recorded knowledge stay coherent and true?" |

Quality & Release is **not** trying to confirm success — its mandate is to find reasons to
reject the release. That adversarial stance is the entire source of the role's value; a QA
pass that sets out to bless the work is theater.

---

## Recommended workflow

```
Jason approves scope
        ↓
GPT defines requirements and architectural gates
        ↓
Claude implements and submits evidence
        ↓
GPT performs independent architecture and release review
        ↓
Jason accepts, requests changes, or stops the release
```

The independent review is conducted from implementation evidence and ends with one explicit
release disposition (see *Release disposition*). The **Engineering Lifecycle** below expands
this into per-stage handoff artifacts.

---

## Engineering Lifecycle

```
Idea
  ↓
PRD                         (Chief Architect)
  ↓
Architecture Review         (Chief Architect; Product Owner prioritizes)
  ↓
Implementation Brief        (Chief Architect → Principal Engineer)   [see Brief Contract]
  ↓
Engineering                 (Principal Engineer, on a branch)
  ↓
Engineering Review          (Principal Engineer authors)
  ↓
Architecture Review         (Chief Architect: does it fit the design?)
  ↓
QA Review                   (Quality & Release: independent verdict)  [see QA Review]
  ↓
Merge                       (gated by QA; Product Owner go/no-go)
  ↓
Librarian Pass              (Historian: changelog, roadmap, ADR index, cross-refs)
  ↓
Release                     (Product Owner)
```

Each arrow is a **handoff with a defined artifact**. No stage begins until the previous
stage's artifact exists and is accepted. Work is done on a branch and is never merged by the
role that wrote it.

---

## Implementation Brief Contract

The brief is the interface from Architect to Engineer — the single most important handoff in
this model. An underspecified brief forces the Engineer to make product decisions it should
not own (Governance Principle 3). Every brief **must** state:

- **Repository** — which repo.
- **Base branch** — the branch to build on.
- **Commit SHA** — the exact base commit, so "latest main" is never ambiguous.
- **Milestone** — which roadmap version this satisfies.
- **Related PRD(s)** — the requirement source(s).
- **Related ADR(s)** — the decisions that constrain the work.
- **Acceptance criteria** — concrete, checkable conditions for "correct."
- **Out-of-scope items** — what must *not* be built.
- **Definition of Done** — the shared DoD (below), plus any milestone-specific additions.
- **Performance targets** — measurable thresholds and the sizes to test at.
- **Testing expectations** — required scenarios and coverage.
- **Documentation expectations** — which docs must be created or updated.
- **Known risks** — hazards the Architect already sees.

If a brief is missing any of these, the Engineer requests them **before** starting rather
than filling the gap with assumptions.

---

## Architecture Escalation

When implementation uncovers any of the following, the Engineer **must stop and escalate to
the Chief Architect** instead of resolving it as a product or architecture decision
(Governance Principle 7):

- Roadmap conflicts (e.g., the brief and the roadmap describe different scope).
- Architectural inconsistencies between the brief and existing ADRs.
- Conflicting or ambiguous ADRs.
- Missing or contradictory documentation.
- Undefined behavior at a decision boundary.

The Engineer may proceed with clearly-scoped, non-contested work in parallel, but the
contested decision waits for the Architect (and, if needed, the Product Owner). The
escalation and its resolution are recorded so the reasoning is durable.

> Precedent: in v0.3 the brief ("Intelligent Query Engine") diverged from the roadmap
> ("Read-only Chat and Provenance"). It was handled by building the brief and recording the
> reconciliation in an ADR. Under this policy that divergence is escalated *before*
> implementation, and the Architect owns the reconciliation.

---

## Engineering Review (standard format)

The Engineer closes every milestone with an Engineering Review containing:

- **Implemented** — what shipped.
- **Deferred** — what was intentionally left out, and why.
- **Tradeoffs** — decisions made and what they cost.
- **Technical debt** — debt introduced, with location and rationale.
- **Benchmarks** — measured performance at the required sizes.
- **Performance** — scaling behavior and any regressions vs. the prior milestone.
- **Security** — read-only/permission posture and any new surface.
- **Future recommendations** — what to refactor before the next major release.
- **Lessons learned** — process or design insight worth carrying forward.

This format is fixed so reviews are comparable milestone to milestone and the architectural
history accumulates.

---

## QA Review

Quality & Release independently answers five questions, evaluating **evidence** rather than
regenerating it:

1. Did the implementation satisfy the brief's requirements and acceptance criteria?
2. Are the benchmarks sufficient, and are results within target?
3. Were any regressions introduced (functional, performance, or coverage)?
4. Does the architecture remain consistent with the ADRs and system principles?
5. Should this ship? — expressed as one of the explicit dispositions below.

QA's default posture is **skeptical**: a green test run is a claim to be sampled, not a proof
to be accepted. QA may re-run the suite, spot-check a benchmark, or read the diff, but it does
not rebuild the engineer's evidence from scratch. When one GPT serves as both Architect and
QA, the QA pass starts fresh from the implementation evidence and does **not** defer to its
own earlier architectural recommendations — "it matches what I proposed" is not a pass.

### Release disposition (required)

Every release review ends with exactly **one** disposition, stated explicitly:

| Disposition | Meaning |
|---|---|
| **Ready** | Meets acceptance criteria and Definition of Done; ship. |
| **Ready with conditions** | Ship, but named follow-ups must be tracked (list them). |
| **Refactor first** | Functionally acceptable, but technical debt must be paid down before merge. |
| **Not ready** | Requirements or quality bar not met; return to engineering with reasons. |
| **Re-scope** | The work revealed the scope itself is wrong; return to the Architect/Product Owner. |

The disposition is a recommendation to the Product Owner, who retains final go/no-go.

---

## Definition of Done

A milestone is Done only when **all** hold (unless the brief explicitly waives an item):

- All previous tests pass; new tests cover the brief's required scenarios.
- Lint and type checks are clean to the project's configured standard.
- Performance is measured at the required sizes and is within target.
- Read-only / no-write invariants are preserved and tested (per ADR-0007).
- Required documentation is created or updated.
- An Engineering Review is written in the standard format.
- Work is on a branch, in logical commits, **not merged and not pushed** by the Engineer.
- Any escalations are resolved and recorded.
- Documentation impacts (ADRs, changelog, roadmap, cross-references) are identified and
  handed to the Historian/Librarian pass; no known documentation inconsistency is left open.

---

## Architecture Fitness Review

Feature-by-feature review catches local problems but misses **gradual drift**. Every 3–4
releases (or when the Architect or Product Owner calls for one), the project runs an
**Architecture Fitness Review** — a health check of the system as a whole rather than of the
latest feature. It asks:

- Has module coupling increased?
- Are interfaces still clean?
- Are ADRs still being followed in practice?
- Has technical debt accumulated (and is it tracked)?
- Is the roadmap still aligned with the implementation?

**Owner:** Chief Architect, with evidence from the Principal Engineer (coupling/metrics,
debt log) and cross-checked by the Historian/Librarian (ADR adherence, doc alignment).
**Output:** a short findings report with a prioritized remediation list, fed back into the
roadmap. **Cadence:** every 3–4 versions; the first is due by v0.7.

---

## Lessons Learned

A living log of process improvements. Appended over time; entries are not rewritten.

| Date | Milestone | Lesson |
|---|---|---|
| 2026-07-27 | v0.3 | Briefs must pin base branch + SHA and confirm artifact access up front; an underspecified brief pushed product decisions onto the Engineer. |
| 2026-07-27 | v0.3 | Brief/roadmap scope divergence should be escalated to the Architect before implementation, not reconciled unilaterally by the Engineer. |
| 2026-07-27 | v0.3 | QA and Engineer roles overlap on evidence; separate "produce evidence" (Engineer) from "judge sufficiency" (QA) to avoid a rubber-stamp. |
| 2026-07-27 | Governance | With most roles being AI, consensus is cheap and near-worthless; assign each role a distinct primary question and make QA adversarial ("find reasons to reject"). |
| 2026-07-27 | Governance | Documentation coherence is a real job at scale; a dedicated Historian/Librarian role protects institutional memory as ADRs/PRDs/releases accumulate. |
| 2026-07-27 | Governance | Separate *who decides* (GOVERNANCE.md) from *how we collaborate* (this doc) so both stay coherent as the project grows. |

---

## Amendment

This document is governance-adjacent; changes follow the RFC amendment process defined in
[GOVERNANCE.md](GOVERNANCE.md) — proposed by any role, reviewed by the ARB, approved by the
Product Owner, with version history retained.

## Ratification Record

| Version | Date | ARB (GPT) | Product Owner | Change |
|---|---|---|---|---|
| 1.0 | 2026-07-27 | Approved | Approved | Initial ways-of-working: mindsets, lifecycle, brief contract, escalation, reviews, DoD, Architecture Fitness Review. |
