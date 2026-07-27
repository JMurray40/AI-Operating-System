"""In-memory lexical index over parsed notes.

Read-only and offline: builds an inverted index and per-note field token counts from the
already-parsed :class:`Note` set. No embeddings, no vector store, no background service
(explicitly out of scope for v0.3). Construction is O(total tokens); lookups are O(terms).

The index is deliberately separate from the ranker and the engine (single responsibility):
it answers "which notes contain this token, and how often, in which field?" and nothing
about relevance ordering.
"""
from __future__ import annotations

from collections import Counter

from jarvis_core.models.base import LinkKind
from jarvis_core.models.note import Note
from jarvis_core.query.fields import FIELD_ORDER, Field
from jarvis_core.query.tokenizer import normalize, tokenize


class NoteIndex:
    """Precomputed per-note lexical surfaces (immutable after construction)."""

    __slots__ = ("all_tokens", "field_counts", "field_norm", "note", "relpath")

    def __init__(self, note: Note) -> None:
        self.relpath = note.relpath
        self.note = note
        # Raw field texts.
        title = note.title or note.path.stem
        alias_text = " ".join(note.aliases)
        tag_text = " ".join(note.tags)
        filename = note.path.stem
        frontmatter_text = " ".join(
            str(v) for k, v in note.frontmatter.items() if k not in ("title", "aliases", "tags")
        )
        wikilink_text = " ".join(
            link.normalized_target()
            for link in note.links
            if link.kind in (LinkKind.WIKILINK, LinkKind.EMBED)
        )
        raw: dict[Field, str] = {
            Field.TITLE: title,
            Field.ALIAS: alias_text,
            Field.TAG: tag_text,
            Field.FILENAME: filename,
            Field.FRONTMATTER: frontmatter_text,
            Field.WIKILINK: wikilink_text,
            Field.BODY: note.body,
        }
        self.field_counts: dict[Field, Counter[str]] = {
            f: Counter(tokenize(raw[f])) for f in FIELD_ORDER
        }
        # Normalized whole-field strings (for exact title/alias/filename matching).
        self.field_norm: dict[Field, str] = {f: normalize(raw[f]) for f in FIELD_ORDER}
        self.all_tokens: frozenset[str] = frozenset(
            t for f in FIELD_ORDER for t in self.field_counts[f]
        )

    def count(self, field: Field, term: str) -> int:
        return self.field_counts[field].get(term, 0)


class LexicalIndex:
    """Inverted index + per-note surfaces over a fixed set of notes."""

    def __init__(self, notes: list[Note]) -> None:
        self._notes = notes
        self._by_relpath: dict[str, NoteIndex] = {}
        self._postings: dict[str, set[str]] = {}
        for note in notes:
            ni = NoteIndex(note)
            self._by_relpath[note.relpath] = ni
            for token in ni.all_tokens:
                self._postings.setdefault(token, set()).add(note.relpath)

    # ---------------------------------------------------------------- retrieval
    def candidates(self, terms: list[str]) -> set[str]:
        """Relpaths of notes containing *any* of ``terms`` (OR retrieval)."""
        hits: set[str] = set()
        for term in terms:
            hits |= self._postings.get(term, set())
        return hits

    def postings(self, term: str) -> set[str]:
        return set(self._postings.get(term, set()))

    # ------------------------------------------------------------------ access
    def get(self, relpath: str) -> NoteIndex:
        return self._by_relpath[relpath]

    def note(self, relpath: str) -> Note:
        return self._by_relpath[relpath].note

    def contains(self, relpath: str) -> bool:
        return relpath in self._by_relpath

    @property
    def size(self) -> int:
        return len(self._by_relpath)

    @property
    def vocabulary_size(self) -> int:
        return len(self._postings)
