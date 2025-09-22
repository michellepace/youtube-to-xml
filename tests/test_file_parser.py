"""Tests for file_parser.py transcript parsing functionality.

Tests the parse_transcript_file function which converts YouTube transcript
files into structured TranscriptDocument objects with chapters and metadata.
"""

import math

import pytest

from youtube_to_xml.exceptions import (
    FileEmptyError,
    FileInvalidFormatError,
)
from youtube_to_xml.file_parser import (
    parse_transcript_file,
)
from youtube_to_xml.models import (
    Chapter,
    TranscriptDocument,
    TranscriptLine,
    VideoMetadata,
)

# ============= FIXTURES =============


@pytest.fixture
def minimal_transcript() -> str:
    return """Chapter 1
0:02
Line A at 2 seconds"""


@pytest.fixture
def one_chapter_transcript() -> str:
    return """Chapter 1
0:10
Line A at 10 seconds
0:59
Line B at 59 seconds"""


@pytest.fixture
def complex_transcript() -> str:
    return """CHAPTER 1
0:55
spoken words at timestamp
2:28
spoken words at timestamp

CHAPTER 2
1:15:30
spoken words at timestamp
102:45:12
spoken words at timestamp

CHAPTER 3
102:45:13"""


@pytest.fixture
def no_chapters_transcript() -> str:
    return """0:00
spoken words at timestamp
0:01
spoken words at timestamp
0:02
spoken words at timestamp"""


# ============= CORE FUNCTIONALITY TESTS =============


def test_output_structure_conforms_to_interface(one_chapter_transcript: str) -> None:
    """Verify parse_transcript_document returns correct unified model structure."""
    doc = parse_transcript_file(one_chapter_transcript)

    # Core structure validation
    assert isinstance(doc, TranscriptDocument)
    assert isinstance(doc.metadata, VideoMetadata)
    assert isinstance(doc.chapters[0], Chapter)
    assert isinstance(doc.chapters[0].transcript_lines[0], TranscriptLine)


def test_parse_document_metadata_always_empty(one_chapter_transcript: str) -> None:
    """File method always produces empty metadata."""
    doc = parse_transcript_file(one_chapter_transcript)

    assert doc.metadata.video_title == ""
    assert doc.metadata.video_published == ""
    assert doc.metadata.video_duration == 0
    assert doc.metadata.video_url == ""


def test_single_chapter_detection(one_chapter_transcript: str) -> None:
    """Basic transcript produces exactly one chapter."""
    doc = parse_transcript_file(one_chapter_transcript)
    assert len(doc.chapters) == 1
    assert doc.chapters[0].title == "Chapter 1"


def test_single_chapter_time_boundaries(one_chapter_transcript: str) -> None:
    """Single chapter has correct start time and infinite end time."""
    doc = parse_transcript_file(one_chapter_transcript)
    chapter = doc.chapters[0]

    assert chapter.start_time == 10.0  # 0:10 = 10 seconds
    assert chapter.end_time == math.inf


def test_transcript_line_content_conversion(one_chapter_transcript: str) -> None:
    """Transcript lines are correctly converted from string format."""
    doc = parse_transcript_file(one_chapter_transcript)
    lines = doc.chapters[0].transcript_lines

    assert len(lines) == 2
    assert lines[0].timestamp == 10.0
    assert lines[0].text == "Line A at 10 seconds"
    assert lines[1].timestamp == 59.0
    assert lines[1].text == "Line B at 59 seconds"


def test_multiple_chapter_detection(complex_transcript: str) -> None:
    """Complex transcript correctly detects multiple chapters."""
    doc = parse_transcript_file(complex_transcript)

    assert len(doc.chapters) == 3
    assert doc.chapters[0].title == "CHAPTER 1"
    assert doc.chapters[1].title == "CHAPTER 2"
    assert doc.chapters[2].title == "CHAPTER 3"


def test_chapter_boundary_calculation(complex_transcript: str) -> None:
    """Chapter boundaries are calculated correctly between multiple chapters."""
    doc = parse_transcript_file(complex_transcript)

    # Time boundaries: 0:55 → 1:15:30 → 102:45:13 → ∞
    assert doc.chapters[0].start_time == 55.0
    assert doc.chapters[0].end_time == 4530.0

    assert doc.chapters[1].start_time == 4530.0
    assert doc.chapters[1].end_time == 369913.0

    assert doc.chapters[2].start_time == 369913.0
    assert doc.chapters[2].end_time == math.inf


def test_transcript_line_ordering_preserved() -> None:
    """Transcript lines maintain original order within chapters."""
    transcript = """Chapter
0:05
Line E at 5 seconds
0:03
Line C at 3 seconds
0:01
Line A at 1 second
0:04
Line D at 4 seconds
0:02
Line B at 2 seconds"""

    doc = parse_transcript_file(transcript)
    lines = doc.chapters[0].transcript_lines

    # Lines should be in document order, not sorted by timestamp
    assert lines[0].timestamp == 5.0
    assert lines[0].text == "Line E at 5 seconds"

    assert lines[1].timestamp == 3.0
    assert lines[1].text == "Line C at 3 seconds"

    assert lines[2].timestamp == 1.0
    assert lines[2].text == "Line A at 1 second"

    assert lines[3].timestamp == 4.0
    assert lines[3].text == "Line D at 4 seconds"

    assert lines[4].timestamp == 2.0
    assert lines[4].text == "Line B at 2 seconds"


