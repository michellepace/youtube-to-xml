"""Tests for the time utilities module.

Tests for timestamp conversion functions and time formatting utilities.
"""

import math

import pytest

from youtube_to_xml.exceptions import FileInvalidFormatError
from youtube_to_xml.time_utils import (
    TIMESTAMP_PATTERN,
    seconds_to_timestamp,
    timestamp_to_seconds,
)


def test_timestamp_to_seconds_conversion() -> None:
    """Test conversion from timestamp string to float seconds."""
    # M:SS format
    assert timestamp_to_seconds("0:00") == 0.0
    assert timestamp_to_seconds("2:30") == 150.0
    assert timestamp_to_seconds("59:59") == 3599.0

    # H:MM:SS format
    assert timestamp_to_seconds("1:00:00") == 3600.0
    assert timestamp_to_seconds("1:15:30") == 4530.0
    assert timestamp_to_seconds("10:15:30") == 36930.0

    # High hour and whitespace cases
    assert timestamp_to_seconds("999:59:59") == 3599999.0
    assert timestamp_to_seconds(" 0:05 ") == 5.0


def test_seconds_to_timestamp_conversion() -> None:
    """Test conversion from float seconds to timestamp string."""
    # Less than an hour - M:SS format
    assert seconds_to_timestamp(0.0) == "0:00"
    assert seconds_to_timestamp(150.0) == "2:30"
    assert seconds_to_timestamp(3599.0) == "59:59"

    # Hour or more - H:MM:SS format
    assert seconds_to_timestamp(3600.0) == "1:00:00"
    assert seconds_to_timestamp(4530.0) == "1:15:30"
    assert seconds_to_timestamp(36930.0) == "10:15:30"


def test_seconds_to_timestamp_fractional_floors() -> None:
    """Fractional seconds are floored when formatting."""
    assert seconds_to_timestamp(2.9) == "0:02"
    assert seconds_to_timestamp(59.999) == "0:59"


def test_timestamp_to_seconds_raises_error_for_invalid_format() -> None:
    """Test that invalid timestamp formats raise FileInvalidFormatError."""
    invalid_timestamps = [
        "invalid",
        "1:2:3:4",  # too many parts
        "25:61",  # invalid minutes/seconds
        "1:60:30",  # invalid minutes
        "",  # empty string
        "abc:def",  # non-numeric
    ]

    for invalid_ts in invalid_timestamps:
        with pytest.raises(FileInvalidFormatError, match="Invalid timestamp format"):
            timestamp_to_seconds(invalid_ts)


def test_seconds_to_timestamp_rejects_negative_values() -> None:
    """Test that negative values raise ValueError."""
    with pytest.raises(ValueError, match="seconds must be finite and >= 0"):
        seconds_to_timestamp(-1.0)

    with pytest.raises(ValueError, match="seconds must be finite and >= 0"):
        seconds_to_timestamp(-0.1)


def test_seconds_to_timestamp_rejects_infinite_values() -> None:
    """Test that infinite values raise ValueError."""
    with pytest.raises(ValueError, match="seconds must be finite and >= 0"):
        seconds_to_timestamp(math.inf)

    with pytest.raises(ValueError, match="seconds must be finite and >= 0"):
        seconds_to_timestamp(-math.inf)


def test_seconds_to_timestamp_rejects_nan_values() -> None:
    """Test that NaN values raise ValueError."""
    with pytest.raises(ValueError, match="seconds must be finite and >= 0"):
        seconds_to_timestamp(math.nan)


def test_timestamp_pattern_matches_valid_formats() -> None:
    """Test that TIMESTAMP_PATTERN regex matches valid timestamp formats."""
    valid_timestamps = [
        "0:00",
        "1:23",
        "59:59",  # M:SS and MM:SS
        "1:00:00",
        "12:34:56",
        "999:59:59",  # H:MM:SS and HH:MM:SS and HHH:MM:SS
    ]

    for timestamp in valid_timestamps:
        assert TIMESTAMP_PATTERN.match(timestamp), f"Should match: {timestamp}"


def test_timestamp_pattern_rejects_invalid_formats() -> None:
    """Test that TIMESTAMP_PATTERN regex rejects invalid timestamp formats."""
    invalid_timestamps = [
        "1:60",
        "25:61",  # invalid minutes/seconds
        "1:60:30",
        "1:30:60",  # invalid minutes/seconds
        "abc:def",
        "1:2:3:4",  # non-numeric or too many parts
        "",
        ":",
        "1:",
        ":30",  # empty or incomplete
    ]

    for timestamp in invalid_timestamps:
        assert not TIMESTAMP_PATTERN.match(timestamp), f"Should not match: {timestamp}"
