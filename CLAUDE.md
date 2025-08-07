# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Status
YouTube-to-XML transcript converter - **foundation complete, core implementation missing**. Main entry point `src/youtube_to_xml/__init__.py` is placeholder only.

## UV Workflow (Always)
```bash
uv sync                           # Setup/update dependencies 
uv run youtube-to-xml <file>      # Run CLI
uv run python -m pytest          # All tests
uv run python -m pytest -v tests/test_specific.py::test_function  # Single test
uv run ruff check                 # Lint
uv run ruff format                # Format
uv run pre-commit run --all-files # All hooks
```
**Never activate venv** - always use `uv run`

## Design Principles (From SPEC.md - Non-negotiable)
**TDD-Driven Design**: Write tests first - this naturally creates better architecture:
- **Pure functions preferred** - no side effects in business logic, easier to test
- **Clear module boundaries** - easier to test and understand
- **Single responsibility** - complex functions are hard to test

**Key Architecture Guidelines**:
- **Layer separation** - CLI → business logic → I/O
- **One module, one purpose** - Each `.py` file has a clear, focused role
- **Handle errors at boundaries** - Catch exceptions in CLI layer, not business logic
- **Type hints required** - All function signatures need type annotations
- **Descriptive naming** - Functions/variables should clearly indicate purpose

**TDD Testing Guidelines**:
- **pytest `tmp_path` fixture** - no real test files
- **Avoid mocks** - use real operations when possible

## Reference Implementation
`scripts/transcript_reporter.py` contains **working** implementations:
- `find_timestamps()` - timestamp detection
- `find_chapters()` - chapter extraction logic  
- `TIMESTAMP_PATTERN` - regex for validation
- `read_file()` - file I/O patterns

**Adapt these proven patterns** rather than rewriting from scratch.

## Code Quality Standards
- **Ruff**: Strictest settings (ALL rules enabled)
- **Pyright**: Configured to avoid Ruff duplicates  
- **Pre-commit**: Auto-runs on every commit
- **Performance target**: 15,000 lines in <2 seconds

## Key Technical Insights
- **Ruff+Pyright Integration**: Smart rule deduplication prevents duplicate errors
- **Entry Point**: `[project.scripts]` in pyproject.toml → `youtube_to_xml:main`

## Development Context
See `docs/SPEC.md` for current implementation requirements, XML templates, error formats, and detection rules. SPEC.md contains the "what" - CLAUDE.md contains the "how" and "with what tools".