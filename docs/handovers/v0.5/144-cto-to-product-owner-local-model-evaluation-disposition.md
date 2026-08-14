# Handoff 144 - CTO to Product Owner: Local-model Evaluation Disposition

| Field | Value |
|---|---|
| Date | 2026-08-15 |
| From | Chief Architect / CTO |
| To | Product Owner |
| Milestone | v0.5 Personal Prototype |
| Reviewed task | `V05-PT-34` |
| Disposition | **PT34 EVIDENCE ACCEPTED; `gemma4:12b` PROFILE REJECTED** |
| Reviewed return | [Handoff 143](143-principal-engineer-to-cto-local-model-synthetic-evaluation-return.md) |

## 1. Disposition

PT34 is accepted as a complete synthetic evaluation and its fail route is binding. `gemma4:12b`
must not be activated as the local sensitive-data profile on this host.

The predeclared acceptance gates fail decisively:

- median terminal latency is 73.7 seconds against a 20-second ceiling;
- p95 terminal latency is 120.1 seconds against a 45-second ceiling;
- 3 of 11 latency samples timed out;
- quality is 55/100 against an 80/100 minimum;
- instruction following and hostile-output handling both have critical failures; and
- the oversized-context case timed out without a typed limit result.

The CTO independently inspected the retained raw latency, quality, cancellation, context, and
control evidence. No failed or timed-out sample was discarded.

## 2. Control-evidence correction

Handoff 143's broad statement that all controls passed is not accepted literally. Cancellation has
a successful retained redo, but the first control record says `cancelled=false`. The 18K-context
case timed out without explicit limit enforcement, and the two concurrent requests timed out rather
than returning a typed concurrent denial. These are additional profile defects, not reasons to
repeat or weaken the evaluation.

Identity, license, loopback confinement, outbound denial, process stability, cleanup, and absence
of private data are accepted. The model was unloaded and PT33 confinement was preserved.

## 3. Recommended Product Owner decision

Do not change the thresholds and do not retry `gemma4:12b`. If the Product Owner wants to continue
pursuing local sensitive generation on this CPU-only host, the next bounded candidate should be the
already-installed general model `qwen2.5:7b` (recorded size 4.7 GB), subject to:

1. exact manifest, blob, runtime, and license binding;
2. the same PT33 confinement drift checks;
3. the same synthetic fixtures, raw retention, 20-second median, 45-second p95, 80/100 quality,
   and zero-critical-failure gates;
4. explicit typed checks for context limits and concurrent-request denial; and
5. no download, installation, fallback, private data, or automatic profile activation.

This is a new candidate evaluation, not a waiver. The alternative is to stop local-model
evaluation on this hardware and retain `blocked_local_unavailable` for private/restricted requests.

## 4. Explicit exclusions

No further inference, sampling, profile activation, model selection, installation, download,
private-data use, Jarvis change, packaging, certification, merge, push, publication, or release is
authorized by this review.

## 5. Exit statement

**READY FOR PRODUCT OWNER DECISION.** Choose whether to authorize one exact synthetic-only
`qwen2.5:7b` evaluation under unchanged gates or stop local-model evaluation on this host.
