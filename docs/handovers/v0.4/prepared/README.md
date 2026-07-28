# v0.4 Prepared Prompt Pack

These prompts are prepared coordination assets. They are **inactive** until their stated
activation condition is satisfied. Preparing a prompt does not authorize its role, change
the current lifecycle stage, or permit access to Claude's active engineering worktree.

| Prompt | Activation |
|---|---|
| [CTO architecture review](01-cto-architecture-conformance-review.md) | Principal Engineer handoff complete and exact candidate frozen |
| [Quality & Release review](02-quality-release-review.md) | CTO clears the exact candidate for QA |
| [Pilot-readiness audit](03-pilot-readiness-audit.md) | May run read-only while engineering is active |
| [Packaging and recovery review](04-packaging-recovery-review.md) | Candidate packaging instructions and artifacts exist |
| [A11 dogfood operations](05-a11-dogfood-operations.md) | Collection mechanism/template exists; no silent collection |
| [Librarian closeout](06-librarian-closeout.md) | Product Owner approves and candidate is merged locally |
| [Engineering scope monitor](07-engineering-scope-monitor.md) | May run read-only while engineering is active |
| [Deferred-risk register](08-deferred-risk-register.md) | May run read-only; updates require evidence |

Before activating a prompt, the Chief of Staff replaces every `<PLACEHOLDER>`, verifies
the current coordination index, and records the exact branch, worktree, base, candidate,
and incoming handoff.
