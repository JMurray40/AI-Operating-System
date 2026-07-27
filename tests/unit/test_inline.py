from __future__ import annotations

from jarvis_core.models.base import LinkKind
from jarvis_core.parsing.inline import (
    parse_headings,
    parse_markdown_links,
    parse_tags,
    parse_wikilinks,
)


def test_wikilink_with_alias_and_heading():
    links, attach = parse_wikilinks("See [[Target Note|Alias]] and [[Other#Section]].")
    targets = {lk.target: lk for lk in links}
    assert "Target Note" in targets
    assert targets["Target Note"].display == "Alias"
    assert targets["Target Note"].kind is LinkKind.WIKILINK
    assert targets["Other"].heading == "Section"
    assert attach == []


def test_embed_and_attachment_split():
    links, attach = parse_wikilinks("Embed ![[Some Note]] and image ![[pic.png]]")
    assert any(lk.kind is LinkKind.EMBED and lk.target == "Some Note" for lk in links)
    assert any(a.target == "pic.png" and a.is_embed for a in attach)


def test_markdown_links_and_images():
    links, attach = parse_markdown_links("[ext](https://x.com) and ![alt](img.png)")
    assert any(lk.target == "https://x.com" for lk in links)
    assert any(a.target == "img.png" for a in attach)


def test_tags_from_body_and_frontmatter_deduped_sorted():
    tags = parse_tags("Body #alpha and #beta/child", frontmatter_tags=["alpha", "gamma"])
    assert tags == ("alpha", "beta/child", "gamma")


def test_code_fences_ignored():
    links, _ = parse_wikilinks("```\n[[Not A Link]]\n```\nreal [[Real Link]]")
    assert [lk.target for lk in links] == ["Real Link"]


def test_headings_in_order():
    hs = parse_headings("# One\ntext\n## Two\n### Three")
    assert [(h.level, h.text) for h in hs] == [(1, "One"), (2, "Two"), (3, "Three")]
