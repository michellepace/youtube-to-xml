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


def test_models_can_be_created_and_used() -> None:
    """Smoke test: models exist and can be instantiated with expected data."""
    # Defaults are empty strings and 0 for duration (file based scenario)
    file_metadata = VideoMetadata()
    assert file_metadata.video_title == ""
    assert file_metadata.video_published == ""
    assert file_metadata.video_duration == 0
    assert file_metadata.video_url == ""

    # URL method scenario - populated metadata
    url_metadata = VideoMetadata(
        video_title="Test Video",
        video_published="20250717",
        video_duration=163,  # raw seconds
        video_url="https://youtube.com/watch?v=abc123",
    )
    assert url_metadata.video_title == "Test Video"
    assert url_metadata.video_duration == 163

    # Create transcript lines
    line1 = TranscriptLine(timestamp=0.0, text="Hello world")
    line2 = TranscriptLine(timestamp=30.5, text="How are you?")
    assert line1.timestamp == 0.0
    assert line2.text == "How are you?"

    # Create chapter
    chapter = Chapter(
        title="Introduction",
        start_time=0.0,
        end_time=60.0,
        transcript_lines=[line1, line2],
    )
    assert chapter.title == "Introduction"
    assert len(chapter.transcript_lines) == 2

    # Create complete document
    document = TranscriptDocument(metadata=url_metadata, chapters=[chapter])
    assert document.metadata.video_title == "Test Video"
    assert len(document.chapters) == 1
    assert document.chapters[0].title == "Introduction"
