#!/usr/bin/env python3
"""Independent script to test raw yt-dlp API behavior without exception mapping.

This script calls yt-dlp directly to capture the exact exception type and message
that would be raised for a given URL, without any custom exception handling.

Usage:
    python test_raw_yt_dlp.py <URL>
"""

import os
import sys
from pathlib import Path

import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError, UnsupportedError


def test_raw_yt_dlp(url: str) -> None:
    """Test raw yt-dlp API behavior for a given URL."""
    print("=" * 60)
    print(f"Scenario URL:     '{url}'")
    print("Function called:  ydl.extract_info(url, download=False)")

    options = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en", "en-orig"],
        "subtitlesformat": "json3",
    }

    # Store stderr before any redirection
    old_stderr = sys.stderr

    try:
        # Redirect stderr to suppress yt-dlp's direct error output
        with Path(os.devnull).open("w") as devnull:
            sys.stderr = devnull
            try:
                with yt_dlp.YoutubeDL(options) as ydl:
                    ydl.extract_info(url, download=False)
            finally:
                sys.stderr = old_stderr

        print("Exception Type:   None (SUCCESS)")

    except (DownloadError, ExtractorError, UnsupportedError) as e:
        # Restore stderr in case of exception
        sys.stderr = old_stderr
        print(f"Exception Type:   {type(e).__name__}")
        print()
        print("Exact error was in str(e):")
        print("-" * 60)
        print(str(e))
        print("=" * 60)


def main() -> None:
    """Command-line interface."""
    expected_args = 2
    if len(sys.argv) != expected_args:
        print("Usage: python test_raw_yt_dlp.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    test_raw_yt_dlp(url)


if __name__ == "__main__":
    main()
