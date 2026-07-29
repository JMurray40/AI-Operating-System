# Project Resume Installation, Onboarding, and Recovery

This runbook documents executable candidate
`014076c429d47de83be4ca6543264082aa62633f`. Documentation commits on top of that
candidate do not change its executable identity.

Project Resume is an offline, read-only command. It does not classify notes, edit a vault,
repair canonical Markdown, initialize or modify Git, or persist an index.

## Supported clean environment

The supported A12 reference path is a clean Windows environment with:

- 64-bit Python 3.10 or newer (Python 3.12 recommended);
- PowerShell;
- Git available only when local repository activity is being tested; and
- a clean checkout of this repository at the documentation commit under review.

Runtime installation may obtain the declared PyYAML dependency from the configured Python
package source. Runtime use itself requires no network, provider, API key, or credential.
Do not set `PYTHONPATH`; that is a developer convenience, not the supported installed path.

## Clean installation

From the repository root in PowerShell:

```powershell
py -3.12 -m venv .venv-a12
.\.venv-a12\Scripts\Activate.ps1
python -m pip install .
```

If Python 3.10 or 3.11 is the installed supported interpreter, replace `-3.12` with that
version. Do not install the development extra for the non-author packaging review.

### Installed-command verification

```powershell
python -m pip show jarvis-core
jarvis --help
jarvis resume --help
jarvis resume-doctor --help
```

All four commands must exit successfully. `jarvis --help` must list `resume` and
`resume-doctor`. A command that works only with `PYTHONPATH`, an editable install, or an
undeclared dependency is a packaging failure.

## Deterministic fixture rerun

Run from the repository root:

```powershell
jarvis resume "FileOrbit" --path tests/fixtures/fileorbit --format json `
  --as-of 2026-07-28T00:00:00Z > $env:TEMP\jarvis-resume-first.json
jarvis resume "FileOrbit" --path tests/fixtures/fileorbit --format json `
  --as-of 2026-07-28T00:00:00Z > $env:TEMP\jarvis-resume-second.json
Get-FileHash -Algorithm SHA256 $env:TEMP\jarvis-resume-first.json
Get-FileHash -Algorithm SHA256 $env:TEMP\jarvis-resume-second.json
```

Both invocations must have the same exit status and the two SHA-256 values must match.
The output files are reviewer-owned evidence outside the fixture, not product output.
Delete them after their hashes and redacted result are recorded.

Before and after the rerun, inventory and hash `tests/fixtures/fileorbit`. No fixture byte,
path, or timestamp may change.

## Uninstall and reinstall

With the clean environment active:

```powershell
python -m pip uninstall -y jarvis-core
jarvis --help
```

The second command must no longer resolve or must fail because Jarvis is not installed.
Then reinstall and repeat installed-command verification and the deterministic fixture
rerun:

```powershell
python -m pip install .
jarvis --help
jarvis resume-doctor --path tests/fixtures/fileorbit --format json
```

Record the interpreter version, package version, install source commit, commands, exit
statuses, and changed paths inside the isolated environment. Uninstall must not alter a
vault, fixture, pilot, or repository.

## Sensitivity-classification onboarding

Every note eligible for Project Resume must carry an explicit recognized `sensitivity`
frontmatter value:

```text
public | internal | private | restricted
```

Missing, malformed, or unknown sensitivity is excluded by authorization before project
selection, retrieval, graph expansion, claims, citations, conflicts, errors, and trace.
If the canonical project note is excluded, an otherwise exact selector may return
`not_found`. That result does not prove that no similarly named project exists; it means no
authorized project matched, and excluded candidates are not disclosed.

There is no implicit “unclassified means internal” rule. Jarvis never chooses or assigns a
classification and never edits canonical notes. Classification is a separate, explicit
data-owner decision completed before the operational input baseline.

### Owner-controlled procedure

1. **Inventory:** Outside Jarvis, create a private ignored inventory containing each
   candidate note's relative path, exact-byte SHA-256, length, current sensitivity state,
   canonical-project status, and reason it may be needed. Do not copy note content into
   committed evidence.
2. **Approval:** The Product Owner reviews notes individually and records the exact path,
   pre-change hash, recognized label, reason, operator, decision identity, and rollback
   trigger. Folder or project approval never propagates to other notes.
3. **Backup:** Create byte-exact backups of only the approved notes outside the vault and
   software repository. Verify every backup hash. Capture complete canonical worktree and
   Git-integrity evidence as described below; do not copy the entire Git object store as
   the classification gate.
4. **Apply:** The named operator adds only the approved `sensitivity` fields with a
   byte-preserving method. Preserve encoding, line endings, and all unrelated metadata and
   content. Jarvis does not perform this step.
5. **Validate:** Prove only approved files changed and each file equals its expected
   sensitivity-only result. Validate frontmatter/schema, exact post-change hashes,
   authorization counts, exact project selection, Git integrity, and continued no-Git
   status for non-Git vaults.
6. **Rollback:** On any mismatch, restore only approved note bytes from the verified
   backup. Recompute the full inventory and Git evidence. Never reset, clean, stash, prune,
   repack, or overwrite unrelated concurrent work.
7. **Baseline:** After successful classification, issue a versioned private baseline
   binding the executable SHA, owner decision, pre/post inventory digests, approved-note
   hashes, backup/rollback status, authorized/excluded aggregate counts, Git state,
   no-Git proof where applicable, reference profile, reviewer, and timestamp.

Private paths, labels, note names/content, Git subjects/authors/remotes, credentials, and
raw errors remain outside committed evidence.

## `resume-doctor`

Run diagnostics before a live-vault Project Resume operation:

