# Prepared Prompt — Packaging, Recovery, Privacy, and Integrity Review

**Inactive until:** a frozen candidate and its installation/recovery documentation exist.

Act as a release-operations reviewer. Independently verify A7 and A12 plus the final CTO
brief's packaging, diagnostics, recovery, privacy, and unchanged-source requirements.

Use a clean supported Windows environment and exact candidate `<CANDIDATE_SHA>`. Follow
only published documentation as a non-author would. Test installation, `jarvis --help`,
fixture resume, both authorized pilot commands, no-Git degradation, authorized local Git,
invalid vault/root diagnostics, missing/corrupt derived-state rebuild, uninstall/reinstall,
and stdout-only product behavior.

Capture before/after vault and Git inventories, hashes, timestamps where required, status,
HEAD, refs, config, index, packed refs, and derived-state location. Confirm private
evidence stays in the approved ignored non-vault destination and committed evidence is
redacted.

Do not repair documentation or implementation during the review. Do not write canonical
sources, access network/GitHub, expose private content, merge, push, or release.

Append evidence to the QA handoff or create the exact artifact assigned by the active CTO
disposition. Report reproducible failures, environmental skips, and whether A7/A12 pass.

## Activation block

```text
candidate_sha: <CTO_CLEARED_FULL_SHA>
detached_worktree: <ABSOLUTE_PATH>
installation_document: <PATH>
project_resume_document: <PATH>
packaging_evidence: <PATH>
pilot_private_root: <USER_APPROVED_IGNORED_PATH>
qa_handoff: docs/handovers/v0.4/04-quality-to-product-owner-release-review.md
```

## Required procedure

1. Snapshot candidate, vault, approved repository, and evidence-destination state.
2. Install from the documented supported path without developer-only environment fixes.
3. Run help, fixture, both pilot, no-Git, granted-Git, invalid-input, and degraded cases.
4. Exercise missing and corrupt derived-state recovery exactly as documented.
5. Uninstall/reinstall and repeat a deterministic fixture result.
6. Compare every before/after inventory and repository-control object.
7. Verify stdout/stderr, exit codes, temporary files, caches, private artifacts, and
   committed redacted evidence.
8. Have a non-author follow the instructions without undocumented assistance.

For each step record command, environment, expected result, actual result, exit status,
created/changed paths, cleanup, and disposition. A test that cannot run is `Unavailable`,
not `Pass`.

## Failure and stop rules

Any canonical-source mutation, Git mutation, undocumented setup dependency, private-data
leak, recovery write to the vault, misleading no-Git behavior, or non-author failure is
release evidence. Do not repair it. Preserve reproducible diagnostics without private
content and return it to QA/engineering through the active gate.

Do not commit private artifacts. Stop after producing the assigned evidence report.
