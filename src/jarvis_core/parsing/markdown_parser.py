"""Combine frontmatter and inline parsing into a Note.

Parsing is split into two sub-steps so callers can measure them independently:
* **metadata parse** — YAML frontmatter (`split_frontmatter`);
* **markdown parse** — inline elements, links, tags, headings.

``parse_note`` keeps the original signature (backwards compatible). ``parse_note_timed``
records the two sub-steps into a :class:`PerfReport`.
"""
from __future__ import annotations

from pathlib import Path

from jarvis_core.metrics import PerfReport, measure
from jarvis_core.models.links import AttachmentRef, Link
from jarvis_core.models.note import Note
from jarvis_core.parsing.frontmatter import FrontmatterResult, split_frontmatter
from jarvis_core.parsing.inline import (
    parse_headings,
    parse_markdown_links,
    parse_tags,
    parse_wikilinks,
)


def _assemble(path: Path, relpath: str, fm: FrontmatterResult) -> Note:
    """Build a Note from an already-parsed frontmatter result (markdown step)."""
    errors: list[str] = []
    if fm.error:
        errors.append(fm.error)
    body = fm.body
    wl_links, wl_attach = parse_wikilinks(body)
    md_links, md_attach = parse_markdown_links(body)
    links: list[Link] = [*wl_links, *md_links]
    attachments: list[AttachmentRef] = [*wl_attach, *md_attach]
    return Note(
        path=path,
        relpath=relpath,
        frontmatter=fm.data,
        body=body,
        headings=parse_headings(body),
        links=tuple(sorted(links)),
        attachments=tuple(sorted(attachments)),
        tags=parse_tags(body, fm.data.get("tags")),
        parse_errors=tuple(errors),
    )


def parse_note(path: Path, relpath: str, text: str) -> Note:
    """Parse raw file ``text`` into a :class:`Note`.

    Parsing never raises for content problems; issues are recorded in
    ``Note.parse_errors`` so a single malformed file does not abort a scan.
    """
    return _assemble(path, relpath, split_frontmatter(text))


def parse_note_timed(path: Path, relpath: str, text: str, perf: PerfReport) -> Note:
    """Like :func:`parse_note`, recording ``metadata_parse`` and ``markdown_parse``."""
    with measure(perf, "metadata_parse"):
        fm = split_frontmatter(text)
    with measure(perf, "markdown_parse"):
        return _assemble(path, relpath, fm)
