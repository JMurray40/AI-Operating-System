# Multica Setup

Status: active. Staffs the five roles already defined in `GOVERNANCE.md` and
`WAYS_OF_WORKING.md` with persistent Multica agents running the existing Agent Relay
Process (`AGENT_RELAY_PROCESS.md`) and Worklist Process (`WORKLIST_PROCESS.md`) — nothing
about the process itself changes here. This file only assigns runtimes/providers to roles,
plus the Chief of Staff coordination function that already operates in practice (see
`CURRENT_HANDOFF.md`'s "Updated by" field, and `WORKLIST_PROCESS.md`'s queue-owner) but
isn't in `GOVERNANCE.md`'s decision-authority table — it has no decision authority of its
own, only routing (`AGENT_RELAY_PROCESS.md`: "Routing aid only; never grants authority").

## Why this exists

`AGENT_RELAY_PROCESS.md`'s own stated purpose is to "eliminate Product Owner copy-and-paste
handoffs between agents." That's been running manually — Jason relaying
`CURRENT_HANDOFF.md` between separate Claude/GPT chat sessions by hand, capped by each
provider's subscription rate limits. Multica agents on persistent OpenRouter/local runtimes
remove that manual relay without changing any decision authority, review requirement, or
the Product Owner's final say.

## Roster

| Role | Assigned to (per GOVERNANCE.md) | Multica runtime | Decision authority (unchanged) |
|---|---|---|---|
| Product Owner | Jason | Jason — never automated | Vision, priorities, scope approval, risk acceptance, final decisions |
| Chief of Staff | Not in GOVERNANCE.md's table; routing-only | Hermes (Ollama qwen2.5:32b / llama3.3:70b / hermes-3) | None — creates/updates the worklist queue, authorizes tasks after verifying real authority exists, maintains CURRENT_HANDOFF.md. Never itself a decision-authority role. |
| Chief Architect / CTO | GPT | `openai/gpt-6-sol` ($2/$10 per M tokens) — frontier-reasoning tier; `openai/gpt-6-astra` ($10/$50) available for calls that need the top tier | Architecture, product strategy, roadmap, ADR review, technical-debt oversight |
| Principal Engineer | Claude | `x-ai/grok-4.7` ($1.60/$4.80 per M tokens) — positioned for long-running software engineering | Implementation plans, production code, tests, refactoring, performance |
| Quality & Release Manager | GPT or separate reviewer | `anthropic/claude-opus-5.5` ($4/$20 per M tokens) — different lab from both Architect and Engineer, satisfying the independence requirement below | Independent benchmarks, regression analysis, documentation checks, release recommendation |
| Historian / Librarian | GPT or separate reviewer | `z-ai/glm-5.3-flash` ($0.04/$0.14 per M tokens) — reading-comprehension/consistency-checking, not judgment-heavy | Documentation coherence, ADR/PRD consistency, changelog, decision history |

Model names and prices above are verified against the OpenRouter pricing export Jason
pulled and uploaded directly (2026-09-25) — not a web-tool guess. The OpenRouter API is
blocked from every tool available in this Cowork session (confirmed via a direct curl that
returned `blocked-by-allowlist`), so this file is the ground truth; re-export from
openrouter.ai/models periodically since prices move (see the version-tag entries like
`gpt-6-sol` vs `gpt-6-sol-pro` — same price today, may not stay that way).

## What every agent must still do (already fully specified — this file adds nothing here)

Per `AGENT_RELAY_PROCESS.md`'s Start protocol: read `AGENTS.md`,
`docs/coordination/README.md`, and `CURRENT_HANDOFF.md` before any work; open the active
worklist and run its validator; confirm the baton and worklist agree; start only authorized
work assigned to your role.

Per its Return protocol: write the role-owned return/review artifact; update only the
worklist transitions your role may make; rewrite `CURRENT_HANDOFF.md`; run validation;
return only the standard four-line relay message — nothing more (see "Standard agent
return language" in `AGENT_RELAY_PROCESS.md`).

## Independence requirement (GOVERNANCE.md, WAYS_OF_WORKING.md)

Quality & Release and Historian/Librarian must be conducted as passes distinct from
whichever agent played Chief Architect for that piece of work — different model, different
session, starting fresh from the evidence. Do not let the same Multica agent instance play
more than one of {Chief Architect, Quality & Release, Historian} on the same task.

## Not yet done

- `AGENTS.md` (read by every agent as step one of the Start protocol) doesn't yet point at
  this file. Add a line there once the roster above is final, so Multica agents discover
  their runtime assignment the same way they discover everything else — deliberately not
  doing that edit myself without you reading it first.
- The `recovery/coordination-2026-09-25` branch (pushed 2026-09-25) isn't merged to `main`
  yet — that's a Product Owner merge decision, not something this file changes.
