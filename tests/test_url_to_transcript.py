"""Unit tests for scripts/url_to_transcript.py — PR 6 refactoring.

Note: In PR 7 tests will import from youtube_to_xml.url_parser.

Tests that the URL script uses shared models and xml_builder infrastructure
instead of duplicate local implementations.
"""

import sys
from pathlib import Path

from youtube_to_xml.models import Chapter, TranscriptLine, VideoMetadata

# Add scripts directory to path for importing url_to_transcript
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# Import url_to_transcript with proper typing
import url_to_transcript  # type: ignore[import-untyped]


class TestSharedModelImports:
    """Test that URL script imports models from shared modules."""

    def test_url_script_imports_video_metadata_from_shared_models(self) -> None:
        """Test that VideoMetadata is imported from youtube_to_xml.models."""
        # Get the VideoMetadata class used in url_to_transcript module
        url_video_metadata = getattr(url_to_transcript, "VideoMetadata", None)

        # Should not be None (class should exist)
        assert url_video_metadata is not None, (
            "VideoMetadata should be imported in url_to_transcript module"
        )

        # Should be the same class as the shared model
        assert url_video_metadata is VideoMetadata, (
            "VideoMetadata should be imported from youtube_to_xml.models, not locally"
        )

    def test_url_script_imports_transcript_line_from_shared_models(self) -> None:
        """Test that TranscriptLine is imported from youtube_to_xml.models."""
        url_transcript_line = getattr(url_to_transcript, "TranscriptLine", None)

        assert url_transcript_line is not None, (
            "TranscriptLine should be imported in url_to_transcript module"
        )
        assert url_transcript_line is TranscriptLine, (
            "TranscriptLine should be imported from youtube_to_xml.models, not locally"
        )

    def test_url_script_imports_chapter_from_shared_models(self) -> None:
        """Test that Chapter is imported from youtube_to_xml.models."""
        url_chapter = getattr(url_to_transcript, "Chapter", None)

        assert url_chapter is not None, (
            "Chapter should be imported in url_to_transcript module"
        )
        assert url_chapter is Chapter, (
            "Chapter should be imported from youtube_to_xml.models, not defined locally"
        )


class TestVideoMetadataDurationFormat:
    """Test that VideoMetadata.video_duration uses int (raw seconds) format."""

    def test_video_metadata_duration_is_int_type(self) -> None:
        """Test that video_duration field expects int type (raw seconds)."""
        # Get VideoMetadata from url_to_transcript module
        url_video_metadata = url_to_transcript.VideoMetadata

        # Create instance with int duration (raw seconds)
        metadata = url_video_metadata(
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
    """Test that URL script uses xml_builder.transcript_to_xml()."""

    def test_url_script_imports_transcript_to_xml(self) -> None:
        """Test that transcript_to_xml is imported from xml_builder."""
        # Should import transcript_to_xml function
        transcript_to_xml_func = getattr(url_to_transcript, "transcript_to_xml", None)
        assert transcript_to_xml_func is not None, (
            "transcript_to_xml should be imported from xml_builder"
        )

        # Should be a function
        assert callable(transcript_to_xml_func), "transcript_to_xml should be callable"

    def test_url_script_no_longer_has_create_xml_document_function(self) -> None:
        """Test that local XML generation functions are removed."""
        # Should not have local create_xml_document function
        create_xml_func = getattr(url_to_transcript, "create_xml_document", None)
        assert create_xml_func is None, (
            "create_xml_document should be removed (use xml_builder.transcript_to_xml)"
        )

    def test_url_script_no_longer_has_format_xml_output_function(self) -> None:
        """Test that local format_xml_output function is removed."""
        format_xml_func = getattr(url_to_transcript, "format_xml_output", None)
        assert format_xml_func is None, (
            "format_xml_output should be removed (use xml_builder.transcript_to_xml)"
        )
