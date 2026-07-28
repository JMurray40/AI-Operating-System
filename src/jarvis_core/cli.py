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
    jarvis resume "<selector>"          Assemble a deterministic, sourced project briefing.
    jarvis resume-doctor                Diagnose the environment and rebuild derived state.

Exit codes:
    0  success / validation OK / answer produced / complete supported briefing
    1  fatal error (bad path, project not found, validation errors) / internal failure
    2  completed with warnings, a query returned no matches, or a partial briefing
    3  resume: ambiguous project selector (candidates shown, none chosen)
    4  resume: project not found (no substitute)
    5  resume: invalid input or identity
    6  resume: policy error
    7  resume: budget error
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
from jarvis_core.policy.errors import PolicyError
from jarvis_core.project_resume import (
    ProjectResumeError,
    assemble,
    build_request,
    exit_code_for,
)
from jarvis_core.project_resume import (
    render_json as render_resume_json,
)
from jarvis_core.project_resume import (
    render_text as render_resume_text,
)
from jarvis_core.project_resume.contract import (
    DEFAULT_EVIDENCE_TOKEN_BUDGET,
    DEFAULT_OUTPUT_TOKEN_BUDGET,
)
from jarvis_core.project_resume.diagnostics import (
    STATUS_FAIL,
    STATUS_OK,
    run_diagnostics,
)
from jarvis_core.project_resume.identity import resolve_project
from jarvis_core.project_resume.local_git import (
    LocalGitRepositoryActivityAdapter,
    SubprocessProcessRunner,
)
from jarvis_core.project_resume.repository_activity import RepositoryActivityGrant
from jarvis_core.project_resume.request import (
    BudgetRangeError,
    RequestValidationError,
    parse_evaluation_time,
)
from jarvis_core.providers import get_provider
from jarvis_core.query import QueryAnswer, QueryEngine, QueryTrace
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
    # source_root enables current-bytes citation validation at emission (AC-03R2).
    return QueryEngine(
        repo.discover(), scope=local_allow_all(workspace_id="local"), source_root=repo.root
    )


def _print_answer(answer: QueryAnswer, trace: QueryTrace | None, fmt: OutputFormat) -> None:
    if fmt is OutputFormat.JSON:
        payload = answer.to_dict()
        if trace is not None:
            payload["trace"] = trace.to_dict()
        print(_dumps(payload))
        return
    print(answer.answer)
    supported = answer.supported_citations()
    incomplete = answer.incomplete_citations()
    if supported:
        print("\nSources (supporting passages):")
        for c in supported:
            rel = (
                f"relative relevance={c.relative_relevance:g}"
                if c.relative_relevance is not None else "relative relevance=n/a"
            )
            loc = c.locator
            print(
                f"  - {c.title} ({c.relpath}:{loc.line_start}-{loc.line_end})  "
                f"[{rel}] {c.reason}"
            )
    if incomplete:
        print("\nEvidence coverage incomplete — the following sources were referenced, but "
              "no claim-supporting passage was found:")
        for c in incomplete:
            print(f"  - {c.title} ({c.relpath})  [no supporting passage] {c.reason}")
    cov = answer.citation_coverage()
    print(f"\nCoverage: {cov['label']} "
          f"({cov['supported']} supported, {cov['incomplete']} incomplete)")
    if answer.excluded_count:
        print(f"({answer.excluded_count} source(s) excluded by policy)")
    if trace is not None:
        print()
        print(trace.render_text())


def _answered_exit(answer: QueryAnswer) -> int:
    # Only a supported (passage-backed) citation counts as an evidence-backed answer; an
    # answer with only incomplete references is not fully evidence-backed (AC-03R3-02).
    return EXIT_OK if answer.supported_citations() else EXIT_WARNINGS


def _cmd_ask(args: argparse.Namespace) -> int:
    config = _build_config(args)
    answer, trace = _engine(args).run(args.question, want_trace=args.trace)
    _print_answer(answer, trace, config.output_format)
    return _answered_exit(answer)


def _cmd_search(args: argparse.Namespace) -> int:
    config = _build_config(args)
    answer = _engine(args).search(args.query, limit=args.limit)
    _print_answer(answer, None, config.output_format)
    return EXIT_OK if answer.supported_citations() else EXIT_WARNINGS


def _cmd_summarize(args: argparse.Namespace) -> int:
    config = _build_config(args)
    answer = _engine(args).summarize(args.name)
    _print_answer(answer, None, config.output_format)
    return EXIT_OK if answer.supported_citations() else EXIT_WARNINGS


def _cmd_explain(args: argparse.Namespace) -> int:
    config = _build_config(args)
    answer = _engine(args).explain(args.left, args.right)
    _print_answer(answer, None, config.output_format)
    return EXIT_OK if answer.supported_citations() else EXIT_WARNINGS


