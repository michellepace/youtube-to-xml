"""Convert YouTube videos to XML files with transcript lines organized by chapters.

This script downloads YouTube transcripts and creates structured XML files.
The XML structure: <transcript> root with video metadata attributes, containing a
<chapters> element with <chapter> elements that contain individual timestamped
transcript lines.

Usage:
    uv run scripts/url_to_transcript.py <YouTube_URL>

Example:
    uv run scripts/url_to_transcript.py https://youtu.be/Q4gsvJvRjCU

For a provided YouTube URL, the script will:
1. Fetch the video metadata (title, upload date, duration)
2. Download and parse transcript lines (the timestamped text from YouTube's transcript)
3. Assign transcript lines to chapters (using YouTube's chapter markers if available)
4. Create and save an XML document with dynamic filename based on video title

Transcript priority:
1. Manual English transcript uploaded by the video creator (highest quality)
2. Auto-generated English transcript (fallback)
No other languages are downloaded - English only.

The output XML contains video metadata (video_title, upload_date, duration, video_url)
and transcript lines organised by chapter, with each individual transcript line
timestamped.
"""

import contextlib
import json
import math
import os
import re
import sys
import tempfile
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

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
from youtube_to_xml.time_utils import (
    MILLISECONDS_PER_SECOND,
    format_video_duration,
    format_video_upload_date,
    seconds_to_timestamp,
)

# Module-level logger
logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class VideoMetadata:
    """Video metadata needed for XML output."""

    video_title: str
    upload_date: str  # YYYY-MM-DD formatted string
    duration: str  # "2m 43s" formatted string
    video_url: str
    chapters_data: list[dict]


@dataclass(frozen=True, slots=True)
class TranscriptLine:
    """A single YouTube timed transcript line with timestamp."""

    timestamp: float  # in seconds
    text: str


@dataclass(frozen=True, slots=True)
class Chapter:
    """A video chapter containing transcript lines within its time range."""

    title: str
    start_time: float
    end_time: float
    transcript_lines: list[TranscriptLine]  # YouTube transcript lines

    @property
    def duration(self) -> float:
        """Calculate chapter duration (may be inf for the final open-ended chapter)."""
        return self.end_time - self.start_time

    def format_transcript_lines(self) -> str:
        """Format transcript lines as timestamped text for XML output."""
        if not self.transcript_lines:
            return ""

        lines = []
        for line in self.transcript_lines:
            lines.append(seconds_to_timestamp(line.timestamp))
            lines.append(line.text)

        return "\n      ".join(lines)


