"""Query parsing: natural-language question -> structured :class:`ParsedQuery`.

Intent detection is a small, isolated responsibility. The engine, ranker, and graph
builder never re-parse text; they consume the :class:`ParsedQuery` this module produces.
Routing rules mirror the v0.2 ``ask`` prototype (so existing behaviour is preserved) and
add EXPLAIN_RELATIONSHIP for "relationship between A and B" questions.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from jarvis_core.query.tokenizer import salient_terms


class Intent(str, Enum):
    """The structured shape a question was routed to."""

    SUMMARIZE_PROJECT = "summarize_project"
    PROJECTS_MENTIONING = "projects_mentioning"
    RELATED_TO = "related_to"
    EXPLAIN_RELATIONSHIP = "explain_relationship"
    SEARCH = "search"


@dataclass(frozen=True)
class ParsedQuery:
    """The parsed form of a question.

    ``target`` carries a single named entity (summarize). ``left``/``right`` carry the two
    entities of an explain query. ``terms`` are salient free-text tokens for retrieval.
    """

    intent: Intent
    question: str
    terms: tuple[str, ...] = ()
    target: str | None = None
    left: str | None = None
    right: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "intent": self.intent.value,
            "question": self.question,
            "terms": list(self.terms),
            "target": self.target,
            "left": self.left,
            "right": self.right,
        }


_EXPLAIN_RE = re.compile(
    r"(?:explain|describe|what(?:'s| is))?\s*(?:the\s+)?relationship\s+between\s+(.+?)\s+and\s+(.+)"
)
_SUMMARIZE_RE = re.compile(r"(?:summar(?:y|ize|ise))\b(?:\s+the)?\s+(.+)")
_PROJECTS_RE = re.compile(
    r"(?:what|which)\s+projects?\s+"
    r"(?:mention|reference|use|involve|are about|about|discuss(?:ing)?)\s+(.+)"
)
_RELATED_RE = re.compile(r"(?:related to|about|regarding|mention(?:s|ing)?|discussing)\s+(.+)")


class IntentParser:
    """Pure parser: text in, :class:`ParsedQuery` out. No I/O, no graph access."""

    def parse(self, question: str) -> ParsedQuery:
        q = question.strip()
        ql = q.lower()

        m = _EXPLAIN_RE.search(ql)
        if m:
            left = self._clean(m.group(1))
            right = self._clean(m.group(2))
            return ParsedQuery(
                Intent.EXPLAIN_RELATIONSHIP, q, self._terms(f"{left} {right}"),
                left=left, right=right,
            )

        m = _SUMMARIZE_RE.search(ql)
        if m:
            target = self._strip_words(m.group(1), ("project", "note"))
            return ParsedQuery(
                Intent.SUMMARIZE_PROJECT, q, self._terms(target), target=target
            )

        m = _PROJECTS_RE.search(ql)
        if m:
            term = self._clean(m.group(1))
            return ParsedQuery(
                Intent.PROJECTS_MENTIONING, q, self._terms(term), target=term
            )

        m = _RELATED_RE.search(ql)
        wants_related = any(
            w in ql for w in ("related", "show", "list", "every note", "notes", "discussing")
        )
        if m and wants_related:
            term = self._clean(m.group(1))
            return ParsedQuery(Intent.RELATED_TO, q, self._terms(term), target=term)

        return ParsedQuery(Intent.SEARCH, q, self._terms(ql))

    # --------------------------------------------------------------- helpers
    @staticmethod
    def _terms(text: str) -> tuple[str, ...]:
        return tuple(salient_terms(text))

    @staticmethod
    def _clean(text: str) -> str:
        return text.strip().strip(".?!\"'").strip()

    @staticmethod
    def _strip_words(text: str, words: tuple[str, ...]) -> str:
        t = text.strip().strip(".?!\"'").strip()
        for w in words:
            t = re.sub(rf"\s+{re.escape(w)}$", "", t).strip()
            t = re.sub(rf"^{re.escape(w)}\s+", "", t).strip()
        return t
