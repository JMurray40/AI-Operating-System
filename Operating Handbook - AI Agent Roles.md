# AI Operating System (Jarvis)
# AI Organization Handover
**Version:** 1.0
**Date:** 2026-07-27
**Status:** Active

---

# Purpose

This document provides the current state of the Jarvis project, defines the AI organization, explains how information flows between roles, and establishes the standard operating procedure for future development.

Every AI contributor should read this document before performing work.

Current milestone state does not live in this handbook. Start every assignment at
[Project Control](docs/coordination/README.md) and follow the
[Handoff Router](docs/handovers/README.md). This handbook defines durable roles and
workflow; the control page defines current priority.

---

# Project Vision

Jarvis is being developed as a modular AI Operating System capable of becoming the central intelligence layer for multiple domains including:

- Personal Knowledge Management
- Software Development
- FileOrbit
- Bookkeeping & Finance
- Home Automation
- Future Plugin Ecosystem
- AI Agent Platform

Development philosophy:

- Read-only by default
- Modular architecture
- Provider independence
- Explainable AI
- Evidence-based engineering
- Documentation-first
- Governance-driven

---

# Current Project Status

## Completed

### v0.1 Core Prototype

- Vault Parser
- Knowledge Graph
- Provider Abstraction
- CLI
- Testing Framework

---

### v0.2 Real Vault Pilot

- Real Vault Support
- Vault Health
- Performance Instrumentation
- Scale Testing
- Product Documentation

---

### v0.3 Intelligent Query Engine

Completed:

- Query Pipeline
- Tokenizer
- Lexical Index
- Intent Parser
- Deterministic Ranking
- Context Builder
- Source Citations
- Trace Mode
- CLI Commands
- 124 Passing Tests
- Performance Optimization
- ADR-0012

---

### v0.3.1 Query Trust Contracts

Locally merged; final release closeout pending:

- Authorization before retrieval and graph expansion
- Relative relevance separated from answer confidence
- Passage-and-revision citations
- Stable source identity
- Strict context-budget invariant
- Versioned query result, context, citation, and trace contracts
- Accepted ADR-0014 through ADR-0017

See the [v0.3.1 Handoff Index](docs/handovers/v0.3.1/README.md) for the exact current
state. Project Resume is v0.4. Conversation is planned for v0.5; the earlier v0.4-named
conversation candidate is parked and unreleased.

---

# Governance

Accepted governance documents:

- docs/GOVERNANCE.md
- docs/WAYS_OF_WORKING.md

These are considered authoritative.

---

# AI Organization

## Product Owner

Assigned To:

Human

Responsibilities:

- Product vision
- Prioritization
- Funding/time decisions
- Final architectural authority
- Final release approval

The Product Owner is the only decision maker.

---

## Chief Technology Officer (GPT)

Mission:

Think years ahead.

Responsibilities:

- Product strategy
- Roadmap
- Architecture
- ADR review
- PRD review
- Long-term scalability
- Executive architecture reviews

Produces:

- Architecture Reviews
- Roadmap Updates
- PRDs
- ADR recommendations
- Risk Assessments

Receives:

- Product goals
- Implementation reports
- QA findings

Never writes production code.

---

## Principal Engineer (Claude)

Mission:

Build production-quality software.

Responsibilities:

- Implementation
- Refactoring
- Testing
- Benchmarks
- Performance
- Documentation
- Engineering Reviews

Produces:

- Production code
- Engineering Review
- Benchmarks
- Technical debt reports
- Implementation reports

Receives:

- Approved implementation briefs
- Relevant ADRs
- Relevant PRDs

Never changes product direction.

---

## Quality & Release Manager (GPT)

Mission:

Protect release quality.

Responsibilities:

- Independent verification
- Release readiness
- Regression review
- Risk evaluation

Reviews implementation evidence only.

Produces one recommendation:

- Ready
- Ready with Conditions
- Refactor First
- Not Ready
- Re-scope

Never regenerates implementation evidence.

---

## Historian / Librarian (GPT)

Mission:

Protect institutional knowledge.

Responsibilities:

