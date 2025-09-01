"""Tests for the enhanced exception module."""

import pytest

from youtube_to_xml.exceptions import (
    BaseTranscriptError,
    FileEmptyError,
    FileInvalidFormatError,
    URLFormatError,
    URLRateLimitError,
    URLSubtitlesNotFoundError,
    URLVideoNotFoundError,
)

ALL_EXCEPTION_CLASSES = [
    # BaseTranscriptError excluded
    FileEmptyError,
    FileInvalidFormatError,
    URLFormatError,
    URLRateLimitError,
    URLSubtitlesNotFoundError,
    URLVideoNotFoundError,
]


class TestBaseTranscriptError:
    """Tests for the base exception class."""

    def test_base_exception_creation(self) -> None:
        """Test base exception can be created with custom message."""
        error = BaseTranscriptError("Custom error message")
        assert str(error) == "Custom error message"
        assert isinstance(error, Exception)

    def test_base_exception_inheritance(self) -> None:
        """Test that base exception inherits from Exception."""
        error = BaseTranscriptError("Test message")
        assert isinstance(error, Exception)


class TestExceptionMessages:
    """Tests for exception default messages and custom message handling."""

    def test_all_exceptions_have_default_messages(self) -> None:
        """Test that all exceptions have non-empty default messages."""
        for exception_class in ALL_EXCEPTION_CLASSES:
            exception = exception_class()
            assert str(exception), (
                f"{type(exception).__name__} should have a default message"
            )


class TestExceptionHierarchy:
    """Tests for proper exception inheritance hierarchy."""

    def test_all_exceptions_inherit_from_base(self) -> None:
        """Test that all custom exceptions inherit from BaseTranscriptError."""
        for exception_class in ALL_EXCEPTION_CLASSES:
            exception = exception_class()
            assert isinstance(exception, BaseTranscriptError)
            assert isinstance(exception, Exception)

    def test_base_exception_can_catch_all(self) -> None:
        """Test that catching BaseTranscriptError catches all custom exceptions."""

        def _raise_exception(exc: Exception) -> None:
            """Helper function to raise exceptions for testing."""
            raise exc

        for exception_class in ALL_EXCEPTION_CLASSES:
            exception = exception_class()
            with pytest.raises(BaseTranscriptError):
                _raise_exception(exception)


class TestExceptionUsagePatterns:
    """Tests for common exception usage patterns."""

    def test_raising_and_catching_specific_exceptions(self) -> None:
        """Test raising and catching specific exception types."""
        with pytest.raises(FileEmptyError):
            raise FileEmptyError

        with pytest.raises(URLFormatError):
            raise URLFormatError

    def test_raising_and_catching_base_exception(self) -> None:
        """Test raising and catching the base exception type."""
        error_msg = "Generic processing error"
        with pytest.raises(BaseTranscriptError, match="Generic processing error"):
            raise BaseTranscriptError(error_msg)

    def test_all_exceptions_preserve_custom_messages(self) -> None:
        """Test that all exceptions preserve custom messages exactly."""
        custom_message = "Test custom message for validation"
        for exception_class in ALL_EXCEPTION_CLASSES:
            error = exception_class(custom_message)
            assert str(error) == custom_message, (
                f"{exception_class.__name__} failed to preserve custom message"
            )
