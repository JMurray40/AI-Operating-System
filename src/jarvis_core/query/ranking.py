"""Deterministic, explainable relevance ranking.

Ranking is a pure function of (query terms, index, graph) plus a configurable
:class:`RankingWeights`. Every result carries a :class:`RankingExplanation` listing each
signal's raw value and weighted contribution, so a human can always answer "why did this
rank here?". Ordering ties break on ``relpath`` so identical inputs yield identical output.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from jarvis_core.models.note import Note
from jarvis_core.query.fields import FIELD_ORDER, Field
from jarvis_core.query.index import LexicalIndex
from jarvis_core.query.tokenizer import normalize
from jarvis_core.relationships.resolver import ResolutionReport


@dataclass(frozen=True)
class RankingWeights:
    """Per-signal weights. Tune here; the ranker holds no magic numbers of its own."""

    field_weights: dict[Field, float] = field(
        default_factory=lambda: {
            Field.TITLE: 12.0,
            Field.ALIAS: 9.0,
            Field.TAG: 7.0,
            Field.FILENAME: 6.0,
            Field.FRONTMATTER: 4.0,
            Field.WIKILINK: 3.0,
            Field.BODY: 1.0,
        }
    )
    exact_title: float = 25.0
    exact_alias: float = 20.0
    graph_proximity: float = 5.0
    backlink: float = 0.5
    recency: float = 0.0  # off by default: keeps ranking reproducible across clock time
    body_count_cap: int = 5
    backlink_cap: int = 10

    def to_dict(self) -> dict[str, object]:
        return {
            "field_weights": {f.value: w for f, w in self.field_weights.items()},
            "exact_title": self.exact_title,
            "exact_alias": self.exact_alias,
            "graph_proximity": self.graph_proximity,
            "backlink": self.backlink,
            "recency": self.recency,
            "body_count_cap": self.body_count_cap,
            "backlink_cap": self.backlink_cap,
        }


@dataclass(frozen=True)
class Signal:
    """One contributing factor in a note's score."""

    name: str
    raw: float
    weight: float

    @property
    def contribution(self) -> float:
        return round(self.raw * self.weight, 4)

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "raw": self.raw,
            "weight": self.weight,
            "contribution": self.contribution,
        }


@dataclass(frozen=True)
class RankingExplanation:
    """The full, human-readable justification for a note's rank."""

    relpath: str
    score: float
    signals: tuple[Signal, ...]

    def reasons(self) -> tuple[str, ...]:
        """Short phrases naming the signals that actually contributed, strongest first."""
        active = sorted(
            (s for s in self.signals if s.contribution > 0),
            key=lambda s: (-s.contribution, s.name),
        )
        return tuple(f"{s.name} (+{s.contribution:g})" for s in active)

    def to_dict(self) -> dict[str, object]:
        return {
            "relpath": self.relpath,
            "score": round(self.score, 4),
            "signals": [s.to_dict() for s in self.signals if s.contribution > 0],
            "reasons": list(self.reasons()),
        }


@dataclass(frozen=True)
class ScoredNote:
    """A note with its score, confidence (0-1, relative to the top hit), and explanation."""

    note: Note
    score: float
    confidence: float
    explanation: RankingExplanation

    @property
    def relpath(self) -> str:
        return self.note.relpath


class Ranker:
    """Scores candidate notes for a set of query terms. No I/O; pure over its inputs."""

    def __init__(
        self,
        index: LexicalIndex,
        report: ResolutionReport,
        weights: RankingWeights | None = None,
    ) -> None:
        self._index = index
        self._report = report
        self._weights = weights or RankingWeights()
        # Precompute backlink counts once (O(E)) so scoring stays O(candidates), not
        # O(candidates * E). Without this, per-candidate report.incoming() rescans every
        # edge, making ranking quadratic on densely linked vaults.
        counts: Counter[str] = Counter(e.target_relpath for e in report.edges)
        self._backlink_counts: dict[str, int] = dict(counts)

    @property
    def weights(self) -> RankingWeights:
        return self._weights

    def rank(
        self,
        terms: list[str],
        candidates: set[str],
        *,
        phrase: str | None = None,
        neighbor_boost: frozenset[str] = frozenset(),
    ) -> list[ScoredNote]:
        """Return candidates scored and ordered by (-score, relpath)."""
        phrase_norm = normalize(phrase) if phrase else None
        scored: list[tuple[float, str, RankingExplanation, Note]] = []
        for relpath in candidates:
            ni = self._index.get(relpath)
            signals: list[Signal] = []

            # Field frequency signals.
            for f in FIELD_ORDER:
                raw = float(sum(ni.count(f, t) for t in terms))
                if f is Field.BODY:
                    raw = min(raw, float(self._weights.body_count_cap))
                if raw:
                    signals.append(Signal(f"{f.value}_match", raw, self._weights.field_weights[f]))

            # Exact whole-field matches (phrase equals the title/alias/filename).
            if phrase_norm:
                if ni.field_norm[Field.TITLE] == phrase_norm:
                    signals.append(Signal("exact_title", 1.0, self._weights.exact_title))
                if phrase_norm and phrase_norm in {
                    normalize(a) for a in ni.note.aliases
                }:
                    signals.append(Signal("exact_alias", 1.0, self._weights.exact_alias))

            # Graph proximity: a one-hop neighbour of a strong direct match.
            if relpath in neighbor_boost:
                signals.append(Signal("graph_proximity", 1.0, self._weights.graph_proximity))

            # Backlink authority (capped).
            backlinks = min(self._backlink_counts.get(relpath, 0), self._weights.backlink_cap)
            if backlinks:
                signals.append(Signal("backlinks", float(backlinks), self._weights.backlink))

            score = round(sum(s.contribution for s in signals), 4)
            if score <= 0:
                continue
            scored.append(
                (score, relpath, RankingExplanation(relpath, score, tuple(signals)), ni.note)
            )

        scored.sort(key=lambda x: (-x[0], x[1]))
        top = scored[0][0] if scored else 0.0
        results: list[ScoredNote] = []
        for score, _relpath, explanation, note in scored:
            confidence = round(score / top, 3) if top > 0 else 0.0
            results.append(ScoredNote(note, score, confidence, explanation))
        return results
