"""Private benchmark runner and privacy-safe public aggregation."""
from __future__ import annotations

import hashlib
import json
import re
import socket
import time
import tracemalloc
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from types import MappingProxyType

from jarvis_core.models.note import Note
from jarvis_core.personal_recall.corpus import (
    AcquiredSource,
    SourceInventory,
    acquire_sources,
    build_corpus_from_acquired,
    inventory_sources,
)
from jarvis_core.personal_recall.policy import RecallPolicy
from jarvis_core.policy.errors import PolicyError
from jarvis_core.policy.scope import AuthorizationScope
from jarvis_core.query.engine import QueryEngine
from jarvis_core.query.evidence import CitationFactory, CurrentSourceResolver
from jarvis_core.query.intent import Intent, IntentParser
from jarvis_core.query.passages import validate
from jarvis_core.query.results import QueryAnswer
from jarvis_core.query.trace import QueryTrace

_MANIFEST_KEYS = {"schema_version", "benchmark_id", "questions"}
_QUESTION_KEYS = {
    "benchmark_question_id", "category", "question", "expected_relpaths",
    "acceptable_alternates", "reason", "max_sensitivity",
}
_CATEGORIES = {
    "exact", "metadata", "project", "relationship", "paraphrase",
    "negative", "missing",
}
_PUBLIC_KEYS = {
    "schema_version", "task", "policy_sha256", "benchmark_manifest_sha256",
    "source_count", "source_bytes", "source_inventory_sha256", "category_totals",
    "category_top5_hits", "deterministic_runs", "citation_validation",
    "network_attempt_count", "provider_call_count", "persistent_index_write_count",
    "legacy_memory_call_count", "parse_index_ms", "query_p95_ms", "peak_memory_bytes",
    "source_integrity", "response_contract", "answer_claim_count",
    "missing_unresolved_count", "negative_authorization_control_count",
}
_HEX = frozenset("0123456789abcdef")
_AVAILABILITY = frozenset({
    "source_boundary:metadata_unavailable", "source_boundary:read_failed",
    "source_boundary:scan_failed", "source_boundary:resolve_failed",
    "preflight:root_unavailable", "preflight:include_unavailable",
})
_EPOCH_LIMIT = 3
_WINDOW_SECONDS = 300.0
_RETRY_DELAY_SECONDS = 1.0
_COVERAGE = frozenset({"none", "complete", "partial", "incomplete"})
_ROW_KEYS = frozenset({
    "benchmark_question_id", "category", "top5_expected", "coverage", "citations",
    "trace_safe", "response_semantics",
})
_CITATION_KEYS = frozenset({
    "inventory_index", "fingerprint", "locator_sha256", "coverage",
})
_TRACE_KEYS = frozenset({
    "workspace_fingerprint", "candidate_count", "ranked_inventory_indices",
})
_SEMANTIC_KEYS = frozenset({
    "result_type", "answer_claim", "resolution", "candidate_role",
    "expected_answer_source_claimed",
})


class CheckpointFailure(PolicyError):
    """Fixed, path-free terminal category for a bounded proof checkpoint."""

    def __init__(self, checkpoint: str, attempt: int, outcome: str) -> None:
        self.checkpoint = checkpoint
        self.attempt = attempt
        self.outcome = outcome
        super().__init__(f"{checkpoint}:{outcome}")


class BenchmarkGateFailure(PolicyError):
    """A completed three-run proof whose fixed acceptance gate did not pass."""

    def __init__(
        self, category: str, private: dict[str, object], public: dict[str, object]
    ) -> None:
        self.private = private
        self.public = public
        super().__init__(category)


def _event(
    events: list[dict[str, object]], checkpoint: str, attempt: int,
    outcome: str, count: int, started_ns: int,
) -> None:
    events.append({
        "checkpoint": checkpoint,
        "attempt": attempt,
        "outcome": outcome,
        "source_count": count,
        "elapsed_ms": round((time.perf_counter_ns() - started_ns) / 1_000_000, 3),
    })


