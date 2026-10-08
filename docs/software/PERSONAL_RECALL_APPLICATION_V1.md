# Personal Recall application v1

`jarvis.personal-recall.v1` is a fixture-only, read-only retrieval boundary. It opens an
opaque session and returns at most five ranked lexical candidates with revision-bound
citations. Results are candidates, not answers: `resolution` is always `unresolved`,
`answer_claim` is always `none`, and the destination is `local_no_provider`.

The application accepts only an immutable synthetic workspace binding. It verifies the
external classification policy, authorizes before indexing, enforces private-or-lower
sensitivity, and rechecks the complete source inventory before publication. The bounded
path permits at most 1,000 Markdown files, 1 MiB per file, 16 MiB total, and ten seconds
of cooperative work. Cancellation, reset, stale sessions, changed policy or sources,
malformed input, duplicate identity, and resource exhaustion fail closed with categorical
errors and no candidates.

This contract does not provide durable memory, embeddings, generated answers, provider
access, live-vault selection, background watching, source writes, or conversation context
attachment. Activating a private workspace requires a separate authorization.
