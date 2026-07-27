"""Filesystem-backed, strictly read-only knowledge repository."""
from __future__ import annotations

from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.logging_setup import get_logger
from jarvis_core.metrics import PerfReport, measure
from jarvis_core.models.note import Note
from jarvis_core.parsing import parse_note, parse_note_timed

logger = get_logger()


class FileSystemKnowledgeRepository:
    """Discover and parse Markdown notes under a directory, read-only.

    Opens files with mode ``"r"`` only. Never creates, modifies, moves, or deletes
    anything. Excluded directories (``.obsidian`` etc.) are skipped entirely.
    """

    def __init__(self, config: Config) -> None:
        self._config = config
        self._root = Path(config.vault_path).resolve()
        self._cache: list[Note] | None = None
        self._total_bytes: int = 0

    @property
    def root(self) -> Path:
        return self._root

    @property
    def total_bytes(self) -> int:
        """Total UTF-8 bytes read during the last discovery (note cache size)."""
        return self._total_bytes

    def _iter_markdown_paths(self) -> list[Path]:
        if not self._root.exists():
            raise FileNotFoundError(f"Vault path does not exist: {self._root}")
        if not self._root.is_dir():
            raise NotADirectoryError(f"Vault path is not a directory: {self._root}")
        results: list[Path] = []
        for path in sorted(self._root.rglob("*.md")):
            rel_parts = path.relative_to(self._root).parts
            if any(self._config.is_excluded(part) for part in rel_parts[:-1]):
                continue
            results.append(path)
            if len(results) >= self._config.max_files:
                logger.warning(
                    "max_files (%d) reached; discovery truncated", self._config.max_files
                )
                break
        return results

    def discover(self, perf: PerfReport | None = None) -> list[Note]:
        """Parse every in-scope Markdown file into a Note (deterministic order).

        When ``perf`` is supplied, disk reads (``disk_read``) are timed separately from
        parsing (``metadata_parse`` + ``markdown_parse``), so optimization effort can be
        directed precisely. Behaviour is otherwise identical.
        """
        notes: list[Note] = []
        total_bytes = 0
        for path in self._iter_markdown_paths():
            relpath = path.relative_to(self._root).as_posix()
            try:
                if perf is not None:
                    with measure(perf, "disk_read"):
                        text = path.read_text(encoding="utf-8", errors="replace")
                else:
                    text = path.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                logger.error("Could not read %s: %s", relpath, exc)
                continue
            total_bytes += len(text.encode("utf-8", errors="replace"))
            if perf is not None:
                notes.append(parse_note_timed(path, relpath, text, perf))
            else:
                notes.append(parse_note(path, relpath, text))
        notes.sort(key=lambda n: n.relpath)
        self._cache = notes
        self._total_bytes = total_bytes
        return notes

    def all_notes(self) -> list[Note]:
        """Return cached notes, discovering on first use."""
        if self._cache is None:
            return self.discover()
        return self._cache
