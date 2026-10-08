"""Adversarial synthetic controls for the bounded Personal Recall adapter."""
from __future__ import annotations

import gc
import hashlib
import json
import os
import socket
import stat
import weakref
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest
from scripts import personal_recall as cli_module

from jarvis_core.identity import DuplicateIdentityError
from jarvis_core.personal_recall import benchmark as benchmark_module
from jarvis_core.personal_recall import corpus as corpus_module
from jarvis_core.personal_recall.benchmark import (
    classify_s1_response,
    network_blocked,
    run_benchmark,
    validate_private_row,
    validate_public_packet,
)
from jarvis_core.personal_recall.corpus import (
    acquire_sources,
    build_corpus,
    inventory_sources,
    materialize_private_snapshot,
    verify_private_snapshot,
)
from jarvis_core.personal_recall.policy import load_policy
from jarvis_core.policy.errors import PolicyError
from jarvis_core.policy.scope import AuthorizationScope
from jarvis_core.query.engine import QueryEngine

ROOTS = (
    "00 Inbox", "01 Daily Notes", "02 Projects", "03 Areas", "04 Wiki (Resources)",
)


def make_policy(tmp_path: Path, *, label: str = "private") -> tuple[Path, Path]:
    vault = tmp_path / "vault"
    vault.mkdir()
    for name in ROOTS:
        (vault / name).mkdir()
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({
        "schema_version": 1,
        "policy_id": "test",
        "policy_version": "1",
        "workspace_id": "test",
        "vault_root": str(vault),
        "max_sensitivity": "private",
        "rules": [
            {"pattern": f"{name}/**/*.md", "sensitivity": label}
            for name in ROOTS
        ],
    }), encoding="utf-8")
    return vault, policy


def make_manifest(tmp_path: Path, relpath: str) -> Path:
    categories = (
        ["exact"] * 6 + ["metadata"] * 4 + ["project"] * 4
        + ["relationship"] * 4 + ["paraphrase"] * 3
        + ["negative"] * 2 + ["missing"]
    )
    questions = [{
        "benchmark_question_id": f"synthetic-{index}",
        "category": category,
        "question": "unfindablezz" if category in ("negative", "missing") else "alpha",
        "expected_relpaths": [] if category in ("negative", "missing") else [relpath],
        "acceptable_alternates": [],
        "reason": "synthetic test",
        "max_sensitivity": "private",
    } for index, category in enumerate(categories)]
    manifest = tmp_path / "benchmark.json"
    manifest.write_text(json.dumps({
        "schema_version": 1, "benchmark_id": "synthetic", "questions": questions,
    }), encoding="utf-8")
    return manifest


def test_only_approved_markdown_is_read(tmp_path: Path) -> None:
    vault, path = make_policy(tmp_path)
    (vault / "00 Inbox" / "a.md").write_text("# Alpha\nsource phrase", encoding="utf-8")
    (vault / "00 Inbox" / "image.png").write_bytes(b"secret")
    (vault / "00 Inbox" / ".hidden.md").write_text("secret", encoding="utf-8")
    (vault / "00 Inbox" / "Archive").mkdir()
    (vault / "00 Inbox" / "Archive" / "old.md").write_text("secret", encoding="utf-8")
    (vault / "excluded.md").write_text("secret", encoding="utf-8")
    policy = load_policy(path)
    inventory = inventory_sources(policy)
    assert len(inventory) == 1
    assert inventory[0].relpath == "00 Inbox/a.md"
    notes = build_corpus(policy, inventory)
    assert len(notes) == 1
    assert notes[0].sensitivity == "private"
    assert notes[0].source_fingerprint == "sha256:" + inventory[0].sha256


