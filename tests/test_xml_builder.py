"""Tests for the XML builder module.

Following TDD principles with focused separation of concerns.
"""

import math
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from youtube_to_xml.file_parser import Chapter
from youtube_to_xml.models import (
    Chapter as ModelsChapter,
)
from youtube_to_xml.models import (
    TranscriptDocument,
    TranscriptLine,
    VideoMetadata,
)
from youtube_to_xml.xml_builder import chapters_to_xml, transcript_to_xml

# ============= FIXTURES =============


@pytest.fixture
def single_chapter() -> list[Chapter]:
    """Single chapter with special characters for testing."""
    return [
        Chapter(
            title='Introduction & "Getting Started" <Overview>',
            start_time=0.0,
            end_time=math.inf,
            transcript_lines=[
                "0:00",
                "Welcome to today's session",
                "2:28",
                'Let\'s dive into the topic with "quotes" & <tags>',
            ],
        )
    ]


@pytest.fixture
def multiple_chapters() -> list[Chapter]:
    """Multiple chapters for testing."""
    return [
        Chapter(
            title="Introduction",
            start_time=0.0,
            end_time=4530.0,
            transcript_lines=[
                "0:00",
                "Welcome to today's session",
                "2:28",
                "Let's dive into the topic",
                "15:45",
                "First point about methodology",
                "23:30",
                "Second point here",
            ],
        ),
        Chapter(
            title="Getting Started Guide",
            start_time=4530.0,
            end_time=36930.0,
            transcript_lines=[
                "1:15:30",
                "Download the software",
                "2:45:12",
                'Configure it , erm, how "you" like it',
            ],
        ),
        Chapter(
            title="Advanced Features & Tips",
            start_time=36930.0,
            end_time=math.inf,
            transcript_lines=["10:15:30", "Final thoughts on implementation"],
        ),
    ]


# ============= EDGE CASE TESTS =============


def test_empty_chapters_creates_valid_structure() -> None:
    """Empty chapter list creates valid XML with empty chapters element."""
    xml_string = chapters_to_xml([])
    root = ET.fromstring(xml_string)

    assert root.tag == "transcript"
    chapters_elem = root.find("chapters")
    assert chapters_elem is not None
    assert len(chapters_elem) == 0


# ============= VALIDATION TESTS =============


def test_xml_is_valid_and_parseable(
    single_chapter: list[Chapter], tmp_path: Path
) -> None:
    """Generated XML can be parsed successfully by ElementTree."""
    xml_string = chapters_to_xml(single_chapter)

    # Write to file and parse - should not raise exception
    xml_file = tmp_path / "test.xml"
    xml_file.write_text(xml_string, encoding="utf-8")

    # Parsing validation is the core purpose of this test
    parsed_tree = ET.parse(xml_file)
    parsed_root = parsed_tree.getroot()
    assert parsed_root is not None  # Minimal assertion - just verify it parsed


# ============= STRUCTURE TESTS =============


def test_builds_correct_xml_structure(multiple_chapters: list[Chapter]) -> None:
    """XML has correct structure with proper elements, attributes, and content."""
    xml_string = chapters_to_xml(multiple_chapters)
    root = ET.fromstring(xml_string)

    # Root structure
    assert root.tag == "transcript"
    assert len(root) == 1
    assert root[0].tag == "chapters"

    # Chapter elements
    chapters = root.findall(".//chapter")
    assert len(chapters) == 3

    # Chapter attributes
    assert chapters[0].get("title") == "Introduction"
    assert chapters[0].get("start_time") == "0:00"
    assert chapters[1].get("title") == "Getting Started Guide"
    assert chapters[1].get("start_time") == "1:15:30"
    assert chapters[2].get("title") == "Advanced Features & Tips"
    assert chapters[2].get("start_time") == "10:15:30"

    # Transcript line counts (structure validation)
    ch0_text = chapters[0].text or ""
    ch1_text = chapters[1].text or ""
    ch2_text = chapters[2].text or ""
    assert len(ch0_text.strip().split("\n")) == 8  # Introduction transcript lines
    assert len(ch1_text.strip().split("\n")) == 4  # Getting Started transcript lines
    assert len(ch2_text.strip().split("\n")) == 2  # Advanced Features transcript lines


# ============= ESCAPING TESTS =============


def test_escapes_special_xml_characters(single_chapter: list[Chapter]) -> None:
    """Special XML characters are properly escaped in output."""
    xml_string = chapters_to_xml(single_chapter)

    # ElementTree automatically escapes these characters
    assert "&amp;" in xml_string  # & becomes &amp;
    assert "&quot;" in xml_string  # " becomes &quot;
    assert "&lt;" in xml_string  # < becomes &lt;
    assert "&gt;" in xml_string  # > becomes &gt;


# ============= FORMAT TESTS =============


def test_includes_xml_declaration(single_chapter: list[Chapter]) -> None:
    """XML output includes proper declaration."""
    xml_string = chapters_to_xml(single_chapter)
    assert xml_string.startswith("<?xml version='1.0' encoding='utf-8'?>")
    assert xml_string.endswith("</transcript>\n")  # Should end with newline


