"""Shared data models for YouTube transcript processing.

Unified data structures used by both file and URL parsers.
Models store raw data - formatting happens at presentation layer.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VideoMetadata:
    """Video metadata for XML output.

    Stores raw data format - conversion to display format happens
    in presentation layer via time_utils functions (docs/adr/0003).

    Attributes:
        video_title: Title as given by YouTube
        video_published: Upload date as raw YYYYMMDD, or empty
        video_duration: Length in whole seconds (0 for file input)
        video_url: Canonical watch URL
    """

    video_title: str = ""
    video_published: str = ""
    video_duration: int = 0
    video_url: str = ""


@dataclass(frozen=True, slots=True)
class TranscriptLine:
    """A single timestamped transcript line.

    Attributes:
        timestamp: Start time in seconds
        text: Spoken text
    """

    timestamp: float
    text: str


@dataclass(frozen=True, slots=True)
class Chapter:
    """A video chapter containing transcript lines within its time range.

    Attributes:
        title: Chapter title
        start_time: Start in seconds
        end_time: End in seconds (math.inf for the last chapter)
        transcript_lines: Lines spoken within [start_time, end_time)
    """

    title: str
    start_time: float
    end_time: float
    transcript_lines: list[TranscriptLine]


@dataclass(frozen=True, slots=True)
class TranscriptDocument:
    """Complete transcript document with metadata and chapters."""

    metadata: VideoMetadata
    chapters: list[Chapter]
