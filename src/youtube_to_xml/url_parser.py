"""YouTube URL parser module for extracting transcripts and metadata.

This module provides the main interface for parsing YouTube URLs into
TranscriptDocument objects, extracted from scripts/url_to_transcript.py.

Public functions:
- parse_youtube_url(): Main interface that takes a URL and returns TranscriptDocument

Private functions:
- _fetch_video_metadata_and_transcript(): Downloads metadata and transcript from YouTube
- _extract_transcript_lines_from_files(): Processes downloaded transcript files into lines
- _extract_transcript_lines_from_json3(): Converts YouTube JSON3 to TranscriptLine objects
- _assign_transcript_lines_to_chapters(): Groups transcript lines by chapters
- _get_youtube_transcript_file_priority(): Determines transcript file selection priority
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


# Private TypedDict definitions for internal data structures
class _InternalChapterDict(TypedDict):
    """Internal type for YouTube API chapter data."""

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


# Transcript language preferences (ordered by priority - index IS priority)
_TRANSCRIPT_LANGUAGE_PREFERENCES = (
    "en",  # Manual English subtitles (priority 0)
    "en-orig",  # Auto-generated English (priority 1)
)

# Subtitle/transcript file extension for yt-dlp
_TRANSCRIPT_FILE_EXT = "json3"

# Module-level logger
logger = get_logger(__name__)


def _get_youtube_transcript_file_priority(transcript_file_path: Path) -> int:
    """Return priority for transcript file selection (0=highest)."""
    name = transcript_file_path.name

    # Check each language preference in order (index = priority)
    for priority, lang in enumerate(_TRANSCRIPT_LANGUAGE_PREFERENCES):
        if name.endswith(f".{lang}.{_TRANSCRIPT_FILE_EXT}"):
            return priority

    # Return lowest priority for unrecognized languages
    return len(_TRANSCRIPT_LANGUAGE_PREFERENCES)


def _create_video_metadata(raw_metadata: dict, url: str) -> VideoMetadata:
    """Build VideoMetadata object from raw yt-dlp metadata.

    Args:
        raw_metadata: Raw metadata dictionary from yt-dlp
        url: Original YouTube URL (fallback for webpage_url)

    Returns:
        VideoMetadata object with extracted information
    """
    return VideoMetadata(
        video_title=raw_metadata.get("title", "Untitled"),
        video_published=raw_metadata.get("upload_date", ""),  # Raw YYYYMMDD
        video_duration=int(raw_metadata.get("duration", 0)),  # Raw seconds as int
        video_url=raw_metadata.get("webpage_url", url),
    )


def _download_transcript_with_yt_dlp(url: str, temp_dir: Path) -> dict:
    """Handle yt-dlp configuration and download of transcript.

    Args:
        url: YouTube video URL
        temp_dir: Temporary directory for downloaded files

    Returns:
        Raw metadata dictionary from yt-dlp
    """
    yt_dlp_options = {
        # Core purpose: Download transcripts
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": _TRANSCRIPT_LANGUAGE_PREFERENCES,
        "subtitlesformat": _TRANSCRIPT_FILE_EXT,
        # Download behavior: Skip video, only get transcripts
        "skip_download": True,
        "noplaylist": True,
        # Output formatting: Where to save files
        "outtmpl": str(Path(temp_dir) / "%(title)s [%(id)s].%(ext)s"),
        # UI/UX: Quiet operation for CLI user experience
        "no_warnings": True,
        "noprogress": True,
    }

    with yt_dlp.YoutubeDL(yt_dlp_options) as ydl:
        try:
            # a) YT-DLP: get complete video metadata from YouTube
            raw_metadata = ydl.extract_info(url, download=False)
            # b) YT-DLP: download subtitle files (.json3 format)
            ydl.process_info(raw_metadata)
        except (DownloadError, ExtractorError, UnsupportedError) as e:
            mapped_exception = map_yt_dlp_exception(e)
            raise mapped_exception from e

    assert raw_metadata is not None  # Satisfy Pyright type checker  # noqa: S101
    return raw_metadata


def _extract_transcript_lines_from_files(temp_dir: Path) -> list[TranscriptLine]:
    """Process downloaded transcript files into TranscriptLine objects.

    Finds transcript files, selects the best one by language priority,
    and extracts transcript lines from JSON3 format.

    Args:
        temp_dir: Directory containing downloaded transcript files

    Returns:
        List of TranscriptLine objects

    Raises:
        URLTranscriptNotFoundError: If no transcript files found
    """
    # Locate downloaded transcript files
    transcript_files = list(temp_dir.glob(f"*.{_TRANSCRIPT_FILE_EXT}"))

    # Sort transcript files by priority: Uploaded English over auto-generated
    transcript_files.sort(key=_get_youtube_transcript_file_priority)

    # Parse transcript files into structured objects
    if not transcript_files:
        raise URLTranscriptNotFoundError

    # Use highest priority transcript file
    transcript_file = transcript_files[0]
    # Read JSON3 format from disk
    transcript_data = json.loads(transcript_file.read_text(encoding="utf-8"))
    # Extract events → TranscriptLine objects
    events = transcript_data.get("events", [])
    return _extract_transcript_lines_from_json3(events)


def _fetch_video_metadata_and_transcript(
    url: str,
) -> tuple[VideoMetadata, list[TranscriptLine], list[_InternalChapterDict]]:
    """Extract video metadata and download transcript from YouTube using yt-dlp.

    Orchestrates the download and processing of YouTube video data by
    coordinating helper functions for downloading and metadata creation.

    Args:
        url: YouTube video URL

    Returns:
        Tuple of (VideoMetadata object, list of TranscriptLine objects,
                 list of _InternalChapterDict objects from YouTube API)
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Phase 1: Download transcript and metadata using yt-dlp
        raw_metadata = _download_transcript_with_yt_dlp(url, Path(temp_dir))

        # Phase 2: Process downloaded transcript files
        transcript_lines = _extract_transcript_lines_from_files(Path(temp_dir))

        # Phase 3: Create structured metadata object
        metadata = _create_video_metadata(raw_metadata, url)

        # Phase 4: Extract raw YouTube chapter data (kept separate from VideoMetadata)
        raw_youtube_chapters = raw_metadata.get("chapters", [])

        return metadata, transcript_lines, raw_youtube_chapters


