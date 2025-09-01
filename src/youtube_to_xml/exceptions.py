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


class URLFormatError(BaseTranscriptError):
    """Raised when YouTube URL is invalid or malformed."""

    def __init__(self, message: str = "Invalid YouTube URL format") -> None:
        """Initialize the exception with a custom message."""
        super().__init__(message)


class URLVideoNotFoundError(BaseTranscriptError):
    """Raised when YouTube video is not found or unavailable."""

    def __init__(self, message: str = "YouTube video not found or unavailable") -> None:
        """Initialize the exception with a custom message."""
        super().__init__(message)


class URLSubtitlesNotFoundError(BaseTranscriptError):
    """Raised when YouTube video has no available subtitles."""

    def __init__(self, message: str = "No subtitles available for this video") -> None:
        """Initialize the exception with a custom message."""
        super().__init__(message)


class URLRateLimitError(BaseTranscriptError):
    """Raised when access is temporarily blocked due to rate limiting."""

    def __init__(
        self,
        message: str = "YouTube rate limit in force, transcript temporarily unavailable",
    ) -> None:
        """Initialize the exception with a custom message."""
        super().__init__(message)
