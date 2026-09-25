# V05-PT-39 Product Owner Tokenizer Setup Authorization

| Field | Decision |
|---|---|
| Date | 2026-08-21 |
| Decision | **OPTION A APPROVED** |
| Plain-language meaning | Get the missing tokenizer software and matching Qwen tokenizer data, verify them, and install them only in a separate test environment |
| Decision source | Product Owner response to Handoff 160 |

The Product Owner approves Option A from
[Handoff 160](../../../.worktrees/v0.3.1-release/docs/handovers/v0.5/160-cto-to-product-owner-qwen-tokenizer-acquisition-decision.md).

In this authorization, **acquisition** means only:

1. download or receive the minimum missing tokenizer software and matching Qwen2
   tokenizer data from explicitly approved sources;
2. record the source, name, version, license, file size, dependency list, and SHA-256
   digest of every obtained file;
3. scan and inspect the files before use; and
4. install them into a new, isolated, evidence-only environment that does not modify
   the accepted Core or Voice environments or tracked dependency files.

This approval does not imply a purchase and authorizes no model download, model load,
inference, prompt execution, Ollama/provider request, private-data access, profile
activation, fixture generation, integrated evidence run, candidate change, tracked
dependency change, daemon/firewall change, Gemini/fallback use, merge, push,
publication, packaging, certification, or release.

Chief of Staff may now define one exact tokenizer-setup task within Handoff 160 Section
3. That task must name or tightly allowlist the permitted sources and artifacts, keep
all writes isolated from accepted candidates, stop on unexpected dependencies or
provenance/license/hash issues, and return the exact inventory for independent CTO
review before any tokenizer tables or synthetic evidence fixtures are produced.

V05-PT-39 remains blocked. A separately authorized successor may resume the tokenizer
identity prerequisite only after the acquired inventory is independently accepted.
