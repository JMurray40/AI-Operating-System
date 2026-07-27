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


def build_query_vault(root: Path) -> None:
    """A small vault for query-engine tests (projects, mentions, related notes)."""
    root.mkdir(parents=True, exist_ok=True)

    def project(slug: str, title: str, body: str) -> str:
        return (
            f"---\nid: project-{slug}\ntype: project\ntitle: \"{title}\"\nstatus: active\n"
            f"created: {_DATE}\nupdated: {_DATE}\ngoal: \"{title} goal\"\npriority: medium\n"
            f"sensitivity: internal\n---\n\n# {title}\n\n{body}\n"
        )

    (root / "Bookkeeping App.md").write_text(
        project("bookkeeping", "Bookkeeping App",
                "Integrates with QuickBooks to sync invoices. Links [[QuickBooks]]."),
        encoding="utf-8")
    (root / "Marketing Site.md").write_text(
        project("marketing", "Marketing Site", "A static marketing website. No accounting."),
        encoding="utf-8")
    (root / "QuickBooks.md").write_text(
        _concept("concept-quickbooks", "QuickBooks",
                 "Accounting software used for bookkeeping. Links [[Bookkeeping App]]."),
        encoding="utf-8")
    (root / "Smart Home.md").write_text(
        project("smart-home", "Smart Home",
                "Home Automation project. Links [[Home Automation]]."),
        encoding="utf-8")
    (root / "Home Automation.md").write_text(
        _concept("concept-home-automation", "Home Automation",
                 "Controlling lights and devices at home. Links [[Smart Home]]."),
        encoding="utf-8")


def build_feature_vault(root: Path) -> None:
    """A vault exercising v0.3 ranking signals and edge cases.

    Includes: an alias-only match, a tag-only match, duplicate titles, a broken wikilink,
    a missing-frontmatter note, and a project whose term appears only via a linked note.
    Deterministic content.
    """
    root.mkdir(parents=True, exist_ok=True)

    # Project 'Invoicing' (alias 'Billing', tags finance/accounting), broken link to Ghost.
    (root / "Invoicing.md").write_text(
        "---\nid: project-invoicing\ntype: project\ntitle: \"Invoicing\"\n"
        "aliases: [Billing]\ntags: [finance, accounting]\nstatus: active\n"
        f"created: {_DATE}\nupdated: {_DATE}\ngoal: \"Automate invoicing\"\npriority: high\n"
        "sensitivity: internal\n---\n\n# Invoicing\n\n"
        "Syncs invoices with QuickBooks. Links [[Ledger]] and [[Ghost Note]].\n",
        encoding="utf-8",
    )
    # Concept 'Ledger' (tag accounting), no term 'quickbooks' in body.
    (root / "Ledger.md").write_text(
        "---\nid: concept-ledger\ntype: concept\ntitle: \"Ledger\"\ntags: [accounting]\n"
        f"status: active\ncreated: {_DATE}\nupdated: {_DATE}\nsensitivity: internal\n---\n\n"
        "# Ledger\n\nDouble-entry bookkeeping records. Links [[Invoicing]].\n",
        encoding="utf-8",
    )
    # Project 'Storefront' mentions quickbooks ONLY via linked note 'Payments'.
    (root / "Storefront.md").write_text(
        "---\nid: project-storefront\ntype: project\ntitle: \"Storefront\"\nstatus: active\n"
        f"created: {_DATE}\nupdated: {_DATE}\ngoal: \"Sell online\"\npriority: medium\n"
        "sensitivity: internal\n---\n\n# Storefront\n\nOnline shop. Links [[Payments]].\n",
        encoding="utf-8",
    )
    (root / "Payments.md").write_text(
        _concept("concept-payments", "Payments",
                 "Processes card payments via QuickBooks Payments. Links [[Storefront]]."),
        encoding="utf-8",
    )
    # Duplicate titles: two different notes both titled 'Report'.
    (root / "Report A.md").write_text(
        "---\nid: report-a\ntype: reference\ntitle: \"Report\"\nresource_type: doc\n"
        f"source_of_truth: local\nstatus: active\ncreated: {_DATE}\nupdated: {_DATE}\n"
        "sensitivity: internal\n---\n\n# Report\n\nQuarterly report alpha.\n",
        encoding="utf-8",
    )
    (root / "Report B.md").write_text(
        "---\nid: report-b\ntype: reference\ntitle: \"Report\"\nresource_type: doc\n"
        f"source_of_truth: local\nstatus: active\ncreated: {_DATE}\nupdated: {_DATE}\n"
        "sensitivity: internal\n---\n\n# Report\n\nQuarterly report beta.\n",
        encoding="utf-8",
    )
    # Missing-frontmatter note that still mentions a term.
    (root / "Scratch.md").write_text("# Scratch\n\nNotes about QuickBooks exports.\n",
                                     encoding="utf-8")


