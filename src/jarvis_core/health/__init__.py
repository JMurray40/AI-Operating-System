"""Vault health analysis (read-only)."""
from __future__ import annotations

from jarvis_core.health.analyzer import (
    analyze_vault,
    compute_vault_fingerprint,
    is_obsidian_vault,
)
from jarvis_core.health.models import (
    CATEGORY_LABEL,
    CATEGORY_RECOMMENDATION,
    HealthCategory,
    HealthFinding,
    VaultHealthReport,
)
from jarvis_core.health.render import render_text

__all__ = [
    "CATEGORY_LABEL",
    "CATEGORY_RECOMMENDATION",
    "HealthCategory",
    "HealthFinding",
    "VaultHealthReport",
    "analyze_vault",
    "compute_vault_fingerprint",
    "is_obsidian_vault",
    "render_text",
]