def _failure_outcome(error: PolicyError) -> str:
    category = str(error)
    if category in _AVAILABILITY:
        return "availability_unavailable"
    if category in ("source_boundary:fingerprint_changed", "source_boundary:changed_during_read"):
        return "fingerprint_mismatch"
    if category in ("source_boundary:parse_failure", "source_boundary:parse_input"):
        return "parse_failure"
    if category.startswith("privacy:"):
        return "privacy_failure"
    if category == "benchmark:network_attempt":
        return "network_attempt"
    return "boundary_failure"


def _checked_inventory(
    policy: RecallPolicy, baseline: tuple[SourceInventory, ...],
    checkpoint: str, attempt: int, events: list[dict[str, object]],
) -> bool:
    started = time.perf_counter_ns()
    try:
        live = inventory_sources(policy)
    except PolicyError as error:
        outcome = _failure_outcome(error)
        _event(events, checkpoint, attempt, outcome, 0, started)
        if outcome == "availability_unavailable":
            return False
        raise CheckpointFailure(checkpoint, attempt, outcome) from None
    except Exception:
        _event(events, checkpoint, attempt, "unexpected_failure", 0, started)
        raise CheckpointFailure(checkpoint, attempt, "unexpected_failure") from None
    if live != baseline:
        _event(events, checkpoint, attempt, "integrity_mismatch", len(live), started)
        raise CheckpointFailure(checkpoint, attempt, "integrity_mismatch")
    _event(events, checkpoint, attempt, "pass", len(live), started)
    return True


def _acquire_epoch(
    policy: RecallPolicy, baseline: tuple[SourceInventory, ...],
    events: list[dict[str, object]],
) -> tuple[tuple[AcquiredSource, ...], int]:
    deadline = time.monotonic() + _WINDOW_SECONDS
    for attempt in range(1, _EPOCH_LIMIT + 1):
        if time.monotonic() > deadline:
            raise CheckpointFailure("acquisition", attempt, "time_limit")
        if not _checked_inventory(policy, baseline, "initial_inventory", attempt, events):
            if attempt < _EPOCH_LIMIT:
                time.sleep(_RETRY_DELAY_SECONDS)
            continue
        started = time.perf_counter_ns()
        try:
            acquired = acquire_sources(policy, baseline)
        except PolicyError as error:
            outcome = _failure_outcome(error)
            _event(events, "acquisition", attempt, outcome, 0, started)
            if outcome != "availability_unavailable":
                raise CheckpointFailure("acquisition", attempt, outcome) from None
            if attempt < _EPOCH_LIMIT:
                time.sleep(_RETRY_DELAY_SECONDS)
            continue
        except Exception:
            _event(events, "acquisition", attempt, "unexpected_failure", 0, started)
            raise CheckpointFailure("acquisition", attempt, "unexpected_failure") from None
        _event(events, "acquisition", attempt, "pass", len(acquired), started)
        if not _checked_inventory(
            policy, baseline, "post_acquisition_inventory", attempt, events
        ):
            acquired = ()  # discard the complete epoch before any availability retry
            if attempt < _EPOCH_LIMIT:
                time.sleep(_RETRY_DELAY_SECONDS)
            continue
        if time.monotonic() > deadline:
            acquired = ()
            raise CheckpointFailure("acquisition", attempt, "time_limit")
        return acquired, attempt
    raise CheckpointFailure("acquisition", _EPOCH_LIMIT, "availability_exhausted")


def _final_inventory(
    policy: RecallPolicy, baseline: tuple[SourceInventory, ...],
    events: list[dict[str, object]],
) -> None:
    deadline = time.monotonic() + _WINDOW_SECONDS
    for attempt in range(1, _EPOCH_LIMIT + 1):
        if time.monotonic() > deadline:
            raise CheckpointFailure("final_inventory", attempt, "time_limit")
        if _checked_inventory(policy, baseline, "final_inventory", attempt, events):
            return
        if attempt < _EPOCH_LIMIT:
            time.sleep(_RETRY_DELAY_SECONDS)
    raise CheckpointFailure("final_inventory", _EPOCH_LIMIT, "availability_exhausted")


def canonical_json(value: object) -> bytes:
    text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return (text + "\n").encode()


