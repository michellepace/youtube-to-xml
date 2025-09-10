"""End-to-end tests for complete user workflows.

Tests the full application stack from user input to final output:
- File-based workflow: transcript file → CLI → XML output
- URL-based workflow: YouTube URL → experimental url_to_transcript.py → YouTube API →
  XML output

Integration tests (marked with @pytest.mark.integration) hit external YouTube API.
"""

import difflib
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

# Test constants
EXAMPLES_DIR = Path("example_transcripts")
URL_CHAPTERS = "https://www.youtube.com/watch?v=Q4gsvJvRjCU"
URL_CHAPTERS_SHARED = "https://youtu.be/Q4gsvJvRjCU?si=8cEkF7OrXrB1R4d7&t=27"
URL_NO_CHAPTERS = "https://www.youtube.com/watch?v=UdoY2l5TZaA"
URL_NO_TRANSCRIPT = "https://www.youtube.com/watch?v=6eBSHbLKuN0"
URL_INVALID = "https://www.youtube.com/watch?v=play99invalid"

# Error scenario URLs
URL_EMPTY = ""
URL_NON_YOUTUBE = "https://www.google.com/"
URL_INCOMPLETE_ID = "https://www.youtube.com/watch?v=VvkhYW"
URL_MALFORMED = "invalid-url"

SUBPROCESS_TIMEOUT = 10


def run_cli_command(args: list[str], tmp_path: Path) -> subprocess.CompletedProcess[str]:
    """Run the main CLI command."""
    return subprocess.run(  # noqa: S603
        ["uv", "run", "youtube-to-xml", *args],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
        timeout=SUBPROCESS_TIMEOUT,
    )