@pytest.mark.parametrize("mutate", [
    lambda data: data.update(extra="bad"),
    lambda data: data["rules"][0].update(sensitivity="unknown"),
    lambda data: data["rules"][0].update(pattern="00 Inbox/../**/*.md"),
    lambda data: data["rules"][0].update(sensitivity="restricted"),
    lambda data: data.update(max_sensitivity="restricted"),
])
def test_policy_fail_closed(tmp_path: Path, mutate: object) -> None:
    _vault, path = make_policy(tmp_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    mutate(data)  # type: ignore[operator]
    path.write_text(json.dumps(data), encoding="utf-8")
    if data["rules"][0]["sensitivity"] == "restricted":
        assert load_policy(path).classify("00 Inbox/a.md") == "restricted"
    else:
        with pytest.raises(PolicyError):
            load_policy(path)


def test_path_traversal_unmatched_and_casefold(tmp_path: Path) -> None:
    _vault, path = make_policy(tmp_path)
    policy = load_policy(path)
    assert policy.classify("00 Inbox/../private.md") is None
    assert policy.classify("Outside/a.md") is None
    assert policy.classify("00 inbox/A.MD") == "private"


def test_restricted_policy_never_reads_source_bytes(tmp_path: Path) -> None:
    vault, path = make_policy(tmp_path, label="restricted")
    (vault / "00 Inbox" / "a.md").write_text("# Sensitive", encoding="utf-8")
    assert inventory_sources(load_policy(path)) == ()


def test_symlink_excluded_before_read(tmp_path: Path) -> None:
    vault, path = make_policy(tmp_path)
    outside = tmp_path / "outside.md"
    outside.write_text("excluded content", encoding="utf-8")
    try:
        (vault / "00 Inbox" / "escape.md").symlink_to(outside)
    except OSError:
        pytest.skip("symlink creation unavailable")
    with pytest.raises(PolicyError, match="reparse"):
        inventory_sources(load_policy(path))


def test_changed_source_refused(tmp_path: Path) -> None:
    vault, path = make_policy(tmp_path)
    note = vault / "00 Inbox" / "a.md"
    note.write_text("# Alpha", encoding="utf-8")
    policy = load_policy(path)
    inventory = inventory_sources(policy)
    note.write_text("# Changed", encoding="utf-8")
    with pytest.raises(PolicyError, match="fingerprint_changed"):
        build_corpus(policy, inventory)


def test_malformed_markdown_refused(tmp_path: Path) -> None:
    vault, path = make_policy(tmp_path)
    (vault / "00 Inbox" / "a.md").write_text("---\nbroken: [\n---\nbody", encoding="utf-8")
    policy = load_policy(path)
    with pytest.raises(PolicyError, match="parse_failure"):
        build_corpus(policy, inventory_sources(policy))


def test_three_run_benchmark_and_redacted_packet(tmp_path: Path) -> None:
    vault, path = make_policy(tmp_path)
    (vault / "00 Inbox" / "alpha.md").write_text(
        "# Alpha\nThe alpha project status is green.\n", encoding="utf-8"
    )
    policy = load_policy(path)
    manifest = make_manifest(tmp_path, "00 Inbox/alpha.md")
    private, public = run_benchmark(policy, inventory_sources(policy), manifest)
    assert public["deterministic_runs"] == 3
    assert public["category_top5_hits"]["exact"] == 6
    assert public["category_top5_hits"]["relationship"] == 4
    assert public["network_attempt_count"] == 0
    assert len(private["runs"]) == 3
    assert "alpha.md" not in json.dumps(public)
    assert "alpha.md" not in json.dumps(private)
    assert "The alpha project status is green" not in json.dumps(private)
    public["policy_sha256"] = "a" * 64
    public["source_integrity"] = "pass"
    validate_public_packet(public)
    public["private_relpath"] = "00 Inbox/alpha.md"
    with pytest.raises(PolicyError, match="privacy:public_schema"):
        validate_public_packet(public)


def test_authorized_incidental_negative_and_missing_candidates_pass(tmp_path: Path) -> None:
    vault, path = make_policy(tmp_path)
    (vault / "00 Inbox" / "alpha.md").write_text(
        "# Alpha\nalpha evidence", encoding="utf-8"
    )
    policy = load_policy(path)
    manifest = make_manifest(tmp_path, "00 Inbox/alpha.md")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    for question in data["questions"]:
        if question["category"] in ("negative", "missing"):
            question["question"] = "alpha"
    manifest.write_text(json.dumps(data), encoding="utf-8")
    private, public = run_benchmark(policy, inventory_sources(policy), manifest)
    assert len(private["runs"]) == 3
    assert public["deterministic_runs"] == 3
    assert [row["coverage"] for row in private["runs"][0][-3:]] == [
        "complete", "complete", "complete"
    ]
    assert private["runs"][0][-1]["response_semantics"] == {
        "result_type": "ranked_retrieval_candidates",
        "answer_claim": "none",
        "resolution": "unresolved",
        "candidate_role": "candidate_not_answer",
        "expected_answer_source_claimed": False,
    }
    assert "alpha.md" not in json.dumps(public)


def test_claim_or_excluded_leak_fails_closed(tmp_path: Path) -> None:
    vault, path = make_policy(tmp_path)
    (vault / "00 Inbox" / "alpha.md").write_text(
        "# Alpha\nalpha evidence", encoding="utf-8"
    )
    policy = load_policy(path)
    manifest = make_manifest(tmp_path, "00 Inbox/alpha.md")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    for question in data["questions"]:
        if question["category"] == "negative":
            question["question"] = "alpha"
    manifest.write_text(json.dumps(data), encoding="utf-8")
    private, public = run_benchmark(policy, inventory_sources(policy), manifest)
    negative = dict(private["runs"][0][-3])
    assert negative["citations"]
    negative["excluded_identity"] = "forbidden.md"
    with pytest.raises(PolicyError, match="privacy:private_schema"):
        validate_private_row(
            negative, category="negative",
            question_id=str(negative["benchmark_question_id"]), source_count=1,
        )
    row = dict(private["runs"][0][-1])
    assert row["response_semantics"]["resolution"] == "unresolved"
    claim = dict(row["response_semantics"])
    claim["answer_claim"] = "asserted"
    row["response_semantics"] = claim
    with pytest.raises(PolicyError, match="privacy:response_semantics"):
        validate_private_row(
            row, category="missing", question_id=str(row["benchmark_question_id"]),
            source_count=1,
        )
    row["response_semantics"] = private["runs"][0][-1]["response_semantics"]
    row["excluded_content"] = "forbidden source text"
    with pytest.raises(PolicyError, match="privacy:private_schema"):
        validate_private_row(
            row, category="missing", question_id=str(row["benchmark_question_id"]),
            source_count=1,
        )
    public["excluded_identity"] = "forbidden.md"
    public["policy_sha256"] = "a" * 64
    public["source_integrity"] = "pass"
    with pytest.raises(PolicyError, match="privacy:public_schema"):
        validate_public_packet(public)


def test_asserted_missing_answer_text_fails_classification() -> None:
    from jarvis_core.query.intent import Intent
    from jarvis_core.query.results import QueryAnswer
    answer = QueryAnswer(Intent.SEARCH, "alpha", "The missing answer is alpha.")
    trace = SimpleNamespace(ranked=())
    with pytest.raises(PolicyError, match="benchmark:answer_claim"):
        classify_s1_response(answer, trace, ("alpha",), "missing")  # type: ignore[arg-type]


def test_benchmark_acquires_once_and_never_reopens_for_citations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    vault, path = make_policy(tmp_path)
    (vault / "00 Inbox" / "alpha.md").write_text("# Alpha\nalpha evidence", encoding="utf-8")
    policy = load_policy(path)
    inventory = inventory_sources(policy)
    manifest = make_manifest(tmp_path, inventory[0].relpath)
    original_read = corpus_module.read_frozen_source
    original_engine = benchmark_module.QueryEngine
    reads: list[str] = []
    note_orders: list[tuple[int, ...]] = []

    def read_once(policy_arg: object, source: object) -> object:
        reads.append(source.relpath)  # type: ignore[attr-defined]
        return original_read(policy_arg, source)  # type: ignore[arg-type]

    class RecordingEngine(original_engine):
        def __init__(self, notes: object, **kwargs: object) -> None:
            note_orders.append(tuple(id(note) for note in notes))  # type: ignore[arg-type]
            super().__init__(notes, **kwargs)  # type: ignore[arg-type]

    def forbidden_live_citation(*_args: object, **_kwargs: object) -> bytes:
        raise AssertionError("live citation reopen")

    monkeypatch.setattr(corpus_module, "read_frozen_source", read_once)
    monkeypatch.setattr(benchmark_module, "QueryEngine", RecordingEngine)
    monkeypatch.setattr(
        benchmark_module.CurrentSourceResolver, "current_bytes", forbidden_live_citation
    )
    private, public = run_benchmark(policy, inventory, manifest)
    assert reads == [inventory[0].relpath]
    assert len(note_orders) == 3
    assert note_orders[0] == note_orders[1] == note_orders[2]
    assert public["deterministic_runs"] == 3
    assert "alpha.md" not in json.dumps(private)


@pytest.mark.parametrize("stage", ["during_acquisition", "after_acquisition", "before_postrun"])
def test_benchmark_source_mutation_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stage: str,
) -> None:
    vault, path = make_policy(tmp_path)
    note = vault / "00 Inbox" / "alpha.md"
    note.write_text("# Alpha\nalpha evidence", encoding="utf-8")
    policy = load_policy(path)
    inventory = inventory_sources(policy)
    manifest = make_manifest(tmp_path, inventory[0].relpath)

    if stage == "during_acquisition":
        original_read = corpus_module.read_frozen_source

        def mutate_before_read(policy_arg: object, source: object) -> object:
            note.write_text("# Changed\nalpha evidence", encoding="utf-8")
            return original_read(policy_arg, source)  # type: ignore[arg-type]

        monkeypatch.setattr(corpus_module, "read_frozen_source", mutate_before_read)
    elif stage == "after_acquisition":
        original_acquire = benchmark_module.acquire_sources

        def mutate_after_read(policy_arg: object, sources: object) -> object:
            acquired = original_acquire(policy_arg, sources)  # type: ignore[arg-type]
            note.write_text("# Changed\nalpha evidence", encoding="utf-8")
            return acquired

        monkeypatch.setattr(benchmark_module, "acquire_sources", mutate_after_read)
    else:
        original_inventory = benchmark_module.inventory_sources
        calls = 0

        def mutate_before_postrun(policy_arg: object) -> object:
            nonlocal calls
            calls += 1
            if calls == 3:
                note.write_text("# Changed\nalpha evidence", encoding="utf-8")
            return original_inventory(policy_arg)  # type: ignore[arg-type]

        monkeypatch.setattr(benchmark_module, "inventory_sources", mutate_before_postrun)

    expected = {
        "during_acquisition": "acquisition:fingerprint_mismatch",
        "after_acquisition": "post_acquisition_inventory:integrity_mismatch",
        "before_postrun": "final_inventory:integrity_mismatch",
    }
    with pytest.raises(PolicyError, match=expected[stage]):
        run_benchmark(policy, inventory, manifest)


