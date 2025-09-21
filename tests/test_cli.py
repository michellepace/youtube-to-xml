"""Tests for CLI functionality."""

import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


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


def test_parser_path_selection(tmp_path: Path) -> None:
    """Test that CLI uses correct parser."""
    # Create test file in tmp directory
    test_file = tmp_path / "test.txt"
    test_file.write_text("Chapter One\n0:00\nTranscript text here", encoding="utf-8")

    # Run CLI
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
    xml_content = output_file.read_text(encoding="utf-8")
    assert "<transcript" in xml_content
    assert "<chapters>" in xml_content
    assert "<chapter" in xml_content


def test_handle_empty_file_consistently(tmp_path: Path) -> None:
    """Test that parser handles empty files with error messages."""
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

    # Should fail with error message
    assert result.returncode == 1
    assert "Your file is empty" in result.stdout


def test_handle_invalid_format_consistently(tmp_path: Path) -> None:
    """Test that parser handles invalid format with error messages."""
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

    # Should fail with error message
    assert result.returncode == 1
    assert "Wrong format" in result.stdout
    assert "youtube-to-xml --help" in result.stdout


def test_handle_valid_transcript_consistently(tmp_path: Path) -> None:
    """Test that parser handles valid transcripts with success behavior."""
    # Create test file with valid content
    test_file = tmp_path / "valid.txt"
    test_file.write_text("Chapter One\n0:00\nTranscript text here", encoding="utf-8")

    result = subprocess.run(
        ["uv", "run", "youtube-to-xml", "valid.txt"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )

    # Should succeed
    assert result.returncode == 0
    assert "Created:" in result.stdout

    # Verify output file exists
    output_file = tmp_path / "valid.xml"
    assert output_file.exists()

    # Verify XML contains expected structure
    xml_content = output_file.read_text(encoding="utf-8")
    assert "<transcript" in xml_content
    assert "<chapters>" in xml_content
    assert "<chapter" in xml_content
    assert "Chapter One" in xml_content


def test_multi_chapter_transcript_output(tmp_path: Path) -> None:
    """Test that parser handles multi-chapter transcripts correctly."""
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

    # Create test file
    test_file = tmp_path / "complex.txt"
    test_file.write_text(complex_transcript, encoding="utf-8")

    # Run CLI
    result = subprocess.run(
        ["uv", "run", "youtube-to-xml", "complex.txt"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )

    # Should succeed
    assert result.returncode == 0
    assert "Created:" in result.stdout

    # Verify output file exists and contains multiple chapters
    output_file = tmp_path / "complex.xml"
    assert output_file.exists()
    xml_content = output_file.read_text(encoding="utf-8")

    # Verify multi-chapter structure using proper XML parsing
    root = ET.fromstring(xml_content)
    individual_chapters = root.findall(".//chapter")
    assert len(individual_chapters) == 3  # Three chapters

    # Verify chapter titles
    chapter_titles = [ch.get("title") for ch in individual_chapters]
    assert "Introduction to Advanced Topics" in chapter_titles
    assert "Main Content Section" in chapter_titles
    assert "Conclusion and Summary" in chapter_titles
