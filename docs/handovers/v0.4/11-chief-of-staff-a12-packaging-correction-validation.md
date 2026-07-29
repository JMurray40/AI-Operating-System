# Chief of Staff — v0.4 A12 Packaging Correction Validation

| Field | Value |
|---|---|
| Role | Chief of Staff |
| Milestone | v0.4 — Read-only Project Resume CLI Pilot |
| Date | 2026-07-29 |
| Executable | `014076c429d47de83be4ca6543264082aa62633f` |
| Documentation | `79a4999a9d8d6f0ff4a6daf47e758e8dbffc85bb` |
| Documentation parent | `10ebf331449ad11dd0cb4e5e40ffd50d3f531bd9` |
| Wheel | `jarvis_core-0.1.0-py3-none-any.whl` |
| Wheel SHA-256 | `7253e0b938433d7e393d186a3006c971b576381f6518fe986154d162fe0b3662` |
| Status | **Ready for renewed A12-only CTO authorization** |

## Documentation correction

The correction is a documentation-only direct child of the prior reviewed documentation
commit. It changes only:

```text
docs/software/PROJECT_RESUME_INSTALLATION_AND_RECOVERY.md
```

The runbook now:

- binds the exact wheel filename and SHA-256;
- requires hash verification before installation;
- installs the candidate using `--no-index --no-deps`;
- requires no local setuptools/build backend;
- preserves the PyYAML-only network exception;
- uses the same verified wheel for uninstall/reinstall; and
- keeps source installation explicitly limited to engineering/developer environments.

`git diff --check` passes. No executable, test, script, benchmark, packaging metadata,
ADR, pilot, classification, private baseline, or other tracked file changed.

## Independent wheel validation

The Chief of Staff independently verified the ignored private wheel:

- SHA-256 matches the runbook exactly;
- package metadata is `jarvis-core` version `0.1.0`;
- compatibility tag is pure-Python `py3-none-any`;
- runtime dependency is `PyYAML>=6.0`;
- console entry point is `jarvis = jarvis_core.cli:main`;
- 68 `jarvis_core` payload files are present;
- all 68 payload files are byte-identical to executable commit `014076c`;
- zero payload files are missing or mismatched; and
- six expected distribution-metadata entries are present.

Engineering reports a disposable clean-environment smoke test that installed PyYAML
offline, installed the wheel without setuptools, verified all three command surfaces,
uninstalled, proved command removal, and reinstalled from the same wheel. This smoke test
supports renewed authorization but does not substitute for independent A12.

The wheel remains ignored and uncommitted. It must be delivered out of band and verified
by the independent reviewer before use.

## Gate state

A12 remains paused until the CTO:

1. pins executable `014076c`;
2. pins documentation `79a4999`;
3. pins the exact wheel digest above;
4. retains the existing PyYAML-only installation exception;
5. requires network denial before pilot exposure;
6. requires installation and reinstall from the same verified wheel; and
7. reauthorizes only the previously blocked A12 steps.

A10 remains separately authorized and is unaffected.

## Disposition

**PACKAGING CORRECTION VALIDATED; READY FOR RENEWED A12-ONLY CTO AUTHORIZATION.**

This does not authorize A12 execution, architecture clearance, QA, merge, push, tag,
release, candidate modification, additional classification, or v0.5 work.
