"""Tests for the time utilities module.

Tests for timestamp conversion functions and time formatting utilities.
"""

import math

import pytest

from youtube_to_xml.exceptions import FileInvalidFormatError
from youtube_to_xml.time_utils import (
    TIMESTAMP_PATTERN,
    format_video_duration,
    format_video_published,
    seconds_to_timestamp,
    timestamp_to_seconds,
)


def test_timestamp_to_seconds_conversion() -> None:
    """Test conversion from timestamp string to float seconds."""
    assert timestamp_to_seconds("0:00") == 0.0
    assert timestamp_to_seconds("2:30") == 150.0
    assert timestamp_to_seconds("59:59") == 3599.0

    assert timestamp_to_seconds("1:00:00") == 3600.0
    assert timestamp_to_seconds("1:15:30") == 4530.0
    assert timestamp_to_seconds("10:15:30") == 36930.0

    assert timestamp_to_seconds("999:59:59") == 3599999.0
    assert timestamp_to_seconds(" 0:05 ") == 5.0


def test_seconds_to_timestamp_conversion() -> None:
    """Test conversion from float seconds to timestamp string."""
    assert seconds_to_timestamp(0.0) == "0:00"
    assert seconds_to_timestamp(150.0) == "2:30"
    assert seconds_to_timestamp(3599.0) == "59:59"

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
        "1:2:3:4",
        "25:61",
        "1:60:30",
        "",
        "abc:def",
    ]

    for invalid_ts in invalid_timestamps:
        with pytest.raises(FileInvalidFormatError, match="Invalid timestamp format"):
            timestamp_to_seconds(invalid_ts)


def test_seconds_to_timestamp_rejects_negative_values() -> None:
    """Test that negative values raise ValueError."""
    with pytest.raises(ValueError, match="seconds must be finite and >= 0"):
        seconds_to_timestamp(-1.0)


def test_seconds_to_timestamp_rejects_infinite_values() -> None:
    """Test that infinite values raise ValueError."""
    with pytest.raises(ValueError, match="seconds must be finite and >= 0"):
        seconds_to_timestamp(math.inf)


def test_seconds_to_timestamp_rejects_nan_values() -> None:
    """Test that NaN values raise ValueError."""
    with pytest.raises(ValueError, match="seconds must be finite and >= 0"):
        seconds_to_timestamp(math.nan)


def test_timestamp_pattern_matches_valid_formats() -> None:
    """Test that TIMESTAMP_PATTERN regex matches valid timestamp formats."""
    valid_timestamps = [
        "0:00",
        "1:23",
        "59:59",
        "1:00:00",
        "12:34:56",
        "999:59:59",
    ]

    for timestamp in valid_timestamps:
        assert TIMESTAMP_PATTERN.match(timestamp), f"Should match: {timestamp}"


def test_timestamp_pattern_rejects_invalid_formats() -> None:
    """Test that TIMESTAMP_PATTERN regex rejects invalid timestamp formats."""
    invalid_timestamps = [
        "1:60",
        "25:61",
        "1:60:30",
        "1:30:60",
        "abc:def",
        "1:2:3:4",
        "",
        ":",
        "1:",
        ":30",
    ]

    for timestamp in invalid_timestamps:
        assert not TIMESTAMP_PATTERN.match(timestamp), f"Should not match: {timestamp}"


def test_format_video_published_yyyymmdd_to_iso() -> None:
    """Test conversion from YYYYMMDD to YYYY-MM-DD format."""
    assert format_video_published("") == ""
    assert format_video_published("20250101") == "2025-01-01"
    assert format_video_published("19991231") == "1999-12-31"
    assert format_video_published("20240229") == "2024-02-29"


def test_format_video_published_invalid_format_passthrough() -> None:
    """Test that invalid date formats pass through unchanged."""
    assert format_video_published("2025-01-01") == "2025-01-01"
    assert format_video_published("not-a-date") == "not-a-date"
    assert format_video_published("202501") == "202501"
    assert format_video_published("2025013100") == "2025013100"
    assert format_video_published("20251301") == "20251301"


def test_format_video_duration_seconds_to_human() -> None:
    """Test conversion from seconds to human-readable duration."""
    assert format_video_duration(1) == "1s"
    assert format_video_duration(59) == "59s"
    assert format_video_duration(60) == "1m"
    assert format_video_duration(61) == "1m 1s"
    assert format_video_duration(3600) == "1h"
    assert format_video_duration(3660) == "1h 1m"
    assert format_video_duration(7322) == "2h 2m 2s"
    assert format_video_duration(36000) == "10h"
    assert format_video_duration(86399) == "23h 59m 59s"
    assert format_video_duration(3661.9) == "1h 1m 1s"


def test_format_video_duration_non_positive_returns_empty() -> None:
    """Zero and negative durations return empty string."""
    assert format_video_duration(0) == ""
    assert format_video_duration(-1) == ""


def test_format_video_duration_non_finite_returns_empty() -> None:
    """Non-finite values return empty string."""
    assert format_video_duration(math.inf) == ""
