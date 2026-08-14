# PT35 qwen2.5:7b Identity, Manifest, and License Binding

| Field | Value |
|---|---|
| Task | V05-PT-35 synthetic-only evaluation |
| Model | `qwen2.5:7b` |
| Server | `127.0.0.1:11434`, PID 40516 (PT33-confined) |
| Bound | 2026-08-15 |
| Model digest (ollama) | `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e` |
| Source | Already installed on the PT33-confined host (no install/download/update) |

## 1. Runtime binding

| Item | Value |
|---|---|
| Server | Ollama v0.32.6, PID 40516, `ollama.exe serve`, executable SHA-256 `A64341018083A575267896F8117E66CCA0A04262A963BFB3053E46CE2FC4ACDA` |
| Listener | `127.0.0.1:11434` only (no `0.0.0.0`, no `[::]`) |
| Outbound deny | `{f28e9ff6-c7ea-4e3e-8582-9dc9f357ae24}` "Jarvis PT33 block ollama outbound", Enabled, Block, Outbound, Any profile |
| Inbound allows | 0 (both removed in PT33) |
| Non-loopback connections | 0 from PID 40516 at binding time |
| Loaded models at binding | 0 (`/api/ps` empty) |

## 2. Model identity (from `/api/show` and GGUF metadata)

| Item | Value |
|---|---|
| Family / format | `qwen2` / `gguf` |
| Parameter size | 7.6B (actual count 7,615,616,512) |
| Quantization | `Q4_K_M` (file_type 15) |
| Finetune | Instruct |
| Context length | 32,768 |
| Block count | 28 |
| Attention heads | 28 (KV 4) |
| Embedding length | 3,584 |
| Feed-forward length | 18,944 |
| Base model | Qwen2.5 7B (Qwen), instruct variant |
| Modelfile FROM | `C:\Users\jmurr\.ollama\models\blobs\sha256-2bada8a7450677000f678be90653b85d364de7db25eb5ea54136ada5f3933730` |

## 3. Manifest and blob verification (all PASS)

Manifest: `C:\Users\jmurr\.ollama\models\manifests\registry.ollama.ai\library\qwen2.5\7b`
(schemaVersion 2). All blobs present, byte-exact size, SHA-256 digest verified on disk.

| Layer | Digest (sha256) | Size (bytes) | Present | Size match | Hash match |
|---|---|---|---|---|---|
| model | `2bada8a7450677000f678be90653b85d364de7db25eb5ea54136ada5f3933730` | 4,683,073,952 | yes | yes | yes |
| system | `66b9ea09bd5b7099cbb4fc820f31b575c0366fa439b08245566692c6784e281e` | 68 | yes | yes | yes |
| template | `eb4402837c7829a690fa845de4d7f3fd842c2adee476d5341da8a46ea9255175` | 1,482 | yes | yes | yes |
| license | `832dd9e00a68dd83b3c3fb9f5588dad7dcf337a0db50f7d9483f310cd292e92e` | 11,343 | yes | yes | yes |
| config | `2f15b3218f0552c60647ce60ada83632d2c09755b16259b13e3e4458e9ae419d` | 487 | yes | yes | yes |

## 4. Parameters and prompt template

- Prompt template: Qwen chat template (`<|im_start|>`/`<|im_end|>` role markup with system/user/
  assistant/tool segments).
- Modelfile SYSTEM: "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."
- No explicit parameter overrides in the modelfile (default sampling applies). Terminal answers are
  direct assistant content, not a reasoning/thinking channel (unlike gemma4 in PT34).

## 5. License

- Apache License 2.0, Copyright 2024 Alibaba Cloud.
- License text embedded in modelfile and license blob (11,343 bytes) verified.
- This is the same license family already accepted for `gemma4:12b` in PT34 (apache-2.0).