@pytest.mark.parametrize("checkpoint,fail_call", [
    ("initial_inventory", 1),
    ("post_acquisition_inventory", 2),
    ("final_inventory", 3),
])
def test_whole_corpus_availability_retry_then_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, checkpoint: str, fail_call: int,
) -> None:
    vault, path = make_policy(tmp_path)
    (vault / "00 Inbox" / "alpha.md").write_text("# Alpha\nalpha evidence", encoding="utf-8")
    policy = load_policy(path)
    inventory = inventory_sources(policy)
    manifest = make_manifest(tmp_path, inventory[0].relpath)
    original_inventory = benchmark_module.inventory_sources
    original_acquire = benchmark_module.acquire_sources
    original_engine = benchmark_module.QueryEngine
    inventory_calls = 0
    acquisition_count = 0
    engine_count = 0
    discarded: list[weakref.ReferenceType[object]] = []
    events: list[dict[str, object]] = []

    def flaky_inventory(policy_arg: object) -> object:
        nonlocal inventory_calls
        inventory_calls += 1
        if inventory_calls == fail_call:
            raise PolicyError("source_boundary:metadata_unavailable")
        return original_inventory(policy_arg)  # type: ignore[arg-type]

    def tracked_acquire(policy_arg: object, sources: object) -> object:
        nonlocal acquisition_count
        acquisition_count += 1
        acquired = original_acquire(policy_arg, sources)  # type: ignore[arg-type]
        discarded.append(weakref.ref(acquired[0]))
        return acquired

    class RecordingEngine(original_engine):
        def __init__(self, notes: object, **kwargs: object) -> None:
            nonlocal engine_count
            assert any(
                event["checkpoint"] == "post_acquisition_inventory"
                and event["outcome"] == "pass" for event in events
            )
            engine_count += 1
            super().__init__(notes, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(benchmark_module, "inventory_sources", flaky_inventory)
    monkeypatch.setattr(benchmark_module, "acquire_sources", tracked_acquire)
    monkeypatch.setattr(benchmark_module, "QueryEngine", RecordingEngine)
    monkeypatch.setattr(benchmark_module.time, "sleep", lambda _delay: None)
    private, public = run_benchmark(policy, inventory, manifest, events)
    assert public["deterministic_runs"] == 3
    assert engine_count == 3
    assert acquisition_count == (2 if checkpoint == "post_acquisition_inventory" else 1)
    assert any(
        event["checkpoint"] == checkpoint and event["outcome"] == "availability_unavailable"
        for event in events
    )
    assert len(private["checkpoint_events"]) == len(events)
    assert "alpha.md" not in json.dumps(events)
    gc.collect()
    assert all(ref() is None for ref in discarded)


@pytest.mark.parametrize("checkpoint", ["initial_inventory", "final_inventory"])
def test_availability_bound_exhausts_without_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, checkpoint: str,
) -> None:
    vault, path = make_policy(tmp_path)
    (vault / "00 Inbox" / "alpha.md").write_text("# Alpha\nalpha evidence", encoding="utf-8")
    policy = load_policy(path)
    inventory = inventory_sources(policy)
    manifest = make_manifest(tmp_path, inventory[0].relpath)
    original_inventory = benchmark_module.inventory_sources
    calls = 0
    events: list[dict[str, object]] = []

    def unavailable(policy_arg: object) -> object:
        nonlocal calls
        calls += 1
        if checkpoint == "initial_inventory" or calls >= 3:
            raise PolicyError("source_boundary:read_failed")
        return original_inventory(policy_arg)  # type: ignore[arg-type]

    monkeypatch.setattr(benchmark_module, "inventory_sources", unavailable)
    monkeypatch.setattr(benchmark_module.time, "sleep", lambda _delay: None)
    expected = "acquisition" if checkpoint == "initial_inventory" else "final_inventory"
    with pytest.raises(benchmark_module.CheckpointFailure) as caught:
        run_benchmark(policy, inventory, manifest, events)
    assert str(caught.value) == f"{expected}:availability_exhausted"
    assert calls == (3 if checkpoint == "initial_inventory" else 5)
    assert sum(event["outcome"] == "availability_unavailable" for event in events) == 3


