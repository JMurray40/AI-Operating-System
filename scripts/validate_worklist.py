"""Validate a version worklist using only the Python standard library."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

STATUSES = {
    "proposed",
    "blocked",
    "authorized",
    "in_progress",
    "ready_for_review",
    "returned_for_correction",
    "accepted",
    "superseded",
    "cancelled",
}
ACTIVE = {"authorized", "in_progress", "ready_for_review"}
TASK_ID = re.compile(r"^[A-Z][A-Z0-9]*-[A-Z][A-Z0-9]*-[0-9]{2}$")
SHA = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_TOP = {
    "schema_version",
    "worklist_id",
    "project",
    "milestone",
    "repository_root",
    "owner_role",
    "updated_at",
    "current_focus_ids",
    "tasks",
}
READINESS_STATUSES = {"draft", "ready", "waived"}
EXECUTION_KINDS = {"discovery", "execution", "review", "decision", "closeout"}
REQUIRED_TASK = {
    "id",
    "title",
    "workstream",
    "priority",
    "owner_role",
    "reviewer_role",
    "status",
    "authorization",
    "depends_on",
    "blocked_by",
    "concurrency_group",
    "allow_parallel_in_group",
    "inputs",
    "outputs",
    "scope",
    "exclusions",
    "acceptance_criteria",
    "required_evidence",
    "stop_conditions",
    "history",
}
ALLOWED_TRANSITIONS = {
    "proposed": {"blocked", "authorized", "cancelled", "superseded"},
    "blocked": {"authorized", "cancelled", "superseded"},
    "authorized": {"in_progress", "blocked", "cancelled", "superseded"},
    "in_progress": {"ready_for_review", "blocked", "cancelled"},
    "ready_for_review": {"accepted", "returned_for_correction", "blocked"},
    "returned_for_correction": {"authorized", "in_progress", "cancelled", "superseded"},
    "accepted": {"superseded"},
    "superseded": set(),
    "cancelled": set(),
}


class Problems:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def load_json(path: Path, problems: Problems) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        problems.error(f"cannot read valid UTF-8 JSON: {exc}")
        return {}
    if not isinstance(data, dict):
        problems.error("top level must be an object")
        return {}
    return data


def nonempty_strings(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, str) and item.strip() for item in value)
    )


def is_placeholder(value: str) -> bool:
    return value.startswith("<") and value.endswith(">")


def validate_history(task: dict[str, Any], problems: Problems) -> None:
    task_id = task.get("id", "<unknown>")
    history = task.get("history")
    if not isinstance(history, list) or not history:
        problems.error(f"{task_id}: history must be a non-empty array")
        return
    prior_to: str | None = None
    for index, entry in enumerate(history):
        if not isinstance(entry, dict):
            problems.error(f"{task_id}: history[{index}] must be an object")
            continue
        required = {"at", "actor_role", "from_status", "to_status", "reason", "artifact"}
        missing = required - set(entry)
        if missing:
            problems.error(f"{task_id}: history[{index}] missing {sorted(missing)}")
            continue
        source = entry["from_status"]
        target = entry["to_status"]
        actor = entry["actor_role"]
        if target not in STATUSES:
            problems.error(f"{task_id}: history[{index}] has invalid to_status {target!r}")
            continue
        if index and source != prior_to:
            problems.error(
                f"{task_id}: history[{index}] from_status {source!r} "
                f"does not match prior {prior_to!r}"
            )
        if source in STATUSES and target not in ALLOWED_TRANSITIONS[source]:
            problems.error(f"{task_id}: invalid transition {source} -> {target}")
        if target in {"authorized", "superseded", "cancelled"} and actor != "chief_of_staff":
            problems.error(f"{task_id}: only chief_of_staff may set {target}")
        if target in {"in_progress", "ready_for_review"} and actor != task.get("owner_role"):
            problems.error(f"{task_id}: only owner_role may set {target}")
        if target in {"accepted", "returned_for_correction"} and actor not in {
            task.get("reviewer_role"),
            "chief_of_staff",
        }:
            problems.error(f"{task_id}: only reviewer_role or chief_of_staff may set {target}")
        prior_to = target
    if prior_to != task.get("status"):
        problems.error(f"{task_id}: final history status {prior_to!r} != task status")


def validate_paths(task: dict[str, Any], root: Path, problems: Problems) -> None:
    candidates: list[tuple[str, str]] = []
    artifact = task.get("authorization", {}).get("artifact")
    if isinstance(artifact, str):
        candidates.append(("authorization.artifact", artifact))
    candidates.extend(
        (f"inputs[{index}]", value)
        for index, value in enumerate(task.get("inputs", []))
        if isinstance(value, str)
    )
    for label, value in candidates:
        if is_placeholder(value):
            if task["status"] in ACTIVE:
                problems.error(f"{task['id']}: active task has placeholder {label}: {value}")
            continue
        relative = Path(value)
        if relative.is_absolute():
            problems.error(f"{task['id']}: {label} must be repository-relative: {value}")
        elif not (root / relative).exists() and task["status"] in ACTIVE | {"accepted"}:
            problems.error(f"{task['id']}: {label} does not exist: {value}")


def detect_cycles(tasks: dict[str, dict[str, Any]], problems: Problems) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str, chain: list[str]) -> None:
        if task_id in visiting:
            problems.error(f"dependency cycle: {' -> '.join([*chain, task_id])}")
            return
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in tasks[task_id].get("depends_on", []):
            if dependency in tasks:
                visit(dependency, [*chain, task_id])
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in tasks:
        visit(task_id, [])


def validate(path: Path) -> Problems:
    problems = Problems()
    data = load_json(path, problems)
    if not data:
        return problems
    missing_top = REQUIRED_TOP - set(data)
    if missing_top:
        problems.error(f"top level missing {sorted(missing_top)}")
    schema_version = data.get("schema_version")
    if schema_version not in {"1.0", "1.1", "1.2"}:
        problems.error("schema_version must be '1.0', '1.1', or '1.2'")
    if data.get("owner_role") != "chief_of_staff":
        problems.error("owner_role must be chief_of_staff")
    root_value = data.get("repository_root", ".")
    root = (Path.cwd() / root_value).resolve() if isinstance(root_value, str) else Path.cwd()
    raw_tasks = data.get("tasks")
    if not isinstance(raw_tasks, list) or not raw_tasks:
        problems.error("tasks must be a non-empty array")
        return problems

    if schema_version in {"1.1", "1.2"}:
        readiness = data.get("readiness")
        required_readiness = {
            "status",
            "artifact",
            "required_capabilities",
            "required_software",
            "required_privileges",
            "human_actions",
            "environments",
            "preflight_checks",
            "fallback_routes",
            "unresolved",
        }
        if not isinstance(readiness, dict) or not required_readiness <= set(readiness):
            problems.error("schema 1.1 requires a complete readiness object")
        else:
            if readiness["status"] not in READINESS_STATUSES:
                problems.error("readiness.status must be draft, ready, or waived")
            for field in required_readiness - {"status", "artifact", "unresolved"}:
                if not nonempty_strings(readiness[field]):
                    problems.error(f"readiness.{field} must contain non-empty strings")
            if not isinstance(readiness["unresolved"], list) or not all(
                isinstance(item, str) and item.strip() for item in readiness["unresolved"]
            ):
                problems.error("readiness.unresolved must be an array of non-empty strings")
            artifact = readiness["artifact"]
            if not isinstance(artifact, str) or not artifact.strip():
                problems.error("readiness.artifact must be a non-empty path")
            elif not is_placeholder(artifact) and not (root / artifact).exists():
                problems.error(f"readiness.artifact does not exist: {artifact}")
            if readiness.get("status") == "ready" and readiness.get("unresolved"):
                problems.error("readiness cannot be ready while unresolved items remain")

        envelopes = data.get("authorization_envelopes")
        if not isinstance(envelopes, list) or not envelopes:
            problems.error("schema 1.1 requires authorization_envelopes")
        else:
            envelope_ids: set[str] = set()
            for index, envelope in enumerate(envelopes):
                required_envelope = {
                    "id",
                    "decision_id",
                    "artifact",
                    "covered_task_ids",
                    "activation_rule",
                    "max_retries",
                }
                if not isinstance(envelope, dict) or not required_envelope <= set(envelope):
                    problems.error(f"authorization_envelopes[{index}] is incomplete")
                    continue
                envelope_id = envelope["id"]
                if not isinstance(envelope_id, str) or not envelope_id.strip():
                    problems.error(f"authorization_envelopes[{index}].id must be non-empty")
                elif envelope_id in envelope_ids:
                    problems.error(f"duplicate authorization envelope id: {envelope_id}")
                else:
                    envelope_ids.add(envelope_id)
                if not nonempty_strings(envelope["covered_task_ids"]):
                    problems.error(
                        f"authorization_envelopes[{index}].covered_task_ids must be non-empty"
                    )
                if not isinstance(envelope["max_retries"], int) or envelope["max_retries"] < 0:
                    problems.error(
                        f"authorization_envelopes[{index}].max_retries must be non-negative"
                    )
                for field in ("decision_id", "artifact", "activation_rule"):
                    if not isinstance(envelope[field], str) or not envelope[field].strip():
                        problems.error(
                            f"authorization_envelopes[{index}].{field} must be non-empty"
                        )
                artifact = envelope.get("artifact")
                if (
                    isinstance(artifact, str)
                    and not is_placeholder(artifact)
                    and not (root / artifact).exists()
                ):
                    problems.error(
                        f"authorization_envelopes[{index}].artifact does not exist: {artifact}"
                    )

    delivery_policy: dict[str, Any] = {}
    policy_effective_at: datetime | None = None
    if schema_version == "1.2":
        raw_policy = data.get("delivery_policy")
        required_policy = {
            "effective_at",
            "mode",
            "outcome_sized_tasks",
            "same_task_in_scope_corrections",
            "consolidated_reviewer_punchlist",
            "documentation_counts_only_when_deliverable",
            "explicit_human_action_routing",
            "max_correction_rounds_before_root_cause_review",
            "allowed_early_stop_classes",
        }
        if not isinstance(raw_policy, dict) or not required_policy <= set(raw_policy):
            problems.error("schema 1.2 requires a complete delivery_policy object")
        else:
            delivery_policy = raw_policy
            if raw_policy["mode"] not in {
                "prototype_momentum",
                "release_certification",
                "general",
            }:
                problems.error("delivery_policy.mode is invalid")
            for field in (
                "outcome_sized_tasks",
                "same_task_in_scope_corrections",
                "consolidated_reviewer_punchlist",
                "documentation_counts_only_when_deliverable",
                "explicit_human_action_routing",
            ):
                if raw_policy[field] is not True:
                    problems.error(f"delivery_policy.{field} must be true")
            limit = raw_policy["max_correction_rounds_before_root_cause_review"]
            if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
                problems.error(
                    "delivery_policy.max_correction_rounds_before_root_cause_review "
                    "must be a positive integer"
                )
            expected_stops = {
                "human_action",
                "missing_authority",
                "unsafe_or_irreversible",
                "external_capability",
                "scope_change_required",
            }
            stop_classes = raw_policy["allowed_early_stop_classes"]
            if not isinstance(stop_classes, list) or set(stop_classes) != expected_stops:
                problems.error(
                    "delivery_policy.allowed_early_stop_classes must contain the five "
                    "canonical classes exactly"
                )
            try:
                policy_effective_at = datetime.fromisoformat(
                    raw_policy["effective_at"].replace("Z", "+00:00")
                )
            except (AttributeError, ValueError):
                problems.error("delivery_policy.effective_at must be an ISO date-time")

    tasks: dict[str, dict[str, Any]] = {}
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for index, task in enumerate(raw_tasks):
        if not isinstance(task, dict):
            problems.error(f"tasks[{index}] must be an object")
            continue
        missing = REQUIRED_TASK - set(task)
        task_id = task.get("id", f"tasks[{index}]")
        if missing:
            problems.error(f"{task_id}: missing {sorted(missing)}")
            continue
        if not isinstance(task_id, str) or not TASK_ID.fullmatch(task_id):
            problems.error(f"tasks[{index}]: invalid task id {task_id!r}")
            continue
        if task_id in tasks:
            problems.error(f"duplicate task id: {task_id}")
            continue
        tasks[task_id] = task
        groups[task["concurrency_group"]].append(task)
        status = task["status"]
        if status not in STATUSES:
            problems.error(f"{task_id}: invalid status {status!r}")
        if task["priority"] not in {"P0", "P1", "P2", "P3"}:
            problems.error(f"{task_id}: invalid priority")
        for field in (
            "inputs",
            "outputs",
            "scope",
            "exclusions",
            "acceptance_criteria",
            "required_evidence",
            "stop_conditions",
        ):
            if not nonempty_strings(task[field]):
                problems.error(f"{task_id}: {field} must contain non-empty strings")
        if not isinstance(task["depends_on"], list) or len(task["depends_on"]) != len(
            set(task["depends_on"])
        ):
            problems.error(f"{task_id}: depends_on must be a unique array")
        if status == "blocked" and not task["blocked_by"]:
            problems.error(f"{task_id}: blocked task requires blocked_by")
        if status != "blocked" and task["blocked_by"]:
            problems.warn(f"{task_id}: non-blocked task still lists blockers")
        auth = task["authorization"]
        if not isinstance(auth, dict) or not {"state", "decision_id", "artifact"} <= set(auth):
            problems.error(f"{task_id}: malformed authorization")
        elif status in ACTIVE | {"accepted"}:
            if auth["state"] not in {"approved", "not_required"}:
                problems.error(f"{task_id}: {status} requires approved/not_required authorization")
            if auth["state"] == "approved" and not auth["artifact"]:
                problems.error(f"{task_id}: approved authorization requires artifact")
        state = task.get("repository_state")
        if isinstance(state, dict):
            for field in ("executable_commit", "tree", "evidence_head"):
                value = state.get(field)
                if value is not None and (not isinstance(value, str) or not SHA.fullmatch(value)):
                    problems.error(
                        f"{task_id}: repository_state.{field} must be a full lowercase SHA"
                    )
        if schema_version in {"1.1", "1.2"}:
            execution = task.get("execution")
            required_execution = {
                "wave_id",
                "kind",
                "environment",
                "required_capabilities",
                "required_software",
                "required_privileges",
                "human_actions",
                "preflight_checks",
                "activation_condition",
                "pass_route",
                "fail_route",
                "retry_policy",
                "estimated_duration",
            }
            if not isinstance(execution, dict) or not required_execution <= set(execution):
                problems.error(f"{task_id}: schema 1.1 requires a complete execution object")
            else:
                if execution["kind"] not in EXECUTION_KINDS:
                    problems.error(f"{task_id}: invalid execution.kind")
                for field in (
                    "required_capabilities",
                    "required_software",
                    "required_privileges",
                    "human_actions",
                    "preflight_checks",
                ):
                    if not nonempty_strings(execution[field]):
                        problems.error(f"{task_id}: execution.{field} must be non-empty")
                for field in (
                    "wave_id",
                    "environment",
                    "activation_condition",
                    "pass_route",
                    "fail_route",
                    "retry_policy",
                    "estimated_duration",
                ):
                    if not isinstance(execution[field], str) or not execution[field].strip():
                        problems.error(f"{task_id}: execution.{field} must be non-empty")
                readiness = data.get("readiness", {})
                if (
                    status in ACTIVE
                    and execution.get("kind") == "execution"
                    and readiness.get("status") != "ready"
                ):
                    problems.error(
                        f"{task_id}: active execution requires readiness.status ready"
                    )
        validate_history(task, problems)
        if schema_version == "1.2" and policy_effective_at is not None:
            post_policy_returns = []
            root_cause_reviews = []
            for entry in task.get("history", []):
                try:
                    entry_at = datetime.fromisoformat(entry["at"].replace("Z", "+00:00"))
                except (KeyError, AttributeError, ValueError):
                    continue
                if entry_at < policy_effective_at:
                    continue
                reason = str(entry.get("reason", "")).lower()
                if entry.get("to_status") == "returned_for_correction":
                    post_policy_returns.append(entry)
                if "root-cause" in reason or "process review" in reason:
                    root_cause_reviews.append(entry)
            limit = delivery_policy.get("max_correction_rounds_before_root_cause_review", 1)
            if len(post_policy_returns) > limit and not root_cause_reviews:
                problems.error(
                    f"{task_id}: correction-round limit exceeded after delivery-policy "
                    "effective date without a root-cause/process review"
                )
        validate_paths(task, root, problems)

    for task_id, task in tasks.items():
        for dependency in task["depends_on"]:
            if dependency == task_id:
                problems.error(f"{task_id}: task cannot depend on itself")
            elif dependency not in tasks:
                problems.error(f"{task_id}: missing dependency {dependency}")
        if task["status"] in ACTIVE:
            incomplete = [
                dependency
                for dependency in task["depends_on"]
                if dependency in tasks and tasks[dependency]["status"] != "accepted"
            ]
            if incomplete:
                problems.error(f"{task_id}: active with unaccepted dependencies {incomplete}")

    if schema_version in {"1.1", "1.2"} and isinstance(
        data.get("authorization_envelopes"), list
    ):
        for index, envelope in enumerate(data["authorization_envelopes"]):
            if not isinstance(envelope, dict):
                continue
            for covered_id in envelope.get("covered_task_ids", []):
                if covered_id not in tasks:
                    problems.error(
                        f"authorization_envelopes[{index}] covers missing task {covered_id}"
                    )

    focus = data.get("current_focus_ids")
    if not isinstance(focus, list) or len(focus) != len(set(focus)):
        problems.error("current_focus_ids must be a unique array")
    else:
        for task_id in focus:
            if task_id not in tasks:
                problems.error(f"current_focus_ids contains missing task {task_id}")
            elif tasks[task_id]["status"] not in ACTIVE:
                problems.error(f"current focus {task_id} is not active")
        unlisted = sorted(
            task_id
            for task_id, task in tasks.items()
            if task["status"] in ACTIVE and task_id not in focus
        )
        if unlisted:
            problems.error(f"active tasks missing from current_focus_ids: {unlisted}")

    for group, members in groups.items():
        active = [task for task in members if task["status"] in ACTIVE]
        if len(active) > 1 and not all(task["allow_parallel_in_group"] for task in active):
            active_ids = [task["id"] for task in active]
            problems.error(f"concurrency group {group!r} has multiple active tasks: {active_ids}")
    detect_cycles(tasks, problems)
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("worklists", nargs="+", type=Path)
    args = parser.parse_args()
    failed = False
    for path in args.worklists:
        problems = validate(path)
        for warning in problems.warnings:
            print(f"WARNING {path}: {warning}")
        for error in problems.errors:
            print(f"ERROR {path}: {error}")
        if problems.errors:
            failed = True
        else:
            print(f"OK {path}: valid worklist")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