def fetch_video_metadata_and_transcript(
    url: str,
) -> tuple[VideoMetadata, list[TranscriptLine]]:
    """Extract video metadata and download transcript from YouTube using yt-dlp.

    Uses yt-dlp to fetch video information and transcript, avoiding rate limits
    by using yt-dlp's built-in transcript handling instead of direct HTTP requests.

    Args:
        url: YouTube video URL

    Returns:
        Tuple of (VideoMetadata object, list of TranscriptLine objects)

    Raises:
        URLBotProtectionError: If YouTube requires verification
        URLNotYouTubeError: If URL is not a YouTube video
        URLIncompleteError: If YouTube URL has incomplete video ID
        URLIsInvalidError: If URL format is invalid
        URLVideoUnavailableError: If YouTube video is unavailable
        URLTranscriptNotFoundError: If no transcript is available
        URLRateLimitError: If YouTube rate limit is encountered
    """
    options = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en", "en-orig"],  # English manual then auto-generated
        "subtitlesformat": "json3",
        "outtmpl": "%(title)s [%(id)s].%(ext)s",
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to temp directory for yt-dlp output
        options["outtmpl"] = str(Path(temp_dir) / "%(title)s [%(id)s].%(ext)s")

        # Phase 1: Use yt-dlp to get data for transcript
        with (
            open(os.devnull, "w") as devnull,  # noqa: PTH123 - os.devnull for cross-platform
            contextlib.redirect_stderr(devnull),
            yt_dlp.YoutubeDL(options) as ydl,
        ):
            try:
                # a) get complete video metadata from YouTube
                raw_metadata = ydl.extract_info(url, download=False)
                # b) download subtitle files to temp_dir (.json3 format)
                ydl.process_info(raw_metadata)
            except (DownloadError, ExtractorError, UnsupportedError) as e:
                mapped_exception = map_yt_dlp_exception(e)
                raise mapped_exception from e

        # Phase 2: File processing (outside yt-dlp context)
        # Note: raw_metadata is never None in practice - yt-dlp raises exceptions instead
        assert raw_metadata is not None  # Satisfy Pyright type checker  # noqa: S101

        # a) Locate downloaded transcript files
        video_id = raw_metadata.get("id", "")
        transcript_files = [
            p for p in Path(temp_dir).glob("*.json3") if f"[{video_id}]" in p.name
        ]

        # Implement transcript priority: manual English (.en.json3) over auto-generated
        transcript_files.sort(key=lambda p: ".en-orig.json3" in p.name)

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
            upload_date=format_video_upload_date(raw_metadata.get("upload_date", "")),
            duration=format_video_duration(float(raw_metadata.get("duration", 0))),
            video_url=raw_metadata.get("webpage_url", url),
            chapters_data=raw_metadata.get("chapters", []),
        )

        return metadata, transcript_lines


