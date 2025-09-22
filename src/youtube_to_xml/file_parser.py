"""YouTube transcript parser module.

Parses YouTube transcript text files and extracts chapters with their transcript lines.
Based on structural patterns:
- First line of transcript (if not timestamp) is the first chapter
- When exactly 2 lines exist between consecutive timestamps, the line before
  the second timestamp is a new chapter title

Timestamps are stored internally as float seconds for calculations, then
converted back to "M:SS" or "H:MM:SS" format for XML output.
"""

import math
from collections.abc import Sequence
from typing import TypedDict

from youtube_to_xml.exceptions import (
    FileEmptyError,
    FileInvalidFormatError,
)
from youtube_to_xml.models import (
    Chapter as ModelsChapter,
)
from youtube_to_xml.models import (
    TranscriptDocument,
    TranscriptLine,
    VideoMetadata,
)
from youtube_to_xml.time_utils import TIMESTAMP_PATTERN, timestamp_to_seconds


# Private TypedDict definition for internal chapter metadata
class _InternalChapterDict(TypedDict):
    """Internal type for chapter metadata during file parsing."""

    title_index: int
    title: str
    start_time: float
    transcript_start: int


# Chapter detection rule: exactly 2 lines between timestamps indicates new chapter
LINES_FOR_CHAPTER_BOUNDARY = 2

# Format validation constants
MINIMUM_LINES_REQUIRED = 3


def _find_timestamps(transcript_lines: Sequence[str]) -> list[int]:
    """Find all timestamp line indices in the transcript."""
    return [
        i
        for i, line in enumerate(transcript_lines)
        if TIMESTAMP_PATTERN.match(line.strip())
    ]


def _validate_transcript_format(raw_transcript: str) -> None:
    """Validate that the transcript is in YouTube format.

    Requirements
    - 1st line: (non-timestamp) → becomes first chapter
    - 2nd line: (timestamp e.g. "0:03") → becomes start_time for first chapter
    - 3rd line: (non-timestamp) → first transcript line of first chapter
    """
    if not raw_transcript.strip():
        raise FileEmptyError

    transcript_lines = raw_transcript.splitlines()

    # Remove blank lines for validation (consistent with processing)
    non_empty_lines = [line for line in transcript_lines if line.strip()]

    # Must have at least 3 lines for minimum format
    if len(non_empty_lines) < MINIMUM_LINES_REQUIRED:
        msg = "File must have at least 3 lines: chapter title, timestamp, transcript"
        raise FileInvalidFormatError(msg)

    # Line 1: Must be chapter title (non-timestamp)
    if TIMESTAMP_PATTERN.match(non_empty_lines[0].strip()):
        msg = "First line must be chapter title, not timestamp"
        raise FileInvalidFormatError(msg)

    # Line 2: Must be timestamp
    if not TIMESTAMP_PATTERN.match(non_empty_lines[1].strip()):
        msg = "Second line must be a timestamp"
        raise FileInvalidFormatError(msg)

    # Line 3: Must be transcript text (non-timestamp)
    if TIMESTAMP_PATTERN.match(non_empty_lines[2].strip()):
        msg = "Third line must be transcript text, not timestamp"
        raise FileInvalidFormatError(msg)


def _find_first_chapter(
    transcript_lines: list[str], timestamp_indices: list[int]
) -> _InternalChapterDict | None:
    """Find first chapter metadata if transcript starts with a title."""
    if TIMESTAMP_PATTERN.match(transcript_lines[0].strip()):
        return None

    return {
        "title_index": 0,
        "title": transcript_lines[0],
        "start_time": timestamp_to_seconds(transcript_lines[timestamp_indices[0]]),
        "transcript_start": timestamp_indices[0],
    }


def _find_subsequent_chapters(
    transcript_lines: list[str], timestamp_indices: list[int]
) -> list[_InternalChapterDict]:
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
                    "transcript_start": next_idx,
                }
            )
    return chapters