def build_trust_vault(root: Path) -> None:
    """A vault exercising v0.3.1 trust contracts: sensitivity, identity, passages, CRLF.

    Deterministic. Contains:
    - Alpha (public project) linking a restricted note and an internal concept;
    - Secret (restricted) with a unique term ``zebrasecret``;
    - Shared (internal concept);
    - Bare.md (no frontmatter -> unknown sensitivity, fails closed);
    - Dup1/Dup2 (duplicate explicit id);
    - Crlf.md written with CRLF line endings and nested headings.
    """
    root.mkdir(parents=True, exist_ok=True)

    (root / "Alpha.md").write_text(
        "---\nid: project-alpha\ntype: project\ntitle: \"Alpha\"\nstatus: active\n"
        f"created: {_DATE}\nupdated: {_DATE}\ngoal: \"Ship Alpha widget\"\npriority: high\n"
        "sensitivity: public\n---\n\n# Alpha\n\n"
        "Alpha widget project. Links [[Shared]] and [[Secret]].\n",
        encoding="utf-8",
    )
    (root / "Secret.md").write_text(
        "---\nid: note-secret\ntype: reference\ntitle: \"Secret\"\nresource_type: doc\n"
        f"source_of_truth: local\nstatus: active\ncreated: {_DATE}\nupdated: {_DATE}\n"
        "sensitivity: restricted\n---\n\n# Secret\n\nContains zebrasecret material. [[Alpha]]\n",
        encoding="utf-8",
    )
    (root / "Shared.md").write_text(
        _concept("concept-shared", "Shared", "Shared concept text. Links [[Alpha]]."),
        encoding="utf-8",
    )
    (root / "Bare.md").write_text("# Bare\n\nNo frontmatter here; sensitivity unknown.\n",
                                  encoding="utf-8")
    (root / "Dup1.md").write_text(
        "---\nid: dup-id\ntype: concept\ntitle: \"Dup One\"\nstatus: active\n"
        f"created: {_DATE}\nupdated: {_DATE}\nsensitivity: internal\n---\n\n"
        "# Dup One\n\n[[Alpha]]\n",
        encoding="utf-8",
    )
    (root / "Dup2.md").write_text(
        "---\nid: dup-id\ntype: concept\ntitle: \"Dup Two\"\nstatus: active\n"
        f"created: {_DATE}\nupdated: {_DATE}\nsensitivity: internal\n---\n\n"
        "# Dup Two\n\n[[Alpha]]\n",
        encoding="utf-8",
    )
    # CRLF file with nested headings for locator/newline tests.
    crlf = (
        "---\r\nid: note-crlf\r\ntype: concept\r\ntitle: \"Crlf\"\r\nstatus: active\r\n"
        f"created: {_DATE}\r\nupdated: {_DATE}\r\nsensitivity: internal\r\n---\r\n\r\n"
        "# Crlf\r\n\r\n## Details\r\n\r\nCrlf carriage content here. [[Alpha]]\r\n"
    )
    (root / "Crlf.md").write_bytes(crlf.encode("utf-8"))


def build_trust_vault_no_dupes(root: Path) -> None:
    """Like :func:`build_trust_vault` but without the duplicate-id notes (loadable)."""
    build_trust_vault(root)
    (root / "Dup1.md").unlink()
    (root / "Dup2.md").unlink()
