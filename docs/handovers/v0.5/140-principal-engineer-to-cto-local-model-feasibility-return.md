# Handoff 140 - Principal Engineer to CTO: Local-model Feasibility Return

| Field | Value |
|---|---|
| Date | 2026-08-14 |
| From | Principal Engineer |
| To | Chief Architect / CTO |
| Milestone | v0.5 Personal Prototype |
| Task | `V05-PT-32` |
| Status | **READY FOR REVIEW - READ-ONLY EVIDENCE ONLY** |
| Frozen executable | `08b0b11383031d6e91f6f26145bfdffc710ca36b` |
| Documentation pin | `d345910f6239f5707975c77c45ea3759249d145e` (tree `a68b0d0657fc752cfe2ef017ffaecdbe8ffd27aa`) |
| Authority | [PT30 decision](../../../../../docs/coordination/reviews/V05-PT-30-PRODUCT-OWNER-ACCEPTANCE-AND-NEXT-GATES.md) and [PT32 activation](../../../../../docs/coordination/reviews/V05-PT-31-ACCEPTANCE-AND-PT32-ACTIVATION.md) |

## 1. Preflight confirmation

- PT31 documentation package is pinned at `d345910f6239f5707975c77c45ea3759249d145e`; the
  `v0.3.1-release` worktree `HEAD` equals that pin exactly.
- Frozen executable commit `08b0b11383031d6e91f6f26145bfdffc710ca36b` exists in the repository.
- No credential environment variables were present or consumed (verified the environment exposes
  only `OLLAMA_HOST`, `OLLAMA_CONTEXT_LENGTH`, `OLLAMA_NUM_PARALLEL`; no provider key/token set).
- No provider or model process was started; no install, download, model load, inference, network
  change, or executable mutation occurred. All commands below were ordinary-access reads.

## 2. Proven host facts (read directly from the host)

### 2.1 Operating system

| Fact | Value |
|---|---|
| OS name | Microsoft Windows 11 Pro |
| Version / build | 10.0.26200 / 26200 |
| Architecture | 64-bit |
| Network profile | Active adapter "Network 3" (Ethernet), category **Public** |

### 2.2 CPU

| Fact | Value |
|---|---|
| CPU | Intel(R) Core(TM) i5-14450HX |
| Cores / logical processors | 10 / 16 |
| Base max clock | 2400 MHz |
| ISA | x64 |

### 2.3 Memory

| Fact | Value |
|---|---|
| Total physical RAM | 34,079,776,768 bytes (~31.7 GiB) |

### 2.4 GPU / display adapters

| Adapter | Type | Driver version | Driver date |
|---|---|---|---|
| Intel(R) UHD Graphics (`PCI\VEN_8086&DEV_A78B`) | Integrated (Arc-family iGPU) | 32.0.101.7082 | 2025-11-30 |
| DisplayLink USB Device x4 | USB dock display | 9.3.3324.0 | 2020-04-15 |

- The Intel adapter reports `AdapterRAM` of 2,147,479,552 (~2 GiB), consistent with shared memory.
- **No discrete NVIDIA or AMD GPU is present. There is no CUDA or ROCm backend available.**
- Inference would run on CPU via the iGPU's shared-memory path at best; this is a feasibility
  limiting fact, not a performance measurement.

### 2.5 Disk / capacity

| Volume | Total | Free |
|---|---|---|
| C: (system, Windows) | 1,022,828,212,224 (~952 GiB) | 615,207,219,200 (~572 GiB) |
| G: (Google Drive mount) | 1,022,828,212,224 (~952 GiB) | 584,446,857,216 (~544 GiB) |

- Existing Ollama blob store on C: holds ~49.8 GiB across 20 blobs.
- The largest installed model blob (gemma4:26b) is 17,987,569,344 bytes (~16.75 GiB); current free
  C: space can hold it and the installed set several times over.

## 3. Ollama presence and provenance

| Fact | Value |
|---|---|
| Executable | `C:\Users\jmurr\AppData\Local\Programs\Ollama\ollama.exe` |
| Version | **0.32.6** (confirmed via `ollama --version`) |
| Install type | Standard per-user AppData install (not a service; no Windows service entry found) |
| Runtime | Running: server PID 3596 (`ollama.exe`), GUI PID 25912 (`ollama app.exe`) |
| Home/config root | `C:\Users\jmurr\.ollama` |
| Model root | `C:\Users\jmurr\.ollama\models` |

## 4. Installed-model metadata (read-only, `ollama list` + manifests)

| Model tag | ID | Size |
|---|---|---|
| gemma4:12b | 4eb23ef187e2 | 7.6 GB |
| qwen2.5-coder:7b | dae161e27b0e | 4.7 GB |
| qwen2.5-coder:14b | 9ec8897f747e | 9.0 GB |
| qwen2.5:7b | 845dbda0ea48 | 4.7 GB |
| gemma4:latest | c6eb396dbd59 | 9.6 GB |
| gemma4:26b | 5571076f3d70 | 17 GB |

