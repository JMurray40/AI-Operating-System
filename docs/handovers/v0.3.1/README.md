# v0.3.1 Handoff Index — Latest Effective State

| Field | Value |
|---|---|
| Milestone | v0.3.1 — Query Trust Contracts |
| Status | Merged locally; Librarian closeout required before final release |
| Owner | Chief of Staff |
| Updated | 2026-07-27 |
| Merged branch | `main` at `00f181312b92cc59f20407fec6db1d1a3da09ec0` |
| Executable candidate under evidence review | `956c2ed1dd1144e836014b049a89c47e971818a0` |
| Coordination lineage | Evidence-routing state begins at `3918257ba1f5325b2f56f89a81574c4144c6004f`; verify the current worktree HEAD at startup |

## Current effective state

| Item | Effective state |
|---|---|
| Lifecycle stage | Post-merge Historian / Librarian closeout |
| Next responsible role | Historian / Librarian |
| Current incoming artifact | [Post-merge Librarian prompt](07-chief-of-staff-to-librarian-post-merge-closeout.md) |
| Required next output | `07-librarian-to-product-owner-repository-closeout.md` |
| Architecture | Ready for limited revalidation; QR-031-01 through QR-031-03 closed |
| QA | **Ready**; affected Areas A, G, and H passed |
| Evidence | Executable `956c2ed`; evidence commit `8fa5f18`; artifact digest verified |
| Merge/release | Merged locally at `00f1813`; push, tag, and release await Librarian closeout |
| Parked conversation work | Out of scope and untouched |

Do not push, tag, release, begin v0.4 implementation, or reconcile conversation work until
the Librarian closeout is complete and accepted.

## Accepted evidence contract

The Principal Engineer produced:

```text
docs/evidence/v0.3.1/paired-performance-956c2ed-vs-ce0dc35.json
```

The artifact must retain all candidate and baseline samples for five paired attempts,
record execution identities and conditions, support independent recomputation, and be
bound to the Engineering Review addendum by SHA-256.

The CTO verified evidence integrity, arithmetic, digest, executable-file diff, and the
predeclared aggregation rule. QA independently revalidated affected Areas A, G, and H and
issued `Ready`. The Product Owner approved controlled merge; the merge completed locally
and now awaits Librarian closeout before push, tag, or release.

## Latest effective revisions

Read the latest named revision first. Earlier sections preserve history.

| Artifact | Latest effective revision/state |
|---|---|
| [Engineering Review](03-principal-engineer-to-cto-engineering-review.md) | Rev 6 with Evidence Addendum complete |
| [CTO Architecture Disposition](04-cto-to-quality-architecture-disposition.md) | **Ready for limited Quality & Release revalidation** |
| [Quality & Release Review](05-quality-to-product-owner-release-review.md) | **Ready**; superseding A/G/H revalidation complete |
| [Project Control](../../coordination/README.md) | Post-merge Librarian closeout assigned |

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
| 03 | [Engineering Review](03-principal-engineer-to-cto-engineering-review.md) | Read Rev 6 and its Evidence Addendum |
| 04 | [CTO disposition](04-cto-to-quality-architecture-disposition.md) | Latest limited-QA clearance governs |
| 05 | [QA review](05-quality-to-product-owner-release-review.md) | Latest superseding revision is `Ready` |
| 06 | [Product Owner decision](06-product-owner-to-librarian-release-decision.md) | **Approved for controlled merge** |

### Chief of Staff prompts

| Artifact | Status |
|---|---|
| [Initial remediation](04-chief-of-staff-to-principal-engineer-remediation-prompt.md) | Superseded |
| [Remediation Rev 2](04-chief-of-staff-to-principal-engineer-remediation-prompt-rev2.md) | Superseded |
| [Remediation Rev 3](04-chief-of-staff-to-principal-engineer-remediation-prompt-rev3.md) | Superseded |
| [Remediation Rev 4](04-chief-of-staff-to-principal-engineer-remediation-prompt-rev4.md) | Superseded |
| [QA review prompt](05-chief-of-staff-to-quality-release-review-prompt.md) | Historical |
| [QA remediation](05-chief-of-staff-to-principal-engineer-qa-remediation.md) | Superseded |
| [Performance evidence correction](06-chief-of-staff-to-principal-engineer-evidence-correction.md) | Completed |
| [Limited QA revalidation](07-chief-of-staff-to-quality-limited-revalidation.md) | Completed |
| [Post-merge Librarian closeout](07-chief-of-staff-to-librarian-post-merge-closeout.md) | **Current** |

## Next-file rule

The next required lifecycle file is:

```text
docs/handovers/v0.3.1/07-librarian-to-product-owner-repository-closeout.md
```

After that closeout is committed, final push, tag, and release remain Product
Owner-controlled.
