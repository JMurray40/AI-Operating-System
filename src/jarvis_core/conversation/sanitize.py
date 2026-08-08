"""Content sanitization for provider output (R7, C25, AC-05-05R).

A single low-level defanger shared by every public surface — the application (before
anything is stored), the presentation object (before anything is shown), and therefore the
in-process API, text, JSON, CLI, trace, and history renderers that all consume it (AC-05-05R:
ONE pipeline, applied uniformly, not one per surface). Neutralizes active or
automatically-fetched content — HTML/script, remote images, data/javascript/file URLs,
autolinks, and control characters — while keeping readable, inert text.

AC-05-05R residual: the prior round's pipeline handled active/fetchable content but never
addressed three named categories from the redaction corpus: (1) Windows/POSIX absolute-path
disclosure, (2) traceback/exception/file-line disclosure, and (3) credential/secret-like
canaries. All three are addressed here so every public surface gets the same guarantee.
"""
from __future__ import annotations

import re

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]*)\)")
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]*)\)")
_AUTOLINK_RE = re.compile(r"<((?:https?|data|javascript|file):[^>]*)>", re.IGNORECASE)
_BLOCKED_SCHEME_RE = re.compile(r"(?i)\b(?:javascript|data|file|vbscript):[^\s)]*")
_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

# AC-05-05R: absolute-path disclosure. Windows drive-letter paths, UNC paths, and POSIX
# absolute paths. Deliberately requires an ABSOLUTE leading form (drive letter + backslash,
# double backslash, or a "/" not preceded by a word/dot/slash char) so it never touches an
# ordinary fraction ("3/4"), a relative mention ("path/to/file"), or a URL already handled by
# the link/image/autolink rules above (which never leave a bare "//" for this rule to see).
_WINDOWS_DRIVE_PATH_RE = re.compile(r"[A-Za-z]:\\(?:[^\s\\/:*?\"<>|]+\\)*[^\s\\/:*?\"<>|]*")
_UNC_PATH_RE = re.compile(r"\\\\[^\s\\]+(?:\\[^\s\\]+)+")
_POSIX_ABS_PATH_RE = re.compile(r"(?<![\w./])/(?:[A-Za-z0-9_.\-]+/)+[A-Za-z0-9_.\-]*")

# AC-05-05R: traceback/exception/file-line disclosure.
_TRACEBACK_HEADER_RE = re.compile(r"(?i)Traceback\s*\(most recent call last\)\s*:?")
_FILE_LINE_RE = re.compile(r'File\s+"[^"\n]+"\s*,\s*line\s+\d+')
_EXCEPTION_MARKER_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_.]*(?:Error|Exception)\b\s*:")

# AC-05-05R: credential/bearer-token/API-key/secret-like canaries. Deterministic, not fuzzy:
# a word containing one of the named secret-shaped substrings (case-insensitive), optionally
# with a following "=value"/":value", is redacted whole. This intentionally catches this
# codebase's own test canaries (e.g. "SECRETVALUE", "CANARY-API-KEY-...") since they are
# exactly the shape a real leaked secret would take in provider output.
_SECRET_LIKE_RE = re.compile(
    r"(?i)\b[\w.\-]*(?:secret|password|passwd|credential|api[_-]?key|access[_-]?key|"
    r"bearer)[\w.\-]*(?:\s*[:=]\s*[^\s,;)]+)?"
)
_BEARER_HEADER_RE = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9\-_.=]{6,}\b")


def sanitize_markdown(text: str) -> str:
    """Defang active/auto-fetched content and redact disclosure-shaped text; keep the rest
    readable and inert."""
    text = _CONTROL_RE.sub("", text)
    text = _AUTOLINK_RE.sub(r"[blocked-link \1]", text)
    text = _IMAGE_RE.sub(r"[image: \1]", text)  # never emit a fetchable image reference
    text = _LINK_RE.sub(r"\1 (\2)", text)  # link text with inert URL in parentheses
    text = _BLOCKED_SCHEME_RE.sub("[blocked-scheme]", text)
    text = _HTML_TAG_RE.sub("", text)  # drop any HTML/script tags
    text = _BEARER_HEADER_RE.sub("[redacted-credential]", text)
    text = _SECRET_LIKE_RE.sub("[redacted-credential]", text)
    text = _TRACEBACK_HEADER_RE.sub("[redacted-traceback]", text)
    text = _FILE_LINE_RE.sub("[redacted-file-line]", text)
    text = _EXCEPTION_MARKER_RE.sub("[redacted-error]:", text)
    text = _WINDOWS_DRIVE_PATH_RE.sub("[redacted-path]", text)
    text = _UNC_PATH_RE.sub("[redacted-path]", text)
    text = _POSIX_ABS_PATH_RE.sub("[redacted-path]", text)
    return text


__all__ = ["sanitize_markdown"]
