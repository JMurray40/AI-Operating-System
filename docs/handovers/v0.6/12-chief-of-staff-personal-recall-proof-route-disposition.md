# Handoff 12 - Personal Recall proof-route disposition

Date: 2026-09-23
Sender: Chief of Staff
Receiver: Product Owner
Task: `V06-PR-02`
Disposition: **READY FOR PRODUCT OWNER DECISION - NO FURTHER LIVE-VAULT RETRY**

## Decision summary

[Verified] The Personal Recall candidate is technically credible offline: the isolated seven-file candidate passed 820 tests and Ruff against accepted Core commit `429c1c37d6bf17aab02b2d741b11a72d01d9a430`, tree `c08ccaf8044952299054fb0e2a41a788f8c325f0`.

[Verified] Real-vault proof is not complete. The final authorized attempt stopped before corpus acquisition at `initial_inventory:integrity_mismatch`. No recall, citation, three-run determinism or performance result exists for the private vault.

[Inferred] The repeated stops now demonstrate a design mismatch, not an ordinary implementation defect: an actively used vault cannot reliably satisfy a proof protocol that requires exact identity with an earlier live-filesystem baseline.

[Recommended] End the current retry cycle. Do not weaken integrity checks and do not authorize another live-vault attempt under the current design.

## Recommended route

Authorize a separately governed **temporary private snapshot proof**:

1. Create one read-only, hash-bound copy of only the already approved Markdown scope.
2. Store it outside Git in the existing private evidence boundary.
3. Validate its inventory and content hashes before any question runs.
4. Run the existing 24-question benchmark three times against that immutable snapshot.
5. Publish only the already approved redacted aggregate evidence.
6. After independent review, securely remove the snapshot under separate explicit cleanup authority.

This route preserves the strict source-integrity requirement while removing live-vault timing and synchronization from the benchmark. It does not authorize persistent indexing, embeddings, durable memory, broader vault scope, providers, credentials, network access or frontend activation.

## Alternatives

### Alternative A - Park S1 real-vault proof

Accept the synthetic implementation evidence only, record S1 as unproven and pause Personal Recall before private-vault use. This is the lowest-risk route but delivers no working personal recall milestone.

### Alternative B - Human-declared quiet-window retry

Pause editors and synchronization, rebaseline the live vault and attempt the benchmark again. This is not recommended: prior quiescence checks already passed before later failures, and the route remains timing-dependent.

## Product Owner decision requested

Choose exactly one:

1. **Approve the recommended temporary private snapshot proof.**
2. **Park S1 and accept synthetic evidence only.**
3. **Return for a different architecture decision.**

No implementation or proof execution begins from this document alone. If option 1 is approved, Chief of Staff will publish one outcome-sized authorization covering snapshot creation, validation, benchmark execution, independent review evidence and governed cleanup. Ordinary in-scope defects must be corrected within that single task; they must not generate serial micro-handoffs.

## Boundary

`V06-PR-01` remains blocked and terminal under its current authority. No vault content was read for this review, no private evidence was changed, and no proof attempt, network access, provider use, source edit, commit, merge or push occurred.
