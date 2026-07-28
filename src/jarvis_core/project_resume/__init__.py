"""v0.4 Read-only Project Resume: deterministic, sourced project briefings.

Built over the released v0.3.1 trust pipeline (authorized view, stable identity, passage
citations, context budget). Read-only and offline; local Git activity is a distinct,
request-scoped, read-only capability (ADR-0018 through ADR-0021).
"""
from __future__ import annotations

from jarvis_core.project_resume.assembler import assemble
from jarvis_core.project_resume.contract import (
    PROJECT_RESUME_CONTRACT_VERSION,
    PROJECT_RESUME_TRACE_VERSION,
    REPOSITORY_ACTIVITY_CONTRACT_VERSION,
)
from jarvis_core.project_resume.render import (
    EXIT_CODES,
    exit_code_for,
    render_json,
    render_text,
)
from jarvis_core.project_resume.request import (
    BudgetRangeError,
    ProjectResumeError,
    ProjectResumeRequest,
    RequestValidationError,
    build_request,
)
from jarvis_core.project_resume.results import (
    BriefingClaim,
    BriefingSection,
    Conflict,
    CoverageSummary,
    EvidenceCitation,
    Limitation,
    Omission,
    ProjectIdentity,
    ProjectResumeResult,
    RepositoryCitation,
)
from jarvis_core.project_resume.trace import ProjectResumeTrace, workspace_fingerprint

__all__ = [
    "EXIT_CODES",
    "PROJECT_RESUME_CONTRACT_VERSION",
    "PROJECT_RESUME_TRACE_VERSION",
    "REPOSITORY_ACTIVITY_CONTRACT_VERSION",
    "BriefingClaim",
    "BriefingSection",
    "BudgetRangeError",
    "Conflict",
    "CoverageSummary",
    "EvidenceCitation",
    "Limitation",
    "Omission",
    "ProjectIdentity",
    "ProjectResumeError",
    "ProjectResumeRequest",
    "ProjectResumeResult",
    "ProjectResumeTrace",
    "RepositoryCitation",
    "RequestValidationError",
    "assemble",
    "build_request",
    "exit_code_for",
    "render_json",
    "render_text",
    "workspace_fingerprint",
]