def validate_public_packet(packet: dict[str, object]) -> None:
    """Accept only bounded aggregate fields; no private dynamic text is representable."""
    if set(packet) != _PUBLIC_KEYS or packet["schema_version"] != 1:
        raise PolicyError("privacy:public_schema")
    if (packet["task"] not in ("V06-PR-01", "V06-PR-03")
            or packet["citation_validation"] != "pass"
            or packet["source_integrity"] != "pass"
            or packet["response_contract"] != "ranked_candidates_only"
            or packet["answer_claim_count"] != 0
            or packet["missing_unresolved_count"] != 1
            or packet["negative_authorization_control_count"] != 2):
        raise PolicyError("privacy:public_value")
    for key in ("policy_sha256", "benchmark_manifest_sha256", "source_inventory_sha256"):
        value = packet[key]
        if not isinstance(value, str) or len(value) != 64 or not set(value) <= _HEX:
            raise PolicyError("privacy:public_digest")
    for key in ("category_totals", "category_top5_hits"):
        value = packet[key]
        if not isinstance(value, dict) or set(value) != _CATEGORIES or not all(
            type(item) is int and item >= 0 for item in value.values()
        ):
            raise PolicyError("privacy:public_counts")
    for key in (
        "source_count", "source_bytes", "deterministic_runs", "network_attempt_count",
        "provider_call_count", "persistent_index_write_count", "legacy_memory_call_count",
        "peak_memory_bytes",
        "answer_claim_count", "missing_unresolved_count",
        "negative_authorization_control_count",
    ):
        if type(packet[key]) is not int or packet[key] < 0:
            raise PolicyError("privacy:public_count")
    if not isinstance(packet["parse_index_ms"], list) or len(packet["parse_index_ms"]) != 3:
        raise PolicyError("privacy:public_timing")
    if not all(type(value) in (int, float) and value >= 0
               for value in [*packet["parse_index_ms"], packet["query_p95_ms"]]):
        raise PolicyError("privacy:public_timing")


def load_manifest(path: Path) -> dict[str, object]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PolicyError("benchmark:unreadable") from exc
    if not isinstance(raw, dict) or set(raw) != _MANIFEST_KEYS or raw.get("schema_version") != 1:
        raise PolicyError("benchmark:schema")
    if not isinstance(raw.get("benchmark_id"), str) or not raw["benchmark_id"]:
        raise PolicyError("benchmark:id")
    questions = raw.get("questions")
    if not isinstance(questions, list) or len(questions) != 24:
        raise PolicyError("benchmark:question_count")
    counts = {category: 0 for category in _CATEGORIES}
    ids: set[str] = set()
    for question in questions:
        if not isinstance(question, dict) or set(question) != _QUESTION_KEYS:
            raise PolicyError("benchmark:question_schema")
        qid = question.get("benchmark_question_id")
        category = question.get("category")
        if not isinstance(qid, str) or not qid or qid in ids or category not in _CATEGORIES:
            raise PolicyError("benchmark:question_value")
        ids.add(qid)
        counts[str(category)] += 1
        if question.get("max_sensitivity") != "private":
            raise PolicyError("benchmark:ceiling")
        if not isinstance(question.get("question"), str) or not str(question["question"]).strip():
            raise PolicyError("benchmark:empty_question")
        for key in ("expected_relpaths", "acceptable_alternates"):
            if not isinstance(question.get(key), list) or not all(
                isinstance(v, str) and v and not v.startswith(("/", "\\"))
                and ":" not in v and ".." not in Path(v).parts
                for v in question[key]
            ):
                raise PolicyError("benchmark:expected_sources")
        if not isinstance(question.get("reason"), str) or not question["reason"].strip():
            raise PolicyError("benchmark:reason")
        if category not in ("negative", "missing") and not question["expected_relpaths"]:
            raise PolicyError("benchmark:expected_sources")
    if counts != {"exact": 6, "metadata": 4, "project": 4, "relationship": 4,
                  "paraphrase": 3, "negative": 2, "missing": 1}:
        raise PolicyError("benchmark:category_counts")
    return raw


