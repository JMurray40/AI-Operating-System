"""Visible-context conversation application layer (v0.5, session-only; ADR-0022/0023/0024).

A cohesive application layer over the released deterministic query/evidence pipeline. It
owns temporary cross-turn state and provider orchestration and receives no vault-write,
operational-store, tool, or general-network capability. See Handoff 07 for the contract.
"""

from __future__ import annotations

from jarvis_core.conversation.application import ConversationApplication
from jarvis_core.conversation.approval import EgressApproval, create_approval
from jarvis_core.conversation.contract import (
    CONVERSATION_CONTRACT_VERSION,
    Coverage,
    EvidenceType,
    ExitCode,
    FailureClass,
    LocalReadinessState,
    RemoteEligibility,
    TerminalState,
)
from jarvis_core.conversation.presentation import PresentationResult, present
from jarvis_core.conversation.request import (
    LOCAL_QWEN_PROFILE_ID,
    Budgets,
    HistoryLimits,
    LocalLimits,
    LocalWarmClass,
    PrepareTurnRequest,
    ProviderProfile,
    local_qwen_profile,
    mock_profile,
)
from jarvis_core.conversation.results import AttemptResult, TurnResult
from jarvis_core.conversation.session import Session
from jarvis_core.conversation.snapshot import ContextItem, ContextSnapshot

__all__ = [
    "CONVERSATION_CONTRACT_VERSION",
    "LOCAL_QWEN_PROFILE_ID",
    "AttemptResult",
    "Budgets",
    "ContextItem",
    "ContextSnapshot",
    "ConversationApplication",
    "Coverage",
    "EgressApproval",
    "EvidenceType",
    "ExitCode",
    "FailureClass",
    "HistoryLimits",
    "LocalLimits",
    "LocalReadinessState",
    "LocalWarmClass",
    "PrepareTurnRequest",
    "PresentationResult",
    "ProviderProfile",
    "RemoteEligibility",
    "Session",
    "TerminalState",
    "TurnResult",
    "create_approval",
    "local_qwen_profile",
    "mock_profile",
    "present",
]
