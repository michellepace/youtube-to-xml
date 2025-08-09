"""YouTube Transcript Chapter Extractor.

Detects chapter titles based on structural patterns:
- First line of transcript (if not timestamp)
- Second line when exactly 2 lines between consecutive timestamps

Usage: python transcript_reporter.py <filename>

Note: This reference implementation identifies chapters but does not extract
their content. The youtube-to-xml converter will extend this to include
content extraction for XML generation.
"""

import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

# Constants
LINES_BETWEEN_TIMESTAMPS = 2
TIMESTAMP_PATTERN = re.compile(r"^\d{1,2}:\d{2}(:\d{2})?$")

# Formatting constants
SEPARATOR_WIDTH = 70


@dataclass(frozen=True, slots=True)
class Chapter:
    """Represents a chapter with line index, title, and start timestamp.

    Attributes:
        line_idx: Zero-based index of the chapter title line
        title: Chapter title text
        start_time: Starting timestamp for this chapter (e.g., "0:00")

    🔥 Note: For full XML converter implementation, this will be extended to include:
        content_lines: List[str]  # All transcript lines belonging to this chapter
    """

    line_idx: int
    title: str
    start_time: str
    # content_lines: List[str]    # 🔥 still to be implemented  # noqa: ERA001


def read_file(filename: str) -> list[str]:
    """Read file and return lines."""
    return Path(filename).read_text(encoding="utf-8").splitlines()


def find_timestamps(lines: list[str]) -> list[int]:
    """Find timestamp line indices."""
    return [i for i, line in enumerate(lines) if TIMESTAMP_PATTERN.match(line.strip())]


def find_chapters(lines: list[str], timestamp_indices: list[int]) -> list[Chapter]:
    """Find chapters using Rule 1 and Rule 2.

    🔥 Note: This function identifies chapter locations but does not extract
    the content lines. The XML converter will extend this to also capture
    all lines belonging to each chapter.
    """
    chapters = []

    # Rule 1: If first line isn't a timestamp and a timestamp follows,
    # it's the first chapter
    if lines and not TIMESTAMP_PATTERN.match(lines[0].strip()) and timestamp_indices:
        chapter_start_time = lines[timestamp_indices[0]]
        chapters.append(Chapter(0, lines[0], chapter_start_time))

    # Rule 2: When exactly 2 lines exist between consecutive timestamps,
    # the line before the second timestamp is a chapter
    for i in range(len(timestamp_indices) - 1):
        current_timestamp_idx = timestamp_indices[i]
        next_timestamp_idx = timestamp_indices[i + 1]
        lines_between = next_timestamp_idx - current_timestamp_idx - 1

        if lines_between == LINES_BETWEEN_TIMESTAMPS:
            chapter_line_idx = current_timestamp_idx + 2
            chapter_start_time = lines[next_timestamp_idx]
            chapters.append(
                Chapter(chapter_line_idx, lines[chapter_line_idx], chapter_start_time)
            )

    return chapters


def count_lines_between_timestamps(timestamp_indices: list[int]) -> list[int]:
    """Count lines between timestamps."""
    return [
        timestamp_indices[i + 1] - timestamp_indices[i] - 1
        for i in range(len(timestamp_indices) - 1)
    ]


def print_results(lines: list[str], timestamp_indices: list[int]) -> None:
    """Print analysis results in required format."""
    line_counts = count_lines_between_timestamps(timestamp_indices)
    line_count_frequency = Counter(line_counts)

    print("=" * SEPARATOR_WIDTH)
    print("TRANSCRIPT ANALYSIS REPORT — Lines, Timestamps, Chapters")
    print("=" * SEPARATOR_WIDTH)
    print(f"Total lines in file: {len(lines)}")
    print(f"Total timestamps found: {len(timestamp_indices)}")
    print(f"Total timestamp pairs analyzed: {len(line_counts)}")
    print()

    print("LINE COUNT DISTRIBUTION:")
    print("-" * SEPARATOR_WIDTH)
    for count in sorted(line_count_frequency.keys()):
        instances = line_count_frequency[count]
        print(f"No. of Instances with {count} line count: {instances}")

    print()
    print("VERIFICATION SUMMARY:")
    print("-" * SEPARATOR_WIDTH)
    unique_counts = set(line_counts)
    if unique_counts <= {1, 2}:
        print("✅ VERIFIED: Only 1 and 2 line counts exist between timestamps")
    else:
        unexpected = unique_counts - {1, 2}
        print(f"❌ FAILED: Found unexpected line counts: {unexpected}")


def main() -> None:
    """Main function."""
    filename = sys.argv[1]
    lines = read_file(filename)
    timestamp_indices = find_timestamps(lines)
    chapters = find_chapters(lines, timestamp_indices)
    print_results(lines, timestamp_indices)

    # Print found chapters
    print()
    print(f"CHAPTERS DETECTED: {len(chapters)} with start times")
    print("-" * SEPARATOR_WIDTH)
    for chapter in chapters:
        print(f"Line {chapter.line_idx + 1}: {chapter.title} ({chapter.start_time})")


if __name__ == "__main__":
    main()
