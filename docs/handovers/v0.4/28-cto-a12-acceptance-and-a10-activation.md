# Handoff 28 — CTO A12 Acceptance and A10 Activation

**From:** Chief Architect / CTO  
**To:** Chief of Staff; Principal Engineer  
**Date:** 2026-07-29  
**Scope:** Bounded evidence binding for the exact v0.4 Project Resume candidate  
**Disposition:** **A12 ACCEPTED — A10 SEPARATELY ACTIVATED**

## 1. Authoritative inputs

This review is based on:

- Handoff 25, `25-cto-command-scope-exact-candidate-clearance.md`;
- `docs/evidence/v0.4/a12-ff402d7-packaging-recovery.md`; and
- Handoff 27, `27-a12-to-cto-and-quality-packaging-recovery-clearance.md`.

The review preserves the Product Owner pilot substitution, classification authorization,
post-classification baseline, current-PC reference profile, Handoff 06 canonical/reachable
Git boundary, privacy boundary, and all accepted Project Resume ADRs.

## 2. Bound identities

| Item | Accepted identity |
|---|---|
| Executable | `ff402d7f82c061426a5e960f7177d916c355bbf2` |
| Executable tree | `a7ff2c023b0e59df1f8bbc2ad05a3af843a5e344` |
| Wheel | `jarvis_core-0.1.0-py3-none-any.whl` |
| Wheel SHA-256 | `8dcc1378a1ac4c3b96dbfea94c0443e92ffaec54fafeb1db5aa73e449a768cd3` |
| Wheel size | 126,683 bytes |
| Runtime payload | 68 `jarvis_core` files |
| Distribution metadata | 6 entries |
| PyYAML wheel SHA-256 | `4a2e8cebe2ff6ab7d1050ecd59c25d4c8bd7e6f400f5f82b96557ac0abafd0ac` |
| A12 public evidence | `docs/evidence/v0.4/a12-ff402d7-packaging-recovery.md` |

The executable commit independently resolves to the stated executable tree. The
candidate-specific wheel independently rehashes to the accepted SHA-256 and has the stated
size.

The wheel bound to `014076c429d47de83be4ca6543264082aa62633f` remains superseded.
Its distinct digest is not accepted as executable, installation, payload, or A12 evidence
for this candidate.

## 3. Handoff 25 Section 7.2 determination

**Section 7.2 is satisfied.**

The independent A12 record establishes:

1. the fresh wheel digest and size matched the Engineering return;
2. all 74 wheel entries were enumerated;
3. all 68 candidate-owned runtime payload files were byte-identical to
   `ff402d7:src/jarvis_core/*`;
4. no runtime payload was missing, mismatched, unbound, or placed under an unexpected
   top-level package;
5. distribution metadata declared package `jarvis-core` version 0.1.0;
6. the Python floor, sole runtime dependency `PyYAML>=6.0`, console entry point
   `jarvis = jarvis_core.cli:main`, and `py3-none-any` wheel tag were correct; and
7. no unexpected dependency, provider, build-backend, or executable payload was reported.

The verified wheel digest is therefore the sole accepted installation identity for
candidate `ff402d7`.

## 4. Handoff 25 Section 7.3 determination

**Section 7.3 is satisfied.**

The independent non-author A12 evidence demonstrates:

- creation of a clean isolated CPython 3.14.4 environment before pilot exposure;
- offline, dependency-disabled installation of the retained verified PyYAML wheel and
  candidate wheel;
- no setuptools or build backend;
- network denial proved before either private pilot was exposed;
- installed-command and help verification;
- successful deterministic fixture execution;
- granted different-owner repository operation using the accepted request-scoped
  command environment;
- safe no-Git degradation for the non-Git pilot;
- healthy `resume-doctor` results;
- absence of persistent or temporary Jarvis Git-configuration artifacts;
- uninstall, command-removal proof, offline reinstall from the same verified wheel, and
  reproduction of command, fixture, pilot, and doctor outputs;
- exact before/after canonical, worktree, index, refs, reflogs, configuration, remotes,
  ownership, reachable-object, no-Git, fixture, and command-boundary comparisons; and
- private before/after evidence digests whose differences are limited to evidence
  bookkeeping fields.

The evidence also records that pre-existing artifacts from superseded testing were neither
accessed nor modified. They are not candidate artifacts or accepted evidence inputs.

No A12 stop condition is present.

## 5. Exact-candidate A12 acceptance

**A12 is accepted for executable `ff402d7f82c061426a5e960f7177d916c355bbf2`,
tree `a7ff2c023b0e59df1f8bbc2ad05a3af843a5e344`, and wheel SHA-256
`8dcc1378a1ac4c3b96dbfea94c0443e92ffaec54fafeb1db5aa73e449a768cd3`.**

This acceptance is evidence-bound. Any executable, tree, packaging metadata, wheel bytes,
dependency identity, documentation procedure, or accepted pilot baseline change invalidates
it.

A12 acceptance does not authorize Quality & Release, merge, push, tag, publication, or
release.

