# Local Setup

## Requirements
- Python 3.10+ (3.12+ recommended; see ADR-0006). No network or API keys required at runtime.

## Install (editable, with dev tools)
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```
This installs the single runtime dependency (PyYAML) and dev tools (pytest, ruff, mypy).

> The `jarvis` console script requires setuptools ≥61 (standard with Python 3.11+/3.12).
> In any older environment, use the module form below — it always works.

## Run without installing
From the repository root:
```bash
PYTHONPATH=src python -m jarvis_core inspect tests/fixtures/ai-operating-system
```

## Verify
```bash
jarvis inspect tests/fixtures/ai-operating-system
jarvis validate tests/fixtures/edge-cases
jarvis load-project "AI Operating System" --format json
jarvis summarize-project "FileOrbit" --provider mock
```
The default input is the bundled sample fixture — never a live vault.
