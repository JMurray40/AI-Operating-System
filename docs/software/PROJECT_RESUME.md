# Project Resume (v0.4)

v0.4 adds **read-only Project Resume**: a deterministic, fully-sourced project briefing
assembled over the released v0.3.1 trust pipeline. Given one project selector it answers *"where
did I leave off, and what does the evidence actually say?"* — selecting exactly one project,
discovering authorized evidence, ordering it by explicit authority rather than search relevance,
binding every material claim to a passage-and-revision citation validated against current bytes,
and rendering a briefing whose supported and unsupported statements are visibly distinct. It is
offline and read-only; local Git activity is a separate, request-scoped, read-only capability.
See ADR-0018–0021, which build on the v0.3.1 query trust contracts (ADR-0014–0017).

Project Resume is **v0.4**; visible-context conversation remains **v0.5**.

## Contract versions

Project Resume adds its own versioned contracts, never conflated with the query versions:

- `contract_version: jarvis.project-resume.v0.4.0` — every structured result.
- `jarvis.project-resume-trace.v0.4.0` — the trace.
- `jarvis.repository-activity.local-git.v0.4.0` — repository-activity records.

The query `index_version` (`jarvis.index.v0.3.1`) is reported in the trace but kept distinct.

## Exact project selection (ADR-0018)

Selection is an authorization and disclosure boundary, not a relevance problem. Only
`type=project` notes inside the request-scoped authorized view participate. One normalized
selector is compared through four exact tiers — canonical id, title, alias, then the weaker
filename stem — and the *first* tier with any match controls the outcome. Exactly one match is
selected; two or more at the controlling tier are returned as safe sorted **candidates** without
choosing; no match returns **not found** without substituting a related project; duplicate
explicit ids or malformed identity **fail closed** as invalid identity. There is no fuzzy,
prefix, substring, semantic, graph, or recency tie-breaking.

## Evidence discovery channels

After selection, evidence is discovered over the authorized view through typed channels: the
canonical project passage; notes whose typed `projects` metadata resolves to the selected stable
identity; authorized outgoing/incoming relationships (bounded BFS); and query retrieval
materially bound to the project. Each selected source records its channel and reason; sources are
deduplicated by stable identity + current fingerprint; graph-selected and relevance-ranked
sources stay distinct; cycles terminate by visited identity; and configured caps (graph depth,
fan-out, per-channel, and total candidates) are enforced with bounded, non-disclosing omissions.
Local repository activity is a separate grant-gated channel, never discovered here.

## Authority, temporal state, supersession, and conflict (ADR-0019)

Retrieval relevance can never decide what is authoritative or current. Each source is lifted into
authority space with a typed class (strongest first: accepted decision, current state, current
priority, session summary, draft, inferred) and a temporal state derived from explicit source
dates and the request-supplied evaluation time (`dated`, `undated`, or `stale` at/after the
configured threshold). Within a subject, records order by class, then effective date, then
`updated`, then stable identity, then locator; a draft is never promoted by recency. Supersession
exists only when current authorized evidence carries an explicit `supersedes` reference that
resolves to a known identity in the subject set. When two or more materially different claims
remain supported at the strongest present class and neither validly supersedes the other, both
are **retained and marked conflicting** — nothing is merged or silently chosen. Excluded evidence
is simply absent, so it can neither create nor resolve a conflict.

## Claims, citations, coverage (ADR-0020)

The briefing has ten fixed sections, in order: project; current state; next action and
priorities; accepted decisions; recent sessions; open tasks and questions; resources; repository
activity; conflicts/staleness/missing context; evidence coverage and omissions. Evidence is
bucketed into these sections by note type, and ordering/conflicts within a bucket are resolved by
the authority module (so an accepted decision outranks a competing draft in the same subject).

Every material claim is bound to at least one citation validated against **current** source bytes
immediately before emission, through the reusable query-layer citation service (never a copied
implementation): the stored fingerprint must match the current bytes re-read within the resolved
root, and the full heading/line locator plus a non-empty excerpt must validate. A changed,
deleted, unreadable, or escaped source yields no supported citation, so the claim is marked
**incomplete** rather than silently dropped. Metadata-derived claims cite the metadata-bearing
frontmatter locator, not an unrelated body passage. Answer-level coverage summarizes
supported/incomplete/conflicting counts and never reads `complete` while any claim conflicts.

## Two hard budgets (ADR-0020)

