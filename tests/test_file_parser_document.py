"""TESTS FOR THE NEW PARSE_TRANSCRIPT_DOCUMENT FUNCTION IN `file_parser.py`.

# Tests for parse_transcript_document function.
# This new TranscriptDocument parsing interface will become the primary API
# after deprecated parse_transcript_file function is removed in PR 5.

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
    parse_transcript_document,
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


def test_parse_document_returns_transcript_document(one_chapter_transcript: str) -> None:
    """Verify function returns TranscriptDocument type."""
    doc = parse_transcript_document(one_chapter_transcript)
    assert isinstance(doc, TranscriptDocument)


def test_parse_document_metadata_always_empty(one_chapter_transcript: str) -> None:
    """File method always produces empty metadata."""
    doc = parse_transcript_document(one_chapter_transcript)

    assert doc.metadata.video_title == ""
    assert doc.metadata.video_published == ""
    assert doc.metadata.video_duration == 0
    assert doc.metadata.video_url == ""


def test_parse_document_simple_single_chapter(one_chapter_transcript: str) -> None:
    """Parse basic transcript into TranscriptDocument."""
    doc = parse_transcript_document(one_chapter_transcript)

    # Verify structure
    assert isinstance(doc, TranscriptDocument)
    assert isinstance(doc.metadata, VideoMetadata)
    assert len(doc.chapters) == 1

    # Check chapter
    chapter = doc.chapters[0]
    assert isinstance(chapter, Chapter)
    assert chapter.title == "Chapter 1"
    assert chapter.start_time == 10.0
    assert chapter.end_time == math.inf

    # Check transcript lines
    assert len(chapter.transcript_lines) == 2
    assert all(isinstance(line, TranscriptLine) for line in chapter.transcript_lines)

    line1, line2 = chapter.transcript_lines
    assert line1.timestamp == 10.0
    assert line1.text == "Line A at 10 seconds"
    assert line2.timestamp == 59.0
    assert line2.text == "Line B at 59 seconds"


def test_parse_document_multiple_chapters(complex_transcript: str) -> None:
    """Parse transcript with multiple chapters maintaining correct boundaries."""
    doc = parse_transcript_document(complex_transcript)

    assert len(doc.chapters) == 3

    # First chapter - "CHAPTER 1" at 0:55
    ch1 = doc.chapters[0]
    assert ch1.title == "CHAPTER 1"
    assert ch1.start_time == 55.0  # 0:55 = 55 seconds
    assert ch1.end_time == 4530.0  # 1:15:30 = 4530 seconds
    assert len(ch1.transcript_lines) == 2
    assert ch1.transcript_lines[0].timestamp == 55.0
    assert ch1.transcript_lines[0].text == "spoken words at timestamp"
    assert ch1.transcript_lines[1].timestamp == 148.0
    assert ch1.transcript_lines[1].text == "spoken words at timestamp"

    # Second chapter - "CHAPTER 2" at 1:15:30
    ch2 = doc.chapters[1]
    assert ch2.title == "CHAPTER 2"
    assert ch2.start_time == 4530.0
    assert ch2.end_time == 369913.0
    assert len(ch2.transcript_lines) == 2
    assert ch2.transcript_lines[0].timestamp == 4530.0
    assert ch2.transcript_lines[0].text == "spoken words at timestamp"
    assert ch2.transcript_lines[1].timestamp == 369912.0
    assert ch2.transcript_lines[1].text == "spoken words at timestamp"

    # Third chapter - "CHAPTER 3" at 102:45:13
    ch3 = doc.chapters[2]
    assert ch3.title == "CHAPTER 3"
    assert ch3.start_time == 369913.0
    assert ch3.end_time == math.inf
    assert len(ch3.transcript_lines) == 1
    assert ch3.transcript_lines[0].timestamp == 369913.0
    assert ch3.transcript_lines[0].text == ""


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

    doc = parse_transcript_document(transcript)
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

    doc = parse_transcript_document(transcript)

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
    doc = parse_transcript_document(transcript)

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

    doc = parse_transcript_document(transcript)

    assert doc.chapters[0].start_time == 10.0
    assert doc.chapters[0].end_time == 60.0

    assert doc.chapters[1].start_time == 60.0
    assert doc.chapters[1].end_time == 120.0

    assert doc.chapters[2].start_time == 120.0
    assert doc.chapters[2].end_time == math.inf


def test_last_chapter_has_infinite_end_time(minimal_transcript: str) -> None:
    """Last chapter always has math.inf as end time."""
    doc = parse_transcript_document(minimal_transcript)
    assert doc.chapters[-1].end_time == math.inf


def test_subsequent_chapter_detection() -> None:
    """2-line boundary rule correctly identifies chapters."""
    # Exactly 2 lines between timestamps = new chapter
    transcript = """First Chapter
