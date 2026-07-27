"""Combine frontmatter and inline parsing into a Note."""
from __future__ import annotations

from pathlib import Path

from jarvis_core.models.links import AttachmentRef, Link
from jarvis_core.models.note import Note
from jarvis_core.parsing.frontmatter import split_frontmatter
from jarvis_core.parsing.inline import (
    parse_headings,
    parse_markdown_links,
    parse_tags,
    parse_wikilinks,
)


def parse_note(path: Path, relpath: str, text: str) -> Note:
    """Parse raw file ``text`` into a :class:`Note`.

    Parsing never raises for content problems; issues are recorded in
    ``Note.parse_errors`` so a single malformed file does not abort a scan.
    """
    errors: list[str] = []
    fm = split_frontmatter(text)
    if fm.error:
        errors.append(fm.error)

    body = fm.body
    wl_links, wl_attach = parse_wikilinks(body)
    md_links, md_attach = parse_markdown_links(body)

    links: list[Link] = [*wl_links, *md_links]
    attachments: list[AttachmentRef] = [*wl_attach, *md_attach]

    headings = parse_headings(body)
    tags = parse_tags(body, fm.data.get("tags"))

    # Deterministic ordering of links/attachments for stable downstream output.
    links_sorted = tuple(sorted(links))
    attach_sorted = tuple(sorted(attachments))

    return Note(
        path=path,
        relpath=relpath,
        frontmatter=fm.data,
        body=body,
        headings=headings,
        links=links_sorted,
        attachments=attach_sorted,
        tags=tags,
        parse_errors=tuple(errors),
    )


