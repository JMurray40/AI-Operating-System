# Prepared Prompt — Read-Only Engineering Scope Monitor

**May run while engineering is active. This is not a code review or approval gate.**

Act as a Chief-of-Staff scope monitor. Inspect only committed state on
`feature/v0.4-project-resume`; never read or judge Claude's uncommitted work unless Jason
explicitly authorizes that inspection.

Compare new commits against immutable base
`3253b052a3986e7d2c94124fbac86c03980e0765`, the authorization, final CTO brief,
ADR-0018 through ADR-0021, and explicit exclusions.

Report only objective signals:

- branch/worktree identity and cleanliness visible from committed state;
- commit count and changed-path categories;
- presence of provider/chat/conversation/network/GitHub/write/agent/plugin/MCP/automation
  paths or imports;
- changes outside the affected-file forecast;
- changes to accepted ADRs or release gates;
- missing logical handoff/evidence artifacts as completion approaches;
- accidental ancestry from the parked conversation branch; and
- divergence from immutable base or unauthorized push/merge.

Do not modify files, stage, commit, reset, stash, rebase, run destructive commands, or
interrupt engineering for a speculative concern. Escalate only concrete evidence with
commit/path references. Treat ordinary in-scope implementation growth as expected.

Produce a dated read-only status note outside the engineering branch or report directly
to the Chief of Staff. A monitor report cannot clear CTO or QA gates.
