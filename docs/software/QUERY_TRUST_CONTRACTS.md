# Query Trust Contracts (v0.3.1)

v0.3.1 hardens the read-only query engine so that retrieval, authorization, context
budgeting, citations, identity, and trace are explicit, versioned, deterministic, and
testable. It is **infrastructure for trustworthy retrieval**, not a conversational or
generated-answer release. See ADR-0014–0017 and the
[v0.3.1 requirements](V0.3.1_QUERY_TRUST_CONTRACTS_REQUIREMENTS.md).

## Contract version

All affected structured outputs (results, citations, context packages, traces) carry
`contract_version: jarvis.query.v0.3.1`. The index projection version is a separate field,
`index_version: jarvis.index.v0.3.1`; the two are never conflated.

## Retrieval relevance vs answer confidence (ADR-0014)

Ranking exposes **`relative_relevance`** — a deterministic normalization within a single
result set (0–1, relative to the top hit). It is not a probability, a correctness claim, or
comparable across queries. The word *confidence* is never used for ranking, in JSON or text.
No numeric **answer confidence** is emitted in v0.3.1; `answer_confidence` is reserved and
always `null`.

## Authorization before retrieval (ADR-0015)

Every query runs under an immutable `AuthorizationScope` (`workspace_id`, `max_sensitivity`,
optional allowed source-ids / path-prefixes / types, `request_id`, policy id+version).
Authorization and sensitivity filtering happen **before** the request-visible index and
graph are built, so excluded sources cannot influence candidates, ranking, graph expansion,
context, citations, conflict detection, errors, or trace. Only an aggregate `excluded_count`
is ever reported.

Fail-closed: unknown/missing workspace or sensitivity ceiling raises a typed `PolicyError`;
a note whose sensitivity label is unknown or absent is **excluded**, never treated as
unrestricted. Existing CLI behavior uses an explicit local allow-all scope
(`local_allow_all()`), which still enforces the ceiling and fail-closed rules — absence of a
scope never means unrestricted access.

## Stable identity and revision (ADR-0017)

- `source_id` — logical identity, namespaced by workspace. Prefers the validated frontmatter
  `id` (`source_identity_kind: explicit`); otherwise a documented workspace+path fallback
  (`path_derived`) whose weaker stability is labelled honestly.
- `source_fingerprint` — SHA-256 of the **exact source bytes** (CRLF/LF included). A revision
  marker, not an identity; not a secret.
- Duplicate explicit IDs within one workspace are validation failures (`DuplicateIdentityError`)
  and are never silently merged.

## Passage-and-revision citations (ADR-0016)

A citation binds `source_id` + `source_identity_kind` + `title` + `relpath` +
`source_fingerprint` + a deterministic **locator** (heading path + 1-based inclusive
`line_start`/`line_end`) + a bounded **excerpt** + `relative_relevance` (when ranked) +
reason + `coverage`. Before a citation is emitted the engine validates the stored
fingerprint against the **current source bytes** (re-read from the configured `source_root`,
path-escape and missing files fail closed) as well as the full heading hierarchy at the
locator and the non-empty excerpt; a source changed since discovery is stale and declined.
When no `source_root` is configured, validation uses the discovery-time bytes (proving
discovery-revision consistency only). Excerpt bounding is deterministic
(`EXCERPT_MAX_LINES`/`EXCERPT_MAX_CHARS`) and never reorders or normalizes source text.

`coverage` is `supported` when the citation is bound to a validated claim-specific passage,
or `incomplete` when the source is referenced by identity and revision but no specific
supporting passage exists — the engine never attaches arbitrary first content as support.
Ranked (search/related/projects) citations are material: they cite the passage containing
the retrieval evidence, or are declined. Unranked summarize/explain citations cite the
passage that carries the claim-specific evidence (a link to the project or the other
endpoint); absent that, they are marked `incomplete` rather than fabricated.

## Context budget invariant (R2)

`0 <= total_tokens <= token_budget`, always. Negative budgets fail at construction; a zero
budget yields no chunks. A deterministic per-chunk separator (`SEPARATOR_TOKENS`, charged
between chunks) counts toward the total. An oversized chunk is deterministically truncated to
the remaining allowance or omitted with a typed reason — never admitted whole and never given
a fictional one-token minimum.

## Trace (R6)

Trace carries `contract_version`, `index_version`, `request_id`, workspace fingerprint, a
safe authorization summary (policy id/version, workspace, ceiling — no excluded identities),
aggregate `excluded_count`, provider/prompt version (`none` when not applicable), the context
budget/used/truncations/omissions, and rankings labelled `relative_relevance`. Deterministic
structured fields are byte-identical for identical snapshot, scope, request, and config; only
timing varies.

## Migration (pre-1.0 breaking change)

| Old (v0.3) | v0.3.1 | Rule |
|---|---|---|
| `confidence` on ranked results/citations | `relative_relevance` | new writers emit only the new name |
| `confidence` in trace | `relative_relevance` | never reinterpret as answer confidence |
| unversioned payloads | `contract_version: jarvis.query.v0.3.1` | all affected outputs versioned |
| note-level citation | passage-and-revision citation | material claims need a passage |
| implicit unrestricted query | explicit local allow-all scope | missing scope fails closed |

A single-release compatibility **reader** (`jarvis_core.query.compat`) accepts stored legacy
`confidence` and maps it to `relative_relevance` only (never to answer confidence). Writers
emit only the new names. Removal target: no earlier than v0.4. No vault migration and no
source writes occur; notes lacking an explicit `id` continue through the path-derived
fallback.

## Duplicate identity handling (workspace validation vs request disclosure)

Duplicate explicit IDs are validation failures (ADR-0017), handled at two separate layers so
that fixing one never leaks the other:

- **Workspace validation** (all notes): the existing vault validator / health analyzer flags
  duplicate IDs across the entire vault, independent of any request. This is the authoritative
  data-integrity signal for the vault owner.
- **Request-scoped query** (authorized notes only): `build_authorized_view` checks for
  duplicate explicit IDs **only among the notes authorized for the request**, raising
  `DuplicateIdentityError` before any index/graph is built. Because the check runs strictly
  over the authorized subset, a duplicate that involves an *excluded* source can never surface
  through a request-visible error, count, or trace (ADR-0015). A duplicate wholly within the
  authorized set fails the query closed without naming any excluded source.

The two layers are intentionally separate: query disclosure never reveals excluded identities,
while whole-vault validation still surfaces all duplicates to the owner.