## 6. Separately scoped A10 activation

The Principal Engineer is now authorized to execute A10 only against:

- executable `ff402d7f82c061426a5e960f7177d916c355bbf2`;
- executable tree `a7ff2c023b0e59df1f8bbc2ad05a3af843a5e344`;
- the Product Owner-approved current-PC reference profile;
- the accepted post-classification baseline;
- Survivor Group Tracker as the Git-enabled classified replacement pilot; and
- AI Prompt Suite as the classified non-Git replacement pilot.

The verified A12 wheel is not required to become the A10 execution mechanism. If A10 uses
an installed wheel rather than the exact clean source checkout, it must use only the bound
wheel digest in Section 2 and record that choice. Mixing execution identities within a
reported mode is prohibited.

No network, provider, API key, telemetry, Git remote, credential, live GitHub, parked
conversation candidate, or external service is permitted. The pilots and their
classifications remain read-only.

## 7. Exact A10 evidence matrix

Every matrix row is mandatory.

| ID | Required execution/evidence | Acceptance rule |
|---|---|---|
| A10-01 | Record executable commit/tree and, if used, wheel digest | Exact match to Section 2 |
| A10-02 | Record the approved current-PC profile: OS/build, CPU model and available/allotted logical CPUs, physical/available memory, storage type, Python, Git, power state, process affinity, and material background-load facts | Actual conditions disclosed; no unsupported equivalence claim |
| A10-03 | Record explicit evaluation time, budgets, selectors, authorization/grant mode, contract versions, command shape, run counts, warm-ups, percentile estimator, and completion markers | Predeclared before measured samples |
| A10-04 | Git-enabled pilot, repository activity denied | Useful safe briefing; no Git-derived claim/citation; limitation explicit |
| A10-05 | Git-enabled pilot, exact request-scoped local read-only Git grant | Useful safe briefing; bounded Git evidence; no broader repository authority |
| A10-06 | Non-Git pilot, repository activity unavailable/no Git | Useful safe partial briefing; explicit degradation; no repository citation |
| A10-07 | Cold and warm pilot modes reported separately | No aggregation that hides cold-start behavior |
| A10-08 | Three warm-ups followed by at least 30 measured attempts for every warm measured mode | Warm-ups excluded from reported samples |
| A10-09 | Raw retrieval-stage and total-latency sample for every valid measured attempt | Complete arrays retained; no selective deletion |
| A10-10 | Independently recomputable retrieval and total p50/p95/p99 using the predeclared released nearest-index estimator | Recomputed values equal reported values |
| A10-11 | Every valid real-pilot total sample | Strictly less than 30 seconds |
| A10-12 | Stage timing for discovery, authorization, identity, retrieval, graph, authority/conflict, citation validation, Git, rendering, and total where instrumented | Stage boundaries and unavailable measurements explicit |
| A10-13 | Peak memory for every required mode | Method and raw/result units recorded |
| A10-14 | Discovered, authorized, excluded, selected, omitted, source, claim, citation, conflict, limitation, and coverage counts | Counts reconcile with the produced result |
| A10-15 | Missing/unknown sensitivity and excluded material | Excluded before project selection; no excluded-source disclosure |
| A10-16 | Project identity and ambiguity behavior | Exact approved project selected; no fuzzy/substitute selection |
| A10-17 | Citation and trust behavior | Current fingerprints/locators/excerpts valid; Git citations snapshot/object-bound |
| A10-18 | Conflicts, staleness, missing context, incomplete coverage, limitations, and exit status | Visible, structurally correct, and not overstated |
| A10-19 | Deterministic synthetic scale points at 100, 500, 1,000, and 5,000 notes, including high fan-out and cycles | Terminates within documented budgets; raw timing and counts retained |
| A10-20 | Synthetic repository activity | Disabled; fixtures only |
| A10-21 | Before/after canonical-byte inventories for both classified pilots | Exact equality |
| A10-22 | Git-enabled pilot before/after HEAD, worktree status, index, refs, reflogs, configuration, remotes, ownership, reachable objects, and recorded loose-object boundary | Canonical and reachable state exact |
| A10-23 | New unreachable loose objects, if any | Separately reported as `ambient_unreachable_object_drift` only when every Handoff 06 condition passes; no causal claim without proof |
| A10-24 | Non-Git pilot before/after repository state | Remains non-Git |
| A10-25 | Runtime network/provider/telemetry boundary | No egress, provider, upload, remote Git, or telemetry |
| A10-26 | Privacy/redaction review of public outputs | No private path, note content, classification detail, Git subject/author/remote, username, credential, or raw error |
| A10-27 | Failure and completion accounting | Every launched attempt has an outcome; failures retained and explained |
| A10-28 | Successful-briefing validity | `not_found`, failed selection, invalid output, or incomplete execution is never counted as successful performance evidence |
| A10-29 | Candidate and pilot immutability during evidence generation | No executable, wheel, test, script, benchmark, documentation, pilot, or classification modification |
| A10-30 | Redacted committed evidence and private-artifact hashes | Public/private fields comply with Section 8 |

