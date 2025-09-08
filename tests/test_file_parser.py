"""Tests for the transcript parser module.

Following TDD principles with modern pytest patterns.
Uses fixtures to reduce duplication and improve maintainability.
"""

import math

import pytest

from youtube_to_xml.exceptions import (
    FileEmptyError,
    FileInvalidFormatError,
)
from youtube_to_xml.file_parser import (
    find_timestamps,
    parse_transcript_file,
    validate_transcript_format,
)
from youtube_to_xml.time_utils import (
    seconds_to_timestamp,
)

# ============= FIXTURES =============


@pytest.fixture
def simple_transcript() -> str:
    """Basic valid transcript with one chapter."""
    return """Introduction
0:00
Welcome to the session
2:30
Let's begin"""


@pytest.fixture
def two_chapter_transcript() -> str:
    """Transcript with two chapters using subsequent detection."""
    return """Introduction
0:00
First content
2:30
Second content
Chapter Two
5:00
Chapter Two content"""


@pytest.fixture
def complex_transcript() -> str:
    """Realistic transcript with multiple chapters and timestamps."""
    return """\nChapter 1
0:55
content
2:28
content
Chapter 2
1:15:30
content
102:45:12
content\n
Chapter 3
102:45:13"""


# ============= TIMESTAMP TESTS =============


def test_finds_all_timestamp_indices(simple_transcript: str) -> None:
    """Find all timestamp line indices in multi-line text."""
    lines = simple_transcript.splitlines()
    timestamp_indices = find_timestamps(lines)

    assert timestamp_indices == [1, 3]
    assert lines[1] == "0:00"
    assert lines[3] == "2:30"


# ============= VALIDATION TESTS =============


def test_validation_passes_for_valid_transcript(simple_transcript: str) -> None:
    """Valid transcript passes validation."""
    assert validate_transcript_format(simple_transcript) is None


def test_parses_valid_transcript_format() -> None:
    """File following exact required format should parse successfully."""
    required_format = """Introduction to Bret Taylor
00:04
You're CTO of Meta and co-CEO of..."""

    chapters = parse_transcript_file(required_format)
    assert len(chapters) == 1
    assert chapters[0].title == "Introduction to Bret Taylor"


def test_parses_valid_format_with_blank_lines() -> None:
    """File following exact required format should parse successfully."""
    valid_format_with_blank_lines = (
        "\nChapter 1\n\n00:04\n\ncontent\n\nChapter 2\n\n00:05\n\ncontent\n\ncontent\n"
    )

    chapters = parse_transcript_file(valid_format_with_blank_lines)
    assert len(chapters) == 2
    assert chapters[0].title == "Chapter 1"
    assert chapters[1].title == "Chapter 2"


def test_rejects_transcript_starting_with_timestamp() -> None:
    """File that starts with timestamp (like sample-00-chapters.txt) should fail."""
    starts_with_timestamp = """0:21
hey hey hey
0:53
[Music] welcome"""

    with pytest.raises(FileInvalidFormatError):
        parse_transcript_file(starts_with_timestamp)


def test_rejects_empty_transcript() -> None:
    """Empty transcript file should raise FileEmptyError."""
    with pytest.raises(FileEmptyError):
        parse_transcript_file("")

    with pytest.raises(FileEmptyError):
        parse_transcript_file("   \n  \t  \n  ")


def test_rejects_transcript_without_timestamps() -> None:
    """Transcript without any timestamps should raise FileInvalidFormatError."""
    no_timestamps = """Chapter Title
Some content here
More content
Final line"""

    with pytest.raises(FileInvalidFormatError, match="Second line must be a timestamp"):
        parse_transcript_file(no_timestamps)


def test_rejects_consecutive_timestamps_after_title() -> None:
    """Consecutive timestamps after chapter title should fail format validation."""
    consecutive_timestamps = """Introduction to Bret Taylor
00:04
00:05
You're CTO of Meta and and co-CEO of..."""

    with pytest.raises(
        FileInvalidFormatError, match="Third line must be content, not timestamp"
    ):
        parse_transcript_file(consecutive_timestamps)


