"""Tests for CLI functionality."""

import subprocess
from pathlib import Path

from youtube_to_xml.cli import _has_txt_extension, _is_valid_url
from youtube_to_xml.exceptions import EXCEPTION_MESSAGES


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


def test_is_valid_url_accepts_proper_urls() -> None:
    """URLs with scheme and domain (http/https) including YouTube variants."""
    valid_urls = [
        "https://www.youtube.com/watch?v=abc123",
        "https://youtu.be/xyz789",
        "https://www.google.com",
        "http://example.com",
    ]
    for url in valid_urls:
        assert _is_valid_url(url) is True


def test_is_valid_url_rejects_non_urls() -> None:
    """File paths, extensions, random text, and empty strings rejected."""
    non_url_inputs = [
        "transcript.txt",
        "/path/to/file.txt",
        "data.md",
        "config.xml",
        "random_text",
        "",
        "not-a-file-or-url",
    ]
    for input_str in non_url_inputs:
        assert _is_valid_url(input_str) is False


def test_is_valid_url_rejects_urls_without_tld() -> None:
    """URLs without TLD should be rejected to avoid DNS resolution errors."""
    urls_without_tld = [
        "https://ailearnlog",
        "http://localhost",
        "https://intranet",
    ]
    for url in urls_without_tld:
        assert _is_valid_url(url) is False


def test_has_txt_extension_accepts_txt_files() -> None:
    """Accepts .txt files with absolute, relative, and local paths."""
    txt_files = [
        "transcript.txt",
        "/path/to/file.txt",
        "./local/file.txt",
    ]
    for file_path in txt_files:
        assert _has_txt_extension(file_path) is True


def test_has_txt_extension_rejects_non_txt() -> None:
    """Rejects .md/.xml files, extensionless files, and empty strings."""
    non_txt_files = [
        "data.md",
        "file.xml",
        "random_text",
        "",
    ]
    for input_str in non_txt_files:
        assert _has_txt_extension(input_str) is False


# =============================================================================
# CLI Tests: Argument & Input Validation
# =============================================================================


def test_cli_shows_argparse_error_for_no_arguments(tmp_path: Path) -> None:
    """No arguments triggers argparse error with custom help hint."""
    # Run with no arguments
    exit_code, output = run_cli([], tmp_path)
    assert exit_code == 1
    # Generic assertions - argparse shows usage and error, we add help hint
    assert "usage: youtube-to-xml" in output
    assert "error: the following arguments are required" in output
    assert "Try: youtube-to-xml --help" in output


def test_cli_shows_error_for_non_url_non_txt_input(tmp_path: Path) -> None:
    """Ambiguous input that's neither valid URL nor .txt file path."""
    exit_code, output = run_cli("some_text", tmp_path)

    assert exit_code == 1
    assert_error_has_prefix_and_suffix(output)
    assert EXCEPTION_MESSAGES["invalid_input_error"] in output


# =============================================================================
# CLI Tests: File Extension Validation
# =============================================================================


def test_cli_shows_error_for_nonexistent_non_txt_extension(tmp_path: Path) -> None:
    """Non-existent files with non-.txt extensions are rejected."""
    exit_code, output = run_cli("nonexistent.md", tmp_path)

    assert exit_code == 1
    assert_error_has_prefix_and_suffix(output)
    assert EXCEPTION_MESSAGES["invalid_input_error"] in output


def test_cli_shows_error_for_existing_non_txt_extension(tmp_path: Path) -> None:
    """Existing files with non-.txt extensions are rejected."""
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
    """Nonexistent file shows 'couldn't find your file' error."""
    exit_code, output = run_cli("nonexistent.txt", tmp_path)

    assert exit_code == 1
    assert_error_has_prefix_and_suffix(output)
    assert EXCEPTION_MESSAGES["file_not_exists_error"] in output


def test_cli_shows_error_for_empty_txt_file(tmp_path: Path) -> None:
    """Zero-byte file shows appropriate error."""
    test_file = tmp_path / "empty.txt"
    test_file.write_text("", encoding="utf-8")

    exit_code, output = run_cli("empty.txt", tmp_path)

    assert exit_code == 1
    assert_error_has_prefix_and_suffix(output)
    assert EXCEPTION_MESSAGES["file_empty_error"] in output


def test_cli_shows_error_for_invalid_txt_format(tmp_path: Path) -> None:
    """Content not matching required YouTube transcript format."""
    test_file = tmp_path / "invalid.txt"
    test_file.write_text("not youtube transcript", encoding="utf-8")

    exit_code, output = run_cli("invalid.txt", tmp_path)

    assert exit_code == 1
    assert_error_has_prefix_and_suffix(output)
    assert EXCEPTION_MESSAGES["file_invalid_format_error"] in output