If a required stage cannot be measured without changing the frozen candidate, report it as
unavailable and stop for governance review. Do not add instrumentation to the candidate.

## 8. Exact A10 evidence locations

Private raw evidence must be written only under the already ignored repository-relative
location:

```text
data/v0.4-evidence/ff402d7/a10/
```

That directory must contain a redacted-field manifest binding every private artifact by
filename, size, SHA-256, execution mode, attempt count, and completion state. It must not
contain a copy of either pilot or candidate.

Required committed redacted artifacts:

```text
docs/evidence/v0.4/project-resume-performance-ff402d7.json
docs/evidence/v0.4/pilot-evaluation-ff402d7.json
```

Committed artifacts may contain only the allowed aggregate identities, counts, timings,
coverage totals, defect categories, gate results, private-artifact digests, and reviewer
disposition. They must not contain pilot passages, private task/question text, absolute
paths, note names beyond already approved public pilot display names, usernames, Git
subjects/authors/remotes, credentials, classifications, or raw errors.

## 9. A10 stop conditions

A10 stops and returns a finding on:

- candidate, wheel, pilot, classification, or accepted-baseline mismatch;
- canonical-byte or reachable-object mutation;
- unprovable Git-object drift;
- repository grant expansion or missing/mismatched grant acceptance;
- private-data or excluded-source disclosure;
- provider, telemetry, runtime network, remote-Git, or credential activity;
- an invalid timing boundary, missing raw sample, selective sample removal, or
  non-recomputable percentile;
- a valid pilot total sample at or above 30 seconds;
- inability to produce a successful briefing for either classified pilot;
- reliance on `not_found` as passing timing evidence; or
- any undocumented step required to obtain a pass.

The Principal Engineer may document a finding but may not modify the frozen candidate,
wheel, pilots, classifications, benchmark protocol, or evidence rule under this
authorization.

## 10. Reusable prior evidence

The following remains reusable when cited with its exact original identity and digest:

1. Handoff 25’s architecture clearance and CS-01 through CS-22 results for exact executable
   `ff402d7`;
2. Handoff 24’s independent Windows-identity CS-21 result;
3. the A12 evidence and acceptance bound in Sections 2 through 5 of this handoff;
4. Product Owner pilot substitution and classification approvals;
5. accepted pre-edit, apply, and post-classification evidence digests;
6. the accepted post-classification canonical/reachable baseline and Handoff 06 integrity
   rule;
7. documentation-only ancestry and published-procedure validation unchanged by
   `ff402d7`;
8. the verified retained PyYAML wheel identity and offline-installation proof;
9. privacy, no-provider, no-telemetry, and no-remote policy evidence that is independent
   of measured A10 execution; and
10. earlier A1–A9/A11-mechanism evidence whose covered executable paths were unchanged,
    provided the Engineering return maps that evidence to `ff402d7` ancestry and replaces
    any local-Git-affected portion with Handoffs 24, 25, and 27.

The following is not reusable as passing evidence:

- the superseded `014076c` wheel, installed-candidate, local-Git, doctor, payload, or A12
  result;
- performance timing from another executable, profile, pilot baseline, or protocol;
- the original proposed pilot/reference profile;
- pre-classification `not_found` timings;
- any earlier A10 result not bound to `ff402d7`; or
- a prior final integrity comparison in place of the A10-specific before/after comparison.

## 11. Required routing after A10

After A10 completes:

1. The Principal Engineer validates the private manifest and produces the two redacted
   committed evidence artifacts in Section 8.
2. The Principal Engineer integrates A10, the accepted independent A12 package, A1–A9,
   the A11 evidence mechanism with eight-week outcome collection explicitly pending, all
   reusable evidence identities, limitations, and blockers into:

   ```text
   docs/handovers/v0.4/02-principal-engineer-to-cto-engineering-review.md
   ```

3. The Chief of Staff validates exact candidate, tree, wheel, documentation, evidence
   digests, protocol completeness, privacy, and worktree scope before CTO routing.
4. **A further CTO review is required before Quality & Release.** That review must assess
   the complete v0.4 architecture and A1–A10/A12 evidence package, confirm no regression
   from the local-Git correction, resolve every limitation or unavailable row, and issue
   an exact-candidate architecture disposition.
5. Quality & Release may begin only if that later CTO disposition explicitly authorizes it
   against exact executable, tree, wheel, documentation, evidence commits/digests, and a
   complete adversarial QA matrix.

This handoff does not itself authorize Quality & Release.

## 12. Final gate state

- A12: **accepted** for the identities in Section 2.
- A10: **activated** for the exact scope in Sections 6 through 9.
- Candidate/wheel modification: prohibited.
- Pilot/classification modification: prohibited.
- QA, merge, push, tag, publication, release, unrelated work, and v0.5: prohibited.

**Final CTO disposition:** **Accept exact-candidate A12 evidence and proceed with bounded
A10 only. Return through Engineering, Chief-of-Staff validation, and one final CTO
architecture/evidence review before any Quality & Release authorization.**
