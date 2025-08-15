"""Tests for CLI functionality."""

import subprocess
from pathlib import Path


def test_valid_transcript_creates_xml(tmp_path: Path) -> None:
    """Test that valid transcript produces XML output."""
    # Create test file in tmp directory
    test_file = tmp_path / "test.txt"
    test_file.write_text("Chapter One\n0:00\nContent here", encoding="utf-8")

    # Run CLI from tmp directory to isolate all file operations
    result = subprocess.run(
        ["uv", "run", "youtube-to-xml", "test.txt"],
        capture_output=True,
        text=True,
        cwd=tmp_path,  # Run from tmp directory
        check=False,
    )

    # Check success
    assert result.returncode == 0
    assert "Created:" in result.stdout

    # Verify output file exists in tmp location
    output_file = tmp_path / "transcript_files" / "test.xml"
    assert output_file.exists()


def test_missing_file_shows_error(tmp_path: Path) -> None:
    """Test error message for missing file."""
    result = subprocess.run(
        ["uv", "run", "youtube-to-xml", "nonexistent.txt"],
        capture_output=True,
        text=True,
        cwd=tmp_path,  # Run from tmp directory for consistency
        check=False,
    )

    assert result.returncode == 1
    assert "couldn't find your file" in result.stdout


def test_empty_file_shows_error(tmp_path: Path) -> None:
    """Test error message for empty file."""
    # Create empty test file
    test_file = tmp_path / "empty.txt"
    test_file.write_text("", encoding="utf-8")

    result = subprocess.run(
        ["uv", "run", "youtube-to-xml", "empty.txt"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )

    assert result.returncode == 1
    assert "Your file is empty" in result.stdout


def test_invalid_format_shows_error(tmp_path: Path) -> None:
    """Test error message for invalid format."""
    # Create invalid test file (starts with timestamp)
    test_file = tmp_path / "invalid.txt"
    test_file.write_text("0:00\nContent", encoding="utf-8")

    result = subprocess.run(
        ["uv", "run", "youtube-to-xml", "invalid.txt"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )

    assert result.returncode == 1
    assert "Wrong format" in result.stdout
    assert "youtube-to-xml --help" in result.stdout
