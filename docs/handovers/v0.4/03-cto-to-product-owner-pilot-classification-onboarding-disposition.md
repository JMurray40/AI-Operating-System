# CTO to Product Owner — Pilot Classification and Onboarding Disposition

| Field | Value |
|---|---|
| Sender | Chief Architect / CTO |
| Receiver | Product Owner and Chief of Staff |
| Milestone | v0.4 — Read-only Project Resume CLI Pilot |
| Date | 2026-07-29 |
| Status | **A10/A12 paused; explicit pilot classification onboarding required** |
| Frozen executable | `014076c429d47de83be4ca6543264082aa62633f` |
| Reviewed finding | Private `data/v0.4-evidence/014076c/a10-preflight-finding.md` |
| Affected pilots | Survivor Group Tracker; AI Prompt Suite |
| Architecture decision | Preserve ADR-0015 fail-closed authorization |

## 1. Executive finding

The preflight result is architecturally correct:

- Survivor Group Tracker contains 45 discovered notes, including one exact project note,
  but zero notes declare a recognized sensitivity.
- AI Prompt Suite contains 33 discovered notes, including one exact project note, but zero
  notes declare a recognized sensitivity.
- The explicit local authorization scope consequently authorizes zero notes in each vault.
- Project identity resolution then returns `not_found` because ADR-0018 operates only over
  the authorized view.

Authorization is excluding unknown material before project selection exactly as ADR-0015
requires. This is not evidence that the selector or candidate is defective.

The gap is in the real-vault onboarding contract: the approved pilots were checked for an
exact project note, but not for the mandatory sensitivity classification required by the
released trust boundary.

## 2. Explicit architecture disposition

**PRESERVE ADR-0015; REQUIRE PRODUCT OWNER-CONTROLLED CLASSIFICATION ONBOARDING.**

ADR-0015 remains unchanged. ADR-0018 remains unchanged. Unknown, missing, malformed, or
unrecognized sensitivity continues to fail closed before project selection, candidate
generation, graph expansion, claims, citations, conflicts, errors, and trace.

The following are rejected:

- an implicit “unclassified means internal” rule;
- a hardcoded local-vault default;
- a CLI flag that silently assigns trust to missing labels;
- post-retrieval inclusion of unclassified notes;
- timing the `not_found` path as successful A10 briefing evidence; and
- changing the frozen candidate solely to make unclassified pilots pass.

Real-vault use requires a separate onboarding act in which the Product Owner explicitly
classifies the canonical notes that may enter the request scope.

## 3. Why the authorization contract is not revised

The alternative authorization-contract change would turn absence of classification into
an authorization decision. Even if limited to local notes, it would:

- make unknown material trusted through context rather than through explicit policy;
- weaken the same boundary Project Resume is intended to validate;
- create different security meaning for identical note bytes based on entry point;
- allow an unclassified project to influence identity and ambiguity;
- require a new ADR, candidate change, regression review, and refreeze; and
- obscure whether the Product Owner actually intended a note to be readable.

The correct distinction is:

- **Jarvis runtime:** read-only and fail closed on unknown sensitivity.
- **Owner onboarding:** an explicit, auditable canonical-data decision performed before
  the runtime baseline is established.

## 4. Minimum notes requiring classification

Classification is not an all-vault bulk default. Only explicitly reviewed notes may become
eligible.

### 4.1 Survivor Group Tracker

The absolute minimum is:

1. the exact canonical `type: project` note for Survivor Group Tracker; and
2. every note intended to support a material A10 briefing claim, including any selected
   note in these categories:
   - objective/current authoritative state;
   - priority, milestone, next action, task, or open question;
   - accepted decision or supersession evidence;
   - recent session;
   - resource or repository reference; and
   - conflict/staleness evidence that must be shown.

Authorized local Git records do not remove the need to classify the canonical project
note. Git activity is a separate request-scoped capability and cannot establish project
identity on its own.

The remaining discovered notes may stay unclassified and excluded if the Product Owner
does not approve them for this pilot. They must not influence the briefing indirectly.

### 4.2 AI Prompt Suite

The absolute minimum is:

