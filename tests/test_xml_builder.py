"""Tests for the XML builder module.

Following TDD principles with focused separation of concerns.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from youtube_to_xml.parser import Chapter
from youtube_to_xml.xml_builder import chapters_to_xml

# ============= FIXTURES =============


@pytest.fixture
def single_chapter() -> list[Chapter]:
    """Single chapter with special characters for testing."""
    return [
        Chapter(
            title='Introduction & "Getting Started" <Overview>',
            start_time="0:00",
            content_lines=[
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
            start_time="0:00",
            content_lines=[
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
            start_time="1:15:30",
            content_lines=[
                "1:15:30",
                "Download the software",
                "2:45:12",
                'Configure it , erm, how "you" like it',
            ],
        ),
        Chapter(
            title="Advanced Features & Tips",
            start_time="10:15:30",
            content_lines=["10:15:30", "Final thoughts on implementation"],
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

    # Content line counts (structure validation)
    ch0_text = chapters[0].text or ""
    ch1_text = chapters[1].text or ""
    ch2_text = chapters[2].text or ""
    assert len(ch0_text.strip().split("\n")) == 8  # Introduction content lines
    assert len(ch1_text.strip().split("\n")) == 4  # Getting Started content lines
    assert len(ch2_text.strip().split("\n")) == 2  # Advanced Features content lines


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
    """XML output follows template indentation: 2 spaces per level, 6 for content."""
    xml_string = chapters_to_xml(single_chapter)
    lines = xml_string.split("\n")

    # Element indentation (2 spaces per level per ET.indent)
    assert lines[1] == "<transcript>"  # 0 spaces - root level
    assert lines[2] == "  <chapters>"  # 2 spaces - level 1
    assert lines[3].startswith("    <chapter")  # 4 spaces - level 2

    # Content indentation (6 spaces = 3 levels deep x 2 spaces per level)
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
