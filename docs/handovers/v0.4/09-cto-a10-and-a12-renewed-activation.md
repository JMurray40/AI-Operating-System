# CTO — Renewed A10 and A12 Activation

| Field | Value |
|---|---|
| Role | Chief Architect / CTO |
| Milestone | v0.4 — Read-only Project Resume CLI Pilot |
| Date | 2026-07-29 |
| Executable | `014076c429d47de83be4ca6543264082aa62633f` |
| Documentation | `10ebf331449ad11dd0cb4e5e40ffd50d3f531bd9` |
| Engineering branch | `feature/v0.4-project-resume` |
| Pilot baseline | Accepted post-classification baseline from Handoff 07 |
| Reference profile | Product Owner-approved current Windows PC |
| Status | **A10 and A12 separately activated under bounded scopes** |

## 1. Reviewed authority and evidence

This review covers Handovers 03 through 08, including:

- the preserved fail-closed authorization and owner-controlled onboarding decision;
- the Product Owner's exact classification authorization;
- the stopped and rolled-back earlier execution;
- the reachability-based Git-integrity clarification;
- the accepted sensitivity-only classification and post-classification baseline; and
- the validated installation, onboarding, diagnostics, packaging, and recovery
  documentation correction.

The accepted private evidence identities are:

```text
Pre-edit:           964ca74065d9e97d60a93b305b46e480ce6f134f652da4b246563a3686fad58d
Apply:              99908bfbeb547f950d6970992585b702452babb617857baff2f5f7eebc1dd641
Post-classification:fcc7d1d8fbf47f4f1acdc0ed1ebfbd949cdd895e8f1e6964db6c25c3178a5793
```

Each digest resolves exactly once in the approved private evidence package. Private
paths, classifications, note names/content, Git subjects/authors/remotes, credentials,
and raw errors remain outside this artifact.

## 2. Independent verification

### 2.1 Executable and documentation identity

Both supplied identities are valid commits. Documentation commit
`10ebf331449ad11dd0cb4e5e40ffd50d3f531bd9` is a direct child of executable commit
`014076c429d47de83be4ca6543264082aa62633f`.

The child changes exactly eight files, all beneath `docs/software/`:

- `ARCHITECTURE.md`;
- `CLI_USAGE.md`;
- `KNOWN_LIMITATIONS.md`;
- `PROJECT_RESUME.md`;
- `PROJECT_RESUME_INSTALLATION_AND_RECOVERY.md`;
- `README.md`;
- `SETUP.md`; and
- `TESTING.md`.

There is no delta under `src/`, `tests/`, `scripts/`, `pyproject.toml`, ADRs, pilots,
private evidence, or any other non-documentation path. `git diff --check` passes. The
executable being evaluated remains exactly `014076c`.

### 2.2 Classification and post-classification baseline

The accepted baseline binds executable `014076c` and reports:

- exact current hashes for the eight approved sensitivity-only results;
- verified canonical Git stability;
- verified core Git-control stability;
- identical before/after reachable-object digests;
- a valid, expected status delta limited to the approved classification result;
- no new ambient unreachable-object drift during the accepted classification window;
- continued non-Git status for the approved non-Git pilot;
- exact-byte rollback readiness;
- exact project selection within each authorized view; and
- no measured A10 run before activation.

This satisfies the canonical/reachable boundary in Handoff 06. Classification is an
accepted Product Owner-controlled input-baseline act, not a Jarvis write or a relaxation
of ADR-0015.

### 2.3 Documentation sufficiency

Documentation commit `10ebf331` provides the non-author path required for A12:

- clean supported-environment installation;
- installed-command verification without editable mode or `PYTHONPATH`;
- uninstall, command-removal proof, reinstall, and deterministic fixture rerun;
- explicit sensitivity onboarding and fail-closed `not_found` behavior;
- owner inventory, approval, backup, validation, rollback, and baseline procedure;
- `resume-doctor` diagnostics and troubleshooting;
- missing/corrupt derived-state recovery without canonical-source repair;
- reachability-based Git-integrity evidence and separate unreachable-drift reporting;
- an independent A12 procedure; and
- private/public pilot and engineering-handoff evidence boundaries.

The reported documentation validation checked 417 relative links with no broken target.

## 3. Explicit dependency-acquisition decision