```powershell
jarvis resume-doctor --path C:\path\to\vault
jarvis resume-doctor --path C:\path\to\vault --format json
jarvis resume-doctor --path C:\path\to\vault `
  --repository-root C:\path\to\approved-repository --format json
```

The doctor checks the runtime, vault readability, in-memory derived-state rebuild, Git
availability/version, and an optional approved repository root. It uses redacted
diagnostics: `0` means healthy, `2` means warnings or an unavailable optional capability,
and `1` means a failed required check.

Troubleshooting:

| Symptom | Safe response |
|---|---|
| `jarvis` is not recognized | Activate the installation environment and repeat installed-command verification. Do not add `PYTHONPATH`. |
| Invalid or unreadable vault | Correct the command-line path or permissions outside Jarvis; do not ask Jarvis to repair it. |
| `not_found` for an expected project | Confirm the exact selector and have the owner verify explicit sensitivity onboarding. Do not broaden scope or reveal excluded candidates. |
| Ambiguous identity | Correct canonical IDs/aliases only through a separately authorized owner workflow; Jarvis chooses none. |
| Git unavailable or repository rejected | Continue without repository activity when safe, or correct the separately granted root. Do not weaken root confinement. |
| Warning or incomplete coverage | Read limitations and coverage fields; do not reinterpret incomplete evidence as supported. |
| Raw private detail appears in diagnostics | Stop, retain only redacted evidence, and report a security defect. |

## Missing or corrupt derived state

Project Resume has no persisted index. The authorized view, lexical index, relationship
graph, and briefing are rebuilt in memory from current canonical bytes on every invocation.
Therefore:

1. stop the affected invocation;
2. preserve canonical before hashes;
3. remove or quarantine only reviewer-created temporary output outside the vault;
4. run `jarvis resume-doctor --path <vault> --format json`;
5. repeat the deterministic command with an explicit `--as-of`;
6. verify canonical and Git state stayed exact.

Do not rewrite frontmatter, add sensitivity, repair links, normalize Markdown, restore from
an inferred snapshot, initialize Git, or modify any canonical source as “recovery.” A
doctor failure is evidence to report, not permission to repair the vault.

## Reachability-based Git integrity

For an approved Git-enabled pilot, before/after evidence must show exact equality of:

- `HEAD`, its symbolic target, and resolved object ID;
- every ref namespace, packed refs, and every reflog;
- index bytes and deterministic staged entries;
- repository/worktree config;
- deterministic status and pre-existing dirty paths/content hashes;
- canonical worktree paths and exact bytes;
- reachability-affecting shallow, graft, alternate, and replace state;
- pack, pack-index, multi-pack-index, and commit-graph inventories; and
- the reachable-object manifest rooted in HEAD, all refs, reflog tips, index entries, and
  all reachability-affecting state.

The sorted reachable manifest records object ID, type, and uncompressed size and must
remain exact. No reset, clean, stash, add, commit, prune, repack, garbage collection, or
reflog expiry may be used to restore equality.

A newly created loose object may be reported separately as
`ambient_unreachable_object_drift` only when it is valid, remains unreachable from every
defined root, no existing object or object-control file changed, canonical and reachable
state stayed exact, and the Jarvis process transcript contains only the fixed read-only
Git allowlist. Record object ID, type, size, compressed-file hash, observation window, and
reachability privately. Do not delete it and do not claim a checkpoint or background
process caused it without process evidence.

Any reachable change, invalid object, existing-object change/removal, pack/control change,
Jarvis-attributable object creation, or unprovable reachability fails the operation.
“Unreachable drift” is never silently reported as “no Git change.”

## A12 non-author packaging and recovery review

The independent reviewer must use a clean supported environment and only this published
runbook:

1. Pin the documentation commit and verify it declares executable `014076c`.
2. Record the clean environment, interpreter, platform, checkout status, and artifact
   hashes without private values.
3. Snapshot fixture/pilot canonical state, Git integrity, no-Git state, and the approved
   private evidence destination.
4. Perform clean installation without editable mode, `PYTHONPATH`, or author help.
5. Run installed help, deterministic fixture resume, healthy doctor, invalid-path,
   no-Git, optional approved-Git, partial/degraded, and redacted-diagnostic cases.
6. Exercise missing/corrupt derived-state recovery without changing canonical sources.
7. Uninstall, prove the command is removed, reinstall, and repeat the deterministic
   fixture result.
8. Compare all before/after inventories. Report valid unreachable drift separately under
   the rules above.
9. Record each command, expected/actual result, exit status, created/changed path,
   cleanup, limitation, and disposition.

A step that cannot run is `Unavailable`, not `Pass`. The reviewer must not fix
documentation, implementation, pilots, or evidence during A12.

## Pilot and engineering-handoff evidence

The private pilot package must bind:

- executable `014076c429d47de83be4ca6543264082aa62633f`;
- exact documentation commit;
- owner decision and accepted private baseline/evidence digests;
- reference machine profile and supported-environment facts;
- before/after canonical and Git-integrity digests;
- commands, completion markers, timings, exit statuses, and run counts;
- aggregate authorized/excluded counts and safe result status;
- backup and rollback readiness;
- A10/A12 reviewer identities and dispositions; and
- every skip, limitation, environmental interference, or separately reported
  unreachable-object drift.

The public engineering handoff records only the executable and documentation commits,
accepted private evidence digests, aggregate non-sensitive results, validation commands,
and explicit gate disposition. It must not expose private paths, classifications, note
names/content, Git subjects/authors/remotes, raw errors, credentials, or machine secrets.

## Gate boundary

These instructions do not activate A10 or A12. They become inputs to a renewed CTO
acknowledgment, which must pin this documentation commit, executable `014076c`, the
accepted private evidence digests from Handoff 07, the post-classification baseline, the
reference profile, and the exact authorized review scopes.
