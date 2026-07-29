# CTO — Renewed A12-Only Authorization

| Field | Value |
|---|---|
| Role | Chief Architect / CTO |
| Milestone | v0.4 — Read-only Project Resume CLI Pilot |
| Date | 2026-07-29 |
| Executable | `014076c429d47de83be4ca6543264082aa62633f` |
| Documentation | `79a4999a9d8d6f0ff4a6daf47e758e8dbffc85bb` |
| Documentation parent | `10ebf331449ad11dd0cb4e5e40ffd50d3f531bd9` |
| Candidate wheel | `jarvis_core-0.1.0-py3-none-any.whl` |
| Candidate wheel SHA-256 | `7253e0b938433d7e393d186a3006c971b576381f6518fe986154d162fe0b3662` |
| Scope | Independent A12 packaging and recovery only |
| Status | **A12 reauthorized under wheel-only installation controls** |

## 1. Reviewed return

This review covers:

- `09-cto-a10-and-a12-renewed-activation.md`;
- `10-a12-to-principal-engineer-packaging-recovery-disposition.md`;
- `11-chief-of-staff-a12-packaging-correction-validation.md`; and
- `docs/evidence/v0.4/packaging-recovery-014076c.md`.

The first independent A12 attempt correctly stopped before pilot exposure because the
clean environment lacked `setuptools.build_meta` and the prior authorization prohibited
acquiring a build backend. PyYAML was the only package-index acquisition. No pilot path,
content, Git state, provider, telemetry, private evidence value, or runtime network was
exposed. All steps after candidate installation were correctly reported as `Blocked`,
not `Pass`.

The accepted private evidence identity for that stopped attempt remains:

```text
f39e277a3aba8cc99e62cb026f2f6500f3c2fd02a6c00a213c665448c1ca9b92
```

That stopped attempt is retained as history. It is not converted into successful A12
evidence.

## 2. Independent correction verification

Documentation commit `79a4999a9d8d6f0ff4a6daf47e758e8dbffc85bb` is a valid direct
child of `10ebf331449ad11dd0cb4e5e40ffd50d3f531bd9`. Its only changed file is:

```text
docs/software/PROJECT_RESUME_INSTALLATION_AND_RECOVERY.md
```

There is no change to executable code, tests, scripts, benchmark protocol, packaging
metadata, ADRs, pilots, classifications, or the accepted private baseline. There is no
non-documentation delta from executable `014076c`, and `git diff --check` passes.

The out-of-band candidate wheel was independently verified:

- filename: `jarvis_core-0.1.0-py3-none-any.whl`;
- SHA-256:
  `7253e0b938433d7e393d186a3006c971b576381f6518fe986154d162fe0b3662`;
- distribution name/version: `jarvis-core` / `0.1.0`;
- compatibility: pure-Python `py3-none-any`;
- runtime dependency: `PyYAML>=6.0`;
- console entry point: `jarvis = jarvis_core.cli:main`;
- runtime payload entries: 68;
- entries byte-identical to executable `014076c`: 68;
- missing or mismatched runtime payload entries: 0; and
- expected distribution-metadata entries: 6.

The wheel is an integrity-bound packaging of the frozen executable, not a new executable
candidate. It remains ignored and uncommitted and must not be rebuilt during A12.

## 3. Explicit A12 disposition

**INDEPENDENT A12 IS REAUTHORIZED USING THE EXACT VERIFIED CANDIDATE WHEEL.**

This disposition supersedes only the A12 installation and continuation scope in Handoff
09. It does not alter the A10 authorization, executable, accepted pilot baseline,
canonical/reachable Git boundary, or any acceptance criterion.

## 4. Authorized dependency boundary

PyYAML remains the only package that may be acquired from a package index.

The reviewer must:

1. create or verify the isolated clean A12 environment before exposing either pilot;
2. acquire only a PyYAML wheel satisfying `PyYAML>=6.0`, if the previously verified wheel
   is not already retained;
3. record its package name, exact version, public source, filename, SHA-256, and redacted
   acquisition outcome without credentials;
4. retain that exact verified PyYAML wheel locally;
5. install PyYAML offline with package-index access disabled and dependency resolution
   disabled;
6. disable and independently verify network denial before any pilot path or private
   evidence destination is exposed; and
7. keep network denied for every remaining A12 action.

The previously acquired A12 dependency evidence identifies PyYAML 6.0.3 with wheel
SHA-256:

```text
4a2e8cebe2ff6ab7d1050ecd59c25d4c8bd7e6f400f5f82b96557ac0abafd0ac
```

If that exact wheel is retained and its hash verifies, it may be reused offline. If a new
acquisition resolves to a different artifact, version, or hash, stop and return the new
identity for approval before pilot exposure.

No `setuptools`, build backend, build frontend, compiler, source distribution, or other
package may be acquired or invoked to install the candidate. No authenticated index,
private mirror, credential helper, provider, Git remote, or general network path is
authorized.

## 5. Candidate-wheel delivery and installation

The reviewer must receive the candidate wheel out of band. It may not be downloaded from
a package index, fetched from a Git remote, or built from the source tree during A12.

Before installation:

1. require the exact filename;
2. compute SHA-256 locally;
3. require exact equality with
   `7253e0b938433d7e393d186a3006c971b576381f6518fe986154d162fe0b3662`;
4. record only the approved artifact identity and redacted delivery result; and
5. stop immediately on any filename, size, hash, metadata, or delivery discrepancy.

Candidate installation must use this command shape:

```text
pip install --no-index --no-deps <verified-candidate-wheel>
```

The placeholder must resolve to the out-of-band wheel whose hash was just verified.
Editable mode, source installation, `PYTHONPATH`, build isolation, dependency resolution,
and author-provided workarounds are prohibited.

