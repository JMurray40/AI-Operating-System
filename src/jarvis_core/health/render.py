"""Human-readable rendering of a VaultHealthReport."""
from __future__ import annotations

from jarvis_core.health.models import CATEGORY_LABEL, HealthCategory, VaultHealthReport


def render_text(report: VaultHealthReport) -> str:
    """Render a health report as a human-readable plain-text string."""
    lines: list[str] = []
    status = "HEALTHY" if report.ok else "ISSUES FOUND"
    lines.append("=" * 60)
    lines.append(f"Vault Health Report — {status}")
    lines.append("=" * 60)

    # --- Summary ---
    lines.append("")
    lines.append("SUMMARY")
    lines.append(f"  Vault: {report.vault_path}")
    lines.append(f"  Obsidian vault: {'yes' if report.is_obsidian_vault else 'no'}")
    lines.append(f"  Notes analyzed: {report.note_count}")
    lines.append(
        f"  Findings: {len(report.errors)} error(s), "
        f"{len(report.warnings)} warning(s), {len(report.infos)} info."
    )
    counts = report.counts_by_category()
    if counts:
        lines.append("  By category:")
        for cat in HealthCategory:
            if cat.value in counts:
                lines.append(f"    - {CATEGORY_LABEL[cat]}: {counts[cat.value]}")

    if report.perf:
        durations = report.perf.get("durations_ms", {}) if isinstance(report.perf, dict) else {}
        lines.append("")
        lines.append("PERFORMANCE")
        lines.append(f"  Total notes: {report.perf.get('note_count')}")
        if isinstance(durations, dict):
            for stage, ms in durations.items():
                lines.append(f"  {stage}: {ms} ms")
        lines.append(f"  Total runtime: {report.perf.get('total_ms')} ms")
        lines.append(f"  Throughput: {report.perf.get('notes_per_second')} notes/s")

    # --- Errors ---
    lines.append("")
    lines.append(f"ERRORS ({len(report.errors)})")
    if report.errors:
        for f in report.errors:
            lines.append(f"  [{CATEGORY_LABEL[f.category]}] {f.location}: {f.message}")
    else:
        lines.append("  (none)")

    # --- Warnings ---
    lines.append("")
    lines.append(f"WARNINGS ({len(report.warnings)})")
    if report.warnings:
        for f in report.warnings:
            lines.append(f"  [{CATEGORY_LABEL[f.category]}] {f.location}: {f.message}")
    else:
        lines.append("  (none)")

    # --- Info ---
    if report.infos:
        lines.append("")
        lines.append(f"INFO ({len(report.infos)})")
        for f in report.infos:
            lines.append(f"  [{CATEGORY_LABEL[f.category]}] {f.location}: {f.message}")

    # --- Recommendations ---
    recs = report.recommendations()
    lines.append("")
    lines.append(f"RECOMMENDATIONS ({len(recs)})")
    if recs:
        for i, rec in enumerate(recs, start=1):
            lines.append(f"  {i}. {rec}")
    else:
        lines.append("  (none — vault looks healthy)")

    lines.append("")
    return "\n".join(lines)
