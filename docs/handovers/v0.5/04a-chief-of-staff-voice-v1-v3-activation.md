# Handoff 04a — Chief of Staff Voice V1–V3 Activation

| Field | Value |
|---|---|
| Product Owner authority | Jason approved Handoff 04 on 2026-08-02 |
| V1 reconciled baseline | `codex/voice-shell-safety-baseline@bb3bae1eb49222732e4fceb886584ab18b7efedc` |
| V2 starting candidate | `codex/security-boundary-phase1@bb1222b0a52387e894d53a296f691c51de70c23a` |
| V3 starting candidate | `codex/voice-shell-phase1@f32499a815143a1e892356706e38644557c946de` |
| V4 | Not authorized |

## V1 disposition

**Complete.** The root worktree is clean at `bb3bae1`. The local `.env`, `config.json`,
`credentials.json`, `token_business.json`, `token_personal.json`, `.voice_state`, virtual
environment, exchange folders, and worktree container are ignored and remain outside the
candidate histories. No secret value was read or recorded.

`.voice_state` was the sole exception discovered: it was a four-byte tracked runtime-state
artifact introduced in the initial commit. It contained no parseable state or secret
fields. V1 removed it from tracking while preserving its local bytes and corrected the
underscore exchange-folder and `.worktrees/` ignore rules.

The two existing candidates remain clean and unchanged. V1 does not rebase, merge, or
authorize either candidate.

## Activated work

- V2 is authorized only through [Handoff 04b](04b-engineer-1-whole-runtime-quarantine-prompt.md).
- V3 is authorized only through [Handoff 04c](04c-engineer-2-bridge-shaped-mock-contract-prompt.md).
- V2 and V3 remain isolated and must not import, merge, call, or depend on each other.

Each lane must stop after its bounded correction and independent evidence. The Chief of
Staff and CTO must accept both exact candidates before V4 can be proposed.

## Continued prohibitions

No real audio, STT, TTS, model, provider, credential, vault, connector, tool, memory,
browser, subprocess, system control, network, push, merge, release, or Jarvis Core
connection is authorized. V4 and V5 remain closed.
