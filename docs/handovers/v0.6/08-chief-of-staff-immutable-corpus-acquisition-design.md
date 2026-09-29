# Handoff 08 - Personal Recall immutable corpus-acquisition design

Date: 2026-09-22
Sender: Chief of Staff
Receiver: Principal Engineer
Task: `V06-PR-01`
Disposition: **BOUNDED DESIGN CORRECTION AUTHORIZED; ONE COMPLETE PROOF ATTEMPT**

## Root cause and design decision

[Verified] Both benchmark attempts failed before their first question at the same live-filesystem `lstat` boundary, despite exact inventories and successful complete binary reads immediately beforehand. The current benchmark reconstructs its corpus from live files for each planned run, creating repeated filesystem-availability dependencies after source identity has already been established.

[Inferred] Repeated live reopening is unnecessary for a deterministic benchmark over frozen bytes and is now the leading defect. This disposition does not classify the underlying Windows or sync behavior; it removes that behavior from the three-run measurement boundary without weakening integrity controls.

## Frozen correction

Engineering may modify the candidate so the benchmark:

1. Performs the existing full governed-inventory and policy checks.
2. Acquires each authorized source exactly once into memory using the existing path, reparse, metadata, size, timestamp and SHA-256 checks.
3. Immediately reruns the complete live inventory and requires exact equality with the governed baseline before any question executes.
4. Constructs one immutable in-memory corpus from those verified bytes.
5. Runs all three benchmark repetitions against that same immutable corpus without reopening vault paths.
6. Reruns the complete live inventory after all repetitions and requires exact equality with the governed baseline before publishing any result.
7. Releases the in-memory corpus on process exit. Raw note bytes or parsed note text must not be written to private or public evidence, logs, traces, errors or temporary files.

Current-byte citation validity during the benchmark binds to the acquired bytes plus the exact governed inventory fingerprint. The final post-run inventory check proves the live sources still match those bytes. Any acquisition or pre/post inventory failure invalidates the entire attempt.

## Required synthetic evidence

Before real-vault execution, tests must prove:

- each source is opened exactly once per benchmark invocation;
- the three repetitions receive the same immutable source bytes and ordering;
- no source reopen occurs after acquisition;
- mutation during acquisition, between acquisition and the pre-run inventory, or before the post-run inventory fails closed;
- path/reparse/policy/citation/privacy/network gates remain unchanged;
- no source bytes, note text or private paths enter retained evidence;
- full accepted-Core tests, Ruff and candidate-digest evidence pass after the correction.

## Execution authority

After those gates pass, Engineering may make one complete real-vault proof attempt using the already-validated private manifest. Preserve both stopped attempts. No per-file or per-question retry, skip, substitution, persisted private corpus, sync-software change or weakened integrity rule is permitted.

If acquisition or either inventory check fails, stop without retry. All Handoff 258 exclusions remain in force. Product Owner action: none. Next role: Principal Engineer.
