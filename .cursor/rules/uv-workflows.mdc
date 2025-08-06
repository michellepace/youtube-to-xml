---
description: Use UV Python package manager - paradigm shifts, critical workflows, commands
alwaysApply: false
---

Use [UV](https://docs.astral.sh/uv/) package and project manager.

```text
pyproject.toml   →  uv sync  →  `uv.lock`
(what you want)                 (exact versions for reproducibility)
```

## Key UV Paradigm Shifts

1. **Single tool replaces entire toolchain**
   - UV = `pip` + `poetry` + `pyenv` + `virtualenv` + `pipx` + `twine`

2. **No virtual environment activation**
   - Use `uv run` instead of `python` - automatically uses correct env
   - Never need `source .venv/bin/activate`

3. **Python is a managed dependency**
   - `uv python install 3.13` - UV downloads/manages Python versions
   - No system Python required

4. **Universal lockfile**
   - `uv.lock` works on all platforms (replaces `requirements.txt`)
   - Always auto-synced with `pyproject.toml`

5. **Automatic dependency resolution**
   - `uv run` = install deps + update lock + run command
   - No manual `pip install` steps

6. **Scripts have inline dependencies**
   - `uv add --script file.py requests` - deps for single files
   - Scripts run in isolated environments

**Key insight**: UV treats environments as ephemeral. Every `uv run` ensures correct deps/Python version automatically.

## Critical Workflows

### 1. **Creating and Running a Project**
```bash
uv init --package my-project  # Create a packaged application
cd my-project
uv run main.py  # Run the main script
uv run python -c "import sys; print(sys.version)"  # Run Python in project env
```

### 2. **Managing Dependencies**
```bash
uv add requests         # Add production dependency
uv add --dev pytest     # Add dev dependency
uv add "httpx>=0.25.0"  # Add with version constraint
uv remove requests      # Remove dependency
uv tree                 # List dependency tree
uv sync                 # Sync environment with lockfile
```

### 3. **Working with Python Versions**
```bash
uv python install 3.13        # Install Python 3.13
uv python pin 3.13            # Pin project to Python 3.13
uv run --python 3.11 main.py  # Run with specific Python
uv python list                # List available Python versions
uv python dir                 # Show uv installed Python versions path.
```

### 4. **Building and Publishing Packages**
```bash
uv build                  # Build wheel and sdist
uv version --bump minor   # Bump version (major, patch, etc.)
uv publish                # Publish to PyPI
uv build --no-sources     # Build for publishing (no local sources)
```

### 5. **Development Workflow**
```bash
uv sync # Create .venv (if needed) and install all dependencies
uv run pytest                     # Run tests
uv run ruff check                 # Run linter
uv run pre-commit run --all-files # Run all pre-commit hooks on entire codebase
uv run pre-commit run             # Run pre-commit hooks on staged files only
uv lock --upgrade-package httpx   # Update specific package
```

**UV automates the entire Python workflow**: project setup → dependency management → testing → publishing. No manual environment activation, no separate install commands, no Python version conflicts.