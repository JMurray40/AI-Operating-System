"""Deterministic passage locators, excerpts, and citation validation (ADR-0016).

A citation binds a stable identity to an exact source revision (fingerprint) and a
deterministic passage: a heading path plus a 1-based inclusive source line range, with a
bounded excerpt copied verbatim from that passage. Validation proves the current bytes
match the fingerprint, the locator lies within the source, and the excerpt occurs in the
resolved passage. Nothing here normalizes or reorders source text.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from jarvis_core.identity import fingerprint_bytes
from jarvis_core.models.note import Note
from jarvis_core.query.tokenizer import token_set

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
_FENCE_RE = re.compile(r"^\s*(```|~~~)")
EXCERPT_MAX_LINES = 6
EXCERPT_MAX_CHARS = 600


@dataclass(frozen=True)
class Locator:
    """A deterministic passage locator: heading path + inclusive 1-based source lines."""

    heading_path: tuple[str, ...]
    line_start: int
    line_end: int

    def to_dict(self) -> dict[str, object]:
        return {
            "heading_path": list(self.heading_path),
            "line_start": self.line_start,
            "line_end": self.line_end,
        }


@dataclass(frozen=True)
class _Heading:
    line: int   # 1-based source line
    level: int
    text: str


def _headings(note: Note) -> list[_Heading]:
    """Body headings with source line numbers, skipping fenced code (deterministic)."""
    out: list[_Heading] = []
    in_fence = False
    for idx, line in enumerate(note.source_lines):
        source_line = idx + 1
        if source_line < note.body_start_line:
            continue
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = _HEADING_RE.match(line)
        if m:
            out.append(_Heading(source_line, len(m.group(1)), m.group(2).strip()))
    return out


def _heading_path(headings: list[_Heading], enclosing_idx: int) -> tuple[str, ...]:
    """Build the heading path by walking back through strictly-decreasing levels."""
    if enclosing_idx < 0:
        return ()
    path: list[str] = []
    level = headings[enclosing_idx].level + 1
    for i in range(enclosing_idx, -1, -1):
        if headings[i].level < level:
            path.append(headings[i].text)
            level = headings[i].level
            if level == 1:
                break
    path.reverse()
    return tuple(path)


def _section_bounds(
    note: Note, headings: list[_Heading], enclosing_idx: int
) -> tuple[int, int]:
    """Inclusive 1-based [start, end] source lines of a section's content."""
    total = len(note.source_lines)
    if enclosing_idx < 0:
        start = note.body_start_line
        end = headings[0].line - 1 if headings else total
    else:
        h = headings[enclosing_idx]
        start = h.line + 1
        end = total
        for later in headings[enclosing_idx + 1:]:
            if later.level <= h.level:
                end = later.line - 1
                break
    # Trim leading/trailing blank lines to point at real content.
    lines = note.source_lines
    while start <= end and start - 1 < total and not lines[start - 1].strip():
        start += 1
    while end >= start and end - 1 < total and not lines[end - 1].strip():
        end -= 1
    if start > end:
        start = end = min(max(note.body_start_line, 1), max(total, 1))
    return start, end


def _first_evidence_line(note: Note, start: int, end: int, terms: frozenset[str]) -> int:
    """First source line in [start,end] whose tokens intersect ``terms`` (else ``start``)."""
    lines = note.source_lines
    if terms:
        for ln in range(start, end + 1):
            if ln - 1 < len(lines) and token_set(lines[ln - 1]) & terms:
                return ln
    return start


def locate(note: Note, evidence_terms: frozenset[str] = frozenset()) -> tuple[Locator, str]:
    """Return a deterministic locator and bounded excerpt for a note's supporting passage."""
    headings = _headings(note)
    total = len(note.source_lines)
    if total == 0:
        return Locator((), 0, 0), ""

    # Choose the enclosing section: the one containing the first evidence line, else the
    # first content section.
    target_line = note.body_start_line
    if evidence_terms:
        for ln in range(note.body_start_line, total + 1):
            if ln - 1 < total and token_set(note.source_lines[ln - 1]) & evidence_terms:
                target_line = ln
                break
    enclosing_idx = -1
    for i, h in enumerate(headings):
        if h.line <= target_line:
            enclosing_idx = i
        else:
            break

    start, end = _section_bounds(note, headings, enclosing_idx)
    path = _heading_path(headings, enclosing_idx)

    # Excerpt: a deterministic window beginning at the first evidence line in the section.
    ev_line = _first_evidence_line(note, start, end, evidence_terms)
    ex_start = ev_line
    ex_end = min(end, ex_start + EXCERPT_MAX_LINES - 1)
    excerpt_lines = note.source_lines[ex_start - 1: ex_end]
    excerpt = "\n".join(excerpt_lines)[:EXCERPT_MAX_CHARS]
    return Locator(path, start, end), excerpt


@dataclass(frozen=True)
class CitationValidation:
    ok: bool
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {"ok": self.ok, "reason": self.reason}


def validate(
    *,
    locator: Locator,
    excerpt: str,
    source_fingerprint: str,
    current_bytes: bytes,
    current_text: str,
) -> CitationValidation:
    """Validate a citation against the current source (ADR-0016 four checks)."""
    if fingerprint_bytes(current_bytes) != source_fingerprint:
        return CitationValidation(False, "stale: source fingerprint changed")
    lines = current_text.splitlines()
    if not (1 <= locator.line_start <= locator.line_end <= len(lines)):
        return CitationValidation(False, "locator out of range")
    passage = "\n".join(lines[locator.line_start - 1: locator.line_end])
    if excerpt and excerpt not in passage:
        return CitationValidation(False, "excerpt not found in resolved passage")
    if locator.heading_path:
        head_texts = {
            _HEADING_RE.match(ln).group(2).strip()  # type: ignore[union-attr]
            for ln in lines
            if _HEADING_RE.match(ln)
        }
        if locator.heading_path[-1] not in head_texts:
            return CitationValidation(False, "heading path no longer resolves")
    return CitationValidation(True, "valid")