def test_transcript_whitespace_handling() -> None:
    """Transcript whitespace is normalized and titles preserved exactly."""
    transcript = """  \nChapter with CASE and     space

0:00

Lines   are   trimmed   and   singled    spaced		tabs too

    0:01
Special preserved: <@> & ! and unicode 你好 🎉 résumé

0:02"""

    doc = parse_transcript_file(transcript)

    assert len(doc.chapters) == 1
    assert doc.chapters[0].title == "Chapter with CASE and space"

    lines = doc.chapters[0].transcript_lines
    assert lines[0].text == "Lines are trimmed and singled spaced tabs too"
    assert lines[1].text == "Special preserved: <@> & ! and unicode 你好 🎉 résumé"
    assert lines[2].text == ""


# ============= TRANSCRIPT LINE CONVERSION TESTS =============


def test_multiple_transcript_lines_and_timestamp_conversion() -> None:
    """Many timestamp/text pairs with float second conversion."""
    lines_content = ["Chapter", "0:00", "Text 0"]
    for i in range(1, 20):
        lines_content.extend([f"0:{i:02d}", f"Text {i}"])

    transcript = "\n".join(lines_content)
    doc = parse_transcript_file(transcript)

    assert len(doc.chapters[0].transcript_lines) == 20
    for i, line in enumerate(doc.chapters[0].transcript_lines):
        assert isinstance(line.timestamp, float)
        assert line.timestamp == float(i)
        assert line.text == f"Text {i}"


# ============= CHAPTER STRUCTURE TESTS =============


def test_chapter_start_end_times_correct() -> None:
    """Verify proper time boundaries for chapters."""
    transcript = """Chapter 1
0:10
Content
Chapter 2
1:00
Content
Chapter 3
2:00
Content"""

    doc = parse_transcript_file(transcript)

    assert doc.chapters[0].start_time == 10.0
    assert doc.chapters[0].end_time == 60.0

    assert doc.chapters[1].start_time == 60.0
    assert doc.chapters[1].end_time == 120.0

    assert doc.chapters[2].start_time == 120.0
    assert doc.chapters[2].end_time == math.inf


def test_subsequent_chapter_detection() -> None:
    """2-line boundary rule correctly identifies chapters."""
    # Exactly 2 lines between timestamps = chapter boundary
    transcript = """First Chapter
0:00
Line 1
0:05
Line 2
New Chapter Here
0:10
Line 3"""

    doc = parse_transcript_file(transcript)

    assert len(doc.chapters) == 2
    assert doc.chapters[0].title == "First Chapter"
    assert doc.chapters[1].title == "New Chapter Here"


def test_no_chapter_when_one_line_gap() -> None:
    """No chapter detected when only 1 line between timestamps."""
    transcript = """Intro
0:00
Content
2:30
Wrong gap
7:30
More content"""

    doc = parse_transcript_file(transcript)
    assert len(doc.chapters) == 1
    assert doc.chapters[0].title == "Intro"


def test_no_chapter_when_three_line_gap() -> None:
    """No chapter detected when 3 lines between timestamps."""
    transcript = """Intro
0:00
Content
2:30
Line 1
Line 2
Line 3
7:30
More content"""

    doc = parse_transcript_file(transcript)
    assert len(doc.chapters) == 1
    assert doc.chapters[0].title == "Intro"


# ============= EDGE CASES =============


def test_minimal_valid_transcript(minimal_transcript: str) -> None:
    """Process minimal 3-line transcript."""
    doc = parse_transcript_file(minimal_transcript)

    assert len(doc.chapters) == 1
    assert doc.chapters[0].title == "Chapter 1"
    assert len(doc.chapters[0].transcript_lines) == 1
    assert doc.chapters[0].transcript_lines[0].text == "Line A at 2 seconds"
    assert doc.chapters[0].transcript_lines[0].timestamp == 2.0


def test_empty_text_after_timestamp() -> None:
    """Handle empty string text after timestamp."""
    transcript = """Chapter
0:00
First text
0:05
Second text
0:10"""

    doc = parse_transcript_file(transcript)
    lines = doc.chapters[0].transcript_lines

    assert len(lines) == 3
    assert lines[0].text == "First text"
    assert lines[1].text == "Second text"
    assert lines[2].text == ""


# ============= ERROR VALIDATION TESTS =============


@pytest.mark.parametrize(
    ("input_text", "expected_error", "error_match"),
    [
        # Empty input cases
        ("", FileEmptyError, None),
        ("   \n\n  \t  ", FileEmptyError, None),
        # Format validation cases
        (
            "0:00\nShould start with title\nNot timestamp",
            FileInvalidFormatError,
            "First line must be chapter title",
        ),
        ("Title\n0:00", FileInvalidFormatError, "File must have at least 3 lines"),
        ("Title", FileInvalidFormatError, "File must have at least 3 lines"),
        (
            "Title\nNo timestamp here\nJust text",
            FileInvalidFormatError,
            "Second line must be a timestamp",
        ),
        (
            "Title\n0:00\n0:01\nContent",
            FileInvalidFormatError,
            "Third line must be transcript text, not timestamp",
        ),
    ],
)
def test_invalid_input_raises_appropriate_error(
    input_text: str, expected_error: type, error_match: str | None
) -> None:
    """Invalid input formats raise appropriate validation errors."""
    if error_match:
        with pytest.raises(expected_error, match=error_match):
            parse_transcript_file(input_text)
    else:
        with pytest.raises(expected_error):
            parse_transcript_file(input_text)


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