1. the exact canonical `type: project` note for AI Prompt Suite; and
2. each note the Product Owner explicitly approves as material support for the locally
   available briefing sections listed above.

Because current-state text is sparse, the Product Owner is not required to invent or add
new project content. Classifying only the canonical project note is sufficient to test
exact project selection and a valid partial/missing-context briefing if that note contains
the only approved evidence. Existing supporting notes should be classified only when Jason
reviews and intentionally admits them.

No Git classification or repository creation is required or permitted for AI Prompt
Suite. Its repository-activity outcome remains unavailable.

### 4.3 Selection rule for both pilots

The classification inventory must identify the proposed minimum set from existing
relationships and metadata, but it does not make the decision. Jason chooses each note and
one recognized label:

```text
public | internal | private | restricted
```

No tool may infer a label from path, title, type, repository location, current scope, or
neighbor classification.

## 5. Read-only classification inventory

Before any canonical note changes, produce a private read-only inventory for each pilot.
The inventory is an onboarding-administration artifact, not a Project Resume query or
trace.

For every discovered Markdown note, record privately:

- relative path;
- stable ID and type where present;
- display title where present;
- exact-byte SHA-256;
- byte length;
- current sensitivity field/value or `missing`;
- whether it is the canonical project note;
- deterministic relationship to the project, if any;
- proposed reason for inclusion in the minimum set; and
- proposed label left blank until Product Owner review.

The inventory may read only the metadata and relationship information necessary to prepare
the decision. It must not write, normalize, reserialize, repair, or classify any note.

Store it only under an explicitly approved private, ignored, non-vault destination. Do not
commit private paths, titles, task text, note content, or classifications.

## 6. Product Owner review and approval

Jason reviews the private inventory note by note.

Approval must record:

- pilot identity;
- pre-classification root inventory digest;
- exact relative path and pre-change SHA-256 for each approved note;
- chosen recognized sensitivity for each note;
- reason the note is needed for the pilot;
- notes explicitly left unclassified;
- approval timestamp and decision identifier;
- approved editor/operator;
- backup location/digest;
- rollback trigger; and
- confirmation that classification is a canonical owner decision, not a Jarvis runtime
  action.

Approval of a project does not approve all notes in its folder. Approval of one note's
label does not propagate to links or descendants.

The current Product Owner pilot substitution decision does not authorize these writes: it
explicitly excludes writes to either pilot. Jason must issue a narrowly scoped superseding
classification authorization before editing begins.

## 7. Manual versus migration execution

For these two pilots, classification must be **manual**:

- only Jason or his explicitly designated operator edits the approved files;
- only the `sensitivity` frontmatter field is added or changed;
- each value must exactly match the approved per-note decision;
- Jarvis is not used to perform the edit;
- no broad formatter, schema migration, link repair, timestamp updater, or content rewrite
  is run; and
- no unapproved file is changed.

A bulk or scripted migration is not authorized by this disposition. If later requested, it
requires a separate Product Owner authorization, exact migration specification, dry-run
manifest, code review, backup/rollback plan, and its own before/after evidence. It remains
outside the frozen Project Resume runtime.

## 8. Required backup and pre-change evidence

Before manual classification:

1. stop all Jarvis evaluation against the pilot;
2. verify the private evidence destination is ignored and outside both pilot roots;
3. capture a deterministic recursive inventory of every pilot file with relative path,
   byte length, and SHA-256;
4. compute and record a root inventory digest;
5. create an exact-byte backup outside the pilot root and repository;
6. inventory the backup and prove its root digest equals the source digest;
7. record filesystem and environment facts needed to reproduce the comparison;
8. preserve the private Product Owner approval manifest.

For Survivor Group Tracker additionally record:

- `HEAD`;
- deterministic `git status --porcelain=v1 -z`;
- refs and packed-refs bytes/digests;
- repository config bytes/digest;
- index bytes/digest;
- material Git control/object inventory; and
- the exact pre-existing dirty paths/content hashes.

The dirty state must not be cleaned, reset, stashed, staged, committed, or normalized.

For AI Prompt Suite, record and retain proof that no Git repository exists; do not create
one.

## 9. Post-change validation

