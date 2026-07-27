"""Analyze a set of notes and produce a VaultHealthReport (read-only)."""
from __future__ import annotations

import hashlib
from pathlib import Path

from jarvis_core.context.validator import validate_notes
from jarvis_core.health.models import HealthCategory, HealthFinding, VaultHealthReport
from jarvis_core.models.note import Note
from jarvis_core.models.validation import Severity, Stage, ValidationResult
from jarvis_core.relationships.resolver import RelationshipResolver, ResolutionReport


def is_obsidian_vault(path: Path) -> bool:
    """True if the directory looks like an Obsidian vault (has a .obsidian folder)."""
    return (path / ".obsidian").is_dir()


def compute_vault_fingerprint(notes: list[Note]) -> str:
    """Deterministic content fingerprint of a vault (stable for identical content).

    Independent of scan time or filesystem timestamps, so it is safe to embed in a
    report envelope for cache-invalidation and change detection downstream.
    """
    hasher = hashlib.sha256()
    for note in sorted(notes, key=lambda n: n.relpath):
        body_hash = hashlib.md5(note.body.encode("utf-8", "replace")).hexdigest()
        fm_hash = hashlib.md5(repr(sorted(note.frontmatter.items())).encode()).hexdigest()
        hasher.update(f"{note.relpath}\x00{fm_hash}\x00{body_hash}\n".encode())
    return "sha256:" + hasher.hexdigest()[:16]


def analyze_vault(
    notes: list[Note],
    vault_path: Path,
    *,
    resolution: ResolutionReport | None = None,
    validation: ValidationResult | None = None,
    perf: dict[str, object] | None = None,
    generated_at: str | None = None,
    vault_version: str | None = None,
) -> VaultHealthReport:
    """Run all seven health checks and aggregate findings.

    ``resolution`` and ``validation`` may be supplied by the caller (already timed) to
    avoid recomputation; otherwise they are computed here.
    """
    if resolution is None:
        resolution = RelationshipResolver(notes).resolve_all()
    if validation is None:
        validation = validate_notes(notes)

    findings: list[HealthFinding] = []
    findings += _missing_frontmatter(notes)
    findings += _duplicate_ids(notes)
    findings += _orphan_notes(notes, resolution)
    findings += _broken_wikilinks(resolution)
    findings += _invalid_schemas(validation)
    findings += _missing_aliases(notes)
    findings += _circular_references(notes, resolution)

    return VaultHealthReport(
        vault_path=str(vault_path),
        note_count=len(notes),
        is_obsidian_vault=is_obsidian_vault(vault_path),
        findings=tuple(sorted(findings)),
        perf=perf,
        generated_at=generated_at,
        vault_version=vault_version,
    )


def _missing_frontmatter(notes: list[Note]) -> list[HealthFinding]:
    return [
        HealthFinding(
            HealthCategory.MISSING_FRONTMATTER, Severity.WARNING, n.relpath,
            "Note has no YAML frontmatter.",
        )
        for n in notes if not n.has_frontmatter
    ]


def _duplicate_ids(notes: list[Note]) -> list[HealthFinding]:
    by_id: dict[str, list[str]] = {}
    for n in notes:
        if n.id:
            by_id.setdefault(n.id, []).append(n.relpath)
    findings: list[HealthFinding] = []
    for note_id, paths in by_id.items():
        if len(paths) > 1:
            for p in sorted(paths):
                findings.append(
                    HealthFinding(
                        HealthCategory.DUPLICATE_ID, Severity.ERROR, p,
                        f"Duplicate id '{note_id}' shared by {len(paths)} notes.",
                    )
                )
    return findings


def _orphan_notes(notes: list[Note], resolution: ResolutionReport) -> list[HealthFinding]:
    connected: set[str] = set()
    for e in resolution.edges:
        connected.add(e.source)
        connected.add(e.target_relpath)
    return [
        HealthFinding(
            HealthCategory.ORPHAN_NOTE, Severity.WARNING, n.relpath,
            "Orphan note: no resolved incoming or outgoing links.",
        )
        for n in notes if n.relpath not in connected
    ]


def _broken_wikilinks(resolution: ResolutionReport) -> list[HealthFinding]:
    findings: list[HealthFinding] = []
    for u in resolution.unresolved:
        findings.append(
            HealthFinding(
                HealthCategory.BROKEN_WIKILINK, Severity.WARNING, u.source,
                f"Unresolved reference '{u.reference}' ({u.origin}).",
            )
        )
    return findings


def _invalid_schemas(validation: ValidationResult) -> list[HealthFinding]:
    findings: list[HealthFinding] = []
    for issue in validation.issues:
        if issue.severity is not Severity.ERROR:
            continue
        # Duplicate-id integrity errors are reported under DUPLICATE_ID; skip here.
        if issue.stage is Stage.INTEGRITY and "Duplicate id" in issue.message:
            continue
        # Policy (secrets) is a separate concern, not a schema problem.
        if issue.stage is Stage.POLICY:
            continue
        findings.append(
            HealthFinding(
                HealthCategory.INVALID_SCHEMA, Severity.ERROR, issue.location,
                f"[{issue.stage.value}] {issue.message}",
            )
        )
    return findings


def _missing_aliases(notes: list[Note]) -> list[HealthFinding]:
    findings: list[HealthFinding] = []
    for n in notes:
        title = n.title
        if not title or not n.has_frontmatter:
            continue
        stem = n.path.stem
        if stem.strip().lower() == title.strip().lower():
            continue
        alias_set = {a.strip().lower() for a in n.aliases}
        if stem.strip().lower() in alias_set:
            continue
        findings.append(
            HealthFinding(
                HealthCategory.MISSING_ALIAS, Severity.INFO, n.relpath,
                f"Filename '{stem}' differs from title '{title}' and no alias covers it.",
            )
        )
    return findings


def _circular_references(
    notes: list[Note], resolution: ResolutionReport
) -> list[HealthFinding]:
    """Detect cycles via Tarjan strongly-connected components (deterministic)."""
    adjacency: dict[str, list[str]] = {n.relpath: [] for n in notes}
    for e in resolution.edges:
        if e.source in adjacency and e.target_relpath in adjacency:
            adjacency[e.source].append(e.target_relpath)
    for k in adjacency:
        adjacency[k] = sorted(set(adjacency[k]))

    index_counter = [0]
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    components: list[list[str]] = []

    def strongconnect(node: str) -> None:
        indices[node] = index_counter[0]
        lowlink[node] = index_counter[0]
        index_counter[0] += 1
        stack.append(node)
        on_stack.add(node)
        for nxt in adjacency[node]:
            if nxt not in indices:
                strongconnect(nxt)
                lowlink[node] = min(lowlink[node], lowlink[nxt])
            elif nxt in on_stack:
                lowlink[node] = min(lowlink[node], indices[nxt])
        if lowlink[node] == indices[node]:
            comp: list[str] = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                comp.append(w)
                if w == node:
                    break
            components.append(comp)

    # Iterative safety for large vaults: raise recursion limit modestly.
    import sys
    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old_limit, len(notes) * 2 + 1000))
    try:
        for node in sorted(adjacency):
            if node not in indices:
                strongconnect(node)
    finally:
        sys.setrecursionlimit(old_limit)

    findings: list[HealthFinding] = []
    self_loops = {e.source for e in resolution.edges if e.source == e.target_relpath}
    for comp in components:
        if len(comp) > 1:
            members = ", ".join(sorted(comp)[:6])
            more = "" if len(comp) <= 6 else f" (+{len(comp) - 6} more)"
            rep = sorted(comp)[0]
            findings.append(
                HealthFinding(
                    HealthCategory.CIRCULAR_REFERENCE, Severity.INFO, rep,
                    f"Circular reference cluster of {len(comp)} notes: {members}{more}.",
                )
            )
        elif comp[0] in self_loops:
            findings.append(
                HealthFinding(
                    HealthCategory.CIRCULAR_REFERENCE, Severity.INFO, comp[0],
                    "Note links to itself.",
                )
            )
    return findings