def test_initial_inventory_mismatch_never_retries(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    vault, path = make_policy(tmp_path)
    (vault / "00 Inbox" / "alpha.md").write_text("# Alpha\nalpha evidence", encoding="utf-8")
    policy = load_policy(path)
    inventory = inventory_sources(policy)
    manifest = make_manifest(tmp_path, inventory[0].relpath)
    calls = 0

    def mismatch(_policy: object) -> object:
        nonlocal calls
        calls += 1
        return ()

    monkeypatch.setattr(benchmark_module, "inventory_sources", mismatch)
    with pytest.raises(
        benchmark_module.CheckpointFailure, match="initial_inventory:integrity_mismatch"
    ):
        run_benchmark(policy, inventory, manifest)
    assert calls == 1


@pytest.mark.parametrize("fail_count", [1, 3])
def test_acquisition_availability_retries_only_whole_epochs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fail_count: int,
) -> None:
    vault, path = make_policy(tmp_path)
    (vault / "00 Inbox" / "alpha.md").write_text("# Alpha\nalpha evidence", encoding="utf-8")
    policy = load_policy(path)
    inventory = inventory_sources(policy)
    manifest = make_manifest(tmp_path, inventory[0].relpath)
    original_acquire = benchmark_module.acquire_sources
    calls = 0
    events: list[dict[str, object]] = []

    def unavailable(policy_arg: object, sources: object) -> object:
        nonlocal calls
        calls += 1
        if calls <= fail_count:
            raise PolicyError("source_boundary:metadata_unavailable")
        return original_acquire(policy_arg, sources)  # type: ignore[arg-type]

    monkeypatch.setattr(benchmark_module, "acquire_sources", unavailable)
    monkeypatch.setattr(benchmark_module.time, "sleep", lambda _delay: None)
    if fail_count == 3:
        with pytest.raises(
            benchmark_module.CheckpointFailure, match="acquisition:availability_exhausted"
        ):
            run_benchmark(policy, inventory, manifest, events)
        assert calls == 3
    else:
        _private, public = run_benchmark(policy, inventory, manifest, events)
        assert public["deterministic_runs"] == 3
        assert calls == 2
    assert sum(event["outcome"] == "availability_unavailable" for event in events) == fail_count
    assert all(set(event) == {
        "checkpoint", "attempt", "outcome", "source_count", "elapsed_ms"
    } for event in events)


