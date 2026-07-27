"""Offline, deterministic query engine over the parsed vault.

This is the read-only foundation for a future AI-backed ``ask``. It does NOT call any
model, use the network, or require keys. It routes a natural-language question to one of
a few structured intents and answers from the graph and a keyword index. Results are
deterministic (stable ordering) so identical questions on identical vaults are
reproducible.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from jarvis_core.context.loader import ProjectContextLoader, ProjectNotFoundError
from jarvis_core.models.base import NoteType
from jarvis_core.models.context import SourceRef
from jarvis_core.models.note import Note
from jarvis_core.providers.mock import MockProvider
from jarvis_core.relationships.resolver import RelationshipResolver

_STOPWORDS = frozenset(
    {
        "the", "a", "an", "of", "to", "for", "in", "on", "with", "and", "or", "about",
        "that", "this", "is", "are", "show", "list", "find", "every", "all", "note",
        "notes", "related", "mention", "mentions", "project", "projects", "which",
        "what", "who", "where", "summarize", "summary", "summarise", "give", "me",
        "tell", "please",
    }
)


class Intent(str, Enum):
    SUMMARIZE_PROJECT = "summarize_project"
    PROJECTS_MENTIONING = "projects_mentioning"
    RELATED_TO = "related_to"
    SEARCH = "search"


@dataclass(frozen=True)
class QueryResult:
    """A deterministic answer to a question."""

    intent: Intent
    question: str
    answer: str
    matches: tuple[SourceRef, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "intent": self.intent.value,
            "question": self.question,
            "answer": self.answer,
            "matches": [m.to_dict() for m in self.matches],
        }


def _ref(note: Note) -> SourceRef:
    return SourceRef(id=note.id, title=(note.title or note.path.stem), relpath=note.relpath)


class QueryEngine:
    """Routes a question to an intent and answers from the vault (read-only)."""

    def __init__(self, notes: list[Note]) -> None:
        self._notes = notes
        self._resolver = RelationshipResolver(notes)
        self._report = self._resolver.resolve_all()
        self._by_relpath = {n.relpath: n for n in notes}
        # Lowercased searchable text per note (title + aliases + body + frontmatter values).
        self._text: dict[str, str] = {}
        for n in notes:
            parts = [n.title or "", *n.aliases, n.body]
            parts.extend(str(v) for v in n.frontmatter.values())
            self._text[n.relpath] = "\n".join(parts).lower()

    # ------------------------------------------------------------------ routing
    def ask(self, question: str) -> QueryResult:
        q = question.strip()
        ql = q.lower()

        m = re.search(r"(?:summar(?:y|ize|ise))\b(?:\s+the)?\s+(.+)", ql)
        if m:
            name = self._strip_trailing(m.group(1), ("project", "note"))
            return self._summarize_project(q, name)

        m = re.search(
            r"(?:what|which)\s+projects?\s+"
            r"(?:mention|reference|use|involve|are about|about)\s+(.+)",
            ql,
        )
        if m:
            return self._projects_mentioning(q, self._clean_term(m.group(1)))

        m = re.search(r"(?:related to|about|regarding|mention(?:s|ing)?)\s+(.+)", ql)
        wants_related = any(
            w in ql for w in ("related", "show", "list", "every note", "notes")
        )
        if m and wants_related:
            return self._related_to(q, self._clean_term(m.group(1)))

        return self._search(q, self._salient_terms(ql))

    # ------------------------------------------------------------------ intents
    def _summarize_project(self, question: str, name: str) -> QueryResult:
        loader = ProjectContextLoader(self._notes)
        try:
            package = loader.load(name)
        except ProjectNotFoundError as exc:
            return QueryResult(Intent.SUMMARIZE_PROJECT, question, f"{exc}")
        response = MockProvider().summarize(package, model_role="research")
        matches = tuple(package.sources)
        return QueryResult(Intent.SUMMARIZE_PROJECT, question, response.summary, matches)

    def _projects_mentioning(self, question: str, term: str) -> QueryResult:
        if not term:
            return QueryResult(Intent.PROJECTS_MENTIONING, question, "No search term found.")
        hits: list[Note] = []
        for n in self._notes:
            if n.type is not NoteType.PROJECT:
                continue
            if self._note_or_related_mentions(n, term):
                hits.append(n)
        hits.sort(key=lambda n: n.relpath)
        if not hits:
            answer = f"No projects mention '{term}'."
        else:
            names = ", ".join((h.title or h.path.stem) for h in hits)
            answer = f"{len(hits)} project(s) mention '{term}': {names}."
        return QueryResult(
            Intent.PROJECTS_MENTIONING, question, answer, tuple(_ref(h) for h in hits)
        )

    def _related_to(self, question: str, term: str) -> QueryResult:
        if not term:
            return QueryResult(Intent.RELATED_TO, question, "No search term found.")
        direct = [n for n in self._notes if term in self._text[n.relpath]]
        related: dict[str, Note] = {n.relpath: n for n in direct}
        # include one-hop neighbours of direct matches
        for n in direct:
            for tgt in self._report.outgoing(n.relpath):
                if tgt in self._by_relpath:
                    related.setdefault(tgt, self._by_relpath[tgt])
            for src in self._report.incoming(n.relpath):
                if src in self._by_relpath:
                    related.setdefault(src, self._by_relpath[src])
        ordered = sorted(related.values(), key=lambda n: n.relpath)
        if not ordered:
            answer = f"No notes related to '{term}'."
        else:
            answer = f"{len(ordered)} note(s) related to '{term}' (direct matches and neighbours)."
        return QueryResult(
            Intent.RELATED_TO, question, answer, tuple(_ref(n) for n in ordered)
        )

    def _search(self, question: str, terms: list[str]) -> QueryResult:
        if not terms:
            return QueryResult(Intent.SEARCH, question, "No searchable terms found.")
        scored: list[tuple[int, str, Note]] = []
        for n in self._notes:
            text = self._text[n.relpath]
            score = sum(text.count(t) for t in terms)
            if score > 0:
                scored.append((score, n.relpath, n))
        # rank by score desc, then relpath for determinism
        scored.sort(key=lambda x: (-x[0], x[1]))
        top = [n for _, _, n in scored[:20]]
        if not top:
            answer = f"No notes match: {', '.join(terms)}."
        else:
            answer = (
                f"{len(scored)} note(s) match {terms}; top {len(top)} by keyword frequency."
            )
        return QueryResult(Intent.SEARCH, question, answer, tuple(_ref(n) for n in top))

    # ------------------------------------------------------------------ helpers
    def _note_or_related_mentions(self, project: Note, term: str) -> bool:
        if term in self._text[project.relpath]:
            return True
        for tgt in self._report.outgoing(project.relpath):
            if tgt in self._text and term in self._text[tgt]:
                return True
        for src in self._report.incoming(project.relpath):
            if src in self._text and term in self._text[src]:
                return True
        return False

    @staticmethod
    def _strip_trailing(text: str, words: tuple[str, ...]) -> str:
        t = text.strip().strip(".?!\"'").strip()
        for w in words:
            t = re.sub(rf"\s+{re.escape(w)}$", "", t).strip()
            t = re.sub(rf"^{re.escape(w)}\s+", "", t).strip()
        return t

    @staticmethod
    def _clean_term(text: str) -> str:
        return text.strip().strip(".?!\"'").strip()

    @staticmethod
    def _salient_terms(ql: str) -> list[str]:
        words = re.findall(r"[a-z0-9][a-z0-9\-]+", ql)
        seen: list[str] = []
        for w in words:
            if w not in _STOPWORDS and len(w) > 2 and w not in seen:
                seen.append(w)
        return seen
