# v0.3.1 Handoff Index — Latest Effective State

| Field | Value |
|---|---|
| Milestone | v0.3.1 — Query Trust Contracts |
| Status | Active; release blocked pending retained performance evidence |
| Owner | Chief of Staff |
| Updated | 2026-07-27 |
| Branch | `feature/v0.3.1-query-trust-contracts` |
| Executable candidate under evidence review | `956c2ed1dd1144e836014b049a89c47e971818a0` |
| Coordination lineage | Evidence-routing state begins at `3918257ba1f5325b2f56f89a81574c4144c6004f`; verify the current worktree HEAD at startup |

## Current effective state

| Item | Effective state |
|---|---|
| Lifecycle stage | Engineering evidence correction |
| Next responsible role | Principal Engineer / Claude |
| Current incoming artifact | [Performance Evidence Correction](06-chief-of-staff-to-principal-engineer-evidence-correction.md) |
| Required next output | Retained raw JSON plus Evidence Addendum to Engineering Review Rev 6 |
| Architecture | Trust-contract implementation cleared; QR-031-01 and QR-031-02 closed |
| QA | `Refactor first`; rerun not yet authorized |
| Sole open gate | QR-031-03 — retain raw paired samples and bind derived results to the exact execution |
| Merge/release | Prohibited |
| Parked conversation work | Out of scope and untouched |

Do not start QA, Product Owner release decision, Librarian closeout, v0.4 implementation,
or conversation reconciliation from this state.

## Current evidence contract

The Principal Engineer must produce:

```text
docs/evidence/v0.3.1/paired-performance-956c2ed-vs-ce0dc35.json
```

The artifact must retain all candidate and baseline samples for five paired attempts,
record execution identities and conditions, support independent recomputation, and be
bound to the Engineering Review addendum by SHA-256.

After that:

1. CTO reviews only evidence integrity, arithmetic, digest, and executable-file diff.
2. If cleared, QA reruns affected matrix areas A, G, and H.
3. QA issues a superseding disposition to the Product Owner.

## Latest effective revisions

Read the latest named revision first. Earlier sections preserve history.

| Artifact | Latest effective revision/state |
|---|---|
| [Engineering Review](03-principal-engineer-to-cto-engineering-review.md) | Rev 6; pending Evidence Addendum |
| [CTO Architecture Disposition](04-cto-to-quality-architecture-disposition.md) | **Evidence correction required**; QR-031-03 open |
| [Quality & Release Review](05-quality-to-product-owner-release-review.md) | **Refactor first**; superseding QA review pending |
| [Project Control](../../coordination/README.md) | Evidence correction assigned to Principal Engineer |

## Artifact map

### Governing and accepted

| Sequence | Artifact | Status |
|---:|---|---|
| 00 | [Chief of Staff to CTO](00-chief-of-staff-to-cto-finalize-implementation-brief.md) | Historical startup handoff |
| 01 | [Product Owner approval](01-product-owner-to-cto-architecture-approval.md) | Accepted |
| 02 | [CTO implementation brief](02-cto-to-principal-engineer-implementation-brief.md) | Accepted and implemented |
| 02 | [Validated Engineer prompt](02-chief-of-staff-to-principal-engineer-validated-prompt.md) | Historical execution prompt |

### Cumulative lifecycle evidence

| Sequence | Artifact | Current interpretation |
|---:|---|---|
| 03 | [Engineering Review](03-principal-engineer-to-cto-engineering-review.md) | Read Rev 6; add evidence addendum next |
| 04 | [CTO disposition](04-cto-to-quality-architecture-disposition.md) | Latest evidence disposition governs |
| 05 | [QA review](05-quality-to-product-owner-release-review.md) | `Refactor first`; superseding rerun blocked |

### Chief of Staff prompts

| Artifact | Status |
|---|---|
| [Initial remediation](04-chief-of-staff-to-principal-engineer-remediation-prompt.md) | Superseded |
| [Remediation Rev 2](04-chief-of-staff-to-principal-engineer-remediation-prompt-rev2.md) | Superseded |
| [Remediation Rev 3](04-chief-of-staff-to-principal-engineer-remediation-prompt-rev3.md) | Superseded |
| [Remediation Rev 4](04-chief-of-staff-to-principal-engineer-remediation-prompt-rev4.md) | Superseded |
| [QA review prompt](05-chief-of-staff-to-quality-release-review-prompt.md) | Historical |
| [QA remediation](05-chief-of-staff-to-principal-engineer-qa-remediation.md) | Superseded |
| [Performance evidence correction](06-chief-of-staff-to-principal-engineer-evidence-correction.md) | **Current** |

## Next-file rule

The next new lifecycle file is not created until the current evidence gate closes.
Engineering Review receives an Evidence Addendum. CTO and QA append superseding revisions
to their existing cumulative artifacts.

After a Product Owner release decision, create:

```text
docs/handovers/v0.3.1/06-product-owner-to-librarian-release-decision.md
```