def test_partial_acquisition_restarts_from_first_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    vault, path = make_policy(tmp_path)
    for name in ("alpha.md", "beta.md"):
        (vault / "00 Inbox" / name).write_text("# Alpha\nalpha evidence", encoding="utf-8")
    policy = load_policy(path)
    inventory = inventory_sources(policy)
    manifest = make_manifest(tmp_path, inventory[0].relpath)
    original_read = corpus_module.read_frozen_source
    reads: list[str] = []

    def fail_second_once(policy_arg: object, source: object) -> object:
        reads.append(source.relpath)  # type: ignore[attr-defined]
        if len(reads) == 2:
            raise PolicyError("source_boundary:read_failed")
        return original_read(policy_arg, source)  # type: ignore[arg-type]

    monkeypatch.setattr(corpus_module, "read_frozen_source", fail_second_once)
    monkeypatch.setattr(benchmark_module.time, "sleep", lambda _delay: None)
    events: list[dict[str, object]] = []
    _private, public = run_benchmark(policy, inventory, manifest, events)
    assert public["deterministic_runs"] == 3
    assert reads == [
        inventory[0].relpath, inventory[1].relpath,
        inventory[0].relpath, inventory[1].relpath,
    ]
    assert any(
        event["checkpoint"] == "acquisition" and event["attempt"] == 1
        and event["outcome"] == "availability_unavailable" for event in events
    )


def test_post_acquisition_availability_exhausts_whole_epochs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    vault, path = make_policy(tmp_path)
    (vault / "00 Inbox" / "alpha.md").write_text("# Alpha\nalpha evidence", encoding="utf-8")
    policy = load_policy(path)
    inventory = inventory_sources(policy)
    manifest = make_manifest(tmp_path, inventory[0].relpath)
    original_inventory = benchmark_module.inventory_sources
    calls = 0
    events: list[dict[str, object]] = []

    def unavailable_after_acquisition(policy_arg: object) -> object:
        nonlocal calls
        calls += 1
        if calls % 2 == 0:
            raise PolicyError("source_boundary:scan_failed")
        return original_inventory(policy_arg)  # type: ignore[arg-type]

    monkeypatch.setattr(benchmark_module, "inventory_sources", unavailable_after_acquisition)
    monkeypatch.setattr(benchmark_module.time, "sleep", lambda _delay: None)
    with pytest.raises(
        benchmark_module.CheckpointFailure, match="acquisition:availability_exhausted"
    ):
        run_benchmark(policy, inventory, manifest, events)
    assert calls == 6
    assert sum(
        event["checkpoint"] == "post_acquisition_inventory"
        and event["outcome"] == "availability_unavailable" for event in events
    ) == 3


