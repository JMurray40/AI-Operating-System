# ADR-0006: Use Python for the Jarvis Core Prototype

| Field | Value |
|---|---|
| Purpose | Record the language/tooling choice for the first Jarvis Core prototype |
| Status | Proposed |
| Version | 0.1.0 |
| Owner | Jason |
| Date | 2026-07-27 |
| Related | [System Architecture](../SYSTEM_ARCHITECTURE.md), [Implementation Plan](../IMPLEMENTATION_PLAN.md), [Development Guide](../DEVELOPMENT_GUIDE.md) |

## Status note

**Proposed, not accepted.** Per the overnight build instruction, when no language ADR
exists the prototype uses Python but records the choice as a proposal for human review.
No prior ADR approved a language; `SYSTEM_ARCHITECTURE.md` only *mentions* "a Python API
and SQLite" as a deployment expectation.

## Context

The first Jarvis Core work package (IMPLEMENTATION_PLAN.md Phase 3) is a read-only,
sample-vault parser with a mock provider and automated tests. It needs typed data
models, YAML parsing, a small CLI, and strong test tooling, with minimal dependencies
and no network or paid services.

## Decision

Use **Python 3.12+ (target)** for the prototype with:

- `src/` layout and `pyproject.toml`;
- standard-library `dataclasses` for models and `argparse` for the CLI (no heavy
  frameworks);
- `PyYAML` as the only runtime dependency (frontmatter parsing);
- `pytest`, `ruff`, and `mypy` as development tooling.

## Alternatives

- **TypeScript/Node.** Strong for the eventual web UI, but the first deliverable is a
  headless parser/CLI; Python reaches a typed, tested result faster and matches the
  architecture's stated Python API direction.
- **Go/Rust.** Excellent for a packaged binary later, but slower to iterate for a
  throwaway-friendly read-only prototype.

## Consequences

### Positive
- Fast path to a typed, tested prototype with tiny dependency surface.
- Aligns with the architecture's Python API expectation.
- Read-only, provider-neutral boundaries are easy to enforce and test.

### Negative / risks
- A second language may be introduced for the web/UI layer later.
- Python packaging for a desktop app needs a separate decision.

### Assumption recorded during the build
- The build sandbox runs Python 3.10.12, so the code is written to `>=3.10` and was
  **tested on 3.10**. `requires-python` is set to `>=3.10`; 3.12+ remains the
  recommended target. Confirm the supported floor when accepting this ADR.

## Revision history

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-07-27 | Proposed language and tooling for the prototype |
