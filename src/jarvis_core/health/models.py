"""Vault health report models."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from jarvis_core import __version__
from jarvis_core.models.validation import Severity

#: Version of the health-report JSON envelope. Bump on any breaking format change.
REPORT_SCHEMA_VERSION = "1.0"


class HealthCategory(str, Enum):
    """The vault health checks required by Phase 2."""

    MISSING_FRONTMATTER = "missing_frontmatter"
    DUPLICATE_ID = "duplicate_id"
    ORPHAN_NOTE = "orphan_note"
    BROKEN_WIKILINK = "broken_wikilink"
    INVALID_SCHEMA = "invalid_schema"
    MISSING_ALIAS = "missing_alias"
    CIRCULAR_REFERENCE = "circular_reference"


# Human-facing labels and remediation guidance per category.
CATEGORY_LABEL: dict[HealthCategory, str] = {
    HealthCategory.MISSING_FRONTMATTER: "Missing frontmatter",
    HealthCategory.DUPLICATE_ID: "Duplicate IDs",
    HealthCategory.ORPHAN_NOTE: "Orphan notes",
    HealthCategory.BROKEN_WIKILINK: "Broken wikilinks",
    HealthCategory.INVALID_SCHEMA: "Invalid schemas",
    HealthCategory.MISSING_ALIAS: "Missing aliases",
    HealthCategory.CIRCULAR_REFERENCE: "Circular references",
}

CATEGORY_RECOMMENDATION: dict[HealthCategory, str] = {
    HealthCategory.MISSING_FRONTMATTER:
        "Add YAML frontmatter with the common contract (id, type, title, status, "
        "created, updated, sensitivity) to durable notes.",
    HealthCategory.DUPLICATE_ID:
        "Give each note a unique, stable id; never reuse an id across notes.",
    HealthCategory.ORPHAN_NOTE:
        "Link orphan notes from a dashboard or related note, or archive them if obsolete.",
    HealthCategory.BROKEN_WIKILINK:
        "Fix the link target or add the missing note; add an alias if the target was renamed.",
    HealthCategory.INVALID_SCHEMA:
        "Correct frontmatter to match VAULT_SCHEMA.md (required fields, controlled "
        "vocabularies, ISO dates, id pattern).",
    HealthCategory.MISSING_ALIAS:
        "Add an alias covering the filename when it differs from the title, so links "
        "by either name resolve.",
    HealthCategory.CIRCULAR_REFERENCE:
        "Reciprocal links are normal in Obsidian; review only if a cycle implies a "
        "modelling problem (e.g. a note that should be a parent of another).",
}


@dataclass(frozen=True, order=True)
class HealthFinding:
    """A single health finding. Ordered for deterministic output."""

    category: HealthCategory
    severity: Severity
    location: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "category": self.category.value,
            "severity": self.severity.value,
            "location": self.location,
            "message": self.message,
        }


@dataclass(frozen=True)
class VaultHealthReport:
    """Aggregated vault health. Deterministic given the same inputs."""

    vault_path: str
    note_count: int
    is_obsidian_vault: bool
    findings: tuple[HealthFinding, ...] = ()
    perf: dict[str, object] | None = None
    # --- report envelope (metadata for downstream tooling) ---
    schema_version: str = REPORT_SCHEMA_VERSION
    generated_by: str = f"Jarvis {__version__}"
    generated_at: str | None = None   # ISO-8601; None keeps output deterministic
    vault_version: str | None = None  # content fingerprint of the scanned vault

    @property
    def errors(self) -> tuple[HealthFinding, ...]:
        return tuple(f for f in self.findings if f.severity is Severity.ERROR)

    @property
    def warnings(self) -> tuple[HealthFinding, ...]:
        return tuple(f for f in self.findings if f.severity is Severity.WARNING)

    @property
    def infos(self) -> tuple[HealthFinding, ...]:
        return tuple(f for f in self.findings if f.severity is Severity.INFO)

    @property
    def ok(self) -> bool:
        """True when there are no error-severity findings."""
        return not self.errors

    def counts_by_category(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for f in self.findings:
            out[f.category.value] = out.get(f.category.value, 0) + 1
        return dict(sorted(out.items()))

    def recommendations(self) -> tuple[str, ...]:
        present = {f.category for f in self.findings}
        # Deterministic order by category declaration.
        return tuple(
            CATEGORY_RECOMMENDATION[cat]
            for cat in HealthCategory
            if cat in present
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schemaVersion": self.schema_version,
            "generatedBy": self.generated_by,
            "timestamp": self.generated_at,
            "vaultVersion": self.vault_version,
            "vault_path": self.vault_path,
            "note_count": self.note_count,
            "is_obsidian_vault": self.is_obsidian_vault,
            "ok": self.ok,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "info_count": len(self.infos),
            "counts_by_category": self.counts_by_category(),
            "findings": [f.to_dict() for f in sorted(self.findings)],
            "recommendations": list(self.recommendations()),
            "performance": self.perf,
        }
