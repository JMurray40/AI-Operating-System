"""Native-Windows entry point for the bounded V06-PR-01 proof."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import uuid
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from jarvis_core.personal_recall.benchmark import (
    BenchmarkGateFailure,
    CheckpointFailure,
    canonical_json,
    network_blocked,
    run_benchmark,
    validate_public_packet,
)
from jarvis_core.personal_recall.corpus import (
    SourceInventory,
    acquire_sources,
    inventory_sources,
    materialize_private_snapshot,
    resolve_roots,
    verify_private_snapshot,
)
from jarvis_core.personal_recall.policy import load_policy
from jarvis_core.policy.errors import PolicyError

_APPROVED_VAULT = Path(r"C:\Users\jmurr\The BRAIN")
_PR03_FROZEN = {
    "snapshot-inventory.json": "e8cb54d9ec1fe1cabd348a0cc1845bb7a2ce64e838e633449e3171c3ea6ea75a",
    "benchmark-attempt-evidence.json": (
        "0aa9eb07757db05e4a105efe2add53e510e87b0b27afaf700d93802800104e53"
    ),
    "benchmark-failed-results.json": (
        "e3f71fa800163f6acfbe296e4f7b9ac74fd072434170af68bad57cbbc3a4c7ee"
    ),
}
_PR03_FAILED_PUBLIC_SHA256 = "394b428d4334ff32c202ea1e3dc4188f8f05520ea5987cb7c4e4356f4627a601"
_PR03_MANIFEST_SHA256 = "9d70850c5a2a0b746c506c70c4df90e0ba73c892a4e3554e48907c3b5a4decdc"


def _exclusive_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _check_evidence_boundary(args: argparse.Namespace) -> None:
    repo = args.repo.resolve(strict=True)
    private = args.private.resolve()
    public = args.public.resolve()
    expected_private = repo / "data" / "v0.6-evidence" / "personal-recall" / "private"
    expected_public = repo / "docs" / "evidence" / "v0.6"
    if private != expected_private or public != expected_public:
        raise RuntimeError("evidence_boundary")
    policy = load_policy(args.policy)
    if policy.vault_root.resolve(strict=True) != _APPROVED_VAULT.resolve(strict=True):
        raise RuntimeError("vault_boundary")
    if private.is_relative_to(policy.vault_root) or public.is_relative_to(policy.vault_root):
        raise RuntimeError("evidence_boundary")


def preflight(args: argparse.Namespace) -> int:
    _check_evidence_boundary(args)
    policy = load_policy(args.policy)
    vault, roots = resolve_roots(policy)
    inventory = inventory_sources(policy)
    payload = {
        "schema_version": 1,
        "task": "V06-PR-01",
        "status": "pass",
        "core_commit": args.commit,
        "core_tree": args.tree,
        "include_root_count": len(roots),
        "root_digest": hashlib.sha256(str(vault).casefold().encode()).hexdigest(),
        "policy_sha256": hashlib.sha256(args.policy.read_bytes()).hexdigest(),
        "source_count": len(inventory),
        "source_bytes": sum(s.size for s in inventory),
        "source_inventory_sha256": hashlib.sha256(canonical_json([
            {"relpath": s.relpath, "size": s.size, "mtime_ns": s.mtime_ns, "sha256": s.sha256}
            for s in inventory
        ])).hexdigest(),
        "read_only_open": True,
        "reparse_check": "pass",
        "network_required": False,
    }
    private_inventory = [s.__dict__ for s in inventory]
    if args.revision == "v2":
        baseline = json.loads((args.private / "baseline-inventory-v2.json").read_text(
            encoding="utf-8"
        ))
        if baseline != private_inventory:
            raise RuntimeError("source_integrity_failure")
        _exclusive_write(args.private / "preflight-v2.json", canonical_json(payload))
    else:
        _exclusive_write(args.private / "preflight.json", canonical_json(payload))
        _exclusive_write(
            args.private / "baseline-inventory.json", canonical_json(private_inventory)
        )
    print("preflight=pass")
    return 0


def benchmark(args: argparse.Namespace) -> int:
    _check_evidence_boundary(args)
    policy = load_policy(args.policy)
    attempt_path = args.private / "benchmark-attempt-evidence.json"
    private_result_path = args.private / "benchmark-results.json"
    public_result_path = args.public / "personal-recall-s0s1-aggregate.json"
    if any(path.exists() for path in (attempt_path, private_result_path, public_result_path)):
        raise RuntimeError("result_exists")
    inventory_raw = json.loads((args.private / "baseline-inventory-v2.json").read_text())
    from jarvis_core.personal_recall.corpus import SourceInventory
    inventory = tuple(SourceInventory(**row) for row in inventory_raw)
    events: list[dict[str, object]] = []
    try:
        private, public = run_benchmark(policy, inventory, args.manifest, events)
        public["policy_sha256"] = hashlib.sha256(args.policy.read_bytes()).hexdigest()
        public["source_integrity"] = "pass"
        validate_public_packet(public)
        public_bytes = canonical_json(public)
    except PolicyError as exc:
        category = (
            f"{exc.checkpoint}:{exc.outcome}"
            if isinstance(exc, CheckpointFailure) else "benchmark:validation_failure"
        )
        _exclusive_write(attempt_path, canonical_json({
            "schema_version": 1, "task": "V06-PR-01", "status": "failed",
            "failure_category": category, "events": events,
        }))
        raise
    _exclusive_write(private_result_path, canonical_json(private))
    _exclusive_write(public_result_path, public_bytes)
    _exclusive_write(attempt_path, canonical_json({
        "schema_version": 1, "task": "V06-PR-01", "status": "passed",
        "failure_category": None, "events": events,
    }))
    print(f"benchmark=pass packet_sha256={hashlib.sha256(public_bytes).hexdigest()}")
    return 0


def snapshot_proof(args: argparse.Namespace) -> int:
    """Create and retain one private, read-only snapshot before a bounded proof."""
    _check_evidence_boundary(args)
    policy = load_policy(args.policy)
    private_root = args.private / "pr03"
    snapshot_root = private_root / "snapshot"
    inventory_path = private_root / "snapshot-inventory.json"
    result_path = private_root / "benchmark-results.json"
    attempt_path = private_root / "benchmark-attempt-evidence.json"
    public_path = args.public / "personal-recall-s0s1-snapshot-aggregate.json"
    if any(path.exists() for path in (
        private_root, snapshot_root, inventory_path, result_path, attempt_path, public_path
    )):
        raise PolicyError("snapshot:already_exists")
    events: list[dict[str, object]] = []
    try:
        with network_blocked() as network_attempts:
            original_inventory = inventory_sources(policy)
            acquired = acquire_sources(policy, original_inventory)
            if network_attempts:
                raise PolicyError("snapshot:network_attempt")
            private_root.mkdir()
            materialize_private_snapshot(policy, acquired, snapshot_root)
            acquired = ()  # the benchmark reads only the retained copy
            snapshot_policy = replace(policy, vault_root=snapshot_root)
            first_verified = verify_private_snapshot(snapshot_policy, original_inventory)
            _exclusive_write(
                inventory_path, canonical_json([row.__dict__ for row in first_verified])
            )
            bound = tuple(
                SourceInventory(**row)
                for row in json.loads(inventory_path.read_text(encoding="utf-8"))
            )
            if verify_private_snapshot(snapshot_policy, bound) != bound:
                raise PolicyError("snapshot:inventory_mismatch")
            private, public = run_benchmark(snapshot_policy, bound, args.manifest, events)
            if network_attempts:
                raise PolicyError("snapshot:network_attempt")
        public["task"] = "V06-PR-03"
        public["policy_sha256"] = hashlib.sha256(args.policy.read_bytes()).hexdigest()
        public["source_integrity"] = "pass"
        validate_public_packet(public)
        public_bytes = canonical_json(public)
    except PolicyError as exc:
        if private_root.is_dir() and not attempt_path.exists():
            category = (
                f"{exc.checkpoint}:{exc.outcome}"
                if isinstance(exc, CheckpointFailure) else "snapshot:validation_failure"
            )
            _exclusive_write(attempt_path, canonical_json({
                "schema_version": 1, "task": "V06-PR-03", "status": "failed",
                "failure_category": category, "events": events,
            }))
        raise
    _exclusive_write(result_path, canonical_json(private))
    _exclusive_write(public_path, public_bytes)
    _exclusive_write(attempt_path, canonical_json({
        "schema_version": 1, "task": "V06-PR-03", "status": "passed",
        "failure_category": None, "events": events,
    }))
    snapshot_digest = hashlib.sha256(canonical_json([
        {"relpath": row.relpath, "size": row.size, "sha256": row.sha256}
        for row in bound
    ])).hexdigest()
    print(
        f"snapshot_proof=pass source_count={len(bound)} "
        f"snapshot_inventory_sha256={snapshot_digest} "
        f"packet_sha256={hashlib.sha256(public_bytes).hexdigest()}"
    )
    return 0


def snapshot_diagnostic(args: argparse.Namespace) -> int:
    """Retain private measurements for an already-failed, unchanged snapshot."""
    _check_evidence_boundary(args)
    policy = load_policy(args.policy)
    private_root = args.private / "pr03"
    snapshot_root = private_root / "snapshot"
    inventory_path = private_root / "snapshot-inventory.json"
    result_path = private_root / "benchmark-failed-results.json"
    public_path = args.public / "personal-recall-s0s1-snapshot-failed-aggregate.json"
    if not (private_root / "benchmark-attempt-evidence.json").is_file():
        raise PolicyError("snapshot:prior_attempt_missing")
    if result_path.exists() or public_path.exists():
        raise PolicyError("snapshot:diagnostic_exists")
    bound = tuple(
        SourceInventory(**row)
        for row in json.loads(inventory_path.read_text(encoding="utf-8"))
    )
    snapshot_policy = replace(policy, vault_root=snapshot_root)
    if verify_private_snapshot(snapshot_policy, bound) != bound:
        raise PolicyError("snapshot:inventory_mismatch")
    events: list[dict[str, object]] = []
    try:
        run_benchmark(snapshot_policy, bound, args.manifest, events)
    except BenchmarkGateFailure as exc:
        if verify_private_snapshot(snapshot_policy, bound) != bound:
            raise PolicyError("snapshot:inventory_mismatch") from None
        public = dict(exc.public)
        public["task"] = "V06-PR-03"
        public["policy_sha256"] = hashlib.sha256(args.policy.read_bytes()).hexdigest()
        public["source_integrity"] = "pass"
        validate_public_packet(public)
        failed_public = {**public, "status": "failed", "failure_category": str(exc)}
        private = {**exc.private, "failure_category": str(exc)}
        public_bytes = canonical_json(failed_public)
        _exclusive_write(result_path, canonical_json(private))
        _exclusive_write(public_path, public_bytes)
        print(
            f"snapshot_diagnostic={exc} "
            f"packet_sha256={hashlib.sha256(public_bytes).hexdigest()}"
        )
        return 0
    raise PolicyError("snapshot:diagnostic_outcome_changed")


def snapshot_corrected_proof(args: argparse.Namespace) -> int:
    """Run the one authorized corrected proof over the retained PR03 snapshot."""
    _check_evidence_boundary(args)
    policy = load_policy(args.policy)
    private_root = args.private / "pr03"
    public_failed = args.public / "personal-recall-s0s1-snapshot-failed-aggregate.json"
    private_result = private_root / "corrected-benchmark-results.json"
    attempt_path = private_root / "corrected-benchmark-attempt-evidence.json"
    public_result = args.public / "personal-recall-s0s1-snapshot-corrected-aggregate.json"
    if (any(path.exists() for path in (private_result, attempt_path, public_result))
            or not public_failed.is_file()):
        raise PolicyError("snapshot:corrected_result_boundary")
    for name, expected in _PR03_FROZEN.items():
        path = private_root / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise PolicyError("snapshot:historical_evidence_drift")
    if (hashlib.sha256(public_failed.read_bytes()).hexdigest() != _PR03_FAILED_PUBLIC_SHA256
            or hashlib.sha256(args.manifest.read_bytes()).hexdigest() != _PR03_MANIFEST_SHA256):
        raise PolicyError("snapshot:historical_evidence_drift")
    inventory = tuple(
        SourceInventory(**row)
        for row in json.loads((private_root / "snapshot-inventory.json").read_text(
            encoding="utf-8"
        ))
    )
    snapshot_policy = replace(policy, vault_root=private_root / "snapshot")
    if verify_private_snapshot(snapshot_policy, inventory) != inventory:
        raise PolicyError("snapshot:inventory_mismatch")
    events: list[dict[str, object]] = []
    try:
        private, public = run_benchmark(snapshot_policy, inventory, args.manifest, events)
        if verify_private_snapshot(snapshot_policy, inventory) != inventory:
            raise PolicyError("snapshot:inventory_mismatch")
        public["task"] = "V06-PR-03"
        public["policy_sha256"] = hashlib.sha256(args.policy.read_bytes()).hexdigest()
        public["source_integrity"] = "pass"
        validate_public_packet(public)
        public_bytes = canonical_json(public)
    except PolicyError as exc:
        category = str(exc)
        if category not in {
            "benchmark:negative_control", "benchmark:exact_recall_gate",
            "benchmark:project_recall_gate", "benchmark:performance_gate",
            "snapshot:inventory_mismatch", "privacy:public_schema",
            "privacy:public_value", "privacy:public_digest", "privacy:public_counts",
            "privacy:public_count", "privacy:public_timing",
        }:
            category = "snapshot:corrected_validation_failure"
        _exclusive_write(attempt_path, canonical_json({
            "schema_version": 1, "task": "V06-PR-03", "status": "failed",
            "failure_category": category, "events": events,
        }))
        raise
    _exclusive_write(private_result, canonical_json(private))
    _exclusive_write(public_result, public_bytes)
    _exclusive_write(attempt_path, canonical_json({
        "schema_version": 1, "task": "V06-PR-03", "status": "passed",
        "failure_category": None, "events": events,
    }))
    print(f"snapshot_corrected_proof=pass packet_sha256={hashlib.sha256(public_bytes).hexdigest()}")
    return 0


def snapshot(args: argparse.Namespace) -> int:
    """Capture one authorized read-only inventory and bind the second only if identical."""
    _check_evidence_boundary(args)
    policy = load_policy(args.policy)
    records = [source.__dict__ for source in inventory_sources(policy)]
    paths = [str(record["relpath"]) for record in records]
    mojibake = "".join(map(chr, (0xE2, 0x20AC, 0x201D)))
    if sum(chr(0x2014) in path for path in paths) != 1 or any(
        mojibake in path or chr(0xFFFD) in path for path in paths
    ):
        raise RuntimeError("unicode_identity_failure")
    payload = canonical_json(records)
    target = args.private / f"inventory-snapshot-{args.sequence}.json"
    if args.sequence == 2:
        first = (args.private / "inventory-snapshot-1.json").read_bytes()
        if payload != first:
            raise RuntimeError("source_integrity_failure")
        historical = (args.private / "baseline-inventory.json").read_bytes()
        _exclusive_write(target, payload)
        _exclusive_write(args.private / "baseline-inventory-v2.json", payload)
        binding = {
            "schema_version": 1,
            "task": "V06-PR-01",
            "disposition": "matching_read_only_snapshots",
            "first_sha256": hashlib.sha256(first).hexdigest(),
            "second_sha256": hashlib.sha256(payload).hexdigest(),
            "historical_baseline_sha256": hashlib.sha256(historical).hexdigest(),
            "historical_baseline_has_em_dash": any(
                chr(0x2014) in str(row["relpath"])
                for row in json.loads(historical)
            ),
            "source_count": len(records),
        }
        _exclusive_write(args.private / "baseline-binding-v2.json", canonical_json(binding))
    else:
        _exclusive_write(target, payload)
    print(f"snapshot_{args.sequence}=pass count={len(records)}")
    return 0


def template(args: argparse.Namespace) -> int:
    """Create a private, fillable 24-question manifest without vault content."""
    categories = (
        ["exact"] * 6 + ["metadata"] * 4 + ["project"] * 4
        + ["relationship"] * 4 + ["paraphrase"] * 3
        + ["negative"] * 2 + ["missing"]
    )
    payload = {
        "schema_version": 1,
        "benchmark_id": uuid.uuid4().hex,
        "questions": [
            {
                "benchmark_question_id": uuid.uuid4().hex,
                "category": category,
                "question": "",
                "expected_relpaths": [],
                "acceptable_alternates": [],
                "reason": "",
                "max_sensitivity": "private",
            }
            for category in categories
        ],
    }
    _exclusive_write(args.private / "benchmark-manifest.json", canonical_json(payload))
    print("private_template_created=true")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for name in (
        "preflight", "benchmark", "template", "snapshot", "snapshot-proof",
        "snapshot-diagnostic", "snapshot-corrected-proof",
    ):
        cmd = sub.add_parser(name)
        cmd.add_argument("--private", type=Path, required=True)
        if name == "template":
            continue
        cmd.add_argument("--repo", type=Path, required=True)
        cmd.add_argument("--policy", type=Path, required=True)
        cmd.add_argument("--public", type=Path, required=True)
        if name == "preflight":
            cmd.add_argument("--commit", required=True)
            cmd.add_argument("--tree", required=True)
            cmd.add_argument("--revision", choices=("initial", "v2"), default="initial")
        elif name == "snapshot":
            cmd.add_argument("--sequence", type=int, choices=(1, 2), required=True)
        else:
            cmd.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "preflight":
        return preflight(args)
    if args.command == "template":
        return template(args)
    if args.command == "snapshot":
        return snapshot(args)
    if args.command == "snapshot-proof":
        return snapshot_proof(args)
    if args.command == "snapshot-diagnostic":
        return snapshot_diagnostic(args)
    if args.command == "snapshot-corrected-proof":
        return snapshot_corrected_proof(args)
    return benchmark(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PolicyError as exc:
        category = str(exc)
        if not category or any(char not in "abcdefghijklmnopqrstuvwxyz_:" for char in category):
            category = "policy_failure"
        print(f"recall_failure={category}", file=sys.stderr)
        raise SystemExit(2) from None
    except Exception:
        print("recall_failure=unexpected_failure", file=sys.stderr)
        raise SystemExit(3) from None
