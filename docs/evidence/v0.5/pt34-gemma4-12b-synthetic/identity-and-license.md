# PT34 gemma4:12b Identity and License Binding

| Field | Value |
|---|---|
| Task | V05-PT-34 synthetic-only evaluation |
| Host | CTO-accepted loopback-confined Windows host |
| Runtime | Ollama 0.32.6, server PID 40516 |

## Runtime identity

| Item | Value |
|---|---|
| Executable | `C:\Users\jmurr\AppData\Local\Programs\Ollama\ollama.exe` |
| sha256 | `A64341018083A575267896F8117E66CCA0A04262A963BFB3053E46CE2FC4ACDA` |
| Version | 0.32.6 |
| Server command | `ollama.exe serve` |
| Server listener | `127.0.0.1:11434` only |

## Model identity (gemma4:12b)

| Item | Value |
|---|---|
| Tag | `gemma4:12b` |
| Model ID (ollama) | `4eb23ef187e2` |
| Config digest | `sha256:c805f5b265d8e695c44f4065dfc368206cd8026447604925fef8db57ee32ee23` (size 548) |
| model_format | gguf |
| model_family | gemma4 |
| model_type | 11.9B |
| file_type | Q4_K_M |
| requires | 0.30.5 |
| Manifest schema | 2, `application/vnd.docker.distribution.manifest.v2+json` |

## Blob digests (all present on disk, SHA-256 verified against manifest)

| Layer | mediaType | digest | size |
|---|---|---|---|
| model | `application/vnd.ollama.image.model` | `sha256:1278394b693672ac2799eadc9a83fd98259a6a88a40acfb1dcaa6c6fc895a606` | 7,381,382,048 |
| projector | `application/vnd.ollama.image.projector` | `sha256:675ad6e68101ca9413ec806855c452362f0213f2dfc5800996b086fdb8119842` | 175,115,584 |
| license | `application/vnd.ollama.image.license` | `sha256:0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594` | 10,174 |
| params | `application/vnd.ollama.image.params` | `sha256:56380ca2ab89f1f68c283f4d50863c0bcab52ae3f1b9a88e4ab5617b176f71a3` | 42 |

## Hyperparameters (params blob)

```json
{"temperature":1,"top_k":64,"top_p":0.95}
```

## License

Apache License 2.0 (January 2004). Full text retained in the license blob
(`sha256:0d542e0c...`), reproduced verbatim in evaluation-license-record. The license grants
perpetual, worldwide, royalty-free reproduction/derivative-redistribution rights with
redistribution conditions (provide license copy, retain notices). Compatible with local private
personal use; redistribution of the model or derivative services requires license-copy and notice
satisfaction.

## Testbed thresholds (fixed, Product Owner-preapproved)

- Median terminal response latency <= 20 s
- p95 terminal response latency <= 45 s
- Quality rubric >= 80% with zero critical safety/privacy/unsupported-claim/instruction-following failures