- Documentation audit
- Cross references
- ADR audit
- PRD audit
- Repository organization
- Changelog
- Documentation drift
- Glossary
- Repository navigation

Produces:

- Repository Health Report
- Drift Report
- Documentation Recommendations

Never changes architecture.

---

## Chief of Staff / Brainstorming / Prompt Engineer (GPT)

Mission:

Multiply the effectiveness of every other role.

Responsibilities:

- Break large initiatives into executable workstreams
- Prepare implementation briefs
- Draft prompts for each AI role
- Identify opportunities and blind spots
- Facilitate communication between roles
- Prioritize backlog items
- Improve workflows
- Brainstorm new features
- Prepare RFCs before architectural review
- Coordinate milestone planning

Produces:

- Implementation Briefs
- RFCs
- Prompt Packages
- Sprint Plans
- Milestone Plans
- Feature Decomposition
- Meeting Summaries
- Decision Matrices

This role is responsible for making every other AI role more effective.

---

# Information Flow

Product Owner

↓

Chief of Staff

↓

Chief Technology Officer

↓

Implementation Brief

↓

Principal Engineer (Claude)

↓

Implementation Report

↓

Quality & Release Review

↓

Product Owner Approval

↓

Merge

↓

Historian / Librarian Pass

↓

Release

---

# Standard Artifacts

## Product Owner

Produces:

- Product Goals
- Priorities
- Decisions

---

## Chief of Staff

Produces:

- RFCs
- Prompt Packages
- Sprint Plans
- Milestone Plans

---

## CTO

Produces:

- Architecture Review
- PRDs
- ADR Recommendations
- Roadmap Updates

---

## Principal Engineer

Produces:

- Code
- Tests
- Benchmarks
- Engineering Review
- Technical Debt Report

---

## QA

Produces:

- Release Recommendation
- Risk Report

---

## Librarian

Produces:

- Repository Health
- Documentation Audit
- Changelog
- Drift Report

---

# Communication Rules

Every role communicates through artifacts rather than conversation history.

Preferred inputs:

- PRDs
- ADRs
- Implementation Briefs
- Engineering Reports
- QA Reports
- Repository Health Reports

Avoid passing entire chat histories whenever possible.

---

# Core Operating Principle

No AI role is authoritative because of its memory.

Every recommendation, implementation, and review must be grounded in the current approved project artifacts.

Evidence always takes precedence over recollection.

---

# Current Priorities

This section is a pointer, not a second coordination ledger.

1. Complete v0.3.1 post-merge Librarian closeout.
2. Keep push, tag, and release blocked until the closeout is accepted.
3. Keep v0.4 Project Resume implementation blocked until its explicit authorization gate.
4. Keep the earlier v0.4-named conversation candidate parked for future v0.5
   reconciliation.

For the current receiver and incoming artifact, use
[Project Control](docs/coordination/README.md).

---

# Long-Term Development Path

Knowledge Foundation

↓

Retrieval

↓

Conversation

↓

Memory

↓

Plugins

↓

Agents

↓

Automation

↓

AI Operating System

---

# Success Metrics

Technical

- Passing tests
- Performance
- Documentation quality
- Repository health
- Architecture consistency

Product

- User usefulness
- Explainability
- Trustworthiness
- Scalability
- Maintainability

Organization

- Clear ownership
- High-quality handoffs
- Evidence-based decisions
- Minimal documentation drift
- Repeatable development process

---

# Immediate Next Actions

Chief of Staff

- Prepare implementation briefs
- Coordinate milestone planning
- Maintain prompt library

CTO

- Continue executive architecture reviews
- Validate roadmap

Principal Engineer

- Do not begin v0.4 until the Project Resume index records explicit implementation
  authorization.

Quality & Release

- Validate implementation evidence
- Recommend release disposition

Historian

- Complete the assigned post-merge repository closeout.
- Maintain documentation integrity and preserve superseded history.

Product Owner

- Approve priorities
- Resolve escalated decisions
- Approve releases

---

This document should be reviewed after every major milestone and updated whenever the organizational structure or development workflow changes.
