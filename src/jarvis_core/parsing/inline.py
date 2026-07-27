"""Inline element extraction: wikilinks, embeds, markdown links, tags, headings."""
from __future__ import annotations

import re

from jarvis_core.models.base import LinkKind
from jarvis_core.models.links import AttachmentRef, Link
from jarvis_core.models.note import Heading

# [[target]], [[target|alias]], [[target#heading]], with optional leading ! for embeds
_WIKILINK_RE = re.compile(r"(!?)\[\[([^\]]+)\]\]")
# [text](url) markdown links, excluding images (leading !)
_MDLINK_RE = re.compile(r"(?<!\!)\[([^\]]*)\]\(([^)]+)\)")
# ![alt](path) markdown image embeds
_MDIMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
# #tag (not headings): a hash not preceded by word char, followed by tag chars
_TAG_RE = re.compile(r"(?:(?<=\s)|^)#([A-Za-z0-9_][A-Za-z0-9_\-/]*)")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*$", re.MULTILINE)
_CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`]*`")

_ATTACHMENT_EXTS = (
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".pdf", ".mp4", ".mov",
    ".mp3", ".wav", ".xlsx", ".docx", ".pptx", ".zip",
)


def _strip_code(text: str) -> str:
    """Remove code fences and inline code so their contents are not misparsed."""
    return _INLINE_CODE_RE.sub(" ", _CODE_FENCE_RE.sub(" ", text))


def _looks_like_attachment(target: str) -> bool:
    base = target.split("#", 1)[0].split("|", 1)[0].strip().lower()
    return base.endswith(_ATTACHMENT_EXTS)


def parse_wikilinks(text: str) -> tuple[list[Link], list[AttachmentRef]]:
    """Return (links, attachments) from wikilink and embed syntax."""
    clean = _strip_code(text)
    links: list[Link] = []
    attachments: list[AttachmentRef] = []
    for bang, inner in _WIKILINK_RE.findall(clean):
        is_embed = bang == "!"
        target_part, _, display = inner.partition("|")
        target_no_alias = target_part.strip()
        target_main, _, heading = target_no_alias.partition("#")
        target_main = target_main.strip()
        if _looks_like_attachment(target_no_alias):
            attachments.append(AttachmentRef(target=target_no_alias, is_embed=is_embed))
            continue
        links.append(
            Link(
                kind=LinkKind.EMBED if is_embed else LinkKind.WIKILINK,
                target=target_main or target_no_alias,
                display=display.strip() or None,
                heading=heading.strip() or None,
            )
        )
    return links, attachments


def parse_markdown_links(text: str) -> tuple[list[Link], list[AttachmentRef]]:
    """Return (links, attachments) from markdown link and image syntax."""
    clean = _strip_code(text)
    attachments = [
        AttachmentRef(target=url.strip(), is_embed=True)
        for _, url in _MDIMG_RE.findall(clean)
    ]
    links: list[Link] = []
    for display, url in _MDLINK_RE.findall(clean):
        url = url.strip()
        if _looks_like_attachment(url):
            attachments.append(AttachmentRef(target=url, is_embed=False))
            continue
        links.append(Link(kind=LinkKind.MARKDOWN, target=url, display=display.strip() or None))
    return links, attachments


def parse_tags(text: str, frontmatter_tags: object = None) -> tuple[str, ...]:
    """Return sorted, de-duplicated tags from body ``#tags`` and frontmatter."""
    clean = _strip_code(text)
    found: set[str] = {m.group(1) for m in _TAG_RE.finditer(clean)}
    if isinstance(frontmatter_tags, str):
        found.add(frontmatter_tags.strip().lstrip("#"))
    elif isinstance(frontmatter_tags, (list, tuple)):
        for t in frontmatter_tags:
            if str(t).strip():
                found.add(str(t).strip().lstrip("#"))
    return tuple(sorted(found))


def parse_headings(text: str) -> tuple[Heading, ...]:
    """Return headings in document order (code fences ignored)."""
    clean = _CODE_FENCE_RE.sub("", text)
    return tuple(
        Heading(level=len(h[0]), text=h[1].strip())
        for h in _HEADING_RE.findall(clean)
        if h[1].strip()
    )
