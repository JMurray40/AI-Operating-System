"""Deterministic v0.5 conversation benchmark (H07 §13; direct repository-root harness).

Measures, at 100/500/1,000/5,000 synthetic notes:

* deterministic ``prepare`` latency (p50/p95/p99) and peak memory;
* conversation application overhead excluding retrieval and provider (approve + prompt
  assembly + mock dispatch + evidence validation); and
* controlled-adapter cancellation acknowledgement latency.

It reuses the released benchmark vault generator and percentile method so the baseline is
equivalent. Raw samples and completion markers are retained; import/startup errors fail
visibly with a non-zero exit. No network, provider key, or live call is involved.

    python scripts/benchmark_conversation.py [--sizes 100,500,1000,5000] [--runs 30] \
        [--warmup 3] [--json out.json]
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import threading
import time
import tracemalloc
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from benchmark_project_resume import _stats_ms, build_resume_vault  # noqa: E402

from jarvis_core.config import Config  # noqa: E402
from jarvis_core.conversation import (  # noqa: E402
    ConversationApplication,
    PrepareTurnRequest,
    Session,
)
from jarvis_core.conversation import context as ctx  # noqa: E402
from jarvis_core.conversation.prompt import assemble_prompt  # noqa: E402
from jarvis_core.conversation.request import mock_profile  # noqa: E402
from jarvis_core.policy import local_allow_all  # noqa: E402
from jarvis_core.providers.conversation import (  # noqa: E402
    CancellationToken,
    MockConversationProvider,
    NormalizedResult,
    TerminalState,
)
from jarvis_core.repositories import FileSystemKnowledgeRepository  # noqa: E402

_T = datetime(2026, 8, 1, tzinfo=timezone.utc)
_SELECTOR = "Bench"

# Gates (H07 §13).
GATE_PREPARE_P95_MS = 2000.0
GATE_APP_OVERHEAD_P95_MS = 250.0
GATE_CANCEL_P95_MS = 500.0


def _request(
    notes_root: Path, session_id: str, text: str = "summarize Bench"
) -> PrepareTurnRequest:
    return PrepareTurnRequest(
        request_id="bench",
        session_id=session_id,
        workspace_id="local",
        scope=local_allow_all(workspace_id="local", max_sensitivity="internal"),
        source_root=notes_root,
        user_text=text,
        provider_profile=mock_profile(),
        evaluation_time=_T,
    )


def _load(root: Path) -> list:
    return FileSystemKnowledgeRepository(Config(vault_path=root)).discover()


def _bench_prepare(notes: list, root: Path, runs: int, warmup: int) -> tuple[list[float], float]:
    req = _request(root, "bench-session")
    for _ in range(warmup):
        ctx.prepare(req, notes)
    samples: list[float] = []
    for _ in range(runs):
        t0 = time.perf_counter()
        ctx.prepare(req, notes)
        samples.append((time.perf_counter() - t0) * 1000.0)
    tracemalloc.start()
    ctx.prepare(req, notes)
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return samples, peak / (1024 * 1024)


def _bench_app_overhead(notes: list, root: Path, runs: int, warmup: int) -> list[float]:
    app = ConversationApplication()
    provider = MockConversationProvider(reply="Bench pipeline is green. [C1]")
    samples: list[float] = []
    for i in range(runs + warmup):
        s = app.create_session("local", session_id=f"ov-{i}")
        app.prepare_turn(s, _request(root, s.session_id), notes)  # retrieval excluded below
        t0 = time.perf_counter()
        app.approve(s, actor="bench", now=_T)
        # prompt assembly + dispatch(mock, ~0) + evidence validation
        assemble_prompt(s.pending_prepared.snapshot, history_text=s.history_text())
        app.dispatch_turn(s, provider, now=_T)
        dt = (time.perf_counter() - t0) * 1000.0
        if i >= warmup:
            samples.append(dt)
    return samples


class _ControlledAdapter:
    """Polls the cancellation token every 1ms; returns CANCELLED on observation."""

    name = "controlled"
    adapter_version = "bench.controlled"

    def dispatch(self, request, cancel=None):  # type: ignore[no-untyped-def]
        deadline = time.perf_counter() + 2.0
        while time.perf_counter() < deadline:
            if cancel is not None and cancel.cancelled:
                break
            time.sleep(0.001)
        return NormalizedResult(
            status=TerminalState.CANCELLED,
            provider_id=request.transport.provider_id,
            model_id=request.transport.model_id,
            adapter_version=self.adapter_version,
            finish_reason="cancelled",
        )


def _bench_cancellation(notes: list, root: Path, runs: int) -> list[float]:
    app = ConversationApplication()
    samples: list[float] = []
    for i in range(runs):
        s = app.create_session("local", session_id=f"cx-{i}")
        app.prepare_turn(s, _request(root, s.session_id), notes)
        app.approve(s, actor="bench", now=_T)
        token = CancellationToken()
        holder: dict[str, object] = {}

        def _run(
            _app: ConversationApplication = app,
            _s: Session = s,
            _tok: CancellationToken = token,
            _h: dict[str, object] = holder,
        ) -> None:
            _h["res"] = _app.dispatch_turn(_s, _ControlledAdapter(), now=_T, cancel=_tok)

        th = threading.Thread(target=_run)
        th.start()
        time.sleep(0.005)  # let dispatch begin polling
        t0 = time.perf_counter()
        app.cancel_attempt(token)
        th.join(timeout=3.0)
        samples.append((time.perf_counter() - t0) * 1000.0)
    return samples


def run(sizes: list[int], runs: int, warmup: int) -> dict[str, object]:
    results: dict[str, object] = {
        "schema": "v0.5-conversation-benchmark/1",
        "evaluation_time": _T.isoformat(),
        "runs": runs,
        "warmup": warmup,
        "python": sys.version.split()[0],
        "gates": {
            "prepare_p95_ms": GATE_PREPARE_P95_MS,
            "app_overhead_p95_ms": GATE_APP_OVERHEAD_P95_MS,
            "cancel_p95_ms": GATE_CANCEL_P95_MS,
        },
        "sizes": {},
        "completed": False,
    }
    sizes_out: dict[str, object] = {}
    for n in sizes:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "vault"
            build_resume_vault(root, n)
            notes = _load(root)
            prep, peak_mib = _bench_prepare(notes, root, runs, warmup)
            overhead = _bench_app_overhead(notes, root, runs, warmup)
            cancel = _bench_cancellation(notes, root, max(5, runs // 3))
            sizes_out[str(n)] = {
                "note_count": len(notes),
                "prepare_ms": _stats_ms(prep),
                "prepare_raw_ms": [round(x, 3) for x in prep],
                "peak_mib": round(peak_mib, 3),
                "app_overhead_ms": _stats_ms(overhead),
                "app_overhead_raw_ms": [round(x, 3) for x in overhead],
                "cancel_ms": _stats_ms(cancel),
                "cancel_raw_ms": [round(x, 3) for x in cancel],
            }
    results["sizes"] = sizes_out

    largest = str(max(sizes))
    gate_results = {
        "prepare_p95_under_2s": sizes_out[largest]["prepare_ms"]["p95"] < GATE_PREPARE_P95_MS,
        "app_overhead_p95_under_250ms": all(
            v["app_overhead_ms"]["p95"] < GATE_APP_OVERHEAD_P95_MS for v in sizes_out.values()
        ),
        "cancel_p95_under_500ms": all(
            v["cancel_ms"]["p95"] < GATE_CANCEL_P95_MS for v in sizes_out.values()
        ),
    }
    results["gate_results"] = gate_results
    results["all_gates_pass"] = all(gate_results.values())
    results["completed"] = True
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sizes", default="100,500,1000,5000")
    ap.add_argument("--runs", type=int, default=30)
    ap.add_argument("--warmup", type=int, default=3)
    ap.add_argument("--json", default=None, help="Optional path to write the raw JSON result.")
    args = ap.parse_args()
    sizes = [int(x) for x in args.sizes.split(",") if x.strip()]
    results = run(sizes, args.runs, args.warmup)
    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    for n, v in results["sizes"].items():  # type: ignore[attr-defined]
        p = v["prepare_ms"]
        print(
            f"n={n:>5} notes={v['note_count']:>5} prepare p50/p95/p99="
            f"{p['p50']}/{p['p95']}/{p['p99']}ms peak={v['peak_mib']}MiB "
            f"overhead_p95={v['app_overhead_ms']['p95']}ms cancel_p95={v['cancel_ms']['p95']}ms"
        )
    print("gate_results:", json.dumps(results["gate_results"]))
    print("all_gates_pass:", results["all_gates_pass"])
    return 0 if results["all_gates_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
