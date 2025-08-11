"""Tests for the transcript parser module.

Following TDD principles: each test drives one specific behavior.
Tests are ordered to incrementally build the parser functionality.
"""

import pytest

from youtube_to_xml.parser import (
    TIMESTAMP_PATTERN,
    Chapter,
    detect_chapter_boundaries,
    extract_chapter_content,
    find_timestamps,
    identify_first_chapter,
    parse_transcript,
    validate_transcript_format,
)


class TestTimestampDetection:
    """Tests for timestamp pattern matching and detection."""

    def test_timestamp_pattern_matching(self) -> None:
        """Verify regex matches valid timestamp formats."""
        valid_timestamps = [
            "0:00",  # M:SS
            "00:00",  # MM:SS
            "1:23:45",  # H:MM:SS
            "10:15:30",  # HH:MM:SS
        ]
        for ts in valid_timestamps:
            assert TIMESTAMP_PATTERN.match(ts), f"Should match: {ts}"

        invalid_patterns = [
            "Chapter Title",
            "Some content",
            "123:45",  # Too many digits for minutes
            "1:2:3",  # Invalid format
            "12:60",  # Invalid seconds
            "",
        ]
        for pattern in invalid_patterns:
            assert not TIMESTAMP_PATTERN.match(pattern), f"Should not match: {pattern}"

    def test_find_timestamps_in_text(self) -> None:
        """Find all timestamp line indices in multi-line text."""
        text = """Introduction
0:00
Welcome to the session
2:30
Let's begin
15:45
Chapter content here"""

        lines = text.splitlines()
        timestamp_indices = find_timestamps(lines)

        assert timestamp_indices == [1, 3, 5]
        assert lines[1] == "0:00"
        assert lines[3] == "2:30"
        assert lines[5] == "15:45"


class TestTranscriptValidation:
    """Tests for transcript format validation."""

    def test_validate_transcript_format(self) -> None:
        """Validate transcript format rules."""
        # Valid transcript
        valid_text = """Chapter Title
0:00
Content here"""
        assert validate_transcript_format(valid_text) is None

        # Empty transcript
        with pytest.raises(ValueError, match="empty"):
            validate_transcript_format("")

        # Starts with timestamp
        invalid_start = """0:00
Content here"""
        with pytest.raises(ValueError, match="timestamp"):
            validate_transcript_format(invalid_start)

        # No timestamps
        no_timestamps = """Chapter Title
Just content
No timestamps here"""
        with pytest.raises(ValueError, match="timestamp"):
            validate_transcript_format(no_timestamps)


class TestChapterDetection:
    """Tests for chapter identification rules."""

    def test_identify_first_chapter(self) -> None:
        """First non-timestamp line is always a chapter."""
        text = """Introduction
0:00
Welcome to the session
2:30
More content"""

        lines = text.splitlines()
        timestamp_indices = find_timestamps(lines)
        first_chapter = identify_first_chapter(lines, timestamp_indices)

        assert first_chapter is not None
        assert first_chapter.line_idx == 0
        assert first_chapter.name == "Introduction"
        assert first_chapter.start_timestamp == "0:00"

    def test_detect_chapter_boundaries(self) -> None:
        """When exactly 2 lines between timestamps, second line is new chapter."""
        text = """Introduction
0:00
First content
2:30
Second content
Chapter Two
5:00
Chapter Two content"""

        lines = text.splitlines()
        timestamp_indices = find_timestamps(lines)

        # Skip first chapter for this test
        subsequent_chapters = detect_chapter_boundaries(lines, timestamp_indices)

        assert len(subsequent_chapters) == 1
        assert subsequent_chapters[0].line_idx == 5
        assert subsequent_chapters[0].name == "Chapter Two"
        assert subsequent_chapters[0].start_timestamp == "5:00"


