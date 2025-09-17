"""Shared data models for YouTube transcript processing.

Unified data structures used by both file and URL parsers.
Models store raw data - formatting happens at presentation layer.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class VideoMetadata:
    """Video metadata for XML output.

    Stores raw data format - conversion to display format happens
    in presentation layer via time_utils functions.
    """

    video_title: str = ""
    video_published: str = ""  # YYYYMMDD raw format or empty
    video_duration: int = 0  # seconds as integer (0 for file method)
    video_url: str = ""


@dataclass(frozen=True)
class TranscriptLine:
    """A single timestamped transcript line."""

    timestamp: float  # seconds
    text: str


@dataclass(frozen=True)
class Chapter:
    """A video chapter containing transcript lines within its time range."""

    title: str
    start_time: float
    end_time: float
    transcript_lines: list[TranscriptLine]


@dataclass(frozen=True)
class TranscriptDocument:
    """Complete transcript document with metadata and chapters."""

    metadata: VideoMetadata
    chapters: list[Chapter]
