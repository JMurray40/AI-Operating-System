# Agent Start Rule

Before performing project work:

1. Read `docs/coordination/README.md`.
2. Read `docs/coordination/CURRENT_HANDOFF.md`. This is the canonical baton identifying the
   active worklist, current task, latest return, next role, and required action.
3. Read the active file under `docs/coordination/worklists/` named by the baton.
4. Run `python scripts/validate_worklist.py <active-worklist>`.
5. Start only a task assigned to your role with status `authorized` or `in_progress`.
6. Open and verify the task's linked authorization artifact; neither the baton nor JSON grants
   authority.
7. Follow the task's scope, exclusions, evidence, output, and stop conditions exactly.
   An authorized task is an outcome-sized work unit: complete in-scope diagnosis, correction,
   tests, and review-ready evidence before returning. Internal defects are not handoff events.
8. Before stopping, update `docs/coordination/CURRENT_HANDOFF.md` using
   `docs/coordination/AGENT_RELAY_PROCESS.md` and update the worklist as permitted by your role.
9. End with the exact concise return format defined in the Agent Relay Process. Do not paste
   technical summaries into chat; the repository handoff is the report.
10. Do not mark your own work `accepted` or authorize a dependent task.
11. Return early only for the permitted categories in `AGENT_RELAY_PROCESS.md`. Reviewers must
    inspect the complete submission and issue one consolidated punch list.

The full reusable process is `docs/coordination/WORKLIST_PROCESS.md`. Product Owner decisions,
accepted ADRs and requirements, and handoffs take precedence over the worklist.
