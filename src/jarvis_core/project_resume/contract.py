"""Versioned contract constants and shared enumerations for v0.4 Project Resume.

These are deliberately separate from the v0.3.1 query contract versions: Project Resume
adds its own result/trace/repository-activity contract versions (ADR-0020, ADR-0021) and
never conflates them with ``jarvis.query.v0.3.1``.
"""
from __future__ import annotations

# ---------------------------------------------------------------- contract versions
PROJECT_RESUME_CONTRACT_VERSION = "jarvis.project-resume.v0.4.0"
PROJECT_RESUME_TRACE_VERSION = "jarvis.project-resume-trace.v0.4.0"
REPOSITORY_ACTIVITY_CONTRACT_VERSION = "jarvis.repository-activity.local-git.v0.4.0"

# ---------------------------------------------------------------- budgets (ADR-0020 §11)
DEFAULT_EVIDENCE_TOKEN_BUDGET = 8_000
DEFAULT_OUTPUT_TOKEN_BUDGET = 4_000
DEFAULT_TRACE_TOKEN_SUB_BUDGET = 1_000  # inside, not in addition to, the output budget

EVIDENCE_BUDGET_MIN = 256
EVIDENCE_BUDGET_MAX = 32_000
OUTPUT_BUDGET_MIN = 256
OUTPUT_BUDGET_MAX = 16_000

# ---------------------------------------------------------------- result status
STATUS_COMPLETE = "complete"
STATUS_PARTIAL = "partial"
STATUS_AMBIGUOUS = "ambiguous"
STATUS_NOT_FOUND = "not_found"
STATUS_INVALID_IDENTITY = "invalid_identity"
STATUS_POLICY_ERROR = "policy_error"
STATUS_BUDGET_ERROR = "budget_error"
STATUS_FAILED = "failed"

RESULT_STATUSES: frozenset[str] = frozenset(
    {
        STATUS_COMPLETE,
        STATUS_PARTIAL,
        STATUS_AMBIGUOUS,
        STATUS_NOT_FOUND,
        STATUS_INVALID_IDENTITY,
        STATUS_POLICY_ERROR,
        STATUS_BUDGET_ERROR,
        STATUS_FAILED,
    }
)

# ---------------------------------------------------------------- identity tiers (ADR-0018)
TIER_CANONICAL_ID = "canonical_id"
TIER_TITLE = "title"
TIER_ALIAS = "alias"
TIER_FILENAME_STEM = "filename_stem"

IDENTITY_TIERS: tuple[str, ...] = (TIER_CANONICAL_ID, TIER_TITLE, TIER_ALIAS, TIER_FILENAME_STEM)

# ---------------------------------------------------------------- claim vocab (ADR-0019/0020)
KIND_FACT = "fact"
KIND_INFERENCE = "inference"
KIND_UNKNOWN = "unknown"

SUPPORT_SUPPORTED = "supported"
SUPPORT_INCOMPLETE = "incomplete"
SUPPORT_CONFLICTING = "conflicting"

# Authority classes, strongest first (ADR-0019). Lower index == higher authority.
AUTHORITY_ACCEPTED_DECISION = "accepted_decision"
AUTHORITY_CURRENT_STATE = "current_state"
AUTHORITY_CURRENT_PRIORITY = "current_priority"
AUTHORITY_SESSION_SUMMARY = "session_summary"
AUTHORITY_DRAFT = "draft"
AUTHORITY_INFERRED = "inferred"

AUTHORITY_ORDER: tuple[str, ...] = (
    AUTHORITY_ACCEPTED_DECISION,
    AUTHORITY_CURRENT_STATE,
    AUTHORITY_CURRENT_PRIORITY,
    AUTHORITY_SESSION_SUMMARY,
    AUTHORITY_DRAFT,
    AUTHORITY_INFERRED,
)

TEMPORAL_DATED = "dated"
TEMPORAL_UNDATED = "undated"
TEMPORAL_STALE = "stale"

# ---------------------------------------------------------------- coverage labels
COVERAGE_COMPLETE = "complete"
COVERAGE_PARTIAL = "partial"
COVERAGE_INCOMPLETE = "incomplete"
COVERAGE_NONE = "none"

# ---------------------------------------------------------------- section keys (fixed order)
SECTION_PROJECT = "project"
SECTION_CURRENT_STATE = "current_state"
SECTION_NEXT_ACTION = "next_action"
SECTION_DECISIONS = "accepted_decisions"
SECTION_SESSIONS = "recent_sessions"
SECTION_OPEN_ITEMS = "open_tasks_and_questions"
SECTION_RESOURCES = "resources"
SECTION_REPOSITORY = "repository_activity"
SECTION_CONFLICTS = "conflicts_staleness_missing_context"
SECTION_COVERAGE = "evidence_coverage_and_omissions"

SECTION_ORDER: tuple[tuple[str, str], ...] = (
    (SECTION_PROJECT, "Project"),
    (SECTION_CURRENT_STATE, "Current state"),
    (SECTION_NEXT_ACTION, "Next action and priorities"),
    (SECTION_DECISIONS, "Accepted decisions"),
    (SECTION_SESSIONS, "Recent sessions"),
    (SECTION_OPEN_ITEMS, "Open tasks and questions"),
    (SECTION_RESOURCES, "Resources"),
    (SECTION_REPOSITORY, "Repository activity"),
    (SECTION_CONFLICTS, "Conflicts, staleness, and missing context"),
    (SECTION_COVERAGE, "Evidence coverage and omissions"),
)

EMPTY_SECTION_NOTE = "no supported evidence available"

# ---------------------------------------------------------------- discovery channels (ADR §8)
CHANNEL_CANONICAL = "canonical_project_passage"
CHANNEL_METADATA = "typed_project_metadata"
CHANNEL_RELATIONSHIP = "authorized_relationship"
CHANNEL_RETRIEVAL = "project_bound_retrieval"
CHANNEL_REPOSITORY = "local_repository_activity"
