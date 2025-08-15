"""Custom exceptions for YouTube transcript processing."""


class EmptyFileError(ValueError):
    """Raised when attempting to parse an empty transcript file."""

    def __init__(self, message: str = "Cannot parse an empty transcript file") -> None:
        """Initialize the exception with a custom message."""
        super().__init__(message)


class InvalidTranscriptFormatError(ValueError):
    """Raised when transcript doesn't follow required format."""

    def __init__(
        self,
        message: str = "Transcript must start with a chapter title, not a timestamp",
    ) -> None:
        """Initialize the exception with a custom message."""
        super().__init__(message)


class MissingTimestampError(ValueError):
    """Raised when transcript contains no timestamps."""

    def __init__(
        self,
        message: str = "Transcript must contain at least one timestamp",
    ) -> None:
        """Initialize the exception with a custom message."""
        super().__init__(message)
