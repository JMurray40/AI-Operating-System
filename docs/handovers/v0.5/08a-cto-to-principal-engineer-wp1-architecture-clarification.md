# Handoff 08a — CTO to Principal Engineer: WP1 Architecture Clarification

| Field | Value |
|---|---|
| Sender | Chief Architect / CTO |
| Receiver | Principal Engineer |
| Date | 2026-08-01 |
| Milestone | v0.5 — Visible-Context Conversation |
| Authority | Bounded clarification under Handoffs 07 and 08 |
| Engineering base | `e11703974219425b463a45a97e1d7d2a04de81dc` |
| Observed dirty Engineering HEAD | `e11703974219425b463a45a97e1d7d2a04de81dc` |
| Disposition | **APPROVED WITH REQUIRED WP1 CORRECTION — WP2 AND WP3 REMAIN PAUSED** |

## 1. Review boundary

The CTO reviewed the two load-bearing WP1 questions raised by Engineering while preserving
the current dirty, uncommitted implementation as evidence. No Engineering file, test,
branch, index, commit, provider, credential, or network state was modified by this review.

This clarification does not change the accepted order in Handoff 07. Engineering must
correct WP1 before beginning WP2 or creating a milestone commit.

## 2. Decision A — provider-specific credential availability at prepare

**Approved: mock preparation and Google preparation have different credential-availability
preconditions.**

### 2.1 Mock and non-remote preparation

Preparation for the deterministic mock or another explicitly policy-proven non-remote
profile:

- requires no provider credential;
- performs no credential-provider call;
- performs no network or endpoint check; and
- remains capable of deterministic fixture preparation, inspection, removal, approval, and
  offline dispatch.

A credential requirement on the mock path would create false coupling and would violate
the offline fixture and degraded-operation contracts.

### 2.2 Google remote preparation

Preparation for the approved Google profile must verify **credential availability** before
source retrieval, candidate generation, graph expansion, context assembly, or prompt work.
If unavailable, it returns the typed, redacted `unavailable_credential` outcome and proves
that none of those later stages ran.

This preflight:

- occurs only after request/workspace/provider-profile validation and destination
  eligibility are known;
- uses the typed credential-provider boundary;
- returns availability only and does not place the secret in a request, snapshot, session,
  trace, error, fixture, or evidence object;
- does not call Google, validate the key remotely, estimate live quota, or perform network
  activity;
- is repeated before dispatch; and
- materializes opaque authorization transport only at the adapter boundary for the one
  approved dispatch attempt.

WP1 tests must use an injected fake availability provider and canary values. They must not
read Jason's environment or `GEMINI_API_KEY`. The production environment-backed provider is
WP2 work under Handoff 08 and remains prohibited from reading a live key during tests.

### 2.3 Required regression evidence

Add tests proving:

1. mock prepare succeeds without any credential provider and never consults one;
2. Google prepare with unavailable credential returns `unavailable_credential` before the
   query engine, graph resolver, context builder, prompt assembler, or provider is invoked;
3. Google prepare with fake available status may proceed, but does not materialize or retain
   credential bytes;
4. a credential becoming unavailable after approval blocks dispatch before prompt assembly
   or transport; and
5. trace/error/result surfaces contain no secret, credential name/value, private path, or
   raw exception.

## 3. Decision B — bounded authorized graph-neighbor expansion

**Required before WP1 Engineering completion.** The selected project note alone is not a
sufficient project-scoped conversation context. Deferring all project neighbors would fail
the accepted requirement for useful project-aware context and would leave C04's graph
authorization boundary materially unexercised.

### 3.1 Frozen expansion contract

When an optional exact project selector resolves successfully:

1. Build the immutable authorized view first, applying workspace, path/source, note-type,
   sensitivity, and Google destination rules before adjacency is created.
2. Use the selected project as the sole seed.
3. Expand exactly one graph hop over already validated, resolved first-party note
   relationships supported by the released relationship resolver.
