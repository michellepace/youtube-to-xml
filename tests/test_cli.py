"""Tests for CLI functionality."""

import subprocess
from pathlib import Path

import pytest


def test_valid_transcript_creates_xml(tmp_path: Path) -> None:
    # Create test file in tmp directory
    test_file = tmp_path / "test.txt"
    test_file.write_text("Chapter One\n0:00\nTranscript text here", encoding="utf-8")

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
    output_file = tmp_path / "test.xml"
    assert output_file.exists()


def test_missing_file_shows_error(tmp_path: Path) -> None:
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
    # Create invalid test file (starts with timestamp)
    test_file = tmp_path / "invalid.txt"
    test_file.write_text("0:22\nTranscript text", encoding="utf-8")

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


def test_default_path_uses_new_parser(tmp_path: Path) -> None:
    """Test that default (no --legacy flag) uses new TranscriptDocument parser."""
    # Create test file in tmp directory
    test_file = tmp_path / "test.txt"
    test_file.write_text("Chapter One\n0:00\nTranscript text here", encoding="utf-8")

    # Run CLI without --legacy flag (should use new path)
    result = subprocess.run(
        ["uv", "run", "youtube-to-xml", "test.txt"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )

    # Check success
    assert result.returncode == 0
    assert "Created:" in result.stdout

    # Verify output file exists
    output_file = tmp_path / "test.xml"
    assert output_file.exists()

    # Verify XML contains structure (basic smoke test)
    xml_content = output_file.read_text()
    assert "<transcript" in xml_content
    assert "<chapters>" in xml_content
    assert "<chapter" in xml_content


def test_legacy_flag_uses_legacy_parser(tmp_path: Path) -> None:
    """Test that --legacy flag uses old parser path."""
    # Create test file in tmp directory
    test_file = tmp_path / "test.txt"
    test_file.write_text("Chapter One\n0:00\nTranscript text here", encoding="utf-8")

    # Run CLI with --legacy flag
    result = subprocess.run(
        ["uv", "run", "youtube-to-xml", "--legacy", "test.txt"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )

    # Check success
    assert result.returncode == 0
    assert "Created:" in result.stdout

    # Verify output file exists
    output_file = tmp_path / "test.xml"
    assert output_file.exists()

    # Verify XML contains structure (basic smoke test)
    xml_content = output_file.read_text()
    assert "<transcript" in xml_content
    assert "<chapters>" in xml_content
    assert "<chapter" in xml_content


def test_both_paths_produce_identical_output(tmp_path: Path) -> None:
    """Test that legacy and new paths produce identical XML output."""
    # Create test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("Chapter One\n0:00\nTranscript text here", encoding="utf-8")

    # Run with legacy flag
    result_legacy = subprocess.run(
        ["uv", "run", "youtube-to-xml", "--legacy", "test.txt"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )

    # Read legacy output
    legacy_output = (tmp_path / "test.xml").read_text()
    (tmp_path / "test.xml").unlink()  # Remove for second run

    # Run without legacy flag (new path)
    result_new = subprocess.run(
        ["uv", "run", "youtube-to-xml", "test.txt"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )

    # Read new output
    new_output = (tmp_path / "test.xml").read_text()

    # Both should succeed
    assert result_legacy.returncode == 0
    assert result_new.returncode == 0

    # Outputs should be identical
    assert legacy_output == new_output


@pytest.mark.parametrize("legacy_flag", [True, False])
def test_both_paths_handle_empty_file_consistently(
    tmp_path: Path, *, legacy_flag: bool
) -> None:
    """Test that both paths handle empty files with consistent error messages."""
    # Create empty test file
    test_file = tmp_path / "empty.txt"
    test_file.write_text("", encoding="utf-8")

    # Build command args
    args = ["uv", "run", "youtube-to-xml"]
    if legacy_flag:
        args.append("--legacy")
    args.append("empty.txt")

    result = subprocess.run(  # noqa: S603
        args,
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )

    # Both paths should fail with same exit code and similar error message
    assert result.returncode == 1
    assert "Your file is empty" in result.stdout


@pytest.mark.parametrize("legacy_flag", [True, False])
def test_both_paths_handle_invalid_format_consistently(
    tmp_path: Path, *, legacy_flag: bool
) -> None:
    """Test that both paths handle invalid format with consistent error messages."""
    # Create invalid test file (starts with timestamp)
    test_file = tmp_path / "invalid.txt"
    test_file.write_text("0:22\nTranscript text", encoding="utf-8")

    # Build command args
    args = ["uv", "run", "youtube-to-xml"]
    if legacy_flag:
        args.append("--legacy")
    args.append("invalid.txt")

    result = subprocess.run(  # noqa: S603
        args,
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )

    # Both paths should fail with same exit code and similar error message
    assert result.returncode == 1
    assert "Wrong format" in result.stdout
    assert "youtube-to-xml --help" in result.stdout


@pytest.mark.parametrize("legacy_flag", [True, False])
def test_both_paths_handle_valid_transcript_consistently(
    tmp_path: Path, *, legacy_flag: bool
) -> None:
    """Test that both paths handle valid transcripts with consistent success behavior."""
    # Create test file with valid content
    test_file = tmp_path / "valid.txt"
    test_file.write_text("Chapter One\n0:00\nTranscript text here", encoding="utf-8")

    # Build command args
    args = ["uv", "run", "youtube-to-xml"]
    if legacy_flag:
        args.append("--legacy")
    args.append("valid.txt")

    result = subprocess.run(  # noqa: S603
        args,
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )

    # Both paths should succeed
    assert result.returncode == 0
    assert "Created:" in result.stdout

    # Verify output file exists
    output_file = tmp_path / "valid.xml"
    assert output_file.exists()

    # Verify XML contains expected structure
    xml_content = output_file.read_text()
    assert "<transcript" in xml_content
    assert "<chapters>" in xml_content
    assert "<chapter" in xml_content
    assert "Chapter One" in xml_content


def test_complex_transcript_paths_produce_identical_output(tmp_path: Path) -> None:
    """Test that both paths produce identical output for more complex transcripts."""
    # Create a more complex transcript with multiple chapters
    complex_transcript = """Introduction to Advanced Topics
0:00
Welcome to this comprehensive guide about advanced concepts
0:45
We'll cover several important areas today

Main Content Section
2:30
Let's dive into the core material here
3:15
This section contains detailed explanations

Conclusion and Summary
5:00
To wrap up our discussion
5:30
Thank you for your attention"""

    test_file = tmp_path / "complex.txt"
    test_file.write_text(complex_transcript, encoding="utf-8")

    # Run with legacy flag
    result_legacy = subprocess.run(
        ["uv", "run", "youtube-to-xml", "--legacy", "complex.txt"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )

    # Read legacy output
    legacy_output = (tmp_path / "complex.xml").read_text()
    (tmp_path / "complex.xml").unlink()  # Remove for second run

    # Run without legacy flag (new path)
    result_new = subprocess.run(
        ["uv", "run", "youtube-to-xml", "complex.txt"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )

    # Read new output
    new_output = (tmp_path / "complex.xml").read_text()

    # Both should succeed
    assert result_legacy.returncode == 0
    assert result_new.returncode == 0

    # Outputs should be identical
    assert legacy_output == new_output
