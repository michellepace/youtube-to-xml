"""Wrapper to run the experimental transcript auto fetcher script as an entry point.

This wrapper exists to:
- Enable easier script execution: `uv run transcript-auto-fetcher` vs long path
- Simplify integration test commands in tests/test_integration.py

TODO: When experimental scripts/transcript_auto_fetcher.py is integrated and deleted:
- Remove this wrapper file
- Remove 'transcript-auto-fetcher' entry point from pyproject.toml
- Update integration tests to use main CLI instead
"""

import sys
from pathlib import Path

# Add the project root to Python path so we can import the script
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import after path setup to avoid import errors
from scripts.transcript_auto_fetcher import main as script_main  # noqa: E402


def main() -> None:
    """Entry point wrapper for transcript_auto_fetcher script."""
    script_main()


if __name__ == "__main__":
    main()
