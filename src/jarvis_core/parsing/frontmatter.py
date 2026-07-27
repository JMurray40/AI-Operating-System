"""YAML frontmatter extraction with clear, non-crashing error reporting."""
from __future__ import annotations

from dataclasses import dataclass

import yaml


@dataclass(frozen=True)
class FrontmatterResult:
    """Parsed frontmatter and the remaining body.

    ``error`` is set (and ``data`` left empty) when a fenced frontmatter block is
    present but malformed. A note with no frontmatter is not an error.
    """

    data: dict[str, object]
    body: str
    had_fence: bool
    error: str | None = None


def split_frontmatter(text: str) -> FrontmatterResult:
    """Split a document into YAML frontmatter and body.

    Recognizes a leading ``---`` fence. Malformed YAML is reported as an error rather
    than raised, so a single bad file does not abort a full scan.
    """
    normalized = text.lstrip("﻿")
    if not normalized.startswith("---"):
        return FrontmatterResult(data={}, body=text, had_fence=False)

    lines = normalized.splitlines(keepends=True)
    # first line is the opening fence; find the closing fence
    closing_index: int | None = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            closing_index = i
            break
    if closing_index is None:
        return FrontmatterResult(
            data={}, body=text, had_fence=True,
            error="Unterminated frontmatter fence (no closing '---').",
        )

    raw = "".join(lines[1:closing_index])
    body = "".join(lines[closing_index + 1:])
    try:
        loaded = yaml.safe_load(raw) if raw.strip() else {}
    except yaml.YAMLError as exc:
        detail = str(exc).splitlines()[0] if str(exc) else exc.__class__.__name__
        return FrontmatterResult(
            data={}, body=body, had_fence=True, error=f"Invalid YAML frontmatter: {detail}"
        )
    if loaded is None:
        loaded = {}
    if not isinstance(loaded, dict):
        return FrontmatterResult(
            data={}, body=body, had_fence=True,
            error="Frontmatter is not a YAML mapping.",
        )
    return FrontmatterResult(data=loaded, body=body, had_fence=True)