def test_benchmark_checkpoint_failure_is_fixed_and_path_free(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    vault, path = make_policy(tmp_path)
    (vault / "00 Inbox" / "alpha.md").write_text("# Alpha\nalpha evidence", encoding="utf-8")
    policy = load_policy(path)
    inventory = inventory_sources(policy)
    manifest = make_manifest(tmp_path, inventory[0].relpath)

    def unsafe_engine(*_args: object, **_kwargs: object) -> object:
        raise PolicyError("source_boundary:parse_failure")

    monkeypatch.setattr(benchmark_module, "QueryEngine", unsafe_engine)
    events: list[dict[str, object]] = []
    with pytest.raises(benchmark_module.CheckpointFailure, match="benchmark:parse_failure"):
        run_benchmark(policy, inventory, manifest, events)
    assert events[-1]["checkpoint"] == "benchmark"
    assert events[-1]["outcome"] == "parse_failure"
    assert "alpha.md" not in json.dumps(events)


def test_failed_proof_retains_only_closed_checkpoint_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    vault, policy_path = make_policy(tmp_path)
    (vault / "00 Inbox" / "alpha.md").write_text("# Alpha\nprivate phrase", encoding="utf-8")
    inventory = inventory_sources(load_policy(policy_path))
    private = tmp_path / "private"
    private.mkdir()
    (private / "baseline-inventory-v2.json").write_text(
        json.dumps([row.__dict__ for row in inventory]), encoding="utf-8"
    )
    args = SimpleNamespace(
        private=private, public=tmp_path / "public", policy=policy_path,
        manifest=make_manifest(tmp_path, inventory[0].relpath),
    )
    calls = 0

    def fixed_failure(_policy: object, _inventory: object, _manifest: object,
                      events: list[dict[str, object]]) -> object:
        nonlocal calls
        calls += 1
        events.append({
            "checkpoint": "initial_inventory", "attempt": 1,
            "outcome": "integrity_mismatch", "source_count": 1, "elapsed_ms": 1.0,
        })
        raise benchmark_module.CheckpointFailure("initial_inventory", 1, "integrity_mismatch")

    monkeypatch.setattr(cli_module, "_check_evidence_boundary", lambda _args: None)
    monkeypatch.setattr(cli_module, "run_benchmark", fixed_failure)
    with pytest.raises(benchmark_module.CheckpointFailure):
        cli_module.benchmark(args)
    evidence = (private / "benchmark-attempt-evidence.json").read_text(encoding="utf-8")
    parsed = json.loads(evidence)
    assert set(parsed) == {"schema_version", "task", "status", "failure_category", "events"}
    assert parsed["failure_category"] == "initial_inventory:integrity_mismatch"
    assert "alpha.md" not in evidence
    assert "private phrase" not in evidence
    with pytest.raises(RuntimeError, match="result_exists"):
        cli_module.benchmark(args)
    assert calls == 1


def test_corpus_epoch_five_minute_bound_is_terminal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    vault, path = make_policy(tmp_path)
    (vault / "00 Inbox" / "alpha.md").write_text("# Alpha\nalpha evidence", encoding="utf-8")
    policy = load_policy(path)
    inventory = inventory_sources(policy)
    manifest = make_manifest(tmp_path, inventory[0].relpath)
    clock_values = iter((0.0, 301.0))
    monkeypatch.setattr(benchmark_module.time, "monotonic", lambda: next(clock_values))
    with pytest.raises(benchmark_module.CheckpointFailure, match="acquisition:time_limit"):
        run_benchmark(policy, inventory, manifest)


def test_private_snapshot_is_closed_world_and_read_only(tmp_path: Path) -> None:
    vault, path = make_policy(tmp_path)
    source = vault / "00 Inbox" / "alpha.md"
    source.write_text("# Alpha\nalpha evidence", encoding="utf-8")
    (vault / "00 Inbox" / "unsupported.bin").write_bytes(b"excluded")
    policy = load_policy(path)
    inventory = inventory_sources(policy)
    destination = tmp_path / "snapshot"
    materialize_private_snapshot(policy, acquire_sources(policy, inventory), destination)
    snapshot_policy = replace(policy, vault_root=destination)
    copied = destination / "00 Inbox" / "alpha.md"
    try:
        verified = verify_private_snapshot(snapshot_policy, inventory)
        assert [(r.relpath, r.size, r.sha256) for r in verified] == [
            (r.relpath, r.size, r.sha256) for r in inventory
        ]
        assert not (destination / "00 Inbox" / "unsupported.bin").exists()
        assert copied.stat().st_file_attributes & stat.FILE_ATTRIBUTE_READONLY
        assert source.read_bytes() == copied.read_bytes()
        (destination / "00 Inbox" / "extra.bin").write_bytes(b"extra")
        with pytest.raises(PolicyError, match="snapshot:unexpected_entry"):
            verify_private_snapshot(snapshot_policy, inventory)
        with pytest.raises(PolicyError, match="snapshot:destination_unavailable"):
            materialize_private_snapshot(policy, acquire_sources(policy, inventory), destination)
    finally:
        os.chmod(copied, stat.S_IWRITE | stat.S_IREAD)


@pytest.mark.parametrize("bad_relpath", ["../escape.md", "00 Inbox/unsupported.bin"])
def test_snapshot_rejects_escape_and_unsupported_path_before_write(
    tmp_path: Path, bad_relpath: str,
) -> None:
    vault, path = make_policy(tmp_path)
    (vault / "00 Inbox" / "alpha.md").write_text("# Alpha", encoding="utf-8")
    policy = load_policy(path)
    acquired = acquire_sources(policy, inventory_sources(policy))
    bad = replace(acquired[0], inventory=replace(acquired[0].inventory, relpath=bad_relpath))
    destination = tmp_path / "snapshot"
    with pytest.raises(PolicyError, match="snapshot:source_boundary"):
        materialize_private_snapshot(policy, (bad,), destination)
    assert not destination.exists()


def test_snapshot_rejects_case_colliding_identity_before_write(tmp_path: Path) -> None:
    vault, path = make_policy(tmp_path)
    (vault / "00 Inbox" / "alpha.md").write_text("# Alpha", encoding="utf-8")
    policy = load_policy(path)
    acquired = acquire_sources(policy, inventory_sources(policy))
    collision = replace(
        acquired[0], inventory=replace(acquired[0].inventory, relpath="00 Inbox/ALPHA.md")
    )
    destination = tmp_path / "snapshot"
    with pytest.raises(PolicyError, match="snapshot:duplicate_identity"):
        materialize_private_snapshot(policy, (acquired[0], collision), destination)
    assert not destination.exists()


def test_snapshot_proof_synthetic_end_to_end_retains_copy(tmp_path: Path,
                                                          monkeypatch: pytest.MonkeyPatch) -> None:
    vault, policy_path = make_policy(tmp_path)
    source = vault / "00 Inbox" / "alpha.md"
    source.write_text("# Alpha\nalpha evidence", encoding="utf-8")
    original_bytes = source.read_bytes()
    private = tmp_path / "private"
    private.mkdir()
    public = tmp_path / "public"
    manifest = make_manifest(tmp_path, "00 Inbox/alpha.md")
    args = SimpleNamespace(
        private=private, public=public, policy=policy_path, manifest=manifest,
    )
    monkeypatch.setattr(cli_module, "_check_evidence_boundary", lambda _args: None)
    try:
        assert cli_module.snapshot_proof(args) == 0
        snapshot = private / "pr03" / "snapshot"
        assert snapshot.is_dir()
        assert (snapshot / "00 Inbox" / "alpha.md").read_bytes() == original_bytes
        assert source.read_bytes() == original_bytes
        assert (private / "pr03" / "snapshot-inventory.json").is_file()
        assert (private / "pr03" / "benchmark-results.json").is_file()
        assert json.loads((private / "pr03" / "benchmark-attempt-evidence.json").read_text())[
            "status"
        ] == "passed"
        packet = json.loads(
            (public / "personal-recall-s0s1-snapshot-aggregate.json").read_text()
        )
        assert packet["task"] == "V06-PR-03"
        assert packet["deterministic_runs"] == 3
        assert "alpha.md" not in json.dumps(packet)
        with pytest.raises(PolicyError, match="snapshot:already_exists"):
            cli_module.snapshot_proof(args)
    finally:
        copied = private / "pr03" / "snapshot" / "00 Inbox" / "alpha.md"
        if copied.exists():
            os.chmod(copied, stat.S_IWRITE | stat.S_IREAD)


def test_corrected_snapshot_proof_retains_history_and_copy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    vault, policy_path = make_policy(tmp_path)
    source = vault / "00 Inbox" / "alpha.md"
    source.write_text("# Alpha\nalpha evidence", encoding="utf-8")
    policy = load_policy(policy_path)
    original = inventory_sources(policy)
    private = tmp_path / "private"
    pr03 = private / "pr03"
    pr03.mkdir(parents=True)
    copied = pr03 / "snapshot" / "00 Inbox" / "alpha.md"
    public = tmp_path / "public"
    public.mkdir()
    manifest = make_manifest(tmp_path, original[0].relpath)
    historical = {
        "snapshot-inventory.json": cli_module.canonical_json(
            [row.__dict__ for row in original]
        ),
        "benchmark-attempt-evidence.json": b"historical-attempt\n",
        "benchmark-failed-results.json": b"historical-failure\n",
    }
    for name, content in historical.items():
        (pr03 / name).write_bytes(content)
    failed_public = public / "personal-recall-s0s1-snapshot-failed-aggregate.json"
    failed_public.write_bytes(b"historical-redacted\n")
    def digest(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()
    monkeypatch.setattr(cli_module, "_check_evidence_boundary", lambda _args: None)
    monkeypatch.setattr(
        cli_module, "_PR03_FROZEN",
        {name: digest(content) for name, content in historical.items()},
    )
    monkeypatch.setattr(
        cli_module, "_PR03_FAILED_PUBLIC_SHA256", digest(failed_public.read_bytes())
    )
    monkeypatch.setattr(cli_module, "_PR03_MANIFEST_SHA256", digest(manifest.read_bytes()))
    args = SimpleNamespace(
        private=private, public=public, policy=policy_path, manifest=manifest,
    )
    try:
        materialize_private_snapshot(policy, acquire_sources(policy, original), pr03 / "snapshot")
        before = digest(copied.read_bytes())
        assert cli_module.snapshot_corrected_proof(args) == 0
        assert digest(copied.read_bytes()) == before
        assert all((pr03 / name).read_bytes() == content
                   for name, content in historical.items())
        assert failed_public.read_bytes() == b"historical-redacted\n"
        assert (pr03 / "corrected-benchmark-results.json").is_file()
        assert (public / "personal-recall-s0s1-snapshot-corrected-aggregate.json").is_file()
        with pytest.raises(PolicyError, match="snapshot:corrected_result_boundary"):
            cli_module.snapshot_corrected_proof(args)
    finally:
        if copied.exists():
            os.chmod(copied, stat.S_IWRITE | stat.S_IREAD)


def test_excluded_content_cannot_reach_index_or_result(tmp_path: Path) -> None:
    vault, path = make_policy(tmp_path)
    (vault / "00 Inbox" / "allowed.md").write_text("# Allowed\nalpha", encoding="utf-8")
    (vault / "excluded.md").write_text("# Forbidden\nuniquesecretterm", encoding="utf-8")
    policy = load_policy(path)
    notes = build_corpus(policy, inventory_sources(policy))
    scope = AuthorizationScope(
        workspace_id="test", max_sensitivity="private", request_id="synthetic",
        allowed_path_prefixes=policy.include_roots,
    )
    answer = QueryEngine(notes, scope=scope, source_root=vault).search("uniquesecretterm")
    assert not answer.citations
    assert "excluded.md" not in json.dumps(answer.to_dict())


def test_duplicate_explicit_identity_fails_closed(tmp_path: Path) -> None:
    vault, path = make_policy(tmp_path)
    for name in ("first.md", "second.md"):
        (vault / "00 Inbox" / name).write_text(
            "---\nid: repeated\n---\n# Alpha\n", encoding="utf-8"
        )
    policy = load_policy(path)
    notes = build_corpus(policy, inventory_sources(policy))
    scope = AuthorizationScope(
        workspace_id="test", max_sensitivity="private", request_id="synthetic",
        allowed_path_prefixes=policy.include_roots,
    )
    with pytest.raises(DuplicateIdentityError):
        QueryEngine(notes, scope=scope, source_root=vault)


def test_network_attempt_blocked() -> None:
    with network_blocked() as attempts, pytest.raises(RuntimeError, match="network_disabled"):
        socket.socket()
    assert len(attempts) == 1
    with network_blocked() as dns_attempts, pytest.raises(RuntimeError, match="network_disabled"):
        socket.getaddrinfo("example.invalid", 443)
    assert len(dns_attempts) == 1


def test_corpus_never_requests_write_mode(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    vault, path = make_policy(tmp_path)
    (vault / "00 Inbox" / "a.md").write_text("# Alpha", encoding="utf-8")
    policy = load_policy(path)
    inventory = inventory_sources(policy)
    original_open = Path.open

    def guarded_open(self: Path, mode: str = "r", *args: object, **kwargs: object) -> object:
        if self.is_relative_to(vault) and any(char in mode for char in "wax+"):
            raise AssertionError("vault write attempted")
        return original_open(self, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guarded_open)
    assert len(build_corpus(policy, inventory)) == 1


def test_unicode_em_dash_filename_round_trip(tmp_path: Path) -> None:
    vault, path = make_policy(tmp_path)
    name = "Index " + chr(0x2014) + " contents.md"
    (vault / "04 Wiki (Resources)" / name).write_text("# Index", encoding="utf-8")
    policy = load_policy(path)
    first = inventory_sources(policy)
    serialized = json.dumps([row.__dict__ for row in first], ensure_ascii=False)
    restored = json.loads(serialized)
    second = inventory_sources(policy)
    assert first == second
    assert restored[0]["relpath"] == first[0].relpath
    assert [ord(char) for char in first[0].relpath if ord(char) > 127] == [0x2014]
    assert "".join(map(chr, [0xE2, 0x20AC, 0x201D])) not in serialized


def test_citation_declined_after_source_drift(tmp_path: Path) -> None:
    vault, path = make_policy(tmp_path)
    source = vault / "00 Inbox" / "alpha.md"
    source.write_text("# Alpha\nalpha evidence", encoding="utf-8")
    policy = load_policy(path)
    notes = build_corpus(policy, inventory_sources(policy))
    scope = AuthorizationScope(
        workspace_id="test", max_sensitivity="private", request_id="synthetic",
        allowed_path_prefixes=policy.include_roots,
    )
    engine = QueryEngine(notes, scope=scope, source_root=vault)
    assert engine.search("alpha").citations
    source.write_text("# Alpha\nchanged evidence", encoding="utf-8")
    assert not engine.search("alpha").citations
