# CTO to Chief of Staff — Git Integrity Boundary Clarification

| Field | Value |
|---|---|
| Sender | Chief Architect / CTO |
| Receiver | Chief of Staff, Product Owner, Principal Engineer, and independent A12 reviewer |
| Milestone | v0.4 — Read-only Project Resume CLI Pilot |
| Date | 2026-07-29 |
| Frozen executable | `014076c429d47de83be4ca6543264082aa62633f` |
| Reviewed event | Pilot classification backup Retry-3 |
| Prior CTO disposition | `03-cto-to-product-owner-pilot-classification-onboarding-disposition.md` |
| Prior Product Owner authorization | `04-product-owner-pilot-classification-authorization.md` |
| Prior execution stop | `05-chief-of-staff-pilot-classification-execution-stop.md` |
| Status | **Git integrity boundary clarified; A10/A12 remain paused** |

## 1. Executive finding

Retry-3 stopped before classification. No `sensitivity` field was added, no Project Resume
operation ran, and no measured benchmark began.

The private Retry-3 evidence records:

- frozen executable `014076c429d47de83be4ca6543264082aa62633f`;
- exact stability of both approved pilots' canonical content;
- exact stability of Survivor Group Tracker's `HEAD`, index, refs, config, status, and
  pre-existing dirty worktree state;
- exact stability of AI Prompt Suite as a non-Git vault;
- four added files and no removed or changed files in Survivor Group Tracker's Git object
  store; and
- no accepted backup or post-classification baseline.

The four additions are valid loose Git blobs:

| Object ID | Type | Uncompressed size |
|---|---:|---:|
| `12c3129c23ca53fda835e648a3b30c8718d4c4ca` | blob | 42,131 bytes |
| `21da6a662399246674d0dbcb81c2786d3b1abe87` | blob | 44,605 bytes |
| `8af255248df63ad01fb06b3e54765a8a31495dc4` | blob | 76,016 bytes |
| `e0cae64bfe392ce9180ddc63ca6a13bb82570e70` | blob | 17,637 bytes |

An independent read-only `git fsck --full --unreachable --no-progress` check identifies
all four as unreachable. Their appearance is consistent with an external checkpoint,
snapshot, editor, or other background process, but the evidence does not prove which
process created them. No causal attribution is accepted.

## 2. Explicit architecture disposition

**ACCEPT REACHABILITY-BASED GIT STABILITY WITH RECORDED UNREACHABLE-OBJECT DRIFT.**

For the v0.4 pilot evidence boundary, a new unreachable loose object is not, by itself, a
canonical project mutation and does not invalidate an otherwise exact pilot baseline.
It is separately recorded as ambient object-store drift.

This is a refinement of evidence meaning, not a waiver of repository integrity:

- canonical Git state must remain exact;
- the reachable object graph must remain exact;
- Project Resume must remain read-only;
- all unexpected object-store activity must remain visible in evidence; and
- an object that becomes reachable, replaces existing bytes, or is attributable to the
  evaluated operation is a blocking mutation.

ADR-0015 and the frozen candidate remain unchanged. This disposition does not introduce
an unclassified-note default, alter authorization, or authorize implementation work.

## 3. Canonical Git state

The following form the canonical Git baseline for Survivor Group Tracker and must be
captured before and after each controlled classification, A10, or A12 window:

1. the `HEAD` file, symbolic target, and resolved object ID;
2. every ref in every namespace, including loose and packed refs, stash, notes, replace,
   bisect, and worktree refs where present;
3. all reflog bytes and resolved reflog object IDs;
4. index bytes and a deterministic `git ls-files --stage -z` digest;
5. repository and applicable worktree config bytes;
6. deterministic `git status --porcelain=v1 -z` bytes;
7. all canonical worktree file paths, exact bytes, lengths, and SHA-256 values;
8. the exact pre-existing dirty paths, staging state, and content hashes;
9. reachability-affecting metadata, including `shallow`, grafts, alternates, and replace
   refs where present; and
10. pack, pack-index, multi-pack-index, and commit-graph inventories and hashes.

