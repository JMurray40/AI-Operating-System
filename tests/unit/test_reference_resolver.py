from __future__ import annotations

from jarvis_core.conversation.entities import MentionedEntity
from jarvis_core.conversation.references import ReferenceResolver


def _ent(title: str, relpath: str, turn: int = 0) -> MentionedEntity:
    return MentionedEntity(relpath=relpath, title=title, id=None, turn=turn)


def test_no_pronoun_passthrough():
    r = ReferenceResolver().resolve("What is FileOrbit?", [])
    assert r.effective_query == "What is FileOrbit?"
    assert r.focus is None


def test_pronoun_resolves_to_focus():
    stack = [_ent("FileOrbit", "projects/FileOrbit.md")]
    r = ReferenceResolver().resolve("Who is working on it?", stack)
    assert r.focus is not None and r.focus.title == "FileOrbit"
    assert "FileOrbit" in r.effective_query
    assert "it" in r.pronouns
    assert any("refers to 'FileOrbit'" in a for a in r.assumptions)


def test_explicit_entity_is_not_substituted():
    stack = [_ent("FileOrbit", "projects/FileOrbit.md")]
    r = ReferenceResolver().resolve("What is FileOrbit exactly?", stack)
    # names the entity -> no pronoun substitution appended
    assert r.effective_query == "What is FileOrbit exactly?"


def test_related_topics_are_not_ambiguous():
    stack = [
        _ent("FileOrbit", "projects/FileOrbit.md"),
        _ent("FileOrbit Repository", "resources/FileOrbit Repository.md"),
    ]
    r = ReferenceResolver().resolve("What are its risks?", stack)
    assert r.ambiguous is False


def test_unrelated_topics_are_ambiguous():
    stack = [
        _ent("Smart Home", "Smart Home.md"),
        _ent("Bookkeeping App", "Bookkeeping App.md"),
    ]
    r = ReferenceResolver().resolve("Tell me about it", stack)
    assert r.ambiguous is True
    assert r.focus is not None and r.focus.title == "Smart Home"  # most recent


def test_resolution_is_deterministic():
    stack = [_ent("FileOrbit", "projects/FileOrbit.md")]
    a = ReferenceResolver().resolve("what about it?", stack).to_dict()
    b = ReferenceResolver().resolve("what about it?", stack).to_dict()
    assert a == b
