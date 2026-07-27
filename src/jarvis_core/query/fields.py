"""The searchable fields a note contributes to the lexical index.

Field identity is centralized here so the index, ranker, and trace all agree on names
and on the default per-field ranking weight (one source of truth, no magic strings).
"""
from __future__ import annotations

from enum import Enum


class Field(str, Enum):
    """A distinct text surface extracted from a note for lexical matching."""

    TITLE = "title"
    ALIAS = "alias"
    TAG = "tag"
    FILENAME = "filename"
    FRONTMATTER = "frontmatter"
    WIKILINK = "wikilink"
    BODY = "body"


#: Deterministic display/iteration order for fields (strongest signal first).
FIELD_ORDER: tuple[Field, ...] = (
    Field.TITLE,
    Field.ALIAS,
    Field.TAG,
    Field.FILENAME,
    Field.FRONTMATTER,
    Field.WIKILINK,
    Field.BODY,
)
