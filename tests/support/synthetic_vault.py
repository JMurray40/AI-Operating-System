"""Deterministic synthetic-vault generators for tests.

These write to a caller-provided temporary directory (never a real vault). Content is
fully deterministic so tests are reproducible.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_DATE = "2026-07-27"


def _concept(note_id: str, title: str, body: str) -> str:
    return (
        f"---\nid: {note_id}\ntype: concept\ntitle: \"{title}\"\nstatus: active\n"
        f"created: {_DATE}\nupdated: {_DATE}\nsensitivity: internal\n---\n\n"
        f"# {title}\n\n{body}\n"
    )


@dataclass(frozen=True)
class ExpectedVault:
    """Expected metrics for a generated vault (for assertions)."""

    note_count: int
    missing_frontmatter: int = 0

    def missing_fm_count(self) -> int:
        return self.missing_frontmatter


def build_synthetic_vault(root: Path, n_notes: int, *, missing_fm: int = 0) -> ExpectedVault:
    """Create ``n_notes`` notes as a connected chain (no orphans, no broken links).

    ``missing_fm`` of them are written without frontmatter (still linked into the chain,
    so they remain connected). Deterministic; returns the expected metrics.
    """
    root.mkdir(parents=True, exist_ok=True)
    width = max(4, len(str(n_notes)))
    missing_indices = set(range(1, n_notes, max(1, n_notes // missing_fm))) if missing_fm else set()
    missing_indices = set(sorted(missing_indices)[:missing_fm])

    for i in range(n_notes):
        name = f"Note {i:0{width}d}"
        link = f"[[Note {i + 1:0{width}d}]]" if i < n_notes - 1 else "(end of chain)"
        if i in missing_indices:
            content = f"# {name}\n\nLinks to {link}\n"  # no frontmatter
        else:
            content = _concept(f"note-{i:0{width}d}", name, f"Links to {link}")
        (root / f"{name}.md").write_text(content, encoding="utf-8")

    return ExpectedVault(note_count=n_notes, missing_frontmatter=len(missing_indices))


@dataclass(frozen=True)
class ExpectedDefects:
    note_count: int
    missing_frontmatter: int
    duplicate_id: int
    orphan_note: int
    broken_wikilink: int
    invalid_schema: int
    missing_alias: int
    circular_reference: int


def build_defect_vault(root: Path) -> ExpectedDefects:
    """Create a small vault containing exactly one instance of each defect category."""
    root.mkdir(parents=True, exist_ok=True)

    # Alpha: valid project, links Bravo (cycle) and Ghost (broken).
    (root / "Alpha.md").write_text(
        "---\nid: project-alpha\ntype: project\ntitle: \"Alpha\"\nstatus: active\n"
        f"created: {_DATE}\nupdated: {_DATE}\ngoal: \"Test\"\npriority: low\n"
        "sensitivity: internal\n---\n\n# Alpha\n\nLinks [[Bravo]] and [[Ghost]].\n",
        encoding="utf-8",
    )
    # Bravo: links back to Alpha -> circular reference cluster {Alpha, Bravo}.
    (root / "Bravo.md").write_text(_concept("concept-bravo", "Bravo", "Links [[Alpha]]."),
                                   encoding="utf-8")
    # Duplicate ids.
    (root / "Dupe1.md").write_text(
        "---\nid: shared-id\ntype: concept\ntitle: \"Dupe1\"\nstatus: active\n"
        f"created: {_DATE}\nupdated: {_DATE}\nsensitivity: internal\n---\n\n# Dupe1\n\n[[Alpha]]\n",
        encoding="utf-8",
    )
    (root / "Dupe2.md").write_text(
        "---\nid: shared-id\ntype: concept\ntitle: \"Dupe2\"\nstatus: active\n"
        f"created: {_DATE}\nupdated: {_DATE}\nsensitivity: internal\n---\n\n# Dupe2\n\n[[Alpha]]\n",
        encoding="utf-8",
    )
    # Missing frontmatter (still linked -> not an orphan).
    (root / "NoFm.md").write_text("# NoFm\n\nLinks [[Alpha]]\n", encoding="utf-8")
    # Malformed YAML -> invalid schema (syntax) + counts as missing frontmatter.
    (root / "BadYaml.md").write_text(
        "---\nid: bad\ntitle: \"BadYaml\ntags: [x, y\n---\n\n# BadYaml\n\n[[Alpha]]\n",
        encoding="utf-8",
    )
    # Missing alias: filename differs from title, no alias covering it.
    (root / "Alias.md").write_text(
        "---\nid: concept-alias\ntype: concept\ntitle: \"Alias Title\"\nstatus: active\n"
        f"created: {_DATE}\nupdated: {_DATE}\nsensitivity: internal\n---\n\n"
        "# Alias Title\n\n[[Alpha]]\n",
        encoding="utf-8",
    )
    # Orphan: valid, no links either way.
    (root / "Orphan.md").write_text(_concept("concept-orphan", "Orphan", "No links here."),
                                    encoding="utf-8")

    return ExpectedDefects(
        note_count=8,
        missing_frontmatter=2,   # NoFm, BadYaml
        duplicate_id=2,          # Dupe1, Dupe2
        orphan_note=1,           # Orphan
        broken_wikilink=1,       # Ghost
        invalid_schema=1,        # BadYaml (syntax)
        missing_alias=1,         # Alias.md
        circular_reference=1,    # {Alpha, Bravo}
    )
