"""Unit tests for youtube_to_xml.url_parser module.

Tests the URL parser module interface and functionality for converting
YouTube URLs into structured TranscriptDocument objects.
"""

import inspect
from pathlib import Path
from typing import get_args

import youtube_to_xml.url_parser as url_parser_module
from youtube_to_xml.models import (
    Chapter,
    TranscriptDocument,
    TranscriptLine,
    VideoMetadata,
)
from youtube_to_xml.url_parser import (
    _assign_transcript_lines_to_chapters,
    _create_video_metadata,
    _extract_transcript_lines_from_json3,
    _fetch_video_metadata_and_transcript,
    _get_youtube_transcript_file_priority,
    _InternalChapterDict,
    _Json3Event,
    parse_youtube_url,
)


class TestSharedModelImports:
    """Test that URL parser module uses shared models."""

    def test_url_parser_uses_video_metadata_from_shared_models(self) -> None:
        """Test that url_parser module uses VideoMetadata from youtube_to_xml.models."""
        # Check that fetch_video_metadata_and_transcript returns VideoMetadata
        sig = inspect.signature(_fetch_video_metadata_and_transcript)
        return_annotation = sig.return_annotation

        # Should return tuple containing VideoMetadata
        args = get_args(return_annotation)
        if args:
            assert VideoMetadata in args, (
                "fetch_video_metadata_and_transcript should return VideoMetadata "
                "from shared models"
            )

    def test_url_parser_uses_transcript_line_from_shared_models(self) -> None:
        """Test that url_parser module uses TranscriptLine from youtube_to_xml.models."""
        # Check that extract_transcript_lines_from_json3 returns list[TranscriptLine]
        sig = inspect.signature(_extract_transcript_lines_from_json3)
        return_annotation = sig.return_annotation

        # Should return list[TranscriptLine]
        args = get_args(return_annotation)
        if args:
            assert TranscriptLine in args, (
                "extract_transcript_lines_from_json3 should return list[TranscriptLine] "
                "from shared models"
            )

    def test_url_parser_uses_chapter_from_shared_models(self) -> None:
        """Test that url_parser module uses Chapter from youtube_to_xml.models."""
        # Check that assign_transcript_lines_to_chapters returns list[Chapter]
        sig = inspect.signature(_assign_transcript_lines_to_chapters)
        return_annotation = sig.return_annotation

        # Should return list[Chapter]
        args = get_args(return_annotation)
        if args:
            assert Chapter in args, (
                "assign_transcript_lines_to_chapters should return list[Chapter] "
                "from shared models"
            )


class TestVideoMetadataDurationFormat:
    """Test that VideoMetadata.video_duration uses int (raw seconds) format."""

    def test_video_metadata_duration_is_int_type(self) -> None:
        """Test that video_duration field expects int type (raw seconds)."""
        # Create instance with int duration (raw seconds)
        metadata = VideoMetadata(
            video_title="Test Video",
            video_published="20240315",
            video_duration=163,  # Raw seconds as int
            video_url="https://youtube.com/watch?v=test",
        )

        # Should accept int and store as int
        assert isinstance(metadata.video_duration, int), (
            "video_duration should be stored as int (raw seconds)"
        )
        assert metadata.video_duration == 163, (
            "video_duration should be raw seconds value"
        )


class TestXMLBuilderCompatibility:
    """Test that URL parser module integrates with xml_builder correctly."""

    def test_url_parser_module_has_no_duplicate_xml_functions(self) -> None:
        """Test that url_parser module doesn't contain duplicate XML functions."""
        # Should not have local create_xml_document function
        create_xml_func = getattr(url_parser_module, "create_xml_document", None)
        assert create_xml_func is None, (
            "create_xml_document should not exist (use xml_builder.transcript_to_xml)"
        )

        # Should not have local format_xml_output function
        format_xml_func = getattr(url_parser_module, "format_xml_output", None)
        assert format_xml_func is None, (
            "format_xml_output should not exist (use xml_builder.transcript_to_xml)"
        )

    def test_parse_youtube_url_returns_transcript_document_for_xml_builder(self) -> None:
        """Test parse_youtube_url returns TranscriptDocument for xml_builder."""
        # Verify return type is TranscriptDocument (xml_builder.transcript_to_xml accepts)
        sig = inspect.signature(parse_youtube_url)
        return_annotation = sig.return_annotation

        assert return_annotation == TranscriptDocument, (
            "parse_youtube_url should return TranscriptDocument for xml_builder "
            "compatibility"
        )


class TestParseYoutubeUrlFunction:
    """Test that parse_youtube_url function exists with correct interface (PR 7)."""

    def test_parse_youtube_url_function_exists(self) -> None:
        """Test that parse_youtube_url function exists in url_parser module."""
        # Function should exist and be importable
        assert callable(parse_youtube_url)

    def test_parse_youtube_url_accepts_one_parameter(self) -> None:
        """Test that parse_youtube_url accepts exactly one parameter."""
        sig = inspect.signature(parse_youtube_url)
        params = list(sig.parameters.values())
        assert len(params) == 1

    def test_parse_youtube_url_parameter_named_url(self) -> None:
        """Test that parse_youtube_url parameter is named 'url'."""
        sig = inspect.signature(parse_youtube_url)
        params = list(sig.parameters.values())
        assert params[0].name == "url"

    def test_parse_youtube_url_returns_transcript_document(self) -> None:
        """Test that parse_youtube_url has TranscriptDocument return type annotation."""
        sig = inspect.signature(parse_youtube_url)
        if sig.return_annotation != inspect.Signature.empty:
            assert sig.return_annotation == TranscriptDocument


