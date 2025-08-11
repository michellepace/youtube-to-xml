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

# Timestamp pattern matching M:SS, MM:SS, H:MM:SS, or HH:MM:SS
# Minutes and seconds must be 00-59
TIMESTAMP_PATTERN = re.compile(r"^\d{1,2}:[0-5]\d(:[0-5]\d)?$")


@dataclass(frozen=True, slots=True)
class Chapter:
    """Chapter with all data needed for XML generation.

    Attributes:
        line_idx: Zero-based index of the chapter title line in the original text
        name: Chapter title text
        start_timestamp: Starting timestamp for this chapter (e.g., "0:00")
        content: All transcript lines belonging to this chapter (including timestamps)
    """

    line_idx: int
    name: str
    start_timestamp: str
    content: list[str]


def find_timestamps(lines: Sequence[str]) -> list[int]:
    """Find all timestamp line indices in the transcript.

    Args:
        lines: List of transcript lines

    Returns:
        List of zero-based indices where timestamps appear
    """
    return [i for i, line in enumerate(lines) if TIMESTAMP_PATTERN.match(line.strip())]


def validate_transcript_format(text: str) -> None:
    """Validate that the transcript meets format requirements.

    Args:
        text: Raw transcript text

    Raises:
        ValueError: If transcript is empty, starts with timestamp,
                   or contains no timestamps
    """
    if not text.strip():
        msg = "Your file is empty"
        raise ValueError(msg)

    lines = text.splitlines()

    # Check first line is not a timestamp
    if lines and TIMESTAMP_PATTERN.match(lines[0].strip()):
        msg = (
            "Wrong format - transcript must start with a chapter title, not a timestamp"
        )
        raise ValueError(msg)

    # Check that at least one timestamp exists
    timestamp_indices = find_timestamps(lines)
    if not timestamp_indices:
        msg = "Wrong format - transcript must contain at least one timestamp"
        raise ValueError(msg)


def identify_first_chapter(
    lines: Sequence[str], timestamp_indices: list[int]
) -> Chapter | None:
    """Identify the first chapter using Rule 1.

    Rule 1: If the first line isn't a timestamp and a timestamp follows,
    it's the first chapter.

    Args:
        lines: List of transcript lines
        timestamp_indices: List of timestamp line indices

    Returns:
        First chapter if found, None otherwise
    """
    if not lines or not timestamp_indices:
        return None

    # If first line is not a timestamp, it's the first chapter
    if not TIMESTAMP_PATTERN.match(lines[0].strip()):
        chapter_start_time = lines[timestamp_indices[0]]
        return Chapter(
            line_idx=0,
            name=lines[0],
            start_timestamp=chapter_start_time,
            content=[],  # Content will be filled later
        )

    return None


def detect_chapter_boundaries(
    lines: Sequence[str], timestamp_indices: list[int]
) -> list[Chapter]:
    """Detect subsequent chapters using the two-line rule.

    Rule 2: When exactly 2 lines exist between consecutive timestamps,
    the line before the second timestamp is a new chapter.

    Args:
        lines: List of transcript lines
        timestamp_indices: List of timestamp line indices

    Returns:
        List of chapters found using the two-line rule
    """
    chapters = []

    for i in range(len(timestamp_indices) - 1):
        current_timestamp_idx = timestamp_indices[i]
        next_timestamp_idx = timestamp_indices[i + 1]
        lines_between = next_timestamp_idx - current_timestamp_idx - 1

        if lines_between == 2:  # noqa: PLR2004
            # The line before the next timestamp is a chapter title
            chapter_line_idx = next_timestamp_idx - 1
            chapter_start_time = lines[next_timestamp_idx]
            chapters.append(
                Chapter(
                    line_idx=chapter_line_idx,
                    name=lines[chapter_line_idx],
                    start_timestamp=chapter_start_time,
                    content=[],  # Content will be filled later
                )
            )

    return chapters


def extract_chapter_content(
    lines: Sequence[str], chapters: list[Chapter], chapter_index: int
) -> list[str]:
    """Extract content lines for a specific chapter.

    Args:
        lines: List of all transcript lines
        chapters: List of all chapters (without content)
        chapter_index: Index of the chapter to extract content for

    Returns:
        List of content lines for the specified chapter
    """
    chapter = chapters[chapter_index]

    # Find the timestamp line for this chapter
    timestamp_indices = find_timestamps(lines)

    # Find where this chapter's timestamp appears
    chapter_timestamp_idx = None
    for idx in timestamp_indices:
        # For chapters after the first, timestamp should be right after title
        if lines[idx] == chapter.start_timestamp and (
            chapter.line_idx == 0 or idx == chapter.line_idx + 1
        ):
            chapter_timestamp_idx = idx
            break

    # If we can't find the timestamp, try the line right after the chapter title
    if (
        chapter_timestamp_idx is None
        and chapter.line_idx + 1 < len(lines)
        and lines[chapter.line_idx + 1] == chapter.start_timestamp
    ):
        chapter_timestamp_idx = chapter.line_idx + 1

    if chapter_timestamp_idx is None:
        return []

    # Determine the end boundary
    if chapter_index == len(chapters) - 1:
        # Last chapter: include everything from timestamp to end
        content = list(lines[chapter_timestamp_idx:])
    else:
        # Not last chapter: include until the next chapter's title line
        next_chapter = chapters[chapter_index + 1]
        content = list(lines[chapter_timestamp_idx : next_chapter.line_idx])

    return content


def parse_transcript(text: str) -> list[Chapter]:
    """Parse transcript text and return list of chapters with content.

    This is the main entry point for parsing YouTube transcripts.

    Args:
        text: Raw transcript text

    Returns:
        List of Chapter objects with complete data including content

    Raises:
        ValueError: If transcript is empty, starts with timestamp,
                   or contains no timestamps
    """
    # Validate format first
    validate_transcript_format(text)

    lines = text.splitlines()
    timestamp_indices = find_timestamps(lines)

    # Collect all chapters (first + subsequent)
    chapters = []

    # Find first chapter
    first_chapter = identify_first_chapter(lines, timestamp_indices)
    if first_chapter:
        chapters.append(first_chapter)

    # Find subsequent chapters using two-line rule
    subsequent_chapters = detect_chapter_boundaries(lines, timestamp_indices)
    chapters.extend(subsequent_chapters)

    # Sort chapters by line index to maintain order
    chapters.sort(key=lambda ch: ch.line_idx)

    # Extract content for each chapter
    chapters_with_content = []
    for i, chapter in enumerate(chapters):
        content = extract_chapter_content(lines, chapters, i)
        chapters_with_content.append(
            Chapter(
                line_idx=chapter.line_idx,
                name=chapter.name,
                start_timestamp=chapter.start_timestamp,
                content=content,
            )
        )

    return chapters_with_content
