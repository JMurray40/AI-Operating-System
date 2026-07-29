# v0.4 Project Resume — Independent Packaging and Recovery Evidence

| Field | Value |
|---|---|
| Reviewer | Independent Codex non-author reviewer |
| Date | 2026-07-29 |
| Executable | `014076c429d47de83be4ca6543264082aa62633f` |
| Documentation | `10ebf331449ad11dd0cb4e5e40ffd50d3f531bd9` |
| Reference profile | Product Owner-approved current Windows PC |
| Disposition | **Blocked before pilot exposure** |

## Result

The documented preferred Python 3.12 runtime was unavailable. The runbook supports Python
3.10 or newer, so the reviewer created a clean isolated Python 3.14.4 environment.

The environment initially contained pip 26.0.1 but neither PyYAML nor setuptools. Under
the CTO's narrow installation-only exception, the reviewer acquired only the declared
PyYAML runtime dependency from the configured public package source:

```text
Package: PyYAML 6.0.3
Wheel SHA-256: 4a2e8cebe2ff6ab7d1050ecd59c25d4c8bd7e6f400f5f82b96557ac0abafd0ac
```

The wheel installed successfully offline with dependency resolution disabled.

Private A12 evidence SHA-256:

```text
f39e277a3aba8cc99e62cb026f2f6500f3c2fd02a6c00a213c665448c1ca9b92
```

The subsequent local candidate installation used no package index, dependencies, build
isolation, editable mode, or `PYTHONPATH`. It failed because the clean environment did not
contain the declared setuptools build backend.

Safe failure category:

```text
build_backend_unavailable: setuptools.build_meta could not be imported
```

The CTO authorization permitted acquisition of PyYAML only and expressly required the
reviewer to stop if another download was needed. No setuptools download, shared-environment
copy, editable installation, undocumented workaround, or author assistance was used.

## Scope reached

| A12 step | Result |
|---|---|
| Exact executable/documentation checkout | Pass |
| Isolated supported Python environment | Pass using supported Python 3.14.4; preferred 3.12 unavailable |
| Authorized PyYAML acquisition and offline installation | Pass |
| Non-editable local candidate installation | **Blocked** |
| Installed command/help verification | Blocked |
| Deterministic fixture rerun | Blocked |
| Pilot briefings | Blocked |
| Diagnostics and recovery | Blocked |
| Uninstall/reinstall | Blocked |

Neither pilot path, content, Git repository, classification, or private evidence value was
exposed to the A12 runtime. Network-denial verification was not reached because candidate
installation failed first. No runtime or pilot network activity occurred.

## Required correction

Engineering and the CTO must provide one authorized clean-environment installation path:

1. supply a prebuilt, integrity-bound candidate wheel and document installing it without
   a build backend; or
2. explicitly authorize and integrity-bind acquisition of the declared
   `setuptools>=68` build dependency in addition to PyYAML.

The independent reviewer must not choose between these alternatives or modify the
candidate/runbook during review. A12 requires renewed exact-scope authorization after the
correction.

## Disposition

**A12 BLOCKED — PACKAGING/BUILD-BACKEND PREREQUISITE MISSING.**

This is not an architecture disposition, QA result, merge decision, or release decision.
A10 remains a separately authorized Principal Engineering activity.

---

## Superseding A12 revision — verified wheel path

| Field | Value |
|---|---|
| Reviewer | Independent Codex non-author reviewer |
| Date | 2026-07-29 |
| Executable | `014076c429d47de83be4ca6543264082aa62633f` |
| Documentation | `79a4999a9d8d6f0ff4a6daf47e758e8dbffc85bb` |
| Candidate wheel SHA-256 | `7253e0b938433d7e393d186a3006c971b576381f6518fe986154d162fe0b3662` |
| PyYAML wheel SHA-256 | `4a2e8cebe2ff6ab7d1050ecd59c25d4c8bd7e6f400f5f82b96557ac0abafd0ac` |
| Disposition | **Refactor first** |

The renewed wheel-only procedure passed installation, command discovery, deterministic
fixture execution, diagnostics, fail-closed invalid-path handling, uninstall, command-removal
proof, and reinstall from the same verified wheel. PyYAML was installed from the retained
verified wheel. Candidate installation and reinstallation used `--no-index --no-deps`;
setuptools remained absent.

The deterministic fixture produced 11,182 stdout bytes with SHA-256
`8e5136c86a61ba877c5e0af2996b7d798ca0888c3fc47b877c019ecc322953e5`
before and after reinstall. Its doctor passed.

Network denial was verified before pilot exposure using the exact isolated interpreter:
an outbound HTTPS connection failed with Windows error 10051. The subsequent pilot runs
were executed inside that network-restricted sandbox.

### Pilot and integrity results

- Both classified pilots produced bounded partial briefings without canonical writes.
- The no-Git pilot degraded safely when repository activity was requested.
- Survivor Group Tracker's repository-activity grant could not be exercised. The candidate
  launches Git with system and global configuration disabled; under the independent Windows
  sandbox identity, Git's ownership safety check rejects the repository. The adapter redacts
  this as `unavailable_not_a_repository`, and `resume-doctor` fails that check.
- No hidden `safe.directory`, ownership, repository-config, or candidate workaround was used.

Pre/post hashes matched exactly:

| Boundary | SHA-256 |
|---|---|
| Survivor canonical files | `e2f978387e27874a867981c2bc6278cf9406213c1cab67796a1120a3162abf2a` |
| Survivor reachable Git state | `27b23f5b25ebf8154d995a0ce22c2b6cecd1cea0d1b167ab7dd74f2bb87e972d` |
| AI Prompt Suite canonical files | `7caa0e245ecd6a9590095c5f1e2850e049e0b31e3d5c7899a4a4f35e0dd920a5` |
| Deterministic fixture | `fff1a61e1a5212da2e17020687f63c9ee353020c059df5d38b563927e88979e4` |

AI Prompt Suite remained without a Git repository. No pilot, fixture, candidate, documentation,
Git ref, reflog, index, configuration, or reachable object changed.

### Required correction

Engineering and the CTO must define and test a narrow, non-writing way for the local Git
adapter to operate in the supported clean-Windows/non-author isolation model without trusting
ambient Git configuration or weakening repository-root confinement. The correction must be
candidate-bound and independently reauthorized. A12 must then rerun the affected
repository-activity and doctor checks; the already-passing packaging/recovery controls need
not be repeated unless the executable or packaging artifact changes.
