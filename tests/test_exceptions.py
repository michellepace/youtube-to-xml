"""Tests for the enhanced exception module."""

import pytest

from youtube_to_xml.exceptions import (
    BaseTranscriptError,
    FileEmptyError,
    FileEncodingError,
    FileInvalidFormatError,
    FileNotExistsError,
    FilePermissionError,
    InvalidInputError,
    URLBotProtectionError,
    URLIncompleteError,
    URLIsInvalidError,
    URLNotYouTubeError,
    URLRateLimitError,
    URLTranscriptNotFoundError,
    URLUnmappedError,
    URLVideoUnavailableError,
    map_yt_dlp_exception,
)

ALL_EXCEPTION_CLASSES = [
    # BaseTranscriptError excluded
    FileEmptyError,
    FileEncodingError,
    FileInvalidFormatError,
    FileNotExistsError,
    FilePermissionError,
    InvalidInputError,
    URLBotProtectionError,
    URLIncompleteError,
    URLIsInvalidError,
    URLNotYouTubeError,
    URLRateLimitError,
    URLTranscriptNotFoundError,
    URLUnmappedError,
    URLVideoUnavailableError,
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

        with pytest.raises(URLIsInvalidError):
            raise URLIsInvalidError

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


class TestYtDlpExceptionMapping:
    """Tests for yt-dlp exception mapping to custom exceptions."""

    def test_map_yt_dlp_exception_patterns(self) -> None:
        """Test that error patterns map to correct exception types with messages."""
        test_cases = [
            ("HTTP Error 429", URLRateLimitError, "limiting"),
            (
                "ERROR: [youtube] Q4gsvJvRjCU: Sign in to confirm you're not a bot",
                URLBotProtectionError,
                "verification",
            ),
            (
                "ERROR: Unsupported URL: https://www.google.com/",
                URLNotYouTubeError,
                "not a youtube",
            ),
            (
                "ERROR: [youtube:truncated_id] Q4g: Incomplete YouTube ID Q4g",
                URLIncompleteError,
                "incomplete",
            ),
            ("ERROR: [generic] '' is not a valid URL", URLIsInvalidError, "invalid"),
            (
                "ERROR: [youtube] invalid-url: Video unavailable",
                URLIsInvalidError,
                "invalid",
            ),
            (
                "ERROR: [youtube] ai_HGCf2w_w: Video unavailable",
                URLVideoUnavailableError,
                "unavailable",
            ),
            ("Some unknown error message", URLUnmappedError, "error"),
        ]

        for error_msg, expected_type, expected_text in test_cases:
            error = Exception(error_msg)
            result = map_yt_dlp_exception(error)
            assert isinstance(result, expected_type)
            assert isinstance(result, BaseTranscriptError)
            assert expected_text in str(result).lower()

    def test_rate_limit_error_message(self) -> None:
        """Test URLRateLimitError with custom message."""
        bot_protection_msg = (
            "YouTube bot protection triggered - try switching networks or using cookies"
        )
        error = URLRateLimitError(bot_protection_msg)
        assert isinstance(error, URLRateLimitError)
        assert isinstance(error, BaseTranscriptError)
        assert "bot protection" in str(error).lower()

    def test_unmapped_error_uses_default_message(self) -> None:
        """Test that unmapped errors use the default URLUnmappedError message."""
        original_error = Exception("Some weird new yt-dlp error we haven't seen before")

        result = map_yt_dlp_exception(original_error)

        assert isinstance(result, URLUnmappedError)
        assert isinstance(result, BaseTranscriptError)
        assert "error" in str(result).lower()
