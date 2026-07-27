"""Read-only knowledge repositories."""
from __future__ import annotations

from jarvis_core.repositories.base import KnowledgeRepository
from jarvis_core.repositories.filesystem import FileSystemKnowledgeRepository

__all__ = ["FileSystemKnowledgeRepository", "KnowledgeRepository"]
