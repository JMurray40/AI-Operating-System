from __future__ import annotations

from jarvis_core.query.tokenizer import normalize, salient_terms, token_set, tokenize


def test_tokenize_lowercases_and_keeps_hyphens():
    assert tokenize("Read-Only QuickBooks!") == ["read-only", "quickbooks"]


def test_tokenize_is_deterministic():
    assert tokenize("A b A b") == tokenize("A b A b")


def test_token_set_dedupes():
    assert token_set("a a b") == {"a", "b"}


def test_normalize_collapses_whitespace():
    assert normalize("  Home   Automation ") == "home automation"


def test_salient_terms_drops_stopwords_and_short_tokens():
    assert salient_terms("What projects mention QuickBooks?") == ["quickbooks"]


def test_salient_terms_preserves_order_without_duplicates():
    assert salient_terms("alpha beta alpha gamma") == ["alpha", "beta", "gamma"]
