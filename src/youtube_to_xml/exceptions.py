"""Custom exceptions for YouTube transcript processing."""


class BaseTranscriptError(Exception):
    """Base exception for all transcript processing failures."""

    def __init__(self, message: str) -> None:
        """Initialize the exception with a custom message."""
        super().__init__(message)


class FileEmptyError(BaseTranscriptError):
    """Raised when attempting to parse an empty transcript file."""

    def __init__(self, message: str = "Cannot parse an empty transcript file") -> None:
        """Initialize the exception with a custom message."""
        super().__init__(message)


class FileInvalidFormatError(BaseTranscriptError):
    """Raised when transcript file doesn't follow expected manual format.

    File must start with chapter title, not a timestamp.
    """

    def __init__(
        self,
        message: str = "Transcript file must start with a chapter title, not a timestamp",
    ) -> None:
        """Initialize the exception with a custom message."""
        super().__init__(message)


class URLIsInvalidError(BaseTranscriptError):
    """Raised when URL format is invalid (empty or malformed text)."""

    def __init__(self, message: str = "Invalid URL format") -> None:
        """Initialize the exception with a custom message."""
        super().__init__(message)


class URLVideoUnavailableError(BaseTranscriptError):
    """Raised when YouTube video exists but is unavailable."""

    def __init__(self, message: str = "YouTube video unavailable") -> None:
        """Initialize the exception with a custom message."""
        super().__init__(message)


class URLSubtitlesNotFoundError(BaseTranscriptError):
    """Raised when YouTube video has no available subtitles."""

    def __init__(
        self, message: str = "This video doesn't have subtitles available"
    ) -> None:
        """Initialize the exception with a custom message."""
        super().__init__(message)


class URLRateLimitError(BaseTranscriptError):
    """Raised when access is temporarily blocked due to rate limiting."""

    def __init__(
        self,
        message: str = "YouTube is temporarily limiting requests - try again later",
    ) -> None:
        """Initialize the exception with a custom message."""
        super().__init__(message)


class URLNotYouTubeError(BaseTranscriptError):
    """Raised when URL is not a YouTube video URL."""

    def __init__(self, message: str = "URL is not a YouTube video") -> None:
        """Initialize the exception with a custom message."""
        super().__init__(message)


class URLIncompleteError(BaseTranscriptError):
    """Raised when YouTube URL has incomplete video ID."""

    def __init__(self, message: str = "YouTube URL is incomplete") -> None:
        """Initialize the exception with a custom message."""
        super().__init__(message)


class URLBotProtectionError(BaseTranscriptError):
    """Raised when YouTube requires verification to access video."""

    def __init__(
        self, message: str = "YouTube requires verification - try switching networks"
    ) -> None:
        """Initialize the exception with a custom message."""
        super().__init__(message)


def map_yt_dlp_exception(error: Exception) -> BaseTranscriptError:
    """Map yt-dlp exceptions to our custom exceptions based on error patterns.

    Args:
        error: The yt-dlp exception (DownloadError, ExtractorError, or UnsupportedError)

    Returns:
        Appropriate custom exception for the error pattern
    """
    error_msg = str(error)

    # Map specific error patterns to appropriate exceptions
    if "Sign in to confirm you're not a bot" in error_msg:
        return URLBotProtectionError()
    if "Unsupported URL" in error_msg:
        return URLNotYouTubeError()
    if "Incomplete YouTube ID" in error_msg:
        return URLIncompleteError()
    if "is not a valid URL" in error_msg:
        return URLIsInvalidError()
    if "Video unavailable" in error_msg:
        return URLVideoUnavailableError()
    # Default for unknown yt-dlp errors
    return URLVideoUnavailableError()
