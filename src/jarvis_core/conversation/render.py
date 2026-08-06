"""Safe rendering with text/JSON parity (R7, C25).

Neutralizes active or automatically-fetched content in provider output — HTML/script,
remote images, data/javascript URLs, autolinks, and control characters — before it is
shown. Text and JSON expose the same status, coverage, citations, and limitations; status
is never conveyed by color alone.
"""

from __future__ import annotations

from jarvis_core.conversation.presentation import present
from jarvis_core.conversation.results import TurnResult
from jarvis_core.conversation.sanitize import sanitize_markdown
from jarvis_core.conversation.snapshot import ContextSnapshot


# ------------------------------------------------------------------ manifest
def manifest_dict(snapshot: ContextSnapshot) -> dict[str, object]:
    return snapshot.to_dict()


def manifest_text(snapshot: ContextSnapshot) -> str:
    lines: list[str] = []
    lines.append(f"Context manifest for request {snapshot.request_id}")
    lines.append(f"snapshot digest: {snapshot.digest}")
    pol = snapshot.provider_policy
    dest = "local (no egress)" if not pol.is_remote else f"{pol.provider_id} @ {pol.host}"
    lines.append(f"destination: {dest} | model: {pol.model_id} | op: {pol.operation}")
    acct = snapshot.budget_accounting
    lines.append(
        f"items: {acct.get('items_included')} included, "
        f"{acct.get('items_omitted')} omitted | "
        f"context tokens: {acct.get('context_tokens_used')}/{acct.get('context_token_budget')}"
    )
    if snapshot.assumptions:
        lines.append("assumptions:")
        for a in snapshot.assumptions:
            lines.append(f"  - {a.get('trigger')} -> {a.get('resolved_to')} [{a.get('status')}]")
    lines.append("context items:")
    if not snapshot.items:
        lines.append("  (none authorized for this turn)")
    for item in snapshot.items:
        lines.append(
            f"  [{item.item_id}] {item.title} ({item.relpath}) "
            f"lines {item.line_start}-{item.line_end} "
            f"| sensitivity={item.sensitivity} | tokens={item.token_count}"
        )
        lines.append(f"        reason: {item.reason}")
    if snapshot.safe_omissions:
        lines.append("omitted (budget):")
        for om in snapshot.safe_omissions:
            lines.append(f"  - {om.get('title')} ({om.get('reason')})")
    excluded = snapshot.authorization_summary.get("excluded_count", 0)
    lines.append(f"excluded (unauthorized, aggregate only): {excluded}")
    return "\n".join(lines)


# ------------------------------------------------------------------ result
# The single sanitized presentation object drives BOTH surfaces (AC-05-05).
def result_dict(turn: TurnResult) -> dict[str, object]:
    return present(turn).to_dict()


def result_text(turn: TurnResult) -> str:
    return present(turn).to_text()


__all__ = [
    "manifest_dict",
    "manifest_text",
    "result_dict",
    "result_text",
    "sanitize_markdown",
]