def run_youtube_script(url: str, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    """Run experimental YouTube script."""
    result = subprocess.run(  # noqa: S603
        ["uv", "run", "url-to-transcript", url],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
        timeout=SUBPROCESS_TIMEOUT,
    )

    # Handle rate limiting and bot protection - skip test if encountered
    if result.returncode != 0:
        output = (result.stderr + result.stdout).lower()
        if any(
            pattern.lower() in output
            for pattern in [
                "429",
                "Rate limited",
                "Too Many Requests",
                "bot protection triggered",  # Our custom message
                "YouTube bot protection",  # Our custom message
            ]
        ):
            pytest.skip("YouTube rate limited or bot protection triggered")

    return result


def setup_reference_file(tmp_path: Path, reference_name: str) -> Path:
    """Copy reference file to tmp directory for testing."""
    source = EXAMPLES_DIR / reference_name
    target = tmp_path / reference_name
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    return target


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

    result = run_cli_command(["input.txt"], tmp_path)

    assert result.returncode == 0
    assert "Created:" in result.stdout

    # Verify output matches reference file exactly
    output_file = tmp_path / "input.xml"
    reference_file = setup_reference_file(tmp_path, "x4-chapters.xml")

    assert output_file.exists()
    assert_files_identical(output_file, reference_file)


def test_file_chapters_with_blanks_success(tmp_path: Path) -> None:
    """Test CLI processing of file with chapters containing blank lines."""
    input_file = EXAMPLES_DIR / "x3-chapters-with-blanks.txt"
    (tmp_path / "input.txt").write_text(input_file.read_text(encoding="utf-8"))

    result = run_cli_command(["input.txt"], tmp_path)

    assert result.returncode == 0
    assert "Created:" in result.stdout

    output_file = tmp_path / "input.xml"
    reference_file = setup_reference_file(tmp_path, "x3-chapters-with-blanks.xml")

    assert output_file.exists()
    assert_files_identical(output_file, reference_file)


def test_file_invalid_format_error(tmp_path: Path) -> None:
    """Test CLI error handling for invalid transcript format."""
    input_file = EXAMPLES_DIR / "x0-chapters-invalid-format.txt"
    (tmp_path / "input.txt").write_text(input_file.read_text(encoding="utf-8"))

    result = run_cli_command(["input.txt"], tmp_path)

    assert result.returncode == 1
    assert "Wrong format" in result.stdout
    assert "youtube-to-xml --help" in result.stdout


@pytest.mark.integration
def test_url_multi_chapters_success(tmp_path: Path) -> None:
    """Test YouTube fetcher with multi-chapter video."""
    result = run_youtube_script(URL_CHAPTERS, tmp_path)

    assert result.returncode == 0
    assert "✅ Created:" in result.stdout

    xml_files = list(tmp_path.glob("*.xml"))
    assert len(xml_files) == 1, "Expected exactly one XML file to be generated"

    reference_file = setup_reference_file(
        tmp_path, "how-claude-code-hooks-save-me-hours-daily.xml"
    )
    assert_files_identical(xml_files[0], reference_file)


@pytest.mark.integration
def test_url_multi_chapters_shared_success(tmp_path: Path) -> None:
    """Test YouTube fetcher with shared URL format containing parameters."""
    result = run_youtube_script(URL_CHAPTERS_SHARED, tmp_path)

    assert result.returncode == 0
    assert "✅ Created:" in result.stdout

    xml_files = list(tmp_path.glob("*.xml"))
    assert len(xml_files) == 1

    reference_file = setup_reference_file(
        tmp_path, "how-claude-code-hooks-save-me-hours-daily.xml"
    )
    assert_files_identical(xml_files[0], reference_file)


@pytest.mark.integration
def test_url_single_chapter_success(tmp_path: Path) -> None:
    """Test YouTube fetcher with single-chapter video."""
    result = run_youtube_script(URL_NO_CHAPTERS, tmp_path)

    assert result.returncode == 0
    assert "✅ Created:" in result.stdout

    xml_files = list(tmp_path.glob("*.xml"))
    assert len(xml_files) == 1

    reference_file = setup_reference_file(
        tmp_path, "pick-up-where-you-left-off-with-claude.xml"
    )
    assert_files_identical(xml_files[0], reference_file)


@pytest.mark.integration
def test_url_no_subtitles_error(tmp_path: Path) -> None:
    """Test YouTube fetcher exits with error when video has no subtitles."""
    result = run_youtube_script(URL_NO_TRANSCRIPT, tmp_path)

    assert result.returncode == 1
    assert "❌ Error:" in result.stdout
    assert "This video doesn't have subtitles available" in result.stdout

    xml_files = list(tmp_path.glob("*.xml"))
    assert len(xml_files) == 0, "No XML file should be created without subtitles"


@pytest.mark.integration
def test_url_invalid_format_error(tmp_path: Path) -> None:
    """Test YouTube fetcher error handling for invalid URL."""
    result = run_youtube_script(URL_INVALID, tmp_path)

    assert result.returncode == 1
    error_patterns = ["truncated", "Incomplete YouTube ID", "Video unavailable"]
    combined = result.stdout + result.stderr
    assert any(pattern in combined for pattern in error_patterns), (
        f"Expected error message not found in: {combined}"
    )


@pytest.mark.integration
@pytest.mark.parametrize(
    ("url", "expected_error_message"),
    [
        (URL_EMPTY, "Invalid URL format"),  # URLIsInvalidError
        (URL_NON_YOUTUBE, "URL is not a YouTube video"),  # URLNotYouTubeError
        (URL_INCOMPLETE_ID, "YouTube URL is incomplete"),  # URLIncompleteError
        (URL_MALFORMED, "Invalid URL format"),  # URLIsInvalidError
    ],
)
def test_url_error_scenarios(
    url: str, expected_error_message: str, tmp_path: Path
) -> None:
    """Test various URL error scenarios produce correct error messages."""
    result = run_youtube_script(url, tmp_path)

    assert result.returncode == 1
    assert (
        expected_error_message in result.stdout or expected_error_message in result.stderr
    ), (
        f"Expected '{expected_error_message}' not found in output.\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )


@pytest.mark.integration
def test_url_vs_file_equivalent_output(tmp_path: Path) -> None:
    """Test URL vs file processing equivalence using direct XML parsing."""
    # Process file method
    input_file = EXAMPLES_DIR / "how-claude-code-hooks-save-me-hours-daily.txt"
    (tmp_path / "input.txt").write_text(input_file.read_text(encoding="utf-8"))

    file_result = run_cli_command(["input.txt"], tmp_path)

    # Process URL method
    url_result = run_youtube_script(URL_CHAPTERS, tmp_path)

    assert file_result.returncode == 0
    assert url_result.returncode == 0

    # Get output files
    file_xml = tmp_path / "input.xml"
    url_xml_files = [f for f in tmp_path.glob("*.xml") if f.name != "input.xml"]
    assert len(url_xml_files) == 1
    url_xml = url_xml_files[0]

    # Parse both XML files
    file_tree = ET.parse(file_xml)
    url_tree = ET.parse(url_xml)
    file_root = file_tree.getroot()
    url_root = url_tree.getroot()

    # 1. Assert both files have same line count
    file_lines = len(file_xml.read_text(encoding="utf-8").splitlines())
    url_lines = len(url_xml.read_text(encoding="utf-8").splitlines())
    assert file_lines == url_lines, "Line count must be the same"

    # 2. Assert transcript element attributes
    expected_attrs = ["video_title", "upload_date", "duration", "video_url"]

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

    # 3. Assert matching chapter structure
    file_chapters = file_root.findall(".//chapter")
    url_chapters = url_root.findall(".//chapter")
    assert len(file_chapters) == len(url_chapters), "Chapter count mismatch"

    # 4. Assert matching chapter titles
    file_titles = [ch.get("title") for ch in file_chapters]
    url_titles = [ch.get("title") for ch in url_chapters]
    assert file_titles == url_titles, "Chapter titles don't match"

    # 5. Assert similar content volume per chapter (allow minor variations)
    for i, (file_ch, url_ch) in enumerate(zip(file_chapters, url_chapters, strict=False)):
        file_content = (file_ch.text or "").strip()
        url_content = (url_ch.text or "").strip()
        file_content_lines = len(file_content.split("\n")) if file_content else 0
        url_content_lines = len(url_content.split("\n")) if url_content else 0

        assert abs(file_content_lines - url_content_lines) <= 2, (
            f"Chapter {i} ({file_titles[i]}) content volume differs significantly"
        )


@pytest.mark.integration
def test_url_unmapped_error_handling(tmp_path: Path) -> None:
    """Test that URLUnknownUnmappedError is properly handled for unmapped yt-dlp errors.

    Uses a private video that triggers a yt-dlp error message that doesn't match
    any existing patterns in map_yt_dlp_exception().
    """
    result = run_youtube_script("https://youtu.be/15vClfaR35w", tmp_path)

    assert result.returncode == 1
    # Should show the actual yt-dlp error message (main() adds "❌ Error:" prefix)
    assert "❌ Error: [youtube] 15vClfaR35w: Private video" in result.stdout, (
        f"Expected yt-dlp error message in stdout, got: {result.stdout}"
    )
    # Should NOT have a traceback in stderr when properly handled
    assert "Traceback" not in result.stderr, (
        f"Should not crash with traceback, got: {result.stderr}"
    )

    # Verify no XML file was created
    xml_files = list(tmp_path.glob("*.xml"))
    assert len(xml_files) == 0, "No XML file should be created on unmapped errors"
