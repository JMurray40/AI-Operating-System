# Product Owner Decision — v0.4 Pilot and Reference Profile

| Field | Value |
|---|---|
| Product Owner | Jason Murray |
| Milestone | v0.4 — Read-only Project Resume CLI Pilot |
| Decision date | 2026-07-28 |
| Status | Accepted operational substitution; CTO evidence-gate acknowledgement required |
| Frozen executable | `014076c429d47de83be4ca6543264082aa62633f` |

## Decision

The originally named AI Operating System and Cloud Organizer Pro vault pilots do not
exist as populated Project Resume vaults. They are replaced for v0.4 technical A10/A12
evidence by:

1. **Survivor Group Tracker** — local Markdown project evidence plus explicitly authorized
   local read-only Git activity.
2. **AI Prompt Suite** — local Markdown project evidence with no Git repository;
   repository activity must remain denied/unavailable and the briefing must continue from
   local evidence.

Both selected roots contain an explicit `type: project` entry note. Private absolute paths
are operational evidence and must remain in the approved ignored evidence destination;
they are not committed to the repository.

## Reference machine

The Product Owner approves the current Windows PC as the v0.4 technical reference machine,
superseding the proposed canonical profile in the original CTO brief for this candidate.

Observed profile:

- Windows 11 Pro, version/build `10.0.26200`;
- Intel Core i5-14450HX;
- 16 logical processors;
- 34,079,776,768 bytes physical memory;
- NVMe SSD;
- repository virtual environment Python `3.14.4`; and
- Git `2.55.0.windows.1`.

Evidence must record the actual profile and must not claim equivalence to Windows 11 23H2,
4 logical CPUs, 8 GiB, or Python 3.10.12. The under-30-second pilot gate applies on this
approved machine. Results are candidate/profile-specific and are not portable performance
claims.

## Evidence and privacy

Private raw evidence is approved under the Git-ignored candidate directory:

```text
data/v0.4-evidence/014076c/
```

Before execution, the runner must verify that the evidence destination is outside both
pilot roots and remains ignored by Git. Committed evidence may contain only the redacted
fields permitted by the final CTO brief.

The existing dirty state of any pilot Git repository is an input baseline, not an
authorization to modify it. Before/after evidence must prove Jarvis caused no file,
metadata, index, ref, configuration, or status change.

## Consequences

- A10 uses the two selected real local projects and the approved current PC.
- Survivor Group Tracker covers authorized local-Git activity.
- AI Prompt Suite covers vault-only behavior with repository activity unavailable.
- A12 uses the same two projects where documentation requires both pilot briefings.
- A11's mechanism remains complete, while its eight-week strategic result remains pending.
- Technical evidence must not claim validation of the nonexistent original vaults.
- The substitution changes evidence inputs and reference profile, not executable scope.
- The CTO must acknowledge this decision before treating A10/A12 evidence as satisfying
  the exact-candidate conformance gate.

## Explicit exclusions

This decision does not authorize:

- executable changes after frozen candidate `014076c`;
- GitHub, network, provider, credential, or remote-repository access;
- writes to either pilot;
- fabrication of project content or dogfood outcomes;
- release, merge, push of the feature branch, or CTO/QA clearance; or
- v0.5 work.

## Exit statement

**PILOT AND REFERENCE PROFILE SUBSTITUTION ACCEPTED.** A10/A12 execution may proceed only
under the existing read-only, privacy, evidence-retention, and exact-candidate controls.
