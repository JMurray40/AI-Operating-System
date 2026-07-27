"""Validation result models mirroring VAULT_SCHEMA.md validation stages."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    """Issue severity. ``ERROR`` is fatal; ``WARNING`` is non-fatal."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class Stage(str, Enum):
    """The five validation stages defined in VAULT_SCHEMA.md."""

    SYNTAX = "syntax"
    SHAPE = "shape"
    VOCABULARY = "vocabulary"
    INTEGRITY = "integrity"
    POLICY = "policy"


@dataclass(frozen=True, order=True)
class ValidationIssue:
    """A single validation finding. Ordered for deterministic output."""

    stage: Stage
    severity: Severity
    location: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "stage": self.stage.value,
            "severity": self.severity.value,
            "location": self.location,
            "message": self.message,
        }


@dataclass(frozen=True)
class ValidationResult:
    """The outcome of validating notes or a context package."""

    issues: tuple[ValidationIssue, ...] = ()

    @property
    def errors(self) -> tuple[ValidationIssue, ...]:
        return tuple(i for i in self.issues if i.severity is Severity.ERROR)

    @property
    def warnings(self) -> tuple[ValidationIssue, ...]:
        return tuple(i for i in self.issues if i.severity is Severity.WARNING)

    @property
    def ok(self) -> bool:
        """True when there are no errors (warnings are tolerated)."""
        return not self.errors

    def sorted(self) -> ValidationResult:
        """Return a copy with issues in deterministic order."""
        return ValidationResult(tuple(sorted(self.issues)))

    def to_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "issues": [i.to_dict() for i in sorted(self.issues)],
        }