def extract_transcript_lines_from_json3(events: list) -> list[TranscriptLine]:
    """Extract individual transcript lines from JSON3 event objects.

    Args:
        events: List of JSON3 event objects from YouTube

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
    metadata: VideoMetadata, transcript_lines: list[TranscriptLine]
) -> list[Chapter]:
    """Parse API transcript data into chapters.

    Args:
        metadata: Video metadata including chapter info
        transcript_lines: List of all individual transcript lines

    Returns:
        List of Chapter objects with assigned transcript lines
    """
    if not metadata.chapters_data:
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
    chapter_list = metadata.chapters_data

    for i, chapter_info in enumerate(chapter_list):
        start = float(chapter_info.get("start_time", 0))

        # End time is start of next chapter, or infinity for last chapter
        if i + 1 < len(chapter_list):
            end = float(chapter_list[i + 1]["start_time"])
        else:
            end = math.inf

        # Filter transcript lines within this chapter's time range
        chapter_transcript_lines = [
            line for line in transcript_lines if start <= line.timestamp < end
        ]

        chapters.append(
            Chapter(
                title=chapter_info.get("title", f"Chapter {i + 1}"),
                start_time=start,
                end_time=end,
                transcript_lines=chapter_transcript_lines,
            )
        )

    return chapters


def create_xml_document(metadata: VideoMetadata, chapters: list[Chapter]) -> str:
    """Create the complete XML document with metadata and chapters.

    Args:
        metadata: Video metadata for attributes
        chapters: List of chapters with transcript lines

    Returns:
        Pretty-formatted XML string
    """
    # Create root element with metadata attributes
    root = ET.Element("transcript")
    root.set("video_title", metadata.video_title)
    root.set("upload_date", metadata.upload_date)
    root.set("duration", metadata.duration)
    root.set("video_url", metadata.video_url)

    # Add chapters container
    chapters_elem = ET.SubElement(root, "chapters")

    # Add each chapter
    for chapter in chapters:
        chapter_elem = ET.SubElement(chapters_elem, "chapter")
        chapter_elem.set("title", chapter.title)
        chapter_elem.set("start_time", seconds_to_timestamp(chapter.start_time))

        # Add transcript lines if available
        formatted_lines = chapter.format_transcript_lines()
        if formatted_lines:
            chapter_elem.text = "\n      " + formatted_lines + "\n    "

    # Convert to pretty XML string
    return format_xml_output(root)


def format_xml_output(element: ET.Element) -> str:
    """Format XML element with proper indentation."""
    ET.indent(element, space="  ")
    return ET.tostring(element, encoding="unicode", xml_declaration=True) + "\n"


def sanitise_title_for_filename(title: str) -> str:
    """Convert video title to safe filename with .xml extension."""
    # Remove non-alphanumeric characters except spaces and hyphens
    safe_title = re.sub(r"[^\w\s-]", "", title.lower())
    # Replace spaces and multiple hyphens with single hyphen
    safe_title = re.sub(r"[\s_-]+", "-", safe_title).strip("-")
    return f"{safe_title}.xml"


def convert_youtube_to_xml(
    video_url: str, execution_id: str
) -> tuple[str, VideoMetadata, list[Chapter], int]:
    """Convert YouTube video to XML transcript with metadata.

    Core business logic that:
    1. Fetches video metadata and downloads transcript using yt-dlp
    2. Assigns transcript lines to chapters
    3. Creates XML document

    Args:
        video_url: YouTube video URL
        execution_id: Unique identifier for this execution

    Returns:
        Tuple of (XML content as string, VideoMetadata object, list of chapters,
                 transcript lines count)
    """
    logger.info("[%s] Processing video: %s", execution_id, video_url)

    # Step 1: Fetch metadata and download transcript using yt-dlp
    try:
        metadata, transcript_lines = fetch_video_metadata_and_transcript(video_url)
    except URLTranscriptNotFoundError:
        logger.warning("[%s] No transcript available for video", execution_id)
        raise  # Re-raise to prevent file creation (no useless empty files)
    except URLRateLimitError:
        logger.exception("[%s] URLRateLimitError", execution_id)
        raise  # Re-raise to prevent file creation

    # Step 2: Assign transcript lines to chapters
    chapters = assign_transcript_lines_to_chapters(metadata, transcript_lines)

    # Step 3: Create XML
    xml_output = create_xml_document(metadata, chapters)

    return xml_output, metadata, chapters, len(transcript_lines)


def convert_and_save_youtube_xml(
    video_url: str, execution_id: str
) -> tuple[Path, VideoMetadata]:
    """Convert YouTube video to XML and save to file.

    Handles the file I/O operation separate from business logic.
    Uses dynamic filename based on video title.

    Args:
        video_url: YouTube video URL
        execution_id: Unique identifier for this execution

    Returns:
        Tuple of (output file path, video metadata)
    """
    # Generate XML content and get metadata for filename
    xml_output, metadata, chapters, transcript_lines_count = convert_youtube_to_xml(
        video_url, execution_id
    )

    # Log processing results for operational visibility
    logger.info(
        "[%s] Generated XML with %d chapters and %d transcript lines",
        execution_id,
        len(chapters),
        transcript_lines_count,
    )

    # Save to file
    output_filename = sanitise_title_for_filename(metadata.video_title)
    if output_filename == ".xml":
        output_filename = f"transcript-{execution_id}.xml"
    output_path = Path(output_filename)
    output_path.write_text(xml_output, encoding="utf-8")

    logger.info("[%s] Successfully created: %s", execution_id, output_path.name)

    return output_path, metadata


def main() -> None:
    """Command-line interface entry point."""
    setup_logging()
    execution_id = str(uuid.uuid4())[:8]

    try:
        video_url = sys.argv[1]
    except IndexError:
        print("YouTube URL to XML Converter")
        print("  Usage: include the YouTube URL as an argument")
        print("  E.g.: url_to_transcript.py https://www.youtube.com/watch?v=Q4gsvJvRjCU")
        sys.exit(1)

    try:
        print(f"🎬 Processing: {video_url}")
        output_path, metadata = convert_and_save_youtube_xml(video_url, execution_id)

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
        logger.info("[%s] Processing failed: %s", execution_id, e)
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except (ValueError, OSError) as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.exception("[%s] Unexpected error", execution_id)
        sys.exit(1)


if __name__ == "__main__":
    main()
