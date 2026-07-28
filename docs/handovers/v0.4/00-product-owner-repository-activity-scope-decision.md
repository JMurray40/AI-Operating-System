# Product Owner Decision — v0.4 Repository Activity Scope

| Field | Value |
|---|---|
| Product Owner | Jason Murray |
| Milestone | v0.4 — Read-only Project Resume CLI Pilot |
| Decision date | 2026-07-27 |
| Status | Accepted |
| Related planning brief | `00-cto-to-principal-engineer-project-resume-planning-brief.md` |

## Decision

v0.4 repository activity is limited to:

- deterministic fixture data for automated evidence; and
- local read-only Git activity, subject to the approved local command, path, timeout,
  output, injection, read-only, and failure-handling controls.

Live GitHub access is deferred to a separately authorized connector milestone.

## Consequences

The v0.4 implementation authorization must:

1. exclude network and live GitHub access;
2. prohibit credentials, remote API calls, and provider egress;
3. require explicit request-scoped repository-activity grants;
4. use typed unavailable/denied/malformed/stale results rather than “no activity”;
5. prove local Git commands cannot mutate repositories;
6. constrain repository paths and arguments;
7. enforce timeouts, bounded output, deterministic parsing, and error redaction;
8. provide deterministic fixture coverage independent of installed Git.

The decision closes the planning brief’s repository-activity scope question. It does not
authorize implementation.

## Deferred scope

Any future live GitHub capability requires a new Product Owner decision plus:

- connector and permission scope;
- credential and secrets handling;
- privacy and egress review;
- rate-limit, timeout, pagination, and failure policy;
- prompt-injection and untrusted-content controls;
- independent security and release evidence.

## Exit statement

**Repository-activity scope accepted: fixtures plus local read-only Git only for v0.4.**
