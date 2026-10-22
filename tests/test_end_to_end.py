"""End-to-end workflow tests for successful user scenarios.

Tests complete successful workflows from user input to final output:
- File-based workflow: transcript file → CLI → XML output
- URL-based workflow: YouTube URL → url_parser.py → YouTube API → XML output
- File vs URL equivalence verification

Uses unified run_cli() helper with automatic rate limiting protection.
Tests that hit YouTube API are marked with @pytest.mark.slow.
For error scenarios, see tests/test_exceptions_url.py.
"""

import difflib
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from youtube_to_xml.exceptions import EXCEPTION_MESSAGES

# Test constants
EXAMPLES_DIR = Path("example_transcripts")
# Creator captions and chapters keep output stable; auto-generated ones drift.
URL_CHAPTERS = "https://www.youtube.com/watch?v=4NlrfOl0l8U"
URL_CHAPTERS_SHARED = "https://youtu.be/4NlrfOl0l8U?si=8cEkF7OrXrB1R4d7&t=27"
URL_NO_CHAPTERS = "https://www.youtube.com/watch?v=UdoY2l5TZaA"
REFERENCE_CHAPTERS = (  # reference files for URL_CHAPTERS
    "the-ai-that-solved-imo-geometry-problems-guest-video-by-aleph0"
)
URL_PLAYLIST = (
    "https://www.youtube.com/watch?v=LorEJPrALcg&list=PLwsjfz99OaPGqtBZJrn3dwMRQSBrcpE7e"
)


def run_cli(command: str, args: list[str] | str, tmp_path: Path) -> tuple[int, str]:
    """Run script and return (exit_code, output).

    Args:
        command: 'youtube-to-xml' (unified CLI)
        args: List of arguments or single URL string
        tmp_path: Working directory for the command
    """
    if isinstance(args, str):
        # Single URL
        cmd_args = ["uv", "run", command, args]
    else:
        # List of args
        cmd_args = ["uv", "run", command]
        cmd_args.extend(args)

    result = subprocess.run(  # noqa: S603
        cmd_args,
        capture_output=True,
        text=True,
        cwd=tmp_path,
        timeout=20,
        check=False,
    )

    # Handle rate limiting - skip test if encountered
    if result.returncode != 0:
        output = (result.stderr + result.stdout).lower()
        if any(pattern in output for pattern in ["429", "rate limit", "bot protection"]):
            pytest.skip("YouTube rate limited or bot protection triggered")

    return result.returncode, result.stdout + result.stderr


def assert_files_identical(actual: Path, expected: Path) -> None:
    """Assert two files are identical using cross-platform comparison."""
    expected_content = expected.read_text(encoding="utf-8")
    actual_content = actual.read_text(encoding="utf-8")

    if expected_content != actual_content:
        # Generate diff-like output for debugging
        diff_lines = list(
            difflib.unified_diff(
                expected_content.splitlines(keepends=True),
                actual_content.splitlines(keepends=True),
                fromfile=f"expected/{expected.name}",
                tofile=f"actual/{actual.name}",
                lineterm="",
            )
        )
        diff_output = "".join(diff_lines)
        pytest.fail(f"Files differ:\n{diff_output}")


def test_file_multi_chapters_success(tmp_path: Path) -> None:
    """Test CLI processing of file with multiple chapters."""
    input_file = EXAMPLES_DIR / "x4-chapters.txt"
    (tmp_path / "input.txt").write_text(input_file.read_text(encoding="utf-8"))

    exit_code, output = run_cli("youtube-to-xml", ["input.txt"], tmp_path)

    assert exit_code == 0
    assert "Created:" in output

    # Verify output matches reference file exactly
    output_file = tmp_path / "input.xml"
    reference_file = EXAMPLES_DIR / "x4-chapters.xml"
    assert_files_identical(output_file, reference_file)


def test_file_chapters_with_blanks_success(tmp_path: Path) -> None:
    """Test CLI processing of file with chapters containing blank lines."""
    input_file = EXAMPLES_DIR / "x3-chapters-with-blanks.txt"
    (tmp_path / "input.txt").write_text(input_file.read_text(encoding="utf-8"))

    exit_code, output = run_cli("youtube-to-xml", ["input.txt"], tmp_path)

    assert exit_code == 0
    assert "Created:" in output

    output_file = tmp_path / "input.xml"
    reference_file = EXAMPLES_DIR / "x3-chapters-with-blanks.xml"
    assert_files_identical(output_file, reference_file)


def test_file_invalid_format_error(tmp_path: Path) -> None:
    """Test CLI error handling for invalid transcript format."""
    input_file = EXAMPLES_DIR / "x0-chapters-invalid-format.txt"
    (tmp_path / "input.txt").write_text(input_file.read_text(encoding="utf-8"))

    exit_code, output = run_cli("youtube-to-xml", ["input.txt"], tmp_path)

    assert exit_code == 1
    assert EXCEPTION_MESSAGES["file_invalid_format_error"] in output