Exact equality is required except for the eight Product Owner-approved classification
fields during the separately authorized classification window. Reflogs are included so
that a change followed by a reset cannot masquerade as stable final refs.

No reset, clean, checkout, stash, add, commit, prune, repack, garbage collection, reflog
expiry, or other Git mutation may be used to manufacture equality.

## 4. Reachable object-graph rule

The evidence procedure must produce a deterministic before/after reachable-object
manifest rooted in:

- `HEAD`;
- all refs in every namespace;
- all reflog tips;
- all index entries; and
- all reachability-affecting replacement, shallow, graft, and alternate configuration.

The manifest records object ID, Git object type, and uncompressed size. Its sorted digest
must remain exact. A read-only full object check must also confirm repository consistency.

An object is treated as ambient unreachable drift only when all of the following are true:

1. it was absent from the before object-store inventory and present afterward;
2. Git validates its object ID and content;
3. it is unreachable from every defined root after the window;
4. no canonical Git state, reachable-object entry, worktree byte, or approved delta was
   changed by its appearance;
5. no pre-existing loose or packed object was changed or removed;
6. no pack, index, multi-pack-index, alternates, or commit-graph file changed;
7. the Project Resume process transcript contains only its approved read-only Git
   allowlist and no object-writing Git or plumbing command; and
8. the new object is recorded privately with object ID, type, size, compressed-file
   SHA-256, first-observed window, and reachability result.

The evidence package must say `ambient_unreachable_object_drift`, not `no Git change`.
It must not claim a checkpoint or scheduler caused the drift unless separate process
evidence establishes that causation.

## 5. Blocking conditions

Stop the active operation and reject the resulting baseline if any of these occur:

- any change to canonical Git state outside the approved classification delta;
- any change to the reachable-object manifest;
- a new object becomes reachable from a ref, reflog, index, replacement, shallow, graft,
  or alternate root;
- any existing object is changed, deleted, replaced, packed, or repacked;
- any pack or object-store control file changes;
- an object-producing command is invoked by Jarvis, the classification procedure, the
  benchmark harness, or the A12 recovery procedure;
- reachability or object validity cannot be proven;
- pilot worktree bytes change outside the authorized delta;
- AI Prompt Suite gains a Git repository; or
- evidence collection cannot distinguish the operation's process tree from other
  writers sufficiently to prove the approved command boundary.

Do not delete, prune, quarantine, or otherwise modify newly observed unreachable objects.
They remain part of the private environmental record.

## 6. Backup and rollback correction

No further full copy of Survivor Group Tracker's entire `.git/objects` directory is
required for the eight-note classification retry. Repeating that multi-gigabyte copy adds
duration and exposure without improving rollback of the only authorized changes.

The revised pre-edit backup must contain:

- exact-byte copies of the eight approved notes;
- a complete deterministic canonical worktree inventory;
- the canonical Git-state evidence in Section 3;
- the reachable-object manifest and full object-store inventory;
- the existing unreachable-object inventory;
- exact proof of the pre-existing dirty and staging state;
- AI Prompt Suite's no-Git proof; and
- the approved private classification manifest.

The backup is accepted only after every backed-up approved note matches its source hash
and the before evidence is internally consistent. Rollback restores only the eight
approved note bytes and then revalidates the complete canonical and reachable baseline.
It must not restore, copy over, delete, or normalize `.git/objects`.

If organizational recovery policy independently requires a full repository backup, that
backup must be created outside this controlled classification evidence window and must not
be used as the gate that repeatedly triggers the observed ambient drift.

## 7. Retry-3 treatment

Retry-3 remains a stopped historical attempt because its procedure applied the older
whole-object-store equality rule and did not complete an accepted backup. It is not
retroactively converted into a successful classification baseline.

Its evidence is nevertheless valid for establishing this clarification:

- it proves no classification occurred;
- it proves the four added blobs were the only recorded source-inventory delta;
- it proves the recorded Git controls and pilot content stayed stable; and
- the independent reachability check confirms the four blobs are currently unreachable.

