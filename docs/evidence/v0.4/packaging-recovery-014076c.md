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
