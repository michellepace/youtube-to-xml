"""Integration tests for end-to-end validation of CLI and YouTube fetcher."""

import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

# Test constants
SCRIPT_PATH = Path.cwd() / "scripts/transcript_auto_fetcher.py"
EXAMPLES_DIR = Path("example_transcripts")
HOOKS_URL = "https://www.youtube.com/watch?v=Q4gsvJvRjCU"
HOOKS_URL_SHARED = "https://youtu.be/Q4gsvJvRjCU?si=8cEkF7OrXrB1R4d7&t=27"
PICKUP_URL_NO_CHAPTERS = "https://www.youtube.com/watch?v=UdoY2l5TZaA"
INVALID_URL = "https://www.youtube.com/watch?v=InvdilB"
SUBPROCESS_TIMEOUT = 20


@pytest.mark.integration
def test_file_multi_chapters_success(tmp_path: Path) -> None:
    """Test CLI processing of file with multiple chapters."""
    # Copy input file to tmp directory and run CLI there
    input_file = EXAMPLES_DIR / "x4-chapters.txt"
    (tmp_path / "input.txt").write_text(input_file.read_text(encoding="utf-8"))

    result = subprocess.run(
        ["uv", "run", "youtube-to-xml", "input.txt"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )

    assert result.returncode == 0
    assert "Created:" in result.stdout

    # Verify output matches reference file exactly
    output_file = tmp_path / "input.xml"
    reference_file = EXAMPLES_DIR / "x4-chapters.xml"

    assert output_file.exists()
    assert output_file.read_text(encoding="utf-8") == reference_file.read_text(
        encoding="utf-8"
    )


@pytest.mark.integration
def test_file_chapters_with_blanks_success(tmp_path: Path) -> None:
    """Test CLI processing of file with chapters containing blank lines."""
    input_file = EXAMPLES_DIR / "x3-chapters-with-blanks.txt"
    (tmp_path / "input.txt").write_text(input_file.read_text(encoding="utf-8"))

    result = subprocess.run(
        ["uv", "run", "youtube-to-xml", "input.txt"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )

    assert result.returncode == 0
    assert "Created:" in result.stdout

    output_file = tmp_path / "input.xml"
    reference_file = EXAMPLES_DIR / "x3-chapters-with-blanks.xml"

    assert output_file.exists()
    assert output_file.read_text(encoding="utf-8") == reference_file.read_text(
        encoding="utf-8"
    )


@pytest.mark.integration
def test_file_invalid_format_error(tmp_path: Path) -> None:
    """Test CLI error handling for invalid transcript format."""
    input_file = EXAMPLES_DIR / "x0-chapters-invalid-format.txt"
    (tmp_path / "input.txt").write_text(input_file.read_text(encoding="utf-8"))

    result = subprocess.run(
        ["uv", "run", "youtube-to-xml", "input.txt"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )

    assert result.returncode == 1
    assert "Wrong format" in result.stdout
    assert "youtube-to-xml --help" in result.stdout


@pytest.mark.integration
def test_url_multi_chapters_success(tmp_path: Path) -> None:
    """Test YouTube fetcher with multi-chapter video."""
    result = subprocess.run(  # noqa: S603
        [
            "uv",
            "run",
            "python",
            str(SCRIPT_PATH),
            HOOKS_URL,
        ],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        timeout=SUBPROCESS_TIMEOUT,
        check=False,
    )

    assert result.returncode == 0
    assert "✅ Saved to:" in result.stdout

    # Find the generated XML file
    xml_files = list(tmp_path.glob("*.xml"))
    assert len(xml_files) == 1, "Expected exactly one XML file to be generated"

    # Compare with reference if it exists
    reference_file = EXAMPLES_DIR / "how-claude-code-hooks-save-me-hours-daily.xml"
    if reference_file.exists():
        output_content = xml_files[0].read_text(encoding="utf-8")
        reference_content = reference_file.read_text(encoding="utf-8")
        assert output_content == reference_content


@pytest.mark.integration
def test_url_multi_chapters_shared_success(tmp_path: Path) -> None:
    """Test YouTube fetcher with shared URL format containing parameters."""
    result = subprocess.run(  # noqa: S603
        [
            "uv",
            "run",
            "python",
            str(SCRIPT_PATH),
            HOOKS_URL_SHARED,
        ],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        timeout=SUBPROCESS_TIMEOUT,
        check=False,
    )

    assert result.returncode == 0
    assert "✅ Saved to:" in result.stdout

    xml_files = list(tmp_path.glob("*.xml"))
    assert len(xml_files) == 1

    reference_file = EXAMPLES_DIR / "how-claude-code-hooks-save-me-hours-daily.xml"
    if reference_file.exists():
        output_content = xml_files[0].read_text(encoding="utf-8")
        reference_content = reference_file.read_text(encoding="utf-8")
        assert output_content == reference_content


@pytest.mark.integration
def test_url_single_chapter_success(tmp_path: Path) -> None:
    """Test YouTube fetcher with single-chapter video."""
    result = subprocess.run(  # noqa: S603
        [
            "uv",
            "run",
            "python",
            str(SCRIPT_PATH),
            PICKUP_URL_NO_CHAPTERS,
        ],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        timeout=SUBPROCESS_TIMEOUT,
        check=False,
    )

    assert result.returncode == 0
    assert "✅ Saved to:" in result.stdout

    xml_files = list(tmp_path.glob("*.xml"))
    assert len(xml_files) == 1

    reference_file = EXAMPLES_DIR / "pick-up-where-you-left-off-with-claude.xml"
    if reference_file.exists():
        output_content = xml_files[0].read_text(encoding="utf-8")
        reference_content = reference_file.read_text(encoding="utf-8")
        assert output_content == reference_content


@pytest.mark.integration
def test_url_invalid_format_error(tmp_path: Path) -> None:
    """Test YouTube fetcher error handling for invalid URL."""
    result = subprocess.run(  # noqa: S603
        [
            "uv",
            "run",
            "python",
            str(SCRIPT_PATH),
            INVALID_URL,
        ],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        timeout=SUBPROCESS_TIMEOUT,
        check=False,
    )

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

    file_result = subprocess.run(
        ["uv", "run", "youtube-to-xml", "input.txt"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        check=False,
    )

    # Process URL method
    url_result = subprocess.run(  # noqa: S603
        ["uv", "run", "python", str(SCRIPT_PATH), HOOKS_URL],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        timeout=SUBPROCESS_TIMEOUT,
        check=False,
    )

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

    # 1. Assert both files have similar line counts (content volume)
    file_lines = len(file_xml.read_text(encoding="utf-8").splitlines())
    url_lines = len(url_xml.read_text(encoding="utf-8").splitlines())
    assert abs(file_lines - url_lines) <= 3, "Line count differs significantly"

    # 2. Assert transcript element attributes
    assert len(file_root.attrib) == 0, "File transcript should have no attributes"
    assert len(url_root.attrib) >= 1, "URL transcript should have metadata attributes"
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
