# CTO Acknowledgment — v0.4 Pilot and Reference Profile Substitution

| Field | Value |
|---|---|
| Role | Chief Architect / CTO |
| Milestone | v0.4 — Read-only Project Resume CLI Pilot |
| Date | 2026-07-28 |
| Status | **Accepted for candidate-specific A10/A12 evidence execution** |
| Product Owner decision | `02-product-owner-pilot-and-reference-profile-decision.md` |
| Frozen executable | `014076c429d47de83be4ca6543264082aa62633f` |
| Engineering branch | `feature/v0.4-project-resume` |
| Private manifest | `data/v0.4-evidence/014076c/pilot-inputs.json` |

## Decision acknowledged

For exact candidate `014076c429d47de83be4ca6543264082aa62633f`, the CTO
acknowledges the Product Owner's substitution of the original technical pilots and
reference profile.

The accepted A10/A12 technical pilots are:

1. **Survivor Group Tracker** — exact project note plus explicitly authorized local
   read-only Git activity.
2. **AI Prompt Suite** — exact project note, 33 Markdown files, and no Git repository;
   repository activity must remain denied/unavailable while local-vault briefing behavior
   continues safely.

The accepted technical reference machine is the current Product Owner-approved Windows PC:

- Windows 11 Pro `10.0.26200`;
- Intel Core i5-14450HX;
- 16 logical processors;
- 34,079,776,768 bytes physical memory;
- NVMe SSD;
- repository virtual-environment Python `3.14.4`; and
- Git `2.55.0.windows.1`.

This profile supersedes the final CTO brief's proposed Windows 11 23H2 / 4 logical CPU /
8 GiB / Python 3.10.12 benchmark profile for this candidate's technical evidence only.
Results must be labeled candidate/profile-specific and must not be presented as portable
performance claims.

## Verification

The CTO independently verified:

- engineering branch `feature/v0.4-project-resume`;
- exact clean candidate
  `014076c429d47de83be4ca6543264082aa62633f`;
- valid private manifest at the approved candidate-specific destination;
- manifest candidate identity equals the frozen executable;
- private evidence root is outside both pilot roots;
- the manifest is ignored through the repository's `data/` rule;
- Survivor Group Tracker is configured for explicitly authorized local Git;
- AI Prompt Suite is configured with repository mode `unavailable` and no repository root;
  and
- no engineering-worktree file was modified by this acknowledgment.

## Evidence interpretation

### Survivor Group Tracker

The pilot's current dirty Git state is the before/after baseline. It must not be cleaned,
stashed, reset, staged, committed, normalized, repaired, or otherwise altered for testing.

Before and after each relevant A10/A12 operation, evidence must bind and compare:

- worktree file inventory and content hashes;
- `git status` in a deterministic machine-readable form;
- `HEAD`;
- refs and packed refs;
- repository config;
- index bytes/fingerprint;
- relevant Git object/control-state fingerprints; and
- approved private evidence-destination state.

A pre-existing difference is not a Jarvis mutation. Any new or changed difference caused
by the candidate is release-blocking evidence.

### AI Prompt Suite

The absence of Git is an intentional degradation case. The result must:

- continue from authorized local Markdown evidence;
- omit or mark repository activity denied/unavailable;
- never describe unavailable activity as “no activity”;
- avoid retry loops and network discovery; and
- expose a clear limitation without treating dependency absence as total failure.

Sparse current-state text may correctly produce incomplete coverage, missing-context
limitations, or no supported claim for a section. That is valid evidence when it follows
the accepted claim/citation/coverage contracts. It becomes a defect only if the candidate:

- fabricates completeness or current state;
- presents unsupported material as verified;
- hides the limitation;
- emits misleading success/coverage status;
- substitutes another project or source; or
- fails to produce the safe locally supported portion of the briefing.

No pilot content may be fabricated or edited to improve the result.

## A10 authorization

The Principal Engineer is authorized to execute A10 against the exact frozen candidate and
the two substituted pilots.

Required modes:

- Survivor Group Tracker with repository activity denied;
- Survivor Group Tracker with explicitly granted local read-only Git;
- AI Prompt Suite with repository activity unavailable/no Git; and
- documented cold/warm and retrieval/total timing modes required by the CTO brief.

Required evidence:

- exact candidate and private-manifest identity;
- actual approved reference profile;
- commands, configuration, evaluation time, budgets, source counts, omissions, and modes;
- raw retrieval-stage and total samples;
- p50/p95/p99 recomputation;
- under-30-second result for each valid pilot run;
- before/after source and Git integrity proof;
- coverage, conflict, limitation, and degradation outcomes;
- redacted committed summary plus private-artifact digest; and
- no claim of equivalence to the superseded proposed profile.

The Principal Engineer may integrate the resulting evidence into the engineering handoff
but may not modify the frozen executable to improve evidence without returning through
the engineering/CTO gate.

## A12 authorization

Codex acting as an independent packaging/recovery reviewer is authorized to execute A12
against the exact frozen candidate after confirming that the candidate's packaging,
installation, Project Resume, diagnostics, and recovery instructions/artifacts exist.

The reviewer must:

- use only published non-author instructions;
- preserve both pilot roots and the existing dirty Git baseline;
- test both substituted pilot briefings;
- cover no-Git degradation and authorized local Git;
- test missing/corrupt derived-state recovery outside canonical sources;
- perform uninstall/reinstall and deterministic fixture rerun where documented;
- retain private evidence only under the approved ignored destination;
- report unavailable steps as `Unavailable`, not `Pass`;
- avoid repairs during review; and
- return failures through the active governance handoff.

This acknowledgment does not itself assert that A12 activation prerequisites are already
complete and does not perform A12.

## Privacy and evidence boundary

Private absolute paths and raw pilot evidence remain only in:

```text
data/v0.4-evidence/014076c/
```

Committed evidence may contain only the redacted fields allowed by the final CTO brief and
Product Owner decision. It must not contain pilot passages, private task/question text,
full private paths, usernames, Git subjects/authors/remotes, credentials, or raw errors.

No telemetry, upload, GitHub/network access, provider egress, or silent dogfood collection
is authorized.

## Scope and non-authorization

This acknowledgment changes evidence inputs and the technical reference profile only. It
does not:

- change executable scope or accepted ADRs;
- authorize edits after `014076c`;
- clear architecture conformance or QA;
- waive A1–A12 requirements;
- authorize live GitHub, network, credentials, providers, or the parked conversation
  candidate;
- authorize merge, push, release, or v0.5 work; or
- convert sparse/incomplete evidence into a defect or a pass without contract-based
  assessment.

## Required next actions

1. Principal Engineer runs A10 against both substituted pilots and retains/redacts evidence
   as specified.
2. Independent Codex reviewer performs A12 only after verifying its packaging/recovery
   activation requirements.
3. Principal Engineer integrates A10 and independently produced A12 evidence and writes:

```text
docs/handovers/v0.4/02-principal-engineer-to-cto-engineering-review.md
```

4. CTO performs exact-candidate architecture conformance review from the completed
   engineering handoff.

## Disposition

**PILOT SUBSTITUTION AND CURRENT-PC REFERENCE PROFILE ACKNOWLEDGED.**

A10 evidence execution may proceed. A12 may proceed when its documented activation
requirements are verified. This is not candidate clearance, QA authorization, merge
authority, or release approval.
