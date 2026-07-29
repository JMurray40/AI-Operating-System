# Local Setup

For the supported non-author Project Resume installation, uninstall/reinstall,
classification onboarding, recovery, and A12 procedure, use
[Project Resume Installation, Onboarding, and Recovery](PROJECT_RESUME_INSTALLATION_AND_RECOVERY.md).

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

## Installed Project Resume verification

An installed candidate must work without `PYTHONPATH` or editable mode:

```bash
jarvis --help
jarvis resume --help
jarvis resume-doctor --help
jarvis resume "FileOrbit" --path tests/fixtures/fileorbit --format json \
  --as-of 2026-07-28T00:00:00Z
```

The frozen executable documented for v0.4 onboarding is
`014076c429d47de83be4ca6543264082aa62633f`.
