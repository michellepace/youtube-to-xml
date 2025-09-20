"""Smoke tests for shared data models.

Simple validation that models can be imported and used as expected.
Real integration testing happens when these models are used by parsers and builders.
"""

from youtube_to_xml.models import (
    Chapter,
    TranscriptDocument,
    TranscriptLine,
    VideoMetadata,
)


def test_transcript_line_stores_timestamp_and_text() -> None:
    """TranscriptLine stores float timestamp and string text."""
    line = TranscriptLine(timestamp=30.5, text="Hello world")
    assert line.timestamp == 30.5
    assert line.text == "Hello world"


def test_video_metadata_creates_with_empty_defaults() -> None:
    """VideoMetadata initializes with empty strings and zero duration."""
    metadata = VideoMetadata()
    assert metadata.video_title == ""
    assert metadata.video_published == ""
    assert metadata.video_duration == 0
    assert metadata.video_url == ""


def test_video_metadata_stores_all_provided_values() -> None:
    """VideoMetadata correctly stores title, date, duration and URL when provided."""
    metadata = VideoMetadata(
        video_title="Test Video",
        video_published="20250717",
        video_duration=163,
        video_url="https://youtube.com/watch?v=abc123",
    )
    assert metadata.video_title == "Test Video"
    assert metadata.video_published == "20250717"
    assert metadata.video_duration == 163
    assert metadata.video_url == "https://youtube.com/watch?v=abc123"


def test_chapter_stores_title_times_and_transcript_lines() -> None:
    """Chapter holds title, start/end times, and list of TranscriptLine objects."""
    lines = [
        TranscriptLine(timestamp=0.0, text="Hello"),
        TranscriptLine(timestamp=30.5, text="World"),
    ]
    chapter = Chapter(
        title="Introduction",
        start_time=0.0,
        end_time=60.0,
        transcript_lines=lines,
    )
    assert chapter.title == "Introduction"
    assert chapter.start_time == 0.0
    assert chapter.end_time == 60.0
    assert len(chapter.transcript_lines) == 2


def test_transcript_document_combines_metadata_and_chapters() -> None:
    """TranscriptDocument holds VideoMetadata and list of Chapter objects."""
    metadata = VideoMetadata(video_title="Test Video")
    chapter = Chapter(
        title="Chapter 1", start_time=0.0, end_time=60.0, transcript_lines=[]
    )

    document = TranscriptDocument(metadata=metadata, chapters=[chapter])
    assert document.metadata.video_title == "Test Video"
    assert len(document.chapters) == 1
    assert document.chapters[0].title == "Chapter 1"


def test_models_use_slots() -> None:
    """Test that models use __slots__ for memory efficiency."""
    assert hasattr(VideoMetadata(), "__slots__")
    assert hasattr(TranscriptLine(0.0, ""), "__slots__")
    assert hasattr(Chapter("", 0.0, 1.0, []), "__slots__")
    assert hasattr(TranscriptDocument(VideoMetadata(), []), "__slots__")
