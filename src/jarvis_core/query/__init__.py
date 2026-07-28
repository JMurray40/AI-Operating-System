"""Offline, read-only, authorized query engine over the parsed vault (v0.3.1)."""
from __future__ import annotations

from jarvis_core.query.contract import CONTRACT_VERSION, INDEX_VERSION
from jarvis_core.query.engine import QueryAnswer, QueryEngine, QueryResult
from jarvis_core.query.intent import Intent, IntentParser, ParsedQuery
from jarvis_core.query.passages import Locator
from jarvis_core.query.ranking import RankingWeights
from jarvis_core.query.results import Citation
from jarvis_core.query.trace import QueryTrace

__all__ = [
    "CONTRACT_VERSION",
    "INDEX_VERSION",
    "Citation",
    "Intent",
    "IntentParser",
    "Locator",
    "ParsedQuery",
    "QueryAnswer",
    "QueryEngine",
    "QueryResult",
    "QueryTrace",
    "RankingWeights",
]
