"""Reference and attachment models."""
from __future__ import annotations

from dataclasses import dataclass

from jarvis_core.models.base import LinkKind


@dataclass(frozen=True, order=True)
class Link:
    """A reference discovered in a note (wikilink, embed, markdown, or frontmatter).

    ``target`` is the raw target text (before resolution); ``display`` is the alias
    shown to the reader if one was given.
    """

    kind: LinkKind
    target: str
    display: str | None = None
    heading: str | None = None

    def normalized_target(self) -> str:
        """Target without heading/block anchors, trimmed for matching."""
        return self.target.split("#", 1)[0].strip()


@dataclass(frozen=True, order=True)
class AttachmentRef:
    """A reference to a non-Markdown attachment (image, pdf, etc.)."""

    target: str
    is_embed: bool = False
