# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Capabilities
**Purpose**: Convert YouTube transcripts to XML for improved LLM comprehension

**Architecture**: UV Package Application with TDD, pure functions, layer separation

**Entry Point**: Single `youtube-to-xml` command handles both transcript files and YouTube URLs

## Core Architecture Pattern

**Unified Data Flow**: Single CLI with auto-detection routes to shared infrastructure:
- **URL Input**: `youtube-to-xml https://youtube.com/...` → `url_parser.parse_youtube_url()` → `TranscriptDocument` → `xml_builder.transcript_to_xml()` → XML
- **File Input**: `youtube-to-xml file.txt` → `file_parser.parse_transcript_file()` → `TranscriptDocument` → `xml_builder.transcript_to_xml()` → XML

**Key Modules**:
- `src/youtube_to_xml/cli.py` - Unified CLI with auto-detection (URLs vs .txt files)
- `src/youtube_to_xml/models.py` - Unified data structures for both file and URL processing
- `src/youtube_to_xml/url_parser.py` - URL-based transcript parsing to `TranscriptDocument`
- `src/youtube_to_xml/file_parser.py` - File-based transcript parsing to `TranscriptDocument`
- `src/youtube_to_xml/xml_builder.py` - Unified XML generation via `transcript_to_xml()`
- `src/youtube_to_xml/exceptions.py` - Centralised exception hierarchy with `BaseTranscriptError`

Full details with I/O examples: [README.md](README.md)

## Tech Stack

- **Python**: 3.13+
- **Key Patterns**: Use `pathlib` (not `os`), `dataclasses`, `logging`, `pytest` with `tmp_path`
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
uv run youtube-to-xml <file|url> # Run unified CLI (auto-detects input type)
uv run pytest # All tests
uv run pytest -m "not slow" # Unit tests only (fast, no network)
uv run pytest -m "slow" # Tests requiring internet (hit yt-dlp API)
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
- Test incrementally: One test should drive one behaviour
- Use focused test names that describe what's being tested

## Code Quality Standards

- **Ruff**: Strictest settings (ALL rules enabled)
- **Pyright**: Configured to avoid Ruff duplicates (see [pyproject.toml](pyproject.toml))
- **Pre-commit**: Auto-runs on every commit