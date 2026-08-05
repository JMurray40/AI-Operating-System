"""Safe rendering with text/JSON parity (R7, C25).

Neutralizes active or automatically-fetched content in provider output — HTML/script,
remote images, data/javascript URLs, autolinks, and control characters — before it is
shown. Text and JSON expose the same status, coverage, citations, and limitations; status
is never conveyed by color alone.
"""

from __future__ import annotations

import re

from jarvis_core.conversation.results import TurnResult
from jarvis_core.conversation.snapshot import ContextSnapshot

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]*)\)")
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]*)\)")
_AUTOLINK_RE = re.compile(r"<((?:https?|data|javascript|file):[^>]*)>", re.IGNORECASE)
_BLOCKED_SCHEME_RE = re.compile(r"(?i)\b(?:javascript|data|file|vbscript):[^\s)]*")
_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def sanitize_markdown(text: str) -> str:
    """Defang active/auto-fetched content; keep readable, inert text."""
    text = _CONTROL_RE.sub("", text)
    text = _AUTOLINK_RE.sub(r"[blocked-link \1]", text)
    text = _IMAGE_RE.sub(r"[image: \1]", text)  # never emit a fetchable image reference
    text = _LINK_RE.sub(r"\1 (\2)", text)  # link text with inert URL in parentheses
    text = _BLOCKED_SCHEME_RE.sub("[blocked-scheme]", text)
    text = _HTML_TAG_RE.sub("", text)  # drop any HTML/script tags
    return text


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
def result_dict(turn: TurnResult) -> dict[str, object]:
    return turn.to_dict()


def result_text(turn: TurnResult) -> str:
    a = turn.attempt
    lines: list[str] = []
    lines.append(
        f"Turn {turn.turn_number} | status: {a.status.value} | coverage: {turn.coverage.value}"
    )
    if a.failure is not None:
        lines.append(f"failure: {a.failure.value}")
        if a.message:
            lines.append(f"  {a.message}")
    if a.text is not None:
        lines.append("answer:")
        lines.append(sanitize_markdown(a.text))
    if a.evidence is not None:
        ev = a.evidence
        lines.append(
            f"evidence: {ev.supported_count} supported, "
            f"{ev.model_knowledge_count} model-knowledge, {ev.unknown_count} unknown"
        )
        for lim in ev.limitations:
            lines.append(f"  limitation: {lim}")
    lines.append(
        f"usage: in={a.usage.input_tokens} out={a.usage.output_tokens} "
        f"({a.usage.provenance.value}) | "
        f"cost: {a.cost.amount_usd} {a.cost.currency} ({a.cost.provenance.value})"
    )
    return "\n".join(lines)


__all__ = [
    "manifest_dict",
    "manifest_text",
    "result_dict",
    "result_text",
    "sanitize_markdown",
]
