from __future__ import annotations

from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.conversation import ConversationManager, StreamEventKind
from jarvis_core.models.context import ContextPackage
from jarvis_core.providers.base import ProviderResponse
from jarvis_core.query import QueryEngine
from jarvis_core.repositories import FileSystemKnowledgeRepository


def _notes(path: Path):
    return FileSystemKnowledgeRepository(Config(vault_path=path)).discover()


class FailingProvider:
    """A provider that always fails (to exercise provider-failure handling)."""

    name = "failing"

    def summarize(self, package: ContextPackage, model_role: str = "fast") -> ProviderResponse:
        raise RuntimeError("simulated provider outage")


def test_streaming_emits_normalized_event_sequence(fileorbit_dir: Path):
    mgr = ConversationManager(QueryEngine(_notes(fileorbit_dir)))
    events = list(mgr.ask_stream("What is FileOrbit?"))
    kinds = [e.kind for e in events]
    assert kinds[0] is StreamEventKind.STARTED
    assert kinds[-1] is StreamEventKind.COMPLETED
    assert StreamEventKind.DELTA in kinds
    assert StreamEventKind.USAGE in kinds
    # reassembled deltas equal the answer text
    text = "".join(e.text for e in events if e.kind is StreamEventKind.DELTA)
    assert "match" in text


def test_provider_failure_is_graceful(fileorbit_dir: Path):
    engine = QueryEngine(_notes(fileorbit_dir), provider=FailingProvider())
    mgr = ConversationManager(engine)
    # 'summarize' intent triggers the provider; failure must not raise.
    ans, _ = mgr.ask("Summarize the FileOrbit project")
    assert ans.status == "failed"
    assert "provider" in ans.text.lower()
    # session still recorded the turn (session-only memory intact)
    assert mgr.session.turn_count == 1


def test_streaming_failure_emits_failed_event(fileorbit_dir: Path):
    engine = QueryEngine(_notes(fileorbit_dir), provider=FailingProvider())
    mgr = ConversationManager(engine)
    kinds = [e.kind for e in mgr.ask_stream("Summarize the FileOrbit project")]
    assert kinds[-1] is StreamEventKind.FAILED
