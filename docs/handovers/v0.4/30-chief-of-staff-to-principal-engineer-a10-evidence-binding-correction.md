# Handoff 30 — Chief of Staff to Principal Engineer: A10 Evidence-binding Correction

**Date:** 2026-07-29

**Disposition:** **EVIDENCE CORRECTION REQUIRED — NO A10 RERUN**

**Executable:** `ff402d7f82c061426a5e960f7177d916c355bbf2`

**Evidence commit reviewed:** `65264af50e375c0bd8e5d1618cfc89b70891df6d`

## Validated results

- Exact executable ancestry, three-file committed scope, branch, and clean worktree validate.
- The private manifest's eight raw artifacts all match their recorded filenames, sizes, and
  SHA-256 values.
- All three 30-sample warm total arrays independently recompute to the published
  p50/p95/p99 values.
- A10-01 through A10-30 are mapped, with A10-12 and the topology portion of A10-19
  explicitly unavailable.
- No performance, pilot, integrity, or candidate rerun is required by this handoff.

## EC-01 — Committed artifact identities are incorrect

The handoff and private manifest record hashes and sizes from pre-commit working files.
Git normalized the committed content. The stated identities therefore do not bind the
reviewed blobs.

Actual `git show 65264af:<path>` identities are:

| Committed artifact | Size | SHA-256 |
|---|---:|---|
| `docs/evidence/v0.4/project-resume-performance-ff402d7.json` | 15,280 | `dc16254ab231560be851cce0714af2e4fd99a16f9d9370e484f672df73a7dad8` |
| `docs/evidence/v0.4/pilot-evaluation-ff402d7.json` | 9,430 | `16cc38e7258abade676f3a827627f700d8c3e6567f760988f9d6ff0c00598b44` |
| `docs/handovers/v0.4/02-principal-engineer-to-cto-engineering-review.md` | 9,476 | `3f3a0e168508e224e8f7bf407b91f61d57d823c78cdf01541d8ff65652fc2446` |

Because EC-02 requires a public-artifact correction, do not merely substitute the first two
hashes above. Recompute their final committed blob sizes and SHA-256 values after the privacy
correction commit, then bind those final identities in the Engineering handoff and private
manifest.

## EC-02 — Public artifact contains prohibited classification detail

`docs/evidence/v0.4/pilot-evaluation-ff402d7.json` contains authorization objects with:

```text
max_sensitivity: restricted
```

Handoff 28 Section 8 prohibits classification detail in committed artifacts. Remove the
classification detail from every public mode. Prefer removing the entire authorization object
unless an individual non-sensitive field is necessary to support a matrix row. Do not replace
it with another sensitivity or classification label.

Re-run the public privacy scan against final committed bytes. Confirm no absolute path,
passage, unapproved note name, task text, Git subject/author/remote, username, sensitivity,
classification, credential, or raw error remains.

## Required correction

Create one documentation/evidence-only child commit of `65264af` changing only:

- `docs/evidence/v0.4/pilot-evaluation-ff402d7.json`;
- `docs/handovers/v0.4/02-principal-engineer-to-cto-engineering-review.md`; and
- the private ignored `a10-manifest.json`.

The performance JSON need not change unless required to correct another verified metadata
field. Its final committed blob identity must still be recorded accurately.

Use a binary-safe method that hashes the exact committed blob bytes, not a checked-out
working file or text pipeline. Record the command/method used.

Return:

- correction commit and exact parent;
- changed-file list;
- final `git show <commit>:<path>` size/SHA-256 for both committed JSON artifacts and the
  handoff;
- updated private manifest size/SHA-256 and verification result;
- final public privacy-scan result;
- `git diff --check`; and
- clean worktree confirmation.

Freeze and stop for Chief of Staff validation.

## Still closed

No A10 rerun, candidate, wheel, test, script, benchmark, protocol, pilot, classification,
or unrelated change is authorized. No CTO review, QA, merge, push, tag, release,
publication, or v0.5 work may begin.
