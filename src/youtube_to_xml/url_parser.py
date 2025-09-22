"""YouTube URL parser module for extracting transcripts and metadata.

This module provides the main interface for parsing YouTube URLs into
TranscriptDocument objects, extracted from scripts/url_to_transcript.py.

Core functions:
- parse_youtube_url(): Main interface that takes a URL and returns TranscriptDocument
- fetch_video_metadata_and_transcript(): Downloads metadata and transcript from YouTube
- extract_transcript_lines_from_json3(): Converts YouTube JSON3 to TranscriptLine objects
- assign_transcript_lines_to_chapters(): Groups transcript lines by chapters
"""

import json
import math
import tempfile
from pathlib import Path
from typing import TypedDict

import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError, UnsupportedError

from youtube_to_xml.exceptions import (
    URLTranscriptNotFoundError,
    map_yt_dlp_exception,
)
from youtube_to_xml.logging_config import get_logger
from youtube_to_xml.models import (
    Chapter,
    TranscriptDocument,
    TranscriptLine,
    VideoMetadata,
)
from youtube_to_xml.time_utils import MILLISECONDS_PER_SECOND


# Private TypedDict definitions for internal YouTube API data structures
class _ChapterDict(TypedDict):
    """Internal type for YouTube chapter data."""

    title: str
    start_time: float
    end_time: float


class _Json3Seg(TypedDict, total=False):
    """Internal type for JSON3 transcript segment."""

    utf8: str


class _Json3Event(TypedDict, total=False):
    """Internal type for JSON3 transcript event."""

    tStartMs: int
    segs: list[_Json3Seg]


# Module-level logger
logger = get_logger(__name__)