Two independent budgets use the released deterministic estimator. The **evidence** budget bounds
selected passages and their wrappers; the **output** budget bounds the complete serialized result
(headings, labels, claim text, citations, conflicts, omissions, limitations, coverage, and the
requested trace). The final serialization is measured before emission; an over-budget result
sheds the lowest-priority claims (recording a bounded omission) or, when even the minimal
structure will not fit, returns a bounded `budget_error` — it never truncates serialized output
or severs a claim from its evidence. The trace is charged to a sub-budget that lives *inside* the
output budget, so a trace can never silently expand the result. CLI overrides are bounded:
evidence `256..32000`, output `256..16000`.

## Local repository activity and redaction (ADR-0021)

Repository activity is **denied by default** and only available with an explicit, frozen,
request-scoped grant that binds one canonical repository root to the selected project for a single
invocation. It is a distinct capability port, never part of the generic repository interface. The
only permitted operation reads recent first-parent commits through exactly three fixed,
`shell=False` command shapes with an allowlisted (never inherited) environment and hard caps on
records, timeout, and stdout/stderr; `rev-parse --show-toplevel` must canonicalize to exactly the
granted root, so parent, sibling, bare, submodule, and linked-worktree roots are rejected. A
deterministic fixture adapter provides the same semantic contract without Git installed. Every
failure is classified to an allowlisted, redacted code — never raw stderr, absolute paths,
usernames, remotes, environment, or credentials — and commit subjects/authors are treated as
inert data, never instructions. Nothing retries and no write method exists.

## Rendering and exit codes

Text and JSON are rendered from the same frozen semantic result, so they can never disagree. A
supported claim and an incomplete reference are structurally and visibly distinct; a passage
citation is never rendered as `L0-L0` (an incomplete reference shows identity + revision only);
inference, conflict, staleness, unavailable dependency, and unknown are labelled; an empty content
section states *"no supported evidence available"* rather than asserting none exist. No result
text is produced through a provider. Outcomes map to stable exit codes that extend the existing
`0/1/2` convention without reassigning it:

| Code | Meaning |
|---|---|
| 0 | complete supported briefing |
| 2 | partial / warning briefing |
| 3 | ambiguous selector (candidates shown, none chosen) |
| 4 | project not found (no substitute) |
| 5 | invalid input or identity |
| 6 | policy error |
| 7 | budget error |
| 1 | internal failure |

## Trace and determinism

`--trace` adds a non-disclosing trace: the Project Resume / trace / repository / index contract
versions, request id, workspace fingerprint, explicit evaluation time, safe authorization summary,
aggregate excluded count, selected identity and tier, discovery channels, included evidence
identities, coverage, budgets, token counts, and bounded omission reasons. Excluded source
identities/content and rejected ambiguity candidates are never traced, and timings are isolated in
their own field so the semantic result stays byte-identical for identical snapshot, scope, request,
and configuration.

## CLI

```bash
jarvis resume "<selector>" [--path <vault>] [--format text|json] [--trace]
  [--as-of <ISO-8601-UTC>] [--evidence-budget <n>] [--output-budget <n>]
  [--include-repository-activity --repository-root <local-git-root>]
jarvis resume-doctor [--path <vault>] [--repository-root <root>] [--format text|json]
```

Output is stdout only. `--as-of` makes the evaluation time explicit for reproducible output. See
[CLI Usage](CLI_USAGE.md) for full flags and examples.

## Diagnostics and recovery

Project Resume keeps **no persisted index**: the authorized view, lexical index, and relationship
graph are derived projections rebuilt in memory from canonical sources on every run, so a missing
or corrupt derived index self-heals on the next invocation. `jarvis resume-doctor` performs that
rebuild explicitly (reporting index version and workspace fingerprint) and diagnoses the runtime,
vault, Git availability/version, and an optional repository root — all strictly read-only. No
diagnostic or recovery step writes to, repairs, or migrates canonical sources.

## Read-only and security invariants

The command never changes vault files, metadata, timestamps, Git worktree/HEAD/refs/config/index/
objects, external resources, or durable state. Adversarial inputs — path traversal, symlink/junction
escape, option-looking or huge selectors, duplicate ids, unauthorized/restricted evidence,
post-discovery byte mutation, prompt injection in vault or Git text, and hostile Git
config/environment — are handled as inert data or fail closed for the affected capability while
preserving safe local-vault completion.

## References

ADR-0018 (identity), ADR-0019 (authority/temporal/conflict), ADR-0020 (claims/citations/budgets),
ADR-0021 (repository activity); building on ADR-0014–0017 (query trust contracts). Benchmark:
`scripts/benchmark_project_resume.py`. Evaluation: `scripts/evaluate_project_resume.py` and
`evaluations/v0.4-project-resume-dogfood-template.tsv`.