class TestContentExtraction:
    """Tests for extracting content lines for each chapter."""

    def test_extract_content_single_chapter(self) -> None:
        """Simplest case: transcript with only ONE chapter."""
        text = """Intro
0:00
Line 1
Line 2"""

        lines = text.splitlines()
        chapters = [
            Chapter(line_idx=0, name="Intro", start_timestamp="0:00", content=[])
        ]

        content = extract_chapter_content(lines, chapters, 0)
        assert content == ["0:00", "Line 1", "Line 2"]

    def test_extract_content_first_chapter(self) -> None:
        """First chapter when multiple exist."""
        text = """Chapter One
0:00
Content 1
2:30
Content 2
Chapter Two
5:00
Other content"""

        lines = text.splitlines()
        chapters = [
            Chapter(line_idx=0, name="Chapter One", start_timestamp="0:00", content=[]),
            Chapter(line_idx=5, name="Chapter Two", start_timestamp="5:00", content=[]),
        ]

        content = extract_chapter_content(lines, chapters, 0)
        # Should stop before "Chapter Two" line
        assert content == ["0:00", "Content 1", "2:30", "Content 2"]

    def test_extract_content_middle_chapter(self) -> None:
        """Middle chapter between two others."""
        text = """Chapter One
0:00
Content 1
2:30
Content 2
Chapter Two
5:00
Middle content
7:30
More middle
Chapter Three
10:00
Final content"""

        lines = text.splitlines()
        chapters = [
            Chapter(line_idx=0, name="Chapter One", start_timestamp="0:00", content=[]),
            Chapter(line_idx=5, name="Chapter Two", start_timestamp="5:00", content=[]),
            Chapter(
                line_idx=10, name="Chapter Three", start_timestamp="10:00", content=[]
            ),
        ]

        content = extract_chapter_content(lines, chapters, 1)
        # Should include from "5:00" to before "Chapter Three"
        assert content == ["5:00", "Middle content", "7:30", "More middle"]

    def test_extract_content_last_chapter(self) -> None:
        """Last chapter includes all remaining lines to EOF."""
        text = """Chapter One
0:00
Content 1
2:30
Content 2
Last Chapter
5:00
Final content
7:30
More content
Even more content"""

        lines = text.splitlines()
        chapters = [
            Chapter(line_idx=0, name="Chapter One", start_timestamp="0:00", content=[]),
            Chapter(
                line_idx=5, name="Last Chapter", start_timestamp="5:00", content=[]
            ),
        ]

        content = extract_chapter_content(lines, chapters, 1)
        # Should include everything from "5:00" to end
        assert content == [
            "5:00",
            "Final content",
            "7:30",
            "More content",
            "Even more content",
        ]


class TestEndToEnd:
    """Integration tests for complete parsing pipeline."""

    def test_parse_simple_transcript(self) -> None:
        """End-to-end with 2-chapter transcript."""
        text = """Introduction
0:00
Welcome to today's session
2:28
Let's dive into the topic
Getting Started
1:15:30
Download the software
2:45:12
Configure it"""

        chapters = parse_transcript(text)

        assert len(chapters) == 2

        # First chapter
        assert chapters[0].name == "Introduction"
        assert chapters[0].start_timestamp == "0:00"
        assert chapters[0].line_idx == 0
        assert chapters[0].content == [
            "0:00",
            "Welcome to today's session",
            "2:28",
            "Let's dive into the topic",
        ]

        # Second chapter
        assert chapters[1].name == "Getting Started"
        assert chapters[1].start_timestamp == "1:15:30"
        assert chapters[1].line_idx == 5
        assert chapters[1].content == [
            "1:15:30",
            "Download the software",
            "2:45:12",
            "Configure it",
        ]

    def test_parse_edge_cases(self) -> None:
        """Test edge cases and special characters."""
        # Empty text
        with pytest.raises(ValueError, match="empty"):
            parse_transcript("")

        # No timestamps
        with pytest.raises(ValueError, match="timestamp"):
            parse_transcript("Just text\nNo timestamps")

        # Starts with timestamp
        with pytest.raises(ValueError, match="timestamp"):
            parse_transcript("0:00\nContent")

        # Special characters in chapter names
        text = """Special & "Characters" <XML>
0:00
Content with , erm, "quotes"
10:15:30
Multi-hour timestamp"""

        chapters = parse_transcript(text)
        assert len(chapters) == 1
        assert chapters[0].name == """Special & "Characters" <XML>"""
        assert chapters[0].content[1] == """Content with , erm, "quotes\""""
        assert "10:15:30" in chapters[0].content
