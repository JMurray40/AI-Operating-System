# Product Owner Authorization — v0.4 Pilot Classification

| Field | Value |
|---|---|
| Role | Product Owner |
| Milestone | v0.4 — Read-only Project Resume CLI Pilot |
| Date | 2026-07-29 |
| Decision ID | `product-owner-approval-2026-07-29` |
| Frozen executable | `014076c429d47de83be4ca6543264082aa62633f` |
| Status | **Narrow classification authorization granted** |
| Governing disposition | `03-cto-to-product-owner-pilot-classification-onboarding-disposition.md` |

## Decision

The Product Owner approves a one-time, owner-controlled classification of exactly four
previously identified notes in each approved pilot:

- Survivor Group Tracker: four notes;
- AI Prompt Suite: four notes.

The exact relative paths, pre-change hashes, and owner-selected labels are retained only
in the approved private ignored evidence package. They are intentionally omitted here to
preserve the privacy boundary established for pilot evidence.

Codex is the explicitly designated operator for these eight exact edits. The operator may
add only the individually approved `sensitivity` frontmatter values. This decision does
not authorize classification inference, propagation, bulk migration, formatting, content
repair, metadata normalization, or changes to any other note.

## Mandatory controls

Before editing, the operator must:

1. inventory and hash both pilot roots;
2. preserve Survivor Group Tracker's pre-existing dirty Git state;
3. record that AI Prompt Suite has no Git repository;
4. create an exact-byte backup outside both pilot roots and the software repository;
5. verify that the backup inventory digest equals the source inventory digest; and
6. retain the private approval and rollback evidence.

After editing, the operator must prove:

1. only the eight approved notes changed;
2. each change is exactly the approved sensitivity classification;
3. frontmatter and schema validation pass;
4. the canonical project note in each pilot is authorized and exactly selectable;
5. Survivor Group Tracker's HEAD, index, refs, config, objects, staging state, and
   pre-existing dirty state remain preserved beneath the approved classification delta;
6. AI Prompt Suite remains non-Git;
7. a verified exact-byte rollback remains available; and
8. no measured A10 run began before the post-classification baseline was established.

Any unexpected delta requires an immediate stop and exact-byte rollback from the verified
backup.

## Boundaries

This authorization supersedes the prior no-write restriction only for the eight approved
classification fields. It does not authorize:

- Jarvis runtime writes;
- additional note classification;
- candidate, ADR, implementation, test, or benchmark changes;
- A10 or A12 execution before renewed CTO acknowledgment;
- architecture clearance, QA, merge, push, or release;
- Git staging, committing, resetting, stashing, or cleaning in either pilot;
- Git initialization for AI Prompt Suite; or
- network, provider, credential, telemetry, or v0.5 work.

## Disposition

**AUTHORIZED FOR THE EIGHT EXACT OWNER-APPROVED CLASSIFICATION EDITS ONLY.**

A10 and A12 remain paused until the verified post-classification baseline, corrected
onboarding and packaging documentation, and renewed CTO acknowledgments are complete.