@pytest.mark.slow
def test_url_multi_chapters_success(tmp_path: Path) -> None:
    """Test YouTube fetcher with multi-chapter video."""
    exit_code, output = run_cli("youtube-to-xml", URL_CHAPTERS, tmp_path)

    assert exit_code == 0
    assert "✅ Created" in output

    xml_files = list(tmp_path.glob("*.xml"))
    assert len(xml_files) == 1, "Expected exactly one XML file to be generated"

    reference_file = EXAMPLES_DIR / f"{REFERENCE_CHAPTERS}.xml"
    assert_files_identical(xml_files[0], reference_file)


@pytest.mark.slow
def test_url_multi_chapters_shared_success(tmp_path: Path) -> None:
    """Test YouTube fetcher with shared URL format containing parameters."""
    exit_code, output = run_cli("youtube-to-xml", URL_CHAPTERS_SHARED, tmp_path)

    assert exit_code == 0
    assert "✅ Created" in output

    xml_files = list(tmp_path.glob("*.xml"))
    assert len(xml_files) == 1

    reference_file = EXAMPLES_DIR / f"{REFERENCE_CHAPTERS}.xml"
    assert_files_identical(xml_files[0], reference_file)


@pytest.mark.slow
def test_url_single_chapter_success(tmp_path: Path) -> None:
    """Test YouTube fetcher with single-chapter video."""
    exit_code, output = run_cli("youtube-to-xml", URL_NO_CHAPTERS, tmp_path)

    assert exit_code == 0
    assert "✅ Created" in output

    xml_files = list(tmp_path.glob("*.xml"))
    assert len(xml_files) == 1

    reference_file = EXAMPLES_DIR / "pick-up-where-you-left-off-with-claude.xml"
    assert_files_identical(xml_files[0], reference_file)


@pytest.mark.slow
def test_url_playlist_processes_single_video(tmp_path: Path) -> None:
    """Test YouTube fetcher processes single video from playlist URL, not playlist."""
    exit_code, output = run_cli("youtube-to-xml", URL_PLAYLIST, tmp_path)

    assert exit_code == 0
    assert "✅ Created" in output

    # Should process exactly one video, not entire playlist
    xml_files = list(tmp_path.glob("*.xml"))
    assert len(xml_files) == 1, "Should create exactly one XML file for single video"


@pytest.mark.slow
def test_url_vs_file_equivalent_output(tmp_path: Path) -> None:
    """Test URL vs file processing equivalence using direct XML parsing."""
    # Process file method
    input_file = EXAMPLES_DIR / f"{REFERENCE_CHAPTERS}.txt"
    (tmp_path / "input.txt").write_text(input_file.read_text(encoding="utf-8"))

    file_exit_code = run_cli("youtube-to-xml", ["input.txt"], tmp_path)[0]

    # Process URL method
    url_exit_code = run_cli("youtube-to-xml", URL_CHAPTERS, tmp_path)[0]

    assert file_exit_code == 0
    assert url_exit_code == 0

    # Get output files
    file_xml = tmp_path / "input.xml"
    url_xml_files = [f for f in tmp_path.glob("*.xml") if f.name != "input.xml"]
    assert len(url_xml_files) == 1
    url_xml = url_xml_files[0]

    file_root = ET.parse(file_xml).getroot()
    url_root = ET.parse(url_xml).getroot()

    # 1. Assert transcript element attributes
    expected_attrs = ["video_title", "video_published", "video_duration", "video_url"]

    # File transcript should have empty metadata
    assert len(file_root.attrib) == 4, (
        "File transcript should have 4 empty metadata attributes"
    )
    assert all(file_root.attrib[attr] == "" for attr in expected_attrs), (
        "File metadata should be empty"
    )

    # URL transcript should have populated metadata
    assert len(url_root.attrib) >= 4, "URL transcript should have metadata attributes"
    assert all(attr in url_root.attrib for attr in expected_attrs), (
        "URL missing required metadata"
    )

    # 2. Assert identical chapters: titles, start times and transcript text
    file_chapters = [(ch.attrib, ch.text) for ch in file_root.iter("chapter")]
    url_chapters = [(ch.attrib, ch.text) for ch in url_root.iter("chapter")]
    assert file_chapters == url_chapters, "Chapters differ between file and URL"


@pytest.mark.slow
def test_url_manual_transcript_priority(tmp_path: Path) -> None:
    """Test manual transcripts are prioritised over auto-generated (higher quality)."""
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    exit_code, output = run_cli("youtube-to-xml", test_url, tmp_path)

    assert exit_code == 0
    assert "✅ Created" in output

    xml_files = list(tmp_path.glob("*.xml"))
    assert len(xml_files) == 1

    # Parse XML and get first chapter content
    tree = ET.parse(xml_files[0])
    root = tree.getroot()
    first_chapter = root.find(".//chapter")
    assert first_chapter is not None

    content = first_chapter.text or ""
    content_lines = [line.strip() for line in content.split("\n") if line.strip()]
    first_3_lines = content_lines[:3]

    # Expect to use manual transcripts as priority
    expected_manual_version = [
        "0:01 [♪♪♪]",
        "0:18 ♪ We're no strangers to love ♪",
        "0:22 ♪ You know the rules and so do I ♪",
    ]
    assert first_3_lines == expected_manual_version, (
        f"Expected clean manual transcript, got: {first_3_lines}"
    )
