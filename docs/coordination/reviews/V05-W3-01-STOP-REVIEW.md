# V05-W3-01 Chief of Staff Stop Review

| Field | Value |
|---|---|
| Task | `V05-W3-01` |
| Reviewer | Chief of Staff |
| Date | 2026-08-12 |
| Incoming artifact | [Handoff 94](../../../.worktrees/v0.3.1-release/docs/handovers/v0.5/94-wave-3-answer-media-synthetic-return.md) |
| Disposition | Superseded by a diagnosis-first correction route |

## Review

The Wave 3 acceptance criteria were not met. Byte-identical answer ISOs were produced, but two
equivalent answer-media-driven zero-NIC installations were not proven. The surviving manual
installation cannot substitute for the required evidence, so acceptance is not amended.

The preserved failure is suitable for offline diagnosis. The next task must first extract and
analyze the existing Windows Setup evidence without booting or altering either synthetic VM.
Only after the cause and a bounded correction are independently accepted may a separate task
build corrected media and attempt exactly two fresh synthetic installations.

## Controls

- Preserve `Jarvis-A12-Synth-A`, `Jarvis-A12-Synth-B`, their VHDXs, and both answer ISOs.
- Do not boot a VM, rebuild media, perform another installation, or use the target VM during
  diagnosis.
- Do not weaken the Wave 3 acceptance criteria.
- If the evidence does not establish a bounded answer-media defect, return to CTO/Product Owner
  rather than guessing.

## Exit

`V05-W3-01` is preserved and superseded. Product Owner decision
`PO-05-W3-DIAGNOSIS-CORRECTION` controls the replacement tasks.
