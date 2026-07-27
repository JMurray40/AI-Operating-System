from __future__ import annotations

from jarvis_core.parsing.frontmatter import split_frontmatter


def test_valid_frontmatter():
    r = split_frontmatter("---\ntype: project\ntitle: X\n---\nbody\n")
    assert r.error is None
    assert r.data["type"] == "project"
    assert r.body.strip() == "body"
    assert r.had_fence


def test_missing_frontmatter_is_not_an_error():
    r = split_frontmatter("# Just a heading\ntext")
    assert r.error is None
    assert r.data == {}
    assert not r.had_fence


def test_malformed_yaml_reported_not_raised():
    r = split_frontmatter('---\ntitle: "Unterminated\ntags: [a, b\n---\nbody')
    assert r.error is not None
    assert r.data == {}


def test_unterminated_fence():
    r = split_frontmatter("---\ntype: project\nno closing fence\n")
    assert r.error is not None
    assert "closing" in r.error.lower()
