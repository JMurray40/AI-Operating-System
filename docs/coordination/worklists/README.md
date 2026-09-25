# Machine-Readable Version Worklists

Read [the full process](../WORKLIST_PROCESS.md) before changing a queue.

## Active Jarvis worklist

[v0.5 Personal Prototype](v0.5-prototype.json)

[v0.5 Full Certification](v0.5-certification.json) is preserved but paused unless the Product
Owner explicitly reactivates certification work.

The completed predecessor queue, [v0.5 Visible-Context Conversation](v0.5.json), is retained
for audit history and is not the active start point.

Validate it from the repository root:

```text
python scripts/validate_worklist.py docs/coordination/worklists/v0.5-prototype.json
```

Start work only when your assigned item is `authorized` or `in_progress`, its dependencies are
accepted, and its `authorization.artifact` exists and actually grants the stated work.

## Reuse

Copy [the template](templates/worklist.json), assign a new `worklist_id`, milestone, task IDs,
paths, owners, and evidence. Complete a
[readiness packet](templates/readiness-packet.json) using the
[End-to-End Readiness Process](../END_TO_END_READINESS_PROCESS.md), then validate before
publishing. Schemas 1.0 and 1.1 remain supported for retained queues; new projects should use 1.2
so the outcome-sized delivery policy is validator-enforced.
