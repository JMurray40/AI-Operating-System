# Handoff 13 — A12 to Principal Engineer: Packaging and Recovery Revalidation

**Date:** 2026-07-29  
**Disposition:** **REFACTOR FIRST**  
**Executable reviewed:** `014076c429d47de83be4ca6543264082aa62633f`  
**Documentation reviewed:** `79a4999a9d8d6f0ff4a6daf47e758e8dbffc85bb`

## Outcome

The renewed, prebuilt-wheel A12 procedure resolved the earlier build-backend blocker.
Installation, installed commands, deterministic fixture, diagnostics, invalid-path behavior,
uninstall, removal proof, and reinstall from the same verified artifact passed offline.
Canonical pilot, fixture, and reachable-Git state remained byte-for-byte stable.

A12 is not ready because the required authorized local-repository mode cannot run in the
documented independent Windows isolation environment. The candidate suppresses system and
global Git configuration. Git then rejects Survivor Group Tracker because the isolated
reviewer identity does not own the repository. The product reports the redacted
`unavailable_not_a_repository` limitation and its doctor fails repository-root validation.

The no-Git pilot's unavailable degradation behaved safely. This finding is limited to the
required granted local-Git path.

## Engineering return

Provide a narrowly bounded correction that:

1. preserves ADR-0021's fixed read-only command shapes, root equality check, environment
   allowlist, redaction, and no-network boundary;
2. supports a repository explicitly granted by the requester when the clean reviewer/runtime
   identity differs from the repository owner;
3. does not trust ambient global/system Git configuration, alter repository configuration or
   ownership, add a broad compatibility framework, or expose private paths; and
4. adds process-boundary tests for both the ownership-safe success path and rejection cases.

Return the exact executable identity, changed-file list, tests, and an architect-facing
security rationale. Freeze the corrected candidate and stop for CTO review. Do not run QA,
merge, push, release, A10, or v0.5 work.

## Evidence

See the superseding revision in
[the A12 packaging/recovery evidence](../../evidence/v0.4/packaging-recovery-014076c.md).
Private raw outputs remain in the approved ignored evidence root.
