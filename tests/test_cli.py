"""Tests for CLI functionality."""

import subprocess
from pathlib import Path

import pytest

from youtube_to_xml.cli import _has_txt_extension, _is_valid_url


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


def test_is_valid_url_accepts_proper_urls() -> None:
    """Valid URLs with scheme and netloc should be recognized."""
    valid_urls = [
        "https://www.youtube.com/watch?v=abc123",
        "https://youtu.be/xyz789",
        "https://www.google.com",
        "http://example.com",
    ]
    for url in valid_urls:
        assert _is_valid_url(url) is True


def test_is_valid_url_rejects_non_urls() -> None:
    """Non-URLs should be rejected by URL validation."""
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


def test_has_txt_extension_accepts_txt_files() -> None:
    """Files with .txt extension should be recognized."""
    txt_files = [
        "transcript.txt",
        "/path/to/file.txt",
        "./local/file.txt",
    ]
    for file_path in txt_files:
        assert _has_txt_extension(file_path) is True


def test_has_txt_extension_rejects_non_txt() -> None:
    """Files without .txt extension should be rejected."""
    non_txt_files = [
        "data.md",
        "file.xml",
        "random_text",
        "",
    ]
    for input_str in non_txt_files:
        assert _has_txt_extension(input_str) is False


def test_cli_shows_argparse_error_for_no_arguments(tmp_path: Path) -> None:
    """No arguments should show argparse error with help hint."""
    # Run with no arguments
    result = subprocess.run(
        ["uv", "run", "youtube-to-xml"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )

    exit_code, output = result.returncode, result.stdout + result.stderr
    assert exit_code == 1
    # Generic assertions - argparse shows usage and error, we add help hint
    assert "usage: youtube-to-xml" in output
    assert "error: the following arguments are required" in output
    assert "Try: youtube-to-xml --help" in output


def test_cli_shows_help_for_invalid_text(tmp_path: Path) -> None:
    """Random text should show concise error message."""
    exit_code, output = run_cli("some_text", tmp_path)

    assert exit_code == 1
    assert "❌" in output
    assert "Try: youtube-to-xml --help" in output
    # Should NOT show full help
    assert "💡 Check that your transcript follows this basic pattern" not in output


def test_cli_shows_help_for_invalid_file_extension(tmp_path: Path) -> None:
    """Non-.txt file extensions should show concise error message."""
    exit_code, output = run_cli("data.md", tmp_path)

    assert exit_code == 1
    assert "❌" in output
    assert "Try: youtube-to-xml --help" in output
    # Should NOT show full help
    assert "💡 Check that your transcript follows this basic pattern" not in output


def test_cli_routes_files_to_file_parser(tmp_path: Path) -> None:
    """Test CLI correctly routes file inputs to file parser (unchanged behavior)."""
    # Create test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Chapter One\n0:00\nTranscript text here", encoding="utf-8")

    # Run CLI with file input
    exit_code, output = run_cli("test.txt", tmp_path)

    # Should succeed and create XML file (existing behavior)
    assert exit_code == 0
    assert "Created:" in output
    assert (tmp_path / "test.xml").exists()


@pytest.mark.integration
def test_cli_routes_urls_to_url_parser(tmp_path: Path) -> None:
    """Test CLI correctly routes URL inputs to URL parser (new behavior)."""
    test_url = "https://www.youtube.com/watch?v=UdoY2l5TZaA"

    # Run CLI with URL input
    exit_code, output = run_cli(test_url, tmp_path)

    # Should succeed and create XML file
    assert exit_code == 0
    assert "Created:" in output

    # Should create XML file with video title as filename
    xml_files = list(tmp_path.glob("*.xml"))
    assert len(xml_files) == 1


def test_valid_transcript_creates_xml(tmp_path: Path) -> None:
    # Create test file in tmp directory
    test_file = tmp_path / "test.txt"
    test_file.write_text("Chapter One\n0:00\nTranscript text here", encoding="utf-8")

    # Run CLI from tmp directory to isolate all file operations
    exit_code, output = run_cli("test.txt", tmp_path)

    # Check success
    assert exit_code == 0
    assert "Created:" in output

    # Verify output file exists in tmp location
    output_file = tmp_path / "test.xml"
    assert output_file.exists()


def test_missing_file_shows_error(tmp_path: Path) -> None:
    exit_code, output = run_cli("nonexistent.txt", tmp_path)

    assert exit_code == 1
    assert "couldn't find your file" in output
    assert "Try: youtube-to-xml --help" in output


def test_empty_file_shows_error(tmp_path: Path) -> None:
    # Create empty test file
    test_file = tmp_path / "empty.txt"
    test_file.write_text("", encoding="utf-8")

    exit_code, output = run_cli("empty.txt", tmp_path)

    assert exit_code == 1
    assert "Your file is empty" in output
    assert "Try: youtube-to-xml --help" in output


def test_invalid_format_shows_error(tmp_path: Path) -> None:
    # Create invalid test file (starts with timestamp)
    test_file = tmp_path / "invalid.txt"
    test_file.write_text("0:22\nTranscript text", encoding="utf-8")

    exit_code, output = run_cli("invalid.txt", tmp_path)

    assert exit_code == 1
    assert "Wrong format" in output
    assert "youtube-to-xml --help" in output


def test_parser_path_selection(tmp_path: Path) -> None:
    """Test that CLI uses correct parser."""
    # Create test file in tmp directory
    test_file = tmp_path / "test.txt"
    test_file.write_text("Chapter One\n0:00\nTranscript text here", encoding="utf-8")

    # Run CLI
    exit_code, output = run_cli("test.txt", tmp_path)

    # Check success
    assert exit_code == 0
    assert "Created:" in output

    # Verify output file exists
    output_file = tmp_path / "test.xml"
    assert output_file.exists()

    # Verify XML contains structure (basic smoke test)
    xml_content = output_file.read_text(encoding="utf-8")
    assert "<transcript" in xml_content
    assert "<chapters>" in xml_content
    assert "<chapter" in xml_content


def test_handle_empty_file_consistently(tmp_path: Path) -> None:
    """Test that parser handles empty files with error messages."""
    # Create empty test file
    test_file = tmp_path / "empty.txt"
    test_file.write_text("", encoding="utf-8")

    exit_code, output = run_cli("empty.txt", tmp_path)

    # Should fail with error message
    assert exit_code == 1
    assert "Your file is empty" in output


def test_handle_invalid_format_consistently(tmp_path: Path) -> None:
    """Test that parser handles invalid format with error messages."""
    # Create invalid test file (starts with timestamp)
    test_file = tmp_path / "invalid.txt"
    test_file.write_text("0:22\nTranscript text", encoding="utf-8")

    exit_code, output = run_cli("invalid.txt", tmp_path)

    # Should fail with error message
    assert exit_code == 1
    assert "Wrong format" in output
    assert "youtube-to-xml --help" in output


def test_handle_valid_transcript_consistently(tmp_path: Path) -> None:
    """Test that parser handles valid transcripts with success behavior."""
    # Create test file with valid content
    test_file = tmp_path / "valid.txt"
    test_file.write_text("Chapter One\n0:00\nTranscript text here", encoding="utf-8")

    exit_code, output = run_cli("valid.txt", tmp_path)

    # Should succeed
    assert exit_code == 0
    assert "Created:" in output

    # Verify output file exists
    output_file = tmp_path / "valid.xml"
    assert output_file.exists()

    # Verify XML contains expected structure
    xml_content = output_file.read_text(encoding="utf-8")
    assert "<transcript" in xml_content
    assert "<chapters>" in xml_content
    assert "<chapter" in xml_content
    assert "Chapter One" in xml_content