**NARROW INSTALLATION-ONLY PYTHON PACKAGE-INDEX ACCESS IS AUTHORIZED FOR A12.**

This exception exists only to create the isolated clean A12 environment and acquire the
declared PyYAML runtime dependency. It is not runtime network authorization.

The independent reviewer must apply this sequence:

1. Create the isolated supported Python environment without mounting, opening, naming,
   hashing, or otherwise exposing either private pilot.
2. Ensure no pilot path, content, Git metadata, remote, credential, provider setting, or
   private evidence value is present in the command, environment, process input, log, or
   network request.
3. Permit TLS package acquisition only from the approved public Python package index and
   its package-file host, only for a PyYAML version satisfying the repository's declared
   `PyYAML>=6.0` requirement.
4. Disable package-manager version checks and do not use an authenticated index, private
   mirror, credential helper, proxy credential, or repository remote.
5. Record only package name, resolved version, public source, downloaded artifact hash,
   installation command shape, exit status, and redacted outcome.
6. Install the local candidate from documentation commit `10ebf331` without editable
   mode, `PYTHONPATH`, or further dependency resolution.
7. Disable and independently verify network denial before any pilot root or private
   evidence destination is made available to the A12 process.
8. Keep network denied for installed-command verification, fixtures, both pilots,
   diagnostics, recovery, uninstall/reinstall verification, and all runtime activity.

This exception does not authorize acquisition of an undeclared runtime dependency. The
build backend and installer must come from the supported Python distribution or an
already approved local environment. If the local candidate cannot be installed after
PyYAML acquisition without another download, the reviewer must stop and report A12 as
`Unavailable` or `Blocked`; the reviewer may not widen the exception.

If the public package-index boundary cannot be technically restricted and evidenced as
above, network installation is not permitted. A12 then remains paused until a separately
approved offline PyYAML wheel/cache is supplied with version, origin, SHA-256, and malware
or provenance review.

No network exception applies to A10.

## 4. A10 authorization — Principal Engineer

The Principal Engineer is authorized to execute acceptance test A10 against:

- executable `014076c429d47de83be4ca6543264082aa62633f`;
- the exact two Product Owner-approved, classified pilots;
- the accepted post-classification baseline identified above; and
- the Product Owner-approved current-PC reference profile.

### Required modes

Run and report separately:

1. the Git-enabled pilot with repository activity denied;
2. the Git-enabled pilot with the exact request-scoped local read-only Git grant;
3. the non-Git pilot with repository activity denied/unavailable; and
4. the documented cold/warm, retrieval-stage, and total-latency modes required by the
   implementation brief.

No `not_found` preflight or other failed briefing may be counted as successful A10
performance evidence.

### Required A10 evidence

The private evidence must record:

- executable, documentation, owner decision, and accepted baseline identities;
- actual current-PC reference profile, Python and Git versions, and local conditions;
- exact redacted command shapes, configuration, explicit evaluation time, budgets, modes,
  run counts, warm-ups, and completion markers;
- discovered, authorized, excluded, selected, omitted, and coverage aggregates;
- every raw retrieval-stage and total sample;
- independently recomputable p50, p95, and p99 for retrieval and total latency;
- an under-30-second total result for every valid pilot run;
- safe repository-denied, repository-granted, and no-Git outcomes;
- before/after canonical and reachable Git evidence;
- before/after canonical bytes for both pilots;
- separately reported `ambient_unreachable_object_drift`, if any, under Handoff 06;
- conflicts, staleness, missing-context, coverage, limitations, and exit statuses; and
- private artifact hashes plus a redacted committed summary.

Any canonical mutation, reachable-object change, unprovable object drift, privacy leak,
provider/network/telemetry activity, incorrect selector, or invalid timing protocol stops
A10 and returns a finding. The Principal Engineer may integrate valid A10 evidence into
the engineering handoff but may not fix or modify the candidate under this authorization.

## 5. A12 authorization — Independent Codex reviewer

An independent Codex reviewer is authorized to execute A12 against:

- executable `014076c429d47de83be4ca6543264082aa62633f`;
- documentation commit `10ebf331449ad11dd0cb4e5e40ffd50d3f531bd9`;
- the exact accepted post-classification pilot baseline; and
- the current-PC supported clean-environment profile.

