"""Wrapper to run the experimental URL to transcript script as an entry point.

This wrapper exists to:
- Enable easier script execution: `uv run url-to-transcript` vs long path
- Simplify integration test commands in tests/test_integration.py

TODO: When experimental scripts/url_to_transcript.py is integrated and deleted:
- Remove this wrapper file
- Remove 'url-to-transcript' entry point from pyproject.toml
- Update integration tests to use main CLI instead
"""

import sys
from pathlib import Path

# Add the project root to Python path so we can import the script
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import after path setup to avoid import errors
try:
    from scripts.url_to_transcript import main as script_main
except ModuleNotFoundError:
    print(
        "This experimental feature only works from a cloned repository.", file=sys.stderr
    )
    raise SystemExit(2) from None


def main() -> None:
    """Entry point wrapper for url_to_transcript script."""
    script_main()


if __name__ == "__main__":
    main()
