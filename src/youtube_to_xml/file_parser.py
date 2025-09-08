"""YouTube transcript parser module.

Parses YouTube transcript text files and extracts chapters with their content.
Based on structural patterns:
- First line of transcript (if not timestamp) is the first chapter
- When exactly 2 lines exist between consecutive timestamps, the line before
  the second timestamp is a new chapter title

Timestamps are stored internally as float seconds for calculations, then
converted back to "M:SS" or "H:MM:SS" format for XML output.
"""

import math
from collections.abc import Sequence
from dataclasses import dataclass

from youtube_to_xml.exceptions import (
    FileEmptyError,
    FileInvalidFormatError,
)
from youtube_to_xml.time_utils import TIMESTAMP_PATTERN, timestamp_to_seconds

# Chapter detection rule: exactly 2 lines between timestamps indicates new chapter
LINES_FOR_CHAPTER_BOUNDARY = 2

# Format validation constants
MINIMUM_LINES_REQUIRED = 3


@dataclass(frozen=True, slots=True)
class Chapter:
    """Chapter with content for XML generation."""

    title: str
    start_time: float  # seconds
    end_time: float  # seconds (math.inf for last chapter)
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
            # Enforce monotonic chapter boundaries
            if end_time <= chapter_data["start_time"]:
                msg = "Subsequent chapter timestamps must be strictly increasing"
                raise FileInvalidFormatError(msg)
        else:
            content_end = len(transcript_lines)
            end_time = math.inf

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
