"""Jarvis Core: read-only Obsidian-vault context assembly for the AI Operating System.

This package is intentionally read-only. It discovers and parses a fixture (or vault)
directory, resolves relationships, assembles a deterministic project context package,
validates it, and hands it to a provider-neutral interface (a mock provider in this
prototype). It never writes to the source it reads.

See docs/software/ARCHITECTURE.md and the repository docs/ (SYSTEM_PRINCIPLES.md,
VAULT_SCHEMA.md, ADR-0004, ADR-0005) for the governing design.
"""

__version__ = "0.1.0"
