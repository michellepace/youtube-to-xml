"""Unit tests for youtube_to_xml.url_parser module.

Tests the URL parser module interface and functionality for converting
YouTube URLs into structured TranscriptDocument objects.
"""

import inspect

# url_parser module imports (group together)
import youtube_to_xml.url_parser as url_parser_module

# Shared model imports
from youtube_to_xml.models import (
    Chapter,
    TranscriptDocument,
    TranscriptLine,
    VideoMetadata,
)
from youtube_to_xml.url_parser import (
    assign_transcript_lines_to_chapters,
    extract_transcript_lines_from_json3,
    fetch_video_metadata_and_transcript,
    parse_youtube_url,
)


class TestSharedModelImports:
    """Test that URL parser module uses shared models."""

    def test_url_parser_uses_video_metadata_from_shared_models(self) -> None:
        """Test that url_parser module uses VideoMetadata from youtube_to_xml.models."""
        # Check that fetch_video_metadata_and_transcript returns VideoMetadata
        sig = inspect.signature(fetch_video_metadata_and_transcript)
        return_annotation = sig.return_annotation

        # Should return tuple containing VideoMetadata
        if hasattr(return_annotation, "__args__"):
            assert VideoMetadata in return_annotation.__args__, (
                "fetch_video_metadata_and_transcript should return VideoMetadata "
                "from shared models"
            )

    def test_url_parser_uses_transcript_line_from_shared_models(self) -> None:
        """Test that url_parser module uses TranscriptLine from youtube_to_xml.models."""
        # Check that extract_transcript_lines_from_json3 returns list[TranscriptLine]
        sig = inspect.signature(extract_transcript_lines_from_json3)
        return_annotation = sig.return_annotation

        # Should return list[TranscriptLine]
        if hasattr(return_annotation, "__args__"):
            assert TranscriptLine in return_annotation.__args__, (
                "extract_transcript_lines_from_json3 should return list[TranscriptLine] "
                "from shared models"
            )

    def test_url_parser_uses_chapter_from_shared_models(self) -> None:
        """Test that url_parser module uses Chapter from youtube_to_xml.models."""
        # Check that assign_transcript_lines_to_chapters returns list[Chapter]
        sig = inspect.signature(assign_transcript_lines_to_chapters)
        return_annotation = sig.return_annotation

        # Should return list[Chapter]
        if hasattr(return_annotation, "__args__"):
            assert Chapter in return_annotation.__args__, (
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


class TestXMLBuilderIntegration:
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
            "integration"
        )


class TestUrlParserModule:
    """Test that url_parser module exists (PR 7)."""

    def test_url_parser_module_can_be_imported(self) -> None:
        """Test that youtube_to_xml.url_parser module exists."""
        # This will fail initially - drives TDD implementation
        # Module is already imported at top level as url_parser_module
        assert url_parser_module is not None


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