def parse_transcript_file(raw_transcript: str) -> TranscriptDocument:
    """Parse transcript file into unified TranscriptDocument format.

    Args:
        raw_transcript: Raw transcript text from file

    Returns:
        TranscriptDocument with empty metadata and structured chapters

    Raises:
        FileEmptyError: If transcript is empty
        FileInvalidFormatError: If format is invalid
    """
    sanitized_transcript = _sanitize_transcript_spacing(raw_transcript)

    _validate_transcript_format(sanitized_transcript)

    transcript_lines = sanitized_transcript.splitlines()
    timestamp_indices = _find_timestamps(transcript_lines)

    chapters_dicts = []

    # Find first chapter
    if first_chapter := _find_first_chapter(transcript_lines, timestamp_indices):
        chapters_dicts.append(first_chapter)

    # Find subsequent chapters
    chapters_dicts.extend(_find_subsequent_chapters(transcript_lines, timestamp_indices))

    # Build chapters with TranscriptLine objects
    chapters = []
    for i, chapter_dict in enumerate(chapters_dicts):
        # Determine transcript range and end time for this chapter
        if i < len(chapters_dicts) - 1:
            transcript_end_idx = chapters_dicts[i + 1]["title_index"]
            end_time = chapters_dicts[i + 1]["start_time"]
            # Enforce monotonic chapter boundaries
            if end_time <= chapter_dict["start_time"]:
                msg = "Subsequent chapter timestamps must be strictly increasing"
                raise FileInvalidFormatError(msg)
        else:
            transcript_end_idx = len(transcript_lines)
            end_time = math.inf

        # Extract transcript lines from start timestamp to range end
        start_idx = chapter_dict["transcript_start"]
        chapter_transcript_text = transcript_lines[start_idx:transcript_end_idx]

        # Convert alternating timestamp/text strings to TranscriptLine objects
        chapter_transcript_lines = _convert_string_lines_to_transcript_objects(
            chapter_transcript_text
        )

        chapters.append(
            ModelsChapter(
                title=chapter_dict["title"],
                start_time=chapter_dict["start_time"],
                end_time=end_time,
                transcript_lines=chapter_transcript_lines,
            )
        )

    return TranscriptDocument(
        metadata=VideoMetadata(),  # Empty metadata for file method
        chapters=chapters,
    )


def _sanitize_transcript_spacing(raw_transcript: str) -> str:
    """Normalize whitespace and remove blank lines from transcript.

    Args:
        raw_transcript: Raw transcript text with potentially inconsistent spacing

    Returns:
        Sanitized transcript string with normalized spacing (leading/trailing
        whitespace trimmed, multiple spaces collapsed to single spaces,
        blank lines removed)
    """
    sanitized_lines = [
        " ".join(line.split()) for line in raw_transcript.splitlines() if line.strip()
    ]
    return "\n".join(sanitized_lines)


def _convert_string_lines_to_transcript_objects(
    raw_lines: list[str],
) -> list["TranscriptLine"]:
    """Convert alternating timestamp/text strings to TranscriptLine objects.

    Args:
        raw_lines: List of strings in alternating timestamp/text pattern

    Returns:
        List of TranscriptLine objects
    """
    result = []
    i = 0

    while i < len(raw_lines):
        # Check if current line is a timestamp
        if TIMESTAMP_PATTERN.match(raw_lines[i].strip()):
            timestamp_str = raw_lines[i]

            # Get the text that follows (or empty if at end)
            if i + 1 < len(raw_lines):
                # Check if next line is also a timestamp (shouldn't happen normally)
                if TIMESTAMP_PATTERN.match(raw_lines[i + 1].strip()):
                    # Two consecutive timestamps - add empty text for first
                    text = ""
                    i += 1  # Only advance by 1 to process next timestamp
                else:
                    # Normal case: timestamp followed by text
                    text = raw_lines[i + 1]
                    i += 2  # Advance past both timestamp and text
            else:
                # Timestamp at end of chapter with no following text
                text = ""
                i += 1

            result.append(
                TranscriptLine(
                    timestamp=timestamp_to_seconds(timestamp_str),
                    text=text,
                )
            )
        else:
            # Non-timestamp line without preceding timestamp (shouldn't happen)
            # Skip it
            i += 1

    return result
