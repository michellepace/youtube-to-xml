"""YouTube Transcript Chapter Extractor.

Detects chapter titles based on structural patterns:
- First line of transcript (if not timestamp)
- Second line when exactly 2 lines between consecutive timestamps

Usage: python transcript_reporter.py <filename>
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
SEPERATOR_WIDTH = 70


@dataclass(frozen=True, slots=True)
class Chapter:
    """Represents a chapter with line index, text, and timestamp."""

    line_idx: int
    text: str
    timestamp: str


def read_file(filename: str) -> list[str]:
    """Read file and return lines."""
    return Path(filename).read_text(encoding="utf-8").splitlines()


def find_timestamps(lines: list[str]) -> list[int]:
    """Find timestamp line indices."""
    return [i for i, line in enumerate(lines) if TIMESTAMP_PATTERN.match(line.strip())]


def find_chapters(lines: list[str], timestamp_indices: list[int]) -> list[Chapter]:
    """Find chapters using the general pattern."""
    chapters = []

    # Rule 1: First line is always a chapter (if not timestamp)
    if lines and not TIMESTAMP_PATTERN.match(lines[0].strip()):
        first_timestamp = lines[timestamp_indices[0]]
        chapters.append(Chapter(0, lines[0], first_timestamp))

    # Rule 2: Second line when exactly 2 lines exist between timestamps
    for i in range(len(timestamp_indices) - 1):
        current_timestamp_idx = timestamp_indices[i]
        next_timestamp_idx = timestamp_indices[i + 1]
        lines_between = next_timestamp_idx - current_timestamp_idx - 1

        if lines_between == LINES_BETWEEN_TIMESTAMPS:
            chapter_line_idx = current_timestamp_idx + 2
            chapter_timestamp = lines[next_timestamp_idx]
            chapters.append(
                Chapter(chapter_line_idx, lines[chapter_line_idx], chapter_timestamp)
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

    print("=" * SEPERATOR_WIDTH)
    print("TRANSCRIPT ANALYSIS REPORT — Lines, Timestamps, Chapters")
    print("=" * SEPERATOR_WIDTH)
    print(f"Total lines in file: {len(lines)}")
    print(f"Total timestamps found: {len(timestamp_indices)}")
    print(f"Total timestamp pairs analyzed: {len(line_counts)}")
    print()

    print("LINE COUNT DISTRIBUTION:")
    print("-" * SEPERATOR_WIDTH)
    for count in sorted(line_count_frequency.keys()):
        instances = line_count_frequency[count]
        print(f"No. of Instances with {count} line count: {instances}")

    print()
    print("VERIFICATION SUMMARY:")
    print("-" * SEPERATOR_WIDTH)
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
    print("-" * SEPERATOR_WIDTH)
    for chapter in chapters:
        print(f"Line {chapter.line_idx + 1}: {chapter.text} ({chapter.timestamp})")


if __name__ == "__main__":
    main()
