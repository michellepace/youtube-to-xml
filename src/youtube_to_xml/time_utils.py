"""Time conversion utilities for timestamp formatting and parsing.

Shared utilities for converting between seconds and timestamp strings.
Used by both file parser and URL-based transcript processors.
"""

import math
import re

from youtube_to_xml.exceptions import FileInvalidFormatError

# Time conversion constants
SECONDS_PER_HOUR = 3600
SECONDS_PER_MINUTE = 60
MILLISECONDS_PER_SECOND = 1000.0

# Timestamp format constants
TIMESTAMP_PARTS_SHORT = 2  # M:SS format
TIMESTAMP_PARTS_LONG = 3  # H:MM:SS format

# Timestamp pattern matching M:SS, MM:SS, H:MM:SS, HH:MM:SS, or HHH:MM:SS
# Minutes and seconds must be 00-59, hours can be up to 999
TIMESTAMP_PATTERN = re.compile(r"^(\d{1,2}:[0-5]\d(:[0-5]\d)?|\d{3}:[0-5]\d:[0-5]\d)$")


def timestamp_to_seconds(timestamp_str: str) -> float:
    """Convert timestamp string to float seconds.

    Args:
        timestamp_str: Time in "M:SS", "MM:SS", or "H:MM:SS" format

    Returns:
        Time in seconds as float

    Examples:
        "2:30" -> 150.0
        "1:15:30" -> 4530.0

    Raises:
        FileInvalidFormatError: If timestamp format is invalid
    """
    # Validate format using regex pattern
    ts = timestamp_str.strip()
    if not TIMESTAMP_PATTERN.match(ts):
        msg = f"Invalid timestamp format: {timestamp_str}"
        raise FileInvalidFormatError(msg)

    parts = ts.split(":")

    if len(parts) == TIMESTAMP_PARTS_SHORT:  # M:SS or MM:SS format
        minutes, seconds = parts
        m = int(minutes)
        s = int(seconds)
        return float(m * SECONDS_PER_MINUTE + s)

    if len(parts) == TIMESTAMP_PARTS_LONG:  # H:MM:SS format
        hours, minutes, seconds = parts
        h = int(hours)
        m = int(minutes)
        s = int(seconds)
        return float(h * SECONDS_PER_HOUR + m * SECONDS_PER_MINUTE + s)

    msg = f"Invalid timestamp format: {timestamp_str}"
    raise FileInvalidFormatError(msg)


def seconds_to_timestamp(seconds: float) -> str:
    """Convert float seconds to timestamp string.

    Args:
        seconds: Time in seconds

    Returns:
        Formatted timestamp string ("M:SS" or "H:MM:SS")

    Examples:
        150.0 -> "2:30"
        4530.0 -> "1:15:30"

    Raises:
        ValueError: If seconds is not finite or negative
    """
    if not math.isfinite(seconds) or seconds < 0:
        msg = "seconds must be finite and >= 0"
        raise ValueError(msg)

    total_seconds = int(seconds)
    hours = total_seconds // SECONDS_PER_HOUR
    minutes = (total_seconds % SECONDS_PER_HOUR) // SECONDS_PER_MINUTE
    secs = total_seconds % SECONDS_PER_MINUTE

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"
