# V05-PT-32 Product Owner Acceptance and Next-gate Authorization

| Field | Value |
|---|---|
| Date | 2026-08-14 |
| Decision maker | Product Owner |
| PT32 | **ACCEPTED** |
| PT33 | **REVERSIBLE LOCAL-RUNTIME CONFINEMENT AUTHORIZED** |
| PT34 | **SYNTHETIC-ONLY `gemma4:12b` EVALUATION PRE-AUTHORIZED; BLOCKED UNTIL PT33 CTO ACCEPTANCE** |

The Product Owner approves all five recommendations in Handoff 141. The accepted PT32 evidence does
not approve the current Ollama host posture or authorize sensitive-data use. Local sensitive
generation remains blocked until the exact confinement and later profile gates are independently
accepted.

PT33 may perform the exact reversible native-Windows confinement correction defined by Handoff 141,
including narrowly scoped elevation for the named firewall operations. It must capture and bind the
before state and rollback procedure, confine the existing Ollama executable to loopback, remove only
the proven Ollama inbound allowances, add the exact-program outbound deny, prove loopback health
without loading a model, prove LAN and non-loopback denial, and stop for CTO review.

PT34 is pre-authorized but remains blocked until the CTO independently accepts PT33. It may then
evaluate only the exact, fully bound `gemma4:12b` candidate with synthetic prompts and synthetic
context. It may not use vaults, personal notes, conversation history, private data, or a fallback
model. The predeclared personal-use thresholds are:

- median terminal response latency no greater than 20 seconds;
- p95 terminal response latency no greater than 45 seconds; and
- at least 80 percent of the fixed quality-rubric points, with zero critical safety, privacy,
  unsupported-claim, or instruction-following failures.

No profile is automatically activated after evaluation. Production use still requires a later
exact Product Owner profile decision. This approval does not authorize installation, download,
update, model acquisition, private-data exposure, Jarvis executable changes, packaging,
certification, merge, push, publication, or release.