def test_matches_template_indentation(single_chapter: list[Chapter]) -> None:
    """XML output follows template indentation: 2 spaces per level, 6 for transcript."""
    xml_string = chapters_to_xml(single_chapter)
    lines = xml_string.split("\n")

    # Element indentation (2 spaces per level per ET.indent)
    transcript_line = lines[1]
    assert transcript_line.startswith("<transcript "), "Root has attributes"
    assert transcript_line.endswith(">"), "Root transcript element should be well-formed"
    assert lines[2] == "  <chapters>"  # 2 spaces - level 1
    assert lines[3].startswith("    <chapter")  # 4 spaces - level 2

    # Transcript text indentation (6 spaces = 3 levels deep x 2 spaces per level)
    assert lines[4].startswith("      0:00")  # 6 spaces
    assert lines[5].startswith("      Welcome to today's session")  # 6 spaces

    # Closing tag indentation - should be on separate line with proper indent
    # Find the closing chapter tag line
    chapter_close_lines = [i for i, line in enumerate(lines) if "</chapter>" in line]
    assert len(chapter_close_lines) > 0, "Should have closing chapter tags"

    for line_idx in chapter_close_lines:
        line = lines[line_idx]
        # Closing chapter tag should be on its own line with 4 spaces (level 2)
        assert line == "    </chapter>", f"Expected '    </chapter>', got '{line}'"


# ===========================================================
# ============= NEW TRANSCRIPT_TO_XML TDD TESTS =============
# ===========================================================


def test_url_method_formatted_metadata() -> None:
    """Populated metadata should be formatted via time_utils."""
    metadata = VideoMetadata(
        video_title="Test Video",
        video_published="20250717",  # Raw YYYYMMDD
        video_duration=163,  # Raw seconds
        video_url="https://youtube.com/watch?v=abc123",
    )
    document = TranscriptDocument(metadata=metadata, chapters=[])
    xml = transcript_to_xml(document)

    # Parse XML for robust attribute checking
    root = ET.fromstring(xml)
    assert root.get("video_title") == "Test Video"
    assert root.get("video_published") == "2025-07-17"  # Formatted by time_utils
    assert root.get("video_duration") == "2m 43s"  # Formatted by time_utils
    assert root.get("video_url") == "https://youtube.com/watch?v=abc123"


def test_transcript_lines_formatted_correctly() -> None:
    """TranscriptLine objects should format as timestamp + text pairs."""
    lines = [
        TranscriptLine(timestamp=0.0, text="Hello world"),
        TranscriptLine(timestamp=150.0, text="Goodbye world"),
    ]
    chapter = ModelsChapter(
        title="Test Chapter", start_time=0.0, end_time=200.0, transcript_lines=lines
    )
    document = TranscriptDocument(metadata=VideoMetadata(), chapters=[chapter])
    xml = transcript_to_xml(document)

    # Should have alternating timestamp/text pattern with proper indentation
    # 150.0 seconds = 2:30 (2 minutes, 30 seconds)
    assert "      0:00\n      Hello world\n      2:30\n      Goodbye world" in xml


def test_chapters_to_xml_still_works() -> None:
    """Existing function should be unchanged."""
    old_chapter = Chapter(
        title="Old Format",
        start_time=0.0,
        end_time=60.0,
        transcript_lines=["0:00", "Old style text"],
    )
    xml = chapters_to_xml([old_chapter])

    # Parse and verify structure
    root = ET.fromstring(xml)
    chapter_elem = root.find(".//chapter")
    assert chapter_elem is not None
    assert chapter_elem.get("title") == "Old Format"


# ============= EDGE CASE TESTS =============


def test_special_characters_in_metadata() -> None:
    """Metadata with XML special characters should be escaped."""
    metadata = VideoMetadata(
        video_title='Test & "Special" <Characters>',
        video_url="https://youtube.com/watch?v=test&t=10s",
    )
    document = TranscriptDocument(metadata=metadata, chapters=[])
    xml = transcript_to_xml(document)

    # XML should be valid despite special characters
    root = ET.fromstring(xml)
    assert root.get("video_title") == 'Test & "Special" <Characters>'
    assert root.get("video_url") == "https://youtube.com/watch?v=test&t=10s"


def test_output_structure_matches_existing_format() -> None:
    """New function output should match existing XML structure exactly."""
    # Create equivalent data - empty metadata like file method
    metadata = VideoMetadata()  # All defaults (empty strings, 0 duration)

    # Single chapter with transcript lines (structured format)
    lines = [
        TranscriptLine(timestamp=2.0, text="Welcome to the session"),
        TranscriptLine(timestamp=150.0, text="Let's begin"),
    ]
    chapter = ModelsChapter(
        title="Introduction", start_time=2.0, end_time=180.0, transcript_lines=lines
    )

    document = TranscriptDocument(metadata=metadata, chapters=[chapter])
    xml = transcript_to_xml(document)

    # Should have same overall structure as existing format
    assert '<transcript video_title="" video_published=""' in xml
    assert 'video_duration="" video_url="">' in xml
    assert "<chapters>" in xml
    assert '<chapter title="Introduction" start_time="0:02">' in xml
    assert "      0:02\n      Welcome to the session" in xml
    assert "      2:30\n      Let's begin" in xml
    assert "</chapter>" in xml
    assert "</chapters>" in xml
    assert "</transcript>" in xml