def test_rejects_content_before_first_timestamp() -> None:
    """Content before first timestamp should fail format validation."""
    content_before_timestamp = """Introduction to Bret Taylor
content line should break
00:04
You're CTO of Meta and and co-CEO of..."""

    with pytest.raises(FileInvalidFormatError, match="Second line must be a timestamp"):
        parse_transcript_file(content_before_timestamp)


def test_rejects_file_with_insufficient_lines() -> None:
    """Files with fewer than 3 lines should fail format validation."""
    too_short = """Chapter Title
00:04"""

    with pytest.raises(FileInvalidFormatError, match="File must have at least 3 lines"):
        parse_transcript_file(too_short)


# ============= CHAPTER DETECTION TESTS =============


def test_finds_first_chapter_from_opening_line(simple_transcript: str) -> None:
    """First non-timestamp line becomes a chapter."""
    chapters = parse_transcript_file(simple_transcript)

    assert len(chapters) == 1
    assert chapters[0].title == "Introduction"
    assert chapters[0].start_time == 0.0


def test_finds_subsequent_chapter_with_boundary_rule(two_chapter_transcript: str) -> None:
    """Chapter detected when exactly 2 lines between timestamps."""
    chapters = parse_transcript_file(two_chapter_transcript)

    assert len(chapters) == 2
    assert chapters[0].title == "Introduction"
    assert chapters[1].title == "Chapter Two"
    assert chapters[1].start_time == 300.0


@pytest.mark.parametrize(
    "text",
    [
        # 1-line gap (not a chapter boundary)
        """Intro
0:00
Content
2:30
Wrong gap
7:30
More content""",
        # 3-line gap (not a chapter boundary)
        """Intro
0:00
Content
2:30
Line 1
Line 2
Line 3
7:30
More content""",
    ],
)
def test_no_chapter_when_boundary_rule_fails(text: str) -> None:
    """No chapter detected when gap is not exactly 2 lines."""
    chapters = parse_transcript_file(text)
    assert len(chapters) == 1
    assert chapters[0].title == "Intro"


def test_finds_all_chapters() -> None:
    """Multiple chapters detected with correct boundaries."""
    text = """First
0:00
Content
2:00
Content
Second
5:00
Content
7:00
Content
Third
10:00
Final"""

    chapters = parse_transcript_file(text)

    assert len(chapters) == 3
    assert [ch.title for ch in chapters] == ["First", "Second", "Third"]
    assert [ch.start_time for ch in chapters] == [0.0, 300.0, 600.0]


# ============= CONTENT EXTRACTION TESTS =============


def test_extracts_all_content_for_single_chapter() -> None:
    """Single chapter includes all content to end."""
    text = """Only Chapter
0:00
Line 1
2:30
Line 2
Final line"""

    chapters = parse_transcript_file(text)
    assert chapters[0].content_lines == [
        "0:00",
        "Line 1",
        "2:30",
        "Line 2",
        "Final line",
    ]


def test_extracts_correct_content_ranges_for_chapters(
    two_chapter_transcript: str,
) -> None:
    """Multiple chapters have correct content ranges."""
    chapters = parse_transcript_file(two_chapter_transcript)

    # First chapter: from timestamp to before second chapter title
    assert chapters[0].content_lines == [
        "0:00",
        "First content",
        "2:30",
        "Second content",
    ]

    # Second chapter: from timestamp to end
    assert chapters[1].content_lines == ["5:00", "Chapter Two content"]


def test_includes_multiple_timestamps_in_chapter_content() -> None:
    """Chapter content includes multiple timestamps."""
    text = """Long Chapter
0:00
Start
5:30
Middle
10:15
More
15:45
Final"""

    chapters = parse_transcript_file(text)
    content = chapters[0].content_lines

    # All timestamps and content should be included
    assert all(ts in content for ts in ["0:00", "5:30", "10:15", "15:45"])
    assert "Final" in content


# ============= INTEGRATION TESTS =============


