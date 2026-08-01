# ADR-0023: Conversation Uses Immutable Visible Context Snapshots

| Field | Value |
|---|---|
| Status | Proposed |
| Date | 2026-08-01 |
| Deciders | Product Owner, advised by Chief Architect / CTO |
| Related | ADR-0015, ADR-0016, ADR-0017, ADR-0020, Security Threat Model |

## Context

A conversational provider request can disclose private source content. Filtering after
retrieval, assembling a prompt before policy, or allowing context to change between preview
and dispatch makes the displayed context untrustworthy.

## Proposed decision

Every turn is a two-phase operation: `prepare` and `dispatch`.

`prepare` requires an immutable workspace authorization scope and provider destination. It
applies authorization and sensitivity policy before candidate generation and graph
expansion, retrieves evidence, validates current bytes, and creates an immutable context
snapshot. The snapshot contains stable source IDs, exact fingerprints, passage locators,
bounded excerpts, reasons, sensitivity, token estimates, omissions, policy version,
provider destination, prompt-template version, prompt-assembler version,
history-serialization version, token-estimator version, safety-instruction version,
output-reserve version and value, and a digest over all of those semantic contents.
Excluded sources cannot influence or appear in the snapshot or safe diagnostics.

The complete snapshot is shown before a remote provider can receive it. The user may remove
items, which creates a new snapshot and digest; the existing snapshot is never mutated.
`dispatch` requires an explicit approval bound to the exact snapshot digest, workspace,
provider destination, model role, request, policy version, prompt-construction versions,
output reserve, and expiry. Source authorization and destination eligibility are
re-evaluated, and every citation is revalidated against current source bytes immediately
before prompt assembly and dispatch. Any mismatch, missing source, path escape, changed
policy or prompt input/version, unclassified sensitivity, or destination mismatch fails
closed.

Prompt assembly occurs only from the approved snapshot. Dispatch content bytes are a
deterministic function of its approved semantic inputs and bound prompt-construction
versions; the assembler may not introduce an unbound content-bearing field. Retrieved text
is delimited as untrusted data and cannot alter system policy, provider selection, tools,
or permissions. No tool capability is present.

Retry uses the same immutable snapshot digest and creates a new attempt ID. If current-byte
or policy validation no longer passes, retry is refused and a new `prepare` is required.
Changing context, provider, role, or user input is a new request, not a retry.

## Consequences

- What the user approves deterministically defines every content-bearing field the adapter
  may send; transport metadata and opaque credential transport are separately allowlisted.
- Context removal, retries, citations, trace, and cost records share one request identity.
- Provider calls cannot occur during discovery, preview, or policy evaluation.
- Local/mock dispatch may omit the human egress confirmation only when policy proves there
  is no external destination; it still uses the same snapshot and authorization pipeline.
- Snapshot contents are session-only under ADR-0022.

## Alternatives rejected

- Approve only a source list: rejected because passage bytes and destination can change.
- Redact after prompt assembly: rejected because disallowed content already crossed the
  internal boundary.
- Rebuild context silently on retry: rejected because it changes the approved disclosure.

## Revisit conditions

Revisit if a later local-only provider can prove a materially simpler boundary without
weakening cross-provider contract equivalence.