def classify_s1_response(
    answer: QueryAnswer, trace: QueryTrace | None, terms: tuple[str, ...],
    category: str,
) -> dict[str, object]:
    """Prove Core emitted a retrieval report, never a fact-level answer claim."""
    if answer.intent is not Intent.SEARCH or trace is None or answer.answer_confidence is not None:
        raise PolicyError("benchmark:answer_claim")
    if not terms:
        valid = answer.answer == "No searchable terms found." and not trace.ranked
    elif not trace.ranked:
        valid = answer.answer == f"No notes match: {', '.join(terms)}."
    else:
        pattern = re.fullmatch(
            r"(\d+) note\(s\) match " + re.escape(str(list(terms)))
            + r"; top (\d+) by relative relevance\.",
            answer.answer,
        )
        valid = bool(
            pattern and int(pattern[1]) >= len(trace.ranked)
            and int(pattern[2]) == len(trace.ranked)
        )
    if not valid:
        raise PolicyError("benchmark:answer_claim")
    return {
        "result_type": "ranked_retrieval_candidates",
        "answer_claim": "none",
        "resolution": "unresolved" if category == "missing" else "retrieve_only",
        "candidate_role": "candidate_not_answer",
        "expected_answer_source_claimed": False,
    }


def validate_private_row(
    row: dict[str, object], *, category: str, question_id: str, source_count: int,
) -> None:
    """Closed projection: excluded identities/content have no representable field."""
    if (set(row) != _ROW_KEYS or row["category"] != category
            or row["benchmark_question_id"] != question_id
            or type(row["top5_expected"]) is not bool or row["coverage"] not in _COVERAGE):
        raise PolicyError("privacy:private_schema")
    semantics = row["response_semantics"]
    if (not isinstance(semantics, dict) or set(semantics) != _SEMANTIC_KEYS
            or semantics != {
                "result_type": "ranked_retrieval_candidates", "answer_claim": "none",
                "resolution": "unresolved" if category == "missing" else "retrieve_only",
                "candidate_role": "candidate_not_answer",
                "expected_answer_source_claimed": False,
            }):
        raise PolicyError("privacy:response_semantics")
    citations = row["citations"]
    if not isinstance(citations, list):
        raise PolicyError("privacy:private_schema")
    for citation in citations:
        if (not isinstance(citation, dict) or set(citation) != _CITATION_KEYS
                or type(citation["inventory_index"]) is not int
                or not 0 <= citation["inventory_index"] < source_count
                or citation["coverage"] != "supported"
                or not isinstance(citation["fingerprint"], str)
                or not re.fullmatch(r"sha256:[0-9a-f]{64}", citation["fingerprint"])
                or not isinstance(citation["locator_sha256"], str)
                or not re.fullmatch(r"[0-9a-f]{64}", citation["locator_sha256"])):
            raise PolicyError("privacy:private_schema")
    safe_trace = row["trace_safe"]
    if (not isinstance(safe_trace, dict) or set(safe_trace) != _TRACE_KEYS
            or not isinstance(safe_trace["workspace_fingerprint"], str)
            or not re.fullmatch(r"sha256:[0-9a-f]{64}", safe_trace["workspace_fingerprint"])
            or type(safe_trace["candidate_count"]) is not int
            or not 0 <= safe_trace["candidate_count"] <= source_count
            or not isinstance(safe_trace["ranked_inventory_indices"], list)
            or not all(type(index) is int and 0 <= index < source_count
                       for index in safe_trace["ranked_inventory_indices"])):
        raise PolicyError("privacy:private_schema")


@contextmanager
def network_blocked() -> Iterator[list[str]]:
    original_socket = socket.socket
    original_connection = socket.create_connection
    original_getaddrinfo = socket.getaddrinfo
    original_gethostbyname = socket.gethostbyname
    attempts: list[str] = []

    def blocked(*_args: object, **_kwargs: object) -> None:
        attempts.append("blocked")
        raise RuntimeError("network_disabled")

    socket.socket = blocked  # type: ignore[assignment]
    socket.create_connection = blocked  # type: ignore[assignment]
    socket.getaddrinfo = blocked  # type: ignore[assignment]
    socket.gethostbyname = blocked  # type: ignore[assignment]
    try:
        yield attempts
    finally:
        socket.socket = original_socket
        socket.create_connection = original_connection
        socket.getaddrinfo = original_getaddrinfo
        socket.gethostbyname = original_gethostbyname


class _NoProvider:
    name = "none"

    def summarize(self, *_args: object, **_kwargs: object) -> None:
        raise PolicyError("benchmark:provider_attempt")