def _extract_transcript_lines_from_json3(
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


def _assign_transcript_lines_to_chapters(
    metadata: VideoMetadata,
    transcript_lines: list[TranscriptLine],
    chapter_dicts: list[_InternalChapterDict],
) -> list[Chapter]:
    """Assign transcript lines to chapters based on temporal boundaries.

    Args:
        metadata: Video metadata for title
        transcript_lines: List of all individual transcript lines
        chapter_dicts: List of internal chapter dictionaries

    Returns:
        List of Chapter objects with assigned transcript lines
    """
    if not chapter_dicts:
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

    for i, youtube_chapter_dict in enumerate(chapter_dicts):
        chapter_start_time = float(youtube_chapter_dict.get("start_time", 0))

        # End time is start of next chapter, or infinity for last chapter
        if i + 1 < len(chapter_dicts):
            chapter_end_time = float(chapter_dicts[i + 1]["start_time"])
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
                title=youtube_chapter_dict.get("title", f"Chapter {i + 1}"),
                start_time=chapter_start_time,
                end_time=chapter_end_time,
                transcript_lines=chapter_transcript_lines,
            )
        )

    return chapters


def parse_youtube_url(url: str) -> TranscriptDocument:
    """Parse YouTube URL and return structured transcript document.

    Main interface function that coordinates the complete URL processing pipeline:
    1. Fetch video metadata and transcript from YouTube (includes JSON3 extraction)
    2. Assign transcript lines to chapters
    3. Return complete TranscriptDocument

    Args:
        url: YouTube video URL

    Returns:
        TranscriptDocument with video metadata and chapters containing transcript lines

    Raises:
        BaseTranscriptError: Domain-level failures (e.g., yt-dlp mapped errors via
            map_yt_dlp_exception(), or URLTranscriptNotFoundError when no transcript
            exists).
    """
    logger.info("Processing video: %s", url)

    # Step 1: Fetch metadata and download transcript using yt-dlp
    metadata, transcript_lines, youtube_chapter_dicts = (
        _fetch_video_metadata_and_transcript(url)
    )

    # Step 2: Assign transcript lines to chapters
    chapters = _assign_transcript_lines_to_chapters(
        metadata, transcript_lines, youtube_chapter_dicts
    )

    # Step 3: Create and return TranscriptDocument
    return TranscriptDocument(metadata=metadata, chapters=chapters)
