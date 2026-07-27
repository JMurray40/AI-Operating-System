"""The core Note model plus the parsed-heading helper."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from jarvis_core.models.base import NoteType
from jarvis_core.models.links import AttachmentRef, Link


@dataclass(frozen=True)
class Heading:
    """A Markdown heading (level 1-6) and its text."""

    level: int
    text: str


@dataclass(frozen=True)
class Note:
    """A parsed Markdown note.

    Implementation-neutral: holds raw frontmatter alongside typed conveniences so the
    validator can inspect exactly what the author wrote. ``path`` is the source file;
    Jarvis never writes to it.
    """

    path: Path
    relpath: str
    frontmatter: dict[str, object]
    body: str
    headings: tuple[Heading, ...] = ()
    links: tuple[Link, ...] = ()
    attachments: tuple[AttachmentRef, ...] = ()
    tags: tuple[str, ...] = ()
    parse_errors: tuple[str, ...] = ()
    # --- exact-source provenance (v0.3.1; additive, set by the repository) ---
    source_text: str = ""          # exact decoded file text (for locator/excerpt/validation)
    source_fingerprint: str = ""   # sha256 of exact source *bytes* (revision, not identity)
    body_start_line: int = 1        # 1-based source line where the body begins (after fm)
    source_bytes: bytes = b""       # exact source bytes at discovery (revision snapshot)

    @property
    def source_lines(self) -> list[str]:
        """The exact source split into lines (no keepends), for locator resolution."""
        return self.source_text.splitlines()

    # --- typed conveniences derived from frontmatter ---
    @property
    def id(self) -> str | None:
        return _as_str(self.frontmatter.get("id"))

    @property
    def title(self) -> str | None:
        return _as_str(self.frontmatter.get("title")) or self._title_from_heading()

    @property
    def type(self) -> NoteType | None:
        return NoteType.from_value(_as_str(self.frontmatter.get("type")))

    @property
    def raw_type(self) -> str | None:
        return _as_str(self.frontmatter.get("type"))

    @property
    def status(self) -> str | None:
        return _as_str(self.frontmatter.get("status"))

    @property
    def sensitivity(self) -> str | None:
        return _as_str(self.frontmatter.get("sensitivity"))

    @property
    def aliases(self) -> tuple[str, ...]:
        return _as_str_tuple(self.frontmatter.get("aliases"))

    @property
    def has_frontmatter(self) -> bool:
        return bool(self.frontmatter)

    def frontmatter_list(self, key: str) -> tuple[str, ...]:
        """Return a frontmatter field coerced to a tuple of strings."""
        return _as_str_tuple(self.frontmatter.get(key))

    def section(self, heading_text: str) -> str | None:
        """Return the body text under a ``## heading`` (case-insensitive), if present."""
        return _extract_section(self.body, heading_text)

    def names(self) -> tuple[str, ...]:
        """All names this note can be resolved by: id, title, aliases, file stem."""
        out: list[str] = []
        for candidate in (self.id, self.title, *self.aliases, self.path.stem):
            if candidate and candidate not in out:
                out.append(candidate)
        return tuple(out)

    def _title_from_heading(self) -> str | None:
        for h in self.headings:
            if h.level == 1:
                return h.text
        return None


def _as_str(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip() or None
    return str(value)


def _as_str_tuple(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value.strip(),) if value.strip() else ()
    if isinstance(value, (list, tuple)):
        return tuple(str(v).strip() for v in value if str(v).strip())
    return ()


def _extract_section(body: str, heading_text: str) -> str | None:
    lines = body.splitlines()
    target = heading_text.strip().lower()
    start: int | None = None
    start_level = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            text = stripped[level:].strip()
            if start is None and text.lower() == target:
                start = i + 1
                start_level = level
            elif start is not None and level <= start_level:
                return "\n".join(lines[start:i]).strip()
    if start is not None:
        return "\n".join(lines[start:]).strip()
    return None
