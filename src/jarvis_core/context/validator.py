"""Note and context validation across the five VAULT_SCHEMA.md stages.

Stages: Syntax, Shape, Vocabulary, Integrity, Policy. Findings are returned as a
:class:`ValidationResult`; nothing is modified.
"""
from __future__ import annotations

import re

from jarvis_core.models.base import (
    COMMON_REQUIRED_FIELDS,
    REGISTERED_SENSITIVITIES,
    REGISTERED_STATUSES,
    REGISTERED_TYPES,
    TYPE_REQUIRED_FIELDS,
)
from jarvis_core.models.note import Note
from jarvis_core.models.validation import (
    Severity,
    Stage,
    ValidationIssue,
    ValidationResult,
)
from jarvis_core.relationships.resolver import RelationshipResolver

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# Conservative secret detectors for the Policy stage.
_SECRET_RES = (
    re.compile(r"\b(?:sk|pk)-[A-Za-z0-9]{16,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"(?i)\b(api[_-]?key|secret|password|token)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{12,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
)


def validate_notes(notes: list[Note]) -> ValidationResult:
    """Validate a collection of notes across all five stages."""
    issues: list[ValidationIssue] = []
    seen_ids: dict[str, str] = {}

    for note in notes:
        loc = note.relpath
        fm = note.frontmatter

        # --- Stage 1: Syntax ---
        for err in note.parse_errors:
            issues.append(ValidationIssue(Stage.SYNTAX, Severity.ERROR, loc, err))

        if not note.has_frontmatter:
            # Missing frontmatter is a shape warning, not a syntax crash.
            issues.append(
                ValidationIssue(
                    Stage.SHAPE, Severity.WARNING, loc, "Note has no YAML frontmatter."
                )
            )
        else:
            # --- Stage 2: Shape (common + type-specific required fields) ---
            for req in COMMON_REQUIRED_FIELDS:
                if req not in fm or _is_empty(fm.get(req)):
                    issues.append(
                        ValidationIssue(
                            Stage.SHAPE, Severity.ERROR, loc,
                            f"Missing required field '{req}'.",
                        )
                    )
            raw_type = note.raw_type
            for req in TYPE_REQUIRED_FIELDS.get(raw_type or "", ()):
                if req not in fm or _is_empty(fm.get(req)):
                    issues.append(
                        ValidationIssue(
                            Stage.SHAPE, Severity.ERROR, loc,
                            f"Type '{raw_type}' requires field '{req}'.",
                        )
                    )

            # --- Stage 3: Vocabulary ---
            if raw_type is not None and raw_type not in REGISTERED_TYPES:
                issues.append(
                    ValidationIssue(
                        Stage.VOCABULARY, Severity.ERROR, loc,
                        f"Unregistered type '{raw_type}'.",
                    )
                )
            status = note.status
            if status is not None and status not in REGISTERED_STATUSES:
                issues.append(
                    ValidationIssue(
                        Stage.VOCABULARY, Severity.ERROR, loc,
                        f"Unregistered status '{status}'.",
                    )
                )
            sens = note.sensitivity
            if sens is not None and sens not in REGISTERED_SENSITIVITIES:
                issues.append(
                    ValidationIssue(
                        Stage.VOCABULARY, Severity.ERROR, loc,
                        f"Unregistered sensitivity '{sens}'.",
                    )
                )

            # --- Stage 4: Integrity (id format, uniqueness, dates) ---
            note_id = note.id
            if note_id is not None:
                if not _ID_RE.match(note_id):
                    issues.append(
                        ValidationIssue(
                            Stage.INTEGRITY, Severity.ERROR, loc,
                            f"Id '{note_id}' does not match pattern ^[a-z0-9][a-z0-9-]*$.",
                        )
                    )
                if note_id in seen_ids:
                    issues.append(
                        ValidationIssue(
                            Stage.INTEGRITY, Severity.ERROR, loc,
                            f"Duplicate id '{note_id}' (also in {seen_ids[note_id]}).",
                        )
                    )
                else:
                    seen_ids[note_id] = loc
            for date_field in ("created", "updated"):
                val = fm.get(date_field)
                if val is not None and not _DATE_RE.match(str(val)):
                    issues.append(
                        ValidationIssue(
                            Stage.INTEGRITY, Severity.WARNING, loc,
                            f"Field '{date_field}'='{val}' is not ISO YYYY-MM-DD.",
                        )
                    )

        # --- Stage 5: Policy (no secrets) ---
        for pattern in _SECRET_RES:
            if pattern.search(note.body):
                issues.append(
                    ValidationIssue(
                        Stage.POLICY, Severity.ERROR, loc,
                        "Possible secret detected in note body (policy: no secrets).",
                    )
                )
                break

    # --- Stage 4 continued: link integrity across the set ---
    resolver = RelationshipResolver(notes)
    report = resolver.resolve_all()
    for unresolved in report.unresolved:
        issues.append(
            ValidationIssue(
                Stage.INTEGRITY, Severity.WARNING, unresolved.source,
                f"Unresolved reference '{unresolved.reference}' ({unresolved.origin}).",
            )
        )

    return ValidationResult(tuple(sorted(issues)))


def _is_empty(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, (list, tuple, dict)):
        return len(value) == 0
    return False
