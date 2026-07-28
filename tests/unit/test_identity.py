from __future__ import annotations

from jarvis_core.identity import compute_identity, fingerprint_bytes


def test_explicit_identity_is_namespaced():
    i = compute_identity("ws", "projects/a.md", "proj-a")
    assert i.kind == "explicit"
    assert i.source_id == "ws:id:proj-a"


def test_path_derived_when_no_id():
    i = compute_identity("ws", "Notes/A.md", None)
    assert i.kind == "path_derived"
    assert i.source_id == "ws:path:notes/a.md"


def test_identity_stable_across_rename_when_explicit():
    a = compute_identity("ws", "old/path.md", "same-id")
    b = compute_identity("ws", "new/location.md", "same-id")
    assert a.source_id == b.source_id  # survives a move (ADR-0017)


def test_identity_workspace_scoped():
    a = compute_identity("ws1", "a.md", "x")
    b = compute_identity("ws2", "a.md", "x")
    assert a.source_id != b.source_id


def test_fingerprint_tracks_bytes():
    assert fingerprint_bytes(b"abc") == fingerprint_bytes(b"abc")
    assert fingerprint_bytes(b"abc") != fingerprint_bytes(b"abc\n")
    assert fingerprint_bytes(b"a\r\nb") != fingerprint_bytes(b"a\nb")  # CRLF vs LF