# ============= Michelle Refactor Later (integration?) =============


def test_file_without_chapters() -> None:
    """File without chapters returns one chapter (without title)."""
    # Create document with no explicit chapter structure
    document = TranscriptDocument(
        metadata=VideoMetadata(),  # Empty metadata for file method
        chapters=[
            ModelsChapter(
                title="",  # No title when no chapters detected
                start_time=6.0,
                end_time=18.0,
                transcript_lines=[
                    TranscriptLine(6.0, "[Music]"),
                    TranscriptLine(15.0, "I'm so"),
                    TranscriptLine(18.0, "[Music]"),
                ],
            )
        ],
    )

    xml = transcript_to_xml(document)

    expected = """<?xml version='1.0' encoding='utf-8'?>
<transcript video_title="" video_published="" video_duration="" video_url="">
  <chapters>
    <chapter title="" start_time="0:06">
      0:06
      [Music]
      0:15
      I'm so
      0:18
      [Music]
    </chapter>
  </chapters>
</transcript>
"""

    assert xml == expected


def test_complete_structure_integration() -> None:
    """Integration test: Real transcript data → XML using pythonic model construction.

    This test uses data extracted from example_transcripts/x4-chapters.xml
    to verify our transcript_to_xml() function works with realistic data.
    Tests URL method scenario with populated metadata that gets formatted.
    Uses direct model construction to demonstrate clean, readable test patterns.
    """
    # Create complete document using natural model construction
    document = TranscriptDocument(
        metadata=VideoMetadata(
            video_title="How Claude Code Hooks Work",
            video_published="20250717",
            video_duration=163,
            video_url="https://youtube.com/watch?v=test123",
        ),
        chapters=[
            ModelsChapter(
                title="Intro",
                start_time=0.0,
                end_time=20.0,
                transcript_lines=[
                    TranscriptLine(0.0, "Hooks are hands down one of the best"),
                    TranscriptLine(2.0, "features in Claude Code and for some"),
                    TranscriptLine(5.0, "reason a lot of people don't know about"),
                ],
            ),
            ModelsChapter(
                title="Hooks",
                start_time=20.0,
                end_time=56.0,
                transcript_lines=[
                    TranscriptLine(20.0, "To create your first hook, use the hooks"),
                    TranscriptLine(22.0, "slash command, which shows this scary"),
                    TranscriptLine(25.0, "looking warning because hooks are"),
                ],
            ),
        ],
    )

    # Generate XML using our new interface
    xml = transcript_to_xml(document)

    # Parse XML for structured assertions (more reliable than string matching)
    root = ET.fromstring(xml)

    # Verify XML declaration and root structure
    assert xml.startswith("<?xml version='1.0' encoding='utf-8'?>")
    assert root.tag == "transcript"

    # Verify metadata attributes (URL method - populated and formatted)
    assert root.get("video_title") == "How Claude Code Hooks Work"
    assert root.get("video_published") == "2025-07-17"  # Formatted by time_utils
    assert root.get("video_duration") == "2m 43s"  # Formatted by time_utils
    assert root.get("video_url") == "https://youtube.com/watch?v=test123"

    # Verify chapters structure
    chapters_elem = root.find("chapters")
    assert chapters_elem is not None
    chapter_elems = chapters_elem.findall("chapter")
    assert len(chapter_elems) == 2

    # Verify chapter attributes
    intro_chapter, hooks_chapter = chapter_elems
    assert intro_chapter.get("title") == "Intro"
    assert intro_chapter.get("start_time") == "0:00"
    assert hooks_chapter.get("title") == "Hooks"
    assert hooks_chapter.get("start_time") == "0:20"

    # Verify transcript content (alternating timestamp/text pattern)
    intro_text = intro_chapter.text.strip().split("\n") if intro_chapter.text else []
    intro_lines = [line.strip() for line in intro_text if line.strip()]

    # Check transcript lines in intro chapter (3 lines = 6 elements total)
    assert intro_lines[0] == "0:00"
    assert intro_lines[1] == "Hooks are hands down one of the best"
    assert intro_lines[2] == "0:02"
    assert intro_lines[3] == "features in Claude Code and for some"
    assert intro_lines[4] == "0:05"
    assert intro_lines[5] == "reason a lot of people don't know about"

    # Check transcript lines in hooks chapter (3 lines = 6 elements)
    hooks_text = hooks_chapter.text.strip().split("\n") if hooks_chapter.text else []
    hooks_lines = [line.strip() for line in hooks_text if line.strip()]

    assert hooks_lines[0] == "0:20"
    assert hooks_lines[1] == "To create your first hook, use the hooks"
    assert hooks_lines[2] == "0:22"
    assert hooks_lines[3] == "slash command, which shows this scary"
    assert hooks_lines[4] == "0:25"
    assert hooks_lines[5] == "looking warning because hooks are"
