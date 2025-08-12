"""YouTube transcript parser module.

Parses YouTube transcript text files and extracts chapters with their content.
Based on structural patterns:
- First line of transcript (if not timestamp) is the first chapter
- When exactly 2 lines exist between consecutive timestamps, the line before
  the second timestamp is a new chapter title
"""

import re
from collections.abc import Sequence
from dataclasses import dataclass

# Timestamp pattern matching M:SS, MM:SS, H:MM:SS, HH:MM:SS, or HHH:MM:SS
# Minutes and seconds must be 00-59, hours can be up to 999
TIMESTAMP_PATTERN = re.compile(r"^(\d{1,2}:[0-5]\d(:[0-5]\d)?|\d{3}:[0-5]\d:[0-5]\d)$")

# Chapter detection rule: exactly 2 lines between timestamps indicates new chapter
LINES_FOR_CHAPTER_BOUNDARY = 2


@dataclass(frozen=True, slots=True)
class Chapter:
    """Chapter with content for XML generation."""

    title: str
    start_time: str
    content_lines: list[str]


def find_timestamps(transcript_lines: Sequence[str]) -> list[int]:
    """Find all timestamp line indices in the transcript."""
    return [
        i
        for i, line in enumerate(transcript_lines)
        if TIMESTAMP_PATTERN.match(line.strip())
    ]


def validate_transcript_format(raw_transcript: str) -> None:
    """Validate that the transcript meets format requirements."""
    if not raw_transcript.strip():
        msg = "Your file is empty"
        raise ValueError(msg)

    transcript_lines = raw_transcript.splitlines()

    # Check first line is not a timestamp
    if transcript_lines and TIMESTAMP_PATTERN.match(transcript_lines[0].strip()):
        msg = "Wrong format - transcript must start with a chapter title, not a timestamp"
        raise ValueError(msg)

    # Check that at least one timestamp exists
    timestamp_indices = find_timestamps(transcript_lines)
    if not timestamp_indices:
        msg = "Wrong format - transcript must contain at least one timestamp"
        raise ValueError(msg)


def _find_first_chapter(
    transcript_lines: list[str], timestamp_indices: list[int]
) -> dict | None:
    """Find first chapter metadata if transcript starts with a title."""
    if TIMESTAMP_PATTERN.match(transcript_lines[0].strip()):
        return None

    return {
        "title_index": 0,
        "title": transcript_lines[0],
        "start_time": transcript_lines[timestamp_indices[0]],
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
                    "start_time": transcript_lines[next_idx],
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
        # Determine content range for this chapter
        if i < len(chapter_metadata) - 1:
            content_end = chapter_metadata[i + 1]["title_index"]
        else:
            content_end = len(transcript_lines)

        # Extract content from start timestamp to range end
        content_lines = transcript_lines[chapter_data["content_start"] : content_end]

        result_chapters.append(
            Chapter(
                title=chapter_data["title"],
                start_time=chapter_data["start_time"],
                content_lines=list(content_lines),
            )
        )

    return result_chapters


def parse_transcript(raw_transcript: str) -> list[Chapter]:
    """Parse transcript text and return chapters with content.

    Raises:
        ValueError: If transcript format is invalid
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