Uninstall/reinstall must use the same locally retained, re-hashed candidate wheel and the
same command shape. The reviewer must not rebuild, rename, patch, unpack/repack, or
substitute the wheel.

## 6. Authorized A12 continuation

After the exact wheel installs successfully, the independent reviewer is authorized to
resume A12 from installed-command verification:

1. verify installed `jarvis --help`, `jarvis resume --help`, and
   `jarvis resume-doctor --help`;
2. run the documented deterministic fixture twice with the explicit evaluation time and
   compare exact outputs/hashes;
3. exercise repository-denied and no-Git fixture behavior;
4. snapshot the accepted pilot and Git baselines before pilot access;
5. run both accepted classified pilots using only their approved selectors and scopes;
6. exercise repository-denied, request-scoped local read-only Git, and non-Git
   degradation;
7. exercise valid/invalid roots, redacted diagnostics, partial/incomplete results, and
   stable exit behavior;
8. exercise missing/corrupt derived-state recovery without canonical-source repair;
9. uninstall, prove command removal, reinstall from the same verified wheel, and repeat
   the deterministic fixture;
10. complete final canonical, reachable-object, privacy, network, and cleanup comparison;
   and
11. issue one explicit independent A12 disposition with private evidence digest and a
   redacted public summary.

Any previously completed pre-pilot step from the stopped attempt may be reused only when
its exact artifact, environment, and evidence identities remain verifiably unchanged.
Otherwise, repeat it. No prior `Blocked` step may be relabelled without execution.

## 7. Integrity and privacy controls

The accepted post-classification baseline and Handoff 06 canonical/reachable Git rules
remain mandatory.

Before and after relevant A12 operations, prove:

- exact canonical pilot bytes except for no authorized delta;
- exact `HEAD`, all ref namespaces, reflogs, index, staged entries, config, status, and
  pre-existing dirty state for the Git-enabled pilot;
- identical reachable-object manifests and reachability-affecting state;
- unchanged pack, pack-index, multi-pack-index, commit-graph, and object-control state;
- continued non-Git status for the non-Git pilot;
- no provider, telemetry, Git remote, credential, or runtime network activity; and
- no private data in committed/public evidence.

Valid new unreachable loose objects may be reported only as
`ambient_unreachable_object_drift` when every Handoff 06 condition passes. They must not
be hidden, deleted, attributed without proof, or described as “no Git change.”

Private paths, classifications, note names/content, Git subjects/authors/remotes,
credentials, environment secrets, and raw errors remain only in the approved ignored
evidence destination. Public evidence contains hashes, aggregate safe results, redacted
failure categories, and explicit dispositions only.

## 8. Mandatory stop conditions

Stop A12 and return a blocking finding on:

- candidate-wheel filename, SHA-256, metadata, or payload mismatch;
- PyYAML wheel mismatch or an unexpected dependency;
- any request for or use of `setuptools`, a build backend, source build, or dependency
  resolver for candidate installation;
- any undocumented installation or recovery step;
- any runtime network requirement or failure to prove network denial before pilot
  exposure;
- any provider, telemetry, Git remote, credential, upload, or runtime egress;
- any canonical-source mutation;
- any reachable-object, ref, reflog, index, config, status, pack, or object-control
  change outside the accepted baseline;
- any invalid or unprovable unreachable-object drift;
- any privacy leak or unredacted public evidence;
- any attempt to classify, repair, normalize, initialize Git, or modify a pilot;
- any need to change the executable, documentation, tests, scripts, benchmark, ADRs, or
  packaging metadata; or
- any step that cannot be completed under the exact published instructions.

An unavailable or blocked step is not a pass. The reviewer must not fix a defect during
the review.

## 9. A10 remains unchanged

The Principal Engineer's separate A10 authorization from Handoff 09 remains active and
unchanged. This A12 correction does not alter its candidate, pilots, current-PC reference
profile, performance protocol, evidence requirements, or stop conditions.

No A12 dependency or wheel rule expands A10 network or installation authority.

## 10. Explicit non-authorization

This disposition does not authorize:

- execution of A10 by the A12 reviewer;
- architecture-conformance review or architecture clearance;
- Quality & Release review;
- merge, push, tag, deployment, publication, or release;
- candidate, documentation, test, script, benchmark, packaging, or ADR changes;
- further classification, migration, pilot edit, or canonical repair;
- A11 dogfood collection;
- provider, telemetry, live GitHub, Git remote, credential, or runtime network access; or
- parked conversation or v0.5 work.

Any correction requires a return through Principal Engineering, Chief of Staff
validation, and a new exact-identity CTO review.

## 11. Required return

The independent A12 reviewer must append or supersede the existing packaging/recovery
disposition and public evidence with:

- executable `014076c`;
- documentation `79a4999`;
- exact candidate-wheel filename and SHA-256;
- exact retained PyYAML wheel identity and SHA-256;
- installation/uninstall/reinstall command shapes and exit statuses;
- network-disable proof before pilot exposure;
- installed-command, fixture, pilot, diagnostics, recovery, and integrity results;
- canonical/reachable comparison outcome;
- every unavailable step, limitation, or ambient-drift report;
- private evidence SHA-256; and
- one explicit A12 disposition.

The resulting evidence may then be returned to Principal Engineering for integration. It
does not itself authorize architecture review or QA.

## Exit statement

**A12 REAUTHORIZED; PREBUILT VERIFIED WHEEL REQUIRED; BUILD BACKEND PROHIBITED.**

Independent A12 may resume only under the exact wheel, offline installation, network
denial, privacy, and canonical/reachable controls above. A10 remains separately
authorized and unchanged. All later governance and release gates remain closed.
