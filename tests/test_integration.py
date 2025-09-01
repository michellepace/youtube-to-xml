"""Integration tests for end-to-end validation of CLI and YouTube fetcher."""

import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

# Import from script for direct function testing
sys.path.insert(0, str(Path.cwd() / "scripts"))

# Test constants
SCRIPT_PATH = Path.cwd() / "scripts/transcript_auto_fetcher.py"
EXAMPLES_DIR = Path("example_transcripts")
URL_CHAPTERS = "https://www.youtube.com/watch?v=Q4gsvJvRjCU"
URL_CHAPTERS_SHARED = "https://youtu.be/Q4gsvJvRjCU?si=8cEkF7OrXrB1R4d7&t=27"
URL_NO_CHAPTERS = "https://www.youtube.com/watch?v=UdoY2l5TZaA"
URL_NO_TRANSCRIPT = "https://www.youtube.com/watch?v=6eBSHbLKuN0"
URL_INVALID = "https://www.youtube.com/watch?v=play99invalid"
SUBPROCESS_TIMEOUT = 20


def run_cli_command(args: list[str], tmp_path: Path) -> subprocess.CompletedProcess:
    """Run the main CLI command."""
    return subprocess.run(  # noqa: S603
        ["uv", "run", "youtube-to-xml", *args],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )


def run_youtube_script(url: str, tmp_path: Path) -> subprocess.CompletedProcess:
    """Run YouTube script with rate limit handling."""
    result = subprocess.run(  # noqa: S603
        ["uv", "run", "python", str(SCRIPT_PATH), url],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        timeout=SUBPROCESS_TIMEOUT,
        check=False,
    )

    # Handle rate limiting - script now exits with error when rate limited
    if result.returncode != 0 and (
        "Rate limited" in result.stderr or "Rate limited" in result.stdout
    ):
        pytest.skip("YouTube rate limited")

    return result


def setup_reference_file(tmp_path: Path, reference_name: str) -> Path:
    """Copy reference file to tmp directory for testing."""
    source = EXAMPLES_DIR / reference_name
    target = tmp_path / reference_name
    target.write_text(source.read_text(encoding="utf-8"))
    return target


def assert_files_identical(actual: Path, expected: Path) -> None:
    """Assert two files are identical using diff."""
    result = subprocess.run(  # noqa: S603
        ["diff", str(expected), str(actual)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"Files differ:\n{result.stdout}"


@pytest.mark.integration
def test_file_multi_chapters_success(tmp_path: Path) -> None:
    """Test CLI processing of file with multiple chapters."""
    # Copy input file to tmp directory and run CLI there
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


@pytest.mark.integration
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


@pytest.mark.integration
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

    # Find the generated XML file
    xml_files = list(tmp_path.glob("*.xml"))
    assert len(xml_files) == 1, "Expected exactly one XML file to be generated"

    # Copy reference file to tmp directory and compare
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

    # Should exit with error code (no useless empty files)
    assert result.returncode == 1
    assert "❌ Error:" in result.stdout
    assert "No subtitle URL found for video" in result.stdout

    # Should NOT create any XML files (useless without subtitles)
    xml_files = list(tmp_path.glob("*.xml"))
    assert len(xml_files) == 0, "No XML file should be created without subtitles"


@pytest.mark.integration
def test_url_invalid_format_error(tmp_path: Path) -> None:
    """Test YouTube fetcher error handling for invalid URL."""
    result = run_youtube_script(URL_INVALID, tmp_path)

    assert result.returncode == 1
    # Check for expected error patterns
    error_patterns = ["truncated", "Incomplete YouTube ID", "Video unavailable"]
    assert any(pattern in result.stderr for pattern in error_patterns), (
        f"Expected error message not found in: {result.stderr}"
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
    assert len(file_root.attrib) == 4, (
        "File transcript should have 4 empty metadata attributes"
    )
    assert file_root.attrib["video_title"] == "", (
        "File transcript video_title should be empty"
    )
    assert file_root.attrib["upload_date"] == "", (
        "File transcript upload_date should be empty"
    )
    assert file_root.attrib["duration"] == "", "File transcript duration should be empty"
    assert file_root.attrib["video_url"] == "", (
        "File transcript video_url should be empty"
    )
    assert len(url_root.attrib) >= 4, "URL transcript should have metadata attributes"
    assert "video_title" in url_root.attrib, "URL transcript missing video_title"

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
