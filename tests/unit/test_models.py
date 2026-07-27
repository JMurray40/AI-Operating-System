from __future__ import annotations

from pathlib import Path

from jarvis_core.models.base import NoteType
from jarvis_core.models.validation import (
    Severity,
    Stage,
    ValidationIssue,
    ValidationResult,
)
from jarvis_core.parsing import parse_note

DOC = """---
id: project-x
type: project
title: X Project
aliases: [XP]
---
# X Project
## Purpose
Do a thing.
## Resume here
Left off at step 3.
"""


def test_note_typed_conveniences():
    n = parse_note(Path("x.md"), "x.md", DOC)
    assert n.type is NoteType.PROJECT
    assert n.title == "X Project"
    assert "XP" in n.aliases
    assert n.section("Purpose") == "Do a thing."
    assert n.section("Resume here") == "Left off at step 3."
    assert "x" in {name.lower() for name in n.names()} or n.id == "project-x"


def test_validation_result_ok_and_ordering():
    issues = (
        ValidationIssue(Stage.POLICY, Severity.WARNING, "b.md", "w"),
        ValidationIssue(Stage.SYNTAX, Severity.ERROR, "a.md", "e"),
    )
    result = ValidationResult(issues).sorted()
    assert not result.ok
    assert result.errors[0].location == "a.md"
    # Deterministic ordering: sorting is stable and idempotent.
    assert result.issues == tuple(sorted(result.issues))
    assert ValidationResult(issues).sorted().issues == result.issues


def test_names_include_stem_when_no_title():
    n = parse_note(Path("Loose Note.md"), "Loose Note.md", "no frontmatter here")
    assert "Loose Note" in n.names()
