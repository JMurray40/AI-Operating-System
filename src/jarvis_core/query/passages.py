"""Deterministic passage locators, excerpts, and citation validation (ADR-0016, AC-03).

A citation binds a stable identity to an exact source revision (fingerprint) and a
deterministic passage: a heading path plus a 1-based inclusive source line range, with a
bounded excerpt copied verbatim from that passage. The passage is chosen to contain the
actual retrieval evidence — including matches in frontmatter, title, aliases, tags, or
filename, not body text only. Validation proves the current bytes match the fingerprint, the
locator lies within the source, the full heading hierarchy still encloses the locator, and
the (non-empty) excerpt occurs in the resolved passage. Nothing normalizes or reorders text.
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
    line: int
    level: int
    text: str


def _lines(text: str) -> list[str]:
    return text.splitlines()


def _body_start(lines: list[str]) -> int:
    """1-based line where the body begins (after a leading YAML frontmatter fence)."""
    if not lines:
        return 1
    if lines[0].lstrip("﻿").strip() != "---":
        return 1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return i + 2  # line after the closing fence
    return 1  # unterminated fence -> treat as no frontmatter


def _scan_headings(lines: list[str], body_start: int) -> list[_Heading]:
    out: list[_Heading] = []
    in_fence = False
    for idx, line in enumerate(lines):
        source_line = idx + 1
        if source_line < body_start:
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


def _enclosing_index(headings: list[_Heading], target: int) -> int:
    idx = -1
    for i, h in enumerate(headings):
        if h.line <= target:
            idx = i
        else:
            break
    return idx


def _heading_path(headings: list[_Heading], idx: int) -> tuple[str, ...]:
    if idx < 0:
        return ()
    path: list[str] = []
    level = headings[idx].level + 1
    for i in range(idx, -1, -1):
        if headings[i].level < level:
            path.append(headings[i].text)
            level = headings[i].level
            if level == 1:
                break
    path.reverse()
    return tuple(path)


def _section_bounds(
    lines: list[str], headings: list[_Heading], idx: int, body_start: int
) -> tuple[int, int]:
    total = len(lines)
    if idx < 0:
        # Pre-first-heading body region.
        start = body_start
        end = (headings[0].line - 1) if headings else total
    else:
        h = headings[idx]
        start = h.line + 1
        end = total
        for later in headings[idx + 1:]:
            if later.level <= h.level:
                end = later.line - 1
                break
    start = max(1, start)
    end = max(start, min(end, total))
    return start, end


def _heading_path_at(lines: list[str], line: int) -> tuple[str, ...]:
    body_start = _body_start(lines)
    if line < body_start:
        return ()
    headings = _scan_headings(lines, body_start)
    return _heading_path(headings, _enclosing_index(headings, line))


def _first_evidence_line(lines: list[str], evidence: frozenset[str]) -> int | None:
    for i, line in enumerate(lines):
        if token_set(line) & evidence:
            return i + 1
    return None


def _first_content_line(lines: list[str], body_start: int) -> int | None:
    for i in range(body_start - 1, len(lines)):
        if lines[i].strip():
            return i + 1
    for i, line in enumerate(lines):
        if line.strip():
            return i + 1
    return None


def locate(note: Note, evidence_terms: frozenset[str] = frozenset()) -> tuple[Locator, str]:
    """Return a deterministic locator + excerpt for the passage supporting the evidence.

    Returns an empty locator/excerpt when no supporting passage exists (e.g. empty source, or
    non-empty evidence that appears nowhere) so the caller can decline a material citation.
    """
    lines = note.source_lines
    total = len(lines)
    if total == 0:
        return Locator((), 0, 0), ""
    body_start = _body_start(lines)
    if evidence_terms:
        target = _first_evidence_line(lines, evidence_terms)
        if target is None:
            return Locator((), 0, 0), ""  # evidence not present -> no supporting passage
    else:
        target = _first_content_line(lines, body_start)
        if target is None:
            return Locator((), 0, 0), ""

    headings = _scan_headings(lines, body_start)
    if target < body_start:
        # Evidence is in the frontmatter block (e.g. a title/metadata match): cite it.
        path: tuple[str, ...] = ()
        sstart, send = 1, max(1, body_start - 1)
    else:
        idx = _enclosing_index(headings, target)
        path = _heading_path(headings, idx)
        sstart, send = _section_bounds(lines, headings, idx, body_start)

    ex_start = max(target, sstart)
    ex_end = min(send, ex_start + EXCERPT_MAX_LINES - 1)
    excerpt = "\n".join(lines[ex_start - 1: ex_end])[:EXCERPT_MAX_CHARS]
    if not excerpt.strip():
        excerpt = lines[target - 1][:EXCERPT_MAX_CHARS]
    return Locator(path, sstart, send), excerpt


@dataclass(frozen=True)
class CitationValidation:
    ok: bool
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {"ok": self.ok, "reason": self.reason}


def validate_against_text(locator: Locator, excerpt: str, current_text: str) -> CitationValidation:
    """Structural validation (no fingerprint): locator, heading path, and excerpt."""
    if not excerpt:
        return CitationValidation(False, "empty excerpt")
    lines = _lines(current_text)
    if not (1 <= locator.line_start <= locator.line_end <= len(lines)):
        return CitationValidation(False, "locator out of range")
    passage = "\n".join(lines[locator.line_start - 1: locator.line_end])
    if excerpt not in passage:
        return CitationValidation(False, "excerpt not found in resolved passage")
    if _heading_path_at(lines, locator.line_start) != tuple(locator.heading_path):
        return CitationValidation(False, "heading hierarchy no longer encloses locator")
    return CitationValidation(True, "valid")


def validate(
    *,
    locator: Locator,
    excerpt: str,
    source_fingerprint: str,
    current_bytes: bytes,
    current_text: str,
) -> CitationValidation:
    """Full validation including staleness (ADR-0016): fingerprint + structure."""
    if fingerprint_bytes(current_bytes) != source_fingerprint:
        return CitationValidation(False, "stale: source fingerprint changed")
    return validate_against_text(locator, excerpt, current_text)