After manual classification and before any Project Resume execution:

1. repeat the complete file inventory and root digest;
2. prove that only Product Owner-approved files changed;
3. prove each changed file's only semantic change is the approved `sensitivity` field;
4. record each post-change exact-byte SHA-256;
5. validate YAML/frontmatter syntax and the note schema;
6. confirm every added value is one of the four recognized labels;
7. confirm IDs, types, titles, dates, content, links, line endings, encoding, and unrelated
   metadata were not changed;
8. rerun read-only repository discovery and policy validation;
9. confirm the canonical project note is authorized under the intended explicit scope;
10. record authorized and excluded aggregate counts without treating exclusions as errors;
11. confirm no measured A10 benchmark has yet run.

For Survivor Group Tracker, repeat all Git-control and dirty-state evidence. The delta must
equal only the approved manual classification edits layered on the preserved pre-existing
dirty state. No index, ref, config, object, or staging change is acceptable.

For AI Prompt Suite, reconfirm that it remains a non-Git vault.

## 10. Rollback

Rollback uses the verified exact-byte backup, not a reverse formatter or generated patch.

Rollback procedure:

1. stop evaluation;
2. restore only the approved changed files from the backup;
3. remove no pre-existing file and create no new canonical file;
4. recompute the full inventory/root digest;
5. require exact equality with the pre-classification digest;
6. for Survivor Group Tracker, require exact equality with pre-classification Git control,
   status, and dirty-content evidence;
7. for AI Prompt Suite, reconfirm no Git repository was created;
8. record rollback completion and reason.

Any mismatch stops onboarding and requires owner review before retry.

## 11. Establishing the post-classification pilot baseline

Successful classification creates a new operational input baseline; it does not rewrite
the earlier evidence.

The new private baseline manifest must include:

- frozen executable SHA `014076c429d47de83be4ca6543264082aa62633f`;
- Product Owner classification decision ID;
- original preflight finding identity/digest;
- pre-classification and post-classification root inventory digests;
- exact approved-note pre/post hashes and labels;
- backup digest and rollback verification status;
- post-classification authorized/excluded aggregate counts;
- Survivor Group Tracker post-classification Git state and control digests;
- AI Prompt Suite no-Git proof;
- approved reference profile;
- evidence destination and ignore proof;
- operator/reviewer identities and timestamps.

A10 and A12 before/after comparisons must start from this post-classification baseline.
They must not use the original pre-classification root digest as the immediate “before”
state, and they must not erase the lineage between the two.

The operational `pilot-inputs.json` must be superseded by a versioned post-classification
manifest or companion baseline artifact. The original remains retained as history.

## 12. Frozen-candidate assessment

Candidate `014076c429d47de83be4ca6543264082aa62633f` may remain the frozen executable.

No executable change is required because:

- fail-closed behavior is correct;
- exact identity behavior is correct;
- classification is a canonical owner-controlled prerequisite outside Jarvis runtime;
- the candidate must continue excluding notes Jason did not classify; and
- A10 can resume only after the explicit input baseline is valid.

If the explicitly classified canonical project notes still return `not_found`, or if
Project Resume cannot produce a contract-valid partial/complete briefing, stop and return
the result as a candidate finding. Do not broaden policy or add classifications to make
the test pass.

Documentation/evidence changes may be committed separately and bound to the frozen
executable. They do not change the executable SHA. The engineering handoff must identify
both the executable and the documentation/evidence commit.

## 13. Required onboarding documentation correction

Before A10 or A12 resumes, publish a candidate-bound documentation addendum that corrects
the missed onboarding prerequisite.

At minimum update or add:

- Project Resume installation/onboarding instructions;
- CLI diagnostics/troubleshooting;
- pilot evaluation procedure;
- packaging/recovery procedure used by A12; and
- engineering handoff evidence requirements.

The documentation must state:

1. every eligible note requires an explicit recognized sensitivity;
2. missing/unknown sensitivity is excluded before project selection;
3. `not_found` may mean no authorized project matches and must not disclose excluded
   candidates;
4. Jarvis does not assign classifications or modify canonical notes;
5. classification is a Product Owner/data-owner action completed before the runtime
   baseline;
