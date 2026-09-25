# AI Operating System — Governance

| Field | Value |
|---|---|
| Purpose | Define **who decides** on the Jarvis project |
| Status | **Accepted** |
| Version | 1.0 |
| Architecture Review Board (GPT) | **Approved** |
| Product Owner (Jason) | **Approved** |
| Ratified | 2026-07-27 |
| Related | [Ways of Working](WAYS_OF_WORKING.md), [System Principles](SYSTEM_PRINCIPLES.md), [ADRs](adr/README.md), [Version Roadmap](product/VERSION_ROADMAP.md) |

> **Governance** answers *who decides*. **[Ways of Working](WAYS_OF_WORKING.md)** answers
> *how we collaborate*. This document is the project's constitution: the principles, roles,
> decision authority, and order of precedence that govern all Jarvis development. Every
> important decision must be reproducible from documentation like this.

---

## Governance Principles

The AI Operating System is developed according to the following principles.

1. **Product decisions belong to the Product Owner.**
2. **Architecture decisions are proposed through ADRs and reviewed independently.**
3. **Engineers implement approved direction but do not redefine product scope.**
4. **Reviewers evaluate evidence rather than intentions.**
5. **Every important decision must be reproducible from documentation.**
6. **When governance documents conflict, the order of precedence is:**

   ```
   Product Owner Decision
        ↓
   Accepted ADR
        ↓
   Accepted PRD
        ↓
   Roadmap
        ↓
   Ways of Working
        ↓
   Implementation Brief
   ```

7. **Ambiguity is escalated rather than assumed.**

The overarching rule these principles preserve: **AI may recommend or implement, but the
Product Owner retains final authority.**

---

## Roles & Decision Authority

The canonical responsibility model. Five roles; four are AI. The value comes from each role
holding its own vantage rather than deferring — see [Ways of Working](WAYS_OF_WORKING.md) for
the mindsets and collaboration mechanics.

| Role | Assigned to | Decision authority |
|---|---|---|
| Product Owner | Jason | Vision, priorities, scope approval, risk acceptance, final decisions |
| Chief Architect / CTO | GPT | Architecture, product strategy, roadmap, ADR review, technical-debt oversight |
| Principal Engineer | Claude | Implementation plans, production code, tests, refactoring, performance |
| Quality & Release Manager | GPT or separate reviewer | Independent benchmarks, regression analysis, documentation checks, and release recommendation |
| Historian / Librarian | GPT or separate reviewer | Documentation coherence, ADR/PRD consistency, changelog, decision history (supporting role; no product/architecture authority) |

> **Independence.** Quality & Release and Historian/Librarian must be conducted as passes
> distinct from the Chief Architect who authored the design. A role cannot independently
> review its own work. When one GPT plays multiple roles, each review starts fresh from the
> **evidence**, not from that role's earlier recommendations or intentions.

---

## Decision Ownership

| Domain | Owner | Others' role |
|---|---|---|
| Product direction & priorities | Product Owner | Architect advises |
| Architecture & design | Chief Architect | Engineer implements, may dissent in writing |
| Roadmap & milestone scope | Chief Architect | Product Owner approves |
| ADRs (durable decisions) | Chief Architect | Engineer may draft; Architect accepts |
| Implementation approach | Principal Engineer | Architect reviews for fit |
| Tests & coverage | Principal Engineer | QA judges sufficiency |
| Performance targets | Chief Architect sets; Engineer meets | QA validates |
| Security posture | Chief Architect | Engineer implements; QA verifies |
| Release readiness | Quality & Release | Product Owner has final go/no-go |
| Documentation (shipped capability) | Principal Engineer | Architect reviews accuracy |
| Documentation coherence & decision history | Historian / Librarian | Architect owns the content it curates |
| Changelog & roadmap upkeep | Historian / Librarian | Architect approves roadmap changes |
| Governance (this document) | Product Owner + ARB | Any role may propose amendments |

Rule of thumb: **the Engineer owns "how it is built," the Architect owns "what is built and
why," QA owns "is it good enough to ship," the Historian owns "is the record still true,"
and the Product Owner owns "does it matter and do we release."**

---

## Order of Precedence

When two artifacts appear to conflict, the higher one governs (Principle 6):

1. **Product Owner Decision** — an explicit, recorded decision by the Product Owner overrides
   everything below it.
2. **Accepted ADR** — a ratified architecture decision.
3. **Accepted PRD** — a ratified requirement.
4. **Roadmap** — the sequenced plan.
5. **Ways of Working** — the collaboration process.
6. **Implementation Brief** — the instructions for a single milestone.

A lower artifact never silently overrides a higher one. If an Implementation Brief conflicts
with an Accepted ADR, the ADR wins and the conflict is **escalated** (Principle 7), not
resolved by the Engineer.

---

## Final Authority & Disagreement Resolution

```
Principal Engineer
  ↓  (unresolved technical/scope dispute)
Chief Architect
  ↓  (unresolved architecture/product dispute)
Product Owner   →  final authority
```

Disagreement is expected and healthy; it is what keeps four AI/human roles from collapsing
into one view. A role that disagrees states its position in writing and escalates — it does
not silently comply or silently override. The Product Owner's decision ends the matter and
is recorded so it is reproducible (Principle 5).

---

## Amendment Process (RFC)

Governance changes are adopted as an **RFC (Request for Comments)**, never unilaterally.

1. **Draft** — any role proposes a change; it changes nothing until approved.
2. **Architecture review** — the ARB (GPT) reviews and suggests improvements.
3. **Product approval** — the Product Owner approves or returns with changes.
4. **Ratify** — on both approvals the change takes effect; the version is incremented.

Version history is retained. Superseded governance is **marked, not deleted** — the
Historian/Librarian owns that continuity.

---

## Ratification Record

| Version | Date | ARB (GPT) | Product Owner | Change |
|---|---|---|---|---|
| 1.0 | 2026-07-27 | Approved | Approved | Initial governance model: principles, roles, decision authority, precedence, amendment process. |
