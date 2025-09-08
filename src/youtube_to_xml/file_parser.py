"""YouTube transcript parser module.

Parses YouTube transcript text files and extracts chapters with their content.
Based on structural patterns:
- First line of transcript (if not timestamp) is the first chapter
- When exactly 2 lines exist between consecutive timestamps, the line before
  the second timestamp is a new chapter title

Timestamps are stored internally as float seconds for calculations, then
converted back to "M:SS" or "H:MM:SS" format for XML output.
"""

import re
from collections.abc import Sequence
from dataclasses import dataclass

from youtube_to_xml.exceptions import (
    FileEmptyError,
    FileInvalidFormatError,
)

# Timestamp pattern matching M:SS, MM:SS, H:MM:SS, HH:MM:SS, or HHH:MM:SS
# Minutes and seconds must be 00-59, hours can be up to 999
TIMESTAMP_PATTERN = re.compile(r"^(\d{1,2}:[0-5]\d(:[0-5]\d)?|\d{3}:[0-5]\d:[0-5]\d)$")

# Chapter detection rule: exactly 2 lines between timestamps indicates new chapter
LINES_FOR_CHAPTER_BOUNDARY = 2

# Format validation constants
MINIMUM_LINES_REQUIRED = 3

# Time conversion constants
SECONDS_PER_HOUR = 3600
SECONDS_PER_MINUTE = 60
TIMESTAMP_PARTS_SHORT = 2  # M:SS format
TIMESTAMP_PARTS_LONG = 3  # H:MM:SS format


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
    # Validate format using existing regex pattern first
    if not TIMESTAMP_PATTERN.match(timestamp_str.strip()):
        msg = f"Invalid timestamp format: {timestamp_str}"
        raise FileInvalidFormatError(msg)

    parts = timestamp_str.split(":")

    if len(parts) == TIMESTAMP_PARTS_SHORT:  # M:SS or MM:SS format
        minutes, seconds = parts
        return float(minutes) * SECONDS_PER_MINUTE + float(seconds)
    if len(parts) == TIMESTAMP_PARTS_LONG:  # H:MM:SS format
        hours, minutes, seconds = parts
        return (
            float(hours) * SECONDS_PER_HOUR
            + float(minutes) * SECONDS_PER_MINUTE
            + float(seconds)
        )

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
    """
    total_seconds = int(seconds)
    hours = total_seconds // SECONDS_PER_HOUR
    minutes = (total_seconds % SECONDS_PER_HOUR) // SECONDS_PER_MINUTE
    secs = total_seconds % SECONDS_PER_MINUTE

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


@dataclass(frozen=True, slots=True)
class Chapter:
    """Chapter with content for XML generation."""

    title: str
    start_time: float  # seconds
    end_time: float  # seconds (float("inf") for last chapter)
    content_lines: list[str]

    @property
    def duration(self) -> float:
        """Calculate chapter duration."""
        return self.end_time - self.start_time


def find_timestamps(transcript_lines: Sequence[str]) -> list[int]:
    """Find all timestamp line indices in the transcript."""
    return [
        i
        for i, line in enumerate(transcript_lines)
        if TIMESTAMP_PATTERN.match(line.strip())
    ]


def validate_transcript_format(raw_transcript: str) -> None:
    """Validate that the transcript is in YouTube format.

    Requirements
    - 1st line: (non-timestamp) → becomes first chapter
    - 2nd line: (timestamp e.g. "0:03") → becomes start_time for first chapter
    - 3rd line: (non-timestamp) → first content line of first chapter
    """
    if not raw_transcript.strip():
        raise FileEmptyError

    transcript_lines = raw_transcript.splitlines()

    # Remove blank lines for validation (consistent with processing)
    non_empty_lines = [line for line in transcript_lines if line.strip()]

    # Must have at least 3 lines for minimum format
    if len(non_empty_lines) < MINIMUM_LINES_REQUIRED:
        msg = "File must have at least 3 lines: chapter title, timestamp, content"
        raise FileInvalidFormatError(msg)

    # Line 1: Must be chapter title (non-timestamp)
    if TIMESTAMP_PATTERN.match(non_empty_lines[0].strip()):
        msg = "First line must be chapter title, not timestamp"
        raise FileInvalidFormatError(msg)

    # Line 2: Must be timestamp
    if not TIMESTAMP_PATTERN.match(non_empty_lines[1].strip()):
        msg = "Second line must be a timestamp"
        raise FileInvalidFormatError(msg)

    # Line 3: Must be content (non-timestamp)
    if TIMESTAMP_PATTERN.match(non_empty_lines[2].strip()):
        msg = "Third line must be content, not timestamp"
        raise FileInvalidFormatError(msg)


def _find_first_chapter(
    transcript_lines: list[str], timestamp_indices: list[int]
) -> dict | None:
    """Find first chapter metadata if transcript starts with a title."""
    if TIMESTAMP_PATTERN.match(transcript_lines[0].strip()):
        return None

    return {
        "title_index": 0,
        "title": transcript_lines[0],
        "start_time": timestamp_to_seconds(transcript_lines[timestamp_indices[0]]),
        "content_start": timestamp_indices[0],
    }


def _find_subsequent_chapters(
    transcript_lines: list[str], timestamp_indices: list[int]
) -> list[dict]:
    """Find subsequent chapters using the 2-line gap rule."""
    chapters = []
    for i in range(len(timestamp_indices) - 1):
        current_idx = timestamp_indices[i]
        next_idx = timestamp_indices[i + 1]

        if next_idx - current_idx - 1 == LINES_FOR_CHAPTER_BOUNDARY:
            chapter_title_idx = next_idx - 1
            chapters.append(
                {
                    "title_index": chapter_title_idx,
                    "title": transcript_lines[chapter_title_idx],
                    "start_time": timestamp_to_seconds(transcript_lines[next_idx]),
                    "content_start": next_idx,
                }
            )
    return chapters


def _extract_content_for_chapters(
    transcript_lines: list[str], chapter_metadata: list[dict]
) -> list[Chapter]:
    """Extract content lines for each chapter and create Chapter objects."""
    result_chapters = []
    for i, chapter_data in enumerate(chapter_metadata):
        # Determine content range and end time for this chapter
        if i < len(chapter_metadata) - 1:
            content_end = chapter_metadata[i + 1]["title_index"]
            end_time = chapter_metadata[i + 1]["start_time"]
        else:
            content_end = len(transcript_lines)
            end_time = float("inf")

        # Extract content from start timestamp to range end
        content_lines = transcript_lines[chapter_data["content_start"] : content_end]

        result_chapters.append(
            Chapter(
                title=chapter_data["title"],
                start_time=chapter_data["start_time"],
                end_time=end_time,
                content_lines=list(content_lines),
            )
        )

    return result_chapters


def parse_transcript_file(raw_transcript: str) -> list[Chapter]:
    """Parse transcript file contents and return chapters with content.

    Args:
        raw_transcript: Raw transcript text content from file

    Returns:
        List of Chapter objects with titles, timestamps, and content

    Raises:
        FileEmptyError: If transcript file is empty
        FileInvalidFormatError: If transcript format is invalid
    """
    validate_transcript_format(raw_transcript)

    # Remove all blank lines from the transcript
    transcript_lines = [line for line in raw_transcript.splitlines() if line.strip()]
    timestamp_indices = find_timestamps(transcript_lines)

    chapters_metadata = []

    # Find first chapter
    if first_chapter := _find_first_chapter(transcript_lines, timestamp_indices):
        chapters_metadata.append(first_chapter)

    # Find subsequent chapters
    chapters_metadata.extend(
        _find_subsequent_chapters(transcript_lines, timestamp_indices)
    )

    # Extract content for chapters (order is already correct)
    return _extract_content_for_chapters(transcript_lines, chapters_metadata)
