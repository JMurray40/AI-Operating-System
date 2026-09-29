# Handoff 10 - Bounded corpus-epoch resilience and observability design

Date: 2026-09-23
Sender: Chief of Staff
Receiver: Principal Engineer
Task: `V06-PR-01`
Disposition: **CONSOLIDATED CORRECTION AND ONE COMPLETE PROOF AUTHORIZED**

## Review finding

[Verified] The immutable in-memory benchmark design passed 807 tests and Ruff. Its real-vault proof failed at one of three live inventory checkpoints, but all checkpoints map to the same `source_integrity_failure` category. A later exact diagnostic inventory matched the baseline. The retained evidence cannot distinguish initial inventory unavailability, post-acquisition unavailability, final verification unavailability, or a true mismatch.

[Inferred] A live synced vault needs bounded whole-corpus acquisition resilience before questions begin. Treating any transient metadata miss as permanent makes the prototype unusable; retrying individual files could create a mixed revision and remains prohibited.

## Frozen correction

Engineering may implement one corpus-epoch controller with these rules:

1. Emit a fixed, privacy-safe checkpoint category for `initial_inventory`, `acquisition`, `post_acquisition_inventory`, `benchmark`, and `final_inventory`. Retained evidence may include only checkpoint, attempt number, fixed outcome category, counts and timing; never paths, source IDs, content, questions or raw exceptions.
2. Before any question runs, allow at most three **whole-corpus epochs** within five minutes. An epoch consists of a full inventory, one-open acquisition of every governed source, and a second full inventory.
3. Any actual inventory mismatch, fingerprint mismatch, policy/path/reparse failure, parse failure, write/network attempt or privacy failure is terminal immediately. Only fixed-category metadata/read unavailability may discard the entire epoch and advance to the next epoch after a fixed delay.
4. A successful epoch must have identical initial inventory, acquired fingerprints and post-acquisition inventory. It creates one immutable in-memory corpus for all three benchmark repetitions.
5. No per-file, per-question or partial-corpus retry is allowed. No benchmark result from a failed epoch exists because questions have not started.
6. After the three repetitions, final inventory verification may use the same maximum-three whole-inventory availability attempts within five minutes. Any successful inventory must exactly equal the governed baseline; any mismatch is terminal. Results remain unpublished until this gate passes.
7. Preserve all prior stopped evidence. Publish one result pair exclusively; never overwrite it.

## Required tests and proof

Synthetic tests must cover every checkpoint and both retry directions, exhaust the bounds, prove a mismatch never retries, prove every discarded epoch releases acquired bytes, prove no question runs before a successful epoch, prove exactly three repetitions share one immutable corpus, and prove no private fields enter evidence. Rerun the full accepted-Core suite, Ruff, privacy scan and candidate digest.

After those gates pass, Engineering may make one complete real-vault proof invocation. This is the final execution attempt under the present S0/S1 design. Failure returns a checkpoint-specific terminal disposition; no further attempt is implied.

No sync-software change, persisted corpus, weaker integrity check, broader scope, persistent index, embedding, durable memory, provider, credential, network access, watcher, background service, legacy-memory function or voice-triggered recall is authorized.

Product Owner action: none. Next role: Principal Engineer.
