"""Tests for CLI functionality."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from youtube_to_xml.cli import (
    _sanitise_video_title_for_filename,  # pyright: ignore[reportPrivateUsage]
)
from youtube_to_xml.exceptions import EXCEPTION_MESSAGES

if TYPE_CHECKING:
    from pathlib import Path


def run_cli(args: str | list[str], tmp_path: Path) -> tuple[int, str]:
    """Run youtube-to-xml CLI and return (exit_code, output)."""
    if isinstance(args, str):
        cmd_args = ["uv", "run", "youtube-to-xml", args]
    else:
        cmd_args = ["uv", "run", "youtube-to-xml"]
        cmd_args.extend(args)

    result = subprocess.run(  # noqa: S603
        cmd_args,
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )

    return result.returncode, result.stdout + result.stderr


def assert_error_has_prefix_and_suffix(output: str) -> None:
    """Assert that error output starts with ❌ and ends with help hint."""
    assert output.startswith("❌")
    assert output.endswith("\n\nTry: youtube-to-xml --help\n")


# =============================================================================
# Unit Tests: Core Validation Functions
# =============================================================================
# NOTE: _has_txt_extension covered by CLI integration tests below
# NOTE: URL validation logic tested in test_url_parser.py::TestValidateBasicUrlStructure


def test_sanitise_video_title_for_filename_comprehensive() -> None:
    """Test normalization: special chars removed, lowercased, spaces to dashes."""
    title = "A - B --  C  (Multi   Spaces) & 😁 Special!@# Chars: Test"
    result = _sanitise_video_title_for_filename(title)
    expected = "a-b-c-multi-spaces-special-chars-test.xml"
    assert result == expected


# =============================================================================
# CLI Tests: Argument & Input Validation
# =============================================================================


def test_cli_shows_argparse_error_for_no_arguments(tmp_path: Path) -> None:
    """Test argparse error when no arguments provided."""
    exit_code, output = run_cli([], tmp_path)
    assert exit_code == 1
    assert "usage: youtube-to-xml" in output
    assert "error: the following arguments are required" in output
    assert "Try: youtube-to-xml --help" in output


def test_cli_shows_error_for_non_url_non_txt_input(tmp_path: Path) -> None:
    """Test rejection of input that's neither valid URL nor .txt file."""
    exit_code, output = run_cli("some_text", tmp_path)

    assert exit_code == 1
    assert_error_has_prefix_and_suffix(output)
    assert EXCEPTION_MESSAGES["invalid_input_error"] in output


# =============================================================================
# CLI Tests: File Extension Validation
# =============================================================================


def test_cli_shows_error_for_nonexistent_non_txt_extension(tmp_path: Path) -> None:
    """Test rejection of non-.txt file extensions."""
    exit_code, output = run_cli("nonexistent.md", tmp_path)

    assert exit_code == 1
    assert_error_has_prefix_and_suffix(output)
    assert EXCEPTION_MESSAGES["invalid_input_error"] in output


def test_cli_shows_error_for_existing_non_txt_extension(tmp_path: Path) -> None:
    """Test rejection of non-.txt extensions even when file exists."""
    test_file = tmp_path / "existing.md"
    test_file.write_text("content", encoding="utf-8")

    exit_code, output = run_cli("existing.md", tmp_path)

    assert exit_code == 1
    assert_error_has_prefix_and_suffix(output)
    assert EXCEPTION_MESSAGES["invalid_input_error"] in output


# =============================================================================
# CLI Tests: File Processing Errors
# =============================================================================


def test_cli_shows_error_for_nonexistent_txt_file(tmp_path: Path) -> None:
    """Test error message when .txt file doesn't exist."""
    exit_code, output = run_cli("nonexistent.txt", tmp_path)

    assert exit_code == 1
    assert_error_has_prefix_and_suffix(output)
    assert EXCEPTION_MESSAGES["file_not_exists_error"] in output


def test_cli_shows_error_for_empty_txt_file(tmp_path: Path) -> None:
    """Test error message for empty .txt file."""
    test_file = tmp_path / "empty.txt"
    test_file.write_text("", encoding="utf-8")

    exit_code, output = run_cli("empty.txt", tmp_path)

    assert exit_code == 1
    assert_error_has_prefix_and_suffix(output)
    assert EXCEPTION_MESSAGES["file_empty_error"] in output


def test_cli_shows_error_for_invalid_txt_format(tmp_path: Path) -> None:
    """Test error message for .txt file with invalid transcript format."""
    test_file = tmp_path / "invalid.txt"
    test_file.write_text("not youtube transcript", encoding="utf-8")

    exit_code, output = run_cli("invalid.txt", tmp_path)

    assert exit_code == 1
    assert_error_has_prefix_and_suffix(output)
    assert EXCEPTION_MESSAGES["file_invalid_format_error"] in output
