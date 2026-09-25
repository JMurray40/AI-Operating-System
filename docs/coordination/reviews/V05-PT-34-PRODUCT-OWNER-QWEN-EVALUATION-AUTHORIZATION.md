# V05-PT-34 Product Owner qwen2.5:7b Evaluation Authorization

| Field | Value |
|---|---|
| Date | 2026-08-15 |
| Decision maker | Product Owner |
| PT34 | **ACCEPTED; `gemma4:12b` REMAINS REJECTED** |
| PT35 | **FORMAL SYNTHETIC-ONLY `qwen2.5:7b` EVALUATION AUTHORIZED** |

The Product Owner authorizes one formal evaluation of the already-installed general model
`qwen2.5:7b` after an informal synthetic screen indicated materially better responsiveness. The
informal screen is not acceptance evidence and does not activate a profile.

PT35 must preserve the Handoff 144 boundaries and unchanged predeclared gates:

- median terminal latency no greater than 20 seconds;
- p95 terminal latency no greater than 45 seconds;
- quality at least 80/100;
- zero critical safety, privacy, unsupported-claim, or instruction-following failures;
- exact runtime, manifest, blob, parameter, and license binding;
- PT33 confinement drift checks before every sample group;
- explicit typed context-limit and concurrent-request-denial outcomes; and
- complete raw sample, timeout, cancellation, resource, stability, quality, and network evidence.

The task may use only fixed synthetic prompts and context. It authorizes no private data, vault,
personal note, conversation history, fallback model, installation, download, update, Jarvis change,
or automatic profile activation. Any resulting profile requires later CTO review and a separate
Product Owner decision.
