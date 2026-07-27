"""Deterministic text tokenization shared by the index and the intent parser.

Kept intentionally tiny and dependency-free: lexical retrieval must be reproducible,
so tokenization is a pure function of its input (no locale, no stemming, no randomness).
Semantic normalization (stemming, synonyms, embeddings) is explicitly out of scope for
v0.3 and belongs to a later semantic-search version.
"""
from __future__ import annotations

import re

# A token is a run of ASCII letters/digits that may contain internal hyphens.
# Mirrors the salient-term rule used by the v0.2 ``ask`` prototype so behaviour is stable.
_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9\-]*")

#: Words removed from *free-text queries* so ranking focuses on salient terms. This is a
#: query-side aid only; the index itself keeps every token so exact lookups never miss.
STOPWORDS: frozenset[str] = frozenset(
    {
        "the", "a", "an", "of", "to", "for", "in", "on", "with", "and", "or", "about",
        "that", "this", "is", "are", "show", "list", "find", "every", "all", "note",
        "notes", "related", "mention", "mentions", "project", "projects", "which",
        "what", "who", "where", "summarize", "summary", "summarise", "give", "me",
        "tell", "please", "explain", "relationship", "between", "everything",
        "discussing", "regarding",
    }
)


def normalize(text: str) -> str:
    """Lowercase and collapse a single value to a stable comparison key."""
    return " ".join(text.strip().lower().split())


def tokenize(text: str) -> list[str]:
    """Split ``text`` into lowercased lexical tokens (order preserved, duplicates kept)."""
    return _TOKEN_RE.findall(text.lower())


def token_set(text: str) -> set[str]:
    """Unique tokens in ``text`` (used for membership checks)."""
    return set(_TOKEN_RE.findall(text.lower()))


def salient_terms(text: str, *, min_len: int = 3) -> list[str]:
    """Query terms with stopwords and very short tokens removed (stable, de-duplicated)."""
    out: list[str] = []
    for tok in tokenize(text):
        if tok in STOPWORDS or len(tok) < min_len:
            continue
        if tok not in out:
            out.append(tok)
    return out
