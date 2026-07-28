# Executive Product and Architecture Summary

| Field | Value |
|---|---|
| Purpose | Summarize the future product documentation and decisions requiring leadership attention |
| Status | Draft for review |
| Version | 1.0.0 |
| Owner | Chief Product Officer / Principal Systems Architect |
| Revised | 2026-07-27 |
| Baseline | Jarvis Core v0.1.0 |

## Overall conclusion

Version 0.1 is the right prototype: deterministic, typed, read-only, provider-neutral at a small seam, and tested against mutation. The next risk is not lack of features. It is extending minimal prototype contracts until they accidentally become permanent platform contracts.

The product should concentrate on one trusted loop:

> Resume or search → inspect context and sources → work with an AI → approve a durable outcome → return later and resume faster.

Agents, plugins, MCP, automation, mobile, and voice should extend that loop only after identity, sensitivity, policy, provenance, operational state, and rollback are explicit.

## Five highest-priority recommendations

1. **Freeze and publish platform boundary schemas before network or write features.** Define entity identity, Context Package v1, source/provenance, provider request/events, capability grants, and audit events. Otherwise each new feature will invent incompatible contracts.
2. **Implement sensitivity and egress policy before the first real cloud provider.** Enforcement must occur at source read, context assembly, provider dispatch, tool execution, result ingestion, and memory write.
3. **Build indexed lexical retrieval and a benchmark before semantic search.** SQLite FTS plus rebuildable projections is the simplest credible path to 100k+ notes; hybrid search must prove improvement on judged queries.
4. **Keep every future effect behind one capability-enforced Tool Gateway.** Native tools, plugins, MCP, agents, and automation must share permission, approval, secret, audit, timeout, and cancellation infrastructure.
5. **Make proposed memory the first write feature.** Exact diffs, expected hashes, atomic writes, verified backups, conflict detection, and rollback should be proven before any general automation.

## Five largest risks

1. **Prompt injection and data exfiltration:** hostile instructions can arrive through notes, web, email, repositories, MCP descriptions, and tool outputs.
2. **Scope dilution:** simultaneous pursuit of chat, voice, agents, mobile, enterprise, and marketplace could prevent Project Resume from becoming indispensable.
3. **Identity ambiguity:** name/alias/stem resolution can silently associate the wrong note as the corpus grows.
4. **Administrative burden:** metadata, approvals, and dashboards may cost more time than they save.
5. **Unsafe extensibility:** in-process plugins or direct MCP-to-model wiring would turn the vault and credentials into a supply-chain attack surface.

## Five most valuable future features

1. **Project Resume briefing:** sourced current state, decisions, sessions, repository activity, questions, and next action.
2. **Visible-context chat:** provider-neutral conversation with inspectable sources, sensitivity, citations, latency, and cost.
3. **Proposed Memory:** reviewed session summaries, decisions, and project updates that improve the vault without transcript dumping.
4. **Relationship intelligence:** high-precision shared-concept and contradiction candidates with evidence.
5. **Approval-driven automation:** durable, idempotent workflows for briefings, capture, and project maintenance.

## Decisions required before additional coding

| Decision | Why now | Recommended status |
|---|---|---|
| Stable entity identity and collision behavior | Current first-writer name resolution cannot scale safely | ADR before v0.2 |
| Context Package v1 schema and owner | Chat/search/provider clients will depend on it | ADR before v0.2 |
| Search projection and SQLite FTS boundary | Avoids database becoming canonical | ADR before v0.2 |
| Sensitivity labels and provider egress | Required before cloud AI sees vault content | ADR before v0.3 |
| Provider protocol v1 | `summarize()` cannot support chat/streaming/tools | ADR before v0.3 |
| Operational DB/event/audit model | Conversations, approvals, agents, and workflows depend on it | ADR before v0.3 |
| Atomic write and approval transaction | Required before memory | ADR before the future memory release |
| Plugin isolation and capability model | Required before plugins/MCP | ADR before v0.7 |
| Agent budget/delegation semantics | Required before multi-agent work | ADR before v0.8 |

## Documentation delivered

- [Product Strategy](product/PRODUCT_STRATEGY.md)
- [Version Roadmap](product/VERSION_ROADMAP.md)
- [Ten capability PRDs](prd/README.md)
- [Enterprise Architecture Review](reviews/ENTERPRISE_ARCHITECTURE_REVIEW.md)
- [Product and Platform Review](reviews/PRODUCT_AND_PLATFORM_REVIEW.md)
- [Eight Agent Specifications](agents/AGENT_SPECIFICATIONS.md)
- [Plugin SDK Specification](sdk/PLUGIN_SDK_SPECIFICATION.md)
- [Security Threat Model](reviews/SECURITY_THREAT_MODEL.md)
- [Developer Experience Strategy](DEVELOPER_EXPERIENCE_STRATEGY.md)
- [100-item Future Research Backlog](../research/FUTURE_RESEARCH_BACKLOG.md)

## Recommended immediate sequence

1. Review and accept/revise this package.
2. Convert the nine pre-coding decisions above into ADRs in priority order.
3. Align Claude’s active implementation branch with the accepted v0.2 boundary decisions.
4. Create the retrieval benchmark and synthetic scale corpus.
5. Implement v0.2 only; keep cloud providers, writes, plugins, agents, and automation out of scope until their gates are met.

## Revision history

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-07-27 | Initial executive summary |
