# V05-W3-02 Chief of Staff Diagnosis Review

| Field | Value |
|---|---|
| Task | `V05-W3-02` |
| Reviewer | Chief of Staff |
| Date | 2026-08-12 |
| Incoming artifact | [Handoff 94a](../../../.worktrees/v0.3.1-release/docs/handovers/v0.5/94a-wave-3-answer-media-diagnosis-return.md) |
| Disposition | Returned for bounded correction |

## Accepted

- The investigation stayed within the diagnosis-only boundary.
- The preserved failure, media, and VM state remain the correct evidence base.
- Multiple discoverable root answer files are a credible design hazard requiring correction.
- Wave 3 acceptance remains unchanged.

## Blocking findings

### `W3D-01` — causation exceeds the cited evidence

The reported `0x80072EE7`, BFSVC, and BCD errors do not themselves prove that two root
`Autounattend.xml` files caused the failure. Provide exact log excerpts with timestamps and
source paths showing which answer file Setup selected or cached in each pass, and distinguish
the first causal failure from downstream errors. If causation cannot be proven, label it a
hypothesis and define an offline discriminating validation before installation.

### `W3D-02` — proposed correction is incomplete

The stock ISO plus the cited OOBE-only answer file omits disk, image, locale, product-key, and
specialize behavior previously supplied by the remastered ISO. Define one authoritative,
Windows-SIM-validated answer file covering every required pass, on one answer-media source,
with the byte-exact stock ISO containing no competing root answer file.

### `W3D-03` — proposed proof violates authority

The matrix cites `oobe\bypassnro`; the controlling decision and `V05-W3-03` prohibit manual
OOBE bypass. Remove it. Synthetic bootstrap and offline OOBE must complete through the answer
media alone.

### `W3D-04` — identity and preservation proof is incomplete

Bind the full stock ISO identity, exact chosen answer XML/ISO identity, and before/after
identities for both preserved VMs/VHDXs and inspected media. Resolve inconsistent v4 XML sizes
and identify exactly which answer-file version is superseded.

### `W3D-05` — worklist lifecycle was invalid

The history skipped `in_progress`. Chief of Staff repaired that coordination history so the
worklist validates; Engineering must follow the lifecycle on its corrected return.

## Required correction

Append a clearly marked superseding section to Handoff 94a that:

1. separates proven facts, supported inference, and hypothesis;
2. identifies the first causal failure from exact retained evidence;
3. defines one complete authoritative answer file across all required passes;
4. validates the proposed XML offline using the accepted serviced Windows SIM/catalog;
5. removes every manual bypass or interactive workaround;
6. binds exact input identities and preservation checks; and
7. provides a deterministic matrix for exactly two fresh proof VMs.

No VM boot, install, media build, XML/media mutation, target activity, or network access is
authorized.

## Exit

`V05-W3-02` is returned for correction. `V05-W3-03` remains blocked.
