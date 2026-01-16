"""Tests for the XML builder module.

Following TDD principles with focused separation of concerns.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING

from youtube_to_xml.models import (
    Chapter as ModelsChapter,
)
from youtube_to_xml.models import (
    TranscriptDocument,
    TranscriptLine,
    VideoMetadata,
)
from youtube_to_xml.xml_builder import transcript_to_xml

if TYPE_CHECKING:
    from pathlib import Path

# ============= FIXTURES =============


# ===========================================================
# ========== 👍 NEW TRANSCRIPT_TO_XML TDD TESTS ============
# ===========================================================

# ============= 1. FOUNDATION TESTS (Basic XML Structure) =============


def test_transcript_to_xml_empty_chapters() -> None:
    """Document with no chapters creates valid XML with empty chapters element."""
    document = TranscriptDocument(metadata=VideoMetadata(), chapters=[])
    xml = transcript_to_xml(document)
    root = ET.fromstring(xml)

    assert root.tag == "transcript"
    chapters_elem = root.find("chapters")
    assert chapters_elem is not None
    assert len(chapters_elem) == 0


def test_transcript_to_xml_basic_structure() -> None:
    """Single chapter with empty metadata produces expected XML elements and structure."""
    metadata = VideoMetadata()

    # Single chapter test data
    lines = [
        TranscriptLine(timestamp=2.0, text="Welcome to the session"),
        TranscriptLine(timestamp=150.0, text="Let's begin"),
    ]
    chapter = ModelsChapter(
        title="Introduction", start_time=2.0, end_time=180.0, transcript_lines=lines
    )

    document = TranscriptDocument(metadata=metadata, chapters=[chapter])
    xml = transcript_to_xml(document)

    # Verify complete XML structure
    assert '<transcript video_title="" video_published=""' in xml
    assert 'video_duration="" video_url="">' in xml
    assert "<chapters>" in xml
    assert '<chapter title="Introduction" start_time="0:02">' in xml
    assert "      0:02\n      Welcome to the session" in xml
    assert "      2:30\n      Let's begin" in xml
    assert "</chapter>" in xml
    assert "</chapters>" in xml
    assert "</transcript>" in xml


def test_transcript_to_xml_single_untitled_chapter() -> None:
    """Chapter with empty title produces XML with empty title attribute."""
    document = TranscriptDocument(
        metadata=VideoMetadata(),
        chapters=[
            ModelsChapter(
                title="",  # Empty title test case
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


# ============= 2. CONTENT FORMATTING TESTS (Data Processing) =============


def test_transcript_to_xml_metadata_formatting() -> None:
    """Metadata timestamps and durations are formatted for XML output."""
    metadata = VideoMetadata(
        video_title="Test Video",
        video_published="20250717",
        video_duration=163,
        video_url="https://youtube.com/watch?v=abc123",
    )
    document = TranscriptDocument(metadata=metadata, chapters=[])
    xml = transcript_to_xml(document)

    root = ET.fromstring(xml)
    assert root.get("video_title") == "Test Video"
    assert root.get("video_published") == "2025-07-17"
    assert root.get("video_duration") == "2m 43s"
    assert root.get("video_url") == "https://youtube.com/watch?v=abc123"


def test_transcript_to_xml_transcript_line_conversion() -> None:
    """TranscriptLine objects produce alternating timestamp and text lines in XML."""
    lines = [
        TranscriptLine(timestamp=0.0, text="Hello world"),
        TranscriptLine(timestamp=150.0, text="Goodbye world"),
    ]
    chapter = ModelsChapter(
        title="Test Chapter", start_time=0.0, end_time=200.0, transcript_lines=lines
    )
    document = TranscriptDocument(metadata=VideoMetadata(), chapters=[chapter])
    xml = transcript_to_xml(document)

    expected_chapter = """    <chapter title="Test Chapter" start_time="0:00">
      0:00
      Hello world
      2:30
      Goodbye world
    </chapter>"""

    assert expected_chapter in xml


# ============= 3. VALIDATION TESTS (XML Compliance) =============


def test_transcript_to_xml_special_character_handling() -> None:
    """Special characters in metadata and transcript content are XML-escaped."""
    lines = [TranscriptLine(0.0, 'Text with "quotes" & <tags>')]
    chapter = ModelsChapter('Chapter & "Title" <Test>', 0.0, 60.0, lines)
    metadata = VideoMetadata(video_title='Video & "Title" <Test>')
    document = TranscriptDocument(metadata=metadata, chapters=[chapter])

    xml_string = transcript_to_xml(document)

    assert "&amp;" in xml_string
    assert "&quot;" in xml_string
    assert "&lt;" in xml_string
    assert "&gt;" in xml_string

    root = ET.fromstring(xml_string)
    assert root.get("video_title") == 'Video & "Title" <Test>'
    chapter_elem = root.find(".//chapter")
    assert chapter_elem is not None
    assert chapter_elem.get("title") == 'Chapter & "Title" <Test>'


def test_transcript_to_xml_validation(tmp_path: Path) -> None:
    """Generated XML is well-formed and parseable by ElementTree."""
    lines = [
        TranscriptLine(timestamp=0.0, text='Welcome & "Getting Started" <Overview>'),
        TranscriptLine(timestamp=148.0, text="Let's dive into the topic"),
    ]
    chapter = ModelsChapter(
        title="Introduction", start_time=0.0, end_time=200.0, transcript_lines=lines
    )
    document = TranscriptDocument(metadata=VideoMetadata(), chapters=[chapter])
    xml_string = transcript_to_xml(document)

    xml_file = tmp_path / "test.xml"
    xml_file.write_text(xml_string, encoding="utf-8")

    parsed_tree = ET.parse(xml_file)
    parsed_root = parsed_tree.getroot()
    assert parsed_root is not None


def test_transcript_to_xml_xml_declaration() -> None:
    """XML output includes proper declaration header and newline ending."""
    lines = [TranscriptLine(timestamp=0.0, text="Welcome to today's session")]
    chapter = ModelsChapter(
        title="Introduction", start_time=0.0, end_time=60.0, transcript_lines=lines
    )
    document = TranscriptDocument(metadata=VideoMetadata(), chapters=[chapter])
    xml_string = transcript_to_xml(document)

    assert xml_string.startswith("<?xml version='1.0' encoding='utf-8'?>")
    assert xml_string.endswith("</transcript>\n")


def test_transcript_to_xml_indentation() -> None:
    """XML elements use correct indentation spacing (2 spaces per level)."""
    lines = [TranscriptLine(0.0, "Welcome"), TranscriptLine(148.0, "Content")]
    chapter = ModelsChapter("Test", 0.0, 60.0, lines)
    document = TranscriptDocument(VideoMetadata(), [chapter])
    xml_lines = transcript_to_xml(document).split("\n")

    # Verify indentation levels: 2 spaces per level, 6 for transcript content
    assert xml_lines[2] == "  <chapters>"  # Level 1: 2 spaces
    assert xml_lines[3].startswith("    <chapter")  # Level 2: 4 spaces
    assert xml_lines[4].startswith("      0:00")  # Content: 6 spaces
    assert xml_lines[8] == "    </chapter>"  # Closing: 4 spaces


# ============= 4. COMPREHENSIVE TESTS (Complete XML Generation) =============


def test_transcript_to_xml_multi_chapter_complete() -> None:
    """Multi-chapter document with metadata produces complete XML structure."""
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
