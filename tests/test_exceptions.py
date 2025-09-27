"""Tests for the enhanced exception module."""

import inspect
import re

import pytest

from youtube_to_xml import exceptions
from youtube_to_xml.exceptions import (
    EXCEPTION_MESSAGES,
    BaseTranscriptError,
    FileEmptyError,
    URLBotProtectionError,
    URLIncompleteError,
    URLIsInvalidError,
    URLNotYouTubeError,
    URLRateLimitError,
    URLUnmappedError,
    URLVideoIsPrivateError,
    URLVideoUnavailableError,
    map_yt_dlp_exception,
)

# Auto-discover all exception classes that inherit from BaseTranscriptError
ALL_EXCEPTION_CLASSES = [
    cls
    for name, cls in inspect.getmembers(exceptions, inspect.isclass)
    if (issubclass(cls, BaseTranscriptError) and cls != BaseTranscriptError)
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
            # Test default constructor (no args) to verify default messages work
            exception = exception_class()  # type: ignore[call-arg]
            assert str(exception), (
                f"{type(exception).__name__} should have a default message"
            )

    def test_all_exceptions_have_message_keys(self) -> None:
        """Test that every exception class has a corresponding message key in MESSAGES."""
        expected_keys = self._derive_expected_message_keys()
        actual_keys = set(EXCEPTION_MESSAGES.keys())

        missing_keys = expected_keys - actual_keys
        assert not missing_keys, f"Missing EXCEPTION_MESSAGES keys: {missing_keys}"

    def test_all_exceptions_use_messages_constants(self) -> None:
        """Test all exception classes use messages from EXCEPTION_MESSAGES constant."""
        for exception_class in ALL_EXCEPTION_CLASSES:
            # Instantiate with default message to check actual message content
            exception = exception_class()  # type: ignore[call-arg]
            message = str(exception)

            # Verify this message exists in MESSAGES values
            assert message in EXCEPTION_MESSAGES.values(), (
                f"{exception_class.__name__} uses hardcoded message: '{message}'"
            )

    def test_no_orphaned_message_keys(self) -> None:
        """Test that no message keys exist without corresponding exception classes."""
        expected_keys = self._derive_expected_message_keys()
        actual_keys = set(EXCEPTION_MESSAGES.keys())

        orphaned_keys = actual_keys - expected_keys
        assert not orphaned_keys, (
            f"Orphaned MESSAGES keys (no corresponding exception): {orphaned_keys}"
        )

    def _derive_expected_message_keys(self) -> set[str]:
        """Derive expected message keys from exception class names in snake_case."""

        def class_name_to_message_key(class_name: str) -> str:
            # Handle special cases
            name = class_name.replace("YouTube", "Youtube").replace("URL", "Url")

            # E.g., URLIsInvalidError → url_is_invalid_error
            parts = re.findall(r"[A-Z][a-z]*", name)
            return "_".join(parts).lower()

        return {
            class_name_to_message_key(exc_class.__name__)
            for exc_class in ALL_EXCEPTION_CLASSES
        }


class TestExceptionHierarchy:
    """Tests for proper exception inheritance hierarchy."""

    def test_all_exceptions_inherit_from_base(self) -> None:
        """Test that all custom exceptions inherit from BaseTranscriptError."""
        for exception_class in ALL_EXCEPTION_CLASSES:
            exception = exception_class()  # type: ignore[call-arg]
            assert isinstance(exception, BaseTranscriptError)
            assert isinstance(exception, Exception)

    def test_base_exception_can_catch_all(self) -> None:
        """Test that catching BaseTranscriptError catches all custom exceptions."""

        def _raise_exception(exc: Exception) -> None:
            """Helper function to raise exceptions for testing."""
            raise exc

        for exception_class in ALL_EXCEPTION_CLASSES:
            exception = exception_class()  # type: ignore[call-arg]
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
            (
                "HTTP Error 429",
                URLRateLimitError,
                EXCEPTION_MESSAGES["url_rate_limit_error"],
            ),
            (
                "ERROR: [youtube] Q4gsvJvRjCU: Sign in to confirm you're not a bot",
                URLBotProtectionError,
                EXCEPTION_MESSAGES["url_bot_protection_error"],
            ),
            (
                "ERROR: Unsupported URL: https://www.google.com/",
                URLNotYouTubeError,
                EXCEPTION_MESSAGES["url_not_youtube_error"],
            ),
            (
                "ERROR: [youtube:truncated_id] Q4g: Incomplete YouTube ID Q4g",
                URLIncompleteError,
                EXCEPTION_MESSAGES["url_incomplete_error"],
            ),
            (
                "ERROR: [generic] '' is not a valid URL",
                URLIsInvalidError,
                EXCEPTION_MESSAGES["url_is_invalid_error"],
            ),
            (
                "ERROR: [youtube] invalid-url: Video unavailable",
                URLIsInvalidError,
                EXCEPTION_MESSAGES["url_is_invalid_error"],
            ),
            (
                "ERROR: [youtube] ai_HGCf2w_w: Video unavailable",
                URLVideoUnavailableError,
                EXCEPTION_MESSAGES["url_video_unavailable_error"],
            ),
            (
                "ERROR: [youtube] abc123: Private video",
                URLVideoIsPrivateError,
                EXCEPTION_MESSAGES["url_video_is_private_error"],
            ),
            (
                "Some unknown error message",
                URLUnmappedError,
                "Some unknown error message",
            ),
        ]

        for error_msg, expected_type, expected_message in test_cases:
            error = Exception(error_msg)
            result = map_yt_dlp_exception(error)
            assert isinstance(result, expected_type)
            assert isinstance(result, BaseTranscriptError)
            assert str(result) == expected_message

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