0:00
Line 1
0:05
Line 2
New Chapter Here
0:10
Line 3"""

    doc = parse_transcript_document(transcript)

    assert len(doc.chapters) == 2
    assert doc.chapters[0].title == "First Chapter"
    assert doc.chapters[1].title == "New Chapter Here"


# ============= EDGE CASES =============


def test_minimal_valid_transcript(minimal_transcript: str) -> None:
    """Process minimal 3-line transcript."""
    doc = parse_transcript_document(minimal_transcript)

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

    doc = parse_transcript_document(transcript)
    lines = doc.chapters[0].transcript_lines

    assert len(lines) == 3
    assert lines[0].text == "First text"
    assert lines[1].text == "Second text"
    assert lines[2].text == ""


# ============= ERROR VALIDATION TESTS =============


def test_empty_input_raises_file_empty_error() -> None:
    """Empty or whitespace input raises FileEmptyError."""
    with pytest.raises(FileEmptyError):
        parse_transcript_document("")

    with pytest.raises(FileEmptyError):
        parse_transcript_document("   \n\n  \t  ")


def test_invalid_format_raises_error() -> None:
    """Starting with timestamp raises FileInvalidFormatError."""
    transcript = """0:00
Should start with title
Not timestamp"""

    with pytest.raises(FileInvalidFormatError, match="First line must be chapter title"):
        parse_transcript_document(transcript)


def test_insufficient_lines_raises_error() -> None:
    """Less than 3 lines raises error."""
    with pytest.raises(FileInvalidFormatError, match="File must have at least 3 lines"):
        parse_transcript_document("Title\n0:00")

    with pytest.raises(FileInvalidFormatError, match="File must have at least 3 lines"):
        parse_transcript_document("Title")


def test_no_timestamps_raises_error() -> None:
    """Text without timestamps raises error."""
    transcript = """Title
No timestamp here
Just text"""

    with pytest.raises(FileInvalidFormatError, match="Second line must be a timestamp"):
        parse_transcript_document(transcript)


# ============= INTEGRATION PATTERN TESTS =============


def test_returns_correct_model_types(one_chapter_transcript: str) -> None:
    """Function returns exact types from shared models module."""
    doc = parse_transcript_document(one_chapter_transcript)

    assert type(doc).__name__ == "TranscriptDocument"
    assert type(doc.metadata).__name__ == "VideoMetadata"
    assert type(doc.chapters[0]).__name__ == "Chapter"
    assert type(doc.chapters[0].transcript_lines[0]).__name__ == "TranscriptLine"


def test_uses_new_chapter_model_not_legacy(one_chapter_transcript: str) -> None:
    """Chapter uses new model with TranscriptLine list, not old string list."""
    doc = parse_transcript_document(one_chapter_transcript)
    chapter = doc.chapters[0]

    assert hasattr(chapter, "transcript_lines")
    assert isinstance(chapter.transcript_lines[0], TranscriptLine)
    assert not isinstance(chapter.transcript_lines[0], str)


def test_xml_builder_interface_compatibility(one_chapter_transcript: str) -> None:
    """Output structure matches xml_builder expected interface."""
    doc = parse_transcript_document(one_chapter_transcript)

    # Document structure
    assert hasattr(doc, "metadata")
    assert hasattr(doc, "chapters")

    # Metadata structure
    assert hasattr(doc.metadata, "video_title")
    assert hasattr(doc.metadata, "video_published")
    assert hasattr(doc.metadata, "video_duration")
    assert hasattr(doc.metadata, "video_url")

    # Chapter and transcript line structure
    for chapter in doc.chapters:
        assert hasattr(chapter, "title")
        assert hasattr(chapter, "start_time")
        assert hasattr(chapter, "end_time")
        assert hasattr(chapter, "transcript_lines")

        for line in chapter.transcript_lines:
            assert hasattr(line, "timestamp")
            assert hasattr(line, "text")
