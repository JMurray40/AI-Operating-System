# Handoff 23 — Chief of Staff to Principal Engineer: Command-scope Activation

**Date:** 2026-07-29

**Disposition:** **AUTHORIZED FOR ONE BOUNDED CORRECTION**

**Starting candidate:** `a7292fd71aa678d10c66c1645340e54199060045`

**Authoritative design:** Handoff 22, Option A

## Authorized work

Implement Handoff 22 Sections 4, 6, 7, and 8 exactly:

1. remove the complete temporary-file, ACL, owner/SID, stale-cleanup, substitution-detection,
   marker, manifest, and artifact-authentication subsystem;
2. after exact authorization, identity, canonical-root, and Git-version validation, supply
   exactly:

   ```text
   GIT_CONFIG_COUNT=1
   GIT_CONFIG_KEY_0=safe.directory
   GIT_CONFIG_VALUE_0=<exact canonical granted root>
   ```

3. retain `GIT_CONFIG_NOSYSTEM=1` and null global configuration;
4. enforce Git 2.38.0 as the minimum for granted repository activity;
5. preserve the three accepted Git command arrays byte-for-byte;
6. update only directly affected tests and narrowly necessary documentation; and
7. demonstrate every CS-01 through CS-22 acceptance row.

## Convergence controls

This is a removal-and-replacement correction, not another hardening pass on the file design.
No dormant fallback, temporary configuration artifact, alternate Git configuration path, or
generic compatibility framework may remain.

Engineering must perform the complete acceptance matrix before returning. A single returned
handoff must identify any row that cannot be demonstrated rather than stopping after the first
failure.

The independent Windows identity run is required before CTO routing. If Engineering cannot
execute it directly, freeze the candidate and return it to the Chief of Staff for that one
environmental validation; do not claim the row passed.

## Required return

Provide:

- exact branch, parent, and new candidate;
- exact changed files and bounded diff;
- proof the file-based subsystem is completely absent;
- proof the three command arrays are byte-identical;
- CS-01 through CS-22 mapped to named tests or retained evidence;
- targeted and full test totals;
- Ruff, mypy, and `git diff --check` results;
- Git 2.38 floor and approved Git 2.55 process-boundary results;
- no-artifact and repository-integrity evidence; and
- any remaining limitation disclosed in one consolidated section.

Freeze the corrected candidate and stop for Chief of Staff validation.

## Still closed

No wheel, A10, A12, QA, merge, push, tag, release, pilot modification, classification
change, unrelated refactor, or v0.5 work is authorized.