def fetch_video_metadata_and_transcript(
    url: str,
) -> tuple[VideoMetadata, list[TranscriptLine], list[_ChapterDict]]:
    """Extract video metadata and download transcript from YouTube using yt-dlp.

    Uses yt-dlp to fetch video information and transcript with built-in
    transcript handling and error management.

    Args:
        url: YouTube video URL

    Returns:
        Tuple of (VideoMetadata object, list of TranscriptLine objects,
                 list of chapter dicts)

    Raises:
        URLBotProtectionError: If YouTube requires verification
        URLNotYouTubeError: If URL is not a YouTube video
        URLIncompleteError: If YouTube URL has incomplete video ID
        URLIsInvalidError: If URL format is invalid
        URLVideoUnavailableError: If YouTube video is unavailable
        URLTranscriptNotFoundError: If no transcript is available
        URLRateLimitError: If YouTube rate limit is encountered
        URLUnmappedError: If an unexpected yt-dlp error occurs
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        options = {
            "no_warnings": True,
            "noprogress": True,
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["en", "en-orig"],  # English manual then auto-generated
            "subtitlesformat": "json3",
            "outtmpl": str(Path(temp_dir) / "%(title)s [%(id)s].%(ext)s"),
        }

        # Phase 1: Use yt-dlp to get data for transcript
        with yt_dlp.YoutubeDL(options) as ydl:
            try:
                # a) get complete video metadata from YouTube
                raw_metadata = ydl.extract_info(url, download=False)
                # b) download subtitle files (.json3 format)
                ydl.process_info(raw_metadata)
            except (DownloadError, ExtractorError, UnsupportedError) as e:
                mapped_exception = map_yt_dlp_exception(e)
                raise mapped_exception from e

        # Phase 2: File processing (outside yt-dlp context)
        # Note: raw_metadata is never None in practice - yt-dlp raises exceptions instead
        assert raw_metadata is not None  # Satisfy Pyright type checker  # noqa: S101

        # a) Locate downloaded transcript files
        transcript_files = list(Path(temp_dir).glob("*.json3"))

        # Implement transcript priority: manual English (.en.json3) over auto-generated
        def priority(p: Path) -> int:
            name = p.name
            # 0 = manual en, 1 = auto en-orig, 2 = everything else
            return (
                0
                if name.endswith(".en.json3")
                else 1
                if name.endswith(".en-orig.json3")
                else 2
            )

        transcript_files.sort(key=priority)

        # b) Parse transcript files into structured objects
        transcript_lines = []
        if transcript_files:
            transcript_file = transcript_files[0]
            # Read JSON3 format from disk
            transcript_data = json.loads(transcript_file.read_text(encoding="utf-8"))
            # Extract events → TranscriptLine objects
            events = transcript_data.get("events", [])
            transcript_lines = extract_transcript_lines_from_json3(events)
        else:
            raise URLTranscriptNotFoundError

        # Phase 3: Create structured metadata object from raw_metadata
        metadata = VideoMetadata(
            video_title=raw_metadata.get("title", "Untitled"),
            video_published=raw_metadata.get("upload_date", ""),  # Raw YYYYMMDD
            video_duration=int(raw_metadata.get("duration", 0)),  # Raw seconds as int
            video_url=raw_metadata.get("webpage_url", url),
        )

        # Handle chapters_dicts separately (not part of shared VideoMetadata model)
        chapters_dicts = raw_metadata.get("chapters", [])

        return metadata, transcript_lines, chapters_dicts


def extract_transcript_lines_from_json3(
    events: list[_Json3Event],
) -> list[TranscriptLine]:
    """Extract individual transcript lines from JSON3 event objects.

    Args:
        events: List of JSON3 event objects from YouTube transcript

    Returns:
        List of TranscriptLine objects with cleaned text and timestamps
    """
    transcript_lines = []

    for event in events:
        # Skip events without transcript data
        if "segs" not in event:
            continue

        # Combine text from all parts
        text_parts = [seg["utf8"] for seg in event["segs"] if "utf8" in seg]
        # Remove line breaks that YouTube adds for display formatting
        text = "".join(text_parts).strip().replace("\n", " ")
        if not text:
            continue

        # Convert milliseconds to seconds
        start_ms = event.get("tStartMs", 0)
        start_seconds = start_ms / MILLISECONDS_PER_SECOND

        transcript_lines.append(TranscriptLine(start_seconds, text))

    return transcript_lines


def assign_transcript_lines_to_chapters(
    metadata: VideoMetadata,
    transcript_lines: list[TranscriptLine],
    chapters_dicts: list[_ChapterDict],
) -> list[Chapter]:
    """Assign transcript lines to chapters based on temporal boundaries.

    Args:
        metadata: Video metadata for title
        transcript_lines: List of all individual transcript lines
        chapters_dicts: List of chapter dictionaries from YouTube API

    Returns:
        List of Chapter objects with assigned transcript lines
    """
    if not chapters_dicts:
        # No chapters - create single chapter with video title
        return [
            Chapter(
                title=metadata.video_title,
                start_time=0,
                end_time=math.inf,
                transcript_lines=transcript_lines,
            )
        ]

    chapters = []

    for i, chapter_dict in enumerate(chapters_dicts):
        chapter_start_time = float(chapter_dict.get("start_time", 0))

        # End time is start of next chapter, or infinity for last chapter
        if i + 1 < len(chapters_dicts):
            chapter_end_time = float(chapters_dicts[i + 1]["start_time"])
        else:
            chapter_end_time = math.inf

        # Filter transcript lines within this chapter's time range
        chapter_transcript_lines = [
            line
            for line in transcript_lines
            if chapter_start_time <= line.timestamp < chapter_end_time
        ]

        chapters.append(
            Chapter(
                title=chapter_dict.get("title", f"Chapter {i + 1}"),
                start_time=chapter_start_time,
                end_time=chapter_end_time,
                transcript_lines=chapter_transcript_lines,
            )
        )

    return chapters


def parse_youtube_url(url: str) -> TranscriptDocument:
    """Parse YouTube URL and return structured transcript document.

    Main interface function that coordinates the complete URL processing pipeline:
    1. Fetch video metadata and transcript from YouTube
    2. Extract transcript lines from JSON3 format
    3. Assign transcript lines to chapters
    4. Return complete TranscriptDocument

    Args:
        url: YouTube video URL

    Returns:
        TranscriptDocument with video metadata and chapters containing transcript lines

    Raises:
        URLBotProtectionError: If YouTube requires verification
        URLNotYouTubeError: If URL is not a YouTube video
        URLIncompleteError: If YouTube URL has incomplete video ID
        URLIsInvalidError: If URL format is invalid
        URLVideoUnavailableError: If YouTube video is unavailable
        URLTranscriptNotFoundError: If no transcript is available
        URLRateLimitError: If YouTube rate limit is encountered
        URLUnmappedError: If an unexpected yt-dlp error occurs
    """
    logger.info("Processing video: %s", url)

    # Step 1: Fetch metadata and download transcript using yt-dlp
    metadata, transcript_lines, chapters_dicts = fetch_video_metadata_and_transcript(url)

    # Step 2: Assign transcript lines to chapters
    chapters = assign_transcript_lines_to_chapters(
        metadata, transcript_lines, chapters_dicts
    )

    # Step 3: Create and return TranscriptDocument
    return TranscriptDocument(metadata=metadata, chapters=chapters)