6. no implicit “unclassified means internal” behavior exists;
7. inventory, approval, backup, validation, rollback, and post-classification baseline
   steps;
8. sparse evidence may correctly yield partial/incomplete coverage;
9. A12 must treat onboarding writes as pre-baseline owner changes, not Jarvis writes;
10. A12 must independently verify that runtime operations preserve the post-classification
    baseline;
11. recovery must never add classifications or repair canonical sources; and
12. private manifests/paths/classifications remain outside committed evidence.

If packaging artifacts embed documentation, publish a docs-only candidate/evidence
identity and ensure the independent reviewer uses the corrected instructions.

## 14. Superseding acknowledgments and decisions

The following gate state changes immediately:

1. `02-cto-pilot-and-reference-profile-acknowledgment.md` is superseded with respect to its
   A10 and A12 execution authorization. Its pilot substitution and current-PC profile
   acknowledgment remain historically valid.
2. `02-product-owner-pilot-and-reference-profile-decision.md` remains valid for pilot
   identities and reference profile, but its prohibition on pilot writes means it does not
   authorize classification. Jason must issue a narrow superseding/additive Product Owner
   classification authorization.
3. The current private `pilot-inputs.json` remains historical pre-classification evidence
   and cannot serve as the final A10/A12 input baseline.

Before A10 resumes, required new artifacts are:

- Product Owner classification authorization;
- private approved classification manifest;
- verified backup and pre/post/rollback evidence;
- post-classification pilot baseline manifest;
- corrected onboarding/A12 documentation; and
- a new CTO acknowledgment pinning those artifacts and reauthorizing A10.

Before A12 resumes, the same package plus candidate packaging/recovery activation
requirements and an independent A12 prompt pinned to the corrected documentation are
required.

## 15. A10 and A12 status

**A10 is paused.** No `not_found` latency may be counted as successful briefing performance.
No warm-up or measured run should begin until the post-classification baseline and renewed
CTO acknowledgment exist.

**A12 is paused.** The current packaging/onboarding contract is incomplete for real-vault
use. Independent A12 must use corrected published instructions and the post-classification
baseline; it must not perform classification itself.

The private preflight finding remains valid gate evidence and must be referenced in the
eventual engineering handoff.

## 16. Explicit exclusions

This disposition does not authorize:

- classification or any pilot write;
- a classification migration;
- candidate, implementation, test, or ADR changes;
- implicit sensitivity defaults;
- A10, A12, QA, architecture clearance, merge, push, or release;
- Git staging/commit/reset/stash/clean in Survivor Group Tracker;
- Git initialization in AI Prompt Suite;
- fabrication of missing project context;
- GitHub, network, provider, credential, or remote access; or
- v0.5 work.

## 17. Required next actions

### Product Owner

1. Review the private read-only inventories.
2. Select exact notes and explicit labels.
3. Approve backup, operator, execution, validation, and rollback boundaries.
4. Issue a narrow classification authorization superseding the conflicting no-write
   restriction for only the approved edits.

### Chief of Staff

1. Keep A10/A12 paused.
2. Validate the classification authorization and evidence package.
3. Coordinate manual owner-approved edits outside Jarvis.
4. Route corrected onboarding documentation for review.
5. Request renewed CTO acknowledgment after the post-classification baseline is complete.

### Principal Engineer

Retain the preflight evidence and frozen candidate. Do not benchmark `not_found`, change
policy, classify notes, edit pilots, or resume A10 without renewed authorization.

### Independent A12 reviewer

Do not begin A12 until the corrected documentation, post-classification baseline, and
renewed CTO activation are pinned.

## Exit statement

**ARCHITECTURE PRESERVED; PILOT CLASSIFICATION ONBOARDING REQUIRED.**

ADR-0015 and ADR-0018 remain unchanged. Candidate `014076c` may remain frozen. The blocker
is an explicit owner-controlled data-onboarding prerequisite and its missing documentation,
not permission to weaken authorization. A10 and A12 remain paused until the superseding
classification decision, reversible evidence, post-classification baseline, documentation
correction, and renewed CTO acknowledgments are complete.