The reviewer must act as a non-author and use only the published documentation. Clarifying
an observable failure is allowed; receiving an undocumented setup step, implementation
fix, private interpretation, or author-assisted workaround is not.

### Required A12 procedure

1. Verify the exact executable/documentation pair and a clean isolated environment.
2. Acquire PyYAML only under Section 3, then prove network denial before pilot exposure.
3. Install non-editably without `PYTHONPATH`; verify installed `jarvis`, `resume`, and
   `resume-doctor` help.
4. Run the deterministic fixture twice with the documented explicit evaluation time and
   compare exact outputs/hashes.
5. Exercise both accepted pilots, repository-denied, request-scoped local read-only Git,
   no-Git degradation, invalid input/root, partial/incomplete, and redacted diagnostic
   behavior.
6. Exercise missing/corrupt derived-state recovery without repairing or writing canonical
   sources.
7. Uninstall, prove the command is removed, reinstall without network, and repeat the
   deterministic fixture result.
8. Compare complete before/after canonical state and the Handoff 06 Git boundary.
9. Record valid unreachable-object drift separately and fail on any blocking condition.
10. Report every unavailable step as `Unavailable`, never `Pass`.

The A12 evidence must record redacted commands, environment facts, expected and actual
results, exit statuses, changed/created paths outside the pilots, cleanup, package
identity/hash/source, network-disable proof, canonical/reachable comparisons, private
artifact digests, limitations, and one explicit A12 disposition.

The reviewer must not repair documentation or implementation during review. A defect is
returned as evidence through the active engineering/CTO gate.

## 6. Boundaries common to A10 and A12

Both authorizations preserve these invariants:

- authorization precedes selection, retrieval, and graph expansion;
- missing/unknown sensitivity remains excluded and non-disclosed;
- Jarvis never assigns classifications or edits canonical notes;
- all runtime vault and Git access is read-only;
- repository activity remains denied by default and request-scoped when granted;
- the non-Git pilot remains non-Git;
- no real provider, API key, cloud service, live GitHub, Git remote, fetch, pull, push,
  clone, or credential use is permitted;
- no telemetry, upload, dogfood event collection, or runtime egress is permitted;
- private evidence remains in the approved ignored destination;
- public artifacts contain only digests, aggregate safe results, and redacted errors;
- no additional classification, migration, note repair, normalization, or pilot edit is
  permitted; and
- the parked conversation candidate and all v0.5 work remain excluded.

New valid unreachable loose objects are never silently waived. They may be reported as
ambient drift only when every Handoff 06 condition passes. The evidence must not claim a
background process caused them without causal proof.

## 7. Explicit non-authorization

Neither A10 nor A12 authorization:

- clears architecture conformance;
- performs or authorizes Quality & Release review;
- authorizes merge, push, tag, deployment, release, or publication;
- authorizes candidate, test, benchmark, script, ADR, pilot, or documentation changes;
- authorizes another classification or migration;
- authorizes A11 dogfood collection;
- waives any A1–A12 acceptance requirement;
- permits a provider, telemetry, Git remote, general internet access, or runtime network;
  or
- expands v0.4 beyond the accepted Project Resume scope.

Any required change returns through Principal Engineering and a new exact-commit CTO
review.

## 8. Required return package

After both bounded scopes complete, the Principal Engineer may integrate:

- its A10 evidence;
- the independent A12 disposition and evidence digest;
- the executable/documentation identities;
- the accepted onboarding evidence identities;
- all remaining A1–A9 technical evidence; and
- explicit skips, limitations, and blockers

into the required engineering handoff:

```text
docs/handovers/v0.4/02-principal-engineer-to-cto-engineering-review.md
```

This activation does not prejudge that handoff or the later architecture disposition.

## 9. Explicit disposition

**A10 AND A12 ARE SEPARATELY AUTHORIZED UNDER THE EXACT SCOPES ABOVE.**

A10 may run now in the existing approved environment against the accepted classified
pilots and current-PC profile. A12 may create its isolated environment using the narrow
PyYAML installation exception, but must disable network before any pilot exposure and use
only documentation commit `10ebf331`.

The executable remains frozen at `014076c`. Architecture clearance, QA, merge, push,
release, additional classification, candidate modification, and v0.5 work remain
unauthorized.
