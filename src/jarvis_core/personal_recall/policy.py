"""Closed-schema external path policy for Personal Recall."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from jarvis_core.policy.errors import PolicyError
from jarvis_core.policy.sensitivity import KNOWN_SENSITIVITIES, ceiling_rank

_TOP_KEYS = {
    "schema_version", "policy_id", "policy_version", "workspace_id", "vault_root",
    "max_sensitivity", "rules",
}
_RULE_KEYS = {"pattern", "sensitivity"}
_APPROVED_PATTERNS = (
    "00 Inbox/**/*.md",
    "01 Daily Notes/**/*.md",
    "02 Projects/**/*.md",
    "03 Areas/**/*.md",
    "04 Wiki (Resources)/**/*.md",
)


@dataclass(frozen=True)
class PolicyRule:
    pattern: str
    sensitivity: str


@dataclass(frozen=True)
class RecallPolicy:
    schema_version: int
    policy_id: str
    policy_version: str
    workspace_id: str
    vault_root: Path
    max_sensitivity: str
    rules: tuple[PolicyRule, ...]

    def classify(self, relpath: str) -> str | None:
        """Return one deterministic label or fail closed on zero/conflicting matches."""
        normalized = relpath.replace("\\", "/").lstrip("/")
        if ".." in PurePosixPath(normalized).parts:
            return None
        matches = {
            r.sensitivity
            for r in self.rules
            if normalized.casefold().startswith(
                (r.pattern.split("/", 1)[0] + "/").casefold()
            )
            and normalized.casefold().endswith(".md")
        }
        return next(iter(matches)) if len(matches) == 1 else None

    @property
    def include_roots(self) -> tuple[str, ...]:
        return tuple(rule.pattern.split("/", 1)[0] for rule in self.rules)


def _required_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PolicyError(f"invalid_policy:{field}")
    return value.strip()


def load_policy(path: Path) -> RecallPolicy:
    """Load an exact, versioned policy. Any ambiguity is a fixed-category failure."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PolicyError("invalid_policy:unreadable") from exc
    if not isinstance(raw, dict) or set(raw) != _TOP_KEYS or raw.get("schema_version") != 1:
        raise PolicyError("invalid_policy:schema")
    rules_raw = raw.get("rules")
    if not isinstance(rules_raw, list) or len(rules_raw) != len(_APPROVED_PATTERNS):
        raise PolicyError("invalid_policy:rules")
    rules: list[PolicyRule] = []
    for item in rules_raw:
        if not isinstance(item, dict) or set(item) != _RULE_KEYS:
            raise PolicyError("invalid_policy:rule_schema")
        pattern = _required_text(item.get("pattern"), "pattern")
        label = _required_text(item.get("sensitivity"), "sensitivity").lower()
        if pattern not in _APPROVED_PATTERNS or label not in KNOWN_SENSITIVITIES:
            raise PolicyError("invalid_policy:rule_value")
        rules.append(PolicyRule(pattern, label))
    if tuple(r.pattern for r in rules) != _APPROVED_PATTERNS:
        raise PolicyError("invalid_policy:rule_order")
    ceiling = _required_text(raw.get("max_sensitivity"), "max_sensitivity").lower()
    ceiling_rank(ceiling)
    if ceiling != "private":
        raise PolicyError("invalid_policy:ceiling")
    root = Path(_required_text(raw.get("vault_root"), "vault_root"))
    if not root.is_absolute():
        raise PolicyError("invalid_policy:root")
    return RecallPolicy(
        1,
        _required_text(raw.get("policy_id"), "policy_id"),
        _required_text(raw.get("policy_version"), "policy_version"),
        _required_text(raw.get("workspace_id"), "workspace_id"),
        root,
        ceiling,
        tuple(rules),
    )