The four objects remain recorded in the next before inventory. Their mere continued
presence is not a new delta.

## 8. Required procedure correction before retry

Before classification is attempted again, the Chief of Staff must supersede the execution
procedure and private evidence schema so they:

1. implement Sections 3 through 6 exactly;
2. distinguish canonical state, reachable objects, pre-existing unreachable objects, and
   newly added unreachable objects;
3. capture reflogs and all ref namespaces, not only `show-ref`;
4. retain per-object evidence without exposing private object content;
5. preserve original line endings and encoding for every approved note;
6. create no Git object as part of evidence collection;
7. record all invoked commands and the controlled process tree;
8. stop on every blocking condition in Section 5; and
9. emit a clear success/failure result for source backup, classification delta,
   rollback readiness, and post-classification baseline separately.

The Product Owner's exact eight-note authorization remains valid in scope. It does not
need to be broadened. The Chief of Staff must confirm the same approved paths, pre-change
hashes, labels, operator, and current quiet-window conditions against the fresh baseline
before execution. Any mismatch requires renewed Product Owner approval.

`05-chief-of-staff-pilot-classification-execution-stop.md` remains valid history and is
superseded only as to the rule that every newly created unreachable loose object
necessarily invalidates canonical Git stability.

## 9. Effect on A10 and A12

**A10 remains paused.** It may resume only after:

- classification completes under the corrected procedure;
- a valid post-classification baseline is accepted;
- the onboarding and A12 documentation correction required by the prior CTO disposition
  is published; and
- a renewed CTO acknowledgment pins the evidence and authorizes A10.

**A12 remains paused.** Its independent procedure must use the same canonical/reachable
integrity definition and the accepted post-classification baseline. A12 must report any
ambient unreachable-object drift separately. It must fail if Jarvis creates an object or
if any canonical or reachable state changes.

The appearance of unreachable objects may no longer be reported as a canonical project
mutation when all Section 4 conditions pass. It also may not be omitted from A10/A12
evidence.

## 10. Frozen-candidate and architecture assessment

Candidate `014076c429d47de83be4ca6543264082aa62633f` remains frozen. No candidate, test,
benchmark, ADR, pilot, classification, or implementation change is required or authorized
by this disposition.

The clarification preserves the intended trust boundary:

- authorization still precedes discovery and selection;
- unclassified notes remain excluded;
- Jarvis remains read-only;
- canonical project and Git state remain exact;
- reachable history cannot change silently; and
- ambient object-store behavior is visible without being mislabeled as canonical project
  work.

## 11. Explicit exclusions

This disposition does not authorize:

- classification or any pilot write;
- a full backup attempt under the superseded equality rule;
- A10, A12, QA, architecture clearance, merge, push, or release;
- candidate, implementation, test, benchmark, ADR, or documentation changes other than
  the already-required onboarding/evidence procedure correction;
- Git staging, commit, reset, stash, clean, prune, repack, or garbage collection;
- deletion or inspection of private object contents beyond integrity/type/size checks;
- attribution of the four objects to a specific background process without proof;
- implicit sensitivity defaults; or
- network, provider, credential, telemetry, live GitHub, or v0.5-expansion work.

## 12. Required next action

The Chief of Staff must update and validate the private classification execution and
evidence procedure against this boundary, then coordinate one new controlled retry. The
retry begins from a fresh exact baseline that includes the four currently observed
unreachable blobs as pre-existing environmental state.

Stop again if canonical or reachable state changes, if an existing object is altered or
removed, or if a new loose object cannot satisfy every ambient-drift condition.

## Exit statement

**GIT INTEGRITY BOUNDARY CLARIFIED; REACHABLE AND CANONICAL STATE REMAIN FAIL-CLOSED.**

New, valid, persistently unreachable loose objects may be recorded as ambient object-store
drift rather than canonical project mutation. They are never silently waived. Retry-3
remains stopped, the frozen candidate remains unchanged, no classification has occurred,
and A10/A12 remain paused pending a corrected procedure, successful owner-authorized
classification, accepted post-classification baseline, documentation correction, and
renewed CTO activation.
