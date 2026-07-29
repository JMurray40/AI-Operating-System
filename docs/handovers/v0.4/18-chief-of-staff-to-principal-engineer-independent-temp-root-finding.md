# Handoff 18 — Chief of Staff to Principal Engineer: Independent Temp-root Finding

**Date:** 2026-07-29

**Disposition:** **RETURN TO ENGINEERING — INDEPENDENT WINDOWS IDENTITY GATE FAILS**

**Candidate reviewed:** `9620c047db7eeba8ba896866283c0d547209f67b`

**Correction range:** `d5560131156015ca477fec2d8f5729f3f80216a7..9620c047db7eeba8ba896866283c0d547209f67b`

## Chief of Staff finding

The branch, exact HEAD, clean state, two-file scope, Ruff result, mypy result, and
`git diff --check` all validate.

The independent Windows-isolation test gate does not:

```text
66 local-Git tests collected
47 passed
19 failed
```

The failures occur before Git execution. `_owner_controlled_base` derives its base from
`tempfile.gettempdir()` and then uses the shared fixed child name `jarvis-safe-root`. In the
independent sandbox identity used for A12-style validation, that existing owner-only directory
belongs to the host identity and cannot be resolved:

```text
PermissionError: access denied to the ambient temporary jarvis-safe-root
```

The adapter maps the result to `unavailable_security_setup`. Snapshot, degradation, fixed
command, real-Git, serialization, substitution, and ACL tests consequently fail because the
runner is never invoked.

This is not the earlier pytest default-temp issue: pytest's own controlled `--basetemp` was
accessible and all test fixtures were created successfully. The product code independently
selected the inaccessible ambient user-temp root.

## Architectural significance

Handoff 17 required an explicit owner-controlled temporary parent rather than ambient
temporary-directory resolution. Candidate `9620c04` still calls `tempfile.gettempdir()` and
uses a cross-process fixed directory name. Its behavior therefore depends on prior state and
which Windows identity created that directory.

This directly affects the authorized A12 model: the installed candidate executes under an
independent restricted identity, while engineering and host-side verification may execute as
the repository owner. A gate that passes only for the creator identity does not close
LG-SEC-02 or establish the required independent packaging/recovery path.

## Required bounded correction

Engineering must keep the correction limited to the local-Git adapter and its tests and:

1. define a deterministic, explicit temp-parent acquisition rule that works for the actual
   running identity without trusting a shared directory owned by a different identity;
2. avoid a cross-identity fixed child whose prior ACL can deny or influence a later process;
3. validate ownership, ACL, confinement, and reparse behavior before writing the repository
   root;
4. treat pre-existing, inaccessible, incorrectly owned, substituted, or malicious temp-root
   state as a redacted typed failure without modifying another identity's artifact;
5. retain bounded stale-artifact recovery only within a namespace proven to belong to the
   current identity/process;
6. add a process-boundary test that creates the shared-name/pre-existing-foreign-owner
   condition and proves the product either uses its own safe namespace or fails with the
   explicitly accepted degradation; and
7. demonstrate the full local-Git test file under the independent Windows identity used for
   A12, not only under the engineering/host identity.

Return a new exact candidate, changed-file list, full and targeted gates, and the revised
security rationale. Stop for Chief of Staff validation.

## Gate state

Candidate `9620c04` is not ready for CTO review. No wheel build, A12, A10, QA, merge, push,
tag, release, pilot modification, classification change, or v0.5 work is authorized.
