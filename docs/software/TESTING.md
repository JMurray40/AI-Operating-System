# Testing

## Run everything
```bash
pytest -q          # 38 tests
ruff check src tests
mypy src
```

## Test groups
- `tests/unit/` — frontmatter, inline parsing, models, read-only repository, resolver.
- `tests/integration/` — context loader, validator, determinism, CLI smoke, read-only safety.

## Notable tests
- **Determinism** (`test_determinism.py`): the same input produces identical JSON and an
  identical mock-provider response.
- **Read-only safety** (`test_readonly_safety.py`): SHA-256 of every fixture file is
  recorded before and after exercising all commands and asserted unchanged.
- **Parser edge cases** (`test_frontmatter.py`, `test_resolver.py`): malformed YAML,
  missing frontmatter, unresolved wikilinks, and conflicting aliases.

## Tooling exceptions (justified)
- `mypy` cannot find type stubs for `PyYAML` in an offline environment; `pyproject.toml`
  sets `ignore_missing_imports` for the `yaml` module only. Installing `types-PyYAML`
  (in the `dev` extra) removes the need for this override when online.
