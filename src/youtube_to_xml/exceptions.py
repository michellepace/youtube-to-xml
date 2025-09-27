"""Custom exceptions for YouTube transcript processing."""

# Centralised default exception messages
EXCEPTION_MESSAGES = {
    # File-related errors
    "file_empty_error": "Your file is empty",
    "file_invalid_format_error": "Wrong format in transcript file",
    "file_not_exists_error": "We couldn't find your file",
    "file_permission_error": "We don't have permission to access your file",
    "file_encoding_error": "File is not UTF-8 encoded",
    # URL-related errors
    "url_is_invalid_error": "Invalid URL format",
    "url_video_unavailable_error": "YouTube video unavailable",
    "url_transcript_not_found_error": "This video doesn't have a transcript available",
    "url_rate_limit_error": "YouTube is temporarily limiting requests - try again later",
    "url_not_youtube_error": "URL is not a YouTube video",
    "url_incomplete_error": "YouTube URL is incomplete",
    "url_bot_protection_error": "YouTube requires verification - try switching networks",
    "url_unmapped_error": "YouTube processing failed - unmapped error",
    # Input validation errors
    "invalid_input_error": "Input must be a YouTube URL or .txt file",
}


class BaseTranscriptError(Exception):
    """Base exception for all transcript processing failures."""

    def __init__(self, message: str) -> None:
        """Initialise with custom message."""
        super().__init__(message)


class FileEmptyError(BaseTranscriptError):
    """Raised when attempting to parse an empty transcript file."""

    def __init__(self, message: str = EXCEPTION_MESSAGES["file_empty_error"]) -> None:
        """Initialise with custom message."""
        super().__init__(message)


class FileInvalidFormatError(BaseTranscriptError):
    """Raised when transcript file doesn't follow expected manual format."""

    def __init__(
        self, message: str = EXCEPTION_MESSAGES["file_invalid_format_error"]
    ) -> None:
        """Initialise with custom message."""
        super().__init__(message)


class URLIsInvalidError(BaseTranscriptError):
    """Raised when URL format is invalid (empty or malformed text)."""

    def __init__(self, message: str = EXCEPTION_MESSAGES["url_is_invalid_error"]) -> None:
        """Initialise with custom message."""
        super().__init__(message)


class URLVideoUnavailableError(BaseTranscriptError):
    """Raised when YouTube video exists but is unavailable."""

    def __init__(
        self, message: str = EXCEPTION_MESSAGES["url_video_unavailable_error"]
    ) -> None:
        """Initialise with custom message."""
        super().__init__(message)


class URLTranscriptNotFoundError(BaseTranscriptError):
    """Raised when YouTube video has no available transcript."""

    def __init__(
        self, message: str = EXCEPTION_MESSAGES["url_transcript_not_found_error"]
    ) -> None:
        """Initialise with custom message."""
        super().__init__(message)


class URLRateLimitError(BaseTranscriptError):
    """Raised when access is temporarily blocked due to rate limiting."""

    def __init__(
        self,
        message: str = EXCEPTION_MESSAGES["url_rate_limit_error"],
    ) -> None:
        """Initialise with custom message."""
        super().__init__(message)


class URLNotYouTubeError(BaseTranscriptError):
    """Raised when URL is not a YouTube video URL."""

    def __init__(
        self, message: str = EXCEPTION_MESSAGES["url_not_youtube_error"]
    ) -> None:
        """Initialise with custom message."""
        super().__init__(message)


class URLIncompleteError(BaseTranscriptError):
    """Raised when YouTube URL has incomplete video ID."""

    def __init__(self, message: str = EXCEPTION_MESSAGES["url_incomplete_error"]) -> None:
        """Initialise with custom message."""
        super().__init__(message)


class URLBotProtectionError(BaseTranscriptError):
    """Raised when YouTube requires verification to access video."""

    def __init__(
        self, message: str = EXCEPTION_MESSAGES["url_bot_protection_error"]
    ) -> None:
        """Initialise with custom message."""
        super().__init__(message)


class URLUnmappedError(BaseTranscriptError):
    """Raised when YouTube processing fails for unknown/unmapped yt-dlp errors."""

    def __init__(self, message: str = EXCEPTION_MESSAGES["url_unmapped_error"]) -> None:
        """Initialise with custom message."""
        super().__init__(message)


class FileNotExistsError(BaseTranscriptError):
    """Raised when transcript file doesn't exist."""

    def __init__(
        self, message: str = EXCEPTION_MESSAGES["file_not_exists_error"]
    ) -> None:
        """Initialise with custom message."""
        super().__init__(message)


class FilePermissionError(BaseTranscriptError):
    """Raised when file cannot be read due to permission issues."""

    def __init__(
        self, message: str = EXCEPTION_MESSAGES["file_permission_error"]
    ) -> None:
        """Initialise with custom message."""
        super().__init__(message)


class FileEncodingError(BaseTranscriptError):
    """Raised when file is not UTF-8 encoded."""

    def __init__(self, message: str = EXCEPTION_MESSAGES["file_encoding_error"]) -> None:
        """Initialise with custom message."""
        super().__init__(message)


class InvalidInputError(BaseTranscriptError):
    """Raised when input is neither a valid URL nor .txt file."""

    def __init__(self, message: str = EXCEPTION_MESSAGES["invalid_input_error"]) -> None:
        """Initialise with custom message."""
        super().__init__(message)


def map_yt_dlp_exception(error: Exception) -> BaseTranscriptError:
    """Map yt-dlp exceptions to our custom exceptions based on error patterns.

    Args:
        error: The yt-dlp exception (DownloadError, ExtractorError, or UnsupportedError)

    Returns:
        Appropriate custom exception for the error pattern
    """
    error_msg = str(error).lower()

    # Map specific error patterns to appropriate exceptions
    error_patterns = [
        ("429", URLRateLimitError),
        ("sign in to confirm you're not a bot", URLBotProtectionError),
        ("unsupported url", URLNotYouTubeError),
        ("incomplete youtube id", URLIncompleteError),
        ("is not a valid url", URLIsInvalidError),
        ("[youtube] invalid-url:", URLIsInvalidError),
        ("video unavailable", URLVideoUnavailableError),
    ]

    for pattern, exception_class in error_patterns:
        if pattern in error_msg:
            return exception_class()

    # Default for unknown yt-dlp errors - preserve original yt-dlp message
    original_msg = str(error)
    clean_msg = original_msg.removeprefix("ERROR: ")
    return URLUnmappedError(clean_msg)
