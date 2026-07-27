"""Offline, read-only query engine over the parsed vault.

Composed of small collaborators: tokenizer, lexical index, intent parser, ranker,
context builder, and trace. The :class:`QueryEngine` orchestrates them.
"""
from __future__ import annotations

from jarvis_core.query.engine import QueryAnswer, QueryEngine, QueryResult
from jarvis_core.query.intent import Intent, IntentParser, ParsedQuery
from jarvis_core.query.ranking import RankingWeights
from jarvis_core.query.results import Citation
from jarvis_core.query.trace import QueryTrace

__all__ = [
    "Citation",
    "Intent",
    "IntentParser",
    "ParsedQuery",
    "QueryAnswer",
    "QueryEngine",
    "QueryResult",
    "QueryTrace",
    "RankingWeights",
]
