## Project Capabilities
**Purpose**: Convert YouTube transcripts to XML for improved LLM comprehension

**Current State**: 
- ✅ File-based CLI (`youtube-to-xml`) - production ready
- 🔬 URL-based script (`url-to-transcript`) - experimental, pending integration

**Architecture**: UV Package Application with TDD, pure functions, layer separation

**Entry Points**: See [pyproject.toml](pyproject.toml) `[project.scripts]` section for available commands

Full details with I/O examples: [README.md](README.md)

## Tech Stack

- **Python**: 3.13+
- **Key Patterns**: Use `pathlib` (not `os.path`), `dataclasses`, `logging`, `pytest` with `tmp_path`
- **Dependencies**: See [pyproject.toml](pyproject.toml) for complete list

## UV Workflow (Always)

**Strict Rules:**
- Use `uv run` - never activate venv
- Use `uv add` - never pip
- Use `pyproject.toml` - never requirements.txt

**Common Commands:**
```bash
# Setup & Dependencies
uv sync # Match packages to lockfile 
uv add --dev <pkg> # Add dev dependency
uv tree # Show dependency tree
uv lock --upgrade-package <pkg> # Update specific package
uv lock --upgrade && uv sync # Update all packages and apply

# Development
uv run pre-commit run --all-files # (hooks in .pre-commit-config.yaml)
uv run youtube-to-xml <file> # Run CLI
uv run pytest # All tests
uv run pytest -m "not integration" # Unit tests only (fast)
uv run pytest -m "integration" # Integration tests only (includes YouTube URLs)
uv run pytest -v tests/test_specific.py::test_function
uv run ruff check --fix # Lint and auto-fix (rules in pyproject.toml)
uv run ruff format # Format (see pyproject.toml)
```

## Code Design Principles: Elegant Simplicity over Over-Engineered

**TDD-Driven Design**: Write tests first - this naturally creates better architecture:
- **Pure functions preferred** - no side effects in business logic, easier to test
- **Clear module boundaries** - easier to test and understand
- **Single responsibility** - complex functions are hard to test

**Key Architecture Guidelines**:
- **Layer separation** - CLI → business logic → I/O
- **One module, one purpose** - Each `.py` file has a clear, focused role
- **Handle errors at boundaries** - Catch exceptions in CLI layer, not business logic
- **Type hints required** - All function signatures need type annotations
- **Descriptive naming** - Functions/variables should clearly indicate purpose and be consistent throughout

## TDD Implementation

- Use pytest's `tmp_path` fixture to avoid creating test files
- Avoid mocks as they introduce unnecessary complexity
- Test incrementally: One test should drive one behavior
- Use focused test names that describe what's being tested  

## Code Quality Standards

- **Ruff**: Strictest settings (ALL rules enabled)
- **Pyright**: Configured to avoid Ruff duplicates  
- **Pre-commit**: Auto-runs on every commit
- **Performance target**: 15,000 lines in <2 seconds