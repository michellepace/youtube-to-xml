"""Tests for the transcript parser module.

Following TDD principles with modern pytest patterns.
Uses fixtures to reduce duplication and improve maintainability.
"""

import pytest

from youtube_to_xml.parser import (
    TIMESTAMP_PATTERN,
    Chapter,
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
    return """Introduction
0:00
Welcome to today's session
2:28
Let's dive into the topic
Getting Started
1:15:30
Download the software
2:45:12
Configure it"""


# ============= TIMESTAMP TESTS =============


@pytest.mark.parametrize("timestamp", ["0:00", "00:00", "1:23:45", "10:15:30"])
def test_valid_timestamps(timestamp: str) -> None:
    """Verify regex matches valid timestamp formats."""
    assert TIMESTAMP_PATTERN.match(timestamp)


@pytest.mark.parametrize("invalid", ["Chapter Title", "123:45", "1:2:3", "12:60", ""])
def test_invalid_timestamps(invalid: str) -> None:
    """Verify regex rejects invalid patterns."""
    assert not TIMESTAMP_PATTERN.match(invalid)


def test_find_timestamps_in_text(simple_transcript: str) -> None:
    """Find all timestamp line indices in multi-line text."""
    lines = simple_transcript.splitlines()
    timestamp_indices = find_timestamps(lines)

    assert timestamp_indices == [1, 3]
    assert lines[1] == "0:00"
    assert lines[3] == "2:30"


# ============= VALIDATION TESTS =============


def test_validate_valid_transcript(simple_transcript: str) -> None:
    """Valid transcript passes validation."""
    assert validate_transcript_format(simple_transcript) is None


@pytest.mark.parametrize(
    ("invalid_input", "error_match"),
    [
        ("", "empty"),
        ("   \n  ", "empty"),
        ("0:00\nContent", "timestamp"),
        ("Chapter\nNo timestamps", "timestamp"),
    ],
)
def test_validate_invalid_transcripts(invalid_input: str, error_match: str) -> None:
    """Invalid transcripts raise appropriate errors."""
    with pytest.raises(ValueError, match=error_match):
        validate_transcript_format(invalid_input)


# ============= CHAPTER DETECTION TESTS =============


def test_first_chapter_detection(simple_transcript: str) -> None:
    """First non-timestamp line becomes a chapter."""
    chapters = parse_transcript(simple_transcript)

    assert len(chapters) == 1
    assert chapters[0].title == "Introduction"
    assert chapters[0].start_time == "0:00"


def test_subsequent_chapter_detection(two_chapter_transcript: str) -> None:
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
def test_no_chapter_when_wrong_gap(text: str) -> None:
    """No chapter detected when gap is not exactly 2 lines."""
    chapters = parse_transcript(text)
    assert len(chapters) == 1
    assert chapters[0].title == "Intro"


def test_multiple_chapters() -> None:
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


def test_single_chapter_content() -> None:
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


def test_chapter_content_ranges(two_chapter_transcript: str) -> None:
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


def test_chapter_with_many_timestamps() -> None:
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


def test_complete_parsing(complex_transcript: str) -> None:
    """End-to-end test with realistic transcript."""
    chapters = parse_transcript(complex_transcript)

    assert len(chapters) == 2

    # Verify first chapter
    assert chapters[0] == Chapter(
        title="Introduction",
        start_time="0:00",
        content_lines=[
            "0:00",
            "Welcome to today's session",
            "2:28",
            "Let's dive into the topic",
        ],
    )

    # Verify second chapter
    assert chapters[1] == Chapter(
        title="Getting Started",
        start_time="1:15:30",
        content_lines=[
            "1:15:30",
            "Download the software",
            "2:45:12",
            "Configure it",
        ],
    )


def test_special_characters() -> None:
    """Parsing handles special characters correctly."""
    text = """Special & "Characters" <XML>
0:00
Content with , erm, "quotes"
10:15:30
Multi-hour timestamp"""

    chapters = parse_transcript(text)
    assert chapters[0].title == """Special & "Characters" <XML>"""
    assert "10:15:30" in chapters[0].content_lines


def test_empty_lines_preserved() -> None:
    """Empty lines are preserved in content."""
    text = """Chapter
0:00

Empty line above
2:30

Another empty line"""

    chapters = parse_transcript(text)
    assert "" in chapters[0].content_lines  # Empty lines preserved


def test_consecutive_timestamps() -> None:
    """Multiple consecutive timestamps handled correctly."""
    text = """Chapter
0:00
0:30
1:00
Some content after"""

    chapters = parse_transcript(text)
    content = chapters[0].content_lines

    # All timestamps should be in content
    assert all(ts in content for ts in ["0:00", "0:30", "1:00"])
    assert "Some content after" in content


# ============= ERROR CASES =============


@pytest.mark.parametrize(
    ("invalid_text", "error_match"),
    [
        ("", "empty"),
        ("Just text\nNo timestamps", "timestamp"),
        ("0:00\nContent", "timestamp"),
    ],
)
def test_error_conditions(invalid_text: str, error_match: str) -> None:
    """Various error conditions raise appropriate exceptions."""
    with pytest.raises(ValueError, match=error_match):
        parse_transcript(invalid_text)