def test_parses_complex_transcript_end_to_end(complex_transcript: str) -> None:
    """End-to-end test with realistic transcript."""
    chapters = parse_transcript_file(complex_transcript)

    # Test overall structure
    assert len(chapters) == 3

    # Test chapter sequence and metadata
    expected_chapters = [
        ("Chapter 1", "0:55"),
        ("Chapter 2", "1:15:30"),
        ("Chapter 3", "102:45:13"),
    ]

    for i, (expected_title, expected_start) in enumerate(expected_chapters):
        assert chapters[i].title == expected_title
        assert seconds_to_timestamp(chapters[i].start_time) == expected_start

    # Test content behavior (sufficient boundary checking)
    ch1_content = chapters[0].content_lines
    assert "0:55" in ch1_content
    assert "2:28" in ch1_content
    assert "content" in ch1_content
    assert len(ch1_content) == 4  # ← This catches boundary issues

    ch2_content = chapters[1].content_lines
    assert "1:15:30" in ch2_content
    assert "102:45:12" in ch2_content
    assert len(ch2_content) == 4  # ← This catches boundary issues

    ch3_content = chapters[2].content_lines
    assert "102:45:13" in ch3_content
    assert len(ch3_content) == 1  # ← This catches boundary issues


def test_handles_special_characters_in_titles() -> None:
    """Parsing handles special characters correctly."""
    text = """Special & "Characters" <XML>
0:00
Content with , erm, "quotes"
10:15:30
Multi-hour timestamp"""

    chapters = parse_transcript_file(text)
    assert chapters[0].title == """Special & "Characters" <XML>"""
    assert "10:15:30" in chapters[0].content_lines


def test_removes_blank_lines_during_processing() -> None:
    """Blank lines are automatically removed from transcript processing."""
    text_with_blanks = (
        "Chapter 1\n\n0:01\ncontent\n\n2:30\ncontent\n\nChapter 2\n5:00\ncontent\n\n"
    )

    chapters = parse_transcript_file(text_with_blanks)

    # Single assert: no blank lines in any chapter title or content
    all_content = [ch.title for ch in chapters] + [
        line for ch in chapters for line in ch.content_lines
    ]
    assert "" not in all_content


# ============= TIMESTAMP TYPE REFACTORING TESTS =============


def test_chapter_has_end_time_field(simple_transcript: str) -> None:
    """Chapter dataclass should have an end_time field."""
    chapters = parse_transcript_file(simple_transcript)
    assert hasattr(chapters[0], "end_time")


def test_chapter_timestamps_are_floats_with_duration(two_chapter_transcript: str) -> None:
    """Chapter timestamps should be floats with correct duration calculation."""
    chapters = parse_transcript_file(two_chapter_transcript)

    # First chapter: 0:00 = 0.0 seconds, ends at 5:00 = 300.0 seconds
    assert isinstance(chapters[0].start_time, float)
    assert chapters[0].start_time == 0.0
    assert chapters[0].end_time == 300.0
    assert chapters[0].duration == 300.0  # 300.0 - 0.0

    # Second chapter: 5:00 = 300.0 seconds, unknown end
    assert isinstance(chapters[1].start_time, float)
    assert chapters[1].start_time == 300.0
    assert math.isinf(chapters[1].end_time)
    assert math.isinf(chapters[1].duration)  # inf - 300.0


def test_complex_timestamps_as_floats(complex_transcript: str) -> None:
    """Complex H:MM:SS timestamps should convert to float seconds."""
    chapters = parse_transcript_file(complex_transcript)

    # 0:55 = 55 seconds
    assert chapters[0].start_time == 55.0

    # 1:15:30 = 4530 seconds
    assert chapters[1].start_time == 4530.0

    # 102:45:13 = 369913 seconds (102*3600 + 45*60 + 13)
    assert chapters[2].start_time == 369913.0

    # End times
    assert chapters[0].end_time == 4530.0
    assert chapters[1].end_time == 369913.0
    assert math.isinf(chapters[2].end_time)


def test_rejects_non_increasing_chapter_timestamps() -> None:
    """Test that non-increasing chapter timestamps raise FileInvalidFormatError."""
    # Create a transcript where second chapter has same/earlier start time than first
    transcript_with_bad_timestamps = """Chapter 1

0:30
First chapter content

Chapter 2

0:30
Second chapter content with same timestamp

Chapter 3

0:25
Third chapter content with earlier timestamp"""

    with pytest.raises(
        FileInvalidFormatError,
        match="Subsequent chapter timestamps must be strictly increasing",
    ):
        parse_transcript_file(transcript_with_bad_timestamps)
