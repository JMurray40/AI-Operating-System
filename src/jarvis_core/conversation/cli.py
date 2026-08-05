"""`jarvis chat` CLI surface (H07 §9, §15). Session-only; text/JSON parity.

Two modes over the same versioned application API:

* scripted (default) — one prepared turn per invocation. Without ``--approve`` it prints
  the context manifest and stops (no dispatch, no network). Remote dispatch requires an
  explicit ``--approve <digest>`` value bound to the exact prepared snapshot — approval is
  never inferred from a flag default, pipe, environment, or workspace setting.
* interactive (``--interactive``) — an in-process REPL holding one session in memory.

Exit codes are the conversation contract's, never a raw provider status. Only the mock
adapter is dispatchable in this cycle; the Google surface is preparable but dispatch stays
unavailable until the separately authorized real-provider activation (WP4).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from jarvis_core.config import Config
from jarvis_core.conversation.application import ConversationApplication
from jarvis_core.conversation.contract import (
    ConversationError,
    ExitCode,
    exit_code_for_failure,
)
from jarvis_core.conversation.render import (
    manifest_dict,
    manifest_text,
    result_dict,
    result_text,
)
from jarvis_core.conversation.request import PrepareTurnRequest, mock_profile
from jarvis_core.conversation.session import Session
from jarvis_core.policy import local_allow_all
from jarvis_core.providers.conversation import MockConversationProvider
from jarvis_core.providers.google_gemini import google_gemini_profile
from jarvis_core.repositories import FileSystemKnowledgeRepository

_PROVIDERS = ("mock", "google")


def add_chat_subparser(sub: argparse._SubParsersAction) -> None:
    """Register the ``chat`` subcommand on the shared parser (additive)."""
    p = sub.add_parser(
        "chat",
        help="Visible-context conversation (session-only; prepare, approve, dispatch).",
    )
    p.add_argument("message", nargs="?", default=None, help="The user turn text (scripted mode).")
    p.add_argument("--path", default=None, help="Vault/fixture directory.")
    p.add_argument("--project", default=None, help="Optional exact project selector (ADR-0018).")
    p.add_argument(
        "--provider", default="mock", choices=_PROVIDERS, help="Destination (default mock)."
    )
    p.add_argument("--remove", default=None, help="Comma-separated context item ids to remove.")
    p.add_argument(
        "--approve",
        dest="approve",
        default=None,
        help="Approve dispatch by supplying the EXACT prepared snapshot digest.",
    )
    p.add_argument(
        "--as-of",
        dest="as_of",
        default=None,
        help="Explicit ISO-8601 UTC evaluation time (use the same value to reproduce a digest).",
    )
    p.add_argument(
        "--session-id",
        dest="session_id",
        default=None,
        help="Pin the session id so the inspect-then-approve digest is reproducible.",
    )
    p.add_argument("--trace", action="store_true", default=False, help="Include the safe trace.")
    p.add_argument("--interactive", action="store_true", default=False, help="Run the REPL.")
    p.add_argument("--format", default="text", choices=["text", "json"])
    p.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    p.set_defaults(func=run_chat)


def _emit(payload: dict[str, object], text: str, fmt: str) -> None:
    if fmt == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(text)


def _evaluation_time(as_of: str | None) -> datetime:
    if as_of is None:
        return datetime.now(timezone.utc)
    value = datetime.fromisoformat(as_of)
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _load(args: argparse.Namespace) -> tuple[list, Path]:
    vault = Path(args.path) if args.path else None
    config = Config(vault_path=vault) if vault else Config()
    repo = FileSystemKnowledgeRepository(config)
    return repo.discover(), Path(repo.root)


def _profile(provider: str) -> object:
    return google_gemini_profile() if provider == "google" else mock_profile()


def _make_request(args: argparse.Namespace, session: Session, root: Path, text: str):  # type: ignore[no-untyped-def]
    ceiling = "internal"
    return PrepareTurnRequest(
        request_id=f"cli-{session.peek_turn_number()}",
        session_id=session.session_id,
        workspace_id=session.workspace_id,
        scope=local_allow_all(workspace_id=session.workspace_id, max_sensitivity=ceiling),
        source_root=root,
        user_text=text,
        provider_profile=_profile(args.provider),  # type: ignore[arg-type]
        project_selector=args.project,
        evaluation_time=_evaluation_time(args.as_of),
        want_trace=args.trace,
    )


def run_chat(args: argparse.Namespace) -> int:
    """Entry point for ``jarvis chat``. Returns a conversation exit code."""
    try:
        notes, root = _load(args)
    except (FileNotFoundError, NotADirectoryError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return int(ExitCode.INTERNAL_ERROR)

    app = ConversationApplication()
    session = app.create_session("local", session_id=args.session_id)

    if args.interactive:
        return _run_interactive(app, session, args, notes, root)

    if not args.message:
        print(
            "error: a message is required in scripted mode (or use --interactive)",
            file=sys.stderr,
        )
        return int(ExitCode.VALIDATION_FAILED)

    try:
        return _run_scripted(app, session, args, notes, root)
    except ConversationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return int(exit_code_for_failure(exc.failure_class))


def _run_scripted(
    app: ConversationApplication,
    session: Session,
    args: argparse.Namespace,
    notes: list,
    root: Path,
) -> int:
    request = _make_request(args, session, root, args.message)
    # prepare-turn credential preflight: the CLI wires no credential provider, so a REMOTE
    # destination fails closed here (no key read, no network) — dispatch stays unavailable.
    snapshot = app.prepare_turn(session, request, notes)

    if args.remove:
        for item_id in [x.strip() for x in args.remove.split(",") if x.strip()]:
            snapshot = app.remove_context(session, item_id)

    if not args.approve:
        # Inspect/prepare only: print the manifest and stop. No dispatch, no network.
        _emit(manifest_dict(snapshot), manifest_text(snapshot), args.format)
        return int(ExitCode.SUCCESS)

    if args.approve != snapshot.digest:
        print(
            "error: --approve value does not match the prepared snapshot digest; "
            "re-run without --approve to view the current digest (use the same --as-of).",
            file=sys.stderr,
        )
        return int(ExitCode.VALIDATION_FAILED)

    if args.provider != "mock":
        # The Google surface is preparable but not dispatchable until WP4 activation.
        print(
            "error: real-provider dispatch is not activated in this build; "
            "the mock adapter is the only dispatchable destination.",
            file=sys.stderr,
        )
        return int(ExitCode.PROVIDER_UNAVAILABLE)

    app.approve(session, actor="cli-user", now=request.evaluation_time)
    turn = app.dispatch_turn(session, MockConversationProvider(), now=request.evaluation_time)
    payload = result_dict(turn)
    if args.trace:
        payload["trace"] = session.trace.to_dict()
    _emit(payload, result_text(turn), args.format)
    if turn.attempt.failure is not None:
        return int(exit_code_for_failure(turn.attempt.failure))
    return int(ExitCode.SUCCESS)


_HELP = (
    "commands: /prepare <text>, /manifest, /remove <id>, /approve, /dispatch, "
    "/cancel, /retry, /history, /trace, /reset, /help, /quit"
)


def _run_interactive(
    app: ConversationApplication,
    session: Session,
    args: argparse.Namespace,
    notes: list,
    root: Path,
) -> int:
    print("jarvis chat (session-only). " + _HELP)
    while True:
        try:
            line = input("chat> ").strip()
        except EOFError:
            break
        if not line:
            continue
        try:
            if line in ("/quit", "/exit"):
                break
            elif line == "/help":
                print(_HELP)
            elif line.startswith("/prepare "):
                req = _make_request(args, session, root, line[len("/prepare ") :].strip())
                snap = app.prepare_turn(session, req, notes)
                print(manifest_text(snap))
            elif line == "/manifest":
                prepared = session.pending_prepared
                print(manifest_text(prepared.snapshot) if prepared else "(nothing prepared)")
            elif line.startswith("/remove "):
                snap = app.remove_context(session, line[len("/remove ") :].strip())
                print(manifest_text(snap))
            elif line == "/approve":
                if session.pending_prepared is None:
                    print("(nothing prepared)")
                else:
                    app.approve(session, actor="cli-user")
                    print("approved: " + session.pending_prepared.snapshot.digest)
            elif line == "/dispatch":
                if args.provider != "mock":
                    print("real-provider dispatch is not activated (mock only)")
                else:
                    turn = app.dispatch_turn(session, MockConversationProvider())
                    print(result_text(turn))
            elif line == "/retry":
                turn = app.retry_attempt(session, MockConversationProvider())
                print(result_text(turn))
            elif line == "/history":
                for row in app.inspect_history(session):
                    print(row)
            elif line == "/trace":
                print(json.dumps(session.trace.to_dict(), indent=2))
            elif line == "/reset":
                app.reset_session(session)
                print("session reset")
            elif line == "/cancel":
                print("no in-flight attempt to cancel (synchronous CLI)")
            else:
                print(_HELP)
        except ConversationError as exc:
            print(f"error: {exc}")
    return int(ExitCode.SUCCESS)


__all__ = ["add_chat_subparser", "run_chat"]
