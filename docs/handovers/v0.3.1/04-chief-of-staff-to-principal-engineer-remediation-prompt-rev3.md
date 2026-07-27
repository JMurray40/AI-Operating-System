# Chief of Staff Final Remediation Prompt — Rev 3

| Field | Value |
|---|---|
| Role | Principal Engineer / Claude |
| Milestone | v0.3.1 — Query Trust Contracts |
| Trigger | Final Superseding CTO Revision 3: Refactor first |
| Returned implementation | `47b1a0bf5609d29abb3633273fec2721b853ef45` |
| Required branch | `feature/v0.3.1-query-trust-contracts` |
| QA status | Blocked |
| Required output | Rev 4 in `03-principal-engineer-to-cto-engineering-review.md` |

## Objective

Close only AC-03R3-01 and AC-03R3-02. All other architecture findings and the performance
gate are closed and must not be reopened.

## AC-03R3-01 — Uniform current-source validation

Use the CTO-preferred v0.3.1 design:

- Make `source_root` mandatory for the filesystem-backed `QueryEngine`.
- Update every supported constructor, caller, benchmark, and test.
- A discovery snapshot alone must never produce `coverage="supported"`.
- Preserve resolved-root confinement and fail closed for path/symlink escape,
  missing/unreadable source, and exact-byte mismatch.
- Preserve post-discovery mutation and CRLF/LF/raw-byte tests.

Do not introduce a new repository framework or future non-filesystem resolver in this
release. If making the root mandatory breaks an accepted non-filesystem boundary, stop and
escalate to the CTO.

## AC-03R3-02 — Visible incomplete evidence

- Separate supported passage citations from incomplete source references in text output.
- Never render locator `0-0` as a valid line range.
- Display explicit language that no claim-supporting passage was found.
- Add an answer-level citation-coverage/limitations signal in structured output.
- Ensure incomplete references do not count as valid material citations.
- Ensure exit/status behavior does not represent an incomplete-only answer as fully
  evidence-backed.
- Test CLI text, JSON, mixed supported/incomplete coverage, and incomplete-only answers.

Keep incomplete references authorized, traceable, and visibly distinct. Do not fabricate a
locator or excerpt to upgrade coverage.

## Evidence and exit

Append **Rev 4** to the Engineering Review with:

- correction diff from `47b1a0bf5609d29abb3633273fec2721b853ef45`;
- exact tests for both remaining findings;
- full tests, Ruff, mypy, `git diff --check`, unchanged-vault, and benchmark confirmation;
- exact corrected HEAD;
- confirmation that all earlier closed findings remain closed;
- scope, merge, and push status.

Do not begin QA, merge, push, modify the parked conversation worktree, or expand scope.
Stop for one final CTO conformance review.

## Exit statement

**Ready for final bounded engineering correction.** QA remains blocked.