4. Include both inbound and outbound direct neighbors where the released resolver can bind
   them unambiguously to one authorized source.
5. Admit at most 25 neighbor notes and at most 26 total notes including the selected
   project.
6. Order eligible neighbors deterministically by stable canonical `source_id`, then current
   relative path. Apply the cap only after authorization, resolution, de-duplication, and
   ordering.
7. Give the resulting authorized bounded note set to the released `QueryEngine`; retrieval
   relevance may rank passages inside that set but may not select identity, expand the
   graph, or override the cap.
8. Preserve the selected project in the authorized candidate set even when it yields no
   supporting passage for a particular question.
9. Apply the existing hard context/prompt budgets after retrieval. Graph caps and token
   budgets are independent limits.

No second-hop traversal, recursive expansion, repository activity expansion, fuzzy target,
unresolved target, duplicate-ID repair, or title-only ambiguity resolution is allowed.
Cycles terminate at the one-hop boundary and through stable-identity de-duplication.

### 3.2 Non-disclosure and failure rules

- Excluded sources cannot appear in or influence visible adjacency, candidates, ranking,
  assumptions, context, citations, conflicts, errors, trace, or omission detail.
- Traversal may not pass through an excluded source to reach an otherwise eligible source.
- A capped authorized neighbor produces only a bounded safe aggregate omission count and
  reason. Do not disclose its identity, title, path, relationship, or sensitivity.
- Missing, malformed, escaped, duplicated, or ambiguously resolved relationship targets are
  not traversed. Use existing typed validation/limitation semantics without guessing.
- Exact current-byte citation validation remains mandatory for every emitted neighbor
  passage at prepare, pre-dispatch, retry, and pre-emission boundaries.

### 3.3 Required regression evidence

Add tests proving:

1. an authorized directly linked project neighbor can be retrieved and cited;
2. authorized inbound and outbound neighbors follow the same deterministic contract;
3. private, restricted, unclassified, wrong-workspace, and path-excluded neighbors cannot
   affect any request-visible surface;
4. traversal cannot cross an excluded intermediary;
5. a second-hop-only note is excluded;
6. cycles terminate and duplicate edges do not duplicate candidates;
7. 25-neighbor and 26-total caps hold at, below, and above the boundary;
8. cap selection is byte-identical under shuffled discovery/edge order;
9. capped omissions disclose only a safe count/reason;
10. duplicate IDs and ambiguous targets fail closed under released identity rules; and
11. no project selector retains ordinary authorized query behavior without implicit
    project expansion.

## 4. Required bounded Engineering action

Engineering is authorized under the existing Handoff 08 scope to:

1. correct the WP1 preparation boundary to implement Decision A;
2. replace the selected-project-only shortcut with Decision B;
3. add the listed focused regression cases;
4. rerun the existing 24 WP1 tests plus all new cases and affected released tests; and
5. keep the worktree dirty and uncommitted while reporting the results and any further
   load-bearing judgment call.

Do not alter the accepted prepare/approval/dispatch ordering to match the current code. The
code must conform to Handoff 07 and this clarification.

## 5. Continued prohibitions

Until the bounded WP1 correction is complete and no new escalation remains:

- do not begin WP2 or WP3;
- do not create a milestone or candidate commit;
- do not install dependencies;
- do not read or use `GEMINI_API_KEY`;
- do not call Google, Ollama, or any external provider;
- do not use network access except the previously authorized official-documentation scope;
- do not modify the historical candidate or Voice Shell;
- do not merge, push, tag, release, perform QA, or begin v0.6.

## 6. Disposition

**APPROVE BOTH DECISIONS.** Separate mock/non-remote preparation from Google credential-
availability preflight, and require bounded one-hop authorized graph-neighbor expansion
before WP1 completion.

After the correction and focused evidence pass, Engineering may resume the already
authorized WP2 and WP3 sequence. It must ultimately return through Handoff 09; this
subordinate clarification does not consume or renumber that handoff.
