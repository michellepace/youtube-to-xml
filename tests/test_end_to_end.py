"""End-to-end workflow tests for successful user scenarios.

Tests complete successful workflows from user input to final output:
- File-based workflow: transcript file → CLI → XML output
- URL-based workflow: YouTube URL → url_to_transcript.py → YouTube API → XML output
- File vs URL equivalence verification

Uses unified run_script() helper with automatic rate limiting protection.
Integration tests (marked with @pytest.mark.integration) hit external YouTube API.
For error scenarios, see tests/test_exceptions_ytdlp.py.
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


def run_script(
    command: str, args: list[str] | str, tmp_path: Path, *, legacy: bool = False
) -> tuple[int, str]:
    """Run script and return (exit_code, output).

    Args:
        command: Either 'youtube-to-xml' or 'url-to-transcript'
        args: List of arguments or single URL string
        tmp_path: Working directory for the command
        legacy: If True, add --legacy flag for youtube-to-xml commands
    """
    if isinstance(args, str):
        # Single URL for url-to-transcript
        cmd_args = ["uv", "run", command, args]
    else:
        # List of args for youtube-to-xml
        cmd_args = ["uv", "run", command]
        if legacy and command == "youtube-to-xml":
            cmd_args.append("--legacy")
        cmd_args.extend(args)

    result = subprocess.run(  # noqa: S603
        cmd_args,
        capture_output=True,
        text=True,
        cwd=tmp_path,
        timeout=15,
        check=False,
    )

    # Handle rate limiting - skip test if encountered
    if result.returncode != 0:
        output = (result.stderr + result.stdout).lower()
        if any(pattern in output for pattern in ["429", "rate limit", "bot protection"]):
            pytest.skip("YouTube rate limited or bot protection triggered")

    return result.returncode, result.stdout + result.stderr


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


@pytest.mark.parametrize("use_legacy", [False, True])
def test_file_multi_chapters_success(tmp_path: Path, *, use_legacy: bool) -> None:
    """Test CLI processing of file with multiple chapters."""
    input_file = EXAMPLES_DIR / "x4-chapters.txt"
    (tmp_path / "input.txt").write_text(input_file.read_text(encoding="utf-8"))

    exit_code, output = run_script(
        "youtube-to-xml", ["input.txt"], tmp_path, legacy=use_legacy
    )

    assert exit_code == 0
    assert "Created:" in output

    # Verify output matches reference file exactly
    output_file = tmp_path / "input.xml"
    reference_file = setup_reference_file(tmp_path, "x4-chapters.xml")

    assert output_file.exists()
    assert_files_identical(output_file, reference_file)


@pytest.mark.parametrize("use_legacy", [False, True])
def test_file_chapters_with_blanks_success(tmp_path: Path, *, use_legacy: bool) -> None:
    """Test CLI processing of file with chapters containing blank lines."""
    input_file = EXAMPLES_DIR / "x3-chapters-with-blanks.txt"
    (tmp_path / "input.txt").write_text(input_file.read_text(encoding="utf-8"))

    exit_code, output = run_script(
        "youtube-to-xml", ["input.txt"], tmp_path, legacy=use_legacy
    )

    assert exit_code == 0
    assert "Created:" in output

    output_file = tmp_path / "input.xml"
    reference_file = setup_reference_file(tmp_path, "x3-chapters-with-blanks.xml")

    assert output_file.exists()
    assert_files_identical(output_file, reference_file)


@pytest.mark.parametrize("use_legacy", [False, True])
def test_file_invalid_format_error(tmp_path: Path, *, use_legacy: bool) -> None:
    """Test CLI error handling for invalid transcript format."""
    input_file = EXAMPLES_DIR / "x0-chapters-invalid-format.txt"
    (tmp_path / "input.txt").write_text(input_file.read_text(encoding="utf-8"))

    exit_code, output = run_script(
        "youtube-to-xml", ["input.txt"], tmp_path, legacy=use_legacy
    )

    assert exit_code == 1
    assert "Wrong format" in output


@pytest.mark.integration
def test_url_multi_chapters_success(tmp_path: Path) -> None:
    """Test YouTube fetcher with multi-chapter video."""
    exit_code, output = run_script("url-to-transcript", URL_CHAPTERS, tmp_path)

    assert exit_code == 0
    assert "✅ Created" in output

    xml_files = list(tmp_path.glob("*.xml"))
    assert len(xml_files) == 1, "Expected exactly one XML file to be generated"

    reference_file = setup_reference_file(
        tmp_path, "how-claude-code-hooks-save-me-hours-daily.xml"
    )
    assert_files_identical(xml_files[0], reference_file)


@pytest.mark.integration
def test_url_multi_chapters_shared_success(tmp_path: Path) -> None:
    """Test YouTube fetcher with shared URL format containing parameters."""
    exit_code, output = run_script("url-to-transcript", URL_CHAPTERS_SHARED, tmp_path)

    assert exit_code == 0
    assert "✅ Created" in output

    xml_files = list(tmp_path.glob("*.xml"))
    assert len(xml_files) == 1

    reference_file = setup_reference_file(
        tmp_path, "how-claude-code-hooks-save-me-hours-daily.xml"
    )
    assert_files_identical(xml_files[0], reference_file)


@pytest.mark.integration
def test_url_single_chapter_success(tmp_path: Path) -> None:
    """Test YouTube fetcher with single-chapter video."""
    exit_code, output = run_script("url-to-transcript", URL_NO_CHAPTERS, tmp_path)

    assert exit_code == 0
    assert "✅ Created" in output

    xml_files = list(tmp_path.glob("*.xml"))
    assert len(xml_files) == 1

    reference_file = setup_reference_file(
        tmp_path, "pick-up-where-you-left-off-with-claude.xml"
    )
    assert_files_identical(xml_files[0], reference_file)


@pytest.mark.integration
def test_url_vs_file_equivalent_output(tmp_path: Path) -> None:
    """Test URL vs file processing equivalence using direct XML parsing."""
    # Process file method
    input_file = EXAMPLES_DIR / "how-claude-code-hooks-save-me-hours-daily.txt"
    (tmp_path / "input.txt").write_text(input_file.read_text(encoding="utf-8"))

    file_exit_code = run_script("youtube-to-xml", ["input.txt"], tmp_path)[0]

    # Process URL method
    url_exit_code = run_script("url-to-transcript", URL_CHAPTERS, tmp_path)[0]

    assert file_exit_code == 0
    assert url_exit_code == 0

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
def test_url_manual_transcript_priority(tmp_path: Path) -> None:
    """Test manual transcripts are prioritised over auto-generated (higher quality)."""
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    exit_code, output = run_script("url-to-transcript", test_url, tmp_path)

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
    first_6_lines = content_lines[:6]

    # Expect to use manual transcripts as priorty
    expected_manual_version = [
        "0:01",
        "[♪♪♪]",
        "0:18",
        "♪ We're no strangers to love ♪",
        "0:22",
        "♪ You know the rules and so do I ♪",
    ]
    assert first_6_lines == expected_manual_version, (
        f"Expected clean manual transcript, got: {first_6_lines}"
    )

    # Auto generated transcript (messier)
    autogen_version = [
        "0:00",
        "[Music]",
        "0:18",
        "We're no strangers to",
        "0:21",
        "love. You know the rules and so do",
    ]
    assert first_6_lines != autogen_version, (
        "Should not match messy auto-generated transcript"
    )


# ================================================================================
# LEGACY FLAG TESTS - PR4: CLI dual-interface with --legacy flag support
# These tests ensure both legacy and new parser paths work identically
# ================================================================================


@pytest.mark.parametrize(
    ("test_file", "reference_file"),
    [
        ("x4-chapters.txt", "x4-chapters.xml"),
        ("x3-chapters-with-blanks.txt", "x3-chapters-with-blanks.xml"),
    ],
)
def test_legacy_vs_new_path_identical_output(
    tmp_path: Path, test_file: str, reference_file: str
) -> None:
    """Test that legacy and new paths produce identical output for example files."""
    # Setup input file
    input_file = EXAMPLES_DIR / test_file
    test_input = tmp_path / "input.txt"
    test_input.write_text(input_file.read_text(encoding="utf-8"))

    # Run with legacy flag
    exit_code_legacy, output_legacy = run_script(
        "youtube-to-xml", ["input.txt"], tmp_path, legacy=True
    )
    assert exit_code_legacy == 0
    assert "Created:" in output_legacy

    # Read legacy output
    legacy_xml = (tmp_path / "input.xml").read_text(encoding="utf-8")
    (tmp_path / "input.xml").unlink()  # Remove for second run

    # Run without legacy flag (new path)
    exit_code_new, output_new = run_script(
        "youtube-to-xml", ["input.txt"], tmp_path, legacy=False
    )
    assert exit_code_new == 0
    assert "Created:" in output_new

    # Read new output
    new_xml = (tmp_path / "input.xml").read_text(encoding="utf-8")

    # Outputs should be identical
    assert legacy_xml == new_xml

    # Both should match reference
    reference_file_path = setup_reference_file(tmp_path, reference_file)
    reference_content = reference_file_path.read_text(encoding="utf-8")
    assert legacy_xml == reference_content
    assert new_xml == reference_content
