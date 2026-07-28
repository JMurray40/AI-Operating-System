# Prepared Prompt — Quality & Release Review

**Inactive until:** the CTO clears exact candidate `<CANDIDATE_SHA>` and produces
`03-cto-to-quality-architecture-disposition.md`.

Act as independent Quality & Release. Ask: what evidence says this v0.4 candidate should
not ship?

Use a clean detached worktree at `<CANDIDATE_SHA>`. Read Project Control, the v0.4 index,
accepted tests A1–A12, ADR-0012 and ADR-0014 through ADR-0021, the final CTO brief,
engineering handoff, and latest CTO disposition. Verify claims directly; do not defer to
the architect or conversation history.

Adversarially execute:

- identity tier, collision, duplicate-ID, and non-disclosure cases;
- restricted project/evidence/Git influence across all outputs;
- authority, date, supersession, conflict, stale, unknown, and incomplete cases;
- current-byte citation mutation/deletion/escape cases;
- exact evidence and serialized-output budget boundaries;
- semantic byte determinism and trace/error redaction;
- ADR-0021 command, path, environment, timeout, overflow, parser, injection, missing-Git,
  stale, and before/after repository-integrity cases;
- CLI text/JSON/help/exit behavior and v0.3.1 compatibility;
- full tests, Ruff, mypy, whitespace, packaging, recovery, and clean-install evidence;
- retained raw benchmark arithmetic, pilot gates, privacy/redaction, and unchanged sources;
- A11 consent/manual workflow, with eight-week strategic outcome still pending; and
- exclusions: no conversation, provider, network, write, agent, plugin, MCP, or automation.

Do not implement fixes, change evidence, merge, push, release, or touch the parked branch.

Produce:

```text
docs/handovers/v0.4/04-quality-to-product-owner-release-review.md
```

End with exactly one disposition: `Ready`, `Ready with conditions`, `Refactor first`,
`Not ready`, or `Re-scope`.
