"""Tests for the enhanced exception module.

Following TDD principles with comprehensive coverage of all exception types.
"""

import pytest

from youtube_to_xml.exceptions import (
    FileEmptyError,
    FileInvalidFormatError,
    TranscriptProcessingError,
    URLFormatError,
    URLSubtitlesUnavailableError,
    URLVideoNotFoundError,
)


class TestTranscriptProcessingError:
    """Tests for the base exception class."""

    def test_base_exception_creation(self) -> None:
        """Test base exception can be created with custom message."""
        error = TranscriptProcessingError("Custom error message")
        assert str(error) == "Custom error message"
        assert isinstance(error, Exception)

    def test_base_exception_inheritance(self) -> None:
        """Test that base exception inherits from Exception."""
        error = TranscriptProcessingError("Test message")
        assert isinstance(error, Exception)


class TestFileInputExceptions:
    """Tests for file input related exceptions."""

    def test_file_empty_error_default_message(self) -> None:
        """Test FileEmptyError with default message."""
        error = FileEmptyError()
        assert str(error) == "Cannot parse an empty transcript file"
        assert isinstance(error, TranscriptProcessingError)

    def test_file_empty_error_custom_message(self) -> None:
        """Test FileEmptyError with custom message."""
        custom_message = "File is completely empty"
        error = FileEmptyError(custom_message)
        assert str(error) == custom_message
        assert isinstance(error, TranscriptProcessingError)

    def test_file_invalid_format_error_default_message(self) -> None:
        """Test FileInvalidFormatError with default message."""
        error = FileInvalidFormatError()
        expected = "Transcript file must start with a chapter title, not a timestamp"
        assert str(error) == expected
        assert isinstance(error, TranscriptProcessingError)

    def test_file_invalid_format_error_custom_message(self) -> None:
        """Test FileInvalidFormatError with custom message."""
        custom_message = "Wrong format detected"
        error = FileInvalidFormatError(custom_message)
        assert str(error) == custom_message
        assert isinstance(error, TranscriptProcessingError)


class TestYouTubeInputExceptions:
    """Tests for YouTube input related exceptions."""

    def test_url_format_error_default_message(self) -> None:
        """Test URLFormatError with default message."""
        error = URLFormatError()
        assert str(error) == "Invalid YouTube URL format"
        assert isinstance(error, TranscriptProcessingError)

    def test_url_format_error_custom_message(self) -> None:
        """Test URLFormatError with custom message."""
        custom_message = "URL is not a valid YouTube link"
        error = URLFormatError(custom_message)
        assert str(error) == custom_message
        assert isinstance(error, TranscriptProcessingError)

    def test_url_video_not_found_error_default_message(self) -> None:
        """Test URLVideoNotFoundError with default message."""
        error = URLVideoNotFoundError()
        assert str(error) == "YouTube video not found or unavailable"
        assert isinstance(error, TranscriptProcessingError)

    def test_url_video_not_found_error_custom_message(self) -> None:
        """Test URLVideoNotFoundError with custom message."""
        custom_message = "Video has been deleted or made private"
        error = URLVideoNotFoundError(custom_message)
        assert str(error) == custom_message
        assert isinstance(error, TranscriptProcessingError)

    def test_url_subtitles_unavailable_error_default_message(self) -> None:
        """Test URLSubtitlesUnavailableError with default message."""
        error = URLSubtitlesUnavailableError()
        assert str(error) == "No subtitles available for this video"
        assert isinstance(error, TranscriptProcessingError)

    def test_url_subtitles_unavailable_error_custom_message(self) -> None:
        """Test URLSubtitlesUnavailableError with custom message."""
        custom_message = "Creator disabled captions and no auto-generated ones exist"
        error = URLSubtitlesUnavailableError(custom_message)
        assert str(error) == custom_message
        assert isinstance(error, TranscriptProcessingError)


class TestExceptionHierarchy:
    """Tests for proper exception inheritance hierarchy."""

    def test_all_exceptions_inherit_from_base(self) -> None:
        """Test that all custom exceptions inherit from TranscriptProcessingError."""
        exceptions_to_test = [
            FileEmptyError(),
            FileInvalidFormatError(),
            URLFormatError(),
            URLVideoNotFoundError(),
            URLSubtitlesUnavailableError(),
        ]

        for exception in exceptions_to_test:
            assert isinstance(exception, TranscriptProcessingError)
            assert isinstance(exception, Exception)

    def test_base_exception_can_catch_all(self) -> None:
        """Test that catching TranscriptProcessingError catches all custom exceptions."""
        exceptions_to_test = [
            FileEmptyError(),
            FileInvalidFormatError(),
            URLFormatError(),
            URLVideoNotFoundError(),
            URLSubtitlesUnavailableError(),
        ]

        def _raise_exception(exc: Exception) -> None:
            """Helper function to raise exceptions for testing."""
            raise exc

        for exception in exceptions_to_test:
            with pytest.raises(TranscriptProcessingError):
                _raise_exception(exception)


class TestExceptionUsagePatterns:
    """Tests for common exception usage patterns."""

    def test_raising_and_catching_specific_exceptions(self) -> None:
        """Test raising and catching specific exception types."""
        with pytest.raises(FileEmptyError, match="Cannot parse an empty transcript file"):
            raise FileEmptyError

        with pytest.raises(URLFormatError, match="Invalid YouTube URL format"):
            raise URLFormatError

    def test_raising_and_catching_base_exception(self) -> None:
        """Test raising and catching the base exception type."""
        error_msg = "Generic processing error"
        with pytest.raises(TranscriptProcessingError, match="Generic processing error"):
            raise TranscriptProcessingError(error_msg)

    def test_exception_message_preservation(self) -> None:
        """Test that custom messages are properly preserved."""
        test_cases = [
            (FileEmptyError, "File is empty"),
            (FileInvalidFormatError, "Bad format"),
            (URLFormatError, "Bad URL"),
            (URLVideoNotFoundError, "Video gone"),
            (URLSubtitlesUnavailableError, "No captions"),
        ]

        for exception_class, message in test_cases:
            error = exception_class(message)
            assert str(error) == message