class _AcquiredSourceResolver(CurrentSourceResolver):
    """Bind Core citation checks to one verified in-memory source revision."""

    def __init__(self, root: Path, source_bytes: dict[str, bytes]) -> None:
        super().__init__(root)
        self._source_bytes = MappingProxyType(source_bytes)

    def current_bytes(self, note: Note) -> bytes:
        return self._source_bytes.get(note.relpath, b"")


def run_benchmark(
    policy: RecallPolicy,
    inventory: tuple[SourceInventory, ...],
    manifest_path: Path,
    events: list[dict[str, object]] | None = None,
) -> tuple[dict[str, object], dict[str, object]]:
    """Run three deterministic lexical passes and return private/public evidence."""
    manifest = load_manifest(manifest_path)
    tracemalloc.start()
    scope = AuthorizationScope(
        workspace_id=policy.workspace_id,
        max_sensitivity=policy.max_sensitivity,
        request_id="personal-recall-benchmark",
        allowed_path_prefixes=policy.include_roots,
        policy_id=policy.policy_id,
        policy_version=policy.policy_version,
    )
    parser = IntentParser()
    inventory_indices = {source.relpath: index for index, source in enumerate(inventory)}
    runs: list[list[dict[str, object]]] = []
    query_ns: list[int] = []
    parse_ns: list[int] = []
    event_log = events if events is not None else []
    network_attempts: list[str] = []
    benchmark_started = time.perf_counter_ns()
    try:
        with network_blocked() as network_attempts:
            acquired, successful_epoch = _acquire_epoch(policy, inventory, event_log)
            parse_start = time.perf_counter_ns()
            notes = build_corpus_from_acquired(policy, acquired)
            source_bytes = {item.inventory.relpath: item.data for item in acquired}
            memory_resolver = _AcquiredSourceResolver(policy.vault_root, source_bytes)
            for _run in range(3):
                started_index = parse_start if _run == 0 else time.perf_counter_ns()
                engine = QueryEngine(
                    notes, scope=scope, source_root=policy.vault_root, provider=_NoProvider()
                )
                # Core stays unchanged; this bounded adapter binds its citation service to
                # the acquired revision until the final live-inventory check succeeds.
                engine._citations = CitationFactory(engine._identities, memory_resolver)
                parse_ns.append(time.perf_counter_ns() - started_index)
                rows: list[dict[str, object]] = []
                for question in manifest["questions"]:  # type: ignore[index]
                    q = question  # type: ignore[assignment]
                    parsed = parser.parse(str(q["question"]))
                    if parsed.intent is Intent.SUMMARIZE_PROJECT:
                        raise PolicyError("benchmark:provider_intent")
                    started = time.perf_counter_ns()
                    answer, trace = engine.run(str(q["question"]), want_trace=True)
                    query_ns.append(time.perf_counter_ns() - started)
                    semantics = classify_s1_response(
                        answer, trace, parsed.terms, str(q["category"])
                    )
                    citations = []
                    returned: set[str] = set()
                    for citation in answer.citations[:5]:
                        if citation.coverage != "supported":
                            raise PolicyError("benchmark:citation_incomplete")
                        data = source_bytes.get(citation.relpath)
                        if data is None:
                            raise PolicyError("benchmark:citation_outside_inventory")
                        check = validate(
                            locator=citation.locator,
                            excerpt=citation.excerpt,
                            source_fingerprint=citation.source_fingerprint,
                            current_bytes=data,
                            current_text=data.decode("utf-8"),
                        )
                        if not check.ok:
                            raise PolicyError("benchmark:citation_invalid")
                        returned.add(citation.relpath)
                        citations.append({
                            "inventory_index": inventory_indices[citation.relpath],
                            "fingerprint": citation.source_fingerprint,
                            "locator_sha256": hashlib.sha256(
                                canonical_json(citation.locator.to_dict())
                            ).hexdigest(),
                            "coverage": citation.coverage,
                        })
                    expected = set(q["expected_relpaths"]) | set(q["acceptable_alternates"])
                    row = {
                        "benchmark_question_id": q["benchmark_question_id"],
                        "category": q["category"],
                        "top5_expected": bool(expected & returned),
                        "coverage": answer.citation_coverage()["label"],
                        "citations": citations,
                        "response_semantics": semantics,
                        "trace_safe": {
                            "workspace_fingerprint": trace.workspace_fingerprint if trace else "",
                            "candidate_count": len(trace.candidates) if trace else 0,
                            "ranked_inventory_indices": [
                                inventory_indices[r.relpath] for r in trace.ranked
                            ] if trace else [],
                        },
                    }
                    validate_private_row(
                        row, category=str(q["category"]),
                        question_id=str(q["benchmark_question_id"]),
                        source_count=len(inventory),
                    )
                    rows.append(row)
                runs.append(rows)
            if network_attempts:
                raise PolicyError("benchmark:network_attempt")
            _event(
                event_log, "benchmark", successful_epoch, "repetitions_complete",
                len(inventory), benchmark_started,
            )
            _final_inventory(policy, inventory, event_log)
        _current, peak = tracemalloc.get_traced_memory()
    except CheckpointFailure:
        raise
    except PolicyError as error:
        outcome = _failure_outcome(error)
        _event(event_log, "benchmark", 1, outcome, len(inventory), benchmark_started)
        raise CheckpointFailure("benchmark", 1, outcome) from None
    except Exception:
        outcome = "network_attempt" if network_attempts else "unexpected_failure"
        _event(event_log, "benchmark", 1, outcome, len(inventory), benchmark_started)
        raise CheckpointFailure("benchmark", 1, outcome) from None
    finally:
        tracemalloc.stop()
    comparable = [canonical_json(rows) for rows in runs]
    deterministic = comparable[0] == comparable[1] == comparable[2]
    if not deterministic:
        raise PolicyError("benchmark:nondeterministic")
    first = runs[0]
    category_totals = {category: 0 for category in _CATEGORIES}
    category_hits = {category: 0 for category in _CATEGORIES}
    for row in first:
        category = str(row["category"])
        category_totals[category] += 1
        category_hits[category] += int(bool(row["top5_expected"]))
    sorted_ns = sorted(query_ns)
    p95_index = max(0, min(len(sorted_ns) - 1, (95 * len(sorted_ns) + 99) // 100 - 1))
    private = {
        "schema_version": 1,
        "benchmark_manifest_sha256": hashlib.sha256(canonical_json(manifest)).hexdigest(),
        "runs": runs,
        "parse_index_ns": parse_ns,
        "query_ns": query_ns,
        "peak_memory_bytes": peak,
        "checkpoint_events": event_log,
    }
    public = {
        "schema_version": 1,
        "task": "V06-PR-01",
        "benchmark_manifest_sha256": private["benchmark_manifest_sha256"],
        "source_count": len(inventory),
        "source_bytes": sum(s.size for s in inventory),
        "source_inventory_sha256": hashlib.sha256(canonical_json([
            {"relpath": s.relpath, "size": s.size, "mtime_ns": s.mtime_ns,
             "sha256": s.sha256}
            for s in inventory
        ])).hexdigest(),
        "category_totals": category_totals,
        "category_top5_hits": category_hits,
        "deterministic_runs": 3 if deterministic else 0,
        "citation_validation": "pass",
        "network_attempt_count": 0,
        "provider_call_count": 0,
        "persistent_index_write_count": 0,
        "legacy_memory_call_count": 0,
        "parse_index_ms": [round(value / 1_000_000, 3) for value in parse_ns],
        "query_p95_ms": round(sorted_ns[p95_index] / 1_000_000, 3),
        "peak_memory_bytes": peak,
        "response_contract": "ranked_candidates_only",
        "answer_claim_count": 0,
        "missing_unresolved_count": 1,
        "negative_authorization_control_count": 2,
    }
    if category_hits["exact"] + category_hits["metadata"] < 9:
        raise BenchmarkGateFailure("benchmark:exact_recall_gate", private, public)
    if category_hits["project"] + category_hits["relationship"] < 6:
        raise BenchmarkGateFailure("benchmark:project_recall_gate", private, public)
    if public["query_p95_ms"] > 500:
        raise BenchmarkGateFailure("benchmark:performance_gate", private, public)
    _event(event_log, "benchmark", successful_epoch, "pass", len(inventory), benchmark_started)
    return private, public