# ------------------------------------------------------------ project resume (v0.4)
def _cmd_resume(args: argparse.Namespace) -> int:
    """Assemble and print a deterministic, sourced Project Resume briefing (read-only).

    Output is stdout only (no product output-file path). Repository activity is denied by
    default and only enabled when BOTH ``--include-repository-activity`` and
    ``--repository-root`` are supplied; the grant binds that root to the exactly-selected
    project for this one invocation. Build-time failures map to the documented resume exit
    codes rather than a traceback.
    """
    config = _build_config(args)
    repo = FileSystemKnowledgeRepository(config)
    notes = repo.discover()
    scope = local_allow_all(workspace_id="local")

    # A root supplied without the activation flag does nothing; the flag without a root is
    # invalid input (ADR-0021, brief §12).
    if args.include_repository_activity and not args.repository_root:
        print(
            "error: --include-repository-activity requires --repository-root",
            file=sys.stderr,
        )
        return exit_code_for("invalid_identity")

    grant = None
    repository_port = None
    if args.include_repository_activity:
        # Bind the grant to the exactly-selected project's stable identity; a non-selection
        # yields a terminal result before the port is ever consulted.
        selection = resolve_project(notes, scope, args.selector)
        project_id = (
            selection.identity.source_id if selection.identity is not None else args.selector
        )
        grant = RepositoryActivityGrant(
            workspace_id="local",
            project_id=project_id,
            repository_root=Path(args.repository_root),
        )
        repository_port = LocalGitRepositoryActivityAdapter(SubprocessProcessRunner())

    evaluation_time = args.as_of or datetime.now(timezone.utc).isoformat()
    evidence_budget = (
        args.evidence_budget if args.evidence_budget is not None
        else DEFAULT_EVIDENCE_TOKEN_BUDGET
    )
    output_budget = (
        args.output_budget if args.output_budget is not None else DEFAULT_OUTPUT_TOKEN_BUDGET
    )

    try:
        request = build_request(
            workspace_id="local",
            project_selector=args.selector,
            authorization_scope=scope,
            source_root=repo.root,
            evaluation_time=evaluation_time,
            evidence_token_budget=evidence_budget,
            output_token_budget=output_budget,
            repository_activity_grant=grant,
            trace_requested=args.trace,
        )
    except BudgetRangeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exit_code_for("budget_error")
    except PolicyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exit_code_for("policy_error")
    except (RequestValidationError, ProjectResumeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exit_code_for("invalid_identity")

    result = assemble(notes, request, repository_port=repository_port)
    if config.output_format is OutputFormat.JSON:
        print(render_resume_json(result))
    else:
        print(render_resume_text(result))
    return exit_code_for(result.status)


def _cmd_resume_doctor(args: argparse.Namespace) -> int:
    """Diagnose the environment and rebuild derived state (read-only; brief §21).

    Reports the runtime, vault readability, the derived-state rebuild (authorized view + lexical
    index + relationship graph reconstructed from canonical sources, never persisted), Git
    availability and version, and — when ``--repository-root`` is given — a redacted probe of
    that root through the local read-only Git adapter. Exit: 0 healthy, 2 warnings, 1 failure.
    """
    config = _build_config(args)
    repo = FileSystemKnowledgeRepository(config)
    notes = repo.discover()
    scope = local_allow_all(workspace_id="local")
    repository_root = Path(args.repository_root) if args.repository_root else None
    try:
        evaluation_time = parse_evaluation_time(args.as_of) if args.as_of else None
    except RequestValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_FATAL

    report = run_diagnostics(
        notes, scope=scope, source_root=repo.root,
        repository_root=repository_root, evaluation_time=evaluation_time,
    )
    if config.output_format is OutputFormat.JSON:
        print(_dumps(report.to_dict()))
    else:
        print(report.render_text())

    if report.overall_status == STATUS_OK:
        return EXIT_OK
    if report.overall_status == STATUS_FAIL:
        return EXIT_FATAL
    return EXIT_WARNINGS


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

    p_resume = sub.add_parser(
        "resume",
        help="Assemble a deterministic, sourced project briefing (read-only, offline).",
    )
    p_resume.add_argument(
        "selector", help="Project selector: canonical id, title, alias, or filename stem."
    )
    p_resume.add_argument("--path", default=None, help="Vault/fixture directory.")
    p_resume.add_argument(
        "--trace", dest="trace", action="store_true", default=False,
        help="Include a non-disclosing trace (versions, fingerprint, channels, timings).",
    )
    p_resume.add_argument(
        "--as-of", dest="as_of", default=None,
        help="Explicit ISO-8601 UTC evaluation time for staleness/determinism (default: now).",
    )
    p_resume.add_argument(
        "--evidence-budget", dest="evidence_budget", type=int, default=None,
        help="Evidence token budget (256..32000; default 8000).",
    )
    p_resume.add_argument(
        "--output-budget", dest="output_budget", type=int, default=None,
        help="Output token budget (256..16000; default 4000).",
    )
    p_resume.add_argument(
        "--include-repository-activity", dest="include_repository_activity",
        action="store_true", default=False,
        help="Enable local read-only Git activity (requires --repository-root).",
    )
    p_resume.add_argument(
        "--repository-root", dest="repository_root", default=None,
        help="Local Git repository root to bind to the selected project for this invocation.",
    )
    _add_common(p_resume, with_path=False)
    p_resume.set_defaults(func=_cmd_resume)

    p_doctor = sub.add_parser(
        "resume-doctor",
        help="Diagnose the environment and rebuild derived state (read-only).",
    )
    p_doctor.add_argument("--path", default=None, help="Vault/fixture directory.")
    p_doctor.add_argument(
        "--repository-root", dest="repository_root", default=None,
        help="Optional local Git repository root to probe (redacted diagnosis).",
    )
    p_doctor.add_argument(
        "--as-of", dest="as_of", default=None,
        help="Explicit ISO-8601 UTC time for the repository staleness probe (default: now).",
    )
    _add_common(p_doctor, with_path=False)
    p_doctor.set_defaults(func=_cmd_resume_doctor)

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
