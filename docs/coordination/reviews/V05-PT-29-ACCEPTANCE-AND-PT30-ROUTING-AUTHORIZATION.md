# V05-PT-29 Acceptance and PT30 Sensitivity-aware Routing Authorization

| Field | Value |
|---|---|
| Date | 2026-08-14 |
| Product Owner direction | `PO-05-SENSITIVITY-AWARE-ROUTING` |
| Accepted candidate | `08b0b11383031d6e91f6f26145bfdffc710ca36b` |
| PT29 disposition | **ACCEPTED** |
| PT30 disposition | **CTO PLANNING AUTHORIZED; IMPLEMENTATION NOT AUTHORIZED** |

Chief of Staff accepts the completed Product Owner hands-on evaluation. The frontend mechanics are
usable, and the primary product finding is accepted: routine per-turn LLM egress approval is too
onerous for the intended agent experience.

The Product Owner clarifies the desired operating model:

- eligible ordinary context may use the approved Google/Gemini destination under a standing policy;
- sensitive context should route to an approved local Ollama model when possible;
- local-model unavailability must fail closed or ask the user what to do, never silently send the
  sensitive context to Gemini;
- route and context remain inspectable, with explicit approval reserved for policy crossings,
  higher-risk actions, and user-selected strict mode; and
- the experience need not be completely seamless, but normal use should feel agent-like.

PT30 authorizes the CTO to reconcile this goal with the accepted destination-before-retrieval,
sensitivity, visible-context, approval-binding, and provider-boundary contracts. The CTO must assess
local Ollama feasibility, propose the model/profile selection rule, define failure and override
semantics, identify required ADR/requirements changes, and return one bounded implementation path.

No Ollama installation, model download, live provider call, credential use, candidate change, Core
change, packaging, certification, merge, push, publication, or release is authorized.
