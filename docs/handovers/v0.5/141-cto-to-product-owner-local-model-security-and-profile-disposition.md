# Handoff 141 - CTO to Product Owner: Local-model Security and Profile Disposition

| Field | Value |
|---|---|
| Date | 2026-08-14 |
| From | Chief Architect / CTO |
| To | Product Owner |
| Milestone | v0.5 Personal Prototype |
| Task | `V05-PT-32` |
| Disposition | **PT32 EVIDENCE ACCEPTED; LOCAL PROFILE NOT APPROVED** |
| Frozen executable | `08b0b11383031d6e91f6f26145bfdffc710ca36b` |
| Documentation pin | `d345910f6239f5707975c77c45ea3759249d145e` |
| Evidence reviewed | [Handoff 140](140-principal-engineer-to-cto-local-model-feasibility-return.md) |
| Governing architecture | [Handoff 138](138-cto-to-product-owner-sensitivity-aware-provider-routing-disposition.md), [Handoff 139](139-cto-to-chief-of-staff-sensitivity-routing-contract-package.md) |

## 1. CTO disposition

**ACCEPT PT32 AS A COMPLETE READ-ONLY FEASIBILITY INVENTORY.** The report distinguishes proven,
absent, and unavailable facts and stayed within its no-mutation boundary. The CTO independently
reproduced the decisive listener fact: PID 3596 listens on IPv4 `0.0.0.0:11434` and IPv6
`[::]:11434`.

**DO NOT APPROVE OR ACTIVATE A LOCAL SENSITIVE-DATA PROFILE.** The current daemon is reachable on
all host interfaces and Handoff 140 records enabled inbound `ollama.exe` allow rules on the active
Public firewall profile. This violates ADR-0025's exact loopback-only boundary. A user-level
`OLLAMA_HOST` value is not evidence when the live process contradicts it. No private/restricted
content may be prepared for or sent to this daemon.

PT32's acceptance is acceptance of the evidence task, not acceptance of host posture, model
fitness, Ollama provenance, licensing, performance, or private-data use.

## 2. Model/profile decision

No exact production profile can be approved from the present evidence because:

- the runtime executable SHA-256 and installer/source identity are not yet bound;
- the full selected model manifest and every referenced blob digest are not yet recorded;
- the daemon is not loopback-confined;
- outbound denial/cloud-surface isolation is unproved;
- no synthetic latency, memory, cancellation, context-limit, output-limit, or quality evidence
  exists; and
- license text and use compatibility have not been reviewed.

The recommended **sole first synthetic evaluation candidate** is installed `gemma4:12b`, beginning
from its disclosed model-layer digest
`sha256:1278394b693672ac2799eadc9a83fd98259a6a88a40acfb1dcaa6c6fc895a606`.
This is not yet an exact profile: Engineering must bind the complete manifest and all blobs before
execution. It is selected for evaluation because it is a general conversation model already
present, materially smaller than the installed 26B model, and plausibly compatible with the
31.7-GiB CPU-only host. Those are capacity-screening facts, not a quality or performance claim.

The coder models are out of role for the first personal-assistant evaluation. `gemma4:latest` is not
acceptable because a mutable tag is not an identity. `gemma4:26b` is deferred because CPU-only
latency and memory pressure are unmeasured. No fallback model is authorized.

## 3. Recommended next gate A - reversible local-runtime confinement

Product Owner should authorize one bounded native-Windows security correction, performed without
private data or model inference:

1. capture a before inventory: Ollama executable path/hash/version, process command lines and
   owners, user/machine environment relevant to Ollama, listener table, active network profiles,
   exact firewall rules plus application/service filters, and repository/candidate identities;
2. export the exact affected firewall rules and record a rollback procedure before mutation;
3. stop only the Ollama GUI/server processes after proving their identities;
4. launch the exact existing executable under a controlled per-process environment bound to
   `127.0.0.1:11434`; no wildcard, LAN address, IPv6-any address, proxy, or ambient endpoint is
   allowed;
5. disable or remove only the proven Ollama inbound allow rules after exact identity capture;
6. add an exact-program outbound deny for the Ollama executable on all profiles so cloud, update,
   telemetry, and arbitrary remote access fail closed; preserve loopback operation;
