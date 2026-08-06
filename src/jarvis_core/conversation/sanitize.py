"""Content sanitization for provider output (R7, C25, AC-05-05).

A single low-level defanger shared by the application (before anything is stored) and the
presentation object (before anything is shown). Neutralizes active or automatically-fetched
content — HTML/script, remote images, data/javascript/file URLs, autolinks, and control
characters — while keeping readable, inert text.
"""
from __future__ import annotations

import re

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]*)\)")
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]*)\)")
_AUTOLINK_RE = re.compile(r"<((?:https?|data|javascript|file):[^>]*)>", re.IGNORECASE)
_BLOCKED_SCHEME_RE = re.compile(r"(?i)\b(?:javascript|data|file|vbscript):[^\s)]*")
_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def sanitize_markdown(text: str) -> str:
    """Defang active/auto-fetched content; keep readable, inert text."""
    text = _CONTROL_RE.sub("", text)
    text = _AUTOLINK_RE.sub(r"[blocked-link \1]", text)
    text = _IMAGE_RE.sub(r"[image: \1]", text)  # never emit a fetchable image reference
    text = _LINK_RE.sub(r"\1 (\2)", text)  # link text with inert URL in parentheses
    text = _BLOCKED_SCHEME_RE.sub("[blocked-scheme]", text)
    text = _HTML_TAG_RE.sub("", text)  # drop any HTML/script tags
    return text


__all__ = ["sanitize_markdown"]
