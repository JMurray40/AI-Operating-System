# V05-PT-29 Product Owner Hands-on Return

| Field | Value |
|---|---|
| Date | 2026-08-14 |
| From | Product Owner |
| To | Chief of Staff |
| Task | `V05-PT-29` |
| Status | **READY FOR REVIEW** |

## Observations

The Product Owner successfully exercised the visible options and found the mechanics understandable.
The mock context makes it difficult to judge how useful real operations will feel.

The principal product finding is that per-turn permission to send ordinary context to the selected
LLM is conceptually at odds with the intended experience: JARVIS is expected to be an agent connected
to an LLM, not a workflow that requires repeated routine egress approval.

## Recommended next design decision

Preserve visible context and user control, but replace mandatory approval on every ordinary turn with
a Product Owner-defined standing trust policy. A likely personal-use profile would:

- approve one provider, endpoint, project scope, and maximum sensitivity tier up front;
- automatically use eligible context within that standing envelope;
- keep a concise, inspectable record of what context was used;
- ask again only when the request crosses the envelope, such as a new provider, higher sensitivity,
  unusually broad context, a write/tool action, or another materially higher-risk operation; and
- retain an optional strict per-turn approval mode.

This would preserve the safety architecture while making normal interaction agent-like. It requires
a separately authorized CTO product/architecture decision before any implementation or live Gemini
pilot.

No live capability, credential, private data, candidate modification, or release action occurred.