class TestTranscriptFilePriority:
    """Test transcript file priority selection logic."""

    def test_transcript_file_priority_ordering(self) -> None:
        """Test files sort by priority: manual English > auto English > others."""
        files = [
            Path("video.es.json3"),  # Other language
            Path("video.en-orig.json3"),  # Auto-generated English
            Path("video.en.json3"),  # Manual English
            Path("video.fr.json3"),  # Other language
        ]

        sorted_files = sorted(files, key=_get_youtube_transcript_file_priority)

        assert sorted_files[0].name == "video.en.json3"  # Highest priority
        assert sorted_files[1].name == "video.en-orig.json3"  # Medium priority
        # Remaining two can be in any order (same priority)


class TestExtractTranscriptLinesBehavior:
    """Test JSON3 transcript parsing behavior."""

    def test_handles_empty_events_list(self) -> None:
        """Empty events should return empty list."""
        assert _extract_transcript_lines_from_json3([]) == []

    def test_skips_events_without_segs(self) -> None:
        """Events without 'segs' key should be skipped."""
        # Create properly typed test events
        events: list[_Json3Event] = [
            {"tStartMs": 1000},  # No segs
            {"tStartMs": 2000, "segs": [{"utf8": "text"}]},
        ]
        result = _extract_transcript_lines_from_json3(events)
        assert len(result) == 1
        assert result[0].text == "text"

    def test_combines_multi_segment_text(self) -> None:
        """Multiple segments should be combined."""
        events: list[_Json3Event] = [
            {
                "tStartMs": 5000,
                "segs": [{"utf8": "Hello"}, {"utf8": " world"}],
            }
        ]
        result = _extract_transcript_lines_from_json3(events)
        assert result[0].text == "Hello world"

    def test_removes_newlines_from_text(self) -> None:
        """Newlines should be replaced with spaces."""
        events: list[_Json3Event] = [{"tStartMs": 0, "segs": [{"utf8": "Line\nbreak"}]}]
        result = _extract_transcript_lines_from_json3(events)
        assert result[0].text == "Line break"

    def test_converts_milliseconds_to_seconds(self) -> None:
        """Timestamps should be converted from ms to seconds."""
        events: list[_Json3Event] = [{"tStartMs": 5500, "segs": [{"utf8": "text"}]}]
        result = _extract_transcript_lines_from_json3(events)
        assert result[0].timestamp == 5.5


class TestAssignChaptersBehavior:
    """Test chapter assignment behavior."""

    def test_no_chapters_creates_single_chapter(self) -> None:
        """No chapters should create one chapter with all lines."""
        metadata = VideoMetadata("Title", "20240101", 100, "url")
        lines = [TranscriptLine(10, "text")]
        result = _assign_transcript_lines_to_chapters(metadata, lines, [])
        assert len(result) == 1
        assert result[0].title == "Title"
        assert result[0].transcript_lines == lines

    def test_assigns_lines_to_correct_chapters(self) -> None:
        """Lines should be assigned based on timestamps."""
        metadata = VideoMetadata("Title", "20240101", 100, "url")
        lines = [
            TranscriptLine(5, "intro"),
            TranscriptLine(15, "main"),
            TranscriptLine(25, "conclusion"),
        ]
        youtube_chapter_dicts: list[_InternalChapterDict] = [
            {"title": "Intro", "start_time": 0, "end_time": 10},
            {"title": "Main", "start_time": 10, "end_time": 20},
            {"title": "End", "start_time": 20, "end_time": 30},
        ]
        result = _assign_transcript_lines_to_chapters(
            metadata, lines, youtube_chapter_dicts
        )
        assert len(result) == 3
        assert result[0].transcript_lines[0].text == "intro"
        assert result[1].transcript_lines[0].text == "main"
        assert result[2].transcript_lines[0].text == "conclusion"


class TestDecomposedFunctions:
    """Test the decomposed helper functions from fetch_video_metadata_and_transcript."""

    def test_create_video_metadata_from_raw_data(self) -> None:
        """Test _create_video_metadata builds correct VideoMetadata object."""
        raw_metadata = {
            "title": "Test Video Title",
            "upload_date": "20240315",
            "duration": 163,
            "webpage_url": "https://youtube.com/watch?v=test123",
        }
        url = "https://youtube.com/watch?v=test123"

        result = _create_video_metadata(raw_metadata, url)

        assert isinstance(result, VideoMetadata)
        assert result.video_title == "Test Video Title"
        assert result.video_published == "20240315"
        assert result.video_duration == 163
        assert result.video_url == "https://youtube.com/watch?v=test123"

    def test_create_video_metadata_with_missing_fields(self) -> None:
        """Test _create_video_metadata handles missing fields with defaults."""
        raw_metadata = {}  # Empty metadata
        url = "https://youtube.com/watch?v=fallback"

        result = _create_video_metadata(raw_metadata, url)

        assert result.video_title == "Untitled"
        assert result.video_published == ""
        assert result.video_duration == 0
        assert result.video_url == "https://youtube.com/watch?v=fallback"