7. prove listeners are only `127.0.0.1:11434` (and `[::1]:11434` only if explicitly supported and
   separately allowlisted), with no `0.0.0.0`, `[::]`, LAN, or public listener;
8. prove connection to the host's LAN addresses on port 11434 is denied and loopback health is
   available without loading a model or running inference;
9. prove no non-loopback Ollama connection exists before, during, or after the health check;
10. capture after inventory, exact diffs, rollback evidence, and an independent ordinary-user
    verification; then stop for CTO review.

If any rule cannot be scoped precisely, rollback cannot be proved, loopback breaks under the
outbound deny, a second executable/install is found, the GUI recreates broad rules/listeners, or an
unexpected remote connection appears, stop and restore the recorded before state. Do not weaken the
firewall or accept interface-wide exposure for convenience.

Elevation may be required only for the exact firewall operations and must be separately approved at
execution. The task may not install, update, download, uninstall, relocate models, edit Jarvis,
change repositories, or expose private data.

## 4. Recommended next gate B - synthetic-only single-model evaluation

This gate remains blocked until CTO accepts gate A. It may then:

1. bind Ollama executable SHA-256/version/source and the complete `gemma4:12b` manifest plus every
   referenced blob digest and size;
2. review and record the exact license without publishing unrelated private paths/content;
3. use only fixed synthetic prompts and synthetic context at declared 1K, 4K, 8K, and the proposed
   maximum input boundary; no vault, pilot, conversation history, or personal data;
4. run cold and warm samples with construction-plus-request boundaries, retaining raw wall time,
   time to terminal response, peak RAM, CPU, any iGPU/shared memory, output tokens, and failure;
5. test cancellation, timeout, malformed/oversized output, context/output limit enforcement,
   concurrent-request denial, process cleanup, and repeated-run stability;
6. continuously prove loopback-only listeners and zero non-loopback Ollama connections;
7. use a fixed assistant-quality rubric for instruction following, grounded use of supplied
   synthetic context, uncertainty, refusal of unsupported claims, and hostile-output handling;
8. record every sample and failure; do not discard warm-up or outlier attempts silently; and
9. stop for CTO/Product Owner selection. No model is activated automatically after a pass.

Minimum recommendation gates for later profile approval are: no security stop; complete identity
and license evidence; all hard limits and cancellation passing; no host instability or sustained
swapping; and median/p95 complete-response latency disclosed against a Product Owner-approved
usability ceiling. The Product Owner must set that latency/quality ceiling before execution so it
cannot be selected post hoc.

## 5. Evidence reuse and non-reuse

Reusable: PT31's accepted contracts, PT32 host CPU/RAM/GPU/disk inventory, installed-model presence,
and frozen executable/documentation identities, provided later checks show no drift.

Must be recollected: process/listener/firewall/environment state after remediation, runtime and full
model hashes, license, network-denial evidence, and all synthetic performance/quality/cancellation/
resource evidence. Existing model presence or size is not successful inference evidence.

## 6. Product Owner decisions requested

1. Accept PT32's read-only evidence while keeping local sensitive generation blocked.
2. Approve gate A's exact reversible confinement correction, including narrowly scoped elevation
   for the named firewall changes.
3. Pre-authorize gate B only after independent CTO acceptance of gate A.
4. Approve `gemma4:12b` as the sole first synthetic evaluation candidate, not as a production
   profile.
5. Provide before gate B one maximum acceptable median/p95 terminal latency and the minimum quality
   rubric outcome for personal use.

## 7. Explicit exclusions

This disposition authorizes no mutation, process restart, firewall change, model load/inference,
private-data use, installation, download, credential, Gemini call, code change, Engineering start,
Quality work, packaging, certification, merge, push, publication, or release. Chief of Staff must
translate any Product Owner approval into separate exact tasks.

## 8. Exit statement

**READY FOR PRODUCT OWNER DECISION.** Sensitive local generation remains unavailable and fails
closed. The next safe path is host confinement first, synthetic single-model evidence second, and a
later exact profile decision third.
