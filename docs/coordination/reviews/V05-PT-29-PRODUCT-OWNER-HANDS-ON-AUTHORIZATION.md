# V05-PT-29 Product Owner Interactive Hands-on Authorization

| Field | Value |
|---|---|
| Date | 2026-08-14 |
| Decision | `PO-05-INTERACTIVE-HANDS-ON` |
| Candidate | `08b0b11383031d6e91f6f26145bfdffc710ca36b` |
| Tree | `df041615730ee65faa6001f717f2ccff3b8d726c` |
| Mode | Offline, synthetic fixture, mock Core only |

The Product Owner's instruction to continue authorizes one hands-on interaction with the accepted
mock-only frontend. The purpose is to judge whether the interaction flow is understandable and
useful enough to justify planning the next capability—not to evaluate model intelligence or live
provider quality.

## Run

From the accepted J.A.R.V.I.S recovery worktree, run:

```text
C:\Users\jmurr\Projects\J.A.R.V.I.S\venv\Scripts\python.exe -m voice_shell.cli --core-mock --fixture synthetic
```

Use the commands printed for the current state. Try at least:

1. Ask a natural-language question.
2. `inspect` the visible context.
3. Optionally `remove 2`, then inspect again.
4. `approve`, then `poll` until the mock result completes.
5. Try `retry`, `cancel`, `decline`, and `reset` when offered.
6. End with `quit`.

Record only usability observations: what was clear, confusing, missing, or unexpectedly cumbersome.
Do not enter credentials, private data, real vault paths, or secrets. Do not activate network,
Gemini, real audio, tools, packaging, certification, merge, push, publication, or release work.

The expected answer content is deterministic mock output. This task evaluates the frontend workflow,
approval boundary, visible context, state guidance, and cleanup—not a real conversational model.
