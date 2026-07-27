"""Command-line interface for Jarvis Core (read-only).

Commands:
    jarvis inspect  <path>              Discover and parse notes; print a summary.
    jarvis validate <path>              Validate notes across the five schema stages.
    jarvis load-project "<name>"        Assemble and print a project context package.
    jarvis summarize-project "<name>"   Send the package to a provider (mock) and print.
    jarvis vault-report <path>          Analyze a vault and print a health report.
    jarvis ask "<question>"             Answer a question (offline, deterministic).
    jarvis search "<terms>"             Ranked lexical search with citations.
    jarvis summarize "<name>"           Summarize a project with cited sources.
    jarvis explain "<A>" "<B>"          Explain how two notes are related.

Exit codes:
    0  success / validation OK / answer produced
    1  fatal error (bad path, project not found, validation errors)
    2  completed with warnings, or a query returned no matches
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from jarvis_core.config import Config, LogLevel, OutputFormat, default_fixture_path
from jarvis_core.context.loader import ProjectContextLoader, ProjectNotFoundError
from jarvis_core.context.validator import validate_notes
from jarvis_core.health import analyze_vault, compute_vault_fingerprint, render_text
from jarvis_core.logging_setup import configure_logging
from jarvis_core.metrics import PerfReport, measure, track_memory
from jarvis_core.models.context import ContextPackage
from jarvis_core.models.note import Note
from jarvis_core.models.validation import ValidationResult
from jarvis_core.policy import local_allow_all
from jarvis_core.providers import get_provider
from jarvis_core.query import Intent, QueryAnswer, QueryEngine, QueryTrace
from jarvis_core.relationships import RelationshipResolver
from jarvis_core.relationships.resolver import ResolutionReport
from jarvis_core.repositories import FileSystemKnowledgeRepository

EXIT_OK = 0
EXIT_FATAL = 1
EXIT_WARNINGS = 2


def _build_config(args: argparse.Namespace) -> Config:
    vault = Path(args.path) if getattr(args, "path", None) else default_fixture_path()
    return Config(
        vault_path=vault,
        log_level=LogLevel(args.log_level),
        provider=getattr(args, "provider", "mock"),
        output_format=OutputFormat(getattr(args, "format", "text")),
        max_files=getattr(args, "max_files", 5000),
    )


def _dumps(obj: object) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=False)


# --------------------------------------------------------------------------- inspect
def _cmd_inspect(args: argparse.Namespace) -> int:
    config = _build_config(args)
    repo = FileSystemKnowledgeRepository(config)
    notes = repo.discover()
    total_links = sum(len(n.links) for n in notes)
    total_attach = sum(len(n.attachments) for n in notes)
    parse_errors = [(n.relpath, e) for n in notes for e in n.parse_errors]
    types: dict[str, int] = {}
    for n in notes:
        key = n.raw_type or "(none)"
        types[key] = types.get(key, 0) + 1

    if config.output_format is OutputFormat.JSON:
        print(_dumps({
            "vault": str(repo.root),
            "note_count": len(notes),
            "link_count": total_links,
            "attachment_count": total_attach,
            "types": dict(sorted(types.items())),
            "parse_errors": [{"relpath": r, "error": e} for r, e in parse_errors],
            "notes": [n.relpath for n in notes],
        }))
    else:
        print(f"Vault: {repo.root}")
        print(f"Notes: {len(notes)} | Links: {total_links} | Attachments: {total_attach}")
        print("Types:")
        for t, c in sorted(types.items()):
            print(f"  {c:3d}  {t}")
        if parse_errors:
            print(f"Parse errors ({len(parse_errors)}):")
            for r, e in parse_errors:
                print(f"  {r}: {e}")
    return EXIT_WARNINGS if parse_errors else EXIT_OK


# -------------------------------------------------------------------------- validate
def _print_validation(result: ValidationResult, fmt: OutputFormat) -> None:
    if fmt is OutputFormat.JSON:
        print(_dumps(result.to_dict()))
        return
    print(f"Validation: {'OK' if result.ok else 'FAILED'} "
          f"({len(result.errors)} error(s), {len(result.warnings)} warning(s))")
    for issue in sorted(result.issues):
        print(f"  [{issue.severity.value}] {issue.stage.value} {issue.location}: {issue.message}")


def _cmd_validate(args: argparse.Namespace) -> int:
    config = _build_config(args)
    repo = FileSystemKnowledgeRepository(config)
    notes = repo.discover()
    result = validate_notes(notes)
    _print_validation(result, config.output_format)
    if result.errors:
        return EXIT_FATAL
    if result.warnings:
        return EXIT_WARNINGS
    return EXIT_OK


# ---------------------------------------------------------------------- load-project
def _print_package(package: ContextPackage, fmt: OutputFormat) -> None:
    if fmt is OutputFormat.JSON:
        print(_dumps(package.to_dict()))
        return
    print(f"# {package.project_title}")
    print(f"id: {package.project_id}  status: {package.status}  priority: {package.priority}")
    print(f"goal: {package.goal}")
    print(f"milestone: {package.current_milestone}")
    print(f"\n## Resume\n{package.resume or '(none)'}")
    print(f"\n## Decisions ({len(package.decisions)})")
    for d in package.decisions:
        print(f"  - {d.decision_date or '????-??-??'} {d.title} [{d.status}]")
    print(f"\n## Sessions ({len(package.sessions)})")
    for s in package.sessions:
        print(f"  - {s.session_date or '????-??-??'} {s.title} ({s.provider})")
    print(f"\n## Resources ({len(package.resources)})")
    for r in package.resources:
        print(f"  - {r.title} [{r.resource_type}] -> {r.uri or 'n/a'}")
    print(f"\n## Concepts ({len(package.concepts)})")
    for c in package.concepts:
        print(f"  - {c.title}")
    print(f"\n## Outstanding questions ({len(package.outstanding_questions)})")
    for q in package.outstanding_questions:
        print(f"  - {q}")
    if package.warnings:
        print(f"\n## Warnings ({len(package.warnings)})")
        for w in package.warnings:
            print(f"  - {w}")
    if package.unresolved_references:
        print(f"\n## Unresolved references ({len(package.unresolved_references)})")
        for u in package.unresolved_references:
            print(f"  - {u}")


def _load_package(args: argparse.Namespace) -> tuple[Config, ContextPackage]:
    config = _build_config(args)
    repo = FileSystemKnowledgeRepository(config)
    notes = repo.discover()
    loader = ProjectContextLoader(notes)
    return config, loader.load(args.project)


def _cmd_load_project(args: argparse.Namespace) -> int:
    config, package = _load_package(args)
    _print_package(package, config.output_format)
    return EXIT_WARNINGS if (package.warnings or package.unresolved_references) else EXIT_OK


# ----------------------------------------------------------------- summarize-project
def _cmd_summarize_project(args: argparse.Namespace) -> int:
    config, package = _load_package(args)
    provider = get_provider(config.provider)
    response = provider.summarize(package, model_role=args.model_role)
    if config.output_format is OutputFormat.JSON:
        print(_dumps(response.to_dict()))
    else:
        print(response.summary)
    return EXIT_WARNINGS if (package.warnings or package.unresolved_references) else EXIT_OK


# -------------------------------------------------------------------- vault-report
def _run_pipeline_with_perf(
    config: Config,
) -> tuple[
    FileSystemKnowledgeRepository, list[Note], ResolutionReport, ValidationResult, PerfReport
]:
    """Discover, resolve, and validate with per-stage timing. Returns
    (notes, resolution, validation, PerfReport)."""
    perf = PerfReport()
    repo = FileSystemKnowledgeRepository(config)
    # Timed discovery splits disk_read / metadata_parse / markdown_parse.
    notes = repo.discover(perf)
    perf.note_count = len(notes)
    perf.cache_bytes = repo.total_bytes
    with measure(perf, "graph"):
        resolution = RelationshipResolver(notes).resolve_all()
    perf.graph_nodes = len(notes)
    perf.graph_edges = len(resolution.edges)
    with measure(perf, "validate"):
        validation = validate_notes(notes)
    return repo, notes, resolution, validation, perf


def _cmd_vault_report(args: argparse.Namespace) -> int:
    config = _build_config(args)
    total = PerfReport()
    with track_memory(total, enabled=args.memory), measure(total, "total"):
        repo, notes, resolution, validation, perf = _run_pipeline_with_perf(config)
    perf.record("total", total.durations["total"])
    perf.peak_memory_bytes = total.peak_memory_bytes
    perf.current_memory_bytes = total.current_memory_bytes
    generated_at = None if args.deterministic else (
        datetime.now(timezone.utc).isoformat(timespec="seconds")
    )
    report = analyze_vault(
        notes, repo.root, resolution=resolution, validation=validation,
        perf=perf.to_dict() if args.timing else None,
        generated_at=generated_at,
        vault_version=compute_vault_fingerprint(notes),
    )
    if config.output_format is OutputFormat.JSON:
        rendered = _dumps(report.to_dict())
    else:
        rendered = render_text(report)
    print(rendered)
    # File output is optional and disabled unless --output is given.
    if args.output:
        out_path = Path(args.output)
        out_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"\n(report written to {out_path})", file=sys.stderr)
    if report.errors:
        return EXIT_FATAL
    if report.warnings:
        return EXIT_WARNINGS
    return EXIT_OK


# ---------------------------------------------------------------- query commands
def _engine(args: argparse.Namespace) -> QueryEngine:
    config = _build_config(args)
    repo = FileSystemKnowledgeRepository(config)
    # Existing CLI behavior runs under an explicit local allow-all scope (never an implicit
    # unrestricted bypass); notes with unknown sensitivity still fail closed (ADR-0015).
    return QueryEngine(repo.discover(), scope=local_allow_all(workspace_id="local"))


def _print_answer(answer: QueryAnswer, trace: QueryTrace | None, fmt: OutputFormat) -> None:
    if fmt is OutputFormat.JSON:
        payload = answer.to_dict()
        if trace is not None:
            payload["trace"] = trace.to_dict()
        print(_dumps(payload))
        return
    print(answer.answer)
    if answer.citations:
        print("\nSources:")
        for c in answer.citations:
            rel = (
                f"relative relevance={c.relative_relevance:g}"
                if c.relative_relevance is not None else "relative relevance=n/a"
            )
            loc = c.locator
            print(
                f"  - {c.title} ({c.relpath}:{loc.line_start}-{loc.line_end})  "
                f"[{rel}] {c.reason}"
            )
    if answer.excluded_count:
        print(f"\n({answer.excluded_count} source(s) excluded by policy)")
    if trace is not None:
        print()
        print(trace.render_text())


def _answered_exit(answer: QueryAnswer) -> int:
    answered = bool(answer.citations) or answer.intent is Intent.SUMMARIZE_PROJECT
    return EXIT_OK if answered else EXIT_WARNINGS


def _cmd_ask(args: argparse.Namespace) -> int:
    config = _build_config(args)
    answer, trace = _engine(args).run(args.question, want_trace=args.trace)
    _print_answer(answer, trace, config.output_format)
    return _answered_exit(answer)


def _cmd_search(args: argparse.Namespace) -> int:
    config = _build_config(args)
    answer = _engine(args).search(args.query, limit=args.limit)
    _print_answer(answer, None, config.output_format)
    return EXIT_OK if answer.citations else EXIT_WARNINGS


def _cmd_summarize(args: argparse.Namespace) -> int:
    config = _build_config(args)
    answer = _engine(args).summarize(args.name)
    _print_answer(answer, None, config.output_format)
    return EXIT_OK if answer.citations else EXIT_WARNINGS


def _cmd_explain(args: argparse.Namespace) -> int:
    config = _build_config(args)
    answer = _engine(args).explain(args.left, args.right)
    _print_answer(answer, None, config.output_format)
    return EXIT_OK if answer.citations else EXIT_WARNINGS


# ------------------------------------------------------------------------------ main
def _add_common(parser: argparse.ArgumentParser, *, with_path: bool) -> None:
    if with_path:
        parser.add_argument(
            "path", nargs="?", default=None,
            help="Vault/fixture directory (defaults to bundled sample fixtures).",
        )
    parser.add_argument("--log-level", default="INFO",
                        choices=[lvl.value for lvl in LogLevel])
    parser.add_argument("--format", default="text",
                        choices=[f.value for f in OutputFormat])
    parser.add_argument("--max-files", type=int, default=5000)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jarvis",
        description="Read-only Obsidian-vault context assembly for the AI Operating System.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_inspect = sub.add_parser("inspect", help="Discover and parse notes; print a summary.")
    _add_common(p_inspect, with_path=True)
    p_inspect.set_defaults(func=_cmd_inspect)

    p_validate = sub.add_parser("validate", help="Validate notes across schema stages.")
    _add_common(p_validate, with_path=True)
    p_validate.set_defaults(func=_cmd_validate)

    p_load = sub.add_parser("load-project", help="Assemble a project context package.")
    p_load.add_argument("project", help="Project name, title, alias, or id.")
    p_load.add_argument("--path", default=None, help="Vault/fixture directory.")
    _add_common(p_load, with_path=False)
    p_load.set_defaults(func=_cmd_load_project)

    p_sum = sub.add_parser("summarize-project", help="Send a project package to a provider.")
    p_sum.add_argument("project", help="Project name, title, alias, or id.")
    p_sum.add_argument("--path", default=None, help="Vault/fixture directory.")
    p_sum.add_argument("--provider", default="mock", help="Provider name (only 'mock').")
    p_sum.add_argument("--model-role", default="fast",
                       help="Role alias (coding, research, fast, private, vision).")
    _add_common(p_sum, with_path=False)
    p_sum.set_defaults(func=_cmd_summarize_project)

    p_report = sub.add_parser(
        "vault-report",
        help="Analyze a vault and print a human-readable health report.",
    )
    _add_common(p_report, with_path=True)
    p_report.add_argument(
        "--output", default=None,
        help="Optional file to also write the report to (disabled by default).",
    )
    p_report.add_argument(
        "--timing", dest="timing", action="store_true", default=True,
        help="Include performance metrics (default on).",
    )
    p_report.add_argument(
        "--no-timing", dest="timing", action="store_false",
        help="Omit performance metrics.",
    )
    p_report.add_argument(
        "--memory", dest="memory", action="store_true", default=False,
        help="Track peak memory via tracemalloc (adds overhead; off by default).",
    )
    p_report.add_argument(
        "--deterministic", dest="deterministic", action="store_true", default=False,
        help="Omit the wall-clock timestamp for reproducible snapshots.",
    )
    p_report.set_defaults(func=_cmd_vault_report)

    p_ask = sub.add_parser(
        "ask",
        help="Answer a question from the vault (offline, deterministic; no AI provider).",
    )
    p_ask.add_argument("question", help="A natural-language question about the vault.")
    p_ask.add_argument("--path", default=None, help="Vault/fixture directory.")
    p_ask.add_argument(
        "--trace", dest="trace", action="store_true", default=False,
        help="Show how the answer was produced (intent, ranking, context, timing).",
    )
    _add_common(p_ask, with_path=False)
    p_ask.set_defaults(func=_cmd_ask)

    p_search = sub.add_parser("search", help="Ranked lexical search across all notes.")
    p_search.add_argument("query", help="Search terms.")
    p_search.add_argument("--path", default=None, help="Vault/fixture directory.")
    p_search.add_argument("--limit", type=int, default=20, help="Max results (default 20).")
    _add_common(p_search, with_path=False)
    p_search.set_defaults(func=_cmd_search)

    p_summarize = sub.add_parser("summarize", help="Summarize a project with cited sources.")
    p_summarize.add_argument("name", help="Project name, title, alias, or id.")
    p_summarize.add_argument("--path", default=None, help="Vault/fixture directory.")
    _add_common(p_summarize, with_path=False)
    p_summarize.set_defaults(func=_cmd_summarize)

    p_explain = sub.add_parser("explain", help="Explain how two notes are related.")
    p_explain.add_argument("left", help="First note name/title/alias/id.")
    p_explain.add_argument("right", help="Second note name/title/alias/id.")
    p_explain.add_argument("--path", default=None, help="Vault/fixture directory.")
    _add_common(p_explain, with_path=False)
    p_explain.set_defaults(func=_cmd_explain)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging(LogLevel(args.log_level))
    try:
        return int(args.func(args))
    except (ProjectNotFoundError, FileNotFoundError, NotADirectoryError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_FATAL
    except NotImplementedError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_FATAL


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
