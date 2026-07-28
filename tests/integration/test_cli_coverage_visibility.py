"""AC-03R3-02: incomplete evidence is visibly distinct in CLI text, JSON, and exit status."""
from __future__ import annotations

import json

from jarvis_core.cli import EXIT_OK, EXIT_WARNINGS, _answered_exit, _print_answer
from jarvis_core.config import OutputFormat
from jarvis_core.query.intent import Intent
from jarvis_core.query.passages import Locator
from jarvis_core.query.results import Citation, QueryAnswer


def _supported() -> Citation:
    return Citation(
        source_id="local:id:a", source_identity_kind="explicit", title="Alpha",
        relpath="a.md", source_fingerprint="sha256:x", locator=Locator(("Alpha",), 3, 4),
        excerpt="supporting text", reason="retrieval match", relative_relevance=1.0,
        coverage="supported",
    )


def _incomplete() -> Citation:
    return Citation(
        source_id="local:id:b", source_identity_kind="explicit", title="Beta",
        relpath="b.md", source_fingerprint="sha256:y", locator=Locator((), 0, 0),
        excerpt="", reason="in assembled context", relative_relevance=None,
        coverage="incomplete",
    )


def _answer(citations) -> QueryAnswer:
    return QueryAnswer(Intent.SEARCH, "q", "an answer", tuple(citations))


def test_text_separates_supported_from_incomplete_and_hides_0_0(capsys):
    _print_answer(_answer([_supported(), _incomplete()]), None, OutputFormat.TEXT)
    out = capsys.readouterr().out
    assert "Sources (supporting passages):" in out
    assert "Evidence coverage incomplete" in out
    assert "no claim-supporting passage was found" in out
    assert "0-0" not in out                     # never render a fake line range
    assert "Coverage: partial (1 supported, 1 incomplete)" in out


def test_json_exposes_answer_level_coverage(capsys):
    _print_answer(_answer([_supported(), _incomplete()]), None, OutputFormat.JSON)
    d = json.loads(capsys.readouterr().out)
    assert d["citation_coverage"]["label"] == "partial"
    assert d["citation_coverage"]["supported"] == 1
    assert d["citation_coverage"]["incomplete"] == 1
    assert d["citation_coverage"]["limitation"]


def test_incomplete_only_answer_is_not_fully_evidence_backed():
    assert _answered_exit(_answer([_incomplete()])) == EXIT_WARNINGS
    assert _answered_exit(_answer([_supported()])) == EXIT_OK
    assert _answered_exit(_answer([])) == EXIT_WARNINGS


def test_incomplete_only_text_shows_coverage_incomplete(capsys):
    _print_answer(_answer([_incomplete()]), None, OutputFormat.TEXT)
    out = capsys.readouterr().out
    assert "Sources (supporting passages):" not in out
    assert "Evidence coverage incomplete" in out
    assert "Coverage: incomplete (0 supported, 1 incomplete)" in out