Model-layer immutable digests read from the manifest files under
`registry.ollama.ai\library\` (each model tag maps to a unique `sha256` model-layer digest; exact
digests are captured in the manifest blobs and are reproducible on demand, e.g. gemma4:12b model
layer `sha256:1278394b693672ac2799eadc9a83fd98259a6a88a40acfb1dcaa6c6fc895a606`,
qwen2.5-coder:14b model layer `sha256:ac9bc7a69dab38da1c790838955f1293420b55ab555ef6b4615efa1c1507b1ed`).

Model params recorded for gemma4:12b: `{"temperature":1,"top_k":64,"top_p":0.95}`. License blobs
are present in each manifest set but their text was not rendered; license compliance is out of
read-only scope.

`C:\Users\jmurr\.ollama\config.json` records local integrations only (`hermes`, `openclaw`,
`vscode`) all selecting `gemma4:*`; `last_selection` is `hermes`. No cloud/provider endpoint is
configured there.

## 5. Loopback / network posture - PROVEN DISCREPANCY

| Item | Fact |
|---|---|
| `OLLAMA_HOST` env (HKCU) | `127.0.0.1:11434` |
| `OLLAMA_CONTEXT_LENGTH` | `16384` |
| `OLLAMA_NUM_PARALLEL` | `1` |
| **Live listening socket** | **`0.0.0.0:11434` and `[::]:11434`, owning process PID 3596 (`ollama.exe`)** |
| Inbound firewall rules | Two `ollama.exe` rules with action **Allow**, enabled, profile **Public** |
| Active network profile | **Public** |

**Finding:** although `OLLAMA_HOST=127.0.0.1:11434` is set in the user environment, the running
Ollama server is actually bound to all interfaces (`0.0.0.0` and `[::]`), not loopback-only, and
inbound `ollama.exe` traffic is firewall-allowed on the Public network profile. The host's
loopback-only posture required for the local sensitive profile is therefore **not currently
satisfied**. Root cause (started before env var took effect, or a profile/registry override) is not
diagnosable without a service/process restart or registry mutation, which is outside this task's
authority and must be handled separately.

- Ollama's own listener currently shows no established outbound connections to remote addresses.
- `cache/model-recommendations.json` advertises cloud models (`glm-5.2:cloud`, `minimax-m3:cloud`)
  as Ollama cloud offerings. This is informational only and is directly relevant to the no-remote-
  fallback requirement: no such cloud profile is configured or used, but the client's "cloud"
  surface exists.

## 6. Absent / not found

- No NVIDIA or AMD discrete GPU (no CUDA/ROCm backend).
- No Windows service running Ollama (process-launched only).
- No evidence of a second Ollama install or alternate model root.
- No provider credential (Gemini/OpenAI/Anthropic) present in the environment during this pass.

## 7. Unavailable facts (require separately authorized action)

These were deliberately not obtained. Each requires elevation, mutation, execution, or a live
adapter run, all excluded by this task:

1. Cold-start and warm complete-response latency, peak RAM/VRAM, and cancellation behavior at the
   accepted input/output limits (requires synthetic local model execution).
2. Proven loopback-only routing *during an actual dispatch* under the adapter (requires running the
   local profile end to end).
3. Proof that the dispatch process cannot reach non-loopback destinations (requires a controlled
   dispatch under the adapter with a sink).
4. Whether the running daemon would rebind to `127.0.0.1` after an env-var-honoring restart
   (requires a process restart, i.e. mutation).
5. Model license text and licensing conformance, quantization/fit details per model beyond blob
   size (requires rendering blobs / model metadata that is not exposed by `ollama list`).
6. Repair of the Public-profile firewall allow and the all-interfaces bind (requires mutation).

## 8. Exact limitations of this report

- All values are existing-state, read-only snapshots taken on 2026-08-14 on the current Windows
  host. They are not measurements of inference performance or quality.
- Blob total (~49.8 GiB) is aggregate; per-model exact on-disk footprint was not enumerated
  per-blob beyond the manifest sizes above.
- SSH key material present under `C:\Users\jmurr\.ollama` (`id_ed25519*`) was detected by filename
  only and was not read; it is outside this report's scope and flagged so it is never treated as
  model evidence.

## 9. Recommended next model-profile decision inputs

These are decision inputs only, not recommendations to acquire or run anything:

1. **Gemma4 family fits the host constraint best by weight class:** gemma4:12b (7.6 GB) and
   gemma4:26b (17 GB) both fit the 31.7 GiB RAM and free disk; CPU-only inference expected (no
   discrete GPU).
2. **Exact model, quantization, context window, and digest** must be pinned by a Product Owner
   decision before any local profile is activated; this report provides the digest-verifiable set
   but does not select one.
3. **The network-posture discrepancy (all-interfaces bind + Public firewall allow) must be
   resolved before any loopback-only local profile is activated**, per the no-remote-fallback and
   loopback-only requirements in Handoff 138/139.
4. Local-only sensitive generation remains unavailable until a model profile is separately
   approved and the posture above is corrected.

## 10. Exit statement

**READY FOR REVIEW.** One privacy-safe read-only inventory produced; proven facts, one proven
posture discrepancy, absences, and unavailable facts are separated above. No elevation, mutation,
install, download, model load, inference, credential, or network change was performed. The
executable candidate and documentation pin are unchanged.
