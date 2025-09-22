"""Convert YouTube videos to XML files with transcript lines organized by chapters.

This script downloads YouTube transcripts and creates structured XML files using
shared models and xml_builder infrastructure.

Usage:
    uv run scripts/url_to_transcript.py <YouTube_URL>

Example:
    uv run scripts/url_to_transcript.py https://youtu.be/Q4gsvJvRjCU

For a provided YouTube URL, the script will:
1. Fetch the video metadata (title, published date, duration)
2. Download and parse transcript lines (the timestamped text from YouTube's transcript)
3. Assign transcript lines to chapters (using YouTube's chapter markers if available)
4. Create TranscriptDocument and generate XML using shared xml_builder

Transcript priority:
1. Manual English transcript uploaded by the video creator (highest quality)
2. Auto-generated English transcript (fallback)
No other languages are downloaded - English only.
"""

import json
import math
import re
import sys
import tempfile
from pathlib import Path
from typing import TypedDict

import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError, UnsupportedError

from youtube_to_xml.exceptions import (
    URLBotProtectionError,
    URLIncompleteError,
    URLIsInvalidError,
    URLNotYouTubeError,
    URLRateLimitError,
    URLTranscriptNotFoundError,
    URLUnmappedError,
    URLVideoUnavailableError,
    map_yt_dlp_exception,
)
from youtube_to_xml.logging_config import get_logger, setup_logging
from youtube_to_xml.models import (
    Chapter,
    TranscriptDocument,
    TranscriptLine,
    VideoMetadata,
)
from youtube_to_xml.time_utils import MILLISECONDS_PER_SECOND
from youtube_to_xml.xml_builder import transcript_to_xml


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

    Uses yt-dlp to fetch video information and transcript, avoiding rate limits
    by using yt-dlp's built-in transcript handling instead of direct HTTP requests.

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
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        options = {
            "no_warnings": True,
            "no_progress": True,
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
    """Parse API transcript data into chapters.

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


def sanitise_title_for_filename(title: str) -> str:
    """Convert video title to safe filename with .xml extension."""
    # Remove non-alphanumeric characters except spaces and hyphens
    safe_title = re.sub(r"[^\w\s-]", "", title.lower())
    # Replace spaces and multiple hyphens with single hyphen
    safe_title = re.sub(r"[\s_-]+", "-", safe_title).strip("-")
    return f"{safe_title}.xml"


def convert_youtube_to_xml(
    video_url: str,
) -> tuple[str, VideoMetadata, list[Chapter], int]:
    """Convert YouTube video to XML transcript with metadata.

    Core business logic that:
    1. Fetches video metadata and downloads transcript using yt-dlp
    2. Assigns transcript lines to chapters
    3. Creates TranscriptDocument and generates XML using shared xml_builder

    Args:
        video_url: YouTube video URL

    Returns:
        Tuple of (XML content as string, VideoMetadata object, list of chapters,
                 transcript lines count)
    """
    logger.info("Processing video: %s", video_url)

    # Step 1: Fetch metadata and download transcript using yt-dlp
    try:
        metadata, transcript_lines, chapters_dicts = fetch_video_metadata_and_transcript(
            video_url
        )
    except URLTranscriptNotFoundError:
        logger.warning("No transcript available for video")
        raise  # Re-raise to prevent file creation (no useless empty files)
    except URLRateLimitError:
        logger.exception("URLRateLimitError")
        raise  # Re-raise to prevent file creation

    # Step 2: Assign transcript lines to chapters
    chapters = assign_transcript_lines_to_chapters(
        metadata, transcript_lines, chapters_dicts
    )

    # Step 3: Create TranscriptDocument and generate XML using shared xml_builder
    document = TranscriptDocument(metadata=metadata, chapters=chapters)
    xml_output = transcript_to_xml(document)

    return xml_output, metadata, chapters, len(transcript_lines)


def convert_and_save_youtube_xml(video_url: str) -> Path:
    """Convert YouTube video to XML and save to file.

    Handles the file I/O operation separate from business logic.
    Uses dynamic filename based on video title.

    Args:
        video_url: YouTube video URL

    Returns:
        Output file path
    """
    # Generate XML content and get metadata for filename
    xml_output, metadata, chapters, transcript_lines_count = convert_youtube_to_xml(
        video_url
    )

    # Log processing results for operational visibility
    logger.info(
        "Generated XML with %d chapters and %d transcript lines",
        len(chapters),
        transcript_lines_count,
    )

    # Save to file
    output_filename = sanitise_title_for_filename(metadata.video_title)
    if output_filename == ".xml":
        output_filename = "transcript-untitled.xml"
    output_path = Path(output_filename)
    output_path.write_text(xml_output, encoding="utf-8")

    logger.info("Successfully created: %s", output_path.name)

    return output_path


def main() -> None:
    """Command-line interface entry point."""
    setup_logging()

    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help"]:  # noqa: PLR2004
        print("YouTube URL to XML Converter")
        print("  Usage: include the YouTube URL as an argument")
        print("  E.g.: url_to_transcript.py https://www.youtube.com/watch?v=Q4gsvJvRjCU")
        sys.exit(1)

    video_url = sys.argv[1]

    try:
        print(f"🎬 Processing: {video_url}")
        output_path = convert_and_save_youtube_xml(video_url)

        print(f"✅ Created: {output_path.name}")
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
        sys.exit(1)
    except (
        URLBotProtectionError,
        URLIncompleteError,
        URLIsInvalidError,
        URLNotYouTubeError,
        URLTranscriptNotFoundError,
        URLRateLimitError,
        URLUnmappedError,
        URLVideoUnavailableError,
    ) as e:
        logger.info("Processing failed: %s", e)
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except (ValueError, OSError) as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.exception("Unexpected error")
        sys.exit(1)


if __name__ == "__main__":
    main()
