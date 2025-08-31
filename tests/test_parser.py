"""Tests for the transcript parser module.

Following TDD principles with modern pytest patterns.
Uses fixtures to reduce duplication and improve maintainability.
"""

import pytest

from youtube_to_xml.exceptions import (
    FileEmptyError,
    FileInvalidFormatError,
)
from youtube_to_xml.parser import (
    TIMESTAMP_PATTERN,
    find_timestamps,
    parse_transcript,
    validate_transcript_format,
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


@pytest.mark.parametrize(
    "timestamp", ["0:00", "2:45", "00:00", "12:59", "1:23:45", "10:15:30", "999:59:59"]
)
def test_valid_timestamps(timestamp: str) -> None:
    """Verify regex matches valid timestamp formats."""
    assert TIMESTAMP_PATTERN.match(timestamp)


@pytest.mark.parametrize("invalid", ["", "Chapter Title", "1:2:3", "123:45", "12:60"])
def test_invalid_timestamps(invalid: str) -> None:
    """Verify regex rejects invalid patterns."""
    assert not TIMESTAMP_PATTERN.match(invalid)


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

    chapters = parse_transcript(required_format)
    assert len(chapters) == 1
    assert chapters[0].title == "Introduction to Bret Taylor"


def test_parses_valid_format_with_blank_lines() -> None:
    """File following exact required format should parse successfully."""
    valid_format_with_blank_lines = (
        "\nChapter 1\n\n00:04\n\ncontent\n\nChapter 2\n\n00:05\n\ncontent\n\ncontent\n"
    )

    chapters = parse_transcript(valid_format_with_blank_lines)
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
        parse_transcript(starts_with_timestamp)


def test_rejects_empty_transcript() -> None:
    """Empty transcript file should raise FileEmptyError."""
    with pytest.raises(FileEmptyError):
        parse_transcript("")

    with pytest.raises(FileEmptyError):
        parse_transcript("   \n  \t  \n  ")


def test_rejects_transcript_without_timestamps() -> None:
    """Transcript without any timestamps should raise FileInvalidFormatError."""
    no_timestamps = """Chapter Title
Some content here
More content
Final line"""

    with pytest.raises(FileInvalidFormatError, match="Second line must be a timestamp"):
        parse_transcript(no_timestamps)


def test_rejects_consecutive_timestamps_after_title() -> None:
    """Consecutive timestamps after chapter title should fail format validation."""
    consecutive_timestamps = """Introduction to Bret Taylor
00:04
00:05
You're CTO of Meta and and co-CEO of..."""

    with pytest.raises(
        FileInvalidFormatError, match="Third line must be content, not timestamp"
    ):
        parse_transcript(consecutive_timestamps)


def test_rejects_content_before_first_timestamp() -> None:
    """Content before first timestamp should fail format validation."""
    content_before_timestamp = """Introduction to Bret Taylor
content line should break
00:04
You're CTO of Meta and and co-CEO of..."""

    with pytest.raises(FileInvalidFormatError, match="Second line must be a timestamp"):
        parse_transcript(content_before_timestamp)


def test_rejects_file_with_insufficient_lines() -> None:
    """Files with fewer than 3 lines should fail format validation."""
    too_short = """Chapter Title
00:04"""

    with pytest.raises(FileInvalidFormatError, match="File must have at least 3 lines"):
        parse_transcript(too_short)


# ============= CHAPTER DETECTION TESTS =============


def test_finds_first_chapter_from_opening_line(simple_transcript: str) -> None:
    """First non-timestamp line becomes a chapter."""
    chapters = parse_transcript(simple_transcript)

    assert len(chapters) == 1
    assert chapters[0].title == "Introduction"
    assert chapters[0].start_time == "0:00"


def test_finds_subsequent_chapter_with_boundary_rule(two_chapter_transcript: str) -> None:
    """Chapter detected when exactly 2 lines between timestamps."""
    chapters = parse_transcript(two_chapter_transcript)

    assert len(chapters) == 2
    assert chapters[0].title == "Introduction"
    assert chapters[1].title == "Chapter Two"
    assert chapters[1].start_time == "5:00"


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
    chapters = parse_transcript(text)
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

    chapters = parse_transcript(text)

    assert len(chapters) == 3
    assert [ch.title for ch in chapters] == ["First", "Second", "Third"]
    assert [ch.start_time for ch in chapters] == ["0:00", "5:00", "10:00"]


# ============= CONTENT EXTRACTION TESTS =============


def test_extracts_all_content_for_single_chapter() -> None:
    """Single chapter includes all content to end."""
    text = """Only Chapter
0:00
Line 1
2:30
Line 2
Final line"""

    chapters = parse_transcript(text)
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
    chapters = parse_transcript(two_chapter_transcript)

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

    chapters = parse_transcript(text)
    content = chapters[0].content_lines

    # All timestamps and content should be included
    assert all(ts in content for ts in ["0:00", "5:30", "10:15", "15:45"])
    assert "Final" in content


# ============= INTEGRATION TESTS =============


def test_parses_complex_transcript_end_to_end(complex_transcript: str) -> None:
    """End-to-end test with realistic transcript."""
    chapters = parse_transcript(complex_transcript)

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
        assert chapters[i].start_time == expected_start

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

    chapters = parse_transcript(text)
    assert chapters[0].title == """Special & "Characters" <XML>"""
    assert "10:15:30" in chapters[0].content_lines


def test_removes_blank_lines_during_processing() -> None:
    """Blank lines are automatically removed from transcript processing."""
    text_with_blanks = (
        "Chapter 1\n\n0:01\ncontent\n\n2:30\ncontent\n\nChapter 2\n5:00\ncontent\n\n"
    )

    chapters = parse_transcript(text_with_blanks)

    # Single assert: no blank lines in any chapter title or content
    all_content = [ch.title for ch in chapters] + [
        line for ch in chapters for line in ch.content_lines
    ]
    assert "" not in all_content
