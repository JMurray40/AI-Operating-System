"""Typed configuration for Jarvis Core.

Safe defaults: the default input points to bundled sample fixtures, never a live
vault. ``read_only`` defaults to True. Excluded directories keep application-managed
folders (``.obsidian``, ``.git``) out of scope by default.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from pathlib import Path


class OutputFormat(str, Enum):
    """Rendering format for CLI output."""

    TEXT = "text"
    JSON = "json"


class LogLevel(str, Enum):
    """Supported logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


# Directories never traversed. `.obsidian` is explicitly excluded per the safety
# constraints (application-managed state must not be read).
DEFAULT_EXCLUDED_DIRS: frozenset[str] = frozenset(
    {
        ".obsidian",
        ".git",
        ".smart-env",
        ".trash",
        ".claude-vault",
        "node_modules",
        ".venv",
        "venv",
        "__pycache__",
    }
)


def _repo_root() -> Path:
    """Best-effort repository root (…/src/jarvis_core/config.py -> repo root)."""
    return Path(__file__).resolve().parents[2]


def default_fixture_path() -> Path:
    """Path to the bundled sample vault used as the safe default input."""
    return _repo_root() / "tests" / "fixtures" / "ai-operating-system"


@dataclass(frozen=True)
class Config:
    """Immutable runtime configuration with safe defaults.

    Attributes:
        vault_path: Directory to scan. Defaults to bundled sample fixtures.
        read_only: Always True in this prototype; a guard, not a toggle for writes.
        log_level: Logging verbosity.
        provider: Provider selection (only ``mock`` is implemented).
        output_format: ``text`` or ``json``.
        max_files: Upper bound on notes discovered (protects against runaways).
        max_context_bytes: Upper bound on assembled context size.
        excluded_dirs: Directory names to skip during discovery.
    """

    vault_path: Path = field(default_factory=default_fixture_path)
    read_only: bool = True
    log_level: LogLevel = LogLevel.INFO
    provider: str = "mock"
    output_format: OutputFormat = OutputFormat.TEXT
    max_files: int = 5000
    max_context_bytes: int = 2_000_000
    excluded_dirs: frozenset[str] = DEFAULT_EXCLUDED_DIRS

    def with_overrides(self, **changes: object) -> Config:
        """Return a copy with selected fields overridden."""
        return replace(self, **changes)  # type: ignore[arg-type]

    def is_excluded(self, name: str) -> bool:
        """True if a directory name should be skipped."""
        return name in self.excluded_dirs